# components/comp_decks.py
# =============================================================================
# Emits the 5 stacked open parking-deck slabs of the Jamaraat Bridge, traced
# from the REAL OSM footprint (NOT a clean oval — legacy oval REJECTED, see
# AGENTS.md USER OVERRIDE). Shape = OSM ways PARAMETERS.DECK_OSM_WAYS
# (440922995 main jamarat platform + 431634032 west spine), already reprojected
# to local meters in references/aerial/osm/local_meters.json.
#
# Each level = one watertight prism per deck polygon (concave top/bottom n-gon
# caps + side walls; n-gons get triangulated by ruh_common.bm_to_object). No
# boolean. Levels stack at PARAMETERS.FLOOR_Z (0/12/24/36/48 m).
#   TODO/VERIFY@render: jamrah oculi (holes), per-deck parapet/fascia rim, and
#   refining the exact edge vs the real aerial — deck SHAPE (real, non-oval) first.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_decks.py
# =============================================================================
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_STRUCT_DECKS_VIS"
COLLECTION = "STRUCTURE"
TRI_CAP    = P.DECKS["TARGET_TRI"]


def _dedupe(poly):
    """Drop consecutive duplicate points (degenerate edges break manifoldness)."""
    out = []
    for p in poly:
        if not out or (abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6):
            out.append(p)
    # also guard wrap-around duplicate
    if len(out) > 1 and out[0] == out[-1]:
        out = out[:-1]
    return out


def _prism(bm, poly, z_lo, z_hi):
    """Closed prism from a flat (concave-ok) polygon, z_lo..z_hi. Watertight:
    top cap + bottom cap (n-gons, triangulated downstream) + quad side walls."""
    top = [bm.verts.new((x, y, z_hi)) for (x, y) in poly]
    bot = [bm.verts.new((x, y, z_lo)) for (x, y) in poly]
    bm.faces.new(top)                       # top cap
    bm.faces.new(list(reversed(bot)))       # bottom cap (opposite winding)
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top[i], top[j], bot[j], bot[i]))   # side wall quad


def build(collection=None):
    """Build all 5 deck levels (real OSM shape) into `collection`; return the object."""
    D = P.DECKS
    collection = collection or C.reset_collection(COLLECTION)

    ways = P.load_osm_ways()
    polys = [_dedupe(ways[wid]) for wid in P.DECK_OSM_WAYS if wid in ways]

    bm = bmesh.new()
    for lvl in range(1, P.FLOOR_COUNT + 1):
        z_top = P.FLOOR_Z[lvl]
        z_bot = z_top - D["SLAB_THICK"]
        for poly in polys:
            _prism(bm, poly, z_bot, z_top)

    return C.bm_to_object(bm, NAME, collection, material_key="CONCRETE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'decks' (real OSM footprint) -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
