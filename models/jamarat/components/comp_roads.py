# components/comp_roads.py
# =============================================================================
# Emits the flyover/road network around the core: every OSM bridge way that is
# NOT the core deck (PARAMETERS.DECK_OSM_WAYS) — the west spine 431634032, east
# approach 431617753 and the interchange/approach ramps — built as a flat slab
# at the elevation bound in PARAMETERS.TRACE["ROAD_LEVEL_MAP"] (height_m).
#   VERIFY@render: real arms SLOPE (descend L3->L1 etc.); flat slabs for now.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_roads.py
# =============================================================================
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_RAMPS_ROADS_VIS"
COLLECTION = "RAMPS"
TRI_CAP    = P.ROADS["TARGET_TRI"]


def _dedupe(poly):
    out = []
    for p in poly:
        if not out or (abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6):
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out = out[:-1]
    return out


def _prism(bm, poly, z_lo, z_hi):
    top = [bm.verts.new((x, y, z_hi)) for (x, y) in poly]
    bot = [bm.verts.new((x, y, z_lo)) for (x, y) in poly]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top[i], top[j], bot[j], bot[i]))


def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    ways = P.load_osm_ways()
    lvl_map = P.TRACE["ROAD_LEVEL_MAP"]
    th = P.ROADS["THICKNESS"]

    bm = bmesh.new()
    for wid, poly in ways.items():
        if wid in P.DECK_OSM_WAYS:
            continue
        z_top = float(lvl_map.get(wid, {}).get("height_m", 10))
        _prism(bm, _dedupe(poly), z_top - th, z_top)

    return C.bm_to_object(bm, NAME, collection, material_key="CONCRETE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'roads' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
