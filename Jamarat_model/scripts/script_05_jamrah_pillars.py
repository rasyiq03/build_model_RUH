# =============================================================================
# script_05_jamrah_pillars.py — 3 elliptical jamrah WALLS + oval basins +
# per-floor oval platforms + throwing parapets + connectors to the deck ring.
# Wall = tapered elliptical blade (long axis X), NOT a box. VIS + COL.
# =============================================================================
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def _ring_z(a_y, b_x, z, n, cx, cy):
    return [(x, y, z) for (x, y) in U.ellipse_xy(a_y, b_x, n=n, cx=cx, cy=cy)]


def _void_x_at(y, va, vb):
    t = max(0.0, 1.0 - (y / va) ** 2)
    return vb * math.sqrt(t)


def build(colls):
    for c in ("PILLARS", "COL_PILLARS"):
        U.clear_collection(colls[c])
    void = P.get_outline("VOID")
    va = max(p[1] for p in void); vb = max(p[0] for p in void)
    pillars = P.get_pillars()
    nseg = PARAMS["PILLAR_WALL_VERTS"]
    Htot = PARAMS["PILLAR_HEIGHT_TOTAL"]
    tb = PARAMS["PILLAR_WALL_THICK_BASE"]; tt = PARAMS["PILLAR_WALL_THICK_TOP"]
    objs = []

    for name, pd in pillars.items():
        cx, cy = pd["pos"]; halfL = pd["length"] / 2.0
        # ---- WALL (tapered elliptical blade), z 0..Htot ----
        bot = _ring_z(tb / 2, halfL, 0.0, nseg, cx, cy)
        top = _ring_z(tt / 2, halfL * 0.82, Htot, nseg, cx, cy)
        objs.append(U.loft_rings(f"JMR_PILLAR_{name}_VIS", bot, top, colls["PILLARS"]))
        # ---- WALL COL hull (coarse) ----
        botc = _ring_z(tb / 2, halfL, 0.0, 12, cx, cy)
        topc = _ring_z(tt / 2, halfL * 0.82, Htot, 12, cx, cy)
        objs.append(U.loft_rings(f"JMR_PILLAR_{name}_COL", botc, topc, colls["COL_PILLARS"]))
        # ---- BASIN oval rim at ground ----
        bo = U.ellipse_xy(halfL + 9, halfL + 9, n=48, cx=cx, cy=cy)  # rounded basin
        bi = U.ellipse_xy(halfL + 7, halfL + 7, n=48, cx=cx, cy=cy)
        objs.append(U.annulus_slab(f"JMR_BASIN_{name}_VIS", bo, bi, 0.0,
                                   PARAMS["BASIN_RIM_HEIGHT"], colls["PILLARS"]))

        # ---- per-floor throwing parapet ring around the wall (barrier) ----
        # Decks are SOLID now: players walk up to each wall and throw over a
        # waist-high oval ring that marks the throwing zone (basin per floor).
        pr = PARAMS["PLATFORM_PARAPET_HEIGHT"]; pt = PARAMS["PLATFORM_PARAPET_THICK"]
        for f in range(1, PARAMS["FLOOR_COUNT"] + 1):
            zf = PARAMS["FLOOR_SURFACE_Z"][f]
            ri = U.ellipse_xy(halfL + 6, halfL + 6, n=48, cx=cx, cy=cy)
            ro = U.ellipse_xy(halfL + 6 + pt, halfL + 6 + pt, n=48, cx=cx, cy=cy)
            objs.append(U.annulus_slab(f"JMR_BASIN_{name}_L{f}_RING_VIS", ro, ri,
                                       zf, zf + pr, colls["PILLARS"]))
            roc = U.ellipse_xy(halfL + 6 + pt, halfL + 6 + pt, n=16, cx=cx, cy=cy)
            ric = U.ellipse_xy(halfL + 6, halfL + 6, n=16, cx=cx, cy=cy)
            objs.append(U.annulus_slab(f"JMR_BASIN_{name}_L{f}_RING_COL", roc, ric,
                                       zf, zf + pr, colls["COL_PILLARS"]))
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_05 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(5)
    print("[JMR] SCRIPT 05 DONE" if ok else "[JMR] SCRIPT 05 HAS FAILURES")


if __name__ == "__main__":
    main()
