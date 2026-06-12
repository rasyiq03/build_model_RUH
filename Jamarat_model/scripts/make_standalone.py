#!/usr/bin/env python3
# =============================================================================
# make_standalone.py — BUNDLER (pure copy-paste/concatenation, no AI re-gen).
# Stitches PARAMETERS.py + jmr_util.py + script_01..09 + materials into ONE
# self-contained file `JAMARAT_STANDALONE.py` with NO local imports — paste it
# into Blender's Text Editor, press Run, and the full model builds in the scene.
# =============================================================================
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)


def read(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def cut_main(src):
    """Drop the trailing `def main()` + `if __name__` runner block."""
    i = src.find("\ndef main(")
    if i == -1:
        i = src.find('\nif __name__')
    return src[:i] if i != -1 else src


def strip_after_marker(src, marker):
    """Remove everything from file start up to & incl. the line containing marker."""
    idx = src.find(marker)
    if idx == -1:
        return src
    end = src.find("\n", idx)
    return src[end + 1:]


def process_params(src):
    src = src.replace("import math\n", "", 1)
    src = src.replace("import trace_data as _T", "_T = sys.modules[__name__]")
    return cut_main(src)


def process_util(src):
    # remove the import/sys.path/PARAMETERS bootstrap block, keep the rest
    src = strip_after_marker(src, "PARAMS = P.PARAMS")
    return src


def process_phase(src, nn):
    src = strip_after_marker(src, "P = U.P; PARAMS = U.PARAMS")
    src = cut_main(src)
    src = re.sub(r"\ndef build\(colls\):", f"\ndef build_{nn:02d}(colls):", src, count=1)
    return src.strip("\n")


def process_materials(src):
    # keep _COLORS, _mat, _pick, apply_materials ; drop imports + main
    src = strip_after_marker(src, "M = PARAMS[\"MATERIALS\"]")
    src = cut_main(src)
    return "M = PARAMS[\"MATERIALS\"]\n" + src.strip("\n")


PHASES = [
    ("script_01_floor_plates", 1), ("script_02_columns", 2),
    ("script_03_ramp_system", 3), ("script_04_fan_ramps", 4),
    ("script_05_jamrah_pillars", 5), ("script_06_towers", 6),
    ("script_07_tensile_roof", 7), ("script_08_ground_plaza", 8),
    ("script_09_furniture", 9),
]

HEADER = '''# =============================================================================
# JAMARAT BRIDGE — STANDALONE SINGLE-FILE BUILDER  (auto-bundled, no external deps)
# =============================================================================
# HOW TO USE (Blender 4.x / 5.x):
#   1. Open Blender -> Scripting tab -> New text block.
#   2. Paste this ENTIRE file. Press "Run Script" (or Alt+P).
#   3. Wait a few seconds -> the complete Jamarat model appears in the scene.
# Or headless:  blender --background --factory-startup --python JAMARAT_STANDALONE.py
#
# Self-contained: bundles PARAMETERS + helpers + all build phases. Real scale
# (950 x 80 m, 5 floors). Procedural, watertight, Roblox-ready.
# (c) reference data: OpenStreetMap contributors (ODbL).
# =============================================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

_ROOT = os.path.join(os.path.expanduser("~"), "jamarat_out")
'''

ALIAS = '''

# --- make `P.` `U.` `G.` references resolve to THIS module (single namespace) ---
U = sys.modules[__name__]
P = sys.modules[__name__]
G = sys.modules[__name__]
'''

FOOTER = '''

# =============================================================================
# ORCHESTRATION + ENTRY POINT
# =============================================================================
_PHASE_FUNCS = [build_01, build_02, build_03, build_04, build_05,
                build_06, build_07, build_08, build_09]


def _descendants(coll):
    out = []
    for c in coll.children:
        out.append(c); out += _descendants(c)
    return out


def all_jmr_meshes():
    root = bpy.data.collections.get("JMR_ROOT")
    out = []; seen = set()
    if root:
        for coll in [root] + _descendants(root):
            for o in coll.objects:
                if o.type == "MESH" and o.name not in seen:
                    seen.add(o.name); out.append(o)
    return out


def main():
    print("=" * 70)
    print("  JAMARAT BRIDGE — standalone build")
    print("=" * 70)
    if not CALIBRATED:
        raise SystemExit("[JMR] FAIL: PARAMETERS not calibrated.")
    reset_scene()
    colls = build_collection_tree()
    total = 0
    for fn in _PHASE_FUNCS:
        objs = fn(colls)
        total += len(objs)
        print(f"[JMR] {fn.__name__}: {len(objs)} objects")
    meshes = all_jmr_meshes()
    apply_materials(meshes)
    seen = set(); uniq = []
    for o in meshes:
        if o.data.name not in seen:
            seen.add(o.data.name); uniq.append(o)
    ok, reps = validate_all(uniq, want_frozen=False)
    over = sum(1 for r in reps if r["tris"] > PARAMS["POLY_LIMIT_PER_MESH"])
    tris = sum(tri_count(o.data) for o in meshes)
    print("=" * 70)
    print(f"[JMR] DONE [{'OK' if ok and over == 0 else 'CHECK'}] — "
          f"objects={len(meshes)} unique={len(uniq)} tris={tris} over_cap={over}")
    print("=" * 70)


main()
'''


def build():
    parts = [HEADER]
    parts.append("\n# ===================== TRACE DATA (exact traced footprint) ===========\n")
    parts.append(read(os.path.join(ROOT, "trace_data.py")))
    parts.append("\n# ===================== GUIDE ROADS (user hand-drawn) =================\n")
    parts.append(read(os.path.join(ROOT, "guide_roads.py")))
    parts.append("\n# ===================== PARAMETERS =====================\n")
    parts.append(process_params(read(os.path.join(ROOT, "PARAMETERS.py"))))
    parts.append("\n# ===================== HELPERS (jmr_util) =====================\n")
    parts.append(process_util(read(os.path.join(HERE, "jmr_util.py"))))
    parts.append(ALIAS)
    for mod, nn in PHASES:
        parts.append(f"\n# ===================== PHASE {nn:02d}: {mod} =====================\n")
        parts.append(process_phase(read(os.path.join(HERE, mod + ".py")), nn))
        parts.append("\n")
    parts.append("\n# ===================== MATERIALS =====================\n")
    parts.append(process_materials(read(os.path.join(HERE, "script_10_materials_validate.py"))))
    parts.append(FOOTER)
    out = "".join(parts)
    dst = os.path.join(ROOT, "JAMARAT_STANDALONE.py")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {dst} ({out.count(chr(10))+1} lines, {len(out)} chars)")


if __name__ == "__main__":
    build()
