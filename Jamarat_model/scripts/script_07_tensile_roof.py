# =============================================================================
# script_07_tensile_roof.py — 5 conical tensile membranes over the spine, each
# with a rigid oculus ring + radial truss spokes, supported by masts + guy cables.
# Membrane = cone frustum (footprint oval -> oculus ring) with volume (watertight).
# =============================================================================
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def build(colls):
    U.clear_collection(colls["ROOF"])
    mems = PARAMS["TRACE"]["ROOF_MEMBRANES"]
    rim_z = PARAMS["MEMBRANE_RIM_Z"]; peak_z = PARAMS["MEMBRANE_PEAK_Z"]
    oc_r = PARAMS["OCULUS_RING_RADIUS"]; oc_t = PARAMS["OCULUS_RING_TUBE"]
    spokes = PARAMS["OCULUS_TRUSS_SPOKES"]
    mast_r = PARAMS["MAST_RADIUS"]; cable_r = PARAMS["GUY_CABLE_RADIUS"]
    deck_top = PARAMS["FLOOR_SURFACE_Z"][PARAMS["FLOOR_COUNT"]]
    objs = []

    nmast = PARAMS["MAST_PER_TENT"]
    for mi, m in enumerate(mems):
        px, py = m["peak"]; fl = m["foot_len_y"]; fw = m["foot_wid_x"]
        # --- membrane: ROUNDED-SQUARE scalloped hypar (NOT oval): squircle base
        #     pushed out + edge dipping between masts, peaked at the central oculus ---
        n = 64
        bottom = []
        for i in range(n):
            th = 2 * math.pi * i / n
            ct, st = math.cos(th), math.sin(th)
            # squircle (rounded square) direction, corners at 45deg
            ex = math.copysign(abs(ct) ** 0.5, ct)
            ey = math.copysign(abs(st) ** 0.5, st)
            scallop = 1.0 + 0.10 * math.cos(nmast * th)      # gentle bumps at masts
            x = px + fw * ex * scallop
            y = py + fl * ey * scallop
            # rim dips slightly between masts (subtle catenary), flatter overall
            zr = rim_z - 1.8 * (0.5 - 0.5 * math.cos(nmast * th))
            bottom.append((x, y, zr))
        top = [(px + oc_r*math.cos(2*math.pi*i/n), py + oc_r*math.sin(2*math.pi*i/n), peak_z)
               for i in range(n)]
        objs.append(U.loft_rings(f"JMR_ROOF_MEMBRANE_{mi}_VIS", bottom, top, colls["ROOF"]))
        # --- oculus ring (torus) at peak ---
        objs.append(U.torus(f"JMR_ROOF_OCULUS_{mi}_VIS", px, py, peak_z, oc_r, oc_t,
                            colls["ROOF"], seg=PARAMS["OCULUS_RING_SEG"], tseg=8))
        # --- radial truss spokes across the oculus ---
        for s in range(spokes // 2):
            a = math.pi * s / (spokes // 2)
            p0 = (px + oc_r*math.cos(a), py + oc_r*math.sin(a), peak_z)
            p1 = (px - oc_r*math.cos(a), py - oc_r*math.sin(a), peak_z)
            objs.append(U.strut(f"JMR_ROOF_SPOKE_{mi}_{s}_VIS", p0, p1, 0.12,
                                colls["ROOF"], n=6))
        # --- MAST_PER_TENT masts around the tent perimeter (clear supports) ---
        nmast = PARAMS["MAST_PER_TENT"]
        for k in range(nmast):
            a = 2 * math.pi * k / nmast
            # mast foot just outside the footprint ellipse, on the deck
            mx = px + (fw + 2) * math.cos(a)
            my = py + (fl + 2) * math.sin(a)
            tip_z = rim_z + 10.0          # masts rise above the membrane rim
            base = (mx, my, deck_top); tip = (mx, my, tip_z)
            objs.append(U.strut(f"JMR_ROOF_MAST_{mi}_{k}_VIS",
                                base, tip, mast_r, colls["ROOF"], n=8))
            # guy cable from each mast tip up to the rigid oculus ring
            objs.append(U.strut(f"JMR_ROOF_GUY_{mi}_{k}_VIS",
                                tip, (px + oc_r*math.cos(a), py + oc_r*math.sin(a), peak_z),
                                cable_r, colls["ROOF"], n=4))
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_07 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(7)
    print("[JMR] SCRIPT 07 DONE" if ok else "[JMR] SCRIPT 07 HAS FAILURES")


if __name__ == "__main__":
    main()
