# components/comp_columns.py
# =============================================================================
# Komponen: Kolom Arcade Inner (Colonnade) Masjidil Haram
# Kolom oktagonal di inner face struktur ring (r=47 m), 4 level @ 6 m.
# Setiap level = satu mesh gabungan ~49 kolom (≈4700 tri ≤ TARGET_TRI=6000).
# Profil: base plinth (r=0.50) → shaft (r=0.35) → capital (r=0.50), h=6 m.
# Ref: interior/masjidalharam010016.jpg, masjidalharam010017.jpg
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_columns.py
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

COLLECTION = "COLUMNS"
TRI_CAP    = P.COLUMNS["TARGET_TRI"]

_N_SIDES = 8   # oktagonal

# Profil kolom (z relatif 0–6 m = 1 lantai).
# Bentuk: base plinth lebar → shaft ramping → capital lebar.
# Ref: 010016/010017 — kolom ramping marmer dengan ujung melebar sedikit.
_COL_PROFILE = [
    (0.50, 0.00),   # plinth: alas
    (0.50, 0.30),   # plinth: atas
    (0.35, 0.55),   # shaft: mulai (menyempit)
    (0.35, 5.45),   # shaft: puncak
    (0.50, 5.70),   # capital: mulai (melebar)
    (0.50, 6.00),   # capital: atas
]


def _revolve_profile(bm, cx, cy, profile, n_sides=_N_SIDES):
    """Solid of revolution dari profile [(r,z)...] ke titik (cx,cy).
    Dipanggil berulang pada bm yang sama — setiap panggilan menambah geometri kolom baru.
    """
    def ring(r, z):
        return [bm.verts.new((cx + r * math.cos(2 * math.pi * i / n_sides),
                               cy + r * math.sin(2 * math.pi * i / n_sides), z))
                for i in range(n_sides)]

    rings = []
    for r, z in profile:
        rings.append(ring(r, z) if r > 0.0 else bm.verts.new((cx, cy, z)))
    bm.verts.ensure_lookup_table()

    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        if isinstance(a, list) and isinstance(b, list):
            for k in range(n_sides):
                l = (k + 1) % n_sides
                bm.faces.new([a[k], b[k], b[l], a[l]])
        elif isinstance(a, list):   # b = apex
            for k in range(n_sides):
                bm.faces.new([a[k], b, a[(k + 1) % n_sides]])
        else:                        # a = pole
            for k in range(n_sides):
                bm.faces.new([a, b[(k + 1) % n_sides], b[k]])

    # bottom cap
    if isinstance(rings[0], list):
        ctr = bm.verts.new((cx, cy, profile[0][1]))
        bm.verts.ensure_lookup_table()
        for k in range(n_sides):
            bm.faces.new([ctr, rings[0][k], rings[0][(k + 1) % n_sides]])

    # top cap
    if isinstance(rings[-1], list):
        ctr = bm.verts.new((cx, cy, profile[-1][1]))
        bm.verts.ensure_lookup_table()
        for k in range(n_sides):
            bm.faces.new([ctr, rings[-1][(k + 1) % n_sides], rings[-1][k]])


def _poly_offset_inward(pts, dist):
    """Geser setiap titik polygon menuju origin sebesar dist meter."""
    result = []
    for ox, oy in pts:
        r = math.hypot(ox, oy)
        f = max(r - dist, 0.01) / r
        result.append((ox * f, oy * f))
    return result


def _sample_along_poly(pts, spacing):
    """Sample titik sepanjang polygon dengan jarak tetap spacing."""
    positions = []
    n = len(pts)
    carry = 0.0
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        seg_len = math.hypot(dx, dy)
        if seg_len < 1e-6:
            continue
        ux, uy = dx / seg_len, dy / seg_len
        d = carry
        while d < seg_len:
            positions.append((ax + ux * d, ay + uy * d))
            d += spacing
        carry = d - seg_len
    return positions


def build(collection):
    ST  = P.STRUCTURE
    M   = P.MATAF
    COL = P.COLUMNS

    fh      = ST["FLOOR_H"]                            # 6 m
    levels  = ST["LEVELS"]                             # 4
    spacing = COL["SPACING"]                           # 6 m pusat-ke-pusat
    mat     = COL["MATERIAL"]

    # --- Inner colonnade: kolom di tepi mataf (r=47m), susunan lingkaran ---
    r_col  = M["INNER_CLEAR"] + M["RING_WIDTH"]        # 47 m
    θ_step = spacing / r_col                           # ≈ 0.1277 rad
    n_cols = int(2 * math.pi / θ_step)                 # ≈ 49 kolom

    for lvl in range(levels):
        z0      = lvl * fh
        profile = [(r, z + z0) for r, z in _COL_PROFILE]
        bm      = bmesh.new()
        for k in range(n_cols):
            θ  = k * θ_step
            _revolve_profile(bm, r_col * math.cos(θ), r_col * math.sin(θ), profile)
        C.bm_to_object(bm, f"RUH_COLUMNS_L{lvl}_VIS", collection, material_key=mat)

    # --- Outer colonnade: kolom di inner face dinding luar (OUTER_POLY), susunan poligon ---
    total_offset = COL["WALL_T"] + COL["COL_OFFSET"]   # 1.2 + 1.5 = 2.7 m
    col_ring     = _poly_offset_inward(ST["OUTER_POLY"], total_offset)
    positions    = _sample_along_poly(col_ring, spacing)

    for lvl in range(levels):
        z0      = lvl * fh
        profile = [(r, z + z0) for r, z in _COL_PROFILE]
        bm      = bmesh.new()
        for cx, cy in positions:
            _revolve_profile(bm, cx, cy, profile)
        C.bm_to_object(bm, f"RUH_COLUMNS_OUTER_L{lvl}_VIS", collection, material_key=mat)


if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    for obj in coll.objects:
        C.validate(obj, TRI_CAP)
