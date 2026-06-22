# components/comp_tower_escalator.py
# =============================================================================
# Type A tower: oval escalator/access + HELIPAD tower (~11 instances). A wide
# OVAL concrete shaft (RADIUS x OVAL_RATIO across) with a vertical LOUVER facade
# and a flat circular HELIPAD roof. One master form, instanced at every
# A_ESC_HELIPAD position in PARAMETERS.TRACE["TOWERS"]. (AGENTS.md §A/§D.)
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_tower_escalator.py
# =============================================================================
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
from mathutils import Matrix
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_TOWER_ESCALATOR_VIS"
COLLECTION = "TOWERS"
TRI_CAP    = P.TOWER_ESCALATOR["TARGET_TRI"]
TYPE       = "A_ESC_HELIPAD"


def _build_one(bm, ox, oy):
    E = P.TOWER_ESCALATOR
    r, ratio, h, seg = E["RADIUS"], E["OVAL_RATIO"], E["HEIGHT"], E["VERTS"]
    ax, by = r * ratio, r
    oval = Matrix.Diagonal((ratio, 1.0, 1.0, 1.0))   # scale circle -> oval (long axis X)

    # 1) Oval shaft, ground -> roof.
    C.add_capped_cone(bm, r, r, h, Matrix.Translation((ox, oy, h / 2.0)) @ oval, seg)
    # 2) Vertical louver fins around the facade.
    for i in range(E["LOUVER_COUNT"]):
        a = 2 * math.pi * i / E["LOUVER_COUNT"]
        px, py = ox + ax * math.cos(a), oy + by * math.sin(a)
        m = Matrix.Translation((px, py, h * 0.5)) @ Matrix.Rotation(a, 4, "Z")
        C.add_box(bm, E["LOUVER_DEPTH"], 0.5, h * 0.86, m)
    # 3) Flat helipad roof disc.
    C.add_capped_cone(bm, E["HELIPAD_RADIUS"], E["HELIPAD_RADIUS"], 0.6,
                      Matrix.Translation((ox, oy, h + 0.3)), seg)


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
    print(f"{C.TAG} component 'tower_escalator' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
