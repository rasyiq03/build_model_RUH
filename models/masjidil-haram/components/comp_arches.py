# components/comp_arches.py
# =============================================================================
# Komponen: Lengkung Arcade (Arches) Masjidil Haram
# Lengkung pointed di antara kolom inner face (r=47 m), 4 level.
# Setiap bay = panel spandrel melengkung: dari titik spring (z=4 m) ke keystone
# (z=5.7 m) lalu datar ke z=6 m, depth=0.5 m ke dalam dinding.
# Satu mesh per level, ≈49 arch × 64 tri = ≈3136 tri per level.
# Ref: interior/masjidalharam010016.jpg, masjidalharam010017.jpg
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_arches.py
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

COLLECTION = "COLUMNS"          # arch + columns membentuk satu colonnade
TRI_CAP    = P.ARCHES["TARGET_TRI"]


# ---------------------------------------------------------------------------
# Helper untuk outer arches (polygon colonnade di OUTER_POLY)
# ---------------------------------------------------------------------------

def _poly_offset_inward(pts, dist):
    result = []
    for ox, oy in pts:
        r = math.hypot(ox, oy)
        f = max(r - dist, 0.01) / r
        result.append((ox * f, oy * f))
    return result


def _sample_along_poly(pts, spacing):
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


def _compute_bisectors(positions):
    """Miter bisector inward di setiap posisi kolom (untuk poligon CW)."""
    n = len(positions)
    bisectors = []
    for i in range(n):
        p0 = positions[(i - 1) % n]
        p1 = positions[i]
        p2 = positions[(i + 1) % n]
        dx1, dy1 = p1[0] - p0[0], p1[1] - p0[1]
        sp1 = math.hypot(dx1, dy1)
        dx2, dy2 = p2[0] - p1[0], p2[1] - p1[1]
        sp2 = math.hypot(dx2, dy2)
        n1 = (dy1 / sp1, -dx1 / sp1) if sp1 > 1e-6 else (0.0, 0.0)
        n2 = (dy2 / sp2, -dx2 / sp2) if sp2 > 1e-6 else (0.0, 0.0)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        if bl > 1e-6:
            cos_half = max(n1[0] * (bx / bl) + n1[1] * (by / bl), 0.15)
            bx, by = (bx / bl) / cos_half, (by / bl) / cos_half
        else:
            bx, by = n1
        bisectors.append((bx, by))
    return bisectors


