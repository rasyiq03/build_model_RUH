# components/comp_tower_service.py
# =============================================================================
# Type C tower: service & elevator tower (3 instances). A cylindrical lift/stair
# shaft (the real one is a HALF-cylinder part-embedded in the deck edge; here a
# full slender cylinder for a watertight master) with a small roof MACHINE-ROOM
# box. Instanced at every C_SERVICE_LIFT position in PARAMETERS.TRACE["TOWERS"].
#   TODO/VERIFY@render: true half-cylinder embedded in the deck edge; window grid.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_tower_service.py
# =============================================================================
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
from mathutils import Matrix
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_TOWER_SERVICE_VIS"
COLLECTION = "TOWERS"
TRI_CAP    = P.TOWER_SERVICE["TARGET_TRI"]
TYPE       = "C_SERVICE_LIFT"


def _build_one(bm, ox, oy):
    S = P.TOWER_SERVICE
    r, h, seg = S["RADIUS"], S["HEIGHT"], S["VERTS"]

    # 1) Lift/stair shaft, ground -> roof.
    C.add_capped_cone(bm, r, r, h, Matrix.Translation((ox, oy, h / 2.0)), seg)
    # 2) Roof machine-room box.
    C.add_box(bm, r * 1.3, r * 1.3, 4.0, Matrix.Translation((ox, oy, h + 2.0)))


def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    bm = bmesh.new()
    for t in P.TRACE["TOWERS"]:
        if t["type"] == TYPE:
            _build_one(bm, t["pos"][0], t["pos"][1])
    return C.bm_to_object(bm, NAME, collection, material_key="CONCRETE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'tower_service' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
