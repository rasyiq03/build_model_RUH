#!/usr/bin/env python3
# PLAN ONLY (no build): mark candidate FLYOVER road segments + LIFT cylinders +
# HELIPAD, for the user to confirm/correct. Flyover = consistent-width roads, not
# the wide silhouette blobs. Non-marked silhouette = noise -> will be ignored.
import os, sys, io, math
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import trace_data as T

sil = np.array(T.SIL_OUTER)
cy_l = np.array(T.SIL_HOLES[0]); cy_r = np.array(T.SIL_HOLES[1])
oc = {k: np.array(v) for k, v in T.OCULUS.items()}
BODY = T.BODY_HALF_Y

# ---- approved 5-floor spine corridor (green) ----
def x_crossings(poly, y):
    xs = []; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
    return sorted(xs)
ys = np.linspace(-BODY, BODY, 220)
le = []; re = []
for y in ys:
    lc = x_crossings(cy_l, y); rc = x_crossings(cy_r, y); sc = x_crossings(sil, y)
    lb = max(lc) if lc else -32.0; rb = min(rc) if rc else 64.0
    if sc:
        lb = max(lb, min(sc)); rb = min(rb, max(sc))
    if rb - lb < 8:
        m = (lb + rb) / 2; lb, rb = m - 4, m + 4
    le.append((lb, y)); re.append((rb, y))
SPINE = np.array(le + re[::-1])

# ---- proposed LIFT cylinders (clean set, per 080628 + perspective07) ----
# clustered at both ends + flanking the spine ("sampai bagian jamarat").
lifts = [
    (-70, 270), (70, 270), (-140, 240), (140, 240),     # N-end cluster
    (-70, -270), (70, -270), (-140, -240), (140, -240), # S-end cluster
    (95, 95), (-90, 95), (95, -115), (-90, -115),       # flanking the spine (mid)
]
helipad = (95, 60)   # cylinder + round disc, beside the spine (perspective07)
print(f"[MARK] proposed lifts={len(lifts)}  helipad@{helipad}")

# ---- candidate flyover road ZONES (consistent-width centerlines) ----
# derived from ref 080628: upper-loop arc, lower road, N-fan, S-fan.
def arc(cx, cy, rx, ry, a0, a1, n=40):
    t = np.linspace(math.radians(a0), math.radians(a1), n)
    return np.column_stack([cx + rx*np.cos(t), cy + ry*np.sin(t)])
ROADS = {
    "1:UPPER-LOOP (E side arc)": arc(-10, 0, 250, 300, -70, 70),
    "2:LOWER-LOOP (W side arc)": arc(-10, 0, 250, 300, 110, 250),
    "3:N-FAN (top ramps)": None,
    "4:S-FAN (bottom ramps)": None,
}
def fan(y0, ysign, n=4, spread=80, L=190):
    segs = []
    for i in range(n):
        a = math.radians(-spread/2 + spread*i/(n-1))
        dx, dy = math.sin(a), math.cos(a)*ysign
        segs.append(np.array([[0, y0], [dx*L, y0 + dy*L]]))
    return segs

# ---- plot ----
fig, ax = plt.subplots(figsize=(11, 13))
ax.fill(sil[:, 0], sil[:, 1], color="0.85", alpha=0.5, zorder=0)   # silhouette (noise/base)
ax.fill(cy_l[:, 0], cy_l[:, 1], color="white", zorder=1)
ax.fill(cy_r[:, 0], cy_r[:, 1], color="white", zorder=1)
ax.fill(SPINE[:, 0], SPINE[:, 1], color="#5cb85c", alpha=0.9, zorder=2, label="5-FLOOR spine (approved)")
for k, p in oc.items():
    ax.fill(p[:, 0], p[:, 1], color="white", zorder=3)

cols = ["#d9534f", "#0275d8", "#f0ad4e", "#9b59b6"]
for i, (name, path) in enumerate(ROADS.items()):
    if path is not None:
        ax.plot(path[:, 0], path[:, 1], color=cols[i], lw=6, alpha=0.8, zorder=4,
                solid_capstyle="round", label=name)
        ax.annotate(name.split(":")[0], path[len(path)//2], color=cols[i], fontsize=13, weight="bold")
for seg in fan(BODY+5, +1):
    ax.plot(seg[:, 0], seg[:, 1], color=cols[2], lw=6, alpha=0.8, zorder=4, solid_capstyle="round")
ax.annotate("3", (0, BODY+120), color=cols[2], fontsize=13, weight="bold")
for seg in fan(-BODY-5, -1):
    ax.plot(seg[:, 0], seg[:, 1], color=cols[3], lw=6, alpha=0.8, zorder=4, solid_capstyle="round")
ax.annotate("4", (0, -BODY-120), color=cols[3], fontsize=13, weight="bold")

for (x, y) in lifts:
    ax.add_patch(plt.Circle((x, y), 9, color="#34495e", zorder=6))
ax.add_patch(plt.Circle(helipad, 13, color="#e67e22", zorder=7))
ax.annotate("HELIPAD", helipad, color="#e67e22", fontsize=11, weight="bold", zorder=8)

ax.set_aspect("equal"); ax.set_xlim(-340, 340); ax.set_ylim(-560, 560)
ax.set_xlabel("X width (m)"); ax.set_ylabel("Y length (m)"); ax.grid(alpha=.3)
ax.set_title("MARKING PLAN — confirm/correct: flyover roads 1-4, lift cylinders, helipad\n"
             "(grey silhouette = base/noise -> NOT generated; consistent-width roads only)")
ax.legend(handles=[
    Patch(color="#5cb85c", label="5-FLOOR spine (approved)"),
    plt.Line2D([], [], color=cols[0], lw=6, label="1 UPPER-LOOP road"),
    plt.Line2D([], [], color=cols[1], lw=6, label="2 LOWER-LOOP road"),
    plt.Line2D([], [], color=cols[2], lw=6, label="3 N-FAN ramps"),
    plt.Line2D([], [], color=cols[3], lw=6, label="4 S-FAN ramps"),
    plt.Line2D([], [], marker="o", color="#34495e", ls="", ms=10, label=f"LIFT cylinder x{len(lifts)}"),
    plt.Line2D([], [], marker="o", color="#e67e22", ls="", ms=12, label="HELIPAD tower"),
], loc="upper right", fontsize=9)
out = os.path.join(ROOT, "renders", "PLAN_flyover_mark.png")
fig.tight_layout(); fig.savefig(out, dpi=95); print(f"[MARK] wrote {out}")
