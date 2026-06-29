# components/comp_maqam_ibrahim.py
# =============================================================================
# Komponen: Maqam Ibrahim — cungkup oktagonal emas di dekat Ka'bah.
# Posisi: searah pintu Ka'bah (+Y utara, offset +X), ~12 m dari pusat Ka'bah.
# Bagian:
#   - Base : plint oktagonal marmer
#   - Body : tower oktagonal emas dengan belt dekoratif + kubah runcing
# Ref: masjidilharam010014 (pin 6), referensi web 2026-06-25
# Koordinat: origin = pusat Ka'bah, +X = timur, +Y = utara
# Run standalone:
#   blender --background --factory-startup --python \
#       models/masjidil-haram/components/comp_maqam_ibrahim.py
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

COLLECTION = "MAQAM_IBRAHIM"
TRI_CAP    = P.MAQAM_IBRAHIM["TARGET_TRI"]


def _revolve_profile(bm, cx, cy, profile, n_sides=8):
    """Solid of revolution di sekitar sumbu Z pada (cx, cy).
    profile = [(r, z), ...] dari bawah ke atas; r=0 → pole vertex.
    Menghasilkan mesh watertight satu objek.
    """
    angles = [2 * math.pi * i / n_sides for i in range(n_sides)]

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
        bot   = rings[i]
        top   = rings[i + 1]
        r_bot = profile[i][0]
        r_top = profile[i + 1][0]

        if r_bot < 1e-6 and r_top >= 1e-6:
            pole = bot[0]
            for j in range(n):
                bm.faces.new([pole, top[(j + 1) % n], top[j]])
        elif r_top < 1e-6 and r_bot >= 1e-6:
            pole = top[0]
            for j in range(n):
                bm.faces.new([pole, bot[j], bot[(j + 1) % n]])
        elif r_bot < 1e-6 and r_top < 1e-6:
            pass
        else:
            for j in range(n):
                bm.faces.new([bot[j], bot[(j+1)%n], top[(j+1)%n], top[j]])

    if profile[0][0] >= 1e-6:
        ctr = bm.verts.new((cx, cy, profile[0][1]))
        bm.verts.ensure_lookup_table()
        bot = rings[0]
        for j in range(n):
            bm.faces.new([ctr, bot[(j + 1) % n], bot[j]])

    if profile[-1][0] >= 1e-6:
        ctr = bm.verts.new((cx, cy, profile[-1][1]))
        bm.verts.ensure_lookup_table()
        top = rings[-1]
        for j in range(n):
            bm.faces.new([ctr, top[j], top[(j + 1) % n]])


def build(collection=None):
    M  = P.MAQAM_IBRAHIM
    MT = P.MATAF
    collection = collection or C.reset_collection(COLLECTION)

    z0     = MT["SLAB_T"]              # 0.3 m — lantai = permukaan atas Mataf
    px     = M["POS_X"]               # 1.5 m ke timur
    py     = M["POS_Y"]               # 12.0 m ke utara dari Ka'bah centre
    n      = M["N_SIDES"]             # 8
    r_base = M["BASE_R"]              # 0.85 m
    base_h = M["BASE_H"]              # 0.20 m
    r_body = M["RADIUS"]              # 0.65 m
    dome_h = M["DOME_H"]              # 0.40 m
    body_h = M["HEIGHT"] - base_h - dome_h   # 1.90 m tinggi badan lurus

    # ── Plint marmer ──────────────────────────────────────────────────────────
    bm = bmesh.new()
    _revolve_profile(bm, px, py, [
        (r_base, z0),
        (r_base, z0 + base_h),
    ], n_sides=n)
    C.bm_to_object(bm, "RUH_MAQAM_BASE_VIS", collection,
                   material_key=M["MATERIAL_BASE"])

    # ── Badan: tower oktagonal + belt dekoratif + kubah runcing ───────────────
    # Belt horizontal menonjol di 40% tinggi badan → memberi detail tanpa polygon banyak.
    z_bot    = z0 + base_h
    belt_z   = z_bot + body_h * 0.40        # belt mulai di 40% tinggi badan
    belt_top = belt_z + 0.10                 # belt tebal 10 cm
    z_top    = z_bot + body_h
    z_peak   = z_top + dome_h
    belt_r   = r_body + 0.04                 # belt menonjol 4 cm dari badan

    bm = bmesh.new()
    _revolve_profile(bm, px, py, [
        (r_body,          z_bot),                     # badan bawah
        (r_body,          belt_z),                    # menuju belt
        (belt_r,          belt_z),                    # belt mulai (step keluar)
        (belt_r,          belt_top),                  # belt atas
        (r_body,          belt_top),                  # kembali ke badan
        (r_body,          z_top),                     # badan atas
        (r_body * 0.65,   z_top + dome_h * 0.45),    # dome taper awal
        (r_body * 0.25,   z_top + dome_h * 0.80),    # dome sempit
        (0.0,             z_peak),                    # puncak (pole)
    ], n_sides=n)
    C.bm_to_object(bm, "RUH_MAQAM_BODY_VIS", collection,
                   material_key=M["MATERIAL_BODY"])

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
