# models/masjidil-haram/components/comp_gates.py
import sys, os, math
import bmesh
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MODEL_DIR))
if MODEL_DIR not in sys.path: sys.path.append(MODEL_DIR)
if ROOT not in sys.path: sys.path.append(ROOT)

import PARAMETERS as P
import ruh_common as C
from components.comp_minarets import snap_to_polygons

NAME = "RUH_GATE"
COLLECTION = "GATES"
GATE_PARAMS = P.TRACE.get("GATE_MAIN", {})
TRI_CAP = GATE_PARAMS.get("TARGET_TRI", 8000)

def build_gate(collection, index, cx, cy, width, angle, height, depth):
    # Base transform
    loc = Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(angle, 4, 'Z')
    master_objs = []
    
    mat_main = GATE_PARAMS.get("MATERIAL_MAIN", "MARBLE")
    mat_orn = GATE_PARAMS.get("MATERIAL_ORNAMENT", "BEIGE")
    
    # 1. Back Wall (recessed) - Only upper part to leave the entrance hollow
    bm_back = bmesh.new()
    back_y = depth / 2.0 - 0.5
    door_h = 10.0
    back_h = height - door_h
    C.add_box(bm_back, width, 1.0, back_h, loc @ Matrix.Translation((0, back_y, door_h + back_h/2.0)))
    obj_back = C.bm_to_object(bm_back, f"{NAME}_{index}_BACK_VIS", collection, material_key="CONCRETE_DARK")
    master_objs.append(obj_back)
    
    # 2. Main Frame (Sides and Top)
    bm_frame = bmesh.new()
    side_w = 4.0
    # Left side
    C.add_box(bm_frame, side_w, depth, height, loc @ Matrix.Translation((-width/2.0 + side_w/2.0, 0, height/2.0)))
    # Right side
    C.add_box(bm_frame, side_w, depth, height, loc @ Matrix.Translation((width/2.0 - side_w/2.0, 0, height/2.0)))
    
    # Top solid block
    top_h = height * 0.4
    inner_w = width - (side_w * 2)
    # Make top block overlap into the pillars slightly to avoid non-manifold merges
    C.add_box(bm_frame, inner_w + 0.2, depth, top_h, loc @ Matrix.Translation((0, 0, height - top_h/2.0)))
    
    # Crenellations (gigi atap)
    cren_count = int(width / 1.5)
    cren_w = 0.6
    cren_h = 1.2
    for i in range(cren_count):
        x = -width/2.0 + (i + 0.5) * (width / cren_count)
        C.add_box(bm_frame, cren_w, depth*0.8, cren_h, loc @ Matrix.Translation((x, 0, height + cren_h/2.0)))
        
    obj_frame = C.bm_to_object(bm_frame, f"{NAME}_{index}_FRAME_VIS", collection, material_key=mat_main)
    master_objs.append(obj_frame)
    
    # 3. Inner Pillars and Arches (Ornaments)
    bm_orn = bmesh.new()
    inner_w = width - (side_w * 2)
    arch_w = inner_w / 3.0
    pillar_w = 1.5
    
    pillar_h = height * 0.4
    
    # 2 Pillars
    C.add_box(bm_orn, pillar_w, depth*0.6, pillar_h, loc @ Matrix.Translation((-arch_w/2.0, 0, pillar_h/2.0)))
    C.add_box(bm_orn, pillar_w, depth*0.6, pillar_h, loc @ Matrix.Translation((arch_w/2.0, 0, pillar_h/2.0)))
    
    # Lintel / Arch Base
    lintel_h = 2.0
    C.add_box(bm_orn, inner_w, depth*0.6, lintel_h, loc @ Matrix.Translation((0, 0, pillar_h + lintel_h/2.0)))
    
    # Arch stepped simulation (low poly arch)
    for i in [-1, 0, 1]:
        ax = i * arch_w
        # Step 1
        C.add_box(bm_orn, arch_w - pillar_w, depth*0.65, 0.5, loc @ Matrix.Translation((ax, 0, pillar_h - 0.25)))
        # Step 2
        C.add_box(bm_orn, arch_w - pillar_w - 0.8, depth*0.65, 0.5, loc @ Matrix.Translation((ax, 0, pillar_h - 0.75)))
        # Step 3
        C.add_box(bm_orn, arch_w - pillar_w - 1.6, depth*0.65, 0.5, loc @ Matrix.Translation((ax, 0, pillar_h - 1.25)))

    # Windows above arches
    win_z = pillar_h + lintel_h + 2.0
    win_h = 3.0
    win_w = arch_w * 0.5
    for i in [-1, 0, 1]:
        ax = i * arch_w
        # Frame
        C.add_box(bm_orn, win_w, depth*0.7, win_h, loc @ Matrix.Translation((ax, 0, win_z + win_h/2.0)))
    
    obj_orn = C.bm_to_object(bm_orn, f"{NAME}_{index}_ORN_VIS", collection, material_key=mat_orn)
    master_objs.append(obj_orn)
    
    # 4. Small Domes on Roof
    bm_dome = bmesh.new()
    dome_z = height + 1.0
    for i in [-1, 1]:
        dx = i * (width * 0.25)
        # Base
        C.add_capped_cone(bm_dome, 1.2, 1.2, 2.0, loc @ Matrix.Translation((dx, 0, dome_z + 1.0)), segments=12)
        # Dome
        C.add_capped_cone(bm_dome, 1.3, 0.0, 2.5, loc @ Matrix.Translation((dx, 0, dome_z + 2.0 + 1.25)), segments=12)
        # Finial
        C.add_capped_cone(bm_dome, 0.1, 0.1, 1.5, loc @ Matrix.Translation((dx, 0, dome_z + 4.5 + 0.75)), segments=8)
        
    obj_dome = C.bm_to_object(bm_dome, f"{NAME}_{index}_DOME_VIS", collection, material_key="DOME_ROOF")
    master_objs.append(obj_dome)
    
    return master_objs[0]


