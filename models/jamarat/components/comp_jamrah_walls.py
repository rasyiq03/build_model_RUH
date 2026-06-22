# components/comp_jamrah_walls.py
# =============================================================================
# Emits the 3 Jamrah stoning walls + their pebble basins. Each Jamrah is a tall
# ELLIPTICAL stone blade (long axis across the spine = X), tapering toward the
# top, planted in a low oval pebble basin, rising through all decks + above roof.
# Order along +Y: ULA (-Y, smallest) -> WUSTA -> AQABAH (+Y, biggest), per
# AGENTS.md §A + PARAMETERS.TRACE["JAMRAH"]. Material = GRANITE (a textured
# highlight element in the TEXTURED build).
#   TODO/VERIFY@render: sloped/rounded wall top; per-deck oculus parapets (pair
#   with the deck oculi, currently deferred); exact basin profile.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_jamrah_walls.py
# =============================================================================
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_JAMARAT_WALLS_VIS"
COLLECTION = "JAMARAT"
TRI_CAP    = P.JAMRAH_WALLS["TARGET_TRI"]

_EPS = 0.01


def _dedupe(poly):
    out = []
    for p in poly:
        if not out or (abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6):
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out = out[:-1]
    return out


def _deck_center_x(y, poly):
    """X of the deck spine centreline at height y = midpoint of the polygon's
    left/right edge crossings. The real spine CURVES, so jamrah must sit on this
    centre, NOT on a straight x=0 line (user fix 2026-06-15)."""
    xs = []
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        if (ay > y) != (by > y):
            xs.append(ax + (y - ay) / (by - ay) * (bx - ax))
    return None if not xs else 0.5 * (min(xs) + max(xs))


def _ellipse(cx, cy, ax, by, n):
    """n points on an ellipse: long axis = X (ax), short axis = Y (by)."""
    return [(cx + ax * math.cos(2 * math.pi * i / n),
             cy + by * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _loft(bm, bot_pts, top_pts, z_lo, z_hi):
    """Closed solid lofting bot_pts(@z_lo) -> top_pts(@z_hi). Watertight."""
    bot = [bm.verts.new((x, y, z_lo)) for (x, y) in bot_pts]
    top = [bm.verts.new((x, y, z_hi)) for (x, y) in top_pts]
    bm.faces.new(list(reversed(bot)))   # bottom cap
    bm.faces.new(top)                    # top cap
    n = len(bot)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))


def _annular_box(bm, outer_pts, inner_pts, z_lo, z_hi):
    """Closed annular box between two equal-count loops (e.g. basin rim)."""
    ot = [bm.verts.new((x, y, z_hi)) for (x, y) in outer_pts]
    ob = [bm.verts.new((x, y, z_lo)) for (x, y) in outer_pts]
    it = [bm.verts.new((x, y, z_hi)) for (x, y) in inner_pts]
    ib = [bm.verts.new((x, y, z_lo)) for (x, y) in inner_pts]
    n = len(outer_pts)

    def bridge(a, b):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bridge(ot, it); bridge(ib, ob); bridge(ot, ob); bridge(ib, it)


def build(collection=None):
    """Build the 3 jamrah walls + basins into `collection`; return the object."""
    W = P.JAMRAH_WALLS
    n = W["WALL_VERTS"]
    collection = collection or C.reset_collection(COLLECTION)

    # Deck spine polygon -> place each jamrah on the CURVING deck centreline.
    ways = P.load_osm_ways()
    deck_poly = _dedupe(ways[P.DECK_OSM_WAYS[0]]) if P.DECK_OSM_WAYS[0] in ways else None

    bm = bmesh.new()
    for key, j in P.TRACE["JAMRAH"].items():
        cx, cy = j["pos"]
        if deck_poly is not None:
            mid = _deck_center_x(cy, deck_poly)
            if mid is not None:
                cx = mid                       # follow the curved spine, not x=0
        half_x = j["len_x"] / 2.0
        base_b = j["thick_y"] / 2.0
        top_b = W["THICK_TOP"] / 2.0
        z_base = -W["PLATFORM_THICK"]
        z_top = P.TRACE["JAMRAH_HEIGHT_TOTAL"]

        # 1) Elliptical wall, tapering (long axis -10%, short axis -> THICK_TOP).
        base_ring = _ellipse(cx, cy, half_x, base_b, n)
        top_ring = _ellipse(cx, cy, half_x * 0.9, top_b, n)
        _loft(bm, base_ring, top_ring, z_base, z_top)

        # 2) Pebble basin: oval floor slab + low rim ring around the wall.
        if j.get("basin"):
            bo_a, bo_b = half_x + 8.0, base_b + 6.0          # basin outer semi-axes
            outer = _ellipse(cx, cy, bo_a, bo_b, n)
            inner = _ellipse(cx, cy, bo_a - 1.2, bo_b - 1.2, n)
            # floor slab (just below ground), then rim floated up a hair.
            _loft(bm, outer, outer, -W["PLATFORM_THICK"] - 0.3, -W["PLATFORM_THICK"])
            _annular_box(bm, outer, inner, _EPS, _EPS + W["BASIN_RIM_H"])

    return C.bm_to_object(bm, NAME, collection, material_key="GRANITE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'jamrah_walls' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
