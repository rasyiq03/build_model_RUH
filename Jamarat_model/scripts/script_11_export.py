# =============================================================================
# script_11_export.py — one FBX per PARAMS["FBX_GROUPS"] collection group, with
# triangulate-on-export + a per-file poly/size report. Standalone: builds the
# whole model (+materials) first, then exports.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import jmr_util as U
import jmr_build
import script_10_materials_validate as MAT
P = U.P; PARAMS = U.PARAMS


def _enable_fbx():
    try:
        bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    except Exception as e:
        print("[JMR] fbx addon note:", e)


def _add_triangulate(meshes):
    for o in meshes:
        if o.type == "MESH" and "Triangulate" not in [m.name for m in o.modifiers]:
            o.modifiers.new("Triangulate", "TRIANGULATE")


def export(colls):
    _enable_fbx()
    out_dir = os.path.join(U._ROOT, "export_fbx")
    os.makedirs(out_dir, exist_ok=True)
    meshes = jmr_build.all_jmr_meshes()
    _add_triangulate(meshes)

    by_coll = {}
    def descend(c):
        by_coll[c.name] = c
        for ch in c.children:
            descend(ch)
    root = bpy.data.collections.get("JMR_ROOT")
    if root:
        descend(root)

    total_tris = 0; total_bytes = 0; n_files = 0
    print("[JMR] --- FBX EXPORT REPORT ---")
    for group, collnames in PARAMS["FBX_GROUPS"].items():
        bpy.ops.object.select_all(action="DESELECT")
        sel = []
        for cn in collnames:
            c = by_coll.get(cn)
            if not c:
                continue
            for o in c.objects:
                if o.type == "MESH":
                    o.select_set(True); sel.append(o)
        if not sel:
            print(f"[JMR]   {group}: (no objects, skipped)")
            continue
        bpy.context.view_layer.objects.active = sel[0]
        path = os.path.join(out_dir, f"JMR_{group}.fbx")
        bpy.ops.export_scene.fbx(
            filepath=path, use_selection=True,
            global_scale=PARAMS["FBX_SCALE"], apply_unit_scale=PARAMS["FBX_APPLY_UNIT"],
            axis_forward=PARAMS["FBX_AXIS_FORWARD"], axis_up=PARAMS["FBX_AXIS_UP"],
            use_mesh_modifiers=PARAMS["FBX_USE_MESH_MODIFIERS"],
            mesh_smooth_type="FACE", bake_space_transform=False,
            object_types={"MESH"},
        )
        tris = sum(U.tri_count(o.data) for o in sel)
        size = os.path.getsize(path)
        total_tris += tris; total_bytes += size; n_files += 1
        print(f"[JMR]   JMR_{group}.fbx : objs={len(sel):4d} tris={tris:7d} "
              f"size={size/1024:8.1f} KB")
    print(f"[JMR] --- {n_files} FBX files, total tris={total_tris}, "
          f"total ~{total_bytes/1024/1024:.2f} MB -> {out_dir}")
    return n_files


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    jmr_build.build_all(colls)
    MAT.apply_materials(jmr_build.all_jmr_meshes())
    n = export(colls)
    U.save_state(11)
    print(f"[JMR] SCRIPT 11 DONE ({n} FBX)" if n >= 7 else
          f"[JMR] SCRIPT 11 WARN: only {n} FBX (expected 7)")


if __name__ == "__main__":
    main()