def _add_arch_bay_poly(bm, p0, p1, b0, b1, z0, z_spr, z_key, z_top, depth, n_seg):
    """Bay arch antara dua posisi kolom p0→p1 dengan miter bisectors b0, b1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    if math.hypot(dx, dy) < 1e-6:
        return
    fr_b, fr_t, bk_b, bk_t = [], [], [], []
    for i in range(n_seg + 1):
        t   = i / n_seg
        ax  = p0[0] + t * dx;  ay  = p0[1] + t * dy
        bxi = b0[0] + t * (b1[0] - b0[0])
        byi = b0[1] + t * (b1[1] - b0[1])
        az  = z0 + z_spr + (z_key - z_spr) * math.sin(t * math.pi)
        tz  = z0 + z_top
        fr_b.append(bm.verts.new((ax,              ay,              az)))
        fr_t.append(bm.verts.new((ax,              ay,              tz)))
        bk_b.append(bm.verts.new((ax + bxi * depth, ay + byi * depth, az)))
        bk_t.append(bm.verts.new((ax + bxi * depth, ay + byi * depth, tz)))
    bm.verts.ensure_lookup_table()
    for i in range(n_seg):
        j = i + 1
        bm.faces.new([fr_b[i], fr_t[i], fr_t[j], fr_b[j]])
        bm.faces.new([bk_b[i], bk_b[j], bk_t[j], bk_t[i]])
        bm.faces.new([fr_t[i], bk_t[i], bk_t[j], fr_t[j]])
        bm.faces.new([fr_b[j], bk_b[j], bk_b[i], fr_b[i]])


def _add_arch_bay(bm, θ_k, θ_step, r_in, r_out, z0, z_spr, z_key, z_top, n_seg):
    """Tambahkan satu spandrel arch bay ke bm yang sudah ada.

    Panel mengisi area antara dua kolom dari z_spr ke z_top, dengan bagian
    bawah mengikuti kurva arch (sine). TANPA cap kiri/kanan — tepi terbuka
    akan ditutup oleh remove_doubles setelah semua bay ditambahkan.
    """
    fr_b, fr_t, bk_b, bk_t = [], [], [], []

    for i in range(n_seg + 1):
        t   = i / n_seg
        θ   = θ_k + t * θ_step
        c   = math.cos(θ)
        s   = math.sin(θ)
        az  = z0 + z_spr + (z_key - z_spr) * math.sin(t * math.pi)
        tz  = z0 + z_top

        fr_b.append(bm.verts.new((r_in  * c, r_in  * s, az)))
        fr_t.append(bm.verts.new((r_in  * c, r_in  * s, tz)))
        bk_b.append(bm.verts.new((r_out * c, r_out * s, az)))
        bk_t.append(bm.verts.new((r_out * c, r_out * s, tz)))

    bm.verts.ensure_lookup_table()

    for i in range(n_seg):
        j = i + 1
        bm.faces.new([fr_b[i], fr_t[i], fr_t[j], fr_b[j]])        # depan
        bm.faces.new([bk_b[i], bk_b[j], bk_t[j], bk_t[i]])        # belakang
        bm.faces.new([fr_t[i], bk_t[i], bk_t[j], fr_t[j]])        # atas
        bm.faces.new([fr_b[j], bk_b[j], bk_b[i], fr_b[i]])        # soffit


def build(collection):
    ST  = P.STRUCTURE
    M   = P.MATAF
    AR  = P.ARCHES
    COL = P.COLUMNS

    fh      = ST["FLOOR_H"]
    levels  = ST["LEVELS"]
    z_spr   = AR["Z_SPRING"]
    z_key   = AR["Z_KEY"]
    n_seg   = AR["N_SEG"]
    depth   = AR["DEPTH"]
    mat     = AR["MATERIAL"]
    spacing = COL["SPACING"]   # 6 m

    # --- Inner arches: melingkar di r=47m ---
    r_col  = M["INNER_CLEAR"] + M["RING_WIDTH"]    # 47 m
    n_cols = int(2 * math.pi / (spacing / r_col))  # ≈ 49
    θ_step = 2 * math.pi / n_cols
    r_in   = r_col
    r_out  = r_col + depth

    for lvl in range(levels):
        z0 = lvl * fh
        bm = bmesh.new()
        for k in range(n_cols):
            _add_arch_bay(bm, k * θ_step, θ_step,
                          r_in, r_out, z0, z_spr, z_key, fh, n_seg)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        C.bm_to_object(bm, f"RUH_ARCHES_L{lvl}_VIS", collection, material_key=mat)

    # --- Outer arches: mengikuti OUTER_POLY inner face ---
    total_offset = COL["WALL_T"] + COL["COL_OFFSET"]   # 2.7 m
    col_ring     = _poly_offset_inward(ST["OUTER_POLY"], total_offset)
    positions    = _sample_along_poly(col_ring, spacing)
    bisectors    = _compute_bisectors(positions)
    n_pos        = len(positions)

    for lvl in range(levels):
        z0 = lvl * fh
        bm = bmesh.new()
        for k in range(n_pos):
            k1 = (k + 1) % n_pos
            _add_arch_bay_poly(bm, positions[k], positions[k1],
                               bisectors[k], bisectors[k1],
                               z0, z_spr, z_key, fh, depth, n_seg)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.005)
        C.bm_to_object(bm, f"RUH_ARCHES_OUTER_L{lvl}_VIS", collection, material_key=mat)


if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    for obj in coll.objects:
        C.validate(obj, TRI_CAP)
