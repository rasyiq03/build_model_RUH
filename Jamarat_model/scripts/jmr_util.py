# =============================================================================
# jmr_util.py — shared helpers for the Jamarat Blender pipeline (bpy, headless).
# Scene reset, collection tree (AGENTS §5), object linking, and the per-mesh
# validator (AGENTS §3 / blender-validate skill). Imported by every script_NN.
# =============================================================================
import os, sys, math
import bpy, bmesh
from mathutils import Vector

# --- make PARAMETERS.py (repo root) importable from any script -----------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import PARAMETERS as P  # noqa: E402

PARAMS = P.PARAMS

# Collection tree (AGENTS §5)
VISUAL_COLLS = ["FLOORS", "COLUMNS", "RAMPS", "PILLARS", "TOWERS",
                "ROOF", "GROUND", "FURNITURE", "BACKGROUND"]
COLLISION_COLLS = ["COL_FLOORS", "COL_RAMPS", "COL_PILLARS", "COL_WALLS"]


# ----------------------------------------------------------------- scene -----
def reset_scene():
    """Factory-clean the scene: delete all objects + purge orphan data."""
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for b in list(block):
            if b.users == 0:
                block.remove(b)
    set_units()


def set_units():
    scn = bpy.context.scene
    scn.unit_settings.system = "METRIC"
    scn.unit_settings.scale_length = 1.0
    scn.unit_settings.length_unit = "METERS"


# ------------------------------------------------------------ collections ----
def get_or_create_collection(name, parent=None):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    parent_coll = parent if parent is not None else bpy.context.scene.collection
    if coll.name not in [c.name for c in parent_coll.children]:
        # avoid double-link
        already = any(coll.name in [c.name for c in p.children]
                      for p in bpy.data.collections) or \
                  coll.name in [c.name for c in bpy.context.scene.collection.children]
        if not already:
            parent_coll.children.link(coll)
    return coll


def build_collection_tree():
    """Create JMR_ROOT/{VISUAL,COLLISION}/... and return a name->collection map."""
    root = get_or_create_collection("JMR_ROOT")
    visual = get_or_create_collection("VISUAL", root)
    collision = get_or_create_collection("COLLISION", root)
    out = {"JMR_ROOT": root, "VISUAL": visual, "COLLISION": collision}
    for n in VISUAL_COLLS:
        out[n] = get_or_create_collection("JMR_" + n, visual)
    for n in COLLISION_COLLS:
        out[n] = get_or_create_collection("JMR_" + n, collision)
    return out


