# components/comp_tower_ventilation.py
# =============================================================================
# Type B tower: ventilation & observation tower (2 instances). A tall narrow
# cylindrical exhaust SHAFT with a FLARED top (widening cone) carrying a small
# OBSERVATION / helipad DISC. Instanced at every B_VENT_OBS position in
# PARAMETERS.TRACE["TOWERS"]. (AGENTS.md §A/§D.)
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_tower_ventilation.py
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

NAME       = "RUH_TOWER_VENTILATION_VIS"
COLLECTION = "TOWERS"
TRI_CAP    = P.TOWER_VENTILATION["TARGET_TRI"]
TYPE       = "B_VENT_OBS"


def _build_one(bm, ox, oy):
    V = P.TOWER_VENTILATION
    r, h, seg = V["RADIUS"], V["HEIGHT"], V["VERTS"]

    # 1) Chimney shaft, ground -> top.
    C.add_capped_cone(bm, r, r, h, Matrix.Translation((ox, oy, h / 2.0)), seg)
    # 2) Flared cap (cone widening r -> FLARE_RADIUS). Overlaps the shaft top by 1 m
    #    (separate solid, different Z) so remove_doubles never fuses them.
    fh = V["FLARE_HEIGHT"]
    f_lo = h - 1.0
    C.add_capped_cone(bm, r, V["FLARE_RADIUS"], fh,
                      Matrix.Translation((ox, oy, f_lo + fh / 2.0)), seg)
    # 3) Observation / helipad disc just above the flare top.
    f_top = f_lo + fh
    C.add_capped_cone(bm, V["DISC_RADIUS"], V["DISC_RADIUS"], 0.6,
                      Matrix.Translation((ox, oy, f_top + 0.4)), seg)


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
    print(f"{C.TAG} component 'tower_ventilation' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
