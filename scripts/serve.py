#!/usr/bin/env python3
"""MarkAI Web Server"""
import json, sys, os, http.server, urllib.parse
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import init_db, list_entries, search_entries_ranked, get_entry, get_typed, get_all_types, get_stats

HOST = "127.0.0.1"

INDEX = """<!DOCTYPE html><html><body>
<h2>MarkAI</h2>
<div id="s">Loading...</div>
<div id="list"></div>
<script>
var A=[],N=0;
function $(i){return document.getElementById(i)}
function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML}
function go(){fetch('/api/list?limit=99999').then(function(r){return r.json()}).then(function(d){var entries=d.entries||d;document.getElementById('s').textContent='OK: '+entries.length+' entries, first: '+entries[0].title}).catch(function(e){document.getElementById('s').textContent='JSON ERR: '+JSON.stringify(e)})}
function more(){var nx=Math.min(N+20,A.length),h='';for(var i=N;i<nx;i++){var e=A[i];h+='<div style="padding:8px;border:1px solid #ccc;margin:4px">'+esc(e.title)+'</div>'}if(h){$('list').innerHTML+=h;N=nx;$('s').textContent=A.length+' entries'}}
go();
</script></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parts = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parts.query))
        path = parts.path
        try:
            if path == "/":
                self._html(INDEX)
            elif path == "/api/list":
                page = int(params.get("page", 1))
                limit = int(params.get("limit", 99999))
                raw = list_entries(limit=limit, offset=(page-1)*limit)
                # strip structured_data to keep JSON parseable in browser
                for e in raw:
                    e.pop("structured_data", None)
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
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.wfile.write(payload)
        self.wfile.flush()

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
