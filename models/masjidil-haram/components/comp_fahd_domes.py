# models/masjidil-haram/components/comp_fahd_domes.py
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

NAME = "RUH_FAHD_DOME"
COLLECTION = "DOMES"
FAHD_PARAMS = getattr(P, "FAHD_DOMES", {})
TRI_CAP = FAHD_PARAMS.get("TARGET_TRI", 8000)

def build_dome(collection, index, cx, cy):
    # Parameters
    drum_r = FAHD_PARAMS.get("DRUM_R", 7.0)
    dome_r = FAHD_PARAMS.get("DOME_R", 8.5)
    dome_h = FAHD_PARAMS.get("DOME_H", 9.0)
    drum_h = FAHD_PARAMS.get("DRUM_H", 5.0)
    n_sides = FAHD_PARAMS.get("N_SIDES", 16)
    z_base = FAHD_PARAMS.get("Z_BASE", 24.0)
    
    mat_main = FAHD_PARAMS.get("MATERIAL", "MARBLE")
    mat_dome = "DOME_ROOF"
    mat_green = "GREEN"
    mat_orn = "BEIGE"
    
    loc = Matrix.Translation((cx, cy, z_base))
    master_objs = []
    
    # 1. Base Drum
    bm_drum = bmesh.new()
    C.add_capped_cone(bm_drum, drum_r, drum_r, drum_h, loc @ Matrix.Translation((0,0,0)), segments=n_sides)
    
    # Arched windows on drum
    # Instead of booleans, we just add decorative recessed arches to the drum surface
    arch_w = drum_r * math.pi / n_sides * 0.8
    for i in range(n_sides):
        angle = i * (2.0 * math.pi / n_sides)
        aloc = loc @ Matrix.Rotation(angle, 4, 'Z') @ Matrix.Translation((drum_r + 0.1, 0, 0))
        
        # Arch base
        C.add_box(bm_drum, 0.4, arch_w, drum_h * 0.7, aloc @ Matrix.Translation((0, 0, drum_h * 0.35)))
    
    obj_drum = C.bm_to_object(bm_drum, f"{NAME}_{index}_DRUM_VIS", collection, material_key=mat_orn)
    master_objs.append(obj_drum)
    
    # 2. Green Trim Ring
    bm_trim = bmesh.new()
    trim_h = 1.0
    C.add_capped_cone(bm_trim, drum_r + 0.4, drum_r + 0.2, trim_h, loc @ Matrix.Translation((0,0,drum_h)), segments=n_sides)
    obj_trim = C.bm_to_object(bm_trim, f"{NAME}_{index}_TRIM_VIS", collection, material_key=mat_green)
    master_objs.append(obj_trim)
    
    # 3. Ribbed Dome
    bm_dome = bmesh.new()
    dome_base_z = drum_h + trim_h
    
    # A low-poly dome (hemisphere-ish)
    n_lat = 8
    n_lon = 32
    verts = []
    verts.append(bm_dome.verts.new((0, 0, dome_base_z + dome_h))) # top vertex
    for i in range(1, n_lat + 1):
        phi = (math.pi / 2.0) * (i / n_lat)
        r = dome_r * math.sin(phi)
        z = dome_base_z + dome_h * math.cos(phi)
        for j in range(n_lon):
            theta = j * (2 * math.pi / n_lon)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            verts.append(bm_dome.verts.new((x, y, z)))
            
    bm_dome.verts.ensure_lookup_table()
    
    # top triangles
    for j in range(n_lon):
        v1 = verts[0]
        v2 = verts[1 + j]
        v3 = verts[1 + (j + 1) % n_lon]
        bm_dome.faces.new([v1, v2, v3])
        
    # quads
    for i in range(1, n_lat):
        row1 = 1 + (i - 1) * n_lon
        row2 = 1 + i * n_lon
        for j in range(n_lon):
            j_next = (j + 1) % n_lon
            v1 = verts[row1 + j]
            v2 = verts[row1 + j_next]
            v3 = verts[row2 + j_next]
            v4 = verts[row2 + j]
            bm_dome.faces.new([v1, v2, v3, v4])
            
    # bottom cap
    bottom_verts = [verts[-n_lon + j] for j in range(n_lon)]
    bottom_verts.reverse() # ensure normal faces downward
    bm_dome.faces.new(bottom_verts)
            
    bmesh.ops.transform(bm_dome, matrix=loc, verts=bm_dome.verts)
    
    obj_dome = C.bm_to_object(bm_dome, f"{NAME}_{index}_ROOF_VIS", collection, material_key=mat_dome)
    master_objs.append(obj_dome)
    
    # 4. Finial
    bm_finial = bmesh.new()
    fin_z = dome_base_z + dome_h
    C.add_capped_cone(bm_finial, 0.2, 0.2, 1.5, loc @ Matrix.Translation((0,0,fin_z)), segments=8)
    C.add_capped_cone(bm_finial, 0.4, 0.0, 1.5, loc @ Matrix.Translation((0,0,fin_z + 1.5)), segments=8)
    obj_finial = C.bm_to_object(bm_finial, f"{NAME}_{index}_FINIAL_VIS", collection, material_key="GOLD")
    master_objs.append(obj_finial)
    
    return master_objs[0]

def build(collection=None):
    collection = collection or C.reset_collection(COLLECTION)
    
    positions = FAHD_PARAMS.get("POSITIONS", [])
    
    obj_ref = None
    for idx, (x, y) in enumerate(positions):
        obj = build_dome(collection, idx+1, cx=x, cy=y)
        if obj_ref is None:
            obj_ref = obj
            
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
    print(f"{C.TAG} comp_fahd_domes OVERALL -> {overall}")
    if overall == "FAIL":
        raise SystemExit(1)
