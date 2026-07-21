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
<script>
var r=new XMLHttpRequest();
r.open('GET','/api/stats',true);
r.onload=function(){
  var d=JSON.parse(r.responseText);
  document.getElementById('s').textContent='Stats OK: '+d.total_entries+' entries, loading list...';
  var r2=new XMLHttpRequest();
  r2.open('GET','/api/list?limit=99999',true);
  r2.onload=function(){
    var data=JSON.parse(r2.responseText);
    var entries=data.entries||data;
    var h='';
    for(var i=0;i<entries.length;i++) h+='<div style="padding:8px;border:1px solid #ccc;margin:4px;border-radius:4px">'+esc(entries[i].title)+'</div>';
    document.getElementById('s').innerHTML='<p>'+entries.length+' entries:</p>'+h;
  };
  function esc(s){if(!s)return'';var d=document.createElement('div');d.textContent=s;return d.innerHTML}
  r2.onerror=function(){document.getElementById('s').textContent='List failed'};
  r2.send();
};
r.onerror=function(){document.getElementById('s').textContent='Stats failed'};
r.send();
</script></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

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
