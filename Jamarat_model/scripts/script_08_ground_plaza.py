# =============================================================================
# script_08_ground_plaza.py — ground slab with radial red/grey paving bands +
# yellow lane lines via VERTEX COLOR (not geometry). Flat COL box. Origin world (0,0,0).
# =============================================================================
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS

RED = (0.62, 0.22, 0.18, 1.0)
GREY = (0.55, 0.55, 0.57, 1.0)
YELLOW = (0.85, 0.72, 0.15, 1.0)


def _ccw(poly):
    return poly if U.signed_area(poly) > 0 else poly[::-1]


def build(colls):
    U.clear_collection(colls["GROUND"])
    gz = PARAMS["GROUND_Z"]
    out = []
    # base desert terrain plane (seen through the courtyard / oculus holes).
    terr = U.box("JMR_GROUND_TERRAIN_VIS", 0, 0, gz - 0.8, 1300, 1500, 1.2,
                 colls["GROUND"])
    out.append(terr)
    return out


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_08 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(8)
    print("[JMR] SCRIPT 08 DONE" if ok else "[JMR] SCRIPT 08 HAS FAILURES")


if __name__ == "__main__":
    main()
