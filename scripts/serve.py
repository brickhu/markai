#!/usr/bin/env python3
"""MarkAI Web Server"""
import json, sys, os, http.server, urllib.parse
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import init_db, list_entries, search_entries_ranked, get_entry, get_typed, get_all_types, get_stats

HOST = "127.0.0.1"

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        parts = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parts.query))
        path = parts.path
        try:
            if path == "/":
                # Server-side rendered HTML
                entries = list_entries(limit=99999)
                rows = ""
                for e in entries:
                    title = e.get("title", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    summary = (e.get("summary", "") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    st = e.get("content_subtype", "") or ""
                    tags = json.loads(e.get("tags", "[]")) if isinstance(e.get("tags"), str) else (e.get("tags") or [])
                    tag_html = "".join(f'<span class="t">{t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</span>' for t in tags)
                    st_html = f'<span class="st">{st}</span>' if st else ""
                    summary_html = f'<div class="d">{summary}</div>' if summary else ""
                    rows += f'<div class="c">{st_html}{tag_html}<div class="t">{title}</div>{summary_html}</div>'
                html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>MarkAI</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:sans-serif;background:#111;color:#ddd;padding:20px;max-width:800px;margin:0 auto}}
h1{{color:#a78bfa;font-size:22px;margin-bottom:20px}}
.c{{background:#1a1a2e;border:1px solid #333;border-radius:8px;padding:12px;margin-bottom:8px}}
.t{{font-size:15px;font-weight:600;margin-bottom:3px}}
.d{{font-size:13px;color:#aaa}}
.st{{display:inline-block;padding:2px 8px;background:#7c3aed22;border-radius:8px;font-size:11px;color:#7c3aed;margin:2px}}
.t{{display:inline-block;padding:2px 8px;background:#333;border-radius:8px;font-size:11px;color:#a78bfa;margin:2px}}
.stats{{color:#888;font-size:13px;margin-bottom:16px}}
</style></head><body>
<h1>MarkAI</h1>
<div class="stats">{len(entries)} entries</div>
{rows}
</body></html>"""
                self._html(html)
            elif path == "/api/list":
                page = int(params.get("page", 1))
                limit = int(params.get("limit", 99999))
                raw = list_entries(limit=limit, offset=(page-1)*limit)
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
