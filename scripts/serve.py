#!/usr/bin/env python3
"""MarkAI Web Server - SSR dual-column layout"""
import json, sys, os, http.server, urllib.parse, html
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import init_db, list_entries, search_entries_ranked, get_entry, get_typed, get_all_types, get_stats

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


def esc(text):
    """HTML escape a string."""
    return html.escape(str(text or ""), quote=True)


def render_card_html(e):
    """Render a single entry card as HTML string."""
    st = e.get("content_subtype", "") or ""
    style = TYPE_STYLES.get(st, DEFAULT_STYLE)
    icon = style["icon"]
    bg = style["bg"]
    border = style["border"]

    title = esc(e.get("title"))
    summary = esc(e.get("summary") or "")
    tags_raw = e.get("tags", [])
    if isinstance(tags_raw, str):
        try:
            tags_raw = json.loads(tags_raw)
        except (json.JSONDecodeError, TypeError):
            tags_raw = []
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in tags_raw[:5])
    st_html = f'<span class="st">{esc(st)}</span>' if st else ""

    return f"""<div class="card" style="background:{bg};border-color:{border}">
  <div class="card-icon">{icon}</div>
  <div class="card-body">
    <div class="card-title">{title}</div>
    <div class="card-meta">{st_html}{tags_html}</div>
    {f'<div class="card-summary">{summary}</div>' if summary else ""}
  </div>
</div>"""


def render_page(entries, query, active_type, types_list):
    """Render full HTML page with dual-column layout."""
    entries_html = "\n".join(render_card_html(e) for e in entries)

    nav_buttons = ""
    active_class = "active" if not active_type and not query else ""
    esc_q = esc(query)

    nav_buttons += f'<a href="/" class="nav-btn {active_class}">📌 全部</a>\n'
    for t in types_list:
        sn = t["subtype"]
        style = TYPE_STYLES.get(sn, DEFAULT_STYLE)
        cnt = t["count"]
        ac = "active" if active_type == sn else ""
        nav_buttons += f'<a href="/?type={esc(sn)}" class="nav-btn {ac}" style="--nav-c:{style["border"]}">{style["icon"]} {esc(sn)} ({cnt})</a>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarkAI</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f0f1a;color:#e0e0e0;min-height:100vh}}
.wrapper{{display:flex;min-height:100vh}}
.sidebar{{width:240px;flex-shrink:0;background:#16162a;border-right:1px solid #2a2a3e;padding:24px 16px;display:flex;flex-direction:column;gap:4px;position:sticky;top:0;height:100vh;overflow-y:auto}}
.logo{{font-size:20px;font-weight:700;color:#a78bfa;margin-bottom:20px;display:flex;align-items:center;gap:8px}}
.logo small{{font-size:12px;color:#666;font-weight:400}}
.nav-section{{margin-bottom:16px}}
.nav-section-title{{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;padding-left:4px}}
.nav-btn{{display:block;padding:8px 12px;border-radius:8px;color:#aaa;text-decoration:none;font-size:13px;transition:.15s;margin-bottom:2px}}
.nav-btn:hover{{background:#1e1e3a;color:#a78bfa}}
.nav-btn.active{{background:rgba(167,139,250,0.12);color:#a78bfa;font-weight:600;border-left:3px solid #a78bfa;padding-left:9px}}
.nav-btn[style*="--nav-c"]:hover{{border-left-color:var(--nav-c)}}
.main{{flex:1;padding:24px 32px;overflow-y:auto}}
.search-bar{{display:flex;gap:10px;margin-bottom:24px}}
.search-bar input{{flex:1;padding:10px 16px;border:1px solid #2a2a3e;border-radius:8px;background:#1a1a2e;color:#e0e0e0;font-size:15px;outline:none}}
.search-bar input:focus{{border-color:#7c3aed}}
.search-bar button{{padding:10px 20px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:15px}}
.search-bar button:hover{{background:#6d28d9}}
.stats{{color:#888;font-size:13px;margin-bottom:16px}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}}
.card{{border:1px solid;border-radius:12px;padding:16px;display:flex;gap:12px;transition:.15s;cursor:pointer}}
.card:hover{{transform:translateY(-1px);box-shadow:0 4px 20px rgba(0,0,0,0.3)}}
.card-icon{{font-size:24px;flex-shrink:0;width:36px;height:36px;display:flex;align-items:center;justify-content:center}}
.card-body{{flex:1;min-width:0}}
.card-title{{font-size:15px;font-weight:600;color:#f1f5f9;margin-bottom:4px;line-height:1.3}}
.card-meta{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px}}
.card-summary{{font-size:13px;color:#94a3b8;line-height:1.4}}
.tag{{display:inline-block;padding:1px 7px;border-radius:6px;background:rgba(255,255,255,0.08);font-size:11px;color:#a78bfa}}
.st{{display:inline-block;padding:1px 7px;border-radius:6px;background:rgba(167,139,250,0.2);font-size:11px;color:#a78bfa;font-weight:600}}
.stats-line{{color:#888;font-size:13px;margin-bottom:16px}}
a{{color:inherit;text-decoration:none}}
@media(max-width:768px){{.sidebar{{width:100%;height:auto;position:static;flex-direction:row;flex-wrap:wrap;padding:12px 16px;border-right:none;border-bottom:1px solid #2a2a3e}} .wrapper{{flex-direction:column}} .main{{padding:16px}} .nav-btn{{font-size:12px;padding:6px 10px}} .logo{{margin-bottom:12px;width:100%}} .card-grid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="wrapper">
  <div class="sidebar">
    <div class="logo">📌 MarkAI <small>v3</small></div>
    <div class="nav-section">
      <div class="nav-section-title">类型筛选</div>
      {nav_buttons}
    </div>
    <div style="margin-top:auto;padding-top:16px;border-top:1px solid #2a2a3e;font-size:11px;color:#555">
      {len(entries)} 条记忆 · ~/.markai/brain.db
    </div>
  </div>
  <div class="main">
    <form class="search-bar" action="/" method="get">
      <input type="text" name="q" placeholder="搜索知识库..." value="{esc_q}">
      <button type="submit">搜索</button>
    </form>
    <div class="stats-line">{len(entries)} 条{' · 搜索: '+esc_q if query else ''}{' · 类型: '+esc(active_type) if active_type else ''}</div>
    <div class="card-grid">
      {entries_html}
    </div>
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
                types_list = get_all_types()

                if active_type:
                    entries = get_typed(active_type, limit=99999)
                elif query:
                    entries = search_entries_ranked(query, limit=99999)
                else:
                    entries = list_entries(limit=99999)

                html = render_page(entries, query, active_type, types_list)
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
