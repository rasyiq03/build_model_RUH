# generate_masjidil_haram.py — thin orchestrator for model "Masjid al-Haram Complex".
# Run: blender --background --factory-startup --python models/masjidil-haram/generate_masjidil_haram.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))      # ruh/
sys.path += [HERE, os.path.join(HERE, "components"), ROOT]

import PARAMETERS as P
import ruh_common as C

# from components import comp_<part>   # <- import each component here

REGISTRY = [
    # (label, build_fn, collection_name, tri_cap)
    # ("<part>", comp_<part>.build, comp_<part>.COLLECTION, comp_<part>.TRI_CAP),
]


def main():
    C.reset_scene()
    colls = {name: C.reset_collection(name) for name in {row[2] for row in REGISTRY}}
    results = []
    for label, build_fn, coll_name, cap in REGISTRY:
        obj = build_fn(colls[coll_name])
        results.append((label, *C.validate(obj, cap, warn=P.POLY_WARN_THRESHOLD)))
    print(f"\n{C.TAG} ===== BUILD SUMMARY (Masjid al-Haram Complex) =====")
    overall = "OK"
    for label, status, tris in results:
        print(f"{C.TAG} {status:4} {label:24} tri={tris}")
        if status == "FAIL":
            overall = "FAIL"
    print(f"{C.TAG} OVERALL: {overall}")
    if overall == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
