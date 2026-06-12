#!/usr/bin/env python3
# =============================================================================
# PHASE R — fit a clean parametric TRACE to the real OSM footprint, then
# overlay proposed layout vs OSM and measure deviation (verification gate, XY).
# Long axis aligned to +Y using the main through-deck way 431634032 (978x88).
# Outputs proposed TRACE dict (JSON) + References/osm/proposed_overlay.png.
# (c) OpenStreetMap contributors (ODbL).
# =============================================================================
import os, sys, math, io, json, xml.etree.ElementTree as ET
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
def proj(la,lo): return np.array([(lo-lon0)*mlon,(la-lat0)*mlat])
def way_xy(wid):
    w=next(x for x in ways if x["id"]==wid)
    return np.array([proj(*nodes[i]) for i in w["nodes"] if i in nodes])

# --- alignment: rotate so main deck (431634032) long axis -> +Y ---
main=way_xy("431634032"); mc=main.mean(0); mp=main-mc
ev,evec=np.linalg.eigh(np.cov(mp.T)); major=evec[:,1]
ang=math.atan2(major[1],major[0]); rot=math.pi/2-ang
c,s=math.cos(rot),math.sin(rot); R=np.array([[c,-s],[s,c]])
# common center = centroid of core deck 440922995
core=way_xy("440922995"); center=core.mean(0)
def L(xy): return ((xy-center)@R.T)
def Lw(wid): return L(way_xy(wid))

# --- OUTLINE_OUTER = real OSM deck envelope (convex hull of core decks) ---
# Core deck ways (exclude thin ramp fingers 755/758/759); these ARE the footprint.
CORE_WAYS=["440922995","431617751"]   # named bridge core + wide deck loop = iconic oval
def convex_hull(P):
    P=P[np.lexsort((P[:,1],P[:,0]))]
    def half(pts):
        h=[]
        for p in pts:
            while len(h)>=2 and np.cross(h[-1]-h[-2],p-h[-2])<=0: h.pop()
            h.append(p)
        return h
    lo=half(P); up=half(P[::-1])
    return np.array(lo[:-1]+up[:-1])
def resample(ring,n=96):
    ring=np.vstack([ring,ring[:1]])
    seg=np.hypot(np.diff(ring[:,0]),np.diff(ring[:,1])); cum=np.concatenate([[0],np.cumsum(seg)])
    s=np.linspace(0,cum[-1],n,endpoint=False)
    return np.column_stack([np.interp(s,cum,ring[:,0]),np.interp(s,cum,ring[:,1])])

corepts=np.vstack([Lw(w) for w in CORE_WAYS])
OUTER=resample(convex_hull(corepts),96)                 # <- traced from OSM

def stadium(a, b, n=96, cx=0.0, cy=0.0):
    t=np.linspace(0,2*math.pi,n,endpoint=False)
    return np.column_stack([cx+b*np.cos(t), cy+a*np.sin(t)])
# VOID + jamarah + ramps are reference-derived (OSM has no hole over the spine).
VOID =stadium(a=215, b=32, n=96)
# 3 jamarah on spine centerline X=0; real spacing Ula-Wusta~135, Wusta-Aqabah~247 m
JAM={"ULA":(0.0,-191.0),"WUSTA":(0.0,-56.0),"AQABAH":(0.0,192.0)}
RAMP_N=(0.0, 470.0); RAMP_S=(0.0,-470.0)

# --- deviation: OUTER (=hull) vs the OSM core deck points it was built from ---
def min_dist(P,ring):
    return np.array([np.min(np.hypot((ring-p)[:,0],(ring-p)[:,1])) for p in P])
# how far do the real OSM core-deck vertices sit OUTSIDE our outline? (gate metric)
dev=min_dist(corepts, OUTER)
print(f"[FIT] OUTER=OSM hull. core-deck vertex vs outline: "
      f"max={dev.max():.1f} m mean={dev.mean():.1f} m (0=on outline)")
print(f"[FIT] OUTER extent Y={np.ptp(OUTER[:,1]):.0f} X={np.ptp(OUTER[:,0]):.0f} | "
      f"core decks Y={np.ptp(corepts[:,1]):.0f} X={np.ptp(corepts[:,0]):.0f}")

trace={"OUTLINE_OUTER":OUTER.round(2).tolist(),
       "OUTLINE_VOID":VOID.round(2).tolist(),
       "PILLARS":{k:{"pos":[round(x,1),round(y,1)],"length":26.0,"thick":4.0,
                     "angle_deg":90.0} for k,(x,y) in JAM.items()},
       "RAMP_N":list(RAMP_N),"RAMP_S":list(RAMP_S),
       "VERIFY_MAX_DEVIATION_M":round(float(dev.max()),2)}
with open(os.path.join(ROOT,"References","osm","proposed_trace.json"),"w") as f:
    json.dump(trace,f,indent=1)

# --- overlay plot ---
fig,ax=plt.subplots(figsize=(8,11))
cols=plt.cm.tab10.colors
for i,w in enumerate(bridges):
    xy=Lw(w["id"]); ax.plot(xy[:,0],xy[:,1],color="0.6",lw=1.0,zorder=1)
ax.plot(*np.vstack([OUTER,OUTER[:1]]).T,'C3-',lw=2,label="proposed OUTER",zorder=4)
ax.plot(*np.vstack([VOID,VOID[:1]]).T,'C0-',lw=2,label="proposed VOID",zorder=4)
for k,(x,y) in JAM.items():
    ax.scatter(x,y,c='C2',s=90,zorder=5); ax.annotate(k,(x,y),fontsize=9)
for nm,(x,y) in (("RAMP_N",RAMP_N),("RAMP_S",RAMP_S)):
    ax.scatter(x,y,c='C1',marker='^',s=90,zorder=5); ax.annotate(nm,(x,y))
ax.set_aspect("equal"); ax.legend(fontsize=8,loc="upper right")
ax.set_title(f"Proposed TRACE vs OSM (grey)  max dev={dev.max():.0f} m  (c) OSM")
ax.set_xlabel("X width (m)"); ax.set_ylabel("Y length (m)"); ax.grid(alpha=.3)
out=os.path.join(ROOT,"References","osm","proposed_overlay.png")
fig.tight_layout(); fig.savefig(out,dpi=110); print("wrote",out)
