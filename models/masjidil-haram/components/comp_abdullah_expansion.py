# components/comp_abdullah_expansion.py
# =============================================================================
# Komponen: Perluasan Raja Abdullah / King Abdullah Expansion (Ekspansi Saudi Ketiga)
# Bangunan multi-lantai di sisi UTARA-BARAT kompleks (Shamiya side).
#
# Shape: OPEN ARC slab — outer = POLY_OUTER (13 titik),
#   inner = irisan OUTER_POLY yang tepat (sudut-sudut aktual, tidak ada proyeksi)
#   sehingga TIDAK ADA face penutup yang memotong interior octagonal ring.
#
# SUMBER:  6 lantai (Saudipedia), area ~300rb m² (Wikipedia), sisi utara (SPA.gov.sa)
# POLYGON: ref-clarify annotation masjidilharam_satelit.png (2026-06-27)
#          Kalibrasi Kaaba(518,551)→(0,0), Marwa(603,311)→(105.4,295.9), ~1.237 m/px
#
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_abdullah_expansion.py
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

COLLECTION = "ABDULLAH_EXPANSION"
TRI_CAP    = P.ABDULLAH_EXPANSION["TARGET_TRI"]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _ray_poly_intersect(theta, poly):
    """Ray dari origin arah theta, kembalikan titik perpotongan dengan poly."""
    dx, dy = math.cos(theta), math.sin(theta)
    best_t, best_pt = float("inf"), None
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        ex, ey = x2 - x1, y2 - y1
        denom = dx * ey - dy * ex
        if abs(denom) < 1e-8:
            continue
        t = (x1 * ey - y1 * ex) / denom
        s = (x1 * dy - y1 * dx) / denom
        if t > 1e-8 and -1e-8 <= s <= 1.0 + 1e-8 and t < best_t:
            best_t, best_pt = t, (dx * t, dy * t)
    if best_pt:
        return best_pt
    r_avg = math.sqrt(sum(x * x + y * y for x, y in poly) / len(poly))
    return (dx * r_avg, dy * r_avg)


def _split_poly_at_angle(pts, theta):
    """
    Cari perpotongan ray dari origin (sudut theta) dengan open polyline pts.
    Returns (idx, point): intersection pada segment pts[idx]→pts[idx+1].
    """
    dx, dy = math.cos(theta), math.sin(theta)
    best_t, best_i, best_pt = float("inf"), -1, None
    for i in range(len(pts) - 1):
        x1, y1 = pts[i];  x2, y2 = pts[i + 1]
        ex, ey = x2 - x1, y2 - y1
        denom = dx * ey - dy * ex
        if abs(denom) < 1e-8:
            continue
        t = (x1 * ey - y1 * ex) / denom
        s = (x1 * dy - y1 * dx) / denom
        if t > 1e-8 and -1e-8 <= s <= 1.0 + 1e-8 and t < best_t:
            s = max(0.0, min(1.0, s))
            best_t, best_i = t, i
            best_pt = (x1 + s * ex, y1 + s * ey)
    return best_i, best_pt


