# ruh_common.py
# =============================================================================
# Shared helpers + VALIDATOR for every RUH component script.
# Every component builds geometry with these helpers so that "watertight",
# "no n-gons", "transforms frozen" hold BY CONSTRUCTION, and is checked by
# validate() before anything is considered done.
#
# Requires Blender 3.0+ (bmesh.ops.create_cone uses radius1/radius2).
# =============================================================================
import bpy
import bmesh
from mathutils import Matrix, Vector

TAG = "[RUH]"


# --- Scene / collection management (idempotent) ------------------------------
def reset_scene():
    """Wipe to an empty factory scene. Used by standalone component runs."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0


def reset_collection(name, parent=None):
    """Return a fresh, EMPTY collection. Re-running clears it first so every
    build is reproducible from a clean state (idempotent)."""
    coll = bpy.data.collections.get(name)
    if coll:
        for obj in list(coll.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll


# --- Primitive builders (all CLOSED -> watertight by construction) -----------
def add_capped_cone(bm, r1, r2, depth, matrix, segments=16):
    """Add a closed (capped) cone/cylinder to `bm`.
    r1 == r2 -> cylinder. matrix places/orients it (built centered on Z)."""
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r1, radius2=r2, depth=depth,
    )
    bmesh.ops.transform(bm, matrix=matrix, verts=res["verts"])
    return res["verts"]


def add_box(bm, sx, sy, sz, matrix):
    """Add a closed box (sx,sy,sz = full dimensions)."""
    res = bmesh.ops.create_cube(bm, size=1.0)
    scale = Matrix.Diagonal((sx, sy, sz, 1.0))
    bmesh.ops.transform(bm, matrix=matrix @ scale, verts=res["verts"])
    return res["verts"]


def segment_matrix(p_start, p_end):
    """Matrix that orients a Z-built primitive along the segment p_start->p_end,
    centered on its midpoint. Returns (matrix, length)."""
    a, b = Vector(p_start), Vector(p_end)
    d = b - a
    length = d.length
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    return Matrix.Translation((a + b) / 2.0) @ rot, length


# --- Finalize: turn a bmesh into a clean, game-ready object -------------------
def bm_to_object(bm, name, collection, material_key=None):
    """Merge doubles, de-n-gon, recalc normals, then write to an object whose
    transforms are already identity (frozen by construction)."""
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)

    if material_key:
        import PARAMETERS as P
        mat_name = P.MATERIALS.get(material_key, material_key)
        mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
        me.materials.append(mat)
    return obj


# --- VALIDATOR ----------------------------------------------------------------
def validate(obj, tri_cap, warn=None):
    """Assert the Roblox hard rules on one object. Prints a [RUH] line and
    returns (status, tri_count). status in {OK, WARN, FAIL}."""
    me = obj.data
    me.calc_loop_triangles()
    tris = len(me.loop_triangles)

    bm = bmesh.new()
    bm.from_mesh(me)
    open_edges  = sum(1 for e in bm.edges if len(e.link_faces) < 2)   # holes
    nonmanifold = sum(1 for e in bm.edges if len(e.link_faces) > 2)   # bad union
    ngons       = sum(1 for f in bm.faces if len(f.verts) > 4)
    bm.free()

    rot_ok   = all(abs(a) < 1e-6 for a in obj.rotation_euler)
    scale_ok = all(abs(s - 1.0) < 1e-6 for s in obj.scale)
    watertight = (open_edges == 0 and nonmanifold == 0)

    problems = []
    if tris > tri_cap:               problems.append(f"tri {tris}>{tri_cap}")
    if not watertight:               problems.append(f"open={open_edges} nonmanifold={nonmanifold}")
    if ngons:                        problems.append(f"ngons={ngons}")
    if not (rot_ok and scale_ok):    problems.append("transform not frozen")

    if problems:
        status = "FAIL"
    elif warn is not None and tris > warn:
        status = "WARN"
    else:
        status = "OK"

    print(f"{TAG} {status:4} {obj.name:34} tri={tris:5} watertight={watertight} ngons={ngons}")
    if problems:
        print(f"{TAG}      -> {'; '.join(problems)}")
    return status, tris
