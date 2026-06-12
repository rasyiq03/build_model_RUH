---
name: blender-validate
description: Validate every emitted Jamarat mesh against the Roblox hard rules (AGENTS §3).
---

# blender-validate

Per-mesh validation used by every build script and by `script_10`. Implemented in
`scripts/jmr_util.py::validate(obj)`; this skill documents the contract.

## Checks (AGENTS §3 — all must hold)
| Check | Rule | Method (jmr_util) |
|-------|------|-------------------|
| Tri count | ≤ 20000 (warn ≥ 19500) | `tri_count(mesh)` = Σ(len(poly.verts)-2) |
| Watertight | no non-manifold / open edges | bmesh: every edge has exactly 2 link_faces |
| No N-gons | all faces ≤ 4 verts | `any(len(p.vertices) > 4)` |
| Has volume | non-zero bbox in all 3 axes + has faces | bbox min-dim > 1e-4 |
| No degenerate faces | face area > 1e-7 | bmesh face.calc_area() |
| Transforms frozen | scale=(1,1,1), rot=(0,0,0) | compare with tolerance |

## Output
`validate(obj)` returns a dict and prints one line:
```
[JMR] OK   JMR_FLOOR_L1_VIS         tris=15990 manifold=1 ngon=0 vol=1 xform=1
[JMR] FAIL JMR_PILLAR_WUSTA_VIS     tris=21044 (> 20000)
```
`validate_all(collection)` prints a table and returns True only if every mesh PASSES.

## Gate
If any mesh FAILS, the script must not be considered done. Fix the root cause
(split by loose parts/material if over tri cap — never decimate hero detail away)
and re-run headless until the whole table is OK/WARN.
