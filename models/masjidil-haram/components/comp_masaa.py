# components/comp_masaa.py
# =============================================================================
# Komponen: Mas'a (Koridor Sa'i Safa–Marwa)
# Koridor 3-lantai ~375 m panjang, 40 m lebar, sejajar sumbu OSM Safa→Marwa.
# Bagian:
#   - Lantai (slab) per level  : LEVELS=3 kotak marmer (bisa dilalui pemain)
#   - Parapet per lantai atas  : pagar pembatas di tepi L1 dan L2
#   - Zona hijau               : penanda lari Sa'i (green material, tengah koridor)
#   - Bukit Safa               : granit di ujung selatan
#   - Bukit Marwa              : marmer di ujung utara
#   - Connector                : jembatan 4-lantai di celah SE struktur → pintu Safa
#   - Pavilion dome (×2)       : tugu berkubah terracotta di ujung Safa & Marwa
# Ref: 010019 (connector + posisi dome), 010027 (detail pavilion dome)
# Koordinat: origin = pusat Ka'bah, +X = timur, +Y = utara.
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

COLLECTION = "MASAA"
TRI_CAP    = P.MASA["TARGET_TRI"]

# Pavilion dome dimensions (Ref: masjidilharam010027)
_DOME_PLAT_R  = 7.0   # jari-jari platform oktagonal alas pavilion (m)
_DOME_PLAT_H  = 0.40  # tinggi platform (m)
_DOME_DRUM_R  = 5.5   # jari-jari drum oktagonal (m)
_DOME_DRUM_H  = 3.0   # tinggi drum (m)
_DOME_R       = 5.0   # jari-jari kubah hemispherical (m)
_DOME_FINIAL_H= 1.6   # tinggi finial emas di atas kubah (m)
_DOME_N_LAT   = 8     # segmen lintang kubah
_DOME_NSIDES  = 16    # penampang drum/kubah

# Trim selatan slab Mas'a — slab dipotong di y≈-50, yaitu titik konvergensi antara
# dinding barat Mas'a (x≈114.6) dan sisi SE ring (129,2)→(109,-70) (x≈114.6).
# Di atas y=-50: ring SE berada di sebelah timur dinding barat Mas'a → slab harus
# berhenti di sini agar tidak menembus footprint ring.
# VEST (vestibule kotak 15m × 40m) mengisi y≈-50 s/d -65 sebagai sambungan ke ring,
# CONN_S (pentagon) mengisi strip barat y≈-65 s/d -85.
# _HL_S: sudut barat-selatan slab (u=-hl_s, v=+hw) di y=-50 →
#   y_sw = cy + sin_a*(-hl_s) + cos_a*hw = -50 → hl_s ≈ 158.1 m
_HL_S      = 158.1   # south half-length (trim) — titik konvergensi ring SE di y≈-50
_VEST_DEPTH = 15.0   # kedalaman vestibule selatan (m)
_HL_SOUTH  = 192.0   # total south half-length: ujung barat body ≈ CONN_S SE (117.3,-83)

# Connector SELATAN — 5 titik pentagon dekat Safa (Ref: 010019 pin2, 010048 pin3)
#   Sisi TIMUR (NE→SE)  : naik dari (117.3,-83) ke sudut barat Mas'a (114.55,-50),
#     melewati (115.8,-65) secara kollinear → tersambung langsung ke ujung slab Mas'a.
#   Sisi BARAT (NW2→SW) : mengikuti 2 segmen OUTER_POLY SE face + 2 m gap.
# NE = (114.55,-50.01) = sudut SW slab Mas'a (v=+20, u=-_HL_S) → tidak ada celah.
# 5 titik CCW dari atas (+Z), signed area ≈ +283 m².
_CONN_PTS = [
    ( 85.1,  -84.8),  # SW  — sisi ring SE→S + 2 m gap, dekat Safa
    (117.3,  -83.0),  # SE  — dinding barat Mas'a dekat Safa
    (114.55, -50.01), # NE  — sudut SW slab Mas'a (y≈-50), sambung langsung ke ujung slab
    (112.3,  -65.5),  # N   — sisi ring NE→SE + 2 m gap, y≈-65.5
    (110.6,  -71.3),  # NW  — sudut ring (109,-70) + 2 m gap (rata sudut)
]

