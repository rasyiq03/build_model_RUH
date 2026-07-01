# generate_masjidil_haram.py — thin orchestrator for model "Masjid al-Haram Complex".
# Run: blender --background --factory-startup --python models/masjidil-haram/generate_masjidil_haram.py
# Output: models/masjidil-haram/exports/masjidil_haram.blend
import sys, os
import bpy
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path += [HERE, os.path.join(HERE, "components"), ROOT]

import PARAMETERS as P
import ruh_common as C
import texture_otomatis_masjidil_haram as TA

# --- Aktif (file ada di disk) ---
from components import comp_haram_structure
from components import comp_mataf
from components import comp_kaaba
from components import comp_hijr_ismail
from components import comp_maqam_ibrahim
from components import comp_masaa
from components import comp_columns
from components import comp_arches
from components import comp_expansion_wings
from components import comp_abdullah_expansion
from components import comp_minarets
from components import comp_gates
from components import comp_fahd_domes

# --- Nonaktif: file hilang dari sesi sebelumnya, perlu direkonstruksi ---
# from components import comp_ground
# from components import comp_landmarks
# from components import comp_furniture
# from components import comp_domes
# from components import comp_masaa_connector
# --- Nonaktif: ditunda per instruksi user ("menara dan gerbang belakangan") ---

REGISTRY = [
    ("haram_structure",    comp_haram_structure.build,    comp_haram_structure.COLLECTION,    comp_haram_structure.TRI_CAP),
    ("mataf",              comp_mataf.build,              comp_mataf.COLLECTION,              comp_mataf.TRI_CAP),
    ("kaaba",              comp_kaaba.build,              comp_kaaba.COLLECTION,              comp_kaaba.TRI_CAP),
    ("hijr_ismail",        comp_hijr_ismail.build,        comp_hijr_ismail.COLLECTION,        comp_hijr_ismail.TRI_CAP),
    ("maqam_ibrahim",      comp_maqam_ibrahim.build,      comp_maqam_ibrahim.COLLECTION,      comp_maqam_ibrahim.TRI_CAP),
    ("masaa",              comp_masaa.build,              comp_masaa.COLLECTION,              comp_masaa.TRI_CAP),
    ("columns",            comp_columns.build,            comp_columns.COLLECTION,            comp_columns.TRI_CAP),
    ("arches",             comp_arches.build,             comp_arches.COLLECTION,             comp_arches.TRI_CAP),
    ("expansion_wings",    comp_expansion_wings.build,    comp_expansion_wings.COLLECTION,    comp_expansion_wings.TRI_CAP),
    ("abdullah_expansion", comp_abdullah_expansion.build, comp_abdullah_expansion.COLLECTION, comp_abdullah_expansion.TRI_CAP),
    # ("ground",          ...) — nonaktif
    # ("landmarks",       ...) — nonaktif
    # ("furniture",       ...) — nonaktif
    # ("domes",           ...) — nonaktif
    # ("masaa_connector", ...) — nonaktif
    ("minarets",           comp_minarets.build,           comp_minarets.COLLECTION,           comp_minarets.TRI_CAP),
    ("gates",              comp_gates.build,              comp_gates.COLLECTION,              comp_gates.TRI_CAP),
    ("fahd_domes",         comp_fahd_domes.build,         comp_fahd_domes.COLLECTION,         comp_fahd_domes.TRI_CAP),
]


def main():
    C.reset_scene()
    colls = {}
    for _, _, coll_name, _ in REGISTRY:
        if coll_name not in colls:
            colls[coll_name] = C.reset_collection(coll_name)

    results = []
    for label, build_fn, coll_name, cap in REGISTRY:
        coll = colls[coll_name]
        build_fn(coll)
        for obj in coll.objects:
            status, tris = C.validate(obj, cap, warn=P.POLY_WARN_THRESHOLD)
            results.append((label, obj.name, status, tris))

    print(f"\n{C.TAG} ===== BUILD SUMMARY (Masjid al-Haram Complex) =====")
    overall = "OK"
    for label, name, status, tris in results:
        print(f"{C.TAG} {status:4} [{label}] {name:40} tri={tris}")
        if status == "FAIL":
            overall = "FAIL"
    print(f"\n{C.TAG} OVERALL: {overall}")
    if overall == "FAIL":
        raise SystemExit(1)

    print(f"\n{C.TAG} ===== APPLYING AUTO TEXTURES =====")
    TA.apply_auto_textures()

    out_dir  = os.path.join(HERE, "exports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "masjidil_haram.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_path, check_existing=False)
    print(f"{C.TAG} Saved → {out_path}")


if __name__ == "__main__":
    main()
