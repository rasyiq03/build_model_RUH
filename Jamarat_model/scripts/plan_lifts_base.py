#!/usr/bin/env python3
# Clean BASE plan (spine + current guide roads + oculus calibration dots) for the
# user to DRAW the lift/helipad boxes on (same workflow as the road guide).
import os, sys, io
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import trace_data as T
import guide_roads as GR

fig, ax = plt.subplots(figsize=(8.5, 12))
# spine
b = np.array(T.BODY_OUTER); ax.fill(b[:, 0], b[:, 1], color="#5cb85c", alpha=0.8, zorder=2)
# roads
for polys, col in ((GR.BLUE_POLYS, "royalblue"), (GR.RED_POLYS, "crimson"),
                   (GR.PURPLE_POLYS, "mediumorchid")):
    for p in polys:
        a = np.array(p + [p[0]]); ax.fill(a[:, 0], a[:, 1], color=col, alpha=0.5, zorder=1)
# oculus calibration dots (KEEP these visible so the drawn plan can be re-traced)
for k, p in T.OCULUS.items():
    pp = np.array(p); cx, cy = pp.mean(0)
    ax.add_patch(plt.Circle((cx, cy), 7, color="white", ec="k", zorder=5))
    ax.annotate(k, (cx + 12, cy), fontsize=11, weight="bold", zorder=6)
ax.set_aspect("equal"); ax.set_xlim(-330, 330); ax.set_ylim(-560, 560)
ax.set_xlabel("X width (m)"); ax.set_ylabel("Y length (m)"); ax.grid(alpha=.3)
ax.set_title("DRAW the lift/helipad boxes here:\n"
             "ORANGE = big cylinder lift building, YELLOW = small tube lift, "
             "CYAN x2 = helipad\n(keep the white oculus dots visible for calibration)")
out = os.path.join(ROOT, "renders", "PLAN_lifts_base.png")
fig.tight_layout(); fig.savefig(out, dpi=110); print(f"wrote {out}")
