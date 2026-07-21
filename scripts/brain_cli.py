#!/usr/bin/env python3
"""
MarkAI · 个人 AI 知识库 CLI
============================
本地第二大脑：存储、检索、管理你的知识和灵感片段。
支持文本、URL、图片（AI 描述）。SQLite FTS5 全文索引 + AI 语义辅助。

用法:
  markai save "内容"                   保存文本
  markai save --title "标题" "内容"    带标题保存
  markai save --url "https://..."      保存网页内容（需配合 web_fetch）
  markai save --image "path/to/img"    保存图片引用+AI描述
  markai search "查询"                 全文搜索（返回 JSON）
  markai list [--limit N]              列出最近条目
  markai get <id>                      获取单条完整内容
  markai delete <id>                   删除条目
  markai stats                         统计信息
  markai export [--format json|md]     导出全部知识库
"""

import sqlite3
import json
import os
import sys
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── 路径配置 ────────────────────────────────────────────
MARKAI_HOME = Path(os.path.expanduser("~/.markai"))
DB_PATH = MARKAI_HOME / "brain.db"
IMAGES_DIR = MARKAI_HOME / "images"
MARKAI_HOME.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ── 数据库 ──────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            content_type TEXT NOT NULL DEFAULT 'text',
            content_subtype TEXT DEFAULT '',
            source_url TEXT DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            summary TEXT NOT NULL DEFAULT '',
            image_path TEXT DEFAULT '',
            structured_data TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # 自动升级旧数据库
    cols = [r[1] for r in conn.execute("PRAGMA table_info(entries)").fetchall()]
    if 'content_subtype' not in cols:
        conn.execute("ALTER TABLE entries ADD COLUMN content_subtype TEXT DEFAULT ''")
    if 'structured_data' not in cols:
        conn.execute("ALTER TABLE entries ADD COLUMN structured_data TEXT DEFAULT '{}'")

    # FTS5 全文索引 — unicode61 对中英文混搜友好（CJK字符作为独立token）
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
                title, content, tags, summary,
                content='entries',
                content_rowid='rowid',
                tokenize='unicode61'
            )
        """)
    except sqlite3.OperationalError:
        pass  # FTS5 不可用时静默跳过

    # 同步触发器
    conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
            INSERT INTO entries_fts(rowid, title, content, tags, summary)
            VALUES (new.rowid, new.title, new.content, new.tags, new.summary);
        END;

        CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, title, content, tags, summary)
            VALUES ('delete', old.rowid, old.title, old.content, old.tags, old.summary);
        END;

        CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, title, content, tags, summary)
            VALUES ('delete', old.rowid, old.title, old.content, old.tags, old.summary);
            INSERT INTO entries_fts(rowid, title, content, tags, summary)
            VALUES (new.rowid, new.title, new.content, new.tags, new.summary);
        END;
    """)
    conn.commit()

    # 迁移旧数据到 FTS
    try:
        conn.execute("""
            INSERT INTO entries_fts(rowid, title, content, tags, summary)
            SELECT rowid, title, content, tags, summary FROM entries
            WHERE rowid NOT IN (SELECT rowid FROM entries_fts)
        """)
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()


# ── 辅助 ────────────────────────────────────────────────
def gen_id(content: str = "") -> str:
    h = hashlib.sha1((content + str(datetime.now().timestamp())).encode()).hexdigest()
    return h[:12]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def print_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def row_to_dict(row) -> dict:
    d = dict(row)
    # 解析 tags JSON
    try:
        d["tags"] = json.loads(d.get("tags", "[]"))
    except (json.JSONDecodeError, TypeError):
        d["tags"] = []
    return d


