# =====================================================================
#   TEXTURING OTOMATIS MASJIDIL HARAM
#   Berbasis sinkronisasi nama objek dengan file gambar (.png/.jpg)
# =====================================================================

import bpy
import os

# Alamat folder tekstur khusus Masjidil Haram.
path_folder = r"C:\Users\Devi Maulani\OneDrive - Politeknik Negeri Bandung\FOLDER DEVI MAULANI\SEMESTER 4\GITHUB\BUILD WORLD\build_model_RUH\build_model_RUH\models\masjidil-haram\references\texture"
path_folder = path_folder + "\\"

def apply_auto_textures():
    print("=== MULAI PROSES TEXTURING OTOMATIS MASJIDIL HARAM ===")
    
    # Pastikan string folder path valid
    if not os.path.exists(path_folder):
        print(f"Folder tekstur tidak ditemukan: {path_folder}")
        print("Silakan edit variabel 'path_folder' di dalam script ini agar mengarah ke folder yang benar.")
        return
        
    found_count = 0
    
    # Loop semua objek bertipe Mesh di dalam Blender
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            # Cari file gambar yang namanya sama dengan nama objek
            nama_file = None
            full_path = None
            
            for ext in [".png", ".jpg", ".jpeg"]:
                test_path = os.path.join(path_folder, obj.name + ext)
                if os.path.exists(test_path):
                    nama_file = obj.name + ext
                    full_path = test_path
                    break
            
            # Jika tidak ketemu nama persis, tapi ini adalah objek dinding (WALL)
            if not full_path and "WALL" in obj.name:
                test_path = os.path.join(path_folder, "RUH_DINDING.png")
                if os.path.exists(test_path):
                    nama_file = "RUH_DINDING.png"
                    full_path = test_path
            
            if full_path:
                print(f"✔ Mengaplikasikan tekstur: {obj.name} -> {nama_file}")
                found_count += 1
                
                # Buat material baru yang unik untuk objek ini
                mat_name = f"MAT_{obj.name}"
                mat = bpy.data.materials.get(mat_name)
                if not mat:
                    mat = bpy.data.materials.new(mat_name)
                
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                nodes.clear() # Bersihkan node yang ada agar tidak menumpuk
                
                node_output = nodes.new(type='ShaderNodeOutputMaterial')
                node_output.location = (300, 0)
                
                node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                node_bsdf.location = (0, 0)
                
                # Setup properti standar
                node_bsdf.inputs["Roughness"].default_value = 0.5
                node_bsdf.inputs["Metallic"].default_value = 0.0
                
                links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
                
                try:
                    node_tex = nodes.new(type='ShaderNodeTexImage')
                    node_tex.location = (-350, 0)
                    
                    # Muat gambar atau gunakan yang sudah ada di memory
                    img = bpy.data.images.get(nama_file)
                    if not img:
                        img = bpy.data.images.load(full_path)
                    
                    node_tex.image = img
                    
                    # Hubungkan Texture ke Base Color
                    links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
                    
                    # Terapkan material ke objek
                    if len(obj.data.materials) == 0:
                        obj.data.materials.append(mat)
                    else:
                        obj.data.materials[0] = mat # Ganti material pertama
                        
                except Exception as e:
                    print(f"Error memuat tekstur {nama_file}: {e}")

    print(f"=== SELESAI! Berhasil memasang {found_count} tekstur otomatis ===")

if __name__ == "__main__":
    apply_auto_textures()
