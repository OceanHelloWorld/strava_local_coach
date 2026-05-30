"""Localhost UI for strava-coach (stdlib http.server only — no web framework).

Run:  uv run --directory server ui.py   (or: python3 server/ui.py)
Open: http://localhost:8722

A "Sync from Strava" button pulls recent activities into the local store; the table
lets you sort/filter and click a row to load that activity's detail + streams on demand.
"""

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import store
import strava_client
import sync as sync_mod

PORT = 8722

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>strava-coach</title>
<style>
  body{font:14px/1.5 system-ui,sans-serif;margin:0;background:#fafafa;color:#222}
  header{background:#fc4c02;color:#fff;padding:14px 20px;display:flex;gap:12px;align-items:center}
  header h1{font-size:18px;margin:0;font-weight:600}
  button{font:inherit;border:0;border-radius:6px;padding:7px 12px;cursor:pointer;background:#fff;color:#fc4c02;font-weight:600}
  button.ghost{background:rgba(255,255,255,.18);color:#fff}
  main{padding:20px;max-width:1100px;margin:0 auto}
  input{font:inherit;padding:7px 10px;border:1px solid #ccc;border-radius:6px}
  table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}
  th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #eee;white-space:nowrap}
  th{background:#f3f3f3;cursor:pointer;user-select:none}
  tr:hover td{background:#fff6f2}
  td.num{text-align:right;font-variant-numeric:tabular-nums}
  #status{margin-left:auto;font-size:13px;opacity:.9}
  #detail{margin-top:18px;background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08);display:none}
  pre{white-space:pre-wrap;word-break:break-word;font-size:12px;max-height:320px;overflow:auto;background:#f7f7f7;padding:10px;border-radius:6px}
</style></head>
<body>
<header>
  <h1>strava-coach</h1>
  <button onclick="sync(false)">Sync new</button>
  <button class="ghost" onclick="sync(true)">Full backfill</button>
  <span id="status"></span>
</header>
<main>
  <p><input id="filter" placeholder="Filter by name or sport…" oninput="render()" style="width:280px"></p>
  <table id="tbl"><thead><tr>
    <th onclick="sortBy('start_date_local')">Date</th>
    <th onclick="sortBy('name')">Name</th>
    <th onclick="sortBy('sport_type')">Sport</th>
    <th onclick="sortBy('distance')">Dist (km)</th>
    <th onclick="sortBy('moving_time')">Pace</th>
    <th onclick="sortBy('average_heartrate')">Avg HR</th>
  </tr></thead><tbody></tbody></table>
  <div id="detail"></div>
</main>
<script>
let acts=[], sortKey='start_date_local', sortDir=-1;
const km=m=>m?(m/1000).toFixed(2):'';
const pace=a=>{if(!a.distance||!a.moving_time)return '';const s=a.moving_time/(a.distance/1000);return Math.floor(s/60)+':'+String(Math.round(s%60)).padStart(2,'0');};
function status(t){document.getElementById('status').textContent=t;}
async function load(){acts=await (await fetch('/api/activities')).json();status(acts.length+' activities stored');render();}
async function sync(full){status('Syncing…');try{const r=await (await fetch('/api/sync',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({full})})).json();if(r.error){status('Error: '+r.error);return;}status('Synced '+r.synced+' new ('+r.count+' total)');load();}catch(e){status('Error: '+e);}}
function sortBy(k){sortDir=sortKey===k?-sortDir:1;sortKey=k;render();}
function render(){
  const f=document.getElementById('filter').value.toLowerCase();
  let rows=acts.filter(a=>!f||((a.name||'')+' '+(a.sport_type||'')).toLowerCase().includes(f));
  rows.sort((a,b)=>{const x=a[sortKey],y=b[sortKey];return (x>y?1:x<y?-1:0)*sortDir;});
  document.querySelector('#tbl tbody').innerHTML=rows.map(a=>`<tr onclick="detail(${a.id})">
    <td>${(a.start_date_local||'').slice(0,10)}</td><td>${a.name||''}</td><td>${a.sport_type||a.type||''}</td>
    <td class="num">${km(a.distance)}</td><td class="num">${pace(a)}</td><td class="num">${a.average_heartrate||''}</td></tr>`).join('');
}
async function detail(id){
  const d=document.getElementById('detail');d.style.display='block';d.innerHTML='Loading activity '+id+'…';
  try{const r=await (await fetch('/api/activity?id='+id)).json();
    if(r.error){d.innerHTML='Error: '+r.error;return;}
    const det=r.detail||{};
    d.innerHTML='<h3>'+(det.name||id)+'</h3><pre>'+JSON.stringify(det,null,2)+'</pre>'+
      '<h4>Streams</h4><pre>'+JSON.stringify(Object.keys(r.streams||{}),null,2)+'</pre>';
  }catch(e){d.innerHTML='Error: '+e;}
}
load();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif parsed.path == "/api/activities":
            self._send(200, json.dumps(store.load_activities()))
        elif parsed.path == "/api/activity":
            qs = urllib.parse.parse_qs(parsed.query)
            aid = (qs.get("id") or [""])[0]
            try:
                detail, _ = strava_client.api_get(f"/activities/{aid}")
                streams, _ = strava_client.api_get(
                    f"/activities/{aid}/streams",
                    {"keys": "heartrate,velocity_smooth,altitude,watts", "key_by_type": "true"},
                )
                self._send(200, json.dumps({"detail": detail, "streams": streams}))
            except strava_client.StravaError as e:
                self._send(502, json.dumps({"error": str(e)}))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/sync":
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            full = False
            if raw:
                try:
                    full = bool(json.loads(raw).get("full"))
                except (json.JSONDecodeError, AttributeError):
                    pass
            try:
                n = sync_mod.sync_activities(full=full)
                self._send(200, json.dumps({"synced": n, "count": len(store.load_activities())}))
            except strava_client.StravaError as e:
                self._send(502, json.dumps({"error": str(e)}))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def log_message(self, *args):  # quiet
        pass


def main():
    print(f"strava-coach UI running at http://localhost:{PORT}  (Ctrl-C to stop)")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