# ── CRUD ────────────────────────────────────────────────
def save_entry(title="", content="", content_type="text",
               content_subtype="", source_url="", tags=None, summary="",
               image_path="", structured_data=None) -> dict:
    tags = tags or []
    structured = structured_data or {}
    entry_id = gen_id(content or title)
    now = now_iso()

    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO entries (id, title, content, content_type,
            content_subtype, source_url, tags, summary, image_path,
            structured_data, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (entry_id, title, content, content_type, content_subtype,
          source_url, json.dumps(tags, ensure_ascii=False),
          summary, image_path,
          json.dumps(structured, ensure_ascii=False), now, now))
    conn.commit()

    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def search_entries(query: str, limit: int = 10) -> list:
    """FTS5 全文搜索 + 逐词回退，中英文混搜友好。"""
    conn = get_db()
    rows = []
    terms = _split_terms(query)

    # 策略 1: 原始查询 FTS
    try:
        rows = conn.execute("""
            SELECT e.*, rank FROM entries_fts f
            JOIN entries e ON e.rowid = f.rowid
            WHERE entries_fts MATCH ?
            ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
    except sqlite3.OperationalError:
        pass

    # 策略 2: FTS OR 查询（拆分词条，解决短语中间有间隔词的问题）
    if not rows and len(terms) > 1:
        or_query = " OR ".join(terms)
        try:
            rows = conn.execute("""
                SELECT e.*, rank FROM entries_fts f
                JOIN entries e ON e.rowid = f.rowid
                WHERE entries_fts MATCH ?
                ORDER BY rank LIMIT ?
            """, (or_query, limit)).fetchall()
        except sqlite3.OperationalError:
            pass

    # 策略 3: LIKE 子串搜索（最宽松的兜底）
    if not rows:
        like_clauses = []
        like_params = []
        for term in terms:
            like_clauses.append("(title LIKE ? OR content LIKE ? OR tags LIKE ? OR summary LIKE ?)")
            p = f"%{term}%"
            like_params.extend([p, p, p, p])
        like_sql = " OR ".join(like_clauses)
        rows = conn.execute(f"""
            SELECT *, -1.0 as rank FROM entries
            WHERE {like_sql}
            ORDER BY created_at DESC
            LIMIT ?
        """, (*like_params, limit)).fetchall()

    conn.close()
    return [row_to_dict(r) for r in rows]


def _split_terms(query: str) -> list:
    """将查询拆分为独立搜索词条，跳过太短的无意义词"""
    # 按空格、标点拆分
    raw = re.split(r'[\s,，。！？、；：""''「」]+', query)
    return [t.strip() for t in raw if len(t.strip()) >= 1]


def list_entries(limit: int = 20) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM entries ORDER BY updated_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_entry(entry_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def delete_entry(entry_id: str) -> bool:
    conn = get_db()
    cur = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def update_entry(entry_id: str, **kwargs):
    """更新条目字段。kwargs 可包含 title, content, tags, summary, source_url"""
    existing = get_entry(entry_id)
    if not existing:
        return None

    for key in ("title", "content", "tags", "summary", "source_url"):
        if key in kwargs and kwargs[key] is not None:
            existing[key] = kwargs[key]

    conn = get_db()
    now = now_iso()
    tags_json = json.dumps(existing.get("tags", []), ensure_ascii=False)
    conn.execute("""
        UPDATE entries SET title=?, content=?, tags=?, summary=?, source_url=?, updated_at=?
        WHERE id=?
    """, (existing["title"], existing["content"], tags_json,
          existing["summary"], existing["source_url"], now, entry_id))
    conn.commit()
    conn.close()
    return get_entry(entry_id)


def check_duplicates(content: str, threshold: float = 0.5) -> list:
    """存储前检测重复/高度相似内容。返回相似条目列表。"""
    entries = list_entries(limit=50)
    if not entries:
        return []
    
    # 用简单的 Jaccard-like 相似度：共同字符占比
    content_set = set(content)
    if len(content_set) < 3:
        return []
    
    dupes = []
    for e in entries:
        e_set = set(e.get("content", ""))
        if len(e_set) < 3:
            continue
        intersection = content_set & e_set
        union = content_set | e_set
        sim = len(intersection) / len(union) if union else 0
        if sim >= threshold:
            dupes.append({"entry": e, "similarity": round(sim, 2)})
    
    # 按相似度降序
    dupes.sort(key=lambda x: -x["similarity"])
    return dupes[:5]


def search_entries_ranked(query: str, limit: int = 10) -> list:
    """增强搜索：FTS + 标签加权 + 时间衰减"""
    results = search_entries(query, limit=limit * 2)  # 多取一些用于重排
    
    if not results:
        return []
    
    # 计算增强分数
    now = datetime.now(timezone.utc)
    for r in results:
        score = 0.0
        
        # FTS rank 分数（越低越好，取负号转正向）
        fts_rank = r.get("rank", -1)
        score += abs(fts_rank) * 10
        
        # 标题命中加分
        q_lower = query.lower()
        title_lower = r.get("title", "").lower()
        if query in title_lower or title_lower in q_lower:
            score += 5.0
        
        # 标签命中加分
        tags = r.get("tags", [])
        tag_match = sum(1 for t in tags if t.lower() in q_lower)
        score += tag_match * 2.0
        
        # 时间衰减（越新越高，7天半衰期）
        try:
            ts = datetime.fromisoformat(r.get("created_at", now.isoformat()))
            days_ago = (now - ts).total_seconds() / 86400
            time_score = 1.0 / (1.0 + days_ago / 7.0)
            score += time_score * 2.0
        except (ValueError, TypeError):
            pass
        
        r["_score"] = round(score, 2)
    
    # 按增强分数排序
    results.sort(key=lambda x: -x.get("_score", 0))
    return results[:limit]


def generate_ics(entry_id: str) -> dict:
    """为条目生成 .ics 日历文件。从内容中提取日期信息。"""
    entry = get_entry(entry_id)
    if not entry:
        return {"ok": False, "error": "条目不存在"}

    # 从内容或摘要中尝试提取日期
    text = entry.get("content", "") + " " + entry.get("summary", "") + " " + entry.get("title", "")
    # 匹配中文日期格式：2026年8月、8月、2026-08、8月1日
    date_match = re.search(
        r'(\d{4}\s*年\s*)?(\d{1,2})\s*月\s*(\d{1,2})?\s*日?', text
    )
    if not date_match:
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if not date_match:
        return {"ok": False, "error": "未在条目中找到可识别的日期信息"}

    try:
        if date_match.lastindex == 3 and len(date_match.group(1) or "") > 4:
            # "2026年8月" or "2026-08" format
            if date_match.group(1) and '年' in date_match.group(1):
                year = date_match.group(1).replace('年', '').strip()
                month = date_match.group(2).zfill(2)
                day = (date_match.group(3) or "1").zfill(2)
            else:
                year = date_match.group(1) or str(datetime.now(timezone.utc).year)
                month = date_match.group(2).zfill(2)
                day = (date_match.group(3) or "01").zfill(2)
        else:
            # 从当前上下文推断年份
            year = str(datetime.now(timezone.utc).year)
            month = date_match.group(2).zfill(2)
            day = (date_match.group(3) or "01").zfill(2)

        dtstart = f"{year}{month}{day}"
        # 默认当天结束
        dtend = f"{year}{month}{str(int(day)+1).zfill(2) if int(day) < 31 else '31'}"
    except Exception:
        return {"ok": False, "error": "日期解析失败"}

    # 构建 .ics 内容
    uid = uuid.uuid4().hex[:16]
    summary = entry.get("title", "MarkAI Entry")[:75]
    desc = (entry.get("summary", "") or entry.get("content", "")[:120]).replace("\n", "\\n")[:200]

    ics = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//markai//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{uid}@markai",
        f"DTSTART;VALUE=DATE:{dtstart}",
        f"DTEND;VALUE=DATE:{dtend}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    # 写入文件
    ics_path = MARKAI_HOME / f"{entry_id}.ics"
    ics_path.write_text("\r\n".join(ics) + "\r\n", encoding="utf-8")

    return {
        "ok": True,
        "file": str(ics_path),
        "summary": summary,
        "date": f"{year}-{month}-{day}",
    }


def get_stats() -> dict:
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    by_type = {}
    for row in conn.execute(
        "SELECT content_type, COUNT(*) as cnt FROM entries GROUP BY content_type"
    ):
        by_type[row["content_type"]] = row["cnt"]

    # 标签云
    tags_rows = conn.execute("SELECT tags FROM entries WHERE tags != '[]'").fetchall()
    tag_freq = {}
    for r in tags_rows:
        try:
            for t in json.loads(r["tags"]):
                tag_freq[t] = tag_freq.get(t, 0) + 1
        except Exception:
            pass
    top_tags = sorted(tag_freq.items(), key=lambda x: -x[1])[:20]

    # 时间范围
    first = conn.execute("SELECT MIN(created_at) as d FROM entries").fetchone()["d"]
    last = conn.execute("SELECT MAX(created_at) as d FROM entries").fetchone()["d"]

    # 最近活跃度（按天统计最近7天的新增）
    week_activity = {}
    for row in conn.execute(
        "SELECT DATE(created_at) as day, COUNT(*) as cnt FROM entries "
        "WHERE created_at >= DATE('now', '-7 days') GROUP BY day"
    ).fetchall():
        week_activity[row["day"]] = row["cnt"]

    conn.close()
    return {
        "total_entries": total,
        "by_type": by_type,
        "top_tags": top_tags,
        "date_range": {"first": first, "last": last},
        "recent_week": week_activity,
        "db_path": str(DB_PATH),
        "images_dir": str(IMAGES_DIR),
    }


def get_typed(subtype: str, limit: int = 50) -> list:
    """按 content_subtype 查询，格式化展示结构化字段"""
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM entries
        WHERE content_subtype = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (subtype, limit)).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_all_types() -> list:
    """统计所有内容子类型"""
    conn = get_db()
    rows = conn.execute("""
        SELECT content_subtype, COUNT(*) as cnt
        FROM entries WHERE content_subtype != ''
        GROUP BY content_subtype ORDER BY cnt DESC
    """).fetchall()
    conn.close()
    return [{"subtype": r["content_subtype"], "count": r["cnt"]} for r in rows]


def export_entries(fmt: str = "json") -> str:
    entries = list_entries(limit=99999)
    if fmt == "md":
        lines = ["# 🧠 Brain 知识库导出\n"]
        for e in entries:
            lines.append(f"## {e['title'] or '(无标题)'}")
            if e["tags"]:
                lines.append(f"标签: {' · '.join(e['tags'])}")
            if e["source_url"]:
                lines.append(f"来源: {e['source_url']}")
            lines.append(f"\n{e['content']}\n")
            lines.append(f"*{e['created_at'][:10]} · ID: {e['id']}*\n\n---\n")
        return "\n".join(lines)
    else:
        return json.dumps(entries, ensure_ascii=False, indent=2)


# ── CLI ─────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    if not args or args[0] in ('--help', '-h'):
        print("""MarkAI · 个人 AI 知识库
用法: markai <command> [args...]

命令:
  save       存储知识     markai save "内容" --title "标题" --tags "a,b"
                         支持 --subtype <type> --structured '{"key":"val"}'
  update     更新条目     markai update <id> --title "新标题"
  search     搜索         markai search "关键词" [--ranked]
  check      重复检测     markai check "内容"
  list       列出         markai list [--limit 20] [--subtype contact]
  get        查看详情     markai get <id>
  delete     删除         markai delete <id>
  calendar   生成日历     markai calendar <id>
  types      类型统计     markai types
  stats      统计         markai stats
  export     导出         markai export [--format json|md]

数据目录: ~/.markai/brain.db
""", file=sys.stderr)
        sys.exit(0)

    init_db()
    cmd = args[0].lower()

    if cmd == "save":
        title = content = source_url = summary = image_path = ""
        content_subtype = ""
        structured_json = ""
        tags = []
        content_type = "text"

        i = 1
        while i < len(args):
            a = args[i]
            if a == "--title" and i + 1 < len(args):
                i += 1; title = args[i]
            elif a == "--url" and i + 1 < len(args):
                i += 1; source_url = args[i]; content_type = "url"
            elif a == "--subtype" and i + 1 < len(args):
                i += 1; content_subtype = args[i]
            elif a == "--structured" and i + 1 < len(args):
                i += 1; structured_json = args[i]
            elif a == "--tags" and i + 1 < len(args):
                i += 1; tags = [t.strip() for t in args[i].split(",") if t.strip()]
            elif a == "--summary" and i + 1 < len(args):
                i += 1; summary = args[i]
            elif a == "--image" and i + 1 < len(args):
                i += 1; image_path = args[i]; content_type = "image"
            elif a == "--type" and i + 1 < len(args):
                i += 1; content_type = args[i]
            elif not a.startswith("--"):
                content = a
            i += 1

        if not content and not sys.stdin.isatty():
            content = sys.stdin.read().strip()

        if not content and content_type != "image":
            print("错误: 请提供要保存的内容", file=sys.stderr)
            sys.exit(1)

        # 解析结构化数据
        structured = {}
        if structured_json:
            try:
                structured = json.loads(structured_json)
            except json.JSONDecodeError:
                pass

        entry = save_entry(
            title=title, content=content, content_type=content_type,
            content_subtype=content_subtype,
            source_url=source_url, tags=tags, summary=summary,
            image_path=image_path, structured_data=structured
        )
        print_json(entry)

    elif cmd == "check":
        # 检测重复内容
        if len(args) < 2:
            print("用法: markai check <内容>", file=sys.stderr)
            sys.exit(1)
        content = args[1]
        if not content and not sys.stdin.isatty():
            content = sys.stdin.read().strip()
        dupes = check_duplicates(content)
        print_json({"duplicates_found": len(dupes), "duplicates": dupes})

    elif cmd == "search":
        if len(args) < 2:
            print("用法: markai search <查询> [--limit N] [--ranked]", file=sys.stderr)
            sys.exit(1)
        query = args[1]
        limit = 10
        ranked = "--ranked" in args
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        if ranked:
            results = search_entries_ranked(query, limit=limit)
        else:
            results = search_entries(query, limit=limit)
        print_json(results)

    elif cmd == "list":
        limit = 20
        subtype = ""
        # markai list types → 列出所有类型
        if len(args) >= 2 and args[1] == "types":
            print_json(get_all_types())
            return
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        if "--subtype" in args:
            idx = args.index("--subtype")
            if idx + 1 < len(args):
                subtype = args[idx + 1]
        if subtype:
            entries = get_typed(subtype, limit=limit)
        else:
            entries = list_entries(limit=limit)
        print_json(entries)

    elif cmd == "get":
        if len(args) < 2:
            print("用法: markai get <id>", file=sys.stderr)
            sys.exit(1)
        entry = get_entry(args[1])
        if entry:
            print_json(entry)
        else:
            print(f"未找到: {args[1]}", file=sys.stderr)
            sys.exit(1)

    elif cmd == "update":
        if len(args) < 2:
            print("用法: markai update <id> [--title ...] [--tags ...] [--summary ...] [--content ...]", file=sys.stderr)
            sys.exit(1)
        entry_id = args[1]
        kwargs = {}
        i = 2
        while i < len(args):
            a = args[i]
            if a == "--title" and i + 1 < len(args):
                i += 1; kwargs["title"] = args[i]
            elif a == "--tags" and i + 1 < len(args):
                i += 1; kwargs["tags"] = [t.strip() for t in args[i].split(",") if t.strip()]
            elif a == "--summary" and i + 1 < len(args):
                i += 1; kwargs["summary"] = args[i]
            elif a == "--content" and i + 1 < len(args):
                i += 1; kwargs["content"] = args[i]
            elif a == "--url" and i + 1 < len(args):
                i += 1; kwargs["source_url"] = args[i]
            i += 1
        entry = update_entry(entry_id, **kwargs)
        if entry:
            print_json(entry)
        else:
            print(f"未找到: {entry_id}", file=sys.stderr)
            sys.exit(1)

    elif cmd == "delete":
        if len(args) < 2:
            print("用法: markai delete <id>", file=sys.stderr)
            sys.exit(1)
        ok = delete_entry(args[1])
        print_json({"deleted": ok, "id": args[1]})

    elif cmd == "types":
        print_json(get_all_types())

    elif cmd == "stats":
        print_json(get_stats())

    elif cmd == "export":
        fmt = "json"
        if "--format" in args:
            idx = args.index("--format")
            if idx + 1 < len(args):
                fmt = args[idx + 1]
        print(export_entries(fmt))

    elif cmd == "calendar":
        if len(args) < 2:
            print("用法: markai calendar <id>", file=sys.stderr)
            sys.exit(1)
        result = generate_ics(args[1])
        print_json(result)
        if result.get("ok"):
            print(f"\n📅 日历文件已生成: {result['file']}", file=sys.stderr)
            print(f"   导入到 iPhone / Google Calendar / Outlook 即可收到推送通知")

    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import hashlib
    main()