# Connector UTARA — 4 titik quadrilateral sisi E ring ke dinding barat Mas'a
# (Ref: 010019 pin1, 010048 pin2 — "tidak tegak lurus garis singgung lingkaran")
# Ring E face: (84,97)→(129,2), outward normal=(0.9037, 0.4281).
# Gap ditutup antara y≈50 (titik persilangan) dan y=97 (pojok ring NE→E).
# 4 titik CCW dari atas (+Z), signed area ≈ +329 m².
_CONN_N_PTS = [
    (106.1,  50.3),  # SW  — dinding barat Mas'a di titik persilangan y≈50
    (102.2,  97.0),  # NW  — dinding barat Mas'a di y=97
    ( 85.8,  97.9),  # NE  — sisi E ring (84,97) + 2 m gap
    (107.9,  51.2),  # SE  — sisi E ring di titik persilangan + 2 m gap
]


def _box(bm, x0, x1, y0, y1, z0, z1):
    """Kotak watertight sumbu-sejajar — 6 quad (12 tri)."""
    v = [bm.verts.new(co) for co in [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]]
    bm.verts.ensure_lookup_table()
    bm.faces.new([v[0], v[3], v[2], v[1]])
    bm.faces.new([v[4], v[5], v[6], v[7]])
    bm.faces.new([v[0], v[1], v[5], v[4]])
    bm.faces.new([v[2], v[3], v[7], v[6]])
    bm.faces.new([v[0], v[4], v[7], v[3]])
    bm.faces.new([v[1], v[2], v[6], v[5]])


def _curved_strip(bm, pts2d, width, z0, z1, n_sub=10):
    """Ribbon mesh watertight sepanjang path 2D pts2d.
    n_sub = subdivisi per segmen (membuat kurva tampak halus).
    Lebar = width m, tinggi = z1-z0 m.
    """
    # Subdivide path for smoothness
    path = []
    for i in range(len(pts2d) - 1):
        for j in range(n_sub):
            t = j / n_sub
            path.append((
                pts2d[i][0] + (pts2d[i+1][0] - pts2d[i][0]) * t,
                pts2d[i][1] + (pts2d[i+1][1] - pts2d[i][1]) * t,
            ))
    path.append(pts2d[-1])
    n = len(path)

    def tang(i):
        if i == 0:
            dx, dy = path[1][0]-path[0][0], path[1][1]-path[0][1]
        elif i == n-1:
            dx, dy = path[-1][0]-path[-2][0], path[-1][1]-path[-2][1]
        else:
            dx, dy = path[i+1][0]-path[i-1][0], path[i+1][1]-path[i-1][1]
        L = math.sqrt(dx*dx + dy*dy)
        return dx/L, dy/L

    hw = width / 2
    lb = []; rb = []; lt = []; rt = []
    for i, (px, py) in enumerate(path):
        tx, ty = tang(i)
        # left = inward (toward ring center), right = outward
        lb.append(bm.verts.new((px - ty*hw, py + tx*hw, z0)))
        rb.append(bm.verts.new((px + ty*hw, py - tx*hw, z0)))
        lt.append(bm.verts.new((px - ty*hw, py + tx*hw, z1)))
        rt.append(bm.verts.new((px + ty*hw, py - tx*hw, z1)))
    bm.verts.ensure_lookup_table()
    for i in range(n - 1):
        bm.faces.new([lt[i], lt[i+1], rt[i+1], rt[i]])     # top (CCW +Z)
        bm.faces.new([rb[i], rb[i+1], lb[i+1], lb[i]])     # bottom
        bm.faces.new([lb[i], lb[i+1], lt[i+1], lt[i]])     # kiri
        bm.faces.new([rt[i], rt[i+1], rb[i+1], rb[i]])     # kanan
    bm.faces.new([lb[0], rb[0], rt[0], lt[0]])             # cap awal
    bm.faces.new([rb[-1], lb[-1], lt[-1], rt[-1]])         # cap akhir


def _polygon_slab(bm, pts2d, z0, z1):
    """Polygon slab watertight — pts2d = daftar (x,y) CCW dari atas (+Z).
    Polygon harus konveks. bm_to_object akan recalc normals & triangulasi ngon.
    """
    n = len(pts2d)
    vb = [bm.verts.new((x, y, z0)) for x, y in pts2d]
    vt = [bm.verts.new((x, y, z1)) for x, y in pts2d]
    bm.verts.ensure_lookup_table()
    bm.faces.new(list(reversed(vb)))   # bawah: CW→normal -Z (luar bawah)
    bm.faces.new(vt)                    # atas:  CCW→normal +Z (luar atas)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([vb[i], vb[j], vt[j], vt[i]])


