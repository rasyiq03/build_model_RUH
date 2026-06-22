# components/comp_ramps_exit.py
# =============================================================================
# Outbound exit ramps: spiral HELIX ramps that wind down from an upper deck (L3)
# to ground (L1) + a long ELEVATED exit bridge. Geometry from PARAMETERS.TRACE
# ["RAMPS"] (HELIX_EXIT centers/r_in/r_out, ELEVATED_EXIT_BRIDGE) + RAMPS_EXIT.
#   VERIFY@render: real descent level + bridge route vs OSM ways.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_ramps_exit.py
# =============================================================================
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_RAMPS_EXIT_VIS"
COLLECTION = "RAMPS"
TRI_CAP    = P.RAMPS_EXIT["TARGET_TRI"]
_TURNS = 2.0
_STEPS = 28


def _helix(bm, cx, cy, r, z_hi, z_lo, width, th):
    prev = None
    for k in range(_STEPS + 1):
        a = 2 * math.pi * _TURNS * k / _STEPS
        z = z_hi + (z_lo - z_hi) * (k / _STEPS)
        p = (cx + r * math.cos(a), cy + r * math.sin(a), z)
        if prev is not None:
            mat, length = C.segment_matrix(prev, p)
            C.add_box(bm, width, th, length, mat)
        prev = p


def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    H = P.TRACE["RAMPS"]["HELIX_EXIT"]
    R = P.RAMPS_EXIT
    z_hi, z_lo = P.FLOOR_Z[3], P.FLOOR_Z[1]
    r = 0.5 * (H["r_in"] + H["r_out"])

    bm = bmesh.new()
    for (cx, cy) in H["centers"]:
        _helix(bm, cx, cy, r, z_hi, z_lo, R["WIDTH"], R["THICKNESS"])
    # Elevated exit bridge: a long slab leaving the core at L3 toward the tunnel.
    mat, length = C.segment_matrix((120.0, 230.0, P.FLOOR_Z[3]), (360.0, 470.0, P.FLOOR_Z[2]))
    C.add_box(bm, R["WIDTH"] + 2.0, R["THICKNESS"], length, mat)
    return C.bm_to_object(bm, NAME, collection, material_key="CONCRETE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'ramps_exit' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
