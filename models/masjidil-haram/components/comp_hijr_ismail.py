# components/comp_hijr_ismail.py
# =============================================================================
# Komponen: Hijr Ismail (Hateem) — dinding busur rendah di utara Ka'bah.
# Bagian:
#   - Arc wall  : dinding busur faceted (16 segmen, 180° = setengah lingkaran) — MARBLE
#   - Gate frame: bingkai gerbang di kedua ujung busur (timur & barat) — MARBLE
#   - Lamp post : tiang lampu ornamental oktagonal (4x) di atas dinding — METAL
# Ref: masjidilharam010042–010046, 010014, 010015 (2026-06-25)
# Geometri busur:
#   - Pusat busur: (0, hy) = midpoint muka utara Ka'bah = (0, 6.4 m)
#   - Radius centreline: 8.5 m dari pusat busur (BUKAN dari pusat Ka'bah)
#   - Busur 0°–180° → setengah lingkaran terbuka ke selatan (ke arah pintu Ka'bah)
#   - Endpoint inner face di (±7.75, 6.4) → gap masuk ~2.2 m dari sudut Ka'bah
#   - Puncak utara inner face: (0, 14.125) = 7.7 m di utara muka Ka'bah
# Z_BASE = MATAF["SLAB_T"] = 0.3 m (lantai = permukaan Mataf ground level)
# Koordinat: origin = pusat Ka'bah, +Y = UTARA (sisi Hijr Ismail), -Y = SELATAN (sisi pintu Ka'bah), +X = timur
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_hijr_ismail.py
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

COLLECTION = "HIJR_ISMAIL"
TRI_CAP    = P.HIJR_ISMAIL["TARGET_TRI"]


# ---------------------------------------------------------------------------
# Primitive helpers
# ---------------------------------------------------------------------------

def _arc_wall(bm, a_start, a_end, r_in, r_out, z0, z1, n_segs, ox=0.0, oy=0.0):
    """Dinding busur watertight — satu bmesh tunggal.
    ox, oy = offset titik pusat busur di dunia (default origin).
    Membuat (n_segs+1) titik sudut per ring, 4 ring total.
    Faces: n_segs top + n_segs bottom + n_segs outer + n_segs inner + 2 end caps.
    Tiap edge dijamin shared oleh tepat 2 face → watertight.
    """
    span   = a_end - a_start
    angles = [a_start + span * i / n_segs for i in range(n_segs + 1)]

    bi = [bm.verts.new((ox + r_in  * math.cos(a), oy + r_in  * math.sin(a), z0)) for a in angles]
    bo = [bm.verts.new((ox + r_out * math.cos(a), oy + r_out * math.sin(a), z0)) for a in angles]
    ti = [bm.verts.new((ox + r_in  * math.cos(a), oy + r_in  * math.sin(a), z1)) for a in angles]
    to = [bm.verts.new((ox + r_out * math.cos(a), oy + r_out * math.sin(a), z1)) for a in angles]
    bm.verts.ensure_lookup_table()

    for i in range(n_segs):
        j = i + 1
        bm.faces.new([ti[i], to[i], to[j], ti[j]])    # atas
        bm.faces.new([bi[i], bi[j], bo[j], bo[i]])    # bawah
        bm.faces.new([bo[i], bo[j], to[j], to[i]])    # luar
        bm.faces.new([bi[j], bi[i], ti[i], ti[j]])    # dalam

    # End cap di a_start dan a_end (tiap edge shared oleh tepat 1 face lain)
    bm.faces.new([bi[0],  bo[0],  to[0],  ti[0]])     # end cap mulai
    bm.faces.new([bo[-1], bi[-1], ti[-1], to[-1]])    # end cap akhir


def _box_local(bm, rx, ry, cx, cy, r0, r1, t0, t1, z0, z1):
    """Kotak watertight dalam sistem koordinat lokal (radial r, tangensial t, Z).
    rx,ry = unit radial; tx,ty = unit tangensial = (-ry, rx).
    r,t = skalar offset dari titik pusat (cx, cy).
    """
    tx, ty = -ry, rx

    def _v(r, t, z):
        return bm.verts.new((cx + r*rx + t*tx, cy + r*ry + t*ty, z))

    b00 = _v(r0, t0, z0); b10 = _v(r1, t0, z0)
    b11 = _v(r1, t1, z0); b01 = _v(r0, t1, z0)
    t00 = _v(r0, t0, z1); t10 = _v(r1, t0, z1)
    t11 = _v(r1, t1, z1); t01 = _v(r0, t1, z1)
    bm.verts.ensure_lookup_table()

    # 6 face, winding CCW dari luar (normal mengarah keluar)
    bm.faces.new([b00, b01, b11, b10])    # bawah
    bm.faces.new([t00, t10, t11, t01])    # atas
    bm.faces.new([b00, b10, t10, t00])    # sisi t0
    bm.faces.new([b10, b11, t11, t10])    # sisi r1
    bm.faces.new([b11, b01, t01, t11])    # sisi t1
    bm.faces.new([b01, b00, t00, t01])    # sisi r0


