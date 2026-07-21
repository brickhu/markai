#!/usr/bin/env python3
"""
MarkAI Web Server — browse and search your knowledge in browser.
Usage: python3 serve.py [--port 8888]
"""

import json
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import (
    init_db, list_entries, search_entries, search_entries_ranked,
    get_entry, get_typed, get_all_types, get_stats
)

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    print("❌ http.server not available (should be part of Python stdlib)")
    sys.exit(1)

HOST = "127.0.0.1"
PORT = 8888


class MarkAIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        params = {}
        if '?' in self.path:
            for p in self.path.split('?')[1].split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    from urllib.parse import unquote
                    params[k] = unquote(v)
        try:
            if path == '/':
                self._serve_file('static/index.html')
            elif path == '/api/list':
                page = int(params.get('page', 1))
                limit = int(params.get('limit', 15))
                offset = (page - 1) * limit
                entries = list_entries(limit=limit, offset=offset)
                self._json(entries)
            elif path == '/api/search':
                q = params.get('q', '')
                results = search_entries_ranked(q, limit=30)
                self._json(results)
            elif path == '/api/get':
                entry = get_entry(params.get('id', ''))
                self._json(entry)
            elif path == '/api/types':
                self._json(get_all_types())
            elif path == '/api/stats':
                self._json(get_stats())
            elif path == '/api/typed':
                subtype = params.get('subtype', '')
                entries = get_typed(subtype, limit=50)
                self._json(entries)
            elif path == '/api/search_raw':
                q = params.get('q', '')
                results = search_entries(q, limit=30)
                self._json(results)
            else:
                self._json({"error": "not found"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _serve_file(self, relpath):
        full_path = Path(__file__).parent / relpath
        if not full_path.exists():
            self.send_response(404)
            self.end_headers()
            return
        content = full_path.read_bytes()
        content_type = 'text/html; charset=utf-8'
        if relpath.endswith('.css'):
            content_type = 'text/css; charset=utf-8'
        elif relpath.endswith('.js'):
            content_type = 'application/javascript; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def _html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        sys.stderr.write(f"  {args[0]} {args[1]} {args[2]}\n")


def main():
    global PORT
    import argparse
    parser = argparse.ArgumentParser(description='MarkAI Web Server')
    parser.add_argument('--port', type=int, default=8888, help='Port to listen on')
    args = parser.parse_args()
    PORT = args.port

    init_db()
    server = HTTPServer((HOST, PORT), MarkAIHandler)
    print(f"📌 MarkAI Web UI running at:")
    print(f"   http://{HOST}:{PORT}")
    print(f"   Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()


if __name__ == "__main__":
    main()
