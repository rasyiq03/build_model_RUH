# =====================================================================
#   KA'BAH PARAMETRIK DENGAN OTOMATISASI TEKSTUR GAMBAR
#   SKALA DUNIA NYATA (1 Blender unit = 1 meter)
#   Kompatibel Penuh untuk Export ke Roblox Studio
# =====================================================================

import bpy
import math
import os

# ---------------------------------------------------------------------
#   ALAMAT FOLDER TEKSTUR TUGAS BESAR (ONEDRIVE POLBAN)
# ---------------------------------------------------------------------
path_folder = "C:\\Users\\Devi Maulani\\OneDrive - Politeknik Negeri Bandung\\FOLDER DEVI MAULANI\\SEMESTER 4\\GITHUB\\tugas-besar-komputer-grafik-eas-roblox\\src\\assets\\MasjidilHaram\\textures\\"

# ---------------------------------------------------------------------
#   PARAMETER UTAMA (meter)
# ---------------------------------------------------------------------
CX, CY = 0.0, 0.0

BODY_L   = 11.90      
BODY_W   = 10.00      
BODY_H   = 13.10      
BODY_Z   = BODY_H / 2.0

BASE_MARGIN = 0.55
BASE_L   = BODY_L + 2 * BASE_MARGIN
BASE_W   = BODY_W + 2 * BASE_MARGIN
BASE_H   = 0.50
BASE_Z   = BASE_H / 2.0

KISWAH_MARGIN = 0.12
KISWAH_L  = BODY_L + 2 * KISWAH_MARGIN
KISWAH_W  = BODY_W + 2 * KISWAH_MARGIN
KISWAH_Z0 = 0.50      
KISWAH_Z1 = 14.00     

HIZAM_H  = 0.95       
HIZAM_Z  = 9.50       

FRONT_Y     = CY - BODY_W / 2.0
DOOR_W      = 1.71    
DOOR_H      = 3.18    
DOOR_X      = -1.50   
DOOR_BASE_Z = 2.13    
DOOR_FRAME  = 0.22    
DOOR_OUT    = 0.12    

CORNER_X = CX - BODY_L / 2.0
CORNER_Y = CY - BODY_W / 2.0
RING_X      = CORNER_X + 0.12
RING_Y      = CORNER_Y + 0.12
RING_Z      = 1.10    
RING_RINGS  = 26
RING_SEG    = 56
RING_INNER  = 0.11    
RING_OUTER  = 0.24    
RING_DEPTH  = 0.32
RING_POWER  = 1.35
RING_LIP    = 0.04

ORN_X    = CX + BODY_L / 2.0 - 1.8
ORN_Y    = FRONT_Y - 0.05
ORN_Z    = 1.30
ORN_R    = 0.08