def _gate_frame(bm, a, r_in, r_out, z0, wall_h, arch_h, pillar_w, ox=0.0, oy=0.0):
    """Bingkai gerbang di ujung busur pada sudut a.
    ox, oy = offset titik pusat busur (sama dgn _arc_wall).
    Terdiri dari 3 kotak (pillar dalam, pillar luar, lintel atas).
    Bingkai menonjol ke arah tangensial dari ujung busur.
    """
    rx, ry = math.cos(a), math.sin(a)    # arah radial di titik ujung

    # cx, cy = pusat busur (offset) — _box_local menambahkan r*rx dan t*tx
    cx = ox
    cy = oy

    # Bingkai menonjol ke KEDUA arah tangensial (simetris di ujung busur)
    # Ini memastikan gate terlihat dari kedua sisi (dalam dan luar Hijr).
    frame_d = wall_h * 0.25
    t0, t1  = -frame_d / 2, frame_d / 2

    z_top = z0 + wall_h + arch_h

    # eps: gap kecil antar kotak agar remove_doubles tidak merge vertex
    # di batas bersama → cegah non-manifold edge (sama seperti Ka'bah hizam)
    eps = 0.002

    # Pilar dalam (r_in → r_in + pillar_w - eps)
    _box_local(bm, rx, ry, cx, cy,
               r_in,                    r_in + pillar_w - eps,
               t0, t1, z0, z_top)
    # Pilar luar (r_out - pillar_w + eps → r_out)
    _box_local(bm, rx, ry, cx, cy,
               r_out - pillar_w + eps,  r_out,
               t0, t1, z0, z_top)
    # Lintel di atas bukaan (r_in+pillar_w → r_out-pillar_w, z: wall_h → z_top)
    _box_local(bm, rx, ry, cx, cy,
               r_in + pillar_w,         r_out - pillar_w,
               t0, t1, z0 + wall_h, z_top)


def _revolve_profile(bm, cx, cy, profile, n_sides=8):
    """Solid of revolution di sekitar sumbu Z pada (cx, cy).
    profile = [(r, z), ...] dari bawah ke atas; r=0 → pole vertex.
    Menghasilkan mesh watertight satu objek.

    Winding convention: CCW dari luar → normal outward.
    Bottom cap: [ctr, bot[j+1], bot[j]] → normal -Z (bawah). ✓
    Band quads: [bot[j], bot[j+1], top[j+1], top[j]] → normal outward. ✓
    Top-pole fan: [pole, bot[j], bot[j+1]] → normal outward. ✓
    """
    angles = [2 * math.pi * i / n_sides for i in range(n_sides)]

    # Bangun rings; r=0 → satu vertex pole
    rings = []
    for (r, z) in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((cx, cy, z))])
        else:
            rings.append([
                bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z))
                for a in angles
            ])
    bm.verts.ensure_lookup_table()

    n = n_sides

    for i in range(len(profile) - 1):
        bot     = rings[i]
        top     = rings[i + 1]
        r_bot   = profile[i][0]
        r_top   = profile[i + 1][0]

        if r_bot < 1e-6 and r_top >= 1e-6:
            # Pole bawah → triangle fan (tidak terjadi pada profil lamp kita)
            pole = bot[0]
            for j in range(n):
                bm.faces.new([pole, top[(j + 1) % n], top[j]])

        elif r_top < 1e-6 and r_bot >= 1e-6:
            # Pole atas (ujung spire) → triangle fan, normal outward
            pole = top[0]
            for j in range(n):
                bm.faces.new([pole, bot[j], bot[(j + 1) % n]])

        elif r_bot < 1e-6 and r_top < 1e-6:
            pass   # dua pole berturut-turut (skip)

        else:
            # Dua ring penuh → quads, normal outward
            for j in range(n):
                bm.faces.new([bot[j], bot[(j+1)%n], top[(j+1)%n], top[j]])

    # Cap bawah (ring pertama bukan pole → tutup dengan fan)
    if profile[0][0] >= 1e-6:
        ctr = bm.verts.new((cx, cy, profile[0][1]))
        bm.verts.ensure_lookup_table()
        bot = rings[0]
        for j in range(n):
            bm.faces.new([ctr, bot[(j + 1) % n], bot[j]])    # normal -Z

    # Cap atas (ring terakhir bukan pole → tutup dengan fan)
    if profile[-1][0] >= 1e-6:
        ctr = bm.verts.new((cx, cy, profile[-1][1]))
        bm.verts.ensure_lookup_table()
        top = rings[-1]
        for j in range(n):
            bm.faces.new([ctr, top[j], top[(j + 1) % n]])    # normal +Z


# ---------------------------------------------------------------------------
# Lamp post profile (dari gambar 010042 + 010044)
# ---------------------------------------------------------------------------
# Profil diukur relatif terhadap z=0 (= atas dinding Hijr Ismail).
# Penampang oktagonal (n_sides=8). Dari bawah (plint) ke pucuk (spire).
# Titik terakhir r=0 → puncak spire ditangani oleh pole-fan, bukan cap atas.

