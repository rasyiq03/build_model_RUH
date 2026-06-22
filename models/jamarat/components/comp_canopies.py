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
_SCALES = (1.0, 0.80, 0.58, 0.34)   # concentric dome rings (smooth surface)
_INSET = 0.85   # cable attach ring sits INSIDE the masts; the gap is spanned by cables
_EDGE_SAG = 0.18    # free edge STRETCHES inward between cable points (taut catenary)
_SUB = 4            # edge subdivisions per cable span
_CUSP_DZ = 0.0      # NO vertical wave — membrane is taut/stretched, not undulating
_SAG_DZ = 0.0       # (user 2026-06-16: "merenggang, bukan bergelombang")
_CROSS = 6
# canopy "over" name -> outline json key
_KEY = {"ula": "ula", "wusta": "wusta", "transition": "transisi", "aqaba": "aqabah"}

MAT_MEMBRANE = 0
MAT_METAL = 1


def _tensile_perimeter(cable_pts, cx, cy, rim_z, sag, cusp_dz, sag_dz, sub):
    """Physical tensile free edge: between two cable points the membrane edge
    bows INWARD (catenary, toward centroid) and DOWN, while it is pulled UP at
    each cable point (anticlastic). Returns a dense list of (x,y,z)."""
    out = []
    n = len(cable_pts)
    for i in range(n):
        ax, ay = cable_pts[i]
        bx, by = cable_pts[(i + 1) % n]
        for k in range(sub):
            t = k / sub
            w = math.sin(math.pi * t)                 # 0 at cable pts, 1 at mid-edge
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            x += (cx - x) * (sag * w)                 # bow inward
            y += (cy - y) * (sag * w)
            z = rim_z + cusp_dz * (1.0 - w) - sag_dz * w
            out.append((x, y, z))
    return out


def _membrane_poly(bm, perim, cx, cy, peak_z, thick):
    """Smooth anticlastic dome over a tensile perimeter `perim` = [(x,y,z)].
    Concentric rings scaled toward the centroid; z eases from the edge to peak."""
    n = len(perim)

    def ring(s, dz):
        verts = []
        for (x, y, ze) in perim:
            z = peak_z - (peak_z - ze) * (s ** 1.4) + dz
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
        # Free edge bows inward between cable points (physical tensile catenary).
        perim = _tensile_perimeter(cable_pts, cx, cy, rim_z, _EDGE_SAG, _CUSP_DZ, _SAG_DZ, _SUB)
        _membrane_poly(bm, perim, cx, cy, peak_z, K["MEMBRANE_THICK"])
        _ring_tube(bm, perim, K["RING_TUBE"])

        before = set(bm.faces)
        C.add_capped_cone(bm, 5.0, 5.0, 5.0, Matrix.Translation((cx, cy, peak_z + 1.5)), 16)   # drum
        # A VERTICAL mast stands at each OUTER position; a steel CABLE runs from its top
        # to the lifted cable point on the membrane edge — membrane hangs from cables.
        for (mx, my), (ex, ey) in zip(poly, cable_pts):
            mat, length = C.segment_matrix((mx, my, deck_top), (mx, my, mast_top))
            C.add_capped_cone(bm, 0.8, 0.5, length, mat, 8)
            cmat, clen = C.segment_matrix((mx, my, mast_top), (ex, ey, rim_z + _CUSP_DZ))
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
