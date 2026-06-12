# =============================================================================
# script_10_materials_validate.py — create material slots, assign by group,
# ensure a UV layer per mesh, then run the full validation report on every mesh.
# Standalone: builds the whole model first (via jmr_build), then materials+validate.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import jmr_util as U
import jmr_build
P = U.P; PARAMS = U.PARAMS
M = PARAMS["MATERIALS"]

# RGBA base colors for the flat low-poly look
_COLORS = {
    "MAT_CONCRETE":    (0.72, 0.72, 0.70, 1),
    "MAT_GRANITE":     (0.40, 0.40, 0.43, 1),
    "MAT_MEMBRANE":    (0.92, 0.92, 0.90, 1),
    "MAT_PAVING_RED":  (0.62, 0.22, 0.18, 1),
    "MAT_PAVING_GREY": (0.55, 0.55, 0.57, 1),
    "MAT_METAL_FRAME": (0.30, 0.31, 0.34, 1),
    "MAT_GLASS":       (0.55, 0.70, 0.80, 1),
    "MAT_COLLISION":   (0.10, 0.80, 0.30, 1),
}


def _mat(name, use_vcol=False):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = _COLORS.get(name, (0.7,0.7,0.7,1))
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = 0.85
            if use_vcol:
                vc = m.node_tree.nodes.new("ShaderNodeVertexColor")
                vc.layer_name = "Col"
                m.node_tree.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def _pick(name):
    n = name
    if "_COL" in n or n.endswith("COL"):
        return "MAT_COLLISION"
    if n.startswith("JMR_PILLAR"):
        return "MAT_GRANITE"
    if n.startswith("JMR_ROOF_MEMBRANE") or n.startswith("JMR_BG_MINA"):
        return "MAT_MEMBRANE"
    if n.startswith("JMR_ROOF"):
        return "MAT_METAL_FRAME"
    if "ROAD_PLAZA" in n:
        return "MAT_PAVING_RED"      # vertex-color paving bands
    if "TERRAIN" in n:
        return "MAT_PAVING_GREY"     # desert ground
    if "RAMPFAN" in n and "PIER" not in n:
        return "MAT_METAL_FRAME"     # flyover road deck (dark asphalt)
    if "ROAD_PILLAR" in n:
        return "MAT_CONCRETE"
    if n.startswith("JMR_ROAD") or "GROUND_ROAD" in n:
        return "MAT_METAL_FRAME"     # dark asphalt look
    if n.startswith("JMR_GROUND_VIS"):
        return "MAT_PAVING_RED"      # vertex-color driven
    if n.startswith("JMR_FURN") or "LOUVER" in n:
        return "MAT_METAL_FRAME"
    if n.startswith("JMR_TOWER") and "HELIPAD" in n:
        return "MAT_METAL_FRAME"
    return "MAT_CONCRETE"


def apply_materials(objs):
    for o in objs:
        if o.type != "MESH":
            continue
        mname = _pick(o.name)
        mat = _mat(mname, use_vcol=(o.name.startswith("JMR_GROUND_VIS")))
        o.data.materials.clear()
        o.data.materials.append(mat)
        # ensure a UV layer exists (cheap planar from XY; present for Roblox)
        if not o.data.uv_layers:
            o.data.uv_layers.new(name="UVMap")


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    jmr_build.build_all(colls)
    meshes = jmr_build.all_jmr_meshes()
    apply_materials(meshes)
    print(f"[JMR] materials assigned to {len(meshes)} meshes; "
          f"{len(bpy.data.materials)} material datablocks")
    # full validation (instances share data; report unique)
    seen = set(); uniq = []
    for o in meshes:
        if o.data.name not in seen:
            seen.add(o.data.name); uniq.append(o)
    ok, reps = U.validate_all(uniq, want_frozen=False)
    over = [r for r in reps if r["tris"] > PARAMS["POLY_LIMIT_PER_MESH"]]
    print(f"[JMR] unique meshes={len(uniq)} total_scene_meshes={len(meshes)} "
          f"over_cap={len(over)}")
    U.save_state(10)
    print("[JMR] SCRIPT 10 DONE" if ok else "[JMR] SCRIPT 10 HAS FAILURES")


if __name__ == "__main__":
    main()