# =====================================================================
#   FUNGSI MATERIAL OTOMATIS BERBASIS IMAGE TEXTURE (ROBLOX READY)
# =====================================================================
def add_material(obj, name, default_color, roughness=0.5, metallic=0.0):
    """Membuat material menggunakan Image Texture jika file ditemukan,
    jika tidak ada gambar, akan menggunakan warna default solid."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear() # Bersihkan agar node tidak menumpuk
    
    # Buat kerangka node standar Roblox
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    node_bsdf.location = (0, 0)
    node_output.location = (300, 0)
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    # Set properti fisik non-warna
    node_bsdf.inputs["Roughness"].default_value = roughness
    node_bsdf.inputs["Metallic"].default_value = metallic

    # Cari file gambar di folder berdasarkan NAMA OBJEK BLENDER
    nama_file = None
    for ext in [".png", ".jpg", ".jpeg"]:
        if os.path.exists(path_folder + obj.name + ext):
            nama_file = obj.name + ext
            break
            
    if nama_file:
        # Jika gambar ditemukan di folder OneDrive Anda
        full_path = path_folder + nama_file
        try:
            node_tex = nodes.new(type='ShaderNodeTexImage')
            node_tex.location = (-350, 0)
            img = bpy.data.images.load(full_path)
            node_tex.image = img
            # Hubungkan Gambar ke Base Color (Dibaca otomatis oleh 3D Importer Roblox)
            links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
            print(f"BERHASIL MENGHUBUNGKAN TEKSTUR: Objek '{obj.name}' -> File '{nama_file}'")
        except Exception as e:
            print(f"Gagal memuat file gambar {nama_file}, fallback ke warna solid. Error: {str(e)}")
            node_bsdf.inputs["Base Color"].default_value = default_color
    else:
        # Jika gambar belum ada, pakai nilai warna bawaan script lama
        node_bsdf.inputs["Base Color"].default_value = default_color
        print(f"Info: Tidak ada file gambar untuk '{obj.name}', menggunakan warna dasar.")
        
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return mat

def set_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

def apply_transform(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)

def add_bevel(obj, width=0.03, segments=2):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'

def new_box(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    apply_transform(obj)
    return obj

def make_funnel(name, location, num_rings, num_seg,
                r_inner, r_outer, depth, power=1.3, lip=0.1):
    verts = []
    for i in range(num_rings):
        u = i / (num_rings - 1)
        r = r_inner + (r_outer - r_inner) * (u ** power)
        z = -depth * (1.0 - u) ** 1.7
        z += lip * (u ** 4)
        for j in range(num_seg):
            ang = 2.0 * math.pi * j / num_seg
            verts.append((r * math.cos(ang), r * math.sin(ang), z))
    faces = []
    for i in range(num_rings - 1):
        for j in range(num_seg):
            a = i * num_seg + j
            b = i * num_seg + (j + 1) % num_seg
            c = (i + 1) * num_seg + (j + 1) % num_seg
            d = (i + 1) * num_seg + j
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return obj

# =====================================================================
#   EKSEKUSI PEMBENTUKAN DAN GENERASI NODE
# =====================================================================
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.data.objects):
    if o.type == 'MESH':
        o.select_set(True)
bpy.ops.object.delete()

# 1. Base_Shadharwan
base = new_box("Base_Shadharwan", (BASE_L, BASE_W, BASE_H), (CX, CY, BASE_Z))
add_bevel(base, width=0.06, segments=2)
add_material(base, "MarmerMat", (0.92, 0.91, 0.88, 1.0), roughness=0.35, metallic=0.0)

# 2. Badan_Kabah
body = new_box("Badan_Kabah", (BODY_L, BODY_W, BODY_H), (CX, CY, BODY_Z))
add_material(body, "BatuMat", (0.20, 0.20, 0.21, 1.0), roughness=0.85, metallic=0.0)

# 3. Kiswah & Hizam
kis_h = KISWAH_Z1 - KISWAH_Z0
kis_cz = (KISWAH_Z1 + KISWAH_Z0) / 2.0
kiswah = new_box("Kiswah", (KISWAH_L, KISWAH_W, kis_h), (CX, CY, kis_cz))
add_material(kiswah, "KiswahMat", (0.02, 0.02, 0.02, 1.0), roughness=0.7, metallic=0.0)
set_smooth(kiswah)

hizam = new_box("Hizam_SabukEmas", (KISWAH_L + 0.04, KISWAH_W + 0.04, HIZAM_H), (CX, CY, HIZAM_Z))
add_material(hizam, "GoldMat", (0.83, 0.66, 0.22, 1.0), roughness=0.3, metallic=0.9)
set_smooth(hizam)

# 4. Pintu Emas (Bingkai, Daun Pintu, Ambang)
door_cz = DOOR_BASE_Z + DOOR_H / 2.0
frame = new_box("Pintu_Bingkai", (DOOR_W, DOOR_OUT * 2.0, DOOR_H), (DOOR_X, FRONT_Y - DOOR_OUT, door_cz))
add_bevel(frame, width=0.03, segments=2)
add_material(frame, "GoldMat", (0.83, 0.66, 0.22, 1.0), roughness=0.25, metallic=0.95)
set_smooth(frame)

panel_w = (DOOR_W - DOOR_FRAME * 3.0) / 2.0
panel_h = DOOR_H - DOOR_FRAME * 2.0
for i, side in enumerate([-1, 1]):
    px = DOOR_X + side * (panel_w / 2.0 + DOOR_FRAME / 2.0)
    # Nama unik per objek agar bisa mendeteksi Pintu_Daun_Left atau Pintu_Daun_Right jika diperlukan terpisah
    suffix = "Left" if side == -1 else "Right"
    panel = new_box(f"Pintu_Daun_{suffix}", (panel_w, DOOR_OUT * 1.2, panel_h), (px, FRONT_Y - DOOR_OUT * 0.6, door_cz))
    add_bevel(panel, width=0.02, segments=2)
    add_material(panel, "GoldDarkMat", (0.55, 0.42, 0.13, 1.0), roughness=0.45, metallic=0.85)
    set_smooth(panel)

lintel = new_box("Pintu_Ambang", (DOOR_W + DOOR_FRAME, DOOR_OUT * 2.2, DOOR_FRAME * 1.4), (DOOR_X, FRONT_Y - DOOR_OUT * 1.1, DOOR_BASE_Z + DOOR_H + DOOR_FRAME * 0.4))
add_bevel(lintel, width=0.03, segments=2)
add_material(lintel, "GoldMat", (0.83, 0.66, 0.22, 1.0), roughness=0.25, metallic=0.95)
set_smooth(lintel)

# 5. Hajar al-Aswad
ring = make_funnel("Hajar_Aswad", location=(RING_X, RING_Y, RING_Z), num_rings=RING_RINGS, num_seg=RING_SEG, r_inner=RING_INNER, r_outer=RING_OUTER, depth=RING_DEPTH, power=RING_POWER, lip=RING_LIP)
ring.rotation_euler = (math.pi / 2, 0, -math.pi / 4)
apply_transform(ring)
add_material(ring, "SilverMat", (0.78, 0.78, 0.80, 1.0), roughness=0.2, metallic=1.0)
set_smooth(ring)

inward = (0.70711, 0.70711, 0.0)
stone_pos = (RING_X + inward[0] * RING_DEPTH * 0.70, RING_Y + inward[1] * RING_DEPTH * 0.70, RING_Z)
bpy.ops.mesh.primitive_uv_sphere_add(radius=RING_INNER * 1.2, segments=20, ring_count=12, location=stone_pos)
stone = bpy.context.active_object
stone.name = "Batu_Hitam"
apply_transform(stone)
add_material(stone, "BatuHitamMat", (0.02, 0.02, 0.02, 1.0), roughness=0.35, metallic=0.1)
set_smooth(stone)

# 6. Ornamen Kecil
bpy.ops.mesh.primitive_uv_sphere_add(radius=ORN_R, segments=24, ring_count=16, location=(ORN_X, ORN_Y, ORN_Z))
orn = bpy.context.active_object
orn.name = "Ornamen_Kecil"
orn.scale = (1.0, 0.6, 1.0)
apply_transform(orn)
add_material(orn, "OrnamenMat", (0.83, 0.66, 0.22, 1.0), roughness=0.3, metallic=0.9)
set_smooth(orn)

print("--- RE-SHADING SELESAI ---")