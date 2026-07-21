#!/usr/bin/env python3
"""
MarkAI Web Server — browse and search your knowledge in browser.
Usage: python3 serve.py [--port 8888]
"""

import json
import sys
import os
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

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarkAI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f0f1a;color:#e0e0e0;padding:20px;max-width:960px;margin:0 auto}
h1{font-size:24px;margin-bottom:20px;color:#a78bfa}
.search-box{display:flex;gap:10px;margin-bottom:20px}
.search-box input{flex:1;padding:12px 16px;border:1px solid #2a2a3e;border-radius:8px;background:#1a1a2e;color:#e0e0e0;font-size:16px}
.search-box button{padding:12px 24px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px}
.filters{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.filters button{padding:6px 14px;border:1px solid #2a2a3e;border-radius:16px;background:transparent;color:#a78bfa;cursor:pointer;font-size:13px}
.filters button.active,.filters button:hover{background:#7c3aed22;border-color:#7c3aed}
.stats{color:#888;font-size:13px;margin-bottom:16px}
.entry{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:10px;padding:16px;margin-bottom:12px;cursor:pointer}
.entry:hover{border-color:#7c3aed}
.entry .title{font-size:16px;font-weight:600;margin-bottom:6px}
.entry .meta{font-size:12px;color:#888;margin-bottom:6px}
.entry .summary{font-size:14px;color:#aaa;line-height:1.5}
.tag{display:inline-block;padding:2px 8px;background:#2a2a3e;border-radius:10px;font-size:11px;color:#a78bfa;margin:2px}
.subtype{display:inline-block;padding:2px 8px;background:#7c3aed22;border-radius:10px;font-size:11px;color:#7c3aed;margin:2px}
.pages{display:flex;justify-content:center;gap:10px;margin-top:20px}
.pages button{padding:8px 20px;border:1px solid #2a2a3e;border-radius:8px;background:transparent;color:#a78bfa;cursor:pointer}
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:#000000aa;z-index:100}
.modal.show{display:flex;align-items:center;justify-content:center}
.modal-content{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:24px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto}
.modal-content h2{color:#a78bfa;margin-bottom:12px}
.modal-content .field{margin-bottom:10px}
.modal-content .field-label{font-size:12px;color:#666;margin-bottom:2px}
.modal-content .field-value{font-size:15px;color:#e0e0e0;word-break:break-all}
.modal-content pre{background:#0f0f1a;padding:12px;border-radius:8px;font-size:13px;color:#a78bfa;overflow-x:auto;margin-top:10px}
.close-btn{float:right;background:none;border:none;color:#888;font-size:24px;cursor:pointer}
</style></head><body>
<h1>📌 MarkAI</h1>
<div class="filters" id="filters">
  <button class="active" onclick="loadAll(1)">全部</button>
</div>
<div class="search-box">
  <input id="q" placeholder="搜索知识库..." onkeydown="if(event.key==='Enter')doSearch()">
  <button onclick="doSearch()">搜索</button>
</div>
<div id="stats" class="stats"></div>
<div id="results"></div>
<div class="pages" id="pages"></div>
<div class="modal" id="modal" onclick="if(event.target===this)closeModal()">
  <div class="modal-content" id="modalContent"></div>
</div>
<script>
var page=1,currentType='';
async function api(u){return (await fetch(u)).json()}
function setActive(btn){document.querySelectorAll('#filters button').forEach(b=>b.classList.remove('active'));btn.classList.add('active')}
async function loadAll(p){page=p;currentType='';setActive(document.querySelector('#filters button'));const d=await api('/api/list?page='+p+'&limit=15');render(d,p)}
async function loadType(t){page=1;currentType=t;document.getElementById('q').value='';const d=await api('/api/typed?subtype='+t+'&limit=15');render(d,1)}
async function doSearch(){const q=document.getElementById('q').value.trim();if(!q)return loadAll(1);currentType='';const d=await api('/api/search?q='+encodeURIComponent(q));render(d,1)}
async function initFilters(){const types=await api('/api/types');const f=document.getElementById('filters');types.forEach(t=>{const b=document.createElement('button');b.textContent=t.subtype+' ('+t.count+')';b.onclick=function(){setActive(b);loadType(t.subtype)};f.appendChild(b)})}
function render(data,p){
  const r=document.getElementById('results'),s=document.getElementById('stats');
  const entries=data.entries||data;
  s.textContent='共 '+entries.length+' 条';
  if(!entries.length){r.innerHTML='<p style="color:#888;margin-top:40px;text-align:center">📭 暂无内容</p>';document.getElementById('pages').innerHTML='';return}
  r.innerHTML=entries.map(e=>'<div class="entry" onclick="showDetail(\''+e.id+'\')">'+
    '<div class="title">'+h(e.title)+'</div>'+
    (e.content_subtype? '<span class="subtype">'+h(e.content_subtype)+'</span> ':'')+
    (e.tags||[]).map(t=>'<span class="tag">'+h(t)+'</span>').join('')+
    (e.summary? '<div class="summary">'+h(e.summary)+'</div>':'')+
  '</div>').join('');
  document.getElementById('pages').innerHTML=p?('<button onclick="loadAll('+(p-1)+')" '+(p<=1?'disabled style="opacity:0.3"':'')+'>← 上一页</button>'+
    '<span style="color:#666;line-height:32px"> 第 '+p+' 页 </span>'+
    '<button onclick="loadAll('+(p+1)+')">下一页 →</button>'):'';
}
async function showDetail(id){const e=await api('/api/get?id='+id);if(!e||e.error)return;
  const m=document.getElementById('modalContent');
  m.innerHTML='<button class="close-btn" onclick="closeModal()">×</button><h2>'+h(e.title)+'</h2>'+
    (e.content_subtype? '<div class="field"><div class="field-label">类型</div><div class="field-value">'+h(e.content_subtype)+'</div></div>':'')+
    (e.tags&&e.tags.length? '<div class="field"><div class="field-label">标签</div><div class="field-value">'+e.tags.map(t=>'<span class="tag">'+h(t)+'</span>').join(' ')+'</div></div>':'')+
    (e.summary? '<div class="field"><div class="field-label">摘要</div><div class="field-value">'+h(e.summary)+'</div></div>':'')+
    '<div class="field"><div class="field-label">内容</div><div class="field-value" style="color:#aaa">'+h(e.content||'')+'</div></div>'+
    (e.source_url? '<div class="field"><div class="field-label">来源</div><div class="field-value"><a href="'+h(e.source_url)+'" style="color:#60a5fa">'+h(e.source_url)+'</a></div></div>':'')+
    '<div class="field" style="margin-top:12px;color:#555;font-size:12px">🆔 '+h(e.id)+' · 📅 '+h((e.created_at||'').slice(0,10))+'</div>';
  document.getElementById('modal').classList.add('show');
}
function closeModal(){document.getElementById('modal').classList.remove('show')}
function h(t){if(!t)return '';const d=document.createElement('div');d.textContent=t;return d.innerHTML}
initFilters();
loadAll(1);
</script></body></html>"""


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
                self._html(HTML)
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
