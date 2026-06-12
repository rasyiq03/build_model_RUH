#!/usr/bin/env python3
# Inspect each man_made=bridge way: name, node count, closed?, PCA extent (m).
import os, sys, math, io, xml.etree.ElementTree as ET
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OSM=os.path.join(ROOT,"References","osm","jamarat.osm")
tree=ET.parse(OSM); root=tree.getroot()
nodes={n.get("id"):(float(n.get("lat")),float(n.get("lon"))) for n in root.findall("node")}
ways=[]
for w in root.findall("way"):
    nd=[c.get("ref") for c in w.findall("nd")]
    tags={t.get("k"):t.get("v") for t in w.findall("tag")}
    ways.append({"id":w.get("id"),"nodes":nd,"tags":tags})
bridges=[w for w in ways if w["tags"].get("man_made")=="bridge"]
allb=[nid for w in bridges for nid in w["nodes"] if nid in nodes]
lat0=np.mean([nodes[i][0] for i in allb]); lon0=np.mean([nodes[i][1] for i in allb])
mlat=110722.5; mlon=111412.84*math.cos(math.radians(lat0))
def proj(la,lo): return ((lo-lon0)*mlon,(la-lat0)*mlat)
def pca_extent(pts):
    p=pts-pts.mean(0); cov=np.cov(p.T); ev,evec=np.linalg.eigh(cov)
    proj_major=p@evec[:,1]; proj_minor=p@evec[:,0]
    return proj_major.max()-proj_major.min(), proj_minor.max()-proj_minor.min()
print(f"origin {lat0:.6f},{lon0:.6f}  bridge ways={len(bridges)}")
fig,ax=plt.subplots(figsize=(9,11))
cols=plt.cm.tab10.colors
for idx,w in enumerate(bridges):
    pts=np.array([proj(*nodes[i]) for i in w["nodes"] if i in nodes])
    closed = w["nodes"][0]==w["nodes"][-1]
    L,W=pca_extent(pts) if len(pts)>=3 else (0,0)
    nm=w["tags"].get("name") or w["tags"].get("name:en") or w["tags"].get("name:ar") or "-"
    h=w["tags"].get("height","-"); lay=w["tags"].get("layer","-")
    print(f"  way {w['id']:>12} nds={len(pts):>4} closed={str(closed):5} "
          f"L={L:7.1f} W={W:7.1f}  h={h:>3} layer={lay:>2} name='{nm}'")
    c=cols[idx%10]
    ax.plot(pts[:,0],pts[:,1],color=c,lw=1.6,label=f"{w['id']} {L:.0f}x{W:.0f} h{h}")
    ax.annotate(w['id'],pts.mean(0),color=c,fontsize=8)
ax.set_aspect("equal"); ax.legend(fontsize=7,loc="upper right")
ax.set_title("Jamarat OSM bridge polygons (local m, E=+X N=+Y)  (c) OSM")
ax.set_xlabel("East X (m)"); ax.set_ylabel("North Y (m)"); ax.grid(alpha=.3)
out=os.path.join(ROOT,"References","osm","osm_bridges_labeled.png")
fig.tight_layout(); fig.savefig(out,dpi=110); print("wrote",out)
