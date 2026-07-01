# components/comp_haram_structure.py
# =============================================================================
# Komponen: Dinding luar octagonal ring (sudut / boundary wall)
#
# Hanya membangun DINDING LUAR octagonal (mengikuti OUTER_POLY) — tanpa floor slab
# interior. Floor slab di luar ring sudah dibangun oleh comp_expansion_wings.
# Floor slab di dalam ring (antara OUTER_POLY dan Mataf) TIDAK dibangun;
# ruang itu diisi kolom (comp_columns) dan area mataf (comp_mataf).
#
# Dinding: OUTER_POLY outer face → OUTER_POLY - WALL_T inner face, z=0..24m
# Tinggi = STRUCTURE.LEVELS × FLOOR_H = 4 × 6 = 24 m (sejajar lantai ring dan wings).
#
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_haram_structure.py
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

COLLECTION = "STRUCTURE"
TRI_CAP    = P.STRUCTURE["TARGET_TRI"]

WALL_T = 1.2   # ketebalan dinding luar ring (m) — inward dari OUTER_POLY


def _annular_slab(bm, outer_pts, inner_pts, z0, z1):
    """Horizontal annular slab antara outer_pts dan inner_pts dari z0 ke z1."""
    n  = len(outer_pts)
    bo = [bm.verts.new((x, y, z0)) for x, y in outer_pts]
    bi = [bm.verts.new((x, y, z0)) for x, y in inner_pts]
    to = [bm.verts.new((x, y, z1)) for x, y in outer_pts]
    ti = [bm.verts.new((x, y, z1)) for x, y in inner_pts]
    bm.verts.ensure_lookup_table()
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ti[i], ti[j], to[j], to[i]])   # top
        bm.faces.new([bo[i], bo[j], bi[j], bi[i]])   # bottom
        bm.faces.new([bo[i], bo[j], to[j], to[i]])   # outer wall
        bm.faces.new([bi[j], bi[i], ti[i], ti[j]])   # inner wall


def _ring_wall(bm, outer_pts, thickness, z0, z1):
    """Dinding luar ring mengikuti outer_pts, mundur thickness ke arah origin."""
    n = len(outer_pts)
    inner_pts = []
    for ox, oy in outer_pts:
        r = math.hypot(ox, oy)
        f = max(r - thickness, 0.01) / r
        inner_pts.append((ox * f, oy * f))

    bo = [bm.verts.new((x, y, z0)) for x, y in outer_pts]
    bi = [bm.verts.new((x, y, z0)) for x, y in inner_pts]
    to = [bm.verts.new((x, y, z1)) for x, y in outer_pts]
    ti = [bm.verts.new((x, y, z1)) for x, y in inner_pts]
    bm.verts.ensure_lookup_table()

    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ti[i], ti[j], to[j], to[i]])   # top
        bm.faces.new([bo[i], bo[j], bi[j], bi[i]])   # bottom
        bm.faces.new([bo[i], bo[j], to[j], to[i]])   # outer face
        bm.faces.new([bi[j], bi[i], ti[i], ti[j]])   # inner face

    return inner_pts                                   # return untuk reuse


def build(collection=None):
    ST  = P.STRUCTURE
    M   = P.MATAF
    collection = collection or C.reset_collection(COLLECTION)

    outer_pts = ST["OUTER_POLY"]
    fh        = ST["FLOOR_H"]        # 6 m
    sh        = ST["SLAB_H"]         # 0.5 m
    levels    = ST["LEVELS"]         # 4
    z_top     = levels * fh          # 24 m
    mat       = ST["MATERIAL"]

    # --- Dinding luar ring (OUTER_POLY → OUTER_POLY - WALL_T, z=0..24m) ---
    bm = bmesh.new()
    wall_inner = _ring_wall(bm, outer_pts, WALL_T, z0=0.0, z1=z_top)
    C.bm_to_object(bm, "RUH_RING_WALL_VIS", collection, material_key=mat)

    # --- Lantai ring (dari dinding dalam ke tepi mataf) per lantai ---
    # Outer edge slab = wall_inner (OUTER_POLY shrunk by WALL_T)
    # Inner edge slab = circle at r=MATAF_R di sudut yang sama dengan wall_inner
    r_mataf = M["INNER_CLEAR"] + M["RING_WIDTH"]   # 47 m — tepi mataf
    ring_inner = []
    for ox, oy in wall_inner:
        theta = math.atan2(oy, ox)
        ring_inner.append((r_mataf * math.cos(theta), r_mataf * math.sin(theta)))

    for lvl in range(levels):
        z0 = lvl * fh
        z1 = z0 + sh
        bm = bmesh.new()
        _annular_slab(bm, wall_inner, ring_inner, z0, z1)
        C.bm_to_object(bm, f"RUH_RING_SLAB_L{lvl}_VIS", collection, material_key=mat)

    # --- Atap ring ---
    bm = bmesh.new()
    _annular_slab(bm, wall_inner, ring_inner, z_top, z_top + 0.3)
    C.bm_to_object(bm, "RUH_RING_ROOF_VIS", collection, material_key=mat)

    # --- Collision (satu blok penuh dinding + lantai + atap) ---
    bm = bmesh.new()
    _ring_wall(bm, outer_pts, WALL_T, z0=0.0, z1=z_top)
    C.bm_to_object(bm, "RUH_RING_WALL_COL", collection)

    return collection.objects[0]


if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    for obj in coll.objects:
        C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
