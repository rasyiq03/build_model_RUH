# models/masjidil-haram/components/comp_minarets.py
import sys, os
import math
import bmesh
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MODEL_DIR))
if MODEL_DIR not in sys.path: sys.path.append(MODEL_DIR)
if ROOT not in sys.path: sys.path.append(ROOT)

import PARAMETERS as P
import ruh_common as C

def closest_point_on_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0: return x1, y1
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    return x1 + t * dx, y1 + t * dy

def snap_to_polygons(px, py, polygons):
    best_dist = float('inf')
    best_pt = (px, py)
    best_angle = 0.0
    for poly in polygons:
        for i in range(len(poly)):
            p1 = poly[i]
            p2 = poly[(i + 1) % len(poly)]
            qx, qy = closest_point_on_segment(px, py, p1[0], p1[1], p2[0], p2[1])
            d = (qx - px)**2 + (qy - py)**2
            if d < best_dist:
                best_dist = d
                best_pt = (qx, qy)
                best_angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    return best_pt[0], best_pt[1], best_angle

NAME       = "RUH_MINARET"
COLLECTION = "MINARETS"
TRI_CAP    = P.MINARETS["TARGET_TRI"]

def build_single_minaret(collection, index, x, y, H, R, suffix, rot_z=0.0):
    # Base location + rotation so the octagon faces align with the wall
    # create_cone's first vertex is at +X. We want a flat edge to align with rot_z.
    # The flat edge is at 22.5 degrees (pi/8) from the vertex.
    loc = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rot_z - (math.pi / 8), 4, 'Z')
    master_objs = []
    
    # --- BASE (Grey Marble) ---
    bm_base = bmesh.new()
    h_base = H * 0.25
    C.add_capped_cone(bm_base, R*1.2, R*1.2, h_base, loc @ Matrix.Translation((0, 0, h_base/2.0)), segments=8)
    obj_base = C.bm_to_object(bm_base, f"{NAME}_{index}_{suffix}_BASE_VIS", collection, material_key="MARBLE")
    master_objs.append(obj_base)
    
    # --- BODY (Beige Concrete/Stone) ---
    bm_body = bmesh.new()
    z = h_base
    h_trans = 2.0
    C.add_capped_cone(bm_body, R*1.2, R*1.0, h_trans, loc @ Matrix.Translation((0, 0, z+h_trans/2.0)), segments=8)
    z += h_trans
    
    h_balc1 = 1.0
    C.add_capped_cone(bm_body, R*1.5, R*1.5, h_balc1, loc @ Matrix.Translation((0, 0, z+h_balc1/2.0)), segments=8)
    z += h_balc1
    h_gap1 = 4.0
    C.add_capped_cone(bm_body, R*0.8, R*0.8, h_gap1, loc @ Matrix.Translation((0, 0, z+h_gap1/2.0)), segments=8)
    for j in range(8):
        angle = j * (math.pi / 4)
        px = math.cos(angle) * (R*1.3)
        py = math.sin(angle) * (R*1.3)
        C.add_capped_cone(bm_body, 0.15, 0.15, h_gap1, loc @ Matrix.Translation((px, py, z+h_gap1/2.0)), segments=8)
    z += h_gap1
    
    h_roof1 = 2.0
    z += h_roof1
    
    h_mid = H * 0.35
    C.add_capped_cone(bm_body, R*0.9, R*0.9, h_mid, loc @ Matrix.Translation((0,0,z+h_mid/2.0)), segments=8)
    z += h_mid
    
    h_balc2 = 1.0
    C.add_capped_cone(bm_body, R*1.4, R*1.4, h_balc2, loc @ Matrix.Translation((0,0,z+h_balc2/2.0)), segments=8)
    z += h_balc2
    h_gap2 = 3.5
    C.add_capped_cone(bm_body, R*0.7, R*0.7, h_gap2, loc @ Matrix.Translation((0,0,z+h_gap2/2.0)), segments=8)
    for j in range(8):
        angle = j * (math.pi / 4)
        px = math.cos(angle) * (R*1.2)
        py = math.sin(angle) * (R*1.2)
        C.add_capped_cone(bm_body, 0.15, 0.15, h_gap2, loc @ Matrix.Translation((px, py, z+h_gap2/2.0)), segments=8)
    z += h_gap2
    
    h_roof2 = 2.0
    z += h_roof2
    
    h_up = H - z - 12.0
    if h_up < 0: h_up = 10.0
    C.add_capped_cone(bm_body, R*0.7, R*0.7, h_up, loc @ Matrix.Translation((0,0,z+h_up/2.0)), segments=16)
    z += h_up
    
    C.add_capped_cone(bm_body, R*0.8, R*0.8, 1.0, loc @ Matrix.Translation((0,0,z+0.5)), segments=16)
    z += 1.0
    
    obj_body = C.bm_to_object(bm_body, f"{NAME}_{index}_{suffix}_BODY_VIS", collection, material_key="CONCRETE")
    master_objs.append(obj_body)
    
    # --- ROOFS (Green) ---
    bm_roof = bmesh.new()
    z_r = h_base + h_trans + h_balc1 + h_gap1
    C.add_capped_cone(bm_roof, R*1.6, R*1.0, h_roof1, loc @ Matrix.Translation((0,0,z_r+h_roof1/2.0)), segments=8)
    
    z_r += h_roof1 + h_mid + h_balc2 + h_gap2
    C.add_capped_cone(bm_roof, R*1.5, R*0.9, h_roof2, loc @ Matrix.Translation((0,0,z_r+h_roof2/2.0)), segments=8)
    
    z_r = z
    h_dome = 6.0
    C.add_capped_cone(bm_roof, R*0.8, 0.0, h_dome, loc @ Matrix.Translation((0,0,z_r+h_dome/2.0)), segments=16)
    z_r += h_dome
    
    obj_roof = C.bm_to_object(bm_roof, f"{NAME}_{index}_{suffix}_ROOF_VIS", collection, material_key="DOME_ROOF")
    master_objs.append(obj_roof)
    
    # --- FINIAL (Gold) ---
    bm_finial = bmesh.new()
    h_fin = 5.0
    C.add_capped_cone(bm_finial, 0.1, 0.1, h_fin, loc @ Matrix.Translation((0,0,z_r+h_fin/2.0)), segments=8)
    C.add_capped_cone(bm_finial, 0.4, 0.4, 0.8, loc @ Matrix.Translation((0,0,z_r+h_fin)), segments=8)
    obj_finial = C.bm_to_object(bm_finial, f"{NAME}_{index}_{suffix}_FINIAL_VIS", collection, material_key="GOLD")
    master_objs.append(obj_finial)
    
    return master_objs[0]

