# =============================================================================
# script_04_fan_ramps.py — ROADS from the user's hand-drawn guide (guide_roads.py):
#   BLUE + RED  = roads at the TOP floor level (~48.5 m), connecting to the deck.
#   PURPLE      = ramps descending floor-3 (24.5 m) -> ground (0.5 m): highest near
#                 the BLUE/AQABAH end, lowest near the RED/ULA end.
# Flat/sloped polygon slabs + support piers. All attach to the body.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
import guide_roads as G
P = U.P; PARAMS = U.PARAMS


def _ccw(poly):
    return poly if U.signed_area(poly) > 0 else poly[::-1]


def _piers(ring, tag, ztop_fn, ground, colls, step=42, minh=4.0):
    xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
    out = []; i = 0; y = min(ys)
    while y <= max(ys):
        x = min(xs)
        while x <= max(xs):
            if U.point_in_poly(ring, x, y) and ztop_fn(x, y) - ground > minh:
                out.append(U.cylinder(f"JMR_ROAD_{tag}_PIER_{i}_VIS", x, y, 1.4, 1.4,
                                      ground, ztop_fn(x, y) - 0.4, colls["RAMPS"], n=8))
                i += 1
            x += step
        y += step
    return out


def build(colls):
    U.clear_collection(colls["RAMPS"])
    U.clear_collection(colls["COL_RAMPS"])
    gz = PARAMS["GROUND_Z"]
    z_top = PARAMS["FLOOR_SURFACE_Z"][PARAMS["FLOOR_COUNT"]]   # top floor 48.5
    z_f3 = PARAMS["FLOOR_SURFACE_Z"][3]                        # floor 3 = 24.5
    thick = PARAMS["RAMP_THICKNESS"]
    objs = []

    rail_h = 1.0          # ~1 m road barrier (real-world)
    rail_t = 0.3

    # --- BLUE + RED: flat roads at the TOP floor level ---
    for tag, polys in (("BLUE", G.BLUE_POLYS), ("RED", G.RED_POLYS)):
        for i, poly in enumerate(polys):
            ring = _ccw([tuple(p) for p in poly])
            objs.append(U.polygon_slab(f"JMR_ROAD_{tag}_{i}_VIS", ring, [],
                                       z_top - thick, z_top, colls["RAMPS"]))
            objs.append(U.polygon_slab(f"JMR_ROAD_{tag}_{i}_COL", ring, [],
                                       z_top - 0.25, z_top, colls["COL_RAMPS"]))
            # 1 m barrier railing around the road edge
            rin = U.offset_polygon(ring, rail_t)
            objs.append(U.annulus_slab(f"JMR_ROAD_{tag}_{i}_RAIL_VIS", ring, rin,
                                       z_top, z_top + rail_h, colls["RAMPS"]))
            # invisible collision wall (keeps players/vehicles on the road)
            objs.append(U.annulus_slab(f"JMR_ROAD_{tag}_{i}_RAIL_COL", ring, rin,
                                       z_top, z_top + rail_h + 0.3, colls["COL_RAMPS"]))
            objs += _piers(ring, f"{tag}{i}", lambda x, y: z_top, gz + 0.0, colls)

    # --- PURPLE: ramp floor-3 -> ground (high near +Y/AQABAH, low near -Y/ULA) ---
    y_hi, y_lo = 250.0, -300.0
    def ztop(x, y):
        t = min(1.0, max(0.0, (y - y_lo) / (y_hi - y_lo)))
        return (gz + 0.5) + (z_f3 - (gz + 0.5)) * t
    def zbot(x, y):
        return ztop(x, y) - thick
    for i, poly in enumerate(G.PURPLE_POLYS):
        ring = _ccw([tuple(p) for p in poly])
        objs.append(U.polygon_slab(f"JMR_ROAD_PURPLE_{i}_VIS", ring, [], zbot, ztop,
                                   colls["RAMPS"]))
        objs.append(U.polygon_slab(f"JMR_ROAD_PURPLE_{i}_COL", ring, [],
                                   lambda x, y: ztop(x, y) - 0.25, ztop, colls["COL_RAMPS"]))
        # 1 m barrier railing following the ramp slope
        rin = U.offset_polygon(ring, rail_t)
        objs.append(U.annulus_slab(f"JMR_ROAD_PURPLE_{i}_RAIL_VIS", ring, rin,
                                   ztop, lambda x, y: ztop(x, y) + rail_h, colls["RAMPS"]))
        objs.append(U.annulus_slab(f"JMR_ROAD_PURPLE_{i}_RAIL_COL", ring, rin,
                                   ztop, lambda x, y: ztop(x, y) + rail_h + 0.3, colls["COL_RAMPS"]))
        objs += _piers(ring, f"P{i}", ztop, gz + 0.0, colls)
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_04 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(4)
    print("[JMR] SCRIPT 04 DONE" if ok else "[JMR] SCRIPT 04 HAS FAILURES")


if __name__ == "__main__":
    main()
