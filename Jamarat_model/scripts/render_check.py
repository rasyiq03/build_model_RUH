# Load the assembled model and render aerial / top / ground views for sanity.
import os, math, bpy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "state", "jamarat_full.blend"))
OUT = os.path.join(ROOT, "renders"); os.makedirs(OUT, exist_ok=True)

scn = bpy.context.scene
scn.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "RenderEngineEeveeNext") else "BLENDER_WORKBENCH"
try:
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "MATERIAL"
except Exception as e:
    print("shade note", e)
scn.render.resolution_x = 1280; scn.render.resolution_y = 720
scn.render.film_transparent = False
scn.world.color = (0.6, 0.7, 0.85) if scn.world else None

cam_d = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cam_d)
scn.collection.objects.link(cam); scn.camera = cam

def look_at(loc, tgt=(0, 0, 30)):
    import mathutils
    d = mathutils.Vector(tgt) - mathutils.Vector(loc)
    cam.location = loc
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

views = {
    "aerial": (300, -430, 230),
    "deck": (90, -120, 60),         # solid deck surface + jamrah wall
    "flyover": (40, -620, 40),      # end-on: flyover roads ramping down to ground
    "userview": (260, -560, 250),   # match user's screenshot angle (deck edge + ramps)
}
cam_d.lens = 35
TGT = {"deck": (0, -40, 30), "flyover": (0, -350, 8), "userview": (0, -300, 20)}
for name, loc in views.items():
    look_at(loc, TGT.get(name, (0, 0, 35)))
    scn.render.filepath = os.path.join(OUT, f"check_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("[JMR] wrote", name)

# top ortho (full)
cam_d.type = "ORTHO"; cam_d.ortho_scale = 760
cam.location = (0, 0, 900); cam.rotation_euler = (0, 0, 0)
scn.render.filepath = os.path.join(OUT, "check_top.png")
bpy.ops.render.render(write_still=True)
print("[JMR] wrote top")

# top ortho with ROOF + TOWERS + GROUND hidden -> verify the traced footprint
scn.world.color = (0.05, 0.05, 0.08)
for cn in ("JMR_ROOF", "JMR_TOWERS", "JMR_GROUND"):
    c = bpy.data.collections.get(cn)
    if c:
        for o in c.objects:
            o.hide_render = True
# show only the TOP floor so the silhouette reads cleanly
fl = bpy.data.collections.get("JMR_FLOORS")
if fl:
    for o in fl.objects:
        if not o.name.endswith("L5_VIS"):
            o.hide_render = True
scn.render.filepath = os.path.join(OUT, "check_top_plan.png")
bpy.ops.render.render(write_still=True)
print("[JMR] wrote top_plan; DONE")
