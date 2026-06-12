# =============================================================================
# script_01_floor_plates.py — 5 SOLID walkable decks on the TRACED abstract body
# (NOT an oval) with small OCULUS holes at the 3 jamarah + courtyard holes.
# Build = bmesh triangle_fill polygon-with-holes -> watertight solid slab.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def _ccw(poly):
    return poly if U.signed_area(poly) > 0 else poly[::-1]


def build(colls):
    U.clear_collection(colls["FLOORS"])
    U.clear_collection(colls["COL_FLOORS"])
    U.clear_collection(colls["COL_WALLS"])
    t = PARAMS["TRACE"]
    # Floors = the genuine 5-floor DECK BODY (central mass). The long finger/arm
    # extensions are flyover ROADS (built sloped in script_04), NOT stacked floors.
    body = _ccw(list(t["BODY_OUTER"]))
    body_holes = [list(h) for h in t["BODY_HOLES"]]
    oculus = [list(t["OCULUS"][k]) for k in t["OCULUS"]]
    # holes must wind opposite to outer for triangle_fill; normalize to CW
    holes = []
    for h in body_holes + oculus:
        holes.append(h if U.signed_area(h) < 0 else h[::-1])
    deck_holes = holes
    fasc = PARAMS["FLOOR_EDGE_FASCIA"]
    rail_in = U.offset_polygon(body, 0.8)
    objs = []

    for f in range(1, PARAMS["FLOOR_COUNT"] + 1):
        z0 = PARAMS["FLOOR_Z"][f]
        z1 = PARAMS["FLOOR_SURFACE_Z"][f]

        # --- VIS: solid traced deck with oculus + courtyard holes ---
        objs.append(U.polygon_slab(f"JMR_FLOOR_L{f}_VIS", body, deck_holes,
                                   z0, z1, colls["FLOORS"]))
        # --- fascia downstand along the (organic) outer edge ---
        objs.append(U.annulus_slab(f"JMR_FLOOR_L{f}_FASCIA_VIS", body, rail_in,
                                   z0 - fasc, z0, colls["FLOORS"]))
        # --- perimeter safety rail (low parapet around the deck edge) ---
        objs.append(U.annulus_slab(f"JMR_FLOOR_L{f}_RAIL_VIS", body, rail_in,
                                   z1, z1 + 1.1, colls["FLOORS"]))
        # --- COL: solid walkable slab (same footprint, thin) ---
        objs.append(U.polygon_slab(f"JMR_FLOOR_L{f}_COL", body, deck_holes,
                                   z1 - 0.3, z1, colls["COL_FLOORS"]))
        # --- COL outer edge barrier wall ---
        objs.append(U.annulus_slab(f"JMR_FLOOR_L{f}_EDGEWALL_COL", body, rail_in,
                                   z1, z1 + 1.4, colls["COL_WALLS"]))
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    print(f"[JMR] script_01 emitted {len(objs)} meshes")
    ok, _ = U.validate_all(objs)
    U.save_state(1)
    print("[JMR] SCRIPT 01 DONE" if ok else "[JMR] SCRIPT 01 HAS FAILURES")


if __name__ == "__main__":
    main()
