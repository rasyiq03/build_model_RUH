# =============================================================================
# jmr_build.py — orchestration: import every phase module and build the whole
# model into the collection tree in ONE session. Used by script_10, script_11,
# and the single-file deliverable build_jamarat_all.py.
# =============================================================================
import importlib
import jmr_util as U

PHASES = [
    "script_01_floor_plates",
    "script_02_columns",
    "script_03_ramp_system",
    "script_04_fan_ramps",
    "script_05_jamrah_pillars",
    "script_06_towers",
    "script_07_tensile_roof",
    "script_08_ground_plaza",
    "script_09_furniture",
]


def build_all(colls):
    """Run every phase build(colls) in order; return list of all emitted objects."""
    all_objs = []
    for name in PHASES:
        mod = importlib.import_module(name)
        objs = mod.build(colls)
        print(f"[JMR] {name}: {len(objs)} objects")
        all_objs += objs
    print(f"[JMR] build_all total objects = {len(all_objs)}")
    return all_objs


def all_jmr_meshes():
    """Every mesh object under JMR_ROOT (visual + collision)."""
    import bpy
    root = bpy.data.collections.get("JMR_ROOT")
    out = []
    if root:
        seen = set()
        for coll in [root] + _descendants(root):
            for o in coll.objects:
                if o.type == "MESH" and o.name not in seen:
                    seen.add(o.name); out.append(o)
    return out


def _descendants(coll):
    out = []
    for c in coll.children:
        out.append(c); out += _descendants(c)
    return out
