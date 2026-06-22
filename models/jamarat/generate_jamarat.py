# generate_jamarat.py — orchestrator for model "Jamarat Bridge Complex" (POLOS).
# Builds geometry + empty named material slots. NO textures.
# Run: blender --background --factory-startup --python models/jamarat/generate_jamarat.py
#
# Two-version setup (single-source geometry; user decision 2026-06-15):
#   - THIS file            -> POLOS    (no texture)
#   - generate_jamarat_textured.py -> TEXTURED (same geometry + materials.apply_all)
# Both call build() below; only `textured` differs. Never duplicate geometry.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))      # ruh/
sys.path += [HERE, os.path.join(HERE, "components"), ROOT]

import PARAMETERS as P
import ruh_common as C

import comp_decks
import comp_columns
import comp_jamrah_walls
import comp_canopies
import comp_tower_escalator
import comp_tower_ventilation
import comp_tower_service
import comp_roads
import comp_ramps_inbound
import comp_ramps_exit
import comp_furniture

REGISTRY = [
    # (label, build_fn, collection_name, tri_cap)
    ("decks",        comp_decks.build,        comp_decks.COLLECTION,        comp_decks.TRI_CAP),
    ("columns",      comp_columns.build,      comp_columns.COLLECTION,      comp_columns.TRI_CAP),
    ("jamrah_walls", comp_jamrah_walls.build, comp_jamrah_walls.COLLECTION, comp_jamrah_walls.TRI_CAP),
    ("canopies",     comp_canopies.build,     comp_canopies.COLLECTION,     comp_canopies.TRI_CAP),
    ("tower_escalator",   comp_tower_escalator.build,   comp_tower_escalator.COLLECTION,   comp_tower_escalator.TRI_CAP),
    ("tower_ventilation", comp_tower_ventilation.build, comp_tower_ventilation.COLLECTION, comp_tower_ventilation.TRI_CAP),
    ("tower_service",     comp_tower_service.build,     comp_tower_service.COLLECTION,     comp_tower_service.TRI_CAP),
    ("roads",         comp_roads.build,         comp_roads.COLLECTION,         comp_roads.TRI_CAP),
    ("ramps_inbound", comp_ramps_inbound.build, comp_ramps_inbound.COLLECTION, comp_ramps_inbound.TRI_CAP),
    ("ramps_exit",    comp_ramps_exit.build,    comp_ramps_exit.COLLECTION,    comp_ramps_exit.TRI_CAP),
    ("furniture",     comp_furniture.build,     comp_furniture.COLLECTION,     comp_furniture.TRI_CAP),
]


def build(textured=False):
    """Build the whole model once. Returns (collections, results).
    textured=False -> empty material slots (POLOS).
    textured=True  -> run the materials.py texture pass after geometry."""
    C.reset_scene()
    colls = {name: C.reset_collection(name) for name in {row[2] for row in REGISTRY}}
    results = []
    for label, build_fn, coll_name, cap in REGISTRY:
        obj = build_fn(colls[coll_name])
        results.append((label, *C.validate(obj, cap, warn=P.POLY_WARN_THRESHOLD)))
    if textured:
        import materials
        materials.apply_all(colls)
    return colls, results


def main(textured=False):
    _, results = build(textured=textured)
    mode = "TEXTURED" if textured else "POLOS"
    print(f"\n{C.TAG} ===== BUILD SUMMARY (Jamarat Bridge Complex / {mode}) =====")
    overall = "OK"
    for label, status, tris in results:
        print(f"{C.TAG} {status:4} {label:24} tri={tris}")
        if status == "FAIL":
            overall = "FAIL"
    print(f"{C.TAG} OVERALL: {overall}")
    if overall == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main(textured=False)
