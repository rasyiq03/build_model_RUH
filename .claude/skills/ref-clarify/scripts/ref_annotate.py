#!/usr/bin/env python3
"""
ref_annotate.py — human-in-the-loop reference clarifier for RUH / Claude Code.

Claude Code runs this when a reference image is ambiguous, or two references
conflict, instead of guessing. It opens the image in the user's browser. The
user can:
  - drop numbered pins, each with a typed comment ("1 = the green Mas'a zone"),
  - draw boxes, arrows, and freehand marks,
  - ZOOM/PAN the annotation canvas (so small features are easy to mark),
  - open extra REFERENCE images large in a zoom/pan lightbox (see --ref),
  - write an overall answer, and/or upload clearer files as the answer.

On "Save & Finish" it writes, into <out-dir> (default: <image_dir>/_clarify):
  <stem>__annotated.png   full-resolution image + the user's annotations
  <stem>__notes.json      structured pins / shapes / answer / metadata
and prints those two paths to stdout so Claude Code can read them back
(it can SEE the annotated PNG and parse the JSON).

Pure Python standard library — NO pip install, works anywhere Python 3 + a
browser exist. Cross-platform (Windows / macOS / Linux desktop).

Usage:
  python ref_annotate.py path/to/primary.png \
      --question "Drop a pin on each tower (A/B/C)." \
      --ref path/to/real_photo.jpg --ref path/to/rough_trace.png

Flags:
  --question TEXT   the specific thing Claude needs clarified (shown to the user)
  --ref PATH        extra reference image shown in a zoomable gallery (repeatable).
                    Annotation still happens ONLY on the primary image.
  --out-dir  DIR    where to write outputs (default: <image_dir>/_clarify)
  --port     N      fixed port (default: auto-pick a free port)
  --no-browser      don't auto-open a browser (used for automated testing)
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Make stdout/stderr robust to non-ASCII (questions/paths) on Windows consoles (cp1252).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PAGE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>ref-clarify · __STEM__</title>
<style>
  :root { color-scheme: light dark; }
  body { margin:0; font:14px/1.45 system-ui, sans-serif; display:flex; height:100vh; }
  #left { flex:1; min-width:0; display:flex; flex-direction:column; background:#1e1e1e; }
  #bar { padding:8px 12px; background:#111; color:#eee; display:flex; gap:8px;
         align-items:center; flex-wrap:wrap; }
  #bar button { background:#333; color:#eee; border:1px solid #555; border-radius:6px;
                padding:6px 10px; cursor:pointer; }
  #bar button.active { background:#3b82f6; border-color:#3b82f6; }
  #stage { flex:1; overflow:auto; display:flex; align-items:flex-start;
           justify-content:center; padding:12px; }
  canvas { background:#000; box-shadow:0 0 0 1px #444; cursor:crosshair; }
  #side { width:340px; box-sizing:border-box; padding:14px; overflow:auto;
          background:#fafafa; color:#111; border-left:1px solid #ddd; }
  @media (prefers-color-scheme: dark){ #side{background:#222;color:#eee;border-color:#444} }
  #q { font-weight:600; margin:0 0 10px; }
  textarea { width:100%; box-sizing:border-box; min-height:90px; padding:8px;
             border-radius:6px; border:1px solid #bbb; font:inherit; }
  .pin-row { display:flex; gap:6px; align-items:flex-start; margin:6px 0; }
  .pin-row .n { flex:0 0 24px; height:24px; border-radius:50%; background:#ef4444;
                color:#fff; display:flex; align-items:center; justify-content:center;
                font-weight:700; font-size:12px; }
  .pin-row input { flex:1; padding:5px; border-radius:5px; border:1px solid #bbb; font:inherit; }
  #refs { display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 4px; }
  #refs figure { margin:0; width:96px; cursor:zoom-in; }
  #refs img { width:96px; height:72px; object-fit:cover; border-radius:5px; border:1px solid #999; display:block; }
  #refs figcaption { font-size:10px; color:#888; text-align:center; word-break:break-all; }
  #save { width:100%; margin-top:12px; padding:11px; font-size:15px; font-weight:600;
          background:#16a34a; color:#fff; border:none; border-radius:8px; cursor:pointer; }
  #cancel { width:100%; margin-top:8px; padding:9px; font-size:13px;
            background:#6b7280; color:#fff; border:none; border-radius:8px; cursor:pointer; }
  #status { margin-top:10px; font-size:13px; color:#666; }
  small { color:#888; }
  /* lightbox */
  #lb { display:none; position:fixed; inset:0; background:rgba(0,0,0,.93); z-index:50;
        flex-direction:column; }
  #lbbar { padding:8px 12px; color:#eee; display:flex; gap:10px; align-items:center; background:#000; }
  #lbbar button { background:#333; color:#eee; border:1px solid #555; border-radius:6px; padding:6px 12px; cursor:pointer; }
  #lbwrap { flex:1; overflow:hidden; position:relative; }
  #lbimg { position:absolute; top:0; left:0; transform-origin:0 0; cursor:grab; user-select:none; }
</style></head>
<body>
  <div id="left">
    <div id="bar">
      <button id="t-pin"  class="active" data-tool="pin">📍 Pin</button>
      <button id="t-box"  data-tool="box">▭ Box</button>
      <button id="t-arr"  data-tool="arrow">↗ Arrow</button>
      <button id="t-pen"  data-tool="pen">✎ Pen</button>
      <button id="t-ell"  data-tool="ellipse">⬭ Circle</button>
      <button id="t-line" data-tool="line">／ Line</button>
      <button id="t-text" data-tool="text">T Text</button>
      <span style="width:1px;height:22px;background:#555"></span>
      <input type="color" id="color" value="#ef4444" title="color">
      <label style="color:#aaa">width <input type="range" id="width" min="1" max="12" value="4"></label>
      <span style="width:1px;height:22px;background:#555"></span>
      <button id="zoomout" title="zoom out">－</button>
      <span id="zlabel" style="color:#aaa;min-width:42px;text-align:center">100%</span>
      <button id="zoomin" title="zoom in">＋</button>
      <button id="zfit" title="fit width">Fit</button>
      <span style="width:1px;height:22px;background:#555"></span>
      <button id="undo">↶ Undo</button>
      <button id="clear">🗑 Clear</button>
    </div>
    <div id="stage"><canvas id="c"></canvas></div>
  </div>
  <div id="side">
    <p id="q">__QUESTION__</p>
    <small>Pick a tool, mark the image. Use ＋／－／Fit (or Ctrl+wheel on the image) to zoom in for precise pins.</small>
    <div id="refsection" style="display:none">
      <p style="margin:14px 0 4px;font-weight:600">Reference images (click to enlarge)</p>
      <div id="refs"></div>
    </div>
    <div id="pins"></div>
    <p style="margin:14px 0 4px;font-weight:600">Overall answer / comment</p>
    <textarea id="answer" placeholder="Explain what Claude got confused about..."></textarea>
    <p style="margin:12px 0 4px;font-weight:600">Add reference file(s) as answer (optional)</p>
    <small>Upload a clearer photo, floor plan, etc. — it becomes part of your answer.</small>
    <input type="file" id="uploads" multiple accept="image/*" style="display:block;margin-top:6px">
    <div id="uplist" style="margin-top:6px"></div>
    <button id="save">Save &amp; Finish</button>
    <button id="cancel">Nothing to add — Cancel</button>
    <div id="status"></div>
  </div>

  <div id="lb">
    <div id="lbbar">
      <b id="lbname" style="flex:1"></b>
      <button id="lbout">－</button><span id="lbz" style="min-width:48px;text-align:center">100%</span><button id="lbin">＋</button>
      <button id="lbfit">Fit</button>
      <button id="lbclose">✕ Close</button>
    </div>
    <div id="lbwrap"><img id="lbimg" draggable="false"></div>
  </div>

<script>
const IMG = "__IMAGE_URI__";
const REFS = __REFS_JSON__;   // [{name, uri}, ...]
const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
const img = new Image();
let tool='pin', color='#ef4444', width=4, zoom=1;
let shapes=[], pins=[], drawing=null, uploads=[];

img.onload = () => { canvas.width=img.naturalWidth; canvas.height=img.naturalHeight; fitWidth(); redraw(); };
img.src = IMG;

// ---- main-canvas zoom (CSS width scaling; keeps pt() mapping correct) -------
function applyZoom(){ canvas.style.width=(img.naturalWidth*zoom)+'px';
  canvas.style.height=(img.naturalHeight*zoom)+'px';
  document.getElementById('zlabel').textContent=Math.round(zoom*100)+'%'; }
function fitWidth(){ const stage=document.getElementById('stage');
  zoom = Math.min(1, (stage.clientWidth-28)/img.naturalWidth) || 1; applyZoom(); }
document.getElementById('zoomin').onclick =()=>{ zoom=Math.min(8, zoom*1.25); applyZoom(); };
document.getElementById('zoomout').onclick=()=>{ zoom=Math.max(0.1, zoom/1.25); applyZoom(); };
document.getElementById('zfit').onclick   =()=> fitWidth();
document.getElementById('stage').addEventListener('wheel', e=>{
  if(!e.ctrlKey) return; e.preventDefault();
  zoom = e.deltaY<0 ? Math.min(8, zoom*1.1) : Math.max(0.1, zoom/1.1); applyZoom();
}, {passive:false});

document.querySelectorAll('#bar [data-tool]').forEach(b=>{
  b.onclick=()=>{ tool=b.dataset.tool;
    document.querySelectorAll('#bar [data-tool]').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); };
});
document.getElementById('color').oninput = e => color = e.target.value;
document.getElementById('width').oninput = e => width = +e.target.value;
document.getElementById('undo').onclick = () => {
  if (shapes.length || pins.length) {
    if (pins.length && (!shapes.length || pins[pins.length-1].seq > shapes[shapes.length-1].seq)) pins.pop();
    else shapes.pop();
    renderPins(); redraw();
  }
};
document.getElementById('clear').onclick = () => { shapes=[]; pins=[]; renderPins(); redraw(); };

// ---- reference gallery + lightbox -----------------------------------------
(function(){ if(!REFS.length) return;
  document.getElementById('refsection').style.display='block';
  const box=document.getElementById('refs');
  REFS.forEach(r=>{ const fig=document.createElement('figure');
    const im=document.createElement('img'); im.src=r.uri; im.alt=r.name;
    const cap=document.createElement('figcaption'); cap.textContent=r.name;
    fig.appendChild(im); fig.appendChild(cap); fig.onclick=()=>openLB(r); box.appendChild(fig); });
})();
const lb=document.getElementById('lb'), lbimg=document.getElementById('lbimg');
let lbScale=1, lbX=0, lbY=0, lbDrag=null;
function lbUpdate(){ lbimg.style.transform=`translate(${lbX}px,${lbY}px) scale(${lbScale})`;
  document.getElementById('lbz').textContent=Math.round(lbScale*100)+'%'; }
function lbFit(){ const w=document.getElementById('lbwrap');
  lbScale=Math.min(w.clientWidth/lbimg.naturalWidth, w.clientHeight/lbimg.naturalHeight)||1;
  lbX=(w.clientWidth-lbimg.naturalWidth*lbScale)/2; lbY=(w.clientHeight-lbimg.naturalHeight*lbScale)/2; lbUpdate(); }
function openLB(r){ document.getElementById('lbname').textContent=r.name; lb.style.display='flex';
  lbimg.onload=lbFit; lbimg.src=r.uri; if(lbimg.complete) lbFit(); }
document.getElementById('lbclose').onclick=()=>{ lb.style.display='none'; };
document.getElementById('lbin').onclick =()=>{ lbScale*=1.25; lbUpdate(); };
document.getElementById('lbout').onclick=()=>{ lbScale/=1.25; lbUpdate(); };
document.getElementById('lbfit').onclick=lbFit;
document.getElementById('lbwrap').addEventListener('wheel',e=>{ e.preventDefault();
  const f=e.deltaY<0?1.1:1/1.1; lbScale*=f; lbUpdate(); },{passive:false});
lbimg.addEventListener('mousedown',e=>{ lbDrag={x:e.clientX-lbX,y:e.clientY-lbY}; lbimg.style.cursor='grabbing'; });
window.addEventListener('mousemove',e=>{ if(lbDrag){ lbX=e.clientX-lbDrag.x; lbY=e.clientY-lbDrag.y; lbUpdate(); }});
window.addEventListener('mouseup',()=>{ lbDrag=null; lbimg.style.cursor='grab'; });
window.addEventListener('keydown',e=>{ if(e.key==='Escape') lb.style.display='none'; });

document.getElementById('uploads').addEventListener('change', e=>{
  uploads=[]; const list=document.getElementById('uplist'); list.innerHTML='';
  [...e.target.files].forEach(f=>{
    const r=new FileReader();
    r.onload=()=>{ uploads.push({name:f.name, type:f.type, data:r.result});
      const d=document.createElement('div'); d.textContent='📎 '+f.name; list.appendChild(d); };
    r.readAsDataURL(f);
  });
});

let seq=0;
function pt(e){ const r=canvas.getBoundingClientRect();
  return { x:(e.clientX-r.left)*(canvas.width/r.width),
           y:(e.clientY-r.top)*(canvas.height/r.height) }; }

canvas.addEventListener('mousedown', e=>{
  const p=pt(e);
  if (tool==='pin'){ pins.push({n:pins.length+1, x:p.x, y:p.y, comment:'', color, seq:seq++}); renderPins(); redraw(); return; }
  if (tool==='text'){ const t=prompt('Label text:'); if(t){ shapes.push({type:'text', color, width, seq:seq++, x0:p.x, y0:p.y, text:t}); redraw(); } return; }
  drawing={ type:tool, color, width, seq:seq++, x0:p.x, y0:p.y, x1:p.x, y1:p.y, points:[[p.x,p.y]] };
});
canvas.addEventListener('mousemove', e=>{
  if(!drawing) return; const p=pt(e);
  drawing.x1=p.x; drawing.y1=p.y; if(drawing.type==='pen') drawing.points.push([p.x,p.y]);
  redraw(); drawShape(drawing);
});
window.addEventListener('mouseup', ()=>{ if(drawing){ shapes.push(drawing); drawing=null; redraw(); }});

function drawShape(s){
  ctx.strokeStyle=s.color; ctx.fillStyle=s.color; ctx.lineWidth=s.width; ctx.lineJoin='round'; ctx.lineCap='round';
  if(s.type==='box'){ ctx.strokeRect(s.x0,s.y0,s.x1-s.x0,s.y1-s.y0); }
  else if(s.type==='ellipse'){ ctx.beginPath();
    ctx.ellipse((s.x0+s.x1)/2,(s.y0+s.y1)/2,Math.abs(s.x1-s.x0)/2,Math.abs(s.y1-s.y0)/2,0,0,7); ctx.stroke(); }
  else if(s.type==='line'){ ctx.beginPath(); ctx.moveTo(s.x0,s.y0); ctx.lineTo(s.x1,s.y1); ctx.stroke(); }
  else if(s.type==='text'){ const fs=Math.max(16, canvas.width*0.016);
    ctx.font='bold '+fs+'px system-ui'; ctx.textAlign='left'; ctx.textBaseline='top';
    ctx.lineWidth=Math.max(3,fs*0.18); ctx.strokeStyle='#000'; ctx.strokeText(s.text||'', s.x0, s.y0);
    ctx.fillStyle=s.color; ctx.fillText(s.text||'', s.x0, s.y0); }
  else if(s.type==='arrow'){ const a=Math.atan2(s.y1-s.y0,s.x1-s.x0), h=14+s.width*2;
    ctx.beginPath(); ctx.moveTo(s.x0,s.y0); ctx.lineTo(s.x1,s.y1); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(s.x1,s.y1);
    ctx.lineTo(s.x1-h*Math.cos(a-0.4), s.y1-h*Math.sin(a-0.4));
    ctx.lineTo(s.x1-h*Math.cos(a+0.4), s.y1-h*Math.sin(a+0.4)); ctx.closePath(); ctx.fill(); }
  else if(s.type==='pen'){ ctx.beginPath(); s.points.forEach((q,i)=> i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1])); ctx.stroke(); }
}
function drawPin(p){ const r=Math.max(11, canvas.width*0.011);
  ctx.beginPath(); ctx.arc(p.x,p.y,r,0,7); ctx.fillStyle=p.color||'#ef4444'; ctx.fill();
  ctx.lineWidth=2; ctx.strokeStyle='#fff'; ctx.stroke();
  ctx.fillStyle='#fff'; ctx.font='bold '+Math.round(r*1.2)+'px system-ui'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(p.n, p.x, p.y); }
function redraw(){ ctx.clearRect(0,0,canvas.width,canvas.height); if(img.complete) ctx.drawImage(img,0,0);
  shapes.forEach(drawShape); pins.forEach(drawPin); }

function renderPins(){ const box=document.getElementById('pins'); box.innerHTML='';
  pins.forEach((p,i)=>{ const row=document.createElement('div'); row.className='pin-row';
    row.innerHTML='<div class="n" style="background:'+(p.color||'#ef4444')+'">'+p.n+'</div>';
    const inp=document.createElement('input'); inp.placeholder='what is #'+p.n+'?'; inp.value=p.comment;
    inp.oninput=e=>{ pins[i].comment=e.target.value; }; row.appendChild(inp); box.appendChild(row); });
}

document.getElementById('save').onclick = async () => {
  const status=document.getElementById('status'); status.textContent='Saving...';
  const payload = { answer: document.getElementById('answer').value,
    pins: pins.map(p=>({n:p.n,x:Math.round(p.x),y:Math.round(p.y),comment:p.comment})),
    shapes: shapes.map(s=> s.type==='pen'
        ? {type:'pen', color:s.color, points:s.points.map(q=>[Math.round(q[0]),Math.round(q[1])])}
        : s.type==='text'
        ? {type:'text', color:s.color, x0:Math.round(s.x0), y0:Math.round(s.y0), text:s.text}
        : {type:s.type, color:s.color, x0:Math.round(s.x0),y0:Math.round(s.y0),x1:Math.round(s.x1),y1:Math.round(s.y1)}),
    image_size:[canvas.width,canvas.height],
    uploads: uploads.map(u=>({name:u.name, type:u.type, data:u.data})),
    png: canvas.toDataURL('image/png') };
  try {
    const r = await fetch('/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    if(r.ok){ status.innerHTML='<b style="color:#16a34a">Saved ✓ You can close this tab.</b>'; }
    else { status.textContent='Save failed ('+r.status+').'; }
  } catch(err){ status.textContent='Save error: '+err; }
};
document.getElementById('cancel').onclick = async () => {
  const status=document.getElementById('status');
  try { await fetch('/cancel', {method:'POST'});
    status.innerHTML='<b>Closed without changes. You can close this tab.</b>'; }
  catch(err){ status.textContent='Cancel error: '+err; }
};
</script>
</body></html>"""


