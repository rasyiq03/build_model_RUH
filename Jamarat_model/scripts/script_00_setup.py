# =============================================================================
# script_00_setup.py — scene reset, metric units, JMR collection tree, PARAMS dump.
# Run: blender --background --factory-startup --python scripts/script_00_setup.py
# Done when: tree exists, console prints PARAMS summary + CALIBRATED, no error.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P
PARAMS = U.PARAMS


def main():
    print("=" * 64)
    print("[JMR] script_00 — scene setup")
    print("=" * 64)

    # 1. hard gate: must be calibrated before any layout work
    print(f"[JMR] CALIBRATED = {P.CALIBRATED} | {P.calibration_status()}")
    if not P.CALIBRATED:
        raise SystemExit("[JMR] FAIL: PARAMETERS not calibrated — run Phase R first.")

    # 2. reset scene + metric units
    U.reset_scene()
    scn = U.bpy.context.scene
    print(f"[JMR] units: {scn.unit_settings.system} "
          f"scale_length={scn.unit_settings.scale_length} "
          f"({scn.unit_settings.length_unit})")

    # 3. collection tree (AGENTS §5)
    colls = U.build_collection_tree()
    print(f"[JMR] collections ({len(colls)}): " + ", ".join(sorted(colls.keys())))

    # 4. PARAMS summary
    r = PARAMS["REFERENCE"]
    print("-" * 64)
    print(f"[JMR] REAL {r['REAL_LENGTH']}m(Y) x {r['REAL_WIDTH']}m(X), "
          f"{r['REAL_FLOOR_COUNT']} floors @ {r['REAL_FLOOR_HEIGHT']}m")
    print(f"[JMR] Floor Z (slab top): {PARAMS['FLOOR_SURFACE_Z']}")
    print(f"[JMR] poly cap {PARAMS['POLY_LIMIT_PER_MESH']} "
          f"(warn {PARAMS['POLY_WARN_THRESHOLD']})")
    t = PARAMS["TRACE"]
    print(f"[JMR] TRACE: OUTER={len(t['OUTLINE_OUTER'])}v VOID={len(t['OUTLINE_VOID'])}v "
          f"pillars={list(t['PILLARS'])} towers={len(t['TOWERS'])} "
          f"membranes={len(t['ROOF_MEMBRANES'])}")
    print(f"[JMR] verify max dev = {t['VERIFY_MAX_DEVIATION_M']} m "
          f"(tol {t['VERIFY_TOLERANCE_M']} m)")

    # 5. save state
    U.save_state(0)
    print("[JMR] SCRIPT 00 DONE")


if __name__ == "__main__":
    main()
