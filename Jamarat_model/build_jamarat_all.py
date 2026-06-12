# =============================================================================
# build_jamarat_all.py — SINGLE-FILE DELIVERABLE
# Generates the COMPLETE Jamarat Bridge 3D model (all phases) in ONE Blender run,
# at real scale, calibrated from OSM + references, then validates + exports FBX.
#
#   "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" ^
#       --background --factory-startup --python build_jamarat_all.py
#
# Optional flags after `--`:  --no-export   (skip FBX)   --no-save (skip .blend)
#
# It reuses the calibrated PARAMETERS.py (CALIBRATED=True) and the modular phase
# builders in scripts/. Everything is procedural, watertight, Roblox-ready.
# =============================================================================
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(ROOT, "scripts")
for p in (ROOT, SCRIPTS):
    if p not in sys.path:
        sys.path.insert(0, p)

import bpy  # noqa: E402
import jmr_util as U  # noqa: E402
import jmr_build  # noqa: E402
import script_10_materials_validate as MAT  # noqa: E402
import script_11_export as EXP  # noqa: E402
P = U.P; PARAMS = U.PARAMS

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
NO_EXPORT = "--no-export" in argv
NO_SAVE = "--no-save" in argv


def main():
    print("=" * 70)
    print("  JAMARAT BRIDGE — full procedural build (single-file)")
    print("=" * 70)
    if not P.CALIBRATED:
        raise SystemExit("[JMR] FAIL: PARAMETERS not calibrated. Run Phase R first.")
    print(f"[JMR] CALIBRATED={P.CALIBRATED} | real {PARAMS['BUILDING_LENGTH']}x"
          f"{PARAMS['BUILDING_WIDTH']} m, {PARAMS['FLOOR_COUNT']} floors")

    # 1. scene + collection tree
    U.reset_scene()
    colls = U.build_collection_tree()

    # 2. build every phase
    jmr_build.build_all(colls)
    meshes = jmr_build.all_jmr_meshes()

    # 3. materials + UVs
    MAT.apply_materials(meshes)
    print(f"[JMR] materials: {len(bpy.data.materials)} datablocks on {len(meshes)} meshes")

    # 4. validate everything (unique mesh data)
    seen = set(); uniq = []
    for o in meshes:
        if o.data.name not in seen:
            seen.add(o.data.name); uniq.append(o)
    ok, reps = U.validate_all(uniq, want_frozen=False)
    over = sum(1 for r in reps if r["tris"] > PARAMS["POLY_LIMIT_PER_MESH"])
    tot_tris = sum(U.tri_count(o.data) for o in meshes)
    print(f"[JMR] SCENE: objects={len(meshes)} unique_meshes={len(uniq)} "
          f"total_tris={tot_tris} over_cap={over} validate_ok={ok}")

    # 5. export FBX
    n = 0
    if not NO_EXPORT:
        n = EXP.export(colls)

    # 6. save final .blend
    if not NO_SAVE:
        path = os.path.join(ROOT, "state", "jamarat_full.blend")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print(f"[JMR] saved {path}")

    status = "OK" if (ok and over == 0 and (NO_EXPORT or n >= 7)) else "CHECK"
    print("=" * 70)
    print(f"[JMR] BUILD COMPLETE [{status}] — {len(meshes)} objects, "
          f"{tot_tris} tris, {n} FBX")
    print("=" * 70)


if __name__ == "__main__":
    main()
