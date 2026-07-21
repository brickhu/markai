#!/usr/bin/env python3
"""MarkAI Web Server"""
import json, sys, os, http.server, urllib.parse
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import init_db, list_entries, search_entries_ranked, get_entry, get_typed, get_all_types, get_stats

HOST = "127.0.0.1"
PORT = 8888

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parts = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parts.query))
        path = parts.path
        try:
            if path == "/":
                self.serve("static/index.html", "text/html; charset=utf-8")
            elif path == "/favicon.ico":
                self.serve("static/favicon.ico", "image/x-icon")
            elif path == "/api/list":
                page = int(params.get("page", 1))
                limit = int(params.get("limit", 99999))
                self.json(list_entries(limit=limit, offset=(page-1)*limit))
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
            self.json({"error": str(e)}, 500)

    def serve(self, relpath, mime):
        full = Path(__file__).parent / relpath
        if not full.exists():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.end_headers()
        self.wfile.write(full.read_bytes())

    def json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, *a):
        pass

def main():
    global PORT
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8888)
    a = p.parse_args()
    PORT = a.port
    init_db()
    httpd = http.server.HTTPServer((HOST, PORT), Handler)
    print(f"MarkAI → http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == "__main__":
    main()
