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
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MarkAI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f0f1a;color:#e0e0e0;padding:20px;max-width:960px;margin:0 auto}
h1{font-size:24px;margin-bottom:20px;color:#a78bfa}
.search-box{display:flex;gap:10px;margin-bottom:20px}
.search-box input{flex:1;padding:12px 16px;border:1px solid #2a2a3e;border-radius:8px;background:#1a1a2e;color:#e0e0e0;font-size:16px}
.search-box button{padding:12px 24px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px}
.search-box button:hover{background:#6d28d9}
.filters{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.filters button{padding:6px 14px;border:1px solid #2a2a3e;border-radius:16px;background:transparent;color:#a78bfa;cursor:pointer;font-size:13px}
.filters button.active{background:#7c3aed;color:#fff;border-color:#7c3aed}
*:has(#stats){}
.stats{color:#888;font-size:13px;margin-bottom:16px}
.entry{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:10px;padding:16px;margin-bottom:12px;cursor:pointer}
.entry:hover{border-color:#7c3aed}
.entry .title{font-size:16px;font-weight:600;color:#e0e0e0;margin-bottom:6px}
.entry .meta{font-size:12px;color:#888;margin-bottom:6px}
.entry .summary{font-size:14px;color:#aaa;line-height:1.5}
.entry .tag{display:inline-block;padding:2px 8px;background:#2a2a3e;border-radius:10px;font-size:11px;color:#a78bfa;margin:2px}
.entry .subtype{display:inline-block;padding:2px 8px;background:#7c3aed22;border-radius:10px;font-size:11px;color:#7c3aed;margin:2px}
.pages{display:flex;justify-content:center;gap:10px;margin-top:20px}
.pages button{padding:8px 20px;border:1px solid #2a2a3e;border-radius:8px;background:transparent;color:#a78bfa;cursor:pointer}
.pages button:hover{background:#2a2a3e}
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:#000000aa;z-index:100}
.modal.show{display:flex;align-items:center;justify-content:center}
.modal-content{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:24px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto}
.modal-content h2{color:#a78bfa;margin-bottom:12px}
.modal-content .field{margin-bottom:10px}
.modal-content .field-label{font-size:12px;color:#666;margin-bottom:2px}
.modal-content .field-value{font-size:15px;color:#e0e0e0;word-break:break-all}
.modal-content pre{background:#0f0f1a;padding:12px;border-radius:8px;font-size:13px;color:#a78bfa;overflow-x:auto;margin-top:10px}
.close-btn{float:right;background:none;border:none;color:#888;font-size:24px;cursor:pointer}
.close-btn:hover{color:#fff}
#toast{position:fixed;bottom:20px;right:20px;padding:12px 24px;border-radius:8px;font-size:14px;display:none;z-index:200}
#toast.ok{background:#065f46;color:#6ee7b7;display:block}
#toast.err{background:#7f1d1d;color:#fca5a5;display:block}
</style>
</head>
<body>
<h1>📌 MarkAI</h1>
<div class="filters">
  <button class="active" onclick="loadEntries(1)">全部</button>
  <button onclick="loadType('contact')">📞 联系人</button>
  <button onclick="loadType('expense')">💰 开支</button>
  <button onclick="loadType('reminder')">⏰ 提醒</button>
  <button onclick="loadType('flight')">✈️ 航班</button>
  <button onclick="showAllTypes()">🏷 更多...</button>
</div>
<div class="search-box">
  <input id="q" placeholder="搜索知识库..." onkeydown="if(event.key=='Enter')search()"/>
  <button onclick="search()">搜索</button>
</div>
<div id="stats" class="stats"></div>
<div id="results"></div>
<div class="pages" id="pages"></div>
<div class="modal" id="modal" onclick="if(event.target==this)closeModal()">
  <div class="modal-content" id="modalContent"></div>
</div>
<div id="toast"></div>
<script>
let currentType = '', currentQuery = '', currentPage = 1;
async function api(url){const r=await fetch(url);return r.json()}
function showToast(msg,type){const t=document.getElementById('toast');t.textContent=msg;t.className=type;setTimeout(()=>t.classList.remove('ok','err'),3000)}
document.querySelectorAll('.filters button').forEach(b=>b.addEventListener('click',function(){document.querySelectorAll('.filters button').forEach(b=>b.classList.remove('active'));this.classList.add('active')}))

async function loadEntries(page){
  currentPage=page;currentType='';currentQuery='';
  const data=await api('/api/list?page='+page+'&limit=15');
  render(data,page,'')
}
async function loadType(subtype){
  currentPage=1;currentType=subtype;currentQuery='';
  document.getElementById('q').value='';
  const data=await api('/api/typed?subtype='+subtype+'&limit=15');
  render({entries:data,type:subtype},1,subtype)
}
async function search(){
  const q=document.getElementById('q').value.trim();
  if(!q)return loadEntries(1);
  currentQuery=q;currentType='';currentPage=1;
  const data=await api('/api/search?q='+encodeURIComponent(q));
  render({entries:data,type:'search'},1,'')
}
async function showAllTypes(){
  const t=await api('/api/types');
  let h='<div class="filters" style="margin-bottom:0">';
  t.forEach(t=>{h+='<button onclick="loadType(\''+t.subtype+'\')">'+t.subtype+' ('+t.count+')</button>'});
  h+='<button onclick="loadEntries(1)">返回全部</button></div>';
  document.getElementById('results').innerHTML=h;
}
function render(data,page,type){
  const r=document.getElementById('results');
  const p=document.getElementById('pages');
  const s=document.getElementById('stats');
  if(data.error){r.innerHTML='<p style="color:#f87171">'+data.error+'</p>';p.innerHTML='';return}
  const entries=data.entries||data;
  s.textContent='共 '+entries.length+' 条';
  if(entries.length===0){r.innerHTML='<p style="color:#888;text-align:center;margin-top:40px">📭 暂无内容</p>';p.innerHTML='';return}
  let html='';
  entries.forEach(e=>{
    const tags=e.tags||[];
    const st=e.content_subtype||'';
    const structured=window.structuredData&&window.structuredData[e.id]||{};
    html+='<div class="entry" onclick="showDetail(\''+e.id+'\')">';
    html+='<div class="title">'+escapeHtml(e.title||'(无标题)')+'</div>';
    if(st)html+='<span class="subtype">'+escapeHtml(st)+'</span> ';
    tags.forEach(t=>{html+='<span class="tag">'+escapeHtml(t)+'</span>'});
    if(e.summary)html+='<div class="summary">'+escapeHtml(e.summary)+'</div>';
    // structured fields mini display
    for(const[k,v]of Object.entries(structured)){
      if(typeof v==='string'&&v.length<30)html+='<span class="tag" style="color:#60a5fa">'+escapeHtml(k)+': '+escapeHtml(v)+'</span>'
    }
    html+='</div>';
  });
  r.innerHTML=html;
  p.innerHTML='<button onclick="loadEntries('+(page-1)+')" '+(page<=1?'disabled style="opacity:0.4"':'')+'>← 上一页</button><span style="color:#666;line-height:32px"> 第 '+page+' 页 </span><button onclick="loadEntries('+(page+1)+')">下一页 →</button>';
}
async function showDetail(id){
  const e=await api('/api/get?id='+id);
  if(!e||e.error){showToast('未找到','err');return}
  const m=document.getElementById('modalContent');
  const sd=e.structured_data||{};
  const st=e.content_subtype||'';
  let shtml='<button class="close-btn" onclick="closeModal()">×</button><h2>'+escapeHtml(e.title)+'</h2>';
  if(st)shtml+='<div class="field"><div class="field-label">类型</div><div class="field-value">'+escapeHtml(st)+'</div></div>';
  if(e.tags&&e.tags.length)shtml+='<div class="field"><div class="field-label">标签</div><div class="field-value">'+e.tags.map(t=>'<span class="tag">'+escapeHtml(t)+'</span>').join(' ')+'</div></div>';
  if(e.summary)shtml+='<div class="field"><div class="field-label">摘要</div><div class="field-value">'+escapeHtml(e.summary)+'</div></div>';
  shtml+='<div class="field"><div class="field-label">内容</div><div class="field-value" style="color:#aaa">'+escapeHtml(e.content||'')+'</div></div>';
  if(e.source_url)shtml+='<div class="field"><div class="field-label">来源</div><div class="field-value"><a href="'+escapeHtml(e.source_url)+'" style="color:#60a5fa">'+escapeHtml(e.source_url)+'</a></div></div>';
  if(Object.keys(sd).length){
    shtml+='<div class="field"><div class="field-label">结构化数据</div><pre>'+escapeHtml(JSON.stringify(sd,null,2))+'</pre></div>';
  }
  shtml+='<div class="field" style="margin-top:12px;color:#555;font-size:12px">🆔 '+escapeHtml(e.id)+' · 📅 '+escapeHtml((e.created_at||'').slice(0,10))+'</div>';
  m.innerHTML=shtml;
  document.getElementById('modal').classList.add('show');
}
function closeModal(){document.getElementById('modal').classList.remove('show')}
function escapeHtml(t){if(!t)return '';const d=document.createElement('div');d.textContent=t;return d.innerHTML}
loadEntries(1);
</script>
</body>
</html>"""


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
