# components/comp_kaaba.py
# =============================================================================
# Komponen: Ka'bah — bangunan kubik di titik pusat Mataf (origin 0,0).
# Z_BASE = MATAF["SLAB_T"] (0.3 m) → lantai Ka'bah tepat di atas permukaan Mataf.
# Bagian:
#   - Shadharwan     : plint marmer di dasar Ka'bah
#   - Body           : kotak utama berbalut kiswah hitam
#   - Hizam          : sabuk emas horizontal di ~65% tinggi badan
#   - Roof frame     : bingkai menonjol di tepi atap (tengah atap tampak cekung)
#   - Door panel     : panel emas, muka +X (timur), offset ke -Y (selatan) = ujung kiri
#   - Hajar Aswad    : dome oval di sudut SE (corner +hx,-hy), di sebelah kiri pintu
# Ref: masjidilharam010039-041, wire_masjid010021-023, 010014_annotated (2026-06-25)
# Koordinat: origin = pusat Ka'bah, +X = timur, +Y = utara.
# Pintu Ka'bah di muka +X (TIMUR), offset -Y (selatan) = "ujung kiri" saat menghadap pintu.
# Hijr Ismail di sisi +Y (UTARA). Hajar Aswad di sudut SE (+hx, -hy) = kiri pintu.
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_kaaba.py
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

COLLECTION = "KAABA"
TRI_CAP    = P.KAABA["TARGET_TRI"]


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


def _rect_ring_slab(bm, x_out, y_out, x_in, y_in, z0, z1):
    """Rectangular ring slab (bingkai persegi) — 16 quad watertight.
    Outer rect: ±x_out, ±y_out  |  Inner rect: ±x_in, ±y_in."""
    pts_o = [(x_out, y_out), (-x_out, y_out), (-x_out, -y_out), (x_out, -y_out)]
    pts_i = [(x_in,  y_in),  (-x_in,  y_in),  (-x_in,  -y_in),  (x_in,  -y_in)]
    O0 = [bm.verts.new((x, y, z0)) for x, y in pts_o]
    I0 = [bm.verts.new((x, y, z0)) for x, y in pts_i]
    O1 = [bm.verts.new((x, y, z1)) for x, y in pts_o]
    I1 = [bm.verts.new((x, y, z1)) for x, y in pts_i]
    bm.verts.ensure_lookup_table()
    for k in range(4):
        nk = (k + 1) % 4
        bm.faces.new([O1[k], O1[nk], I1[nk], I1[k]])
        bm.faces.new([O0[k], I0[k], I0[nk], O0[nk]])
        bm.faces.new([O0[k], O0[nk], O1[nk], O1[k]])
        bm.faces.new([I0[k], I1[k], I1[nk], I0[nk]])


def _hajar_dome(bm, cx, cy, cz, face_ax, face_ay, r_d, r_h, r_v,
                n_lat=8, n_lon=16):
    """Dome oval untuk Hajar Aswad — watertight, closed.
    Menghadap ke arah (face_ax, face_ay, 0) = outward dari sudut Ka'bah.
    r_d = kedalaman dome (sumbu maju), r_h = jari-jari horizontal oval,
    r_v = jari-jari vertikal oval (r_v > r_h → lebih tinggi dari lebar).
    Lat 0 = bibir ekuator (di permukaan dinding), lat pi/2 = puncak dome.
    """
    # Tangent horisontal dalam bidang muka (tegak lurus normal dan Z)
    tx, ty = -face_ay, face_ax

    # Bangun ring-ring dari ekuator (lat=0) ke ring terakhir sebelum puncak
    rings = []
    for li in range(n_lat):
        lat   = math.pi / 2 * li / n_lat
        cos_l = math.cos(lat)
        sin_l = math.sin(lat)
        ring  = []
        for lo in range(n_lon):
            lon = 2 * math.pi * lo / n_lon
            hc  = r_h * cos_l * math.cos(lon)   # komponen horisontal oval
            vc  = r_v * cos_l * math.sin(lon)   # komponen vertikal oval
            dc  = r_d * sin_l                    # komponen kedalaman (maju keluar)
            ring.append(bm.verts.new((
                cx + face_ax * dc + tx * hc,
                cy + face_ay * dc + ty * hc,
                cz + vc
            )))
        rings.append(ring)

    pole = bm.verts.new((cx + face_ax * r_d, cy + face_ay * r_d, cz))
    back = bm.verts.new((cx, cy, cz))   # pusat cap belakang (di permukaan dinding)
    bm.verts.ensure_lookup_table()

    # Pita-pita dome (quad per segmen per band)
    for li in range(n_lat - 1):
        for lo in range(n_lon):
            lj = (lo + 1) % n_lon
            bm.faces.new([
                rings[li][lo], rings[li+1][lo],
                rings[li+1][lj], rings[li][lj]
            ])

    # Cap puncak dome (triangle fan dari ring terakhir ke pole)
    rim = rings[-1]
    for lo in range(n_lon):
        lj = (lo + 1) % n_lon
        bm.faces.new([pole, rim[lo], rim[lj]])

    # Cap belakang flat — menutup dome agar watertight
    eq = rings[0]
    for lo in range(n_lon):
        lj = (lo + 1) % n_lon
        bm.faces.new([back, eq[lj], eq[lo]])


