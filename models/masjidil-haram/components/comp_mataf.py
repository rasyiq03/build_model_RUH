# components/comp_mataf.py
# =============================================================================
# Komponen: Mataf — marble tawaf platform around the Ka'bah.
# Ref: masjidilharam010038 (2026-06-24):
#   - SOLID DISK (no inner hole) — Ka'bah sits on top at origin, center fully filled.
#   - Outer boundary: circle r_outer = INNER_CLEAR + RING_WIDTH = 47 m.
#   - LEVELS=1 (single ground-floor base slab).
#   - Prayer lines: concentric raised ring markers on top surface.
#   - No barrier wall (not visible in reference; removed 2026-06-24).
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_mataf.py
# =============================================================================
import sys, os, math

HERE      = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
ROOT      = os.path.dirname(os.path.dirname(MODEL_DIR))
for _p in (MODEL_DIR, ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bmesh
import PARAMETERS as P
import ruh_common as C

COLLECTION = "MATAF"
TRI_CAP    = P.MATAF["TARGET_TRI"]


def _solid_disk(bm, r, z0, z1, sides):
    """Solid disk: center vertex + fan triangles top/bottom + quad side wall.
    Tri count = sides * 4 (2 fan tris top + 2 fan tris bottom + 2 quad tris side)."""
    angles  = [2 * math.pi * i / sides for i in range(sides)]
    bot_rim = [bm.verts.new((r * math.cos(a), r * math.sin(a), z0)) for a in angles]
    top_rim = [bm.verts.new((r * math.cos(a), r * math.sin(a), z1)) for a in angles]
    bot_ctr = bm.verts.new((0.0, 0.0, z0))
    top_ctr = bm.verts.new((0.0, 0.0, z1))
    bm.verts.ensure_lookup_table()
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new([top_ctr, top_rim[i], top_rim[j]])   # top fan (CCW from above)
        bm.faces.new([bot_ctr, bot_rim[j], bot_rim[i]])   # bottom fan (CW from above)
        bm.faces.new([bot_rim[i], bot_rim[j], top_rim[j], top_rim[i]])  # side wall


def _circle_ring_slab(bm, r_inner, r_outer, z0, z1, sides):
    """Circular annular slab (parapet, prayer lines)."""
    angles  = [2 * math.pi * i / sides for i in range(sides)]
    bot_in  = [bm.verts.new((r_inner * math.cos(a), r_inner * math.sin(a), z0)) for a in angles]
    bot_out = [bm.verts.new((r_outer * math.cos(a), r_outer * math.sin(a), z0)) for a in angles]
    top_in  = [bm.verts.new((r_inner * math.cos(a), r_inner * math.sin(a), z1)) for a in angles]
    top_out = [bm.verts.new((r_outer * math.cos(a), r_outer * math.sin(a), z1)) for a in angles]
    bm.verts.ensure_lookup_table()
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new([top_in[i],  top_in[j],  top_out[j], top_out[i]])
        bm.faces.new([bot_out[i], bot_out[j],  bot_in[j],  bot_in[i]])
        bm.faces.new([bot_out[i], bot_out[j], top_out[j], top_out[i]])
        bm.faces.new([bot_in[j],  bot_in[i],  top_in[i],  top_in[j]])


def build(collection=None):
    M  = P.MATAF
    collection = collection or C.reset_collection(COLLECTION)

    r_outer = M["INNER_CLEAR"] + M["RING_WIDTH"]   # 47 m
    levels  = M["LEVELS"]      # 1
    fh      = M["FLOOR_H"]     # 6 m
    par_h   = M["PARAPET_H"]   # 1.1 m
    slab_t  = M["SLAB_T"]      # 0.3 m
    sides   = M["SEGS"]        # 32

    # ── Floor slab: SOLID DISK per level ─────────────────────────────────────
    for lvl in range(levels):
        z0 = lvl * fh
        z1 = z0 + slab_t

        bm = bmesh.new()
        _solid_disk(bm, r_outer, z0, z1, sides)
        C.bm_to_object(bm, f"RUH_MATAF_SLAB_L{lvl}_VIS", collection,
                       material_key=M["MATERIAL"])

        # Outer parapet rim
        bm = bmesh.new()
        _circle_ring_slab(bm, r_outer - 0.3, r_outer, z1, z1 + par_h, sides)
        C.bm_to_object(bm, f"RUH_MATAF_PARAPET_L{lvl}_VIS", collection,
                       material_key=M["MATERIAL"])

    # ── Prayer lines — concentric raised rings on top of ground slab ─────────
    # Ref: masjidilharam010038 — evenly spaced circles visible on Mataf surface
    pw = M["PRAYER_W"]   # 0.08 m wide
    ph = M["PRAYER_H"]   # 0.02 m raised above slab top
    z_top = slab_t       # top of ground slab
    for r_line in M["PRAYER_RADII"]:
        bm = bmesh.new()
        _circle_ring_slab(bm, r_line - pw / 2, r_line + pw / 2,
                          z_top, z_top + ph, sides)
        C.bm_to_object(bm, f"RUH_MATAF_PLINE_R{int(r_line):02d}_VIS", collection,
                       material_key=M["MATERIAL"])

    # ── Collision: solid disk per level ──────────────────────────────────────
    for lvl in range(levels):
        z0 = lvl * fh
        bm = bmesh.new()
        _solid_disk(bm, r_outer, z0, z0 + slab_t, sides)
        C.bm_to_object(bm, f"RUH_MATAF_COL_L{lvl}", collection)

    return collection.objects[0]


if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    fail = False
    for obj in coll.objects:
        status, _ = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
        if status == "FAIL":
            fail = True
    if fail:
        raise SystemExit(1)
