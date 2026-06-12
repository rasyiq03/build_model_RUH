# =============================================================================
# script_03_ramp_system.py — helical circulation ramps (VIS + COL).
# Helix swept trapezoid ribbon around the two end helix centers (RAMP_AXES.HELIX).
# =============================================================================
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def _helix_edges(cx, cy, r_in, r_out, z0, z1, turns, n):
    left = []; right = []
    for i in range(n):
        t = i / (n - 1)
        ang = t * turns * 2 * math.pi
        z = z0 + (z1 - z0) * t
        ca, sa = math.cos(ang), math.sin(ang)
        left.append((cx + r_in * ca, cy + r_in * sa, z))
        right.append((cx + r_out * ca, cy + r_out * sa, z))
    return left, right


def build(colls):
    U.clear_collection(colls["RAMPS"])
    U.clear_collection(colls["COL_RAMPS"])
    helix = PARAMS["TRACE"]["RAMP_AXES"]["HELIX"]
    r_in = PARAMS["RAMP_HELIX_RADIUS_INNER"]; r_out = PARAMS["RAMP_HELIX_RADIUS_OUTER"]
    grad = PARAMS["RAMP_HELIX_GRADIENT"]; thick = PARAMS["RAMP_THICKNESS"]
    z_top = PARAMS["FLOOR_SURFACE_Z"][PARAMS["FLOOR_COUNT"]]   # 48.5
    rm = (r_in + r_out) / 2
    rise_per_turn = grad * 2 * math.pi * rm
    turns = max(1.0, z_top / rise_per_turn)
    n = max(24, int(turns * 24))
    objs = []
    for k, hx in enumerate(helix):
        cx, cy = hx["center"]
        L, R = _helix_edges(cx, cy, r_in, r_out, 0.5, z_top, turns, n)
        objs.append(U.ribbon_solid(f"JMR_RAMP_HELIX{k}_VIS", L, R, thick, colls["RAMPS"]))
        # COL: downsampled flat-ish ribbon
        nc = max(12, n // 5)
        Lc, Rc = _helix_edges(cx, cy, r_in, r_out, 0.4, z_top, turns, nc)
        objs.append(U.ribbon_solid(f"JMR_RAMP_HELIX{k}_COL", Lc, Rc, thick,
                                   colls["COL_RAMPS"]))
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_03 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(3)
    print("[JMR] SCRIPT 03 DONE" if ok else "[JMR] SCRIPT 03 HAS FAILURES")


if __name__ == "__main__":
    main()
