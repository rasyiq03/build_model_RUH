# _dev_render.py — TEMP dev tool: build the model and render assessment views.
# Not part of the model pipeline; safe to delete. Renders top + perspective PNGs
# into models/jamarat/_dev_renders/ for visual fidelity assessment vs references/.
# Run: blender --background --factory-startup --python models/jamarat/_dev_render.py
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path += [HERE, os.path.join(HERE, "components"), ROOT]

import bpy
from mathutils import Vector
import generate_jamarat as base

OUT = os.path.join(HERE, "_dev_renders")
os.makedirs(OUT, exist_ok=True)


def _frame_all(cam, target, distance, elev_deg, azim_deg):
    """Place camera at spherical offset from target, looking at it."""
    e = math.radians(elev_deg)
    a = math.radians(azim_deg)
    cam.location = Vector((
        target.x + distance * math.cos(e) * math.cos(a),
        target.y + distance * math.cos(e) * math.sin(a),
        target.z + distance * math.sin(e),
    ))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def main():
    base.build(textured=True)
    scene = bpy.context.scene

    # world light
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("W"); scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.55, 0.7, 0.95, 1.0)
    bg.inputs[1].default_value = 1.0

    # sun
    sun_data = bpy.data.lights.new("Sun", 'SUN'); sun_data.energy = 4.0
    sun = bpy.data.objects.new("Sun", sun_data); scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(20), math.radians(30))

    # compute scene bounds
    mins = Vector(( 1e9,  1e9,  1e9)); maxs = Vector((-1e9, -1e9, -1e9))
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            mins = Vector((min(mins.x, w.x), min(mins.y, w.y), min(mins.z, w.z)))
            maxs = Vector((max(maxs.x, w.x), max(maxs.y, w.y), max(maxs.z, w.z)))
    center = (mins + maxs) / 2.0
    size = (maxs - mins)
    print("[DEV] bounds min=%s max=%s size=%s" % (
        tuple(round(v,1) for v in mins), tuple(round(v,1) for v in maxs),
        tuple(round(v,1) for v in size)))

    cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
    cam_data.clip_start = 1.0
    cam_data.clip_end = 12000.0
    scene.collection.objects.link(cam); scene.camera = cam

    span = max(size.x, size.y, size.z)

    # (name, elev, azim, dist, ortho, resx, resy, ortho_scale, target_override)
    canopy_c = Vector((0.0, 0.0, 60.0))   # spine canopy row center
    views = [
        ("top",     89.9, 0.0,   span * 1.2, True,  1000, 1600, size.y * 1.12, None),
        ("persp",   30.0, 35.0,  span * 0.9, False, 1600, 1000, None,          None),
        ("side",    6.0,  90.0,  span * 0.8, False, 1600,  700, None,          None),
        ("canopy",  89.9, 0.0,   600.0,      True,  1400, 1400, 520.0,         canopy_c),
        ("canopy3d",38.0, 20.0,  620.0,      False, 1600, 1000, None,          canopy_c),
    ]
    for name, elev, azim, dist, ortho, rx, ry, oscale, tgt in views:
        scene.render.resolution_x = rx
        scene.render.resolution_y = ry
        cam_data.type = 'ORTHO' if ortho else 'PERSP'
        if ortho:
            cam_data.ortho_scale = oscale
        cam_data.lens = 50
        _frame_all(cam, tgt if tgt is not None else center, dist, elev, azim)
        scene.render.filepath = os.path.join(OUT, "view_%s.png" % name)
        bpy.ops.render.render(write_still=True)
        print("[DEV] wrote", scene.render.filepath)


if __name__ == "__main__":
    main()