def link_to(obj, coll):
    """Unlink obj from all collections and link only into coll."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


def clear_collection(coll):
    """Remove all objects currently in coll (idempotent rebuild)."""
    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


# -------------------------------------------------------------- transforms ---
def apply_transforms(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def recalc_normals_outside(obj):
    me = obj.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free(); me.update()


def merge_doubles(obj, dist=1e-4):
    me = obj.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(me); bm.free(); me.update()


# -------------------------------------------------------------- validation ---
def tri_count(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def validate(obj, want_volume=True, want_frozen=True, verbose=True):
    """Per-mesh validation (AGENTS §3). Returns report dict; prints one line."""
    me = obj.data
    tris = tri_count(me)
    ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)

    bm = bmesh.new(); bm.from_mesh(me)
    open_edges = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-7)
    bm.free()

    dims = obj.dimensions
    has_vol = (min(dims) > 1e-4) and (len(me.polygons) > 0)

    s = obj.scale; r = obj.rotation_euler
    frozen = (all(abs(v - 1.0) < 1e-4 for v in s) and
              all(abs(v) < 1e-4 for v in r))

    cap = PARAMS["POLY_LIMIT_PER_MESH"]; warn = PARAMS["POLY_WARN_THRESHOLD"]
    fails = []
    if tris > cap: fails.append(f"tris={tris}>{cap}")
    if ngons: fails.append(f"ngons={ngons}")
    if open_edges: fails.append(f"open_edges={open_edges}")
    if degenerate: fails.append(f"degenerate={degenerate}")
    if want_volume and not has_vol: fails.append("no_volume")
    if want_frozen and not frozen: fails.append("xform_not_frozen")

    status = "FAIL" if fails else ("WARN" if tris > warn else "OK")
    rep = {"name": obj.name, "tris": tris, "ngons": ngons,
           "open_edges": open_edges, "degenerate": degenerate,
           "has_volume": has_vol, "frozen": frozen,
           "status": status, "fails": fails}
    if verbose:
        if fails:
            print(f"[JMR] {status} {obj.name:<34} " + " ".join(fails))
        else:
            print(f"[JMR] {status}   {obj.name:<34} tris={tris} manifold=1 "
                  f"ngon=0 vol={int(has_vol)} xform={int(frozen)}")
    return rep


def validate_all(objs, **kw):
    reps = [validate(o, **kw) for o in objs]
    n_fail = sum(1 for r in reps if r["status"] == "FAIL")
    print(f"[JMR] VALIDATE: {len(reps)} meshes, "
          f"{sum(1 for r in reps if r['status']=='OK')} OK, "
          f"{sum(1 for r in reps if r['status']=='WARN')} WARN, {n_fail} FAIL")
    return n_fail == 0, reps


# --------------------------------------------------------- geometry prims ---
def _new_mesh_obj(name, coll):
    me = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    return obj, me


def _finalize(obj, merge=True):
    """Merge doubles, kill degenerate faces, recalc normals out, set origin, freeze."""
    if merge:
        merge_doubles(obj)
    recalc_normals_outside(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.update()
    return obj


def ring_xyz(ring_xy, z):
    return [(x, y, z) for (x, y) in ring_xy]


def ellipse_xy(a_y, b_x, n=48, cx=0.0, cy=0.0, rot_deg=0.0):
    """Ellipse ring in XY, long axis a_y along Y, b_x along X, optional rotation."""
    th = math.radians(rot_deg); c, s = math.cos(th), math.sin(th)
    out = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        x = b_x * math.cos(t); y = a_y * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def loft_rings(name, bottom, top, coll, cap_bottom=True, cap_top=True, merge=True):
    """Build a closed solid between two equal-length 3D rings (lists of (x,y,z)).
    Side faces = quads; caps = triangle fan to a center vert (no n-gons)."""
    assert len(bottom) == len(top), "rings must match length"
    n = len(bottom)
    verts = list(bottom) + list(top)          # 0..n-1 bottom, n..2n-1 top
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))    # side quad
    if cap_bottom:
        cb = len(verts)
        verts.append((sum(p[0] for p in bottom) / n,
                      sum(p[1] for p in bottom) / n,
                      sum(p[2] for p in bottom) / n))
        for i in range(n):
            j = (i + 1) % n
            faces.append((cb, j, i))          # downward fan
    if cap_top:
        ct = len(verts)
        verts.append((sum(p[0] for p in top) / n,
                      sum(p[1] for p in top) / n,
                      sum(p[2] for p in top) / n))
        for i in range(n):
            j = (i + 1) % n
            faces.append((ct, n + i, n + j))  # upward fan
    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(verts, [], faces); me.update()
    return _finalize(obj, merge=merge)


def annulus_slab(name, outer_xy, inner_xy, z0, z1, coll, merge=True):
    """Watertight annular slab between outer ring and inner (void) ring, z0..z1.
    z0/z1 may be floats or callables f(x,y) (for sloped slabs/railings)."""
    n = len(outer_xy)
    assert len(inner_xy) == n, "outer/inner ring count must match"
    zb = z0 if callable(z0) else (lambda x, y: z0)
    zt = z1 if callable(z1) else (lambda x, y: z1)
    OT = [(x, y, zt(x, y)) for (x, y) in outer_xy]
    IT = [(x, y, zt(x, y)) for (x, y) in inner_xy]
    OB = [(x, y, zb(x, y)) for (x, y) in outer_xy]
    IB = [(x, y, zb(x, y)) for (x, y) in inner_xy]
    verts = OT + IT + OB + IB                 # blocks of n
    o = 0; it = n; ob = 2 * n; ib = 3 * n
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((o + i, o + j, it + j, it + i))     # top ring
        faces.append((ob + i, ib + i, ib + j, ob + j))   # bottom ring
        faces.append((o + i, ob + i, ob + j, o + j))     # outer wall
        faces.append((it + i, it + j, ib + j, ib + i))   # inner wall
    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(verts, [], faces); me.update()
    return _finalize(obj, merge=merge)


def ribbon_solid(name, left, right, thickness, coll, merge=True):
    """Swept solid slab between two edge polylines left/right (lists of (x,y,z),
    equal length). Gives the ramp/connector real volume (thickness downward)."""
    n = len(left)
    assert len(right) == n and n >= 2
    tl = list(left); tr = list(right)
    bl = [(x, y, z - thickness) for (x, y, z) in left]
    br = [(x, y, z - thickness) for (x, y, z) in right]
    verts = tl + tr + bl + br                 # blocks of n
    TL, TR, BL, BR = 0, n, 2 * n, 3 * n
    faces = []
    for i in range(n - 1):
        faces.append((TL+i, TR+i, TR+i+1, TL+i+1))      # top
        faces.append((BL+i, BL+i+1, BR+i+1, BR+i))      # bottom
        faces.append((TL+i, TL+i+1, BL+i+1, BL+i))      # left wall
        faces.append((TR+i, BR+i, BR+i+1, TR+i+1))      # right wall
    faces.append((TL, BL, BR, TR))                      # start cap
    faces.append((TL+n-1, TR+n-1, BR+n-1, BL+n-1))      # end cap
    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(verts, [], faces); me.update()
    return _finalize(obj, merge=merge)


def offset_polygon(poly, d):
    """Inward offset (d>0) of a CCW polygon, preserving vertex count.
    Approximate (vertex-normal method); fine for small d on smooth outlines."""
    n = len(poly)
    out = []
    for i in range(n):
        x0, y0 = poly[(i - 1) % n]
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        # left normals of the two edges (CCW -> inward is left)
        e1 = (x1 - x0, y1 - y0); e2 = (x2 - x1, y2 - y1)
        n1 = (-e1[1], e1[0]); n2 = (-e2[1], e2[0])
        def norm(v):
            L = math.hypot(*v) or 1.0
            return (v[0] / L, v[1] / L)
        n1 = norm(n1); n2 = norm(n2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        L = math.hypot(bx, by) or 1.0
        out.append((x1 + d * bx / L, y1 + d * by / L))
    return out


def signed_area(poly):
    s = 0.0; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return 0.5 * s


def point_in_poly(poly, x, y):
    n = len(poly); inside = False; j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def polygon_slab(name, outer_xy, holes_xy, z0, z1, coll, merge=True):
    """Watertight solid slab from an outer loop + hole loops (the TRACED abstract
    footprint). Top & bottom filled via bmesh triangle_fill (no verts added);
    boundary + each hole bridged into vertical walls. No boolean."""
    loops = [list(outer_xy)] + [list(h) for h in holes_xy]
    counts = [len(l) for l in loops]

    # triangulate the planar polygon-with-holes once on a scratch bmesh.
    sb = bmesh.new()
    rings = []
    for loop in loops:
        ring = [sb.verts.new((x, y, 0.0)) for (x, y) in loop]
        rings.append(ring)
    edges = []
    for ring in rings:
        for i in range(len(ring)):
            edges.append(sb.edges.new((ring[i], ring[(i + 1) % len(ring)])))
    bmesh.ops.triangle_fill(sb, use_beauty=True, use_dissolve=False, edges=edges)
    idx = {v: k for k, v in enumerate(sb.verts)}          # boundary verts first, in order
    pts2d = [(v.co.x, v.co.y) for v in sb.verts]
    tris = [tuple(idx[v] for v in f.verts) for f in sb.faces]
    sb.free()

    nb = len(pts2d)
    zb = z0 if callable(z0) else (lambda x, y: z0)
    zt = z1 if callable(z1) else (lambda x, y: z1)
    verts = [(x, y, zb(x, y)) for (x, y) in pts2d] + [(x, y, zt(x, y)) for (x, y) in pts2d]
    faces = []
    for (a, b, c) in tris:
        faces.append((a, c, b))                  # bottom cap (normal down)
        faces.append((nb + a, nb + b, nb + c))   # top cap (normal up)
    start = 0                                     # side walls per loop
    for cnt in counts:
        for i in range(cnt):
            a = start + i; b = start + (i + 1) % cnt
            faces.append((a, b, nb + b, nb + a))
        start += cnt

    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(verts, [], faces); me.update()
    return _finalize(obj, merge=merge)


def box(name, cx, cy, cz, sx, sy, sz, coll):
    """Axis-aligned box centered at (cx,cy,cz) with full sizes sx,sy,sz."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [(cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
         (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
         (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
         (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz)]
    f = [(0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(v, [], f); me.update()
    return _finalize(obj, merge=False)


def _norm(v):
    L = math.sqrt(sum(c*c for c in v)) or 1.0
    return (v[0]/L, v[1]/L, v[2]/L)


def strut(name, p0, p1, r, coll, n=8):
    """Closed cylinder (real volume) between two 3D points p0,p1 — masts/cables/spokes."""
    d = _norm((p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]))
    ref = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    u = _norm((d[1]*ref[2]-d[2]*ref[1], d[2]*ref[0]-d[0]*ref[2], d[0]*ref[1]-d[1]*ref[0]))
    v = (d[1]*u[2]-d[2]*u[1], d[2]*u[0]-d[0]*u[2], d[0]*u[1]-d[1]*u[0])
    bot, top = [], []
    for i in range(n):
        a = 2*math.pi*i/n; c, s = math.cos(a), math.sin(a)
        off = (r*(c*u[0]+s*v[0]), r*(c*u[1]+s*v[1]), r*(c*u[2]+s*v[2]))
        bot.append((p0[0]+off[0], p0[1]+off[1], p0[2]+off[2]))
        top.append((p1[0]+off[0], p1[1]+off[1], p1[2]+off[2]))
    return loft_rings(name, bot, top, coll)


def torus(name, cx, cy, cz, R, rt, coll, seg=32, tseg=10):
    """Watertight torus (quads) — oculus ring."""
    verts = []; faces = []
    for i in range(seg):
        A = 2*math.pi*i/seg; ca, sa = math.cos(A), math.sin(A)
        for j in range(tseg):
            B = 2*math.pi*j/tseg
            rr = R + rt*math.cos(B)
            verts.append((cx + rr*ca, cy + rr*sa, cz + rt*math.sin(B)))
    for i in range(seg):
        for j in range(tseg):
            a = i*tseg + j; b = ((i+1) % seg)*tseg + j
            a2 = i*tseg + (j+1) % tseg; b2 = ((i+1) % seg)*tseg + (j+1) % tseg
            faces.append((a, b, b2, a2))
    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(verts, [], faces); me.update()
    return _finalize(obj)


def cylinder(name, cx, cy, r_bot, r_top, z0, z1, coll, n=48):
    """Closed cylinder/frustum: loft circle(r_bot)@z0 to circle(r_top)@z1."""
    bot = [(cx + r_bot*math.cos(2*math.pi*i/n), cy + r_bot*math.sin(2*math.pi*i/n), z0)
           for i in range(n)]
    top = [(cx + r_top*math.cos(2*math.pi*i/n), cy + r_top*math.sin(2*math.pi*i/n), z1)
           for i in range(n)]
    return loft_rings(name, bot, top, coll)


def ellipse_perimeter(a, b):
    h = ((a - b) / (a + b)) ** 2
    return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))