def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    
    gates = P.TRACE.get("MINARET_GATES", [])
    minarets = P.TRACE.get("MINARETS", [])
    
    h = GATE_PARAMS.get("HEIGHT", 25.0)
    d = GATE_PARAMS.get("DEPTH", 8.0)
    
    obj_ref = None
    
    for idx, (m1_idx, m2_idx) in enumerate(gates):
        if m1_idx >= len(minarets) or m2_idx >= len(minarets):
            continue
            
        p1 = minarets[m1_idx]
        p2 = minarets[m2_idx]
        
        # p1 and p2 can be tuples (x,y) or dicts {"cx":x, "cy":y}
        x1 = p1[0] if isinstance(p1, tuple) else p1["cx"]
        y1 = p1[1] if isinstance(p1, tuple) else p1["cy"]
        x2 = p2[0] if isinstance(p2, tuple) else p2["cx"]
        y2 = p2[1] if isinstance(p2, tuple) else p2["cy"]
        
        # Snap minaret coordinates using the exact same logic as comp_minarets
        regular_polys = [P.TRACE.get("OUTLINE_OUTER", []), P.STRUCTURE.get("OUTER_POLY", [])]
        x1, y1, _ = snap_to_polygons(x1, y1, regular_polys)
        x2, y2, _ = snap_to_polygons(x2, y2, regular_polys)
        
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        
        # Width is the distance between the two minarets minus their diameters
        # Minaret R_BASE is ~3.5m. We subtract 6.0m to leave a 0.5m overlap on each side.
        distance = math.hypot(x2 - x1, y2 - y1)
        width = max(10.0, distance - 6.0)
        
        # Angle of the gate (parallel to the line connecting the minarets)
        angle = math.atan2(y2 - y1, x2 - x1)
        
        obj = build_gate(collection, idx+1, cx, cy, width, angle, h, d)
        if obj_ref is None: obj_ref = obj
        
    return obj_ref

if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    build(coll)
    overall = "OK"
    for o in coll.objects:
        status, tris = C.validate(o, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
        if status == "FAIL":
            overall = "FAIL"
    print(f"{C.TAG} comp_gates OVERALL -> {overall}")
    if overall == "FAIL":
        raise SystemExit(1)
