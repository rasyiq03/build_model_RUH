# components/comp_canopies.py
# =============================================================================
# Emits the 4 white PTFE tensile canopies over the spine (Ula/Wusta + transition
# plaza + Aqaba). SHAPE FOLLOWS THE MASTS (user 2026-06-16): the footprint polygon
# passes THROUGH the user-marked mast positions (ref-clarify canopy_compare3 ->
# models/jamarat/canopy_masts.json) — each mast is a cusp, so the edge curvature
# follows the mast count (more masts = rounder). Over that polygon a SMOOTH TAUT
# dome is built (peak at centre), a VERTICAL mast stands at EVERY polygon vertex
# with a cable to the edge, and a steel DRUM sits at the peak. NO central column
# (centre = jamrah wall). Membrane = MEMBRANE (textured highlight); masts/cables/
# drum/ring = METAL (per-face material_index).
#
# Standalone: blender --background --factory-startup --python models/jamarat/components/comp_canopies.py
# =============================================================================
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))    # components/
MODEL = os.path.dirname(HERE)                          # models/jamarat/
ROOT = os.path.dirname(os.path.dirname(MODEL))         # ruh/
sys.path += [MODEL, ROOT]

import bpy, bmesh
from mathutils import Vector, Matrix
import PARAMETERS as P
import ruh_common as C

NAME       = "RUH_ROOF_CANOPIES_VIS"
COLLECTION = "ROOF"
TRI_CAP    = P.CANOPIES["TARGET_TRI"]

_MASTS = os.path.join(MODEL, "canopy_masts.json")
_SCALES = (1.0, 0.84, 0.66, 0.46, 0.24)   # concentric dome rings (more = smoother dome)
_INSET = 0.92        # cable attach ring sits just INSIDE the masts
# Real canopies = SMOOTH near-circular white umbrella discs (REAL_aerial_jamarat-bridge.jpg),
# NOT deep stars. The membrane edge is a SMOOTH Catmull-Rom curve THROUGH the mast points
# (honours user 2026-06-16 "shape follows masts": each mast still sits on the edge), with only
# a VERY shallow inward scallop between masts for the subtle umbrella-rib look.
_EDGE_SCALLOP = 0.035   # gentle inward bow between masts (was 0.18 deep cusp = star — REJECTED)
_SUB = 6             # samples per mast span along the smooth edge
_CROSS = 6
# canopy "over" name -> outline json key
_KEY = {"ula": "ula", "wusta": "wusta", "transition": "transisi", "aqaba": "aqabah"}

MAT_MEMBRANE = 0
MAT_METAL = 1


def _catmull_rom(p0, p1, p2, p3, t):
    """Uniform Catmull-Rom interpolation; the curve passes THROUGH p1..p2."""
    t2, t3 = t * t, t * t * t
    return tuple(
        0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t
               + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2
               + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3)
        for d in (0, 1)
    )


def _smooth_perimeter(cable_pts, cx, cy, rim_z, scallop, sub):
    """SMOOTH near-circular free edge: a closed Catmull-Rom spline THROUGH the
    cable/mast points (so each mast still sits on the rim), sampled finely so the
    outline reads as a round umbrella disc. A very shallow inward scallop between
    masts gives the subtle rib look — NOT the old deep star cusp. z = rim (flat,
    taut edge). Returns a dense list of (x,y,z)."""
    out = []
    n = len(cable_pts)
    for i in range(n):
        p0 = cable_pts[(i - 1) % n]
        p1 = cable_pts[i]
        p2 = cable_pts[(i + 1) % n]
        p3 = cable_pts[(i + 2) % n]
        for k in range(sub):
            t = k / sub
            x, y = _catmull_rom(p0, p1, p2, p3, t)
            w = math.sin(math.pi * t)                 # 0 at masts, 1 mid-span
            x += (cx - x) * (scallop * w)             # gentle inward scallop
            y += (cy - y) * (scallop * w)
            out.append((x, y, rim_z))
    return out


