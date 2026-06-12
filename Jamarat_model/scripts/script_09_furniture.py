# =============================================================================
# script_09_furniture.py — Y-branch lamp poles, cooling-fan poles, green signs
# (masters + instanced), plus Mina tent-city background. Instances translate only
# (rotation 0, scale 1) so transforms stay frozen.
# =============================================================================
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def _axes(ring):
    return max(p[1] for p in ring), max(p[0] for p in ring)


def _lamp_master(coll):
    h = PARAMS["LAMP_POLE_HEIGHT"]
    pole = U.cylinder("lamp_pole", 0, 0, 0.16, 0.12, 0, h, coll, n=8)
    a1 = U.strut("lamp_a1", (0, 0, h - 1.0), (1.6, 0, h), 0.08, coll, n=6)
    a2 = U.strut("lamp_a2", (0, 0, h - 1.0), (-1.6, 0, h), 0.08, coll, n=6)
    h1 = U.box("lamp_h1", 1.6, 0, h, 0.5, 0.3, 0.2, coll)
    h2 = U.box("lamp_h2", -1.6, 0, h, 0.5, 0.3, 0.2, coll)
    return U.join_objects([pole, a1, a2, h1, h2], "JMR_FURN_LAMP_MASTER", coll)


def _fan_master(coll):
    h = PARAMS["FAN_POLE_HEIGHT"]; rr = PARAMS["FAN_HEAD_RADIUS"]
    pole = U.cylinder("fan_pole", 0, 0, 0.12, 0.10, 0, h, coll, n=8)
    head = U.cylinder("fan_head", 0, 0, rr, rr, h, h + 0.25, coll, n=12)
    return U.join_objects([pole, head], "JMR_FURN_FAN_MASTER", coll)


def _sign_master(coll):
    w = PARAMS["SIGN_WIDTH"]; hh = PARAMS["SIGN_HEIGHT"]
    pole = U.cylinder("sign_pole", 0, 0, 0.1, 0.1, 0, 3.0, coll, n=6)
    panel = U.box("sign_panel", 0, 0, 3.0 + hh/2, w, 0.15, hh, coll)
    return U.join_objects([pole, panel], "JMR_FURN_SIGN_MASTER", coll)


def build(colls):
    U.clear_collection(colls["FURNITURE"])
    U.clear_collection(colls["BACKGROUND"])
    fc = colls["FURNITURE"]
    outer = P.get_outline("OUTER"); oa, ob = _axes(outer)
    objs = []

    # masters
    lamp = _lamp_master(fc); sign = _sign_master(fc)
    objs += [lamp, sign]

    # street lamps ONLY along the outer road ring at ground (clearly lamps, sparse)
    for i, (x, y) in enumerate(U.sample_ellipse_spacing(oa + 40, ob + 40,
                                                        PARAMS["LAMP_SPACING"] * 4)):
        objs.append(U.duplicate_linked(lamp, f"JMR_FURN_LAMP_{i}_VIS", (x, y, 0.0), fc))

    # a few direction signs near the fan-ramp mouths
    for i, (x, y) in enumerate([(0, 300), (0, -300), (60, 0), (-60, 0)]):
        objs.append(U.duplicate_linked(sign, f"JMR_FURN_SIGN_{i}_VIS", (x, y, 0.0), fc))

    # NOTE: cooling-fan poles REMOVED (user: ambiguous poles on the deck).
    # NOTE: Mina pilgrim tent-city REMOVED (user: model is jamarat-only).
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_09 emitted {len(objs)} objects")
    # validate unique mesh-data only (instances share data)
    seen = set(); uniq = []
    for o in objs:
        if o.data.name not in seen:
            seen.add(o.data.name); uniq.append(o)
    ok, _ = U.validate_all(uniq, want_frozen=False)
    U.save_state(9)
    print("[JMR] SCRIPT 09 DONE" if ok else "[JMR] SCRIPT 09 HAS FAILURES")


if __name__ == "__main__":
    main()
