# components/comp_columns.py
# =============================================================================
# Emits the deck support PIERS. The current Jamaraat Bridge is intentionally
# COLUMN-FREE inside (DATA 2026-06-15: clear spans 60-100 m so pilgrims see all
# 3 jamrah from anywhere; deck box girders @9 m supported at the EDGES). So
# columns are placed ONLY around the deck PERIMETER (PARAMETERS.DECK_OSM_WAYS),
# big square piers spaced ~COLUMNS.PERIM_SPACING, inset slightly from the edge,
# rising full height. No interior grid (old dense 12 m grid = REJECTED).
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_columns.py
# =============================================================================
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
from mathutils import Matrix
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_STRUCT_COLUMNS_VIS"
COLLECTION = "STRUCTURE"
TRI_CAP    = P.COLUMNS["TARGET_TRI"]


def _dedupe(poly):
    out = []
    for p in poly:
        if not out or (abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6):
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out = out[:-1]
    return out


def _centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def _perimeter_points(poly, spacing, inset):
    """Walk the polygon boundary, drop a point every `spacing` metres, nudged
    `inset` toward the centroid so piers sit just inside the edge."""
    cx, cy = _centroid(poly)
    pts = []
    carry = 0.0
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        d = carry
        while d < L:
            t = d / L
            px, py = ax + t * dx, ay + t * dy
            vx, vy = cx - px, cy - py            # toward centroid
            vL = math.hypot(vx, vy) or 1.0
            pts.append((px + vx / vL * inset, py + vy / vL * inset))
            d += spacing
        carry = d - L
    return pts


def build(collection=None):
    """Build the perimeter pier ring (full height) into `collection`; return obj."""
    K = P.COLUMNS
    collection = collection or C.reset_collection(COLLECTION)

    ways = P.load_osm_ways()
    height = P.FLOOR_Z[P.FLOOR_COUNT]      # ground (0) -> top deck

    bm = bmesh.new()
    for wid in P.DECK_OSM_WAYS:
        if wid not in ways:
            continue
        for (x, y) in _perimeter_points(_dedupe(ways[wid]), K["PERIM_SPACING"], K["RING_INSET"]):
            C.add_box(bm, K["SIZE"], K["SIZE"], height, Matrix.Translation((x, y, height / 2.0)))

    return C.bm_to_object(bm, NAME, collection, material_key="CONCRETE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'columns' (perimeter piers) -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
