#!/usr/bin/env python3
# Trace the colour overlay in References/label acuan.JPG -> model coords.
# Roads: PINK (top-floor), BLUE (top-floor), PURPLE (floor3->ground ramp).
# Boxes: ORANGE (big lift building), YELLOW (small tube lift), CYAN (helipad x2).
# Registration: detect the white jamarat spine, map its endpoints to the model
# jamarat span ULA(0,-191)..AQABAH(0,192). Outputs debug masks + a marking plan.
import os, sys, io, math, json
import numpy as np, cv2
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import trace_data as T
IMG = os.path.join(ROOT, "References", "label acuan.JPG")
OUTdir = os.path.join(ROOT, "renders"); os.makedirs(OUTdir, exist_ok=True)

bgr = cv2.imread(IMG); H, W = bgr.shape[:2]
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

def mask(hlo, hhi, slo=90, vlo=90):
    return cv2.inRange(hsv, (hlo, slo, vlo), (hhi, 255, 255))

M = {
    "PINK":   mask(158, 178, 110, 120),
    "BLUE":   mask(100, 122, 90, 90),
    "PURPLE": mask(123, 150, 70, 70),
    "ORANGE": mask(3, 18, 130, 150),
    "YELLOW": mask(22, 38, 110, 170),
    "CYAN":   mask(85, 99, 110, 140),
}
def keep_big(m, minarea):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    out = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= minarea:
            out[lab == i] = 255
    return out

for k, m in M.items():
    minar = 2500 if k in ("PINK", "BLUE", "PURPLE") else 120
    M[k] = keep_big(m, minar)
    print(f"[LABEL] {k}: {int((M[k]>0).sum())} px")

