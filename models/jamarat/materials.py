# materials.py — texturing pass for model "Jamarat Bridge Complex".
# =============================================================================
# Single-source geometry, TWO output versions (user decision 2026-06-15):
#   - generate_jamarat.py            -> POLOS  : geometry + empty named material slots
#   - generate_jamarat_textured.py   -> TEXTURED: same geometry + this texture pass
#
# Components NEVER touch textures/UV; they only assign a named slot via
# ruh_common.bm_to_object(..., material_key=...). This module fills the node tree
# of each MAT_* slot AND adds UVs only where an image texture needs them.
#
# Texture source = CAMPURAN (user-confirmed):
#   - PROCEDURAL (base color + roughness/metallic, no image file) for the majority.
#   - IMAGE TEXTURE for the highlight elements: MAT_GRANITE (jamrah walls) and
#     MAT_MEMBRANE (PTFE canopies). Drop image files in models/jamarat/textures/
#     (see TEX_FILES below); until present, a procedural fallback is used.
# =============================================================================
import os
import bpy

import PARAMETERS as P
from ruh_common import TAG

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "textures")

# --- Per-material look (linear-ish RGB, roughness, metallic) ------------------
# key = MATERIALS key (NOT the slot name). "image" marks the highlight elements.
LOOK = {
    "CONCRETE":   {"color": (0.62, 0.62, 0.60), "rough": 0.85, "metal": 0.0, "bump": 0.04},
    "GRANITE":    {"color": (0.40, 0.38, 0.40), "rough": 0.55, "metal": 0.0, "bump": 0.03, "image": True},
    "MEMBRANE":   {"color": (0.92, 0.92, 0.90), "rough": 0.35, "metal": 0.0, "bump": 0.0, "image": True,
                   "transmission": 0.08},
    "PAVING_RED": {"color": (0.55, 0.22, 0.18), "rough": 0.90, "metal": 0.0, "bump": 0.05},
    "PAVING_GREY":{"color": (0.48, 0.48, 0.47), "rough": 0.90, "metal": 0.0, "bump": 0.05},
    "METAL":      {"color": (0.70, 0.71, 0.73), "rough": 0.35, "metal": 1.0, "bump": 0.0},
    "GLASS":      {"color": (0.75, 0.82, 0.85), "rough": 0.08, "metal": 0.0, "bump": 0.0,
                   "transmission": 0.9},
}

# Expected image-map filenames per highlight material (PBR). Missing -> procedural fallback.
TEX_FILES = {
    "GRANITE":  {"base": "granite_basecolor.jpg",  "rough": "granite_roughness.jpg",  "normal": "granite_normal.jpg"},
    "MEMBRANE": {"base": "membrane_basecolor.jpg", "rough": "membrane_roughness.jpg", "normal": "membrane_normal.jpg"},
}


def _set(inp, node, name, value):
    """Set a Principled input by name if it exists (input names vary by Blender ver)."""
    if name in node.inputs:
        node.inputs[name].default_value = value


def _load_image(filename):
    path = os.path.join(TEX_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        return bpy.data.images.load(path, check_existing=True)
    except Exception:
        return None


def _build_nodes(mat, key):
    """Populate `mat`'s node tree for material `key`. Returns True if it used an
    image texture (caller must then ensure the mesh has UVs)."""
    look = LOOK[key]
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    _set(bsdf.inputs, bsdf, "Base Color", (*look["color"], 1.0))
    _set(bsdf.inputs, bsdf, "Roughness", look["rough"])
    _set(bsdf.inputs, bsdf, "Metallic", look["metal"])
    if "transmission" in look:
        # Blender 4.x renamed "Transmission" -> "Transmission Weight"
        _set(bsdf.inputs, bsdf, "Transmission", look["transmission"])
        _set(bsdf.inputs, bsdf, "Transmission Weight", look["transmission"])

    used_image = False
    if look.get("image"):
        files = TEX_FILES.get(key, {})
        img_base = _load_image(files.get("base", "")) if files else None
        if img_base is not None:
            used_image = True
            coord = nt.nodes.new("ShaderNodeTexCoord");  coord.location = (-700, 0)
            mapping = nt.nodes.new("ShaderNodeMapping");  mapping.location = (-520, 0)
            nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])

            tex = nt.nodes.new("ShaderNodeTexImage"); tex.location = (-320, 100)
            tex.image = img_base
            nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

            img_rough = _load_image(files.get("rough", ""))
            if img_rough is not None:
                img_rough.colorspace_settings.name = "Non-Color"
                rtex = nt.nodes.new("ShaderNodeTexImage"); rtex.location = (-320, -160)
                rtex.image = img_rough
                nt.links.new(mapping.outputs["Vector"], rtex.inputs["Vector"])
                nt.links.new(rtex.outputs["Color"], bsdf.inputs["Roughness"])

            img_norm = _load_image(files.get("normal", ""))
            if img_norm is not None:
                img_norm.colorspace_settings.name = "Non-Color"
                ntex = nt.nodes.new("ShaderNodeTexImage"); ntex.location = (-320, -420)
                ntex.image = img_norm
                nmap = nt.nodes.new("ShaderNodeNormalMap"); nmap.location = (-120, -420)
                nt.links.new(mapping.outputs["Vector"], ntex.inputs["Vector"])
                nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
                nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
            print(f"{TAG}      texture: {key} <- image maps ({TEX_DIR})")
        else:
            print(f"{TAG}      texture: {key} -> procedural fallback (no image in {TEX_DIR})")

    # Procedural micro-bump for non-image (or image-missing) surfaces.
    if not used_image and look.get("bump", 0.0) > 0.0:
        noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-520, -260)
        if "Scale" in noise.inputs:
            noise.inputs["Scale"].default_value = 18.0
        bump = nt.nodes.new("ShaderNodeBump"); bump.location = (-200, -260)
        bump.inputs["Strength"].default_value = look["bump"]
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return used_image


def _smart_uv(obj):
    """Add a UV map to `obj` via smart project (only for image-textured meshes)."""
    if obj.type != "MESH":
        return
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


# --- Public entry point -------------------------------------------------------
def apply_all(collections):
    """Texture pass for generate_jamarat_textured.py. Builds the node tree for
    every MAT_* slot that exists, then UV-unwraps meshes whose material is
    image-textured. `collections` = dict {name: bpy collection} from the build."""
    # slot name -> MATERIALS key  (e.g. "MAT_GRANITE" -> "GRANITE")
    slot_to_key = {slot: key for key, slot in P.MATERIALS.items()}
    image_slots = set()
    print(f"{TAG} ===== TEXTURE PASS (CAMPURAN: procedural + image highlights) =====")

    for key, slot in P.MATERIALS.items():
        mat = bpy.data.materials.get(slot)
        if mat is None:               # slot never used by any built mesh -> skip
            continue
        if _build_nodes(mat, key):
            image_slots.add(slot)

    if not image_slots:
        return
    # UV-unwrap only meshes that carry an image-textured material.
    for coll in collections.values():
        for obj in list(coll.objects):
            if obj.type != "MESH":
                continue
            if any((slot.name in image_slots) for slot in obj.data.materials if slot):
                _smart_uv(obj)
