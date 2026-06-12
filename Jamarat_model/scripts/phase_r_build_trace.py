#!/usr/bin/env python3
# =============================================================================
# PHASE R (v2) — turn the cv2-traced rough silhouette into clean mesh-ready
# polygons and write ROOT/trace_data.py (baked into PARAMETERS + standalone).
# Produces: SIL_OUTER (exact road/plaza footprint), SIL_HOLES (courtyards),
# BODY_OUTER (deck body = silhouette clipped to the central band), OCULUS
# (small holes at the 3 jamarah), TOWERS_XY (detected circle centers).
# =============================================================================
import os, sys, json, io, math
import numpy as np
import cv2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TRACE = os.path.join(ROOT, "References", "osm", "rough_trace.json")
IMG = os.path.join(ROOT, "References", "rough_ortho", "rough_top.png")
OUT = os.path.join(ROOT, "trace_data.py")

BODY_HALF_Y = 250.0    # deck body half-length (clip off only the long fan fingers)
JAM_Y = {"ULA": -191.0, "WUSTA": -56.0, "AQABAH": 192.0}
OCULUS_R = 12.0


def shoelace(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def resample(poly, n):
    p = np.vstack([poly, poly[:1]])
    seg = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
    cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], n, endpoint=False)
    return np.column_stack([np.interp(s, cum, p[:, 0]), np.interp(s, cum, p[:, 1])])


def smooth(poly, k=3, it=2):
    out = poly.copy()
    for _ in range(it):
        out = (np.roll(out, 1, 0) + out + np.roll(out, -1, 0)) / 3.0
    return out


def point_in(poly, pt):
    x, y = pt; n = len(poly); inside = False; j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def clip_band(poly, lo, hi):
    """Sutherland-Hodgman clip polygon to lo <= Y <= hi."""
    def clip_edge(pts, keep, ycut, lower):
        out = []
        n = len(pts)
        for i in range(n):
            a = pts[i]; b = pts[(i + 1) % n]
            ina = (a[1] >= ycut) if lower else (a[1] <= ycut)
            inb = (b[1] >= ycut) if lower else (b[1] <= ycut)
            if ina:
                out.append(a)
            if ina != inb:
                t = (ycut - a[1]) / (b[1] - a[1] + 1e-12)
                out.append(a + t * (b - a))
        return np.array(out) if out else pts
    p = clip_edge(poly, True, lo, True)
    p = clip_edge(p, True, hi, False)
    return p


def dedup_collinear(poly, tol=0.5):
    """Drop near-collinear vertices (prevents sliver/degenerate triangles)."""
    n = len(poly); out = []
    for i in range(n):
        a = poly[(i - 1) % n]; b = poly[i]; c = poly[(i + 1) % n]
        cross = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
        if abs(cross) > tol:
            out.append(b)
    return np.array(out) if len(out) >= 4 else poly


def circle(cx, cy, r, n=20):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])


