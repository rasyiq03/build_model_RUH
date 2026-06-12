# JAMARAT 3D — BUILD REPORT

Status: **COMPLETE [OK]** — all hard gates pass, full model builds in one run.

## The single-file deliverable (what you asked for)
```
"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" ^
    --background --factory-startup --python build_jamarat_all.py
```
Builds the ENTIRE Jamarat model (all phases), assigns materials, validates every
mesh, exports 7 FBX, and saves `state/jamarat_full.blend`. Flags after `--`:
`--no-export`, `--no-save`.

## Result (verified headless, zero tracebacks)
- **374 objects / 291 unique meshes** — every one PASS: ≤20k tris, watertight
  (manifold), no n-gons, has volume, transforms frozen.
- **total 92,164 tris**, 0 meshes over the 20k cap.
- **7 FBX** in `export_fbx/` (~2.74 MB): STRUCTURE, RAMPS, JAMARAT, TOWERS, ROOF,
  GROUND, FURNITURE.
- Render sanity: stadium-oval deck loop + 5 tensile tents + column-grid open
  decks + towers + ramps + Mina BG (`renders/check_*.png`).

## Calibration (Phase R)
- Real OSM fetched (Overpass, way 440922995); published **950×80 m confirmed**
  (OSM 978×88). Clean-oval + silhouette gate (approved). `CALIBRATED=True`.
- User-supplied Tripo rough model cross-checks the layout (`References/rough_ortho/`).
- Decisions: 5 tensile tents, ~12 towers (plain/flared/helipad).

## Architecture
- `PARAMETERS.py` — single source of truth (calibrated TRACE + DETAIL + FBX groups).
- `scripts/jmr_util.py` — scene/collection/geometry/validation helpers.
- `scripts/jmr_build.py` — orchestrator (build_all).
- `scripts/script_00..11_*.py` — each phase runnable standalone (plan→build→
  validate→save state) AND callable by the master via `build(colls)`.
- `skills/blender-run`, `skills/blender-validate` — run/validate contracts.

## Per-script standalone validation (all PASS)
| Script | Emits | Result |
|--------|-------|--------|
| 00 setup | scene, units, 16-collection tree | OK |
| 01 floors | 5 annular decks + COL + fascia + parapet + edge walls (25) | 25 OK |
| 02 columns | master + 3 rings × 5 floors (~1590 cols, 16 meshes) | 16 OK |
| 03 ramps | 2 helical ramps VIS+COL (4) | 4 OK |
| 04 fan ramps | 5 fingers × 2 ends VIS+COL (20) | 20 OK |
| 05 jamrah | 3 walls + basins + platforms + parapets + connectors (114) | 114 OK |
| 06 towers | 12 towers (plain louver / flared / helipad) (25) | 25 OK |
| 07 roof | 5 membranes + oculus tori + spokes + masts + guy cables (80) | 80 OK |
| 08 ground | vertex-color paving slab + COL box (2) | 2 OK |
| 09 furniture | lamp/fan/sign masters + instances + Mina tents (88) | 5 uniq OK |
| 10 materials | 6 mats + UVs + full report | 291 OK |
| 11 export | 7 FBX + poly report | 7 FBX |

## Roblox import notes
- Import at real scale; enable StreamingEnabled.
- COL meshes (in COLLISION collections) → use as collision; set VIS-only parts
  (towers/roof/columns/furniture) CanCollide=false. Decks/ramps: Box fidelity;
  walls/platforms: Hull.

## Known low-fidelity simplifications (honest)
- Jamrah XY + roof + tower placement are reference-derived (not in OSM).
- Tent membranes are solid cone frustums (read as tents; not thin shells).
- Helical ramps are standalone (not yet spliced into each deck edge).
- Paving bands are per-vertex (soft) not crisp decals.
These are refinements, not gate failures.
