# examples/comp_lamp_post.py
# =============================================================================
# REFERENCE COMPONENT for RUH — the pattern every models/<model>/components/
# comp_*.py copies. It is a Y-branch lamp post. It is intentionally generic
# (no real-world reference) so it can serve as the template.
#
# Run it standalone to see the pattern + validator in action:
#   blender --background --factory-startup --python examples/comp_lamp_post.py
#
# What to copy when writing a real component:
#   - the sys.path shim, the PARAMETERS/ruh_common imports
#   - NAME / COLLECTION / TRI_CAP constants
#   - a build(collection=None) that uses ruh_common primitives (watertight)
#   - the __main__ block that resets, builds, and validates
# A real component reads its numbers from models/<model>/PARAMETERS.py and its
# shape from models/<model>/references/ (see that model's AGENTS.md §R).
# =============================================================================
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))   # examples/
ROOT = os.path.dirname(HERE)                          # ruh/
sys.path += [HERE, ROOT]                              # find PARAMETERS + ruh_common

import bmesh
from mathutils import Matrix, Vector
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_FURN_LAMP_POST_VIS"
COLLECTION = "FURNITURE"
TRI_CAP    = P.LAMP["TARGET_TRI"]


def build(collection=None):
    """Build one lamp post into `collection` and return the object.
    Origin sits at the base (world 0,0,0 in local space) for easy placement."""
    L   = P.LAMP
    seg = L["SEGMENTS"]
    collection = collection or C.reset_collection(COLLECTION)
    bm = bmesh.new()

    # 1) Base — slightly tapered short cylinder on the ground.
    C.add_capped_cone(
        bm, L["BASE_RADIUS"], L["BASE_RADIUS"] * 0.8, L["BASE_HEIGHT"],
        Matrix.Translation((0, 0, L["BASE_HEIGHT"] / 2.0)), seg,
    )

    # 2) Pole — tall cylinder on the base.
    pole_z0 = L["BASE_HEIGHT"]
    C.add_capped_cone(
        bm, L["POLE_RADIUS"], L["POLE_RADIUS"], L["POLE_HEIGHT"],
        Matrix.Translation((0, 0, pole_z0 + L["POLE_HEIGHT"] / 2.0)), seg,
    )
    top = pole_z0 + L["POLE_HEIGHT"]

    # 3) Two Y arms + a downward lamp head at the tip of each.
    for side in (+1, -1):
        s = Vector((0, 0, top - 0.15))
        e = Vector((side * L["ARM_LENGTH"], 0, top - 0.15 + L["ARM_RISE"]))
        mat, length = C.segment_matrix(s, e)
        C.add_capped_cone(bm, L["ARM_RADIUS"], L["ARM_RADIUS"], length, mat, seg)

        head_mat = Matrix.Translation((e.x, e.y, e.z - L["HEAD_HEIGHT"] / 2.0))
        C.add_capped_cone(
            bm, L["HEAD_RADIUS"] * 0.4, L["HEAD_RADIUS"], L["HEAD_HEIGHT"],
            head_mat, seg,
        )

    return C.bm_to_object(bm, NAME, collection, material_key=L["MATERIAL"])


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} reference component 'lamp_post' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
