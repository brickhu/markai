#!/usr/bin/env python3
"""MarkAI Web Server — SSR dual-column + detail + stats + delete"""
import json, sys, os, http.server, urllib.parse, html, re
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import init_db, list_entries, search_entries_ranked, get_entry, get_typed, get_all_types, get_stats, delete_entry, get_extracts, get_extract_types_with_counts, add_extract

HOST = "127.0.0.1"

TYPE_STYLES = {
    "contact":   {"bg": "#1e3a5f", "icon": "📞", "border": "#3b82f6"},
    "expense":   {"bg": "#5f1e1e", "icon": "💰", "border": "#ef4444"},
    "flight":    {"bg": "#1e5f4a", "icon": "✈️", "border": "#10b981"},
    "reminder":  {"bg": "#5f4a1e", "icon": "⏰", "border": "#f59e0b"},
    "reference": {"bg": "#3a1e5f", "icon": "📖", "border": "#a78bfa"},
    "meeting":   {"bg": "#1e5f3a", "icon": "📅", "border": "#34d399"},
    "location":  {"bg": "#1e3f5f", "icon": "📍", "border": "#60a5fa"},
    "price":     {"bg": "#5f3a1e", "icon": "💎", "border": "#f97316"},
    "idea":      {"bg": "#2e1e5f", "icon": "💡", "border": "#8b5cf6"},
}
DEFAULT_STYLE = {"bg": "#1e1e2e", "icon": "📌", "border": "#475569"}
BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f0f1a;color:#e0e0e0;min-height:100vh}
.wrapper{display:flex;min-height:100vh}
.sidebar{width:240px;flex-shrink:0;background:#16162a;border-right:1px solid #2a2a3e;padding:24px 16px;display:flex;flex-direction:column;gap:4px;position:sticky;top:0;height:100vh;overflow-y:auto}
.logo{font-size:20px;font-weight:700;color:#a78bfa;margin-bottom:20px;display:flex;align-items:center;gap:8px}
.logo small{font-size:12px;color:#666;font-weight:400}
.nav-section{margin-bottom:16px}
.nav-section-title{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;padding-left:4px}
.nav-btn{display:block;padding:8px 12px;border-radius:8px;color:#aaa;text-decoration:none;font-size:13px;transition:0.15s;margin-bottom:2px}
.nav-btn:hover{background:#1e1e3a;color:#a78bfa}
.nav-btn.active{background:rgba(167,139,250,0.12);color:#a78bfa;font-weight:600;border-left:3px solid #a78bfa;padding-left:9px}
.nav-btn[style*="--nav-c"]:hover{border-left-color:var(--nav-c)}
.nav-btn-add{color:#a78bfa;font-size:12px;border:1px dashed #2a2a3e;text-align:center;padding:6px;border-radius:8px;margin-top:4px}
.nav-btn-add:hover{background:rgba(167,139,250,0.08);border-color:#a78bfa}
.nav-divider{height:1px;background:#2a2a3e;margin:8px 0}
.sidebar-footer{margin-top:auto;padding-top:16px;border-top:1px solid #2a2a3e;font-size:11px;color:#555}
.sidebar-footer a{color:#a78bfa;display:block;padding:6px 0;font-size:12px}
.sidebar-footer a:hover{color:#c4b5fd}
.main{flex:1;padding:24px 32px;overflow-y:auto;max-width:1000px}
a{color:inherit;text-decoration:none}
.search-bar{display:flex;gap:10px;margin-bottom:24px}
.search-bar input{flex:1;padding:10px 16px;border:1px solid #2a2a3e;border-radius:8px;background:#1a1a2e;color:#e0e0e0;font-size:15px;outline:none}
.search-bar input:focus{border-color:#7c3aed}
.search-bar button{padding:10px 20px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:15px}
.search-bar button:hover{background:#6d28d9}
.stats-line{color:#888;font-size:13px;margin-bottom:16px}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.card{border:1px solid;border-radius:12px;padding:16px;display:flex;gap:12px;transition:0.15s}
.card:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.card-icon{font-size:24px;flex-shrink:0;width:36px;height:36px;display:flex;align-items:center;justify-content:center}
.card-body{flex:1;min-width:0}
.card-title{font-size:15px;font-weight:600;color:#f1f5f9;margin-bottom:4px;line-height:1.3}
.card-meta{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px}
.card-summary{font-size:13px;color:#94a3b8;line-height:1.4}
hlt{background:#fbbf24;color:#0f0f1a;padding:0 3px;border-radius:3px}
.mark{background:#fbbf24;color:#0f0f1a;padding:0 2px;border-radius:2px}
.tag{display:inline-block;padding:1px 7px;border-radius:6px;background:rgba(255,255,255,0.08);font-size:11px;color:#a78bfa}
.st{display:inline-block;padding:1px 7px;border-radius:6px;background:rgba(167,139,250,0.2);font-size:11px;color:#a78bfa;font-weight:600}
.empty-state{text-align:center;padding:60px 20px}
.empty-icon{font-size:48px;margin-bottom:16px}
.empty-title{font-size:18px;color:#64748b;margin-bottom:8px}
.empty-desc{font-size:14px;color:#475569}
.breadcrumb{display:flex;align-items:center;gap:8px;font-size:13px;color:#64748b;margin-bottom:20px}
.breadcrumb a{color:#a78bfa}
.breadcrumb a:hover{color:#c4b5fd}
.detail-header{display:flex;gap:16px;align-items:flex-start;margin-bottom:24px}
.detail-icon{font-size:40px;width:56px;height:56px;display:flex;align-items:center;justify-content:center;border-radius:14px;border:1px solid;flex-shrink:0}
.detail-title{font-size:22px;font-weight:700;color:#f1f5f9;line-height:1.3;margin-bottom:8px}
.detail-meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:4px}
.detail-section{margin-bottom:24px}
.detail-section h3{font-size:12px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid #2a2a3e}
.detail-summary{font-size:16px;color:#c4b5fd;line-height:1.6;padding:16px;background:#1a1a2e;border-radius:10px;border:1px solid #2a2a3e}
.detail-content{font-size:15px;color:#94a3b8;line-height:1.8;white-space:pre-wrap;word-break:break-word}
.sd-table{width:100%;border-collapse:collapse;font-size:14px}
.sd-table td{padding:8px 12px;border-bottom:1px solid #2a2a3e;vertical-align:top}
.sd-key{color:#64748b;width:120px;font-weight:600;white-space:nowrap}
.sd-val{color:#e0e0e0;word-break:break-all}
.source-link{color:#60a5fa;font-size:14px;word-break:break-all;display:inline-block;padding:8px 12px;background:#1a1a2e;border-radius:8px;border:1px solid #2a2a3e}
.source-link:hover{border-color:#60a5fa}
.detail-footer{margin-top:32px;padding-top:16px;border-top:1px solid #2a2a3e;font-size:12px;color:#555;display:flex;gap:16px;align-items:center}
.btn{padding:8px 16px;border-radius:8px;border:none;cursor:pointer;font-size:13px;transition:0.15s;display:inline-block;text-decoration:none}
.btn-danger{background:#dc2626;color:#fff}
.btn-danger:hover{background:#b91c1c}
.btn-secondary{background:#2a2a3e;color:#aaa}
.btn-secondary:hover{background:#3a3a5e;color:#e0e0e0}
.confirm-box{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:32px;max-width:480px;margin:60px auto;text-align:center}
.confirm-box h2{color:#f87171;margin-bottom:12px}
.confirm-box p{color:#94a3b8;margin-bottom:24px;font-size:15px}
.confirm-box .actions{display:flex;gap:12px;justify-content:center}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.stat-card{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:20px;text-align:center}
.stat-num{font-size:32px;font-weight:700;color:#a78bfa}
.stat-label{font-size:13px;color:#64748b;margin-top:4px}
.stat-list{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:16px}
.stat-list-row{display:flex;justify-content:space-between;padding:6px 0;font-size:14px;border-bottom:1px solid #1e1e2e}
.stat-list-row:last-child{border-bottom:none}
.stat-list-key{color:#94a3b8}
.stat-list-val{color:#a78bfa;font-weight:600}
.stats-page h2{font-size:16px;color:#a78bfa;margin-bottom:12px;margin-top:24px}
.stats-page h2:first-child{margin-top:0}
@media(max-width:768px){.sidebar{width:100%;height:auto;position:static;flex-direction:row;flex-wrap:wrap;padding:12px 16px;border-right:none;border-bottom:1px solid #2a2a3e}.wrapper{flex-direction:column}.main{padding:16px}.nav-btn{font-size:12px;padding:6px 10px}.logo{margin-bottom:12px;width:100%}.card-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:1fr 1fr}}
"""


def esc(text):
    return html.escape(str(text or ""), quote=True)


def fmt_time(iso):
    return iso[:10] if iso else ""


def highlight(text, query):
    """Wrap matching keywords in <mark> tags."""
    if not query or not text:
        return esc(text)
    escaped = esc(text)
    escaped_q = re.escape(query)
    return re.sub(f"({escaped_q})", r"<mark class='hlt'>\1</mark>", escaped, flags=re.IGNORECASE)


def render_card_html(e, query=""):
    st = e.get("content_subtype", "") or ""
    style = TYPE_STYLES.get(st, DEFAULT_STYLE)
    icon = style["icon"]
    bg = style["bg"]
    border = style["border"]
    eid = esc(e.get("id", ""))
    title = highlight(e.get("title"), query)
    summary = highlight(e.get("summary") or "", query)
    tags_raw = e.get("tags", [])
    if isinstance(tags_raw, str):
        try:
            tags_raw = json.loads(tags_raw)
        except (json.JSONDecodeError, TypeError):
            tags_raw = []
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in tags_raw[:5])
    st_html = f'<span class="st">{esc(st)}</span>' if st else ""

    return f"""<a href="/detail?id={eid}" class="card" style="background:{bg};border-color:{border}">
  <div class="card-icon">{icon}</div>
  <div class="card-body">
    <div class="card-title">{title}</div>
    <div class="card-meta">{st_html}{tags_html}</div>
    {f'<div class="card-summary">{summary}</div>' if summary else ""}
  </div>
</a>"""


def render_sidebar(types_list, active_type="", query="", back_params="", bottom_text="", show_all_active=True):
    ac_rec = "active" if show_all_active and not active_type and not query else ""

    top_html = f"""
  <a href="/" class="nav-btn {ac_rec}">📋 Records</a>
  <a href="/stats" class="nav-btn">📊 统计</a>"""

    lists_html = ""
    for t in types_list:
        sn = t["name"]
        icon = t.get("icon", "\U0001f4cc")
        cnt = t.get("count", 0)
        ac2 = "active" if active_type == sn else ""
        href = f"/list?type={esc(sn)}"
        lists_html += f'<a href="{href}" class="nav-btn {ac2}" style="--nav-c:{t["color"]}">{icon} {esc(sn)} ({cnt})</a>\n'

    return f"""<div class="sidebar">
  <div class="logo">\U0001f4cc MarkAI <small>v3</small></div>
  <div class="nav-section">
    {top_html}
  </div>
  <div class="nav-divider"></div>
  <div class="nav-section">
    <div class="nav-section-title">\U0001f4ca Lists</div>
    {lists_html}
    <a href="/lists/new" class="nav-btn nav-btn-add">+ Add a list</a>
  </div>
  <div class="sidebar-footer">
    {bottom_text}
  </div>
</div>"""

def render_page(entries, query, active_type, types_list):
    entries_html = "\n".join(render_card_html(e, query) for e in entries)

    esc_q = esc(query)
    bt = f"?q={urllib.parse.quote(query)}" if query else (f"?type={urllib.parse.quote(active_type)}" if active_type else "")
    sidebar = render_sidebar(types_list, active_type, query, bt, f"{len(entries)} 条记忆")

    stats_parts = [f"{len(entries)} 条"]
    if query:
        stats_parts.append(f"搜索: {esc_q}")
    if active_type:
        stats_parts.append(f"类型: {esc(active_type)}")

    empty_html = ""
    if not entries:
        reason = "搜索" if query else "类型筛选"
        tip = "换个关键词试试" if query else ""
        empty_html = f"""<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-title">暂无结果</div><div class="empty-desc">{reason}未匹配到任何条目。{tip}</div></div>"""

    page_title = f"{esc_q} — MarkAI" if query else "MarkAI · 知识库"

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title><style>{BASE_CSS}</style></head><body>
<div class="wrapper">
  {sidebar}
  <div class="main">
    <form class="search-bar" action="/" method="get">
      <input type="text" name="q" placeholder="搜索知识库..." value="{esc_q}">
      <button type="submit">搜索</button>
    </form>
    <div class="stats-line">{' · '.join(stats_parts)}</div>
    {empty_html}
    <div class="card-grid">{entries_html}</div>
  </div>
</div>
</body></html>"""


def render_detail_page(entry, back_q, back_type):
    st = entry.get("content_subtype", "") or ""
    style = TYPE_STYLES.get(st, DEFAULT_STYLE)
    icon = style["icon"]
    border = style["border"]
    bg = style["bg"]
    eid = esc(entry.get("id", ""))
    title = esc(entry.get("title"))
    summary = esc(entry.get("summary") or "")
    content = esc(entry.get("content") or "")
    source_url = entry.get("source_url") or ""
    created = fmt_time(entry.get("created_at"))
    updated = fmt_time(entry.get("updated_at"))

    tags_raw = entry.get("tags", [])
    if isinstance(tags_raw, str):
        try:
            tags_raw = json.loads(tags_raw)
        except (json.JSONDecodeError, TypeError):
            tags_raw = []
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in tags_raw)
    st_html = f'<span class="st">{esc(st)}</span>' if st else ""

    sd = entry.get("structured_data", {})
    sd_html = ""
    if isinstance(sd, str):
        try:
            sd = json.loads(sd)
        except (json.JSONDecodeError, TypeError):
            sd = {}
    if sd:
        rows = "".join(f'<tr><td class="sd-key">{esc(k)}</td><td class="sd-val">{esc(str(v))}</td></tr>' for k, v in sd.items())
        sd_html = f'<div class="detail-section"><h3>结构化数据</h3><table class="sd-table">{rows}</table></div>'

    source_html = f'<div class="detail-section"><h3>来源</h3><a href="{esc(source_url)}" class="source-link" target="_blank">{esc(source_url)}</a></div>' if source_url else ""

    back = "/"
    if back_q:
        back += "?q=" + urllib.parse.quote(back_q)
    elif back_type:
        back += "?type=" + urllib.parse.quote(back_type)

    types_list = get_extract_types_with_counts()
    sidebar = render_sidebar(types_list, back_type, back_q, "", f"当前条目")
    page_title = f"{title} — MarkAI"

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title><style>{BASE_CSS}</style></head><body>
<div class="wrapper">
  {sidebar}
  <div class="main">
    <div class="breadcrumb"><a href="{back}">← 首页</a><span>/</span><span>{title}</span></div>

    <div class="detail-header">
      <div class="detail-icon" style="background:{bg};border-color:{border}">{icon}</div>
      <div>
        <div class="detail-title">{title}</div>
        <div class="detail-meta">{st_html}{tags_html}</div>
      </div>
    </div>

    {f'<div class="detail-section"><div class="detail-summary">{summary}</div></div>' if summary else ""}

    <div class="detail-section"><h3>内容</h3><div class="detail-content">{content}</div></div>

    {sd_html}
    {source_html}

    <div class="detail-footer">
      <div style="flex:1">
        {f'<span>创建: {created}</span>' if created else ""}
        {f' · 更新: {updated}</span>' if updated else ""}
        <span style="margin-left:12px">ID: {eid}</span>
      </div>
      <a href="/delete?id={eid}" class="btn btn-danger">🗑 删除</a>
    </div>
  </div>
</div>
</body></html>"""


def render_confirm_delete(entry):
    eid = esc(entry.get("id", ""))
    title = esc(entry.get("title", ""))
    types_list = get_extract_types_with_counts()
    sidebar = render_sidebar(types_list, "", "", "", "确认删除")

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>删除确认 — MarkAI</title><style>{BASE_CSS}</style></head><body>
<div class="wrapper">
  {sidebar}
  <div class="main">
  <div class="breadcrumb"><a href="/">← 首页</a><span>/</span><span>删除</span></div>
  <div class="confirm-box">
    <h2>⚠️ 确认删除</h2>
    <p>确定要删除「{title}」吗？此操作不可撤销。</p>
    <div class="actions">
      <a href="/detail?id={eid}" class="btn btn-secondary">取消</a>
      <a href="/delete?id={eid}&confirm=1" class="btn btn-danger">确认删除</a>
    </div>
  </div>
  </div>
</div>
</body></html>"""


def render_stats_page():
    stats = get_stats()
    types_data = get_all_types()
    total = stats.get("total_entries", 0)
    by_type = stats.get("by_type", {})
    top_tags = stats.get("top_tags", [])
    date_range = stats.get("date_range", {})
    week = stats.get("recent_week", {})

    type_rows = "".join(f'<div class="stat-list-row"><span class="stat-list-key">{esc(k)}</span><span class="stat-list-val">{v}</span></div>' for k, v in sorted(by_type.items()))
    tag_rows = "".join(f'<div class="stat-list-row"><span class="stat-list-key">{esc(k[0])}</span><span class="stat-list-val">{k[1]}</span></div>' for k in top_tags[:15])
    week_rows = "".join(f'<div class="stat-list-row"><span class="stat-list-key">{esc(k)}</span><span class="stat-list-val">{v}</span></div>' for k, v in sorted(week.items()))

    first = date_range.get("first", "")[:10] if date_range.get("first") else "-"
    last = date_range.get("last", "")[:10] if date_range.get("last") else "-"

    types_list = get_extract_types_with_counts()
    sidebar = render_sidebar(types_list, "", "", "", "统计面板", show_all_active=False)

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>统计 — MarkAI</title><style>{BASE_CSS}</style></head><body>
<div class="wrapper">
  {sidebar}
  <div class="main stats-page">
    <h2>📊 统计概览</h2>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">总条目</div></div>
      <div class="stat-card"><div class="stat-num">{len(types_data)}</div><div class="stat-label">类型数</div></div>
      <div class="stat-card"><div class="stat-num">{len(top_tags)}</div><div class="stat-label">标签数</div></div>
      <div class="stat-card"><div class="stat-num">{sum(week.values())}</div><div class="stat-label">本周新增</div></div>
    </div>

    <h2>类型分布</h2>
    <div class="stat-list">{type_rows}</div>

    <h2>热门标签</h2>
    <div class="stat-list">{tag_rows}</div>

    <h2>最近活跃</h2>
    <div class="stat-list">{week_rows}</div>

    <h2>时间范围</h2>
    <div class="stat-list">
      <div class="stat-list-row"><span class="stat-list-key">最早</span><span class="stat-list-val">{esc(first)}</span></div>
      <div class="stat-list-row"><span class="stat-list-key">最近</span><span class="stat-list-val">{esc(last)}</span></div>
    </div>
  </div>
</div>
</body></html>"""


def render_list_page(type_name, extracts, type_info):
    """渲染清单列表页"""
    icon = type_info.get("icon", "📌")
    color = type_info.get("color", "#6366f1")
    fields = type_info.get("fields", [])
    field_labels = {f["name"]: f.get("label", f["name"]) for f in fields}
    field_keys = [f["name"] for f in fields]

    # 统计汇总
    summary_config = type_info.get("summary_config", {})
    sc_type = summary_config.get("type", "count")
    total = len(extracts)

    summary_html = ""
    if sc_type == "count":
        summary_html = f'<div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">共 {esc(type_name)}</div></div>'
    elif sc_type == "count_by":
        sub_field = summary_config.get("field", "type")
        counts = {}
        for e in extracts:
            val = e["data"].get(sub_field, "unknown")
            counts[val] = counts.get(val, 0) + 1
        summary_html = "".join(
            f'<div class="stat-card"><div class="stat-num">{v}</div><div class="stat-label">{esc(k)}</div></div>'
            for k, v in sorted(counts.items())
        )
    elif sc_type == "sum_by":
        sub_field = summary_config.get("field", "type")
        subfields = summary_config.get("subfields", {})
        sums = {}
        for e in extracts:
            val = e["data"].get(sub_field, "other")
            amt = e["data"].get("amount", 0) or 0
            try:
                amt = float(amt)
            except (ValueError, TypeError):
                amt = 0
            sums[val] = sums.get(val, 0) + amt
        summary_html = "".join(
            f'<div class="stat-card"><div class="stat-num">¥{sums[k]:.0f}</div><div class="stat-label">{esc(subfields.get(k, k))}</div></div>'
            for k in ["in", "out", "lend", "borrow"] if k in sums
        )
    elif sc_type == "countdown":
        now_iso = str(datetime.now(timezone.utc))[:10]
        upcoming = sum(1 for e in extracts if str(e["data"].get("date", "")) >= now_iso if e["data"].get("date"))
        expired = total - upcoming
        summary_html = f'<div class="stat-card"><div class="stat-num">{upcoming}</div><div class="stat-label">即将到来</div></div><div class="stat-card"><div class="stat-num">{expired}</div><div class="stat-label">已过期</div></div>'

    # 表格行
    rows_html = ""
    for e in extracts:
        data = e["data"]
        vals = " · ".join(str(data.get(k, "")) for k in field_keys if data.get(k))
        bold_val = esc(str(data.get(field_keys[0], ""))) if field_keys else ""
        eid = esc(e.get("id", ""))
        rows_html += f'<div class="extract-row" onclick="window.location.href=\'/notes?id={esc(e["note_id"])}\'">'
        rows_html += f'<div class="extract-title">{bold_val}</div>'
        if vals:
            rows_html += f'<div class="extract-detail">{esc(vals)}</div>'
        rows_html += "</div>"

    types_list = get_extract_types_with_counts()
    sidebar = render_sidebar(types_list, type_name, "", "", "", show_all_active=False)

    page_title = f"{icon} {type_name} — MarkAI"

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title><style>{BASE_CSS}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-bottom:20px}}
.extract-row{{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:10px;padding:14px;margin-bottom:8px;cursor:pointer;transition:0.15s}}
.extract-row:hover{{border-color:{color};background:#1e1e3a}}
.extract-title{{font-size:15px;font-weight:600;color:#f1f5f9;margin-bottom:4px}}
.extract-detail{{font-size:13px;color:#94a3b8}}
</style></head><body>
<div class="wrapper">
  {sidebar}
  <div class="main">
    <div class="breadcrumb"><a href="/">← 首页</a><span>/</span><span>{icon} {esc(type_name)}</span></div>
    <div class="stats-grid">{summary_html}</div>
    <div class="stats-line">共 {len(extracts)} 条</div>
    {rows_html if rows_html else f'<div class="empty-state"><div class="empty-icon">{icon}</div><div class="empty-title">暂无{esc(type_name)}</div><div class="empty-desc">还没有记录，说「记住 xxx」来添加</div></div>'}
  </div>
</div>
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        parts = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parts.query))
        path = parts.path

        try:
            if path == "/":
                query = params.get("q", "").strip()
                active_type = params.get("type", "").strip()
                tag = params.get("tag", "").strip()
                types_list = get_extract_types_with_counts()

                if tag:
                    entries = [e for e in list_entries(limit=99999) if tag in (e.get("tags") or [])]
                elif active_type:
                    entries = get_typed(active_type, limit=99999)
                elif query:
                    entries = search_entries_ranked(query, limit=99999)
                else:
                    entries = list_entries(limit=99999)

                html = render_page(entries, tag or query, active_type, types_list)
                self._html(html)

            elif path == "/list":
                type_name = params.get("type", "").strip()
                if not type_name:
                    self.redirect("/")
                    return
                types_all = get_extract_types_with_counts()
                type_info = None
                for t in types_all:
                    if t["name"] == type_name:
                        type_info = t
                        break
                if not type_info:
                    self._html(render_page([], "", "", get_extract_types_with_counts()))
                    return
                extracts = get_extracts(type_name=type_name, limit=99999)
                html = render_list_page(type_name, extracts, type_info)
                self._html(html)

            elif path == "/detail":
                entry_id = params.get("id", "").strip()
                if not entry_id:
                    self._html(render_page([], "", "", get_extract_types_with_counts()))
                    return
                entry = get_entry(entry_id)
                if not entry:
                    self._html(render_page([], "", "", get_extract_types_with_counts()))
                    return
                back_q = params.get("q", "")
                back_type = params.get("type", "")
                html = render_detail_page(entry, back_q, back_type)
                self._html(html)

            elif path == "/delete":
                entry_id = params.get("id", "").strip()
                if not entry_id:
                    self._html(render_page([], "", "", get_extract_types_with_counts()))
                    return
                entry = get_entry(entry_id)
                if not entry:
                    self._html(render_page([], "", "", get_extract_types_with_counts()))
                    return
                if params.get("confirm") == "1":
                    delete_entry(entry_id)
                    self.redirect("/")
                    return
                html = render_confirm_delete(entry)
                self._html(html)

            elif path == "/stats":
                html = render_stats_page()
                self._html(html)

            elif path == "/api/list":
                page = int(params.get("page", 1))
                limit = int(params.get("limit", 99999))
                raw = list_entries(limit=limit, offset=(page - 1) * limit)
                for e in raw: e.pop("structured_data", None)
                self.json(raw)
            elif path == "/api/search":
                self.json(search_entries_ranked(params.get("q", ""), limit=99999))
            elif path == "/api/get":
                e = get_entry(params.get("id", ""))
                self.json(e if e else {"error": "not found"})
            elif path == "/api/types":
                self.json(get_all_types())
            elif path == "/api/typed":
                self.json(get_typed(params.get("subtype", ""), limit=99999))
            elif path == "/api/stats":
                self.json(get_stats())
            else:
                self.json({"error": "not found"}, 404)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.json({"error": str(e)}, 500)

    def _html(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Connection", "close")
        self.end_headers()

    def json(self, data, code=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *a):
        pass


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8888)
    a = p.parse_args()
    init_db()
    httpd = http.server.HTTPServer((HOST, a.port), Handler)
    print(f"MarkAI → http://{HOST}:{a.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    main()
