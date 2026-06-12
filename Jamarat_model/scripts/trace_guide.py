#!/usr/bin/env python3
# Trace the user's hand-drawn road guide (renders/PLAN_flyover_split_implementation.PNG).
# It is drawn ON the model-frame plan, so calibrate px->m via the oculus dots
# (AQABAH Y=+192, ULA Y=-191, X=0 column), then segment the stroke colours.
import os, sys, io, json
import numpy as np, cv2
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import trace_data as T
IMG = os.path.join(ROOT, "renders", "PLAN_flyover_split_implementation.PNG")
bgr = cv2.imread(IMG); H, W = bgr.shape[:2]
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

# --- calibrate via central white oculus dots ---
white = cv2.inRange(hsv, (0, 0, 225), (180, 40, 255))
n, lab, stats, _ = cv2.connectedComponentsWithStats(white)
dots = [(stats[i,0]+stats[i,2]/2, stats[i,1]+stats[i,3]/2) for i in range(1, n)
        if 40 < stats[i, 4] < 600 and 0.30*W < stats[i,0]+stats[i,2]/2 < 0.62*W]
dots.sort(key=lambda d: d[1])
aq = dots[0]; ula = dots[-1]                      # top dot=AQABAH(+192), bottom=ULA(-191)
x0 = np.mean([d[0] for d in dots])
s = (192.0 - (-191.0)) / (ula[1] - aq[1])          # m per pixel-row
def to_m(col, row):
    return np.column_stack([(np.asarray(col) - x0) * s,
                            192.0 - (np.asarray(row) - aq[1]) * s])
print(f"[GUIDE] x0={x0:.0f} aq_row={aq[1]:.0f} ula_row={ula[1]:.0f} s={s:.3f} m/px")

# --- segment stroke colours ---
def m(hlo, hhi, slo, vlo, vhi=255):
    return cv2.inRange(hsv, (hlo, slo, vlo), (hhi, 255, vhi))
masks = {
    "BLUE":   m(100, 119, 90, 90),
    "RED":    cv2.bitwise_or(m(0, 8, 110, 90), m(160, 179, 110, 90)),
    "PURPLE": m(125, 150, 70, 130),                 # medium/bright purple
    "DPURPLE": m(120, 150, 50, 45, 128),            # darker purple (low value)
}
def clean(x, k=400):
    x = cv2.morphologyEx(x, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    nn, ll, st, _ = cv2.connectedComponentsWithStats(x)
    o = np.zeros_like(x)
    for i in range(1, nn):
        if st[i, cv2.CC_STAT_AREA] >= k:
            o[ll == i] = 255
    return o
masks = {k: clean(v) for k, v in masks.items()}
for k, v in masks.items():
    print(f"[GUIDE] {k}: {int((v>0).sum())} px")

# --- to model points ---
roads = {}
for k, v in masks.items():
    ys, xs = np.where(v > 0)
    roads[k] = to_m(xs[::4], ys[::4]) if len(xs) else np.empty((0, 2))

# --- plot over the model spine ---
sil = np.array(T.SIL_OUTER)
fig, ax = plt.subplots(figsize=(9, 13))
ax.fill(sil[:, 0], sil[:, 1], color="0.93", alpha=0.5, zorder=0)
for k, p in T.OCULUS.items():
    pp = np.array(p); ax.fill(pp[:, 0], pp[:, 1], color="k", zorder=5)
    ax.annotate(k, pp.mean(0), fontsize=10, zorder=6)
colors = {"BLUE": "royalblue", "RED": "crimson", "PURPLE": "mediumorchid", "DPURPLE": "indigo"}
for k, p in roads.items():
    if len(p):
        ax.scatter(p[:, 0], p[:, 1], s=4, c=colors[k], alpha=0.5, label=k, zorder=3)
ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_xlabel("X width (m)"); ax.set_ylabel("Y length (m)")
ax.set_title("Traced from your hand-drawn guide (model frame)\n"
             "BLUE / RED(pink) = top-floor roads?  PURPLE / DPURPLE = floor3->ground ramps?")
ax.legend(loc="upper right", markerscale=3, fontsize=10)
out = os.path.join(ROOT, "renders", "PLAN_guide_traced.png")
fig.tight_layout(); fig.savefig(out, dpi=95); print(f"[GUIDE] wrote {out}")

# save road points for the build step
data = {k: roads[k].round(1).tolist() for k in roads}
json.dump(data, open(os.path.join(ROOT, "References", "osm", "guide_roads.json"), "w"))
print("[GUIDE] wrote guide_roads.json")