def _membrane_poly(bm, perim, cx, cy, peak_z, thick):
    """Smooth anticlastic dome over a tensile perimeter `perim` = [(x,y,z)].
    Concentric rings scaled toward the centroid; z eases from the edge to peak."""
    n = len(perim)

    def ring(s, dz):
        # Parabolic cap (1 - s^2): FLAT, rounded top (zero slope at centre, no
        # sharp point) easing to the rim — a gentle umbrella dome, not a pyramid.
        verts = []
        for (x, y, ze) in perim:
            z = ze + (peak_z - ze) * (1.0 - s * s) + dz
            verts.append(bm.verts.new((cx + (x - cx) * s, cy + (y - cy) * s, z)))
        return verts

    top = [ring(s, 0.0) for s in _SCALES]
    bot = [ring(s, -thick) for s in _SCALES]
    apex_t = bm.verts.new((cx, cy, peak_z))
    apex_b = bm.verts.new((cx, cy, peak_z - thick))

    def face(vs):
        f = bm.faces.new(vs); f.material_index = MAT_MEMBRANE

    inner_t, inner_b = top[-1], bot[-1]
    for i in range(n):
        j = (i + 1) % n
        face((apex_t, inner_t[i], inner_t[j]))           # top apex fan
        face((apex_b, inner_b[j], inner_b[i]))           # bottom apex fan
    for r in range(len(_SCALES) - 1):
        at, bt = top[r + 1], top[r]
        ab, bb = bot[r + 1], bot[r]
        for i in range(n):
            j = (i + 1) % n
            face((at[i], at[j], bt[j], bt[i]))           # top ring band
            face((ab[i], bb[i], bb[j], ab[j]))           # bottom ring band
    ot, ob = top[0], bot[0]
    for i in range(n):
        j = (i + 1) % n
        face((ot[i], ob[i], ob[j], ot[j]))               # outer edge (close shell)
    return (cx, cy)


def _ring_tube(bm, pts, radius):
    """Closed swept tube through `pts` (membrane edge cable)."""
    n = len(pts)
    rings = []
    for i in range(n):
        p = Vector(pts[i])
        t = (Vector(pts[(i + 1) % n]) - Vector(pts[(i - 1) % n]))
        t = t.normalized() if t.length > 1e-6 else Vector((1, 0, 0))
        up = Vector((0, 0, 1)) if abs(t.z) < 0.99 else Vector((1, 0, 0))
        n1 = t.cross(up).normalized()
        n2 = t.cross(n1).normalized()
        rings.append([bm.verts.new((p + n1 * (radius * math.cos(2 * math.pi * k / _CROSS))
                                      + n2 * (radius * math.sin(2 * math.pi * k / _CROSS)))[:])
                      for k in range(_CROSS)])
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(_CROSS):
            kk = (k + 1) % _CROSS
            f = bm.faces.new((a[k], a[kk], b[kk], b[k])); f.material_index = MAT_METAL


def build(collection=None):
    """Build the 4 canopies (footprint = polygon through user-marked masts)."""
    K = P.CANOPIES
    collection = collection or C.reset_collection(COLLECTION)
    peak_z, rim_z = P.TRACE["CANOPY_PEAK_Z"], P.TRACE["CANOPY_RIM_Z"]
    deck_top = P.FLOOR_Z[P.FLOOR_COUNT]
    mast_top = peak_z + 4.0
    masts = json.load(open(_MASTS, encoding="utf-8"))

    bm = bmesh.new()
    for c in P.TRACE["CANOPIES"]:
        key = _KEY.get(c["over"])
        poly = [tuple(p) for p in masts.get(key, [])]   # OUTER ring = mast positions
        if len(poly) < 3:
            continue
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        # Cable attach points sit INSIDE the masts; the membrane hangs from cables.
        cable_pts = [(cx + (x - cx) * _INSET, cy + (y - cy) * _INSET) for (x, y) in poly]
        # Smooth round umbrella edge: Catmull-Rom spline through the cable/mast points.
        perim = _smooth_perimeter(cable_pts, cx, cy, rim_z, _EDGE_SCALLOP, _SUB)
        _membrane_poly(bm, perim, cx, cy, peak_z, K["MEMBRANE_THICK"])
        _ring_tube(bm, perim, K["RING_TUBE"])

        before = set(bm.faces)
        C.add_capped_cone(bm, 5.0, 5.0, 5.0, Matrix.Translation((cx, cy, peak_z + 1.5)), 16)   # drum
        # A VERTICAL mast stands at each OUTER position; a steel CABLE runs from its top
        # to the lifted cable point on the membrane edge — membrane hangs from cables.
        for (mx, my), (ex, ey) in zip(poly, cable_pts):
            mat, length = C.segment_matrix((mx, my, deck_top), (mx, my, mast_top))
            C.add_capped_cone(bm, 0.8, 0.5, length, mat, 8)
            cmat, clen = C.segment_matrix((mx, my, mast_top), (ex, ey, rim_z))
            C.add_capped_cone(bm, K["CABLE_RADIUS"], K["CABLE_RADIUS"], clen, cmat, 4)
        for f in bm.faces:
            if f not in before:
                f.material_index = MAT_METAL

    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(NAME, me); collection.objects.link(obj)
    for keyname in ("MEMBRANE", "METAL"):
        slot = P.MATERIALS.get(keyname, keyname)
        me.materials.append(bpy.data.materials.get(slot) or bpy.data.materials.new(slot))
    return obj


# --- Standalone verification --------------------------------------------------
if __name__ == "__main__":
    C.reset_scene()
    coll = C.reset_collection(COLLECTION)
    obj = build(coll)
    status, tris = C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
    print(f"{C.TAG} component 'canopies' (user-drawn outlines) -> {status}")
    if status == "FAIL":
        raise SystemExit(1)
