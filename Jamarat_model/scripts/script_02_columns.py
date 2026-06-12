# =============================================================================
# script_02_columns.py — master square column + instanced grid on 3 rings/floor.
# Columns joined per ring+floor into single meshes (low object count, tri-safe).
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
P = U.P; PARAMS = U.PARAMS


def build(colls):
    U.clear_collection(colls["COLUMNS"])
    t = PARAMS["TRACE"]
    body = list(t["BODY_OUTER"])
    holes = [list(h) for h in t["BODY_HOLES"]] + [list(t["OCULUS"][k]) for k in t["OCULUS"]]
    size = PARAMS["COLUMN_SIZE"]; inset = PARAMS["COLUMN_RING_INSET"]
    spacing = PARAMS["COLUMN_SPACING"] * 1.6
    body_in = U.offset_polygon(body if U.signed_area(body) > 0 else body[::-1], inset + 2)
    objs = []

    # master prototype (naming requirement; ≤200 tri)
    master = U.box("JMR_COLUMN_MASTER", 0, 0, 6, size, size, 12.0, colls["COLUMNS"])
    objs.append(master)

    # column grid: sample a lattice clipped to the (organic) deck body, away from holes
    xs = [p[0] for p in body]; ys = [p[1] for p in body]
    gx0, gx1 = min(xs), max(xs); gy0, gy1 = min(ys), max(ys)
    grid = []
    y = gy0 + spacing / 2
    while y < gy1:
        x = gx0 + spacing / 2
        while x < gx1:
            if U.point_in_poly(body_in, x, y) and not any(U.point_in_poly(h, x, y) for h in holes):
                grid.append((x, y))
            x += spacing
        y += spacing

    for f in range(1, PARAMS["FLOOR_COUNT"] + 1):
        z0 = PARAMS["FLOOR_SURFACE_Z"][f]
        h = PARAMS["FLOOR_GAP"] - PARAMS["FLOOR_HEIGHT"]   # 12 - 0.5
        cz = z0 + h / 2
        specs = [(x, y, cz, size, size, h) for (x, y) in grid]
        m = U.multi_box_mesh(f"JMR_COLUMN_L{f}_GRID_VIS", specs, colls["COLUMNS"])
        objs.append(m)
    return objs


def main():
    U.reset_scene()
    colls = U.build_collection_tree()
    objs = build(colls)
    ncol = sum(len(o.data.polygons) // 6 for o in objs if "MASTER" not in o.name)
    print(f"[JMR] script_02 emitted {len(objs)} meshes (~{ncol} columns)")
    ok, _ = U.validate_all(objs)
    U.save_state(2)
    print("[JMR] SCRIPT 02 DONE" if ok else "[JMR] SCRIPT 02 HAS FAILURES")


if __name__ == "__main__":
    main()