def build_page(image_uri, question, stem, refs):
    q = (question or "Mark anything that's unclear and add a comment.").replace("&", "&amp;").replace("<", "&lt;")
    return (PAGE.replace("__IMAGE_URI__", image_uri)
                .replace("__REFS_JSON__", json.dumps(refs))
                .replace("__QUESTION__", q)
                .replace("__STEM__", stem))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # keep stdout clean for Claude Code
        pass

    def do_GET(self):
        if self.path != "/":
            self.send_error(404); return
        body = self.server.page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        srv = self.server
        if self.path == "/cancel":
            srv.result = {"cancelled": True}
            reply = json.dumps({"ok": True, "cancelled": True}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(reply)))
            self.end_headers()
            self.wfile.write(reply)
            srv.done.set()
            return
        if self.path != "/save":
            self.send_error(404); return
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n).decode("utf-8"))

        srv = self.server
        os.makedirs(srv.out_dir, exist_ok=True)
        png_path = os.path.join(srv.out_dir, srv.stem + "__annotated.png")
        json_path = os.path.join(srv.out_dir, srv.stem + "__notes.json")

        b64 = data["png"].split(",", 1)[1]
        with open(png_path, "wb") as f:
            f.write(base64.b64decode(b64))

        # write any uploaded reference files the user added as their answer
        uploaded_paths = []
        for u in data.get("uploads", []):
            blob = u.get("data", "")
            raw = blob.split(",", 1)[1] if "," in blob else blob
            safe = os.path.basename(u.get("name", "upload")).replace("\\", "_").replace("/", "_")
            safe = safe or "upload.bin"
            up_path = os.path.join(srv.out_dir, "uploaded_" + safe)
            with open(up_path, "wb") as f:
                f.write(base64.b64decode(raw))
            uploaded_paths.append(os.path.abspath(up_path))

        notes = {
            "source_image": os.path.abspath(srv.image_path),
            "question": srv.question,
            "answer": data.get("answer", ""),
            "pins": data.get("pins", []),
            "shapes": data.get("shapes", []),
            "reference_images": srv.ref_paths,
            "uploaded_references": uploaded_paths,
            "image_size": data.get("image_size"),
            "annotated_image": os.path.abspath(png_path),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)

        srv.result = {"annotated_image": os.path.abspath(png_path),
                      "notes_json": os.path.abspath(json_path),
                      "uploaded_references": uploaded_paths}
        reply = json.dumps({"ok": True, **srv.result}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)
        srv.done.set()


