# components/comp_ramps_inbound.py
# =============================================================================
# Inbound access ramp: a FAN of sloped slabs climbing from the eastern approach
# mouth up to the deck edge (one-way IN). Geometry from PARAMETERS.TRACE["RAMPS"]
# ["INBOUND_FAN"] (mouth, deck_join, count, spread_deg, width) + RAMPS_INBOUND.
#   VERIFY@render: exact level it joins + real fan splay vs OSM way 431617753.
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_ramps_inbound.py
# =============================================================================
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bmesh
from mathutils import Vector
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_RAMPS_INBOUND_VIS"
COLLECTION = "RAMPS"
TRI_CAP    = P.RAMPS_INBOUND["TARGET_TRI"]


def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    F = P.TRACE["RAMPS"]["INBOUND_FAN"]
    R = P.RAMPS_INBOUND
    mouth = Vector((F["mouth"][0], F["mouth"][1], 0.0))         # ground at the approach
    join = Vector((F["deck_join"][0], F["deck_join"][1], P.FLOOR_Z[2]))   # climb to L2 edge
    base = (join - mouth)
    count, spread = F["count"], math.radians(F["spread_deg"])

    bm = bmesh.new()
    for i in range(count):
        a = (-spread / 2.0) + spread * (i / max(1, count - 1))
        rot = base.copy()
        rx = rot.x * math.cos(a) - rot.y * math.sin(a)          # fan-rotate about the mouth
        ry = rot.x * math.sin(a) + rot.y * math.cos(a)
        end = mouth + Vector((rx, ry, base.z))
        mat, length = C.segment_matrix(mouth[:], end[:])
        C.add_box(bm, R["WIDTH"], R["THICKNESS"], length, mat)
    return C.bm_to_object(bm, NAME, collection, material_key="CONCRETE")


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'ramps_inbound' -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