def _walk_forward(pts, idx, dist):
    """Maju dist m dari pts[idx]; returns (first_vtx_after, point).
    first_vtx_after = indeks vertex pts pertama yang letaknya SETELAH point,
    sehingga pts[first_vtx_after:end] memberikan interior vertices yang benar.
    """
    remaining = dist
    for i in range(idx, len(pts) - 1):
        x0, y0 = pts[i];  x1, y1 = pts[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        if remaining <= seg:
            t = remaining / seg
            return i + 1, (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
        remaining -= seg
    return len(pts) - 1, pts[-1]


def _walk_backward(pts, idx, dist):
    """Mundur dist m dari pts[idx]; returns (last_vtx_before, point).
    last_vtx_before = indeks vertex pts terakhir yang letaknya SEBELUM point,
    sehingga pts[start:last_vtx_before+1] memberikan interior vertices yang benar.
    """
    remaining = dist
    for i in range(idx, 0, -1):
        x1, y1 = pts[i];  x0, y0 = pts[i - 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        if remaining <= seg:
            t = remaining / seg
            return i - 1, (x1 - t * (x1 - x0), y1 - t * (y1 - y0))
        remaining -= seg
    return 0, pts[0]


def _inner_arc_from_outer_poly(outer_pts, outer_poly):
    """
    Build inner boundary arc yang tepat mengikuti OUTER_POLY corners.
    outer_pts[0]  = titik awal outer arc (P0, barat)
    outer_pts[-1] = titik akhir outer arc (P12, utara/timur)

    Returns: list titik inner dari awal ke akhir, berisi:
      - proyeksi outer_pts[0] ke OUTER_POLY
      - semua OUTER_POLY corners dalam rentang sudut
      - proyeksi outer_pts[-1] ke OUTER_POLY
    """
    theta_start = math.atan2(outer_pts[0][1],   outer_pts[0][0])    # P0
    theta_end   = math.atan2(outer_pts[-1][1],  outer_pts[-1][0])   # P12

    p_start = _ray_poly_intersect(theta_start, outer_poly)
    p_end   = _ray_poly_intersect(theta_end,   outer_poly)

    # OUTER_POLY corners dalam rentang sudut [theta_end .. theta_start]
    corners = []
    for px, py in outer_poly:
        theta = math.atan2(py, px)
        if theta_end <= theta <= theta_start:
            corners.append((theta, (px, py)))
    corners.sort(key=lambda t: -t[0])   # descending angle = awal→akhir (CW)

    inner = [p_start]
    for _, pt in corners:
        last = inner[-1]
        if math.hypot(pt[0] - last[0], pt[1] - last[1]) > 0.5:
            inner.append(pt)

    if math.hypot(p_end[0] - inner[-1][0], p_end[1] - inner[-1][1]) > 0.5:
        inner.append(p_end)

    return inner


def _open_arc_slab(bm, outer_pts, inner_pts, z0, z1):
    """
    Open arc annular slab — TIDAK menutup melingkar (tidak ada face penutup).
    outer_pts dan inner_pts adalah open arcs dari titik awal ke akhir.
    End caps menutup kedua ujung slab.
    top/bottom face di-fill via triangle_fill.
    """
    n_o = len(outer_pts)
    n_i = len(inner_pts)

    bo = [bm.verts.new((x, y, z0)) for x, y in outer_pts]
    bi = [bm.verts.new((x, y, z0)) for x, y in inner_pts]
    to = [bm.verts.new((x, y, z1)) for x, y in outer_pts]
    ti = [bm.verts.new((x, y, z1)) for x, y in inner_pts]
    bm.verts.ensure_lookup_table()

    # Outer wall — n_o-1 quads, OPEN (tidak ada wrap-around ke vertex 0)
    for i in range(n_o - 1):
        bm.faces.new([bo[i], bo[i + 1], to[i + 1], to[i]])

    # Inner wall — n_i-1 quads, OPEN, winding terbalik agar normal keluar
    for i in range(n_i - 1):
        bm.faces.new([bi[i + 1], bi[i], ti[i], ti[i + 1]])

    # End cap start: outer[0] → inner[0]
    bm.faces.new([bo[0], to[0], ti[0], bi[0]])
    # End cap end: outer[-1] → inner[-1]
    bm.faces.new([bo[-1], bi[-1], ti[-1], to[-1]])

    bm.edges.ensure_lookup_table()

    # Top face: kumpulkan semua boundary edge di z=z1 lalu triangle_fill
    def _get_edge(a, b):
        return bm.edges.get([a, b])

    top_edges = []
    for i in range(n_o - 1):
        e = _get_edge(to[i], to[i + 1])
        if e:
            top_edges.append(e)
    for i in range(n_i - 1):
        e = _get_edge(ti[i], ti[i + 1])
        if e:
            top_edges.append(e)
    e = _get_edge(to[0], ti[0])
    if e: top_edges.append(e)
    e = _get_edge(to[-1], ti[-1])
    if e: top_edges.append(e)

    if top_edges:
        bmesh.ops.triangle_fill(bm, use_beauty=True, edges=top_edges)

    bm.edges.ensure_lookup_table()

    # Bottom face: kumpulkan boundary edge di z=z0 lalu triangle_fill
    bot_edges = []
    for i in range(n_o - 1):
        e = _get_edge(bo[i], bo[i + 1])
        if e:
            bot_edges.append(e)
    for i in range(n_i - 1):
        e = _get_edge(bi[i], bi[i + 1])
        if e:
            bot_edges.append(e)
    e = _get_edge(bo[0], bi[0])
    if e: bot_edges.append(e)
    e = _get_edge(bo[-1], bi[-1])
    if e: bot_edges.append(e)

    if bot_edges:
        bmesh.ops.triangle_fill(bm, use_beauty=True, edges=bot_edges)


def _outer_edge_wall(bm, outer_pts, thickness, z0, z1):
    """Parapet tipis open arc di sepanjang outer edge, menyusut ke arah origin."""
    inner_pts = []
    for ox, oy in outer_pts:
        r = math.hypot(ox, oy)
        f = max(r - thickness, 0.01) / r
        inner_pts.append((ox * f, oy * f))
    _open_arc_slab(bm, outer_pts, inner_pts, z0, z1)


def _build_minaret(bm, cx, cy, ae):
    """Menara segi-N meruncing: shaft lurus + cap kerucut di puncak.
    Dimulai dari z=0 (tanah) hingga MINARET_H.
    """
    n     = ae["MINARET_N"]
    h     = ae["MINARET_H"]
    r0    = ae["MINARET_R_BASE"]
    r1    = ae["MINARET_R_TOP"]
    cap_h = ae["MINARET_CAP_H"]

    zs = [0.0,      h - cap_h,  h]
    rs = [r0,       r1,         r1 * 0.12]

    rings = []
    for z, r in zip(zs, rs):
        ring = [bm.verts.new((cx + r * math.cos(2 * math.pi * k / n),
                               cy + r * math.sin(2 * math.pi * k / n), z))
                for k in range(n)]
        rings.append(ring)
    bm.verts.ensure_lookup_table()

    # Bottom disk (normal ke bawah = -Z)
    bc = bm.verts.new((cx, cy, 0.0))
    bm.verts.ensure_lookup_table()
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new([bc, rings[0][j], rings[0][k]])

    # Side quads antar ring (normal keluar)
    for ri in range(len(rings) - 1):
        bot, top_r = rings[ri], rings[ri + 1]
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([bot[k], bot[j], top_r[j], top_r[k]])

    # Top tip (normal ke atas = +Z)
    tc = bm.verts.new((cx, cy, h))
    bm.verts.ensure_lookup_table()
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new([rings[-1][j], rings[-1][k], tc])


# ---------------------------------------------------------------------------
# build()
# ---------------------------------------------------------------------------

def build(collection):
    AE         = P.ABDULLAH_EXPANSION
    EW         = P.EXPANSION_WINGS
    ST         = P.STRUCTURE
    full       = AE["POLY_OUTER"]        # 13 titik P0..P12
    inner_poly = ST["OUTER_POLY"]
    half       = AE["CORR_W"] / 2.0     # setengah lebar saluran = 10 m

    # --- 4 sudut separator dari anotasi satelit (masjidilharam_satelit__notes.json 2026-06-28) ---
    # Kalibrasi: Kaaba px(518,551)=local(0,0), skala 1.237 m/px.
    # Pin1 SW  px(221,427) → local(-367, 153) → 157.4°  (antara P0-P1)
    # Pin2 A/B px(287,329) → local(-286, 275) → 136.3°  (antara P3-P4)
    # Pin3 B/C px(421,227) → local(-120, 401) → 106.7°  (antara P6-P7)
    # Pin4 NE  px(541,210) → local( +28, 422) →  86.1°  (antara P10-P11)
    THETA_1 = math.radians(157.4)
    THETA_2 = math.radians(136.3)
    THETA_3 = math.radians(106.7)
    THETA_4 = math.radians( 86.1)

    i1, pt1 = _split_poly_at_angle(full, THETA_1)   # antara P0-P1
    i2, pt2 = _split_poly_at_angle(full, THETA_2)   # antara P3-P4
    i3, pt3 = _split_poly_at_angle(full, THETA_3)   # antara P6-P7
    i4, pt4 = _split_poly_at_angle(full, THETA_4)   # antara P10-P11

    # Sisipkan ke polyline sehingga _point_before/_point_after bisa bekerja
    full_ext = (full[:i1+1] + [pt1] +
                full[i1+1:i2+1] + [pt2] +
                full[i2+1:i3+1] + [pt3] +
                full[i3+1:i4+1] + [pt4] +
                full[i4+1:])
    j1, j2 = i1 + 1, i2 + 2   # indeks pt1, pt2 di full_ext
    j3, j4 = i3 + 3, i4 + 4   # indeks pt3, pt4 di full_ext

    # --- Outer arcs (3 section, masing-masing berakhir 'half' m dari corridor center) ---
    # _walk_forward/_walk_backward mengembalikan first_vtx_after/last_vtx_before,
    # sehingga interior slice full_ext[sa:ea+1] selalu SETELAH start dan SEBELUM end.
    # (Penting: menghindari backward-step ketika pt1 ≈ P1 dan P1 masih ada di full_ext.)
    sa, a_start = _walk_forward(full_ext,  j1, half)
    ea, a_end   = _walk_backward(full_ext, j2, half)
    outer_A = [a_start] + full_ext[sa : ea + 1] + [a_end]

    sb, b_start = _walk_forward(full_ext,  j2, half)
    eb, b_end   = _walk_backward(full_ext, j3, half)
    outer_B = [b_start] + full_ext[sb : eb + 1] + [b_end]

    sc, c_start = _walk_forward(full_ext,  j3, half)
    ec, c_end   = _walk_backward(full_ext, j4, half)
    outer_C = [c_start] + full_ext[sc : ec + 1] + [c_end]

    # --- Inner boundaries mengikuti OUTER_POLY corners persis ---
    inner_A = _inner_arc_from_outer_poly(outer_A, inner_poly)
    inner_B = _inner_arc_from_outer_poly(outer_B, inner_poly)
    inner_C = _inner_arc_from_outer_poly(outer_C, inner_poly)

    fh     = AE["FLOOR_H"]
    st     = AE["SLAB_T"]
    lvls   = AE["LEVELS"]
    mat    = AE["MATERIAL"]
    base_z = EW["LEVELS"] * ST["FLOOR_H"]   # 24 m

    sections = [
        ("A", outer_A, inner_A),
        ("B", outer_B, inner_B),
        ("C", outer_C, inner_C),
    ]

    for sec, outer, inner in sections:
        for lvl in range(lvls):
            z0 = base_z + lvl * fh
            z1 = z0 + st

            bm = bmesh.new()
            _open_arc_slab(bm, outer, inner, z0, z1)
            C.bm_to_object(bm, f"RUH_ABD_{sec}_SLAB_L{lvl}_VIS",
                           collection, material_key=mat)

            bm = bmesh.new()
            _outer_edge_wall(bm, outer, thickness=0.4,
                             z0=z1, z1=z1 + AE["PARAPET_H"])
            C.bm_to_object(bm, f"RUH_ABD_{sec}_PAR_L{lvl}_VIS",
                           collection, material_key=mat)

        z_roof = base_z + lvls * fh
        bm = bmesh.new()
        _open_arc_slab(bm, outer, inner, z_roof, z_roof + 0.4)
        C.bm_to_object(bm, f"RUH_ABD_{sec}_ROOF_VIS",
                       collection, material_key=mat)

        bm = bmesh.new()
        _outer_edge_wall(bm, outer, thickness=0.5,
                         z0=z_roof + 0.4,
                         z1=z_roof + 0.4 + AE["ROOF_PARAPET_H"])
        C.bm_to_object(bm, f"RUH_ABD_{sec}_ROOF_PAR_VIS",
                       collection, material_key=mat)

        z_top = z_roof + 0.4 + AE["ROOF_PARAPET_H"]
        bm = bmesh.new()
        _open_arc_slab(bm, outer, inner, base_z, z_top)
        C.bm_to_object(bm, f"RUH_ABD_{sec}_COL", collection)

    # --- Menara Bab Abdullah (ke-12 & ke-13) ---
    # Posisi dari ref-clarify masjdiilharam_satelit3 (2026-06-28), tinggi 135 m (SPA.gov.sa)
    mn_mat = AE["MINARET_MATERIAL"]
    for idx, mn in enumerate(AE["MINARETS"]):
        bm = bmesh.new()
        _build_minaret(bm, mn["cx"], mn["cy"], AE)
        C.bm_to_object(bm, f"RUH_ABD_MINARET_{idx+12}_VIS",
                       collection, material_key=mn_mat)


if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    for obj in coll.objects:
        C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