# ---- registration: white spine basins INSIDE the road loop ----
# The pink/blue/purple roads enclose the real jamarat spine; use their convex
# hull as the search region so tent-city / building whites are excluded.
road_all = M["PINK"] | M["BLUE"] | M["PURPLE"]
ys_r, xs_r = np.where(road_all > 0)
hull = cv2.convexHull(np.column_stack([xs_r, ys_r]))
band = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(band, hull, 255)
band = cv2.erode(band, np.ones((15, 15), np.uint8))   # stay well inside the roads
white = cv2.inRange(hsv, (0, 0, 212), (180, 35, 255))  # only the PURE-white tents
white = cv2.bitwise_and(white, band)
white = cv2.morphologyEx(white, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
cnts, _ = cv2.findContours(white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = [c for c in cnts if cv2.contourArea(c) > 400]
cents = np.array([c.reshape(-1, 2).mean(0) for c in cnts])
print(f"[LABEL] white spine blobs: {len(cents)}")
# PCA line through the basin centroids
mean = cents.mean(0); u, s, vt = np.linalg.svd(cents - mean)
axis = vt[0]                                   # spine direction (px)
proj = (cents - mean) @ axis
p_min = mean + axis * proj.min(); p_max = mean + axis * proj.max()
# Orient by the ROADS (user: PINK road -> AQABAH end, BLUE road -> ULA end).
def centroid(m):
    ys, xs = np.where(m > 0); return np.array([xs.mean(), ys.mean()])
pink_c = centroid(M["PINK"]); blue_c = centroid(M["BLUE"])
pp = (pink_c - mean) @ axis; bp = (blue_c - mean) @ axis
if pp >= bp:                       # pink at the high-projection end
    p_aq, p_ula = p_max, p_min
else:                              # pink at the low-projection end
    p_aq, p_ula = p_min, p_max
A = np.array([0.0, -191.0])        # ULA  (model)
B = np.array([0.0,  192.0])        # AQABAH (model)
img_vec = p_aq - p_ula; mdl_vec = B - A
scale = np.linalg.norm(mdl_vec) / (np.linalg.norm(img_vec) + 1e-9)
ang = math.atan2(mdl_vec[1], mdl_vec[0]) - math.atan2(img_vec[1], img_vec[0])
ca, sa = math.cos(ang), math.sin(ang)
Rm = np.array([[ca, -sa], [sa, ca]]) * scale
def to_model(px):                  # px: Nx2 (col,row)
    return (px - p_ula) @ Rm.T + A
print(f"[LABEL] pink_end={'max' if pp>=bp else 'min'} -> AQABAH | "
      f"scale={scale:.3f} m/px  angle={math.degrees(ang):.1f} deg")

def mask_points(m, step=6):
    ys, xs = np.where(m > 0)
    pts = np.column_stack([xs, ys])[::step]
    return to_model(pts) if len(pts) else np.empty((0, 2))

def box_centroids(m, amin=120, amax=40000):
    # boxes are drawn as rectangle OUTLINES -> dilate to close, then contour
    md = cv2.dilate(m, np.ones((7, 7), np.uint8))
    cn, _ = cv2.findContours(md, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cn:
        a = cv2.contourArea(c)
        if amin < a < amax:
            M0 = cv2.moments(c)
            if M0["m00"] > 0:
                p = to_model(np.array([[M0["m10"]/M0["m00"], M0["m01"]/M0["m00"]]]))[0]
                if abs(p[0]) < 330 and abs(p[1]) < 340:    # within the structure region
                    out.append((float(p[0]), float(p[1])))
    return out

roads = {k: mask_points(M[k]) for k in ("PINK", "BLUE", "PURPLE")}
boxes = {k: box_centroids(M[k]) for k in ("ORANGE", "YELLOW", "CYAN")}
for k, b in boxes.items():
    print(f"[LABEL] {k} boxes: {len(b)}")

# ---- approved green spine corridor (context) ----
sil = np.array(T.SIL_OUTER); cy_l = np.array(T.SIL_HOLES[0]); cy_r = np.array(T.SIL_HOLES[1])
def xcross(poly, y):
    xs = []; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i+1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y-y1)/(y2-y1)*(x2-x1))
    return sorted(xs)
ys = np.linspace(-T.BODY_HALF_Y, T.BODY_HALF_Y, 200); le = []; re = []
for y in ys:
    lc = xcross(cy_l, y); rc = xcross(cy_r, y); sc = xcross(sil, y)
    lb = max(lc) if lc else -32.0; rb = min(rc) if rc else 64.0
    if sc: lb = max(lb, min(sc)); rb = min(rb, max(sc))
    if rb-lb < 8: m = (lb+rb)/2; lb, rb = m-4, m+4
    le.append((lb, y)); re.append((rb, y))
SPINE = np.array(le + re[::-1])
fig, ax = plt.subplots(figsize=(11, 13))
ax.fill(sil[:, 0], sil[:, 1], color="0.92", alpha=0.5, zorder=0)
ax.fill(SPINE[:, 0], SPINE[:, 1], color="#5cb85c", alpha=0.7, zorder=1, label="5-floor spine")
for k, c in (("PINK", "magenta"), ("BLUE", "royalblue"), ("PURPLE", "purple")):
    p = roads[k]
    if len(p):
        ax.scatter(p[:, 0], p[:, 1], s=2, c=c, alpha=0.35, zorder=2, label=f"{k} road")
for nm, col, mk in (("ORANGE", "darkorange", "s"), ("YELLOW", "gold", "o"), ("CYAN", "deepskyblue", "^")):
    for (x, y) in boxes[nm]:
        ax.scatter(x, y, c=col, marker=mk, s=120, edgecolor="k", zorder=5)
for k, p in T.OCULUS.items():
    pp = np.array(p); ax.fill(pp[:, 0], pp[:, 1], color="k", zorder=6)
    ax.annotate(k, pp.mean(0), color="k", fontsize=9, zorder=7)
ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_xlabel("X width (m)"); ax.set_ylabel("Y length (m)")
ax.set_title("TRACED from label acuan.JPG -> model frame (registered via spine)\n"
             "PINK/BLUE=top-floor roads, PURPLE=floor3->ground ramp; "
             "sq=ORANGE lift, o=YELLOW lift, ^=CYAN helipad")
ax.legend(loc="upper right", fontsize=8, markerscale=4)
out = os.path.join(OUTdir, "PLAN_label_traced.png")
fig.tight_layout(); fig.savefig(out, dpi=95); print(f"[LABEL] wrote {out}")

# debug overlay on the ORIGINAL image: spine endpoints + pink/blue centroids
ov = bgr.copy()
for c in cents:
    cv2.circle(ov, tuple(c.astype(int)), 5, (0, 255, 0), -1)
cv2.circle(ov, tuple(p_ula.astype(int)), 22, (255, 255, 255), 4)
cv2.putText(ov, "ULA", tuple(p_ula.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
cv2.circle(ov, tuple(p_aq.astype(int)), 22, (0, 0, 0), 4)
cv2.putText(ov, "AQABAH", tuple(p_aq.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 3)
cv2.circle(ov, tuple(pink_c.astype(int)), 26, (255, 0, 255), 5)
cv2.putText(ov, "PINK", tuple(pink_c.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,255), 3)
cv2.circle(ov, tuple(blue_c.astype(int)), 26, (255, 120, 0), 5)
cv2.putText(ov, "BLUE", tuple(blue_c.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,120,0), 3)
cv2.imwrite(os.path.join(OUTdir, "PLAN_label_debug.png"), ov)
print("[LABEL] wrote PLAN_label_debug.png")

# debug mask mosaic
dbg = np.zeros((H, W, 3), np.uint8)
palette = {"PINK": (255, 0, 255), "BLUE": (255, 100, 0), "PURPLE": (200, 0, 120),
           "ORANGE": (0, 140, 255), "YELLOW": (0, 220, 255), "CYAN": (255, 220, 0)}
for k, m in M.items():
    dbg[m > 0] = palette[k]
cv2.imwrite(os.path.join(OUTdir, "PLAN_label_masks.png"), dbg)
print("[LABEL] wrote PLAN_label_masks.png")