_LAMP_PROFILE = [
    # (radius_m,  z_di_atas_dinding_m)
    (0.28, 0.00),   # plint bawah — lebar
    (0.28, 0.10),   # plint atas
    (0.20, 0.13),   # step turun ke tiang
    (0.08, 0.19),
    (0.07, 0.20),   # tiang tipis mulai
    (0.08, 0.42),   # ornamen bulge tengah tiang
    (0.07, 0.52),   # ornamen selesai
    (0.07, 0.96),   # tiang atas
    (0.15, 1.10),   # flare bawah badan lamp
    (0.17, 1.20),   # badan mulai (silinder lebar)
    (0.17, 1.90),   # badan atas
    (0.10, 2.00),   # taper atas badan
    (0.07, 2.08),   # leher
    (0.07, 2.16),   # leher atas
    (0.22, 2.26),   # cap flare keluar
    (0.22, 2.33),   # cap datar
    (0.06, 2.42),   # cap menyempit ke pangkal spire
    (0.04, 2.48),   # pangkal spire
    (0.00, 2.85),   # ujung spire (r=0 → pole, menutup mesh tanpa cap)
]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(collection=None):
    H  = P.HIJR_ISMAIL
    K  = P.KAABA
    M  = P.MATAF
    collection = collection or C.reset_collection(COLLECTION)

    z0      = M["SLAB_T"]          # 0.3 m — lantai (atas Mataf)
    r_ctr   = H["RADIUS"]          # 8.5 m — radius centreline dari pusat busur
    wall_h  = H["HEIGHT"]          # 1.31 m
    wall_t  = H["THICKNESS"]       # 1.5 m
    n_segs  = H["N_SEGS"]          # 16 segmen polygon
    r_in    = r_ctr - wall_t / 2   # 7.725 m
    r_out   = r_ctr + wall_t / 2   # 9.275 m
    z1      = z0 + wall_h           # atas dinding = 1.61 m

    hy = K["WIDTH_Y"] / 2           # 6.4 m — y muka utara Ka'bah (+Y face)

    # Titik pusat busur Hijr Ismail = midpoint muka utara Ka'bah.
    # Ini menjadikan busur sebagai SETENGAH LINGKARAN SEJATI yang terbuka
    # ke selatan (ke arah Ka'bah), dengan chord datar di y=hy.
    # Endpoint busur di (±r_in..r_out, hy) → jarak ke sudut Ka'bah:
    #   r_in - hx = 7.725 - 5.515 = 2.21 m (gap masuk, tidak mepet).
    arc_cx   = 0.0
    arc_cy   = hy      # 6.4 m

    # Busur Hijr Ismail: SETENGAH LINGKARAN PENUH di utara (+Y) Ka'bah.
    # 0° = timur (+X dari arc_cx), 90° = utara, 180° = barat (-X dari arc_cx).
    a_start  = 0.0          # endpoint timur
    a_end    = math.pi      # endpoint barat
    arc_span = math.pi      # tepat 180°

    # ── Arc wall ──────────────────────────────────────────────────────────────
    bm = bmesh.new()
    _arc_wall(bm, a_start, a_end, r_in, r_out, z0, z1, n_segs,
              ox=arc_cx, oy=arc_cy)
    C.bm_to_object(bm, "RUH_HIJR_WALL_VIS", collection,
                   material_key=H["MATERIAL"])

    # ── Gate frame: bingkai di tiap ujung busur ───────────────────────────────
    pillar_w = H["GATE_PILLAR_W"]   # 0.30 m
    arch_h   = H["GATE_ARCH_H"]     # 0.35 m

    for a_gate, side in ((a_start, "E"), (a_end, "W")):
        bm = bmesh.new()
        _gate_frame(bm, a_gate, r_in, r_out, z0, wall_h, arch_h, pillar_w,
                    ox=arc_cx, oy=arc_cy)
        C.bm_to_object(bm, f"RUH_HIJR_GATE_{side}_VIS", collection,
                       material_key=H["GATE_MATERIAL"])

    # ── Lamp posts: 4 tiang lampu oktagonal di atas dinding ───────────────────
    n_lamps = H["LAMP_COUNT"]   # 4
    for li in range(n_lamps):
        a_lamp = a_start + arc_span * (2 * li + 1) / (2 * n_lamps)
        lx = arc_cx + r_ctr * math.cos(a_lamp)
        ly = arc_cy + r_ctr * math.sin(a_lamp)
        z_lamp = z1   # lamp dimulai dari permukaan atas dinding

        bm = bmesh.new()
        _revolve_profile(
            bm, lx, ly,
            [(r, z_lamp + dz) for r, dz in _LAMP_PROFILE],
            n_sides=8,
        )
        C.bm_to_object(bm, f"RUH_HIJR_LAMP_{li+1:02d}_VIS", collection,
                       material_key=H["LAMP_MATERIAL"])

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