def build(collection=None):
    K  = P.KAABA
    M  = P.MATAF
    collection = collection or C.reset_collection(COLLECTION)

    z_base = M["SLAB_T"]          # 0.3 m — lantai Ka'bah = permukaan atas Mataf
    wx  = K["WIDTH_X"]            # 11.03 m (E-W)
    wy  = K["WIDTH_Y"]            # 12.8 m  (N-S)
    h   = K["HEIGHT"]             # 13.1 m
    shd = K["SHADHARWAN"]
    door = K["DOOR"]
    hx  = wx / 2                  # 5.515 m
    hy  = wy / 2                  # 6.4 m

    # ── Shadharwan: plint marmer menonjol di dasar ─────────────────────────────
    bm = bmesh.new()
    _box(bm,
         -hx - shd["OFFSET"], hx + shd["OFFSET"],
         -hy - shd["OFFSET"], hy + shd["OFFSET"],
         z_base, z_base + shd["H"])
    C.bm_to_object(bm, "RUH_KAABA_SHADHARWAN_VIS", collection,
                   material_key="MARBLE")

    # ── Body utama: dibalut kiswah hitam ──────────────────────────────────────
    bm = bmesh.new()
    _box(bm, -hx, hx, -hy, hy, z_base, z_base + h)
    C.bm_to_object(bm, "RUH_KAABA_BODY_VIS", collection,
                   material_key=K["MATERIAL_CLOTH"])

    # ── Hizam: sabuk emas (pita kaligrafi) di ~65% tinggi badan ───────────────
    # Ref: wire_masjid010021 — pita horisontal terlihat di 60-70% tinggi
    hz_t  = K["HIZAM_T"]
    hz_h  = K["HIZAM_H"]
    hz_z0 = z_base + h * K["HIZAM_Z_FRAC"] - hz_h / 2
    hz_z1 = hz_z0 + hz_h
    eps   = 0.002   # gap kecil di corner untuk menghindari vertex merge antar panel
    bm = bmesh.new()
    _box(bm, -hx - hz_t, hx + hz_t,  hy,        hy + hz_t,  hz_z0, hz_z1)   # muka +Y
    _box(bm, -hx - hz_t, hx + hz_t, -hy - hz_t, -hy,        hz_z0, hz_z1)   # muka -Y
    _box(bm,  hx,        hx + hz_t, -hy + eps,   hy - eps,   hz_z0, hz_z1)   # muka +X
    _box(bm, -hx - hz_t, -hx,       -hy + eps,   hy - eps,   hz_z0, hz_z1)   # muka -X
    C.bm_to_object(bm, "RUH_KAABA_HIZAM_VIS", collection, material_key="GOLD")

    # ── Roof frame: bingkai menonjol di tepi atap ─────────────────────────────
    # Ref: masjidilharam010040, wire_masjid010021
    rfw    = K["ROOF_FRAME_W"]
    rfh    = K["ROOF_FRAME_H"]
    z_roof = z_base + h
    bm = bmesh.new()
    _rect_ring_slab(bm,
                    x_out=hx, y_out=hy,
                    x_in=hx - rfw, y_in=hy - rfw,
                    z0=z_roof, z1=z_roof + rfh)
    C.bm_to_object(bm, "RUH_KAABA_ROOF_FRAME_VIS", collection,
                   material_key=K["MATERIAL_CLOTH"])

    # ── Panel pintu emas: muka +X (timur), OFFSET ke selatan (-Y) ────────────
    # Ref: masjidilharam010014_annotated — pintu "di ujung kiri sedikit" saat menghadap
    # muka timur dari luar. Kiri = arah selatan (-Y). Hajar Aswad lebih jauh ke kiri
    # (sudut SE). Offset DOOR_X_OFFSET ke arah -Y dari tengah muka.
    dw    = door["w"]
    dh    = door["h"]
    dzb   = door["z_base"]
    off   = K["DOOR_X_OFFSET"]              # 1.5 m dari tengah muka, ke selatan
    dy0   = -(off + dw / 2)                 # = -2.45 m (sisi selatan panel)
    dy1   = -(off - dw / 2)                 # = -0.55 m (sisi utara panel)
    bm = bmesh.new()
    _box(bm, hx, hx + 0.05, dy0, dy1,      # muka +X (timur), offset ke -Y (selatan)
         z_base + dzb, z_base + dzb + dh)
    C.bm_to_object(bm, "RUH_KAABA_DOOR_VIS", collection, material_key="GOLD")

    # ── Hajar Aswad: dome oval di sudut SE (+hx, -hy) ────────────────────────
    # Ref: masjidilharam010014_annotated — "hajar aswad di sebelah kiri pintu"
    # Dari luar muka +X (timur): kiri = arah selatan (-Y). Pintu di y≈-1.5, Hajar Aswad
    # di sudut SE (y=-hy) = lebih ke selatan/kiri. Dome menghadap SE (+X/-Y diagonal).
    diag   = math.sqrt(0.5)   # cos/sin 45°
    bm = bmesh.new()
    _hajar_dome(bm,
                cx=hx, cy=-hy, cz=z_base + K["HAJAR_ASWAD_Z"],
                face_ax=diag, face_ay=-diag,     # menghadap SE
                r_d=K["HAJAR_ASWAD_DEPTH"],
                r_h=K["HAJAR_ASWAD_R_H"],
                r_v=K["HAJAR_ASWAD_R_V"])
    C.bm_to_object(bm, "RUH_KAABA_HAJAR_ASWAD_VIS", collection,
                   material_key="GRANITE")

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
