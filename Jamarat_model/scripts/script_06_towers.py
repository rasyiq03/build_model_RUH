# =============================================================================
# script_06_towers.py — 12 escalator/circulation towers from TRACE.TOWERS.
# Types: PLAIN (cylinder + vertical louver fins), FLARED (mushroom cap),
# HELIPAD (flared + circular helipad disc). Towers are CanCollide=false -> VIS only.
# =============================================================================
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def _louvers(name, cx, cy, r, z0, z1, coll):
    cnt = PARAMS["TOWER_LOUVER_COUNT"]; dep = PARAMS["TOWER_LOUVER_DEPTH"]
    specs = []
    h = z1 - z0; cz = (z0 + z1) / 2
    for i in range(cnt):
        a = 2 * math.pi * i / cnt
        x = cx + (r + dep / 2) * math.cos(a); y = cy + (r + dep / 2) * math.sin(a)
        specs.append((x, y, cz, dep + 0.3, 0.4, h, a))
    return U.multi_box_mesh(name, specs, coll)


def build(colls):
    U.clear_collection(colls["TOWERS"])
    towers = P.get_towers()
    r = PARAMS["TOWER_RADIUS"]; H = PARAMS["TOWER_TOTAL_HEIGHT"]; n = PARAMS["TOWER_VERTS"]
    fr = PARAMS["TOWER_FLARE_RADIUS"]; fh = PARAMS["TOWER_FLARE_HEIGHT"]
    hpr = PARAMS["HELIPAD_RADIUS"]; hpt = PARAMS["HELIPAD_THICK"]
    objs = []
    for i, tw in enumerate(towers):
        cx, cy = tw["pos"]; typ = tw["type"]
        # body
        objs.append(U.cylinder(f"JMR_TOWER_{i}_{typ}_VIS", cx, cy, r, r, 0.0, H,
                               colls["TOWERS"], n=n))
        if typ == "PLAIN":
            objs.append(_louvers(f"JMR_TOWER_{i}_LOUVER_VIS", cx, cy, r, 1.0, H - 1.0,
                                 colls["TOWERS"]))
        elif typ == "FLARED":
            objs.append(U.cylinder(f"JMR_TOWER_{i}_FLARE_VIS", cx, cy, r, fr, H, H + fh,
                                   colls["TOWERS"], n=n))
        elif typ == "HELIPAD":
            objs.append(U.cylinder(f"JMR_TOWER_{i}_FLARE_VIS", cx, cy, r, fr * 0.7, H, H + fh,
                                   colls["TOWERS"], n=n))
            objs.append(U.cylinder(f"JMR_TOWER_{i}_HPDISC_VIS", cx, cy, hpr, hpr,
                                   H + fh, H + fh + hpt, colls["TOWERS"], n=n))
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_06 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(6)
    print("[JMR] SCRIPT 06 DONE" if ok else "[JMR] SCRIPT 06 HAS FAILURES")


if __name__ == "__main__":
    main()
