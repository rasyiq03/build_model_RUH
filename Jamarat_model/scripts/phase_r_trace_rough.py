#!/usr/bin/env python3
# =============================================================================
# PHASE R (v2) — EXACT shape trace from the user's rough 3D model top-ortho.
# User mandate: match the REAL abstract footprint exactly (NOT a clean oval).
# Extract the structure silhouette + road network from References/rough_ortho/
# rough_top.png via OpenCV contours, reproject px->meters (long axis = +Y),
# centered at footprint centroid. Emits traced polylines (JSON) + overlay PNG.
# =============================================================================
import os, sys, json, io
import numpy as np
import cv2
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
IMG = os.path.join(ROOT, "References", "rough_ortho", "rough_top.png")
OUT_JSON = os.path.join(ROOT, "References", "osm", "rough_trace.json")
OUT_PNG = os.path.join(ROOT, "References", "osm", "rough_trace_overlay.png")

TARGET_FULL_LEN_M = 1050.0   # full silhouette height (incl. fan ramps) -> meters


def main():
    img = cv2.imread(IMG, cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"cannot read {IMG}")
    h, w = img.shape
    # structure = brighter than the BLACK background (bg=0, structure grey 150-194)
    mask = (img > 90).astype(np.uint8) * 255
    # clean small specks + close gaps
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k, iterations=1)

    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    cnts = [c for c in cnts if cv2.contourArea(c) > 200]
    cnts.sort(key=cv2.contourArea, reverse=True)
    print(f"[ROUGH] image {w}x{h}px, {len(cnts)} contours (area>200)")

    # bounding box of all structure px -> scale so full height = TARGET length
    allpx = np.vstack([c.reshape(-1, 2) for c in cnts])
    x0, y0 = allpx.min(0); x1, y1 = allpx.max(0)
    px_h = (y1 - y0)
    s = TARGET_FULL_LEN_M / px_h          # meters per pixel
    cx_px = (x0 + x1) / 2.0; cy_px = (y0 + y1) / 2.0
    print(f"[ROUGH] silhouette bbox px=({x1-x0}x{y1-y0}) scale={s:.3f} m/px")
    print(f"[ROUGH] full extent: X={ (x1-x0)*s:.0f} m  Y={ (y1-y0)*s:.0f} m")

    def to_m(pts):
        pts = pts.reshape(-1, 2).astype(float)
        X = (pts[:, 0] - cx_px) * s            # image col -> +X
        Y = (cy_px - pts[:, 1]) * s            # image row flip -> +Y (length)
        return np.column_stack([X, Y])

    # detect tower circles (Hough) on the mask
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1.2,
                               minDist=24, param1=120, param2=18,
                               minRadius=10, maxRadius=40)
    towers = []
    if circles is not None:
        for (cxp, cyp, rp) in circles[0]:
            X = (cxp - cx_px) * s; Y = (cy_px - cyp) * s
            towers.append({"pos": [round(float(X), 1), round(float(Y), 1)],
                           "r": round(float(rp * s), 1)})
    print(f"[ROUGH] detected tower circles: {len(towers)}")

    polys = []
    for c in cnts:
        approx = cv2.approxPolyDP(c, 2.0, True)   # simplify ~2px
        polys.append(to_m(approx).round(2).tolist())

    data = {"source": "rough_ortho/rough_top.png (Tripo rough model, user)",
            "scale_m_per_px": s, "target_full_len_m": TARGET_FULL_LEN_M,
            "contours_m": polys, "towers_m": towers}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[ROUGH] wrote {OUT_JSON}  ({len(polys)} contours)")

    # overlay
    fig, ax = plt.subplots(1, 2, figsize=(13, 11))
    ax[0].imshow(img, cmap="gray"); ax[0].imshow(mask, alpha=0.3); ax[0].set_title("mask")
    for p in polys:
        a = np.array(p); ax[1].plot(a[:, 0], a[:, 1], lw=1.0)
    for t in towers:
        ax[1].scatter(*t["pos"], c="r", s=30)
    ax[1].set_aspect("equal"); ax[1].grid(alpha=.3)
    ax[1].set_title(f"traced (m)  full {(x1-x0)*s:.0f}x{(y1-y0)*s:.0f}  towers={len(towers)}")
    ax[1].set_xlabel("X width (m)"); ax[1].set_ylabel("Y length (m)")
    fig.tight_layout(); fig.savefig(OUT_PNG, dpi=100); print(f"[ROUGH] wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