def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    
    # From image and reality:
    # Regular Minarets: ~89m tall, narrower base
    # Abdullah Minarets: ~135m tall, massive wider base
    
    H_REGULAR = 89.0
    R_REGULAR = 3.0
    
    H_ABDULLAH = P.ABDULLAH_EXPANSION.get("MINARET_H", 135.0)
    R_ABDULLAH = 6.0
    
    # 1. Regular minarets (first 11 from TRACE)
    trace_minarets = P.TRACE.get("MINARETS", [])
    regular_positions = trace_minarets[:11]
    
    # 2. Abdullah minarets
    abdullah_positions = []
    for p in P.ABDULLAH_EXPANSION.get("MINARETS", []):
        abdullah_positions.append((p["cx"], p["cy"]))
        
    obj_ref = None
    idx = 1
    
    # Build regular minarets, snapping them to the main walls
    regular_polys = [P.TRACE.get("OUTLINE_OUTER", []), P.STRUCTURE.get("OUTER_POLY", [])]
    for (x, y) in regular_positions:
        sx, sy, angle = snap_to_polygons(x, y, regular_polys)
        obj = build_single_minaret(collection, idx, sx, sy, H_REGULAR, R_REGULAR, "REG", rot_z=angle)
        if obj_ref is None: obj_ref = obj
        idx += 1
        
    # Build Abdullah minarets, snapping them to the Abdullah expansion walls
    abdullah_polys = [P.ABDULLAH_EXPANSION.get("POLY_OUTER", [])]
    for (x, y) in abdullah_positions:
        sx, sy, angle = snap_to_polygons(x, y, abdullah_polys)
        # Khusus minaret di corner, adjust posisinya sedikit ke dalam / pas di edge tengah jika perlu.
        # Atau biarkan di sx,sy tapi rotasinya presisi mengikuti angle dinding.
        obj = build_single_minaret(collection, idx, sx, sy, H_ABDULLAH, R_ABDULLAH, "ABD", rot_z=angle)
        if obj_ref is None: obj_ref = obj
        idx += 1

    return obj_ref

if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    overall = "OK"
    for o in coll.objects:
        status, tris = C.validate(o, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
        if status == "FAIL":
            overall = "FAIL"
    print(f"{C.TAG} comp_minarets OVERALL -> {overall}")
    if overall == "FAIL":
        raise SystemExit(1)
