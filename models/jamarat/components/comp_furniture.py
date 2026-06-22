# components/comp_furniture.py
# =============================================================================
# Street furniture: lamp poles spaced along the TOP-deck edge (instanced master).
# Pole + lamp head; spacing/height from PARAMETERS.FURNITURE. (Cooling-fan poles
# + signage = later additions.) cf examples/comp_lamp_post.py.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_furniture.py
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

NAME       = "RUH_FURN_LAMPS_VIS"
COLLECTION = "FURNITURE"
TRI_CAP    = P.FURNITURE["TARGET_TRI"]


def _perimeter_points(poly, spacing, inset):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    pts, carry, n = [], 0.0, len(poly)
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
            vx, vy = cx - px, cy - py
            vL = math.hypot(vx, vy) or 1.0
            pts.append((px + vx / vL * inset, py + vy / vL * inset))
            d += spacing
        carry = d - L
    return pts


def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    Fp = P.FURNITURE
    ways = P.load_osm_ways()
    poly = ways[P.DECK_OSM_WAYS[0]]
    z0 = P.FLOOR_Z[P.FLOOR_COUNT]          # top-deck level
    h = Fp["LAMP_H"]

    bm = bmesh.new()
    for (x, y) in _perimeter_points(poly, Fp["LAMP_SPACING"], 2.0):
        C.add_capped_cone(bm, 0.18, 0.14, h, Matrix.Translation((x, y, z0 + h / 2.0)), 8)   # pole
        C.add_box(bm, 1.1, 0.5, 0.3, Matrix.Translation((x, y, z0 + h + 0.15)))             # head
    return C.bm_to_object(bm, NAME, collection, material_key="METAL")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'furniture' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