def sample_ellipse_spacing(a_y, b_x, spacing, cx=0.0, cy=0.0, rot_deg=0.0, min_n=8):
    n = max(min_n, int(round(ellipse_perimeter(a_y, b_x) / spacing)))
    return ellipse_xy(a_y, b_x, n=n, cx=cx, cy=cy, rot_deg=rot_deg)


def multi_box_mesh(name, specs, coll):
    """One mesh containing many axis-aligned boxes. specs = [(cx,cy,cz,sx,sy,sz,rotz)]."""
    verts = []; faces = []
    for sp in specs:
        cx, cy, cz, sx, sy, sz = sp[:6]
        rotz = sp[6] if len(sp) > 6 else 0.0
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        c, s = math.cos(rotz), math.sin(rotz)
        base = len(verts)
        local = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
                 (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
        for lx, ly, lz in local:
            verts.append((cx + lx*c - ly*s, cy + lx*s + ly*c, cz + lz))
        for a,b2,c2,d in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
            faces.append((base+a, base+b2, base+c2, base+d))
    obj, me = _new_mesh_obj(name, coll)
    me.from_pydata(verts, [], faces); me.update()
    return _finalize(obj, merge=False)


def join_objects(objs, name, coll):
    """Join a list of objects into one mesh object named `name`."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    merged = bpy.context.view_layer.objects.active
    merged.name = name
    merged.data.name = name
    return _finalize(merged, merge=False)


def duplicate_linked(obj, name, location, coll, rot_z=0.0):
    """Instance (linked mesh data) of obj at a new location -> low memory arrays."""
    inst = bpy.data.objects.new(name, obj.data)
    inst.location = location
    inst.rotation_euler = (0.0, 0.0, rot_z)
    coll.objects.link(inst)
    return inst


# ---------------------------------------------------------------- saving -----
def save_state(nn):
    state_dir = os.path.join(_ROOT, "state")
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, f"after_{nn:02d}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print(f"[JMR] saved {path}")
    return path
