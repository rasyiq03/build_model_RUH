#!/usr/bin/env python3
# PLAN ONLY (no build): visualize the proposed 5-floor-vs-flyover split.
# Current bug: the whole BODY (incl. wide curving arms) is 5 floors. Proposal:
# 5-floor = narrow central SPINE only (jamarat + tents, ~80 m wide, matches the
# published 950x80); FLYOVER (single level) = everything wider (arms/loops/fingers).
import os, sys, io
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

# ORGANIC spine = corridor cut from the REAL base: left edge follows the LEFT
# courtyard's inner (right) edge, right edge follows the RIGHT courtyard's inner
# (left) edge; beyond the courtyards use a narrow band, clamped to the silhouette.
def x_crossings(poly, y):
    xs = []; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
    return sorted(xs)

# spine only spans the central deck region (NOT up the fingers) -> +-BODY_HALF_Y
SPINE_Y = T.BODY_HALF_Y
ys = np.linspace(-SPINE_Y, SPINE_Y, 220)
BAND_L, BAND_R = -32.0, 64.0
left_edge = []; right_edge = []
for y in ys:
    lc = x_crossings(cy_l, y); rc = x_crossings(cy_r, y); sc = x_crossings(sil, y)
    lb = max(lc) if lc else BAND_L           # right edge of LEFT courtyard
    rb = min(rc) if rc else BAND_R           # left edge of RIGHT courtyard
    if sc:
        lb = max(lb, min(sc)); rb = min(rb, max(sc))
    if rb - lb < 8:                          # keep a minimum walkable width
        mid = (lb + rb) / 2; lb, rb = mid - 4, mid + 4
    left_edge.append((lb, y)); right_edge.append((rb, y))
SPINE = np.array(left_edge + right_edge[::-1])
print(f"[PLAN] organic spine cut from courtyards: "
      f"width range {min(r[0]-l[0] for l,r in zip(left_edge,right_edge)):.0f}.."
      f"{max(r[0]-l[0] for l,r in zip(left_edge,right_edge)):.0f} m, "
      f"verts={len(SPINE)}")

fig, ax = plt.subplots(1, 2, figsize=(15, 11))

# ---- LEFT: CURRENT (wrong) ----
a = ax[0]
a.fill(sil[:, 0], sil[:, 1], color="#d9534f", alpha=0.6, label="ALL 5-floor (current)")
a.fill(cy_l[:, 0], cy_l[:, 1], color="white"); a.fill(cy_r[:, 0], cy_r[:, 1], color="white")
for k, p in oc.items():
    a.fill(p[:, 0], p[:, 1], color="white")
a.set_title("CURRENT (wrong): whole body incl. curving ARMS = 5 floors", fontsize=11)
a.annotate("arm = 5-floor\n(should be flyover)", (-260, 200), color="darkred", fontsize=10,
           ha="center", weight="bold")
a.annotate("arm = 5-floor\n(should be flyover)", (260, -120), color="darkred", fontsize=10,
           ha="center", weight="bold")

# ---- RIGHT: PROPOSED ----
b = ax[1]
# flyover = whole silhouette (orange), spine carved green on top
b.fill(sil[:, 0], sil[:, 1], color="#f0ad4e", alpha=0.6)
b.fill(cy_l[:, 0], cy_l[:, 1], color="white"); b.fill(cy_r[:, 0], cy_r[:, 1], color="white")
# spine = ORGANIC corridor cut from the real courtyards (NOT a rectangle)
b.fill(SPINE[:, 0], SPINE[:, 1], color="#5cb85c", alpha=0.9, zorder=3)
for k, p in oc.items():
    b.fill(p[:, 0], p[:, 1], color="white", zorder=4)
    b.annotate(k, p.mean(0), fontsize=9, ha="center", zorder=5, weight="bold")
for tx, ty in [(12, -178), (12, -60), (12, 60), (12, 178)]:
    b.plot(tx, ty, "k^", ms=9, zorder=5)
b.set_title("PROPOSED: 5-floor = ORGANIC spine cut from courtyards; rest = FLYOVER", fontsize=11)
b.legend(handles=[Patch(color="#5cb85c", label="5-FLOOR deck (organic spine, jamarat+tents)"),
                  Patch(color="#f0ad4e", label="FLYOVER roads (single level, ramp to ground)"),
                  plt.Line2D([], [], marker="^", color="k", ls="", label="tent")],
         loc="upper left", fontsize=9)

for x in (a, b):
    x.set_aspect("equal"); x.set_xlim(-340, 340); x.set_ylim(-540, 540)
    x.set_xlabel("X width (m)"); x.set_ylabel("Y length (m)"); x.grid(alpha=.3)
fig.tight_layout()
out = os.path.join(ROOT, "renders", "PLAN_flyover_split.png")
fig.savefig(out, dpi=95); print(f"[PLAN] wrote {out}")
