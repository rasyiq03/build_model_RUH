# components/comp_expansion_wings.py
# =============================================================================
# Komponen: Sayap Ekspansi Masjidil Haram (King Fahd Expansion Wings)
# Bangunan multi-lantai yang mengisi area antara ring utama (OUTER_POLY) dan
# batas luar kompleks (OUTLINE_OUTER). Mencakup sisi W, SW, N, dan S.
#
# Sisi TIMUR (Mas'a / Sa'i corridor) tidak dibangun — sudah ada di comp_masaa.
# Teknik: untuk vertex OUTLINE_OUTER yang membentuk sisi Mas'a (indeks _MASA_IDX),
# outer_eff di-geser ke 1mm di luar inner projection. Slab menjadi tak kasat mata
# di sisi Mas'a, tapi mesh tetap tertutup (watertight) sehingga lulus validate().
#
# Lantai: LEVELS = STRUCTURE.LEVELS = 4 × FLOOR_H = 6 m
# → z=0, 6, 12, 18 m (sejajar lantai ring dan kolom).
#
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_expansion_wings.py
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

COLLECTION = "EXPANSION_WINGS"
TRI_CAP    = P.EXPANSION_WINGS["TARGET_TRI"]

# Vertex OUTLINE_OUTER yang membentuk sisi Mas'a / dinding timur kompleks.
# Outer polygon di-collapse ke 1mm di luar inner agar tidak ada dinding nyata di sini.
# 16: E-upper (35,329)  — transisi ke Mas'a NW
# 17: Mas'a NW (63,328)
# 18: Mas'a N  (67,335)
# 19: Mas'a E-far (117,339)
# 20: SE (156,-57)  — dinding timur Mas'a turun ke selatan
# 21: SE-S (153,-75)
# 22: SE-S2 (148,-93)
_MASA_IDX = frozenset(range(16, 23))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _ray_poly_intersect(theta, poly):
    """Ray dari origin arah theta, kembalikan titik perpotongan pertama dengan poly."""
    dx, dy = math.cos(theta), math.sin(theta)
    best_t  = float("inf")
    best_pt = None
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        denom   = dx * ey - dy * ex
        if abs(denom) < 1e-8:
            continue
        t = (x1 * ey - y1 * ex) / denom
        s = (x1 * dy  - y1 * dx) / denom
        if t > 1e-8 and -1e-8 <= s <= 1.0 + 1e-8 and t < best_t:
            best_t  = t
            best_pt = (dx * t, dy * t)
    if best_pt:
        return best_pt
    r_avg = math.sqrt(sum(x * x + y * y for x, y in poly) / len(poly))
    return (dx * r_avg, dy * r_avg)


def _inner_for_outer(outer_pts, inner_poly):
    """Setiap titik outer di-project ke inner_poly via ray dari origin."""
    return [_ray_poly_intersect(math.atan2(y, x), inner_poly)
            for x, y in outer_pts]


def _polygon_pair_slab(bm, outer_pts, inner_pts, z0, z1):
    """Annular slab antara outer_pts dan inner_pts, dari z0 ke z1."""
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


def _outer_edge_wall(bm, outer_pts, thickness, z0, z1):
    """Parapet tipis di sepanjang outer edge (menyusut thickness ke arah origin)."""
    inner_pts = []
    for ox, oy in outer_pts:
        r = math.hypot(ox, oy)
        f = max(r - thickness, 0.01) / r
        inner_pts.append((ox * f, oy * f))
    _polygon_pair_slab(bm, outer_pts, inner_pts, z0, z1)


def _collapse_masa(outer, inner):
    """
    Untuk vertex Mas'a (indeks _MASA_IDX), geser outer ke 1mm di luar inner.
    Slab menjadi 1mm — tak kasat mata tapi mesh tetap watertight.
    """
    eff = list(outer)
    for i in _MASA_IDX:
        ix, iy = inner[i]
        r = max(math.hypot(ix, iy), 0.01)
        eff[i] = (ix + ix * 0.001 / r, iy + iy * 0.001 / r)
    return eff


# ---------------------------------------------------------------------------
# build()
# ---------------------------------------------------------------------------

def build(collection):
    EW  = P.EXPANSION_WINGS
    ST  = P.STRUCTURE

    outer = P.TRACE["OUTLINE_OUTER"]
    inner = _inner_for_outer(outer, ST["OUTER_POLY"])
    outer_eff = _collapse_masa(outer, inner)  # collapse Mas'a vertices

    fh     = ST["FLOOR_H"]    # 6 m
    sh     = ST["SLAB_H"]     # 0.5 m
    lvls   = EW["LEVELS"]     # 4 lantai — sejajar seluruh ring
    par_h  = EW["PARAPET_H"]
    rp_h   = EW["ROOF_PARAPET_H"]
    mat    = EW["MATERIAL"]

    for lvl in range(lvls):
        z0 = lvl * fh
        z1 = z0 + sh

        bm = bmesh.new()
        _polygon_pair_slab(bm, outer_eff, inner, z0, z1)
        C.bm_to_object(bm, f"RUH_EXP_SLAB_L{lvl}_VIS", collection, material_key=mat)

        bm = bmesh.new()
        _outer_edge_wall(bm, outer_eff, thickness=0.4, z0=z1, z1=z1 + par_h)
        C.bm_to_object(bm, f"RUH_EXP_PAR_L{lvl}_VIS", collection, material_key=mat)

    z_roof = lvls * fh   # = 24.0 m
    bm = bmesh.new()
    _polygon_pair_slab(bm, outer_eff, inner, z_roof, z_roof + 0.3)
    C.bm_to_object(bm, "RUH_EXP_ROOF_VIS", collection, material_key=mat)

    bm = bmesh.new()
    _outer_edge_wall(bm, outer_eff, thickness=0.5,
                     z0=z_roof + 0.3, z1=z_roof + 0.3 + rp_h)
    C.bm_to_object(bm, "RUH_EXP_ROOF_PAR_VIS", collection, material_key=mat)

    z_top = z_roof + 0.3 + rp_h
    bm = bmesh.new()
    _polygon_pair_slab(bm, outer_eff, inner, 0.0, z_top)
    C.bm_to_object(bm, "RUH_EXP_COL", collection)


if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    for obj in coll.objects:
        C.validate(obj, TRI_CAP)
