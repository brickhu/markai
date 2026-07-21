#!/usr/bin/env python3
"""MarkAI Web Server"""
import json, sys, os, http.server, urllib.parse
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain_cli import init_db, list_entries, search_entries, search_entries_ranked, get_entry, get_typed, get_all_types, get_stats

HOST, PORT = "127.0.0.1", 8888

PROD = os.environ.get('ENV') != 'dev'

HTML = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarkAI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f0f1a;color:#e0e0e0;padding:20px;max-width:960px;margin:0 auto}
h1{font-size:24px;margin-bottom:20px;color:#a78bfa}
.ft{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.ft button{padding:6px 14px;border:1px solid #2a2a3e;border-radius:16px;background:transparent;color:#a78bfa;cursor:pointer;font-size:13px}
.ft button.a,.ft button:hover{background:#7c3aed22;border-color:#7c3aed}
.sb{display:flex;gap:10px;margin-bottom:20px}
.sb input{flex:1;padding:12px 16px;border:1px solid #2a2a3e;border-radius:8px;background:#1a1a2e;color:#e0e0e0;font-size:16px;outline:none}
.sb input:focus{border-color:#7c3aed}
.sb button{padding:12px 24px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px}
.st{color:#888;font-size:13px;margin-bottom:16px}
.c{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:10px;padding:16px;margin-bottom:12px;cursor:pointer}
.c:hover{border-color:#7c3aed}
.t{font-size:16px;font-weight:600;margin-bottom:6px}
.s{font-size:14px;color:#aaa;line-height:1.5}
.tag{display:inline-block;padding:2px 8px;background:#2a2a3e;border-radius:10px;font-size:11px;color:#a78bfa;margin:2px}
.stt{display:inline-block;padding:2px 8px;background:#7c3aed22;border-radius:10px;font-size:11px;color:#7c3aed;margin:2px}
#ld{text-align:center;padding:16px;color:#888;cursor:pointer;display:none}
#ld:hover{color:#a78bfa}
.md{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:#000000aa;z-index:100}
.md.s{display:flex;align-items:center;justify-content:center}
.mc{background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:24px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto}
.mc h2{color:#a78bfa;margin-bottom:12px;font-size:20px}
.f{margin-bottom:10px}
.fl{font-size:12px;color:#666;margin-bottom:2px}
.fv{font-size:15px;color:#e0e0e0;word-break:break-all}
pre{background:#0f0f1a;padding:12px;border-radius:8px;font-size:13px;color:#a78bfa;overflow-x:auto;margin-top:10px}
.x{float:right;background:none;border:none;color:#888;font-size:24px;cursor:pointer}
#err{color:#f87171;text-align:center;padding:20px;display:none}
</style></head><body>
<h1>MarkAI</h1>
<div class="ft" id="ft"><button class="a" onclick="loadAll()">全部</button></div>
<div class="sb"><input id="q" placeholder="搜索..." onkeydown="if(event.key==='Enter')qsearch()"><button onclick="qsearch()">搜索</button></div>
<div class="st" id="st"></div>
<div id="list"></div>
<div id="ld" onclick="more()">加载更多</div>
<div id="err"></div>
<div class="md" id="md" onclick="if(event.target==this)close()"><div class="mc" id="mc"></div></div>
<script>
var A=[],N=0,TP='';
function esc(s){if(!s)return '';var d=document.createElement('div');d.textContent=s;return d.innerHTML}
function api(u){return fetch(u).then(function(r){return r.json()})}
function loadAll(){TP='';document.getElementById('q').value='';st('加载中...');api('/api/list?limit=99999').then(function(d){A=d.entries||d;N=0;document.getElementById('list').innerHTML='';more()})}
function loadType(t){TP=t;document.getElementById('q').value='';api('/api/typed?subtype='+t+'&limit=99999').then(function(d){A=d.entries||d;N=0;document.getElementById('list').innerHTML='';more()})}
function qsearch(){var q=document.getElementById('q').value.trim();if(!q)return loadAll();TP='';api('/api/search?q='+encodeURIComponent(q)+'&limit=99999').then(function(d){A=d.entries||d;N=0;document.getElementById('list').innerHTML='';more()})}
function more(){var nx=Math.min(N+20,A.length),h='';for(var i=N;i<nx;i++){var e=A[i];h+='<div class="c" data-id="'+e.id+'"><div class="t">'+esc(e.title)+'</div>';if(e.content_subtype)h+='<span class="stt">'+esc(e.content_subtype)+'</span>';if(e.tags)for(var j=0;j<e.tags.length;j++)h+='<span class="tag">'+esc(e.tags[j])+'</span>';if(e.summary)h+='<div class="s">'+esc(e.summary)+'</div>';h+='</div>'}document.getElementById('list').innerHTML+=h;N=nx;st('共 '+A.length+' 条 | 已显示 '+N+' 条');document.getElementById('ld').style.display=(N<A.length)?'block':'none'}
function st(t){document.getElementById('st').textContent=t}
function init(){document.getElementById('list').onclick=function(e){var p=e.target.closest(".c");if(p\u0026\u0026p.dataset.id)d(p.dataset.id)};
document.getElementById('list').onclick=function(e){var p=e.target.closest('.c');if(p&&p.dataset.id)d(p.dataset.id)};
function d(id){api('/api/get?id='+id).then(function(e){if(!e||e.error)return;var mc=document.getElementById('mc'),h='<button class="x" onclick="close()">x</button><h2>'+esc(e.title)+'</h2>';if(e.content_subtype)h+='<div class="f"><div class="fl">\u7c7b\u578b</div><div class="fv">'+esc(e.content_subtype)+'</div></div>';if(e.tags&&e.tags.length){var th='';for(var i=0;i<e.tags.length;i++)th+='<span class="tag">'+esc(e.tags[i])+'</span>';h+='<div class="f"><div class="fl">\u6807\u7b7e</div><div class="fv">'+th+'</div></div>'}if(e.summary)h+='<div class="f"><div class="fl">\u6458\u8981</div><div class="fv">'+esc(e.summary)+'</div></div>';h+='<div class="f"><div class="fl">\u5185\u5bb9</div><div class="fv">'+esc(e.content||'')+'</div></div>';if(e.source_url)h+='<div class="f"><div class="fl">\u6765\u6e90</div><div><a href="'+esc(e.source_url)+'" target="_blank" style="color:#60a5fa">'+esc(e.source_url)+'</a></div></div>';h+='<div class="f" style="margin-top:12px;color:#555;font-size:12px">'+esc(e.id)+' | '+esc((e.created_at||'').slice(0,10))+'</div>';mc.innerHTML=h;document.getElementById('md').classList.add('s')})}
function close(){document.getElementById('md').classList.remove('s')}
document.getElementById('list').onclick=function(ev){var el=ev.target.closest('.c');if(el&&el.dataset.id)d(el.dataset.id)};
document.getElementById('list').onclick=function(ev){var el=ev.target.closest('.c');if(el&&el.dataset.id)d(el.dataset.id)};
document.getElementById("list").onclick=function(ev){var el=ev.target.closest(".c");if(eld=document.getElementById('list');if(d)d.onclick=function(e){var p=e.target.closest('.c');if(p&&p.dataset.id)d(p.dataset.id)};
init();init();el.dataset.id)d(el.dataset.id)};init();
</script></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        params = {}
        if '?' in self.path:
            for p in self.path.split('?')[1].split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    params[k] = urllib.parse.unquote(v)
        try:
            if path == '/':
                self._serve_file('static/index.html')
            elif path == '/api/list':
                p = int(params.get('page', 1))
                l = int(params.get('limit', 99999))
                self._j(list_entries(limit=l, offset=(p-1)*l))
            elif path == '/api/search':
                self._j(search_entries_ranked(params.get('q', ''), limit=int(params.get('limit', 30))))
            elif path == '/api/get':
                self._j(get_entry(params.get('id', '')) or {"error":"not found"})
            elif path == '/api/types':
                self._j(get_all_types())
            elif path == '/api/stats':
                self._j(get_stats())
            elif path == '/api/typed':
                self._j(get_typed(params.get('subtype', ''), limit=int(params.get('limit', 99999))))
            else:
                self._j({"error":"not found"}, 404)
        except Exception as e:
            self._j({"error":str(e)}, 500)

    
    def _serve_file(self, path):
        fp = Path(__file__).parent / path
        if not fp.exists():
            self.send_response(404)
            self.end_headers()
            return
        ct = 'text/html; charset=utf-8'
        if path.endswith('.css'): ct = 'text/css; charset=utf-8'
        elif path.endswith('.js'): ct = 'application/javascript; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.end_headers()
        self.wfile.write(fp.read_bytes())
    def _j(self, d, c=200):
        self.send_response(c)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(d, ensure_ascii=False, indent=2).encode('utf-8'))

    def _r(self, h):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(h.encode('utf-8'))

    def log_message(self, f, *a):
        pass

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8888)
    a = p.parse_args()
    global PORT; PORT = a.port
    init_db()
    s = http.server.HTTPServer((HOST, PORT), Handler)
    print(f"MarkAI Web UI: http://{HOST}:{PORT}")
    try: s.serve_forever()
    except KeyboardInterrupt: s.server_close()

if __name__ == '__main__':
    main()
