# =============================================================================
# Import the rough Tripo OBJ, recenter, and render TOP/FRONT/SIDE ortho caps
# (workbench, fast) so the AI massing can be used as a shape reference and
# cross-checked vs the calibrated oval. Output -> References/rough_ortho/*.png
# =============================================================================
import os, sys, math, bpy
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OBJ = os.path.join(ROOT, "References", "architectural+complex+3d+model",
                   "tripo_convert_49361f4a-1fc0-477c-93f6-309213489219.obj")
OUTDIR = os.path.join(ROOT, "References", "rough_ortho")
os.makedirs(OUTDIR, exist_ok=True)

# clean scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

print("[ROUGH] importing", os.path.basename(OBJ))
bpy.ops.wm.obj_import(filepath=OBJ)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print(f"[ROUGH] imported {len(objs)} mesh objects")
obj = objs[0]

# recenter to origin, get dims
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
obj.location = (0, 0, 0)
dx, dy, dz = obj.dimensions
print(f"[ROUGH] dims X={dx:.3f} Y={dy:.3f} Z={dz:.3f}")
maxd = max(dx, dy, dz)

# workbench render settings
scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
scn.render.resolution_x = 900; scn.render.resolution_y = 900
scn.render.film_transparent = True
try:
    scn.display.shading.light = "MATCAP"
    scn.display.shading.show_cavity = True
except Exception as e:
    print("[ROUGH] shading note:", e)

cam_data = bpy.data.cameras.new("orthocam"); cam_data.type = "ORTHO"
cam_data.ortho_scale = maxd * 1.15
cam = bpy.data.objects.new("orthocam", cam_data)
scn.collection.objects.link(cam); scn.camera = cam

views = {
    "top":   ((0, 0, maxd*2),  (0, 0, 0)),
    "front": ((0, -maxd*2, 0), (math.radians(90), 0, 0)),
    "side":  ((maxd*2, 0, 0),  (math.radians(90), 0, math.radians(90))),
}
for name, (loc, rot) in views.items():
    cam.location = loc; cam.rotation_euler = rot
    scn.render.filepath = os.path.join(OUTDIR, f"rough_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[ROUGH] wrote rough_{name}.png")
print("[ROUGH] DONE")