def _rotated_box(bm, cx, cy, angle, hu, hv, z0, z1):
    """Watertight box rotated `angle` radians around Z, centered at (cx,cy)."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    def rot(u, v):
        return cx + cos_a * u - sin_a * v, cy + sin_a * u + cos_a * v

    corners = [(-hu, -hv), (hu, -hv), (hu, hv), (-hu, hv)]
    vb = [bm.verts.new((*rot(*c), z0)) for c in corners]
    vt = [bm.verts.new((*rot(*c), z1)) for c in corners]
    bm.verts.ensure_lookup_table()
    bm.faces.new([vb[0], vb[3], vb[2], vb[1]])
    bm.faces.new([vt[0], vt[1], vt[2], vt[3]])
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([vb[i], vb[j], vt[j], vt[i]])


def _rotated_box_ns(bm, cx, cy, angle, hu_n, hu_s, hv, z0, z1):
    """Rotated box asimetris: hu_n ke utara (+u), hu_s ke selatan (-u).
    Digunakan untuk memotong ujung selatan slab agar tidak tembus dinding struktur.
    """
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    def rot(u, v):
        return cx + cos_a * u - sin_a * v, cy + sin_a * u + cos_a * v

    corners = [(-hu_s, -hv), (hu_n, -hv), (hu_n, hv), (-hu_s, hv)]
    vb = [bm.verts.new((*rot(*c), z0)) for c in corners]
    vt = [bm.verts.new((*rot(*c), z1)) for c in corners]
    bm.verts.ensure_lookup_table()
    bm.faces.new([vb[0], vb[3], vb[2], vb[1]])
    bm.faces.new([vt[0], vt[1], vt[2], vt[3]])
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([vb[i], vb[j], vt[j], vt[i]])


def _revolve_profile(bm, cx, cy, profile, n_sides=16):
    """Solid of revolution around Z axis at (cx,cy).
    profile = [(r,z), ...] — r=0 creates a pole (apex/base tip).
    """
    def ring(r, z):
        return [bm.verts.new((cx + r * math.cos(2*math.pi*i/n_sides),
                               cy + r * math.sin(2*math.pi*i/n_sides), z))
                for i in range(n_sides)]

    rings = []
    poles = {}
    for r, z in profile:
        if r == 0.0:
            poles[(r, z)] = bm.verts.new((cx, cy, z))
            rings.append(None)
        else:
            rings.append(ring(r, z))
    bm.verts.ensure_lookup_table()

    for i in range(len(rings) - 1):
        r0, z0 = profile[i]
        r1, z1 = profile[i + 1]
        bot, top = rings[i], rings[i + 1]
        if bot is None:
            pole = poles[(r0, z0)]
            for k in range(n_sides):
                bm.faces.new([pole, top[k], top[(k+1) % n_sides]])
        elif top is None:
            pole = poles[(r1, z1)]
            for k in range(n_sides):
                bm.faces.new([pole, bot[(k+1) % n_sides], bot[k]])
        else:
            for k in range(n_sides):
                l = (k + 1) % n_sides
                bm.faces.new([bot[k], top[k], top[l], bot[l]])

    if rings[0] is not None:
        ctr = bm.verts.new((cx, cy, profile[0][1]))
        bm.verts.ensure_lookup_table()
        for k in range(n_sides):
            bm.faces.new([ctr, rings[0][k], rings[0][(k+1) % n_sides]])
    if rings[-1] is not None:
        ctr = bm.verts.new((cx, cy, profile[-1][1]))
        bm.verts.ensure_lookup_table()
        for k in range(n_sides):
            bm.faces.new([ctr, rings[-1][(k+1) % n_sides], rings[-1][k]])


def _build_pavilion_dome(collection, px, py, z_roof, idx):
    """Satu pavilion dome: alas platform + drum + kubah hemispherical + finial."""
    slab_t = P.MATAF["SLAB_T"]

    # Platform oktagonal (alas)
    z0 = z_roof
    bm = bmesh.new()
    _revolve_profile(bm, px, py, [
        (_DOME_PLAT_R, z0),
        (_DOME_PLAT_R, z0 + _DOME_PLAT_H),
    ], n_sides=8)
    C.bm_to_object(bm, f"RUH_MASAA_DOME{idx}_PLAT_VIS", collection,
                   material_key="MARBLE")

    # Drum oktagonal (kolom dekoratif bawah kubah)
    z_drum = z0 + _DOME_PLAT_H
    bm = bmesh.new()
    _revolve_profile(bm, px, py, [
        (_DOME_DRUM_R, z_drum),
        (_DOME_DRUM_R, z_drum + _DOME_DRUM_H),
    ], n_sides=8)
    C.bm_to_object(bm, f"RUH_MASAA_DOME{idx}_DRUM_VIS", collection,
                   material_key="MARBLE")

    # Kubah hemispherical (terracotta merah)
    z_eq = z_drum + _DOME_DRUM_H   # ekuator kubah
    R = _DOME_R
    profile_dome = []
    for i in range(_DOME_N_LAT + 1):
        theta = math.pi / 2 * i / _DOME_N_LAT
        profile_dome.append((R * math.cos(theta), z_eq + R * math.sin(theta)))
    profile_dome[-1] = (0.0, profile_dome[-1][1])  # puncak sebagai pole
    bm = bmesh.new()
    _revolve_profile(bm, px, py, profile_dome, n_sides=_DOME_NSIDES)
    C.bm_to_object(bm, f"RUH_MASAA_DOME{idx}_SHELL_VIS", collection,
                   material_key="DOME_ROOF")

    # Finial emas (puncak lancip di atas kubah)
    z_apex = z_eq + R
    bm = bmesh.new()
    _revolve_profile(bm, px, py, [
        (0.12, z_apex),
        (0.12, z_apex + _DOME_FINIAL_H * 0.6),
        (0.0,  z_apex + _DOME_FINIAL_H),
    ], n_sides=8)
    C.bm_to_object(bm, f"RUH_MASAA_DOME{idx}_FINIAL_VIS", collection,
                   material_key="GOLD")


def build(collection=None):
    MA  = P.MASA
    TR  = P.TRACE["MASA_AXIS"]
    MT  = P.MATAF
    collection = collection or C.reset_collection(COLLECTION)

    safa  = TR["safa"]    # (137.0, -77.5)
    marwa = TR["marwa"]   # (105.4, 295.9)

    dx = marwa[0] - safa[0]
    dy = marwa[1] - safa[1]
    raw_len = math.sqrt(dx * dx + dy * dy)   # ≈ 374.9 m
    angle   = math.atan2(dy, dx)
    cos_a   = math.cos(angle)
    sin_a   = math.sin(angle)

    cx  = (safa[0] + marwa[0]) / 2
    cy  = (safa[1] + marwa[1]) / 2
    hl  = raw_len / 2 + 8.0
    hw  = MA["WIDTH"] / 2     # 20 m
    slab_t = MT["SLAB_T"]     # 0.3 m
    fh     = MA["FLOOR_H"]    # 8.0 m  (3×8=24 m = ring 4×6 m)
    ph     = 1.1              # parapet height
    pw     = 0.3              # parapet thickness

    # ── Badan utama Mas'a — satu massa solid, selatan sampai _HL_SOUTH (200 m) ─────
    # Mencakup bukit Safa (u≈-187 dari center) dengan margin 13 m.
    eps   = 0.002
    z_top = MA["LEVELS"] * fh + slab_t   # puncak badan = 24.3 m
    bm = bmesh.new()
    _rotated_box_ns(bm, cx, cy, angle, hl, _HL_SOUTH, hw, 0.0, z_top)
    C.bm_to_object(bm, "RUH_MASAA_BODY_VIS", collection,
                   material_key=MA["MATERIAL"])

    # ── Zona hijau Sa'i (tengah ±50 m dari pusat) ─────────────────────────────
    bm = bmesh.new()
    _rotated_box(bm, cx, cy, angle, 50.0, hw, slab_t + 0.001, slab_t + 0.021)
    C.bm_to_object(bm, "RUH_MASAA_GREEN_VIS", collection,
                   material_key=MA["GREEN_MATERIAL"])

    # ── Bukit Safa (granit, ujung selatan) — 4 m ke selatan agar masuk dalam batas ─
    bm = bmesh.new()
    _rotated_box(bm, safa[0], safa[1], angle, 4.0, 8.0, slab_t, slab_t + 5.0)
    C.bm_to_object(bm, "RUH_MASAA_SAFA_VIS", collection, material_key="GRANITE")

    # ── Bukit Marwa (marmer, ujung utara) ─────────────────────────────────────
    bm = bmesh.new()
    _rotated_box(bm, marwa[0], marwa[1], angle, 6.0, 6.0, slab_t, slab_t + 3.5)
    C.bm_to_object(bm, "RUH_MASAA_MARWA_VIS", collection,
                   material_key=MA["MATERIAL"])

    # ── Parapet atap — membentang seluas badan (hl selatan = _HL_SOUTH) ─────────
    z_roof = MA["LEVELS"] * fh      # 3×8=24 m
    for sign in (+1, -1):
        v_off = sign * (hw + pw / 2)
        pcx = cx - sin_a * v_off
        pcy = cy + cos_a * v_off
        bm = bmesh.new()
        _rotated_box_ns(bm, pcx, pcy, angle, hl - eps, _HL_SOUTH - eps, pw / 2,
                        z_roof + slab_t, z_roof + slab_t + ph)
        side = "P" if sign > 0 else "N"
        C.bm_to_object(bm, f"RUH_MASAA_ROOF_PAR_{side}_VIS", collection,
                       material_key=MA["MATERIAL"])

    # vcx/vcy = posisi tugu dome Safa — 22 m dari ujung selatan agar platform (r=7) tidak mepet
    u_dome_safa = -(_HL_SOUTH - 22.0)
    vcx = cx + cos_a * u_dome_safa
    vcy = cy + sin_a * u_dome_safa

    # ── Connector SELATAN — satu massa solid (ring SE/S → dinding barat Mas'a) ────
    bm = bmesh.new()
    _polygon_slab(bm, _CONN_PTS, 0.0, z_top)
    C.bm_to_object(bm, "RUH_MASAA_CONN_S_BODY_VIS", collection,
                   material_key=MA["MATERIAL"])

    # ── Connector UTARA — satu massa solid (sisi E ring → dinding barat Mas'a) ────
    bm = bmesh.new()
    _polygon_slab(bm, _CONN_N_PTS, 0.0, z_top)
    C.bm_to_object(bm, "RUH_MASAA_CONN_N_BODY_VIS", collection,
                   material_key=MA["MATERIAL"])

    # ── Penghubung selatan timur — CONN_S SE corner → sudut SE BODY — satu solid ──
    # Kotak sejajar sumbu Mas'a, dari titik SE CONN_S (117.3,-83) ke sudut SE BODY.
    _u_arc_se  = -_HL_SOUTH
    _v_arc_se  = -hw
    _arc_p2x   = cx + cos_a * _u_arc_se - sin_a * _v_arc_se
    _arc_p2y   = cy + sin_a * _u_arc_se + cos_a * _v_arc_se
    _ARC_P0x, _ARC_P0y = 117.3, -83.0
    _arc_dx    = _arc_p2x - _ARC_P0x
    _arc_dy    = _arc_p2y - _ARC_P0y
    _arc_hu    = abs(cos_a * _arc_dx + sin_a * _arc_dy) / 2
    _arc_hv    = abs(-sin_a * _arc_dx + cos_a * _arc_dy) / 2
    _arc_cx    = (_ARC_P0x + _arc_p2x) / 2
    _arc_cy    = (_ARC_P0y + _arc_p2y) / 2
    _arc_angle = math.atan2(sin_a, cos_a)
    bm = bmesh.new()
    _rotated_box(bm, _arc_cx, _arc_cy, _arc_angle, _arc_hu, _arc_hv, 0.0, z_top)
    C.bm_to_object(bm, "RUH_MASAA_ARC_BODY_VIS", collection,
                   material_key=MA["MATERIAL"])

    # ── Pavilion dome / tugu (Ref: 010027) — 2 buah di ujung Safa & Marwa ───────
    # Tugu Safa: di pusat vestibule (vcx, vcy), di atas roof vestibule (z=24.3m).
    # Tugu Marwa: 15 m dari ujung utara slab, di atas roof utama (z=24.3m).
    for idx, (px, py) in enumerate([
        (vcx, vcy),                                             # Safa: pusat vestibule
        (cx + cos_a * (hl - 25.0), cy + sin_a * (hl - 25.0)), # Marwa: 25 m dari ujung utara
    ]):
        _build_pavilion_dome(collection, px, py, z_roof + slab_t, idx + 1)

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