def main():
    data = json.load(open(TRACE, encoding="utf-8"))
    cnts = [np.array(c) for c in data["contours_m"] if len(c) >= 4]
    cnts.sort(key=shoelace, reverse=True)
    outer = cnts[0]
    print(f"[TRACE] outer area={shoelace(outer):.0f} m^2, pts={len(outer)}")

    # holes = contours whose centroid is inside outer (the courtyards/gaps)
    holes = []
    for c in cnts[1:]:
        cen = c.mean(0)
        if point_in(outer, cen) and shoelace(c) > 1500:
            holes.append(c)
    holes = holes[:2]   # the two main courtyards
    print(f"[TRACE] courtyard holes kept: {len(holes)} "
          f"(areas {[round(shoelace(h)) for h in holes]})")

    SIL_OUTER = smooth(resample(outer, 220)).round(2)
    SIL_HOLES = [smooth(resample(h, 80)).round(2) for h in holes]

    # 5-floor deck BODY = organic SPINE corridor CUT FROM THE REAL BASE: its sides
    # follow the two courtyards' inner edges (approved plan). NOT a rectangle, NOT
    # the wide arms. Arms/fingers become roads (from the user's guide).
    cy_l, cy_r = holes[0], holes[1]
    if cy_l.mean(0)[0] > cy_r.mean(0)[0]:          # ensure left=lower X
        cy_l, cy_r = cy_r, cy_l
    def xcross(poly, y):
        xs = []
        for i in range(len(poly)):
            x1, y1 = poly[i]; x2, y2 = poly[(i+1) % len(poly)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y-y1)/(y2-y1)*(x2-x1))
        return sorted(xs)
    ys = np.linspace(-BODY_HALF_Y, BODY_HALF_Y, 120)
    le, re = [], []
    for y in ys:
        lc = xcross(cy_l, y); rc = xcross(cy_r, y); sc = xcross(outer, y)
        lb = max(lc) if lc else -32.0
        rb = min(rc) if rc else 64.0
        if sc:
            lb = max(lb, min(sc)); rb = min(rb, max(sc))
        if rb - lb < 10:
            m = (lb + rb) / 2; lb, rb = m - 5, m + 5
        le.append((lb, y)); re.append((rb, y))
    BODY_OUTER = smooth(np.array(le + re[::-1])).round(2)
    BODY_HOLES = []                                 # spine is solid (only OCULUS holes)
    print(f"[TRACE] BODY (organic spine) extent Y={np.ptp(BODY_OUTER[:,1]):.0f} "
          f"X={np.ptp(BODY_OUTER[:,0]):.0f}  verts={len(BODY_OUTER)}")

    OCULUS = {k: circle(0.0, y, OCULUS_R, 16).round(2) for k, y in JAM_Y.items()}

    # flyover road fingers = silhouette BEYOND the deck body (ramp down to ground)
    fly_top = clip_band(outer, BODY_HALF_Y - 4, 9999)
    fly_bot = clip_band(outer, -9999, -(BODY_HALF_Y - 4))
    FLY_TOP = dedup_collinear(smooth(resample(fly_top, 90))).round(2) if len(fly_top) >= 4 else []
    FLY_BOT = dedup_collinear(smooth(resample(fly_bot, 90))).round(2) if len(fly_bot) >= 4 else []
    print(f"[TRACE] flyover fingers: top pts={len(FLY_TOP)} bot pts={len(FLY_BOT)} "
          f"(body edge Y=±{BODY_HALF_Y:.0f})")

    # re-detect tower circles with more sensitive params (~10-12 expected)
    img = cv2.imread(IMG, cv2.IMREAD_GRAYSCALE)
    mask = (img > 90).astype(np.uint8) * 255
    h, w = img.shape
    allpx = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    allpx = np.vstack([c.reshape(-1, 2) for c in allpx])
    x0, y0 = allpx.min(0); x1, y1 = allpx.max(0)
    s = data["scale_m_per_px"]; cx_px = (x0 + x1) / 2; cy_px = (y0 + y1) / 2
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                               param1=120, param2=13, minRadius=8, maxRadius=46)
    raw = []
    if circles is not None:
        for (cxp, cyp, rp) in circles[0]:
            raw.append(((cxp - cx_px) * s, (cy_px - cyp) * s, rp * s))
    # cluster nearby detections (merge within 22 m), keep the bigger radius
    raw.sort(key=lambda c: -c[2])
    TOWERS = []
    for X, Y, R in raw:
        if all(math.hypot(X - tx, Y - ty) > 22 for tx, ty in TOWERS):
            # keep only circles sitting on actual structure (towers are at edges)
            TOWERS.append((round(float(X), 1), round(float(Y), 1)))
    print(f"[TRACE] towers detected raw={len(raw)} -> clustered={len(TOWERS)}")

    def fmt(poly):
        return "[" + ",".join(f"({x:.2f},{y:.2f})" for x, y in poly) + "]"

    with open(OUT, "w", encoding="utf-8") as f:
        f.write('# AUTO-GENERATED by scripts/phase_r_build_trace.py — do not hand-edit.\n')
        f.write('# Exact abstract Jamarat footprint traced from the user rough 3D model\n')
        f.write('# (References/rough_ortho/rough_top.png) via OpenCV. Meters, origin=center,\n')
        f.write('# +Y = length. Shape is INTENTIONALLY organic (not an oval).\n\n')
        f.write("SIL_OUTER = " + fmt(SIL_OUTER) + "\n\n")
        f.write("SIL_HOLES = [\n")
        for hpoly in SIL_HOLES:
            f.write("  " + fmt(hpoly) + ",\n")
        f.write("]\n\n")
        f.write("BODY_OUTER = " + fmt(BODY_OUTER) + "\n\n")
        f.write("BODY_HOLES = [\n")
        for hpoly in BODY_HOLES:
            f.write("  " + fmt(hpoly) + ",\n")
        f.write("]\n\n")
        f.write("OCULUS = {\n")
        for k, poly in OCULUS.items():
            f.write(f"  '{k}': " + fmt(poly) + ",\n")
        f.write("}\n\n")
        f.write(f"BODY_HALF_Y = {BODY_HALF_Y}\n")
        f.write(f"FLY_TIP_Y = {float(np.max(np.abs(outer[:,1]))):.1f}\n\n")
        f.write("FLY_TOP = " + (fmt(FLY_TOP) if len(FLY_TOP) else "[]") + "\n\n")
        f.write("FLY_BOT = " + (fmt(FLY_BOT) if len(FLY_BOT) else "[]") + "\n\n")
        f.write("TOWERS_XY = [" + ",".join(f"({x},{y})" for x, y in TOWERS) + "]\n")
    print(f"[TRACE] wrote {OUT}")


if __name__ == "__main__":
    main()