def _data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def main():
    ap = argparse.ArgumentParser(description="Open a reference image for the user to annotate.")
    ap.add_argument("image")
    ap.add_argument("--question", default="")
    ap.add_argument("--ref", action="append", default=[],
                    help="extra reference image shown in a zoomable gallery (repeatable)")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.image):
        print(f"[ref-clarify] ERROR: image not found: {args.image}", file=sys.stderr)
        sys.exit(2)

    stem = os.path.splitext(os.path.basename(args.image))[0]
    out_dir = args.out_dir or os.path.join(os.path.dirname(os.path.abspath(args.image)), "_clarify")
    image_uri = _data_uri(args.image)

    refs, ref_paths = [], []
    for rp in args.ref:
        if os.path.isfile(rp):
            refs.append({"name": os.path.basename(rp), "uri": _data_uri(rp)})
            ref_paths.append(os.path.abspath(rp))
        else:
            print(f"[ref-clarify] WARN: --ref not found, skipping: {rp}", file=sys.stderr)

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    httpd.page = build_page(image_uri, args.question, stem, refs)
    httpd.image_path = args.image
    httpd.question = args.question
    httpd.out_dir = out_dir
    httpd.stem = stem
    httpd.ref_paths = ref_paths
    httpd.result = None
    httpd.done = threading.Event()

    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    print(f"[ref-clarify] image   : {args.image}")
    if args.question:
        print(f"[ref-clarify] question: {args.question}")
    for rp in ref_paths:
        print(f"[ref-clarify] reference: {rp}")
    print(f"[ref-clarify] WAITING for the user to annotate at: {url}")
    print(f"[ref-clarify] (the user marks the image, then clicks 'Save & Finish')")
    sys.stdout.flush()

    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.done.wait()
    except KeyboardInterrupt:
        print("[ref-clarify] cancelled by user", file=sys.stderr)
        httpd.shutdown(); sys.exit(130)

    httpd.shutdown()
    r = httpd.result or {}
    if r.get("cancelled"):
        print("[ref-clarify] CANCELLED — user added nothing (no files written).")
        return
    print("[ref-clarify] SAVED")
    print(f"[ref-clarify] annotated_image: {r.get('annotated_image','')}")
    print(f"[ref-clarify] notes_json: {r.get('notes_json','')}")
    for up in r.get("uploaded_references", []):
        print(f"[ref-clarify] uploaded_reference: {up}")


if __name__ == "__main__":
    main()
