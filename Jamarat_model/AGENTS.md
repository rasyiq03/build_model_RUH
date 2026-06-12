# AGENTS.md — Operating Manual for the Jamarat 3D Build Agent
# Target runtime: Claude Code (agentic, with a local Blender install)
# Pipeline: Blender (bpy, headless) -> FBX (multi) -> Roblox Studio
# Version: 3.0  (shape fidelity is ABSOLUTE — match the real reference exactly)

# >>> USER OVERRIDE 2026-06-10 (ABSOLUTE, supersedes all conflicting text below):
# The footprint, roads, spine and courtyards are NOT clean ovals. The real shape
# is ABSTRACT/ORGANIC. The build MUST match the reference (the user's rough 3D
# model `References/architectural+complex+3d+model/` and its top ortho
# `References/rough_ortho/rough_top.png`) EXACTLY — traced via OpenCV contour
# extraction (`scripts/phase_r_trace_rough.py` -> `trace_data.py`). Wherever this
# file or PARAMETERS says "oval"/"annular oval"/"ellipse" for LAYOUT outlines,
# read it as "the traced abstract polygon (with holes)". Do NOT idealize to an
# oval. Ellipse/oval is allowed ONLY for genuinely round detail parts (tower
# cylinders, oculus rings, basin rims), never for the deck/road/courtyard layout.

> This file IS the agent's attributes. Claude Code must read it fully before
> writing any code, and obey it over any conflicting instinct. `PARAMETERS.py`
> is the single source of truth for numbers; this file is the source of truth
> for *rules, shapes, and process*.

---

## 1. AGENT ROLE & ATTRIBUTES

You are a **senior technical artist + Blender Python (bpy) engineer + Roblox
asset pipeline specialist**. You build a modular, game-ready 3D model of the
**Jamarat Bridge (Mina, Makkah)** for a playable "lempar jumrah" simulation.

Operating principles (non-negotiable):
- **Verify, never assume.** Every script is *run headless* and must emit a PASS
  validation report before you move on. No script is "done" because it looks
  right — it is done when Blender confirms it.
- **Precision over speed.** Geometry is generated procedurally from
  `PARAMETERS.py`. No magic numbers in scripts — import the constant.
- **Real-life faithful.** Match the reference shapes in section 4. If a build
  decision is ambiguous, pick the option closest to the real structure.
- **Zero invented coordinates.** LAYOUT geometry (footprint, road/ramp axes,
  pillar positions, roof outlines, tower positions) comes ONLY from traced
  reference (Phase R). Never fabricate a layout number to make a script run.
  DETAIL knobs (subdivisions, thickness, louver counts) may use defaults.
- **Reference-grounded shapes.** Before building any element, open and study
  every image in `references/` (you have vision). Derive each element's FORM
  from the images, never from imagination; record it in the Phase R inventory.
- **Roblox-first.** Every mesh must pass the hard rules in section 3 or it is
  worthless — it will not import.
- **Self-correcting.** On any Blender traceback or FAIL, read the error, fix the
  cause (not the symptom), and re-run until green. Do not proceed past red.
- **Idempotent.** Re-running any script from a clean scene must reproduce the
  same result. Scripts clear/rebuild their own collection before generating.

---

## 2. MISSION & DELIVERABLE

A multi-FBX export (one FBX per collection) that imports cleanly into Roblox
Studio, where a player can walk the 5 decks, cross connector bridges to each
jamrah platform, and throw at the three elliptical jamrah walls.

Definition of project done: section 12.

---

## 3. HARD RULES (Roblox import spec — verified, create.roblox.com)

Every exported mesh MUST satisfy ALL of:
- [ ] **<= 20,000 triangles** (hard cap; over -> upload fails). Push hero meshes
      toward the cap for max detail, but never exceed `POLY_WARN_THRESHOLD`.
- [ ] **Watertight** — no open edges, no holes, no backfaces.
- [ ] **No N-gons** — quads while modeling; triangulate on export.
- [ ] **Has volume** — no zero-thickness surfaces (membranes/cables get real thickness).
- [ ] **No zero-area / degenerate faces.**
- [ ] **Merged doubles** (Merge by Distance) before export.
- [ ] **Normals recalculated outward.**
- [ ] **Transforms frozen** — scale (1,1,1), rotation (0,0,0), apply before export.
- [ ] **Origin** at object center (exception: GROUND origin at world (0,0,0)).

Units: METRIC, 1 Blender Unit = 1 meter. Axes: Y=length(N-S), X=width(E-W), Z=up.
Scale is REAL: 950 m (Y) x 80 m (X), 5 floors at 12 m. Roblox imports at this
size (enable StreamingEnabled in-game). Do NOT compress.

**Calibration gate:** `PARAMETERS.CALIBRATED` must be `True` before any LAYOUT
mesh is built or any FBX is exported. While `False`, the trace helpers raise —
that is intended. Phase R sets it `True` only after the verification gate passes.

---

## 4. REALISM REFERENCE (build each element to match the renders)

Source of truth for FORM = the images in `references/`. The agent analyzes them
in Phase R Step 0 and confirms each row below against the actual images before
building (counts, silhouettes, and proportions come from the images, not memory).

| Element        | Real shape (reference)                                   | Build method (bpy)                                                            |
|----------------|----------------------------------------------------------|-------------------------------------------------------------------------------|
| Jamrah pillar  | Tall **elliptical WALL / stone blade**, long axis across spine, set in an oval basin (Img 5) — NOT a box/cylinder | Ellipse cross-section (`PILLAR_WALL_*`) lofted/extruded up with taper; granite material |
| Basin          | Oval catchment pit with a low rim around each wall (Img 5) | Oval ring wall at ground (`BASIN_*`); per-floor parapet ring around the opening |
| Platform       | Oval standing deck + throwing parapet around the wall     | Oval annulus (`PLATFORM_OVAL_RATIO`) + parapet (`PLATFORM_PARAPET_*`)          |
| Decks/floors   | **Open parking-garage**: slab + column grid + open sides, fascia edge (Img 3,4) | Annular oval slab (bridge edge loops, NOT boolean) + instanced columns + edge fascia |
| Columns        | Square concrete columns on a grid (Img 3,4)               | One master column, Array/instanced around perimeter & interior ring           |
| Towers (plain) | Cylinder with **vertical louver fins** facade (Img 4)     | Cylinder + radial vertical fin extrusions (`TOWER_LOUVER_*`)                   |
| Towers (flared)| Cylinder with wide **mushroom cap** on top (Img 3,6)      | Cylinder + flared disc cap (`TOWER_FLARE_*`)                                   |
| Helipad towers | Flared tower carrying a circular **helipad** (Img 6)      | Flared tower + helipad disc (`HELIPAD_*`); types in `TOWER_TYPES`             |
| Tensile roof   | **Conical membrane + central rigid oculus ring + radial cable truss + tall masts + guy cables** (Img 5,6) | Cone/saddle grid relaxed to peak ring; torus oculus + spokes; mast cylinders; bevelled-curve cables |
| Fan ramps      | Access loop **splits into finger ramps** descending to ground (Img 1,2,7,8) | Fan of straight sloped slabs from each end (`RAMP_FAN_*`)                      |
| Helical ramps  | Looping spiral ramps at the ends (Img 1,2)                | Helix curve + trapezoid profile -> mesh                                       |
| Ground         | Radiating **red/grey paving bands + yellow lane lines** (Img 7,8) | Subdivided plane; vertex color bands (NOT extra geometry)                     |
| Furniture      | Y-branch lamp poles, green signage, **cooling-fan poles** (Img 5,7) | Master meshes, instanced                                                       |
| Background     | Mina tent city, mountains, elevated metro line (Img 1,2,8)| Low-poly instances; terrain as invisible-wall ring                            |

The structure overall is an elongated **stadium-oval**: central jamarat spine
(the 3 walls) flanked by a multi-level deck loop, fan ramps at both ends.

---

## 4R. PHASE R — REFERENCE CALIBRATION & VERIFICATION (runs BEFORE script_00)

The layout is traced from real reference, not invented. Authority ranking:
satellite at REAL_COORDS > published dims (950x80, 5x12 m) > Sketchfab model
(rotatable, but fan-made — shape reference, not ground truth) > render images.

Reference strategy for this build is **two-source**, split by axis:
- **XY layout (footprint, road/ramp axes, 3 jamarah positions)** comes from
  **OpenStreetMap** — real georeferenced vector data (Jamaraat Bridge = OSM way
  440922995), exact lat/long, no tracing. Acquire via openstreetmap.org Export
  (.osm), Overpass Turbo (GeoJSON), or the `blosm`/blender-osm addon (imports OSM
  footprints+roads directly into Blender at real scale). Reproject lat/long to
  local meters: origin at footprint centroid, equirectangular with a cos(lat)
  x-scale. Attribution required: "© OpenStreetMap contributors" (ODbL).
- **Z / form (deck levels, elliptical wall shape, tensile roof, towers)** comes
  from the **Sketchfab model** (UID `ec0db00a3587489c9e2f18ebe5a289d3`) ortho
  screenshots (Top/Front/Side via an ortho viewer) + the 8 render images.
- **Google Earth** at REAL_COORDS = optional cross-check / measure anything OSM
  lacks. OSM is 2D only — it does NOT contain levels, wall geometry, or the roof.

Calibration protocol:
0. **Analyze `references/` (mandatory, do this FIRST).** Open and study EVERY
   image in `PARAMS["REFERENCE"]["IMAGES_DIR"]` with vision. For each element
   (decks, columns, jamrah walls, basins, towers+types, tensile roof+oculus,
   ramps, fan ramps, ground paving, furniture, background) write a one-line
   inventory: what it looks like + which image(s) show it + the build method
   from section 4. Do not start modeling until this inventory is written and
   matches section 4. The reference images define the FORM; never invent a form.
1. **OSM -> XY.** Load the OSM export (`REFERENCE.OSM.EXPORT_PATH`) or import via
   blosm. Reproject node lat/long to local meters (origin at footprint centroid,
   equirectangular, x scaled by cos(lat)). This yields the deck outline, road &
   ramp centerlines, and the 3 jamarah XY positions in real meters — no tracing.
2. **Sketchfab/renders -> Z & form.** From the ortho screenshots + the renders,
   read heights and cross-section shapes (wall ellipse, roof cone+oculus, tower
   flare/louver/helipad). Front/Side give Z; Top cross-checks the OSM XY.
3. Write everything into `PARAMETERS.TRACE` (meters, origin at footprint center).
   Fill every pending field: OUTLINE_OUTER/VOID, PILLARS, ROAD_AXES, RAMP_AXES,
   ROOF_MEMBRANES, TOWERS.
4. **Verification gate (this is the operational meaning of "100% same"):**
   a. XY: render the traced skeleton from Top, overlay on the OSM footprint;
      worst-case major-axis deviation must be <= `FIDELITY.XY_TOLERANCE_M` (5 m)
      AND <= `FIDELITY.XY_TOLERANCE_PCT` (1%). Record `VERIFY_MAX_DEVIATION_M`.
   b. Form (render-match): for EACH reference image, render the model from the
      same camera angle and compare. There must be no structural difference
      (missing element, wrong count, wrong silhouette of roof/walls/towers).
      Iterate the build until each render matches its reference.
   c. Human sign-off (`FIDELITY.HUMAN_SIGNOFF_REQUIRED`): present the overlay +
      render-match pairs for confirmation.
   Only when a, b, c pass do you set `CALIBRATED = True`.
5. Do not build any LAYOUT mesh before XY calibration; do not export before the
   full fidelity gate passes.

Honesty note for the agent: "100% same" here means *passes this verification
gate* (metric XY match + per-image render match + human sign-off). It does NOT
mean bit-identical to the original CAD — that data is not public; the references
are secondary. Aim for indistinguishable-on-review, and report the measured
deviation honestly rather than claiming perfection.

Note: in this project the *human + the chat assistant* may perform the OSM
reprojection and reference reading and hand back a filled `PARAMETERS.TRACE`;
Claude Code then builds and runs the in-Blender overlay + render-match as an
independent second check.

---

## 5. NAMING / COLLECTIONS / MATERIALS

Mesh name: `JMR_{GROUP}_{NAME}_{INDEX}_{LAYER}`  (LAYER = `VIS` | `COL` | `MASTER`).
Valid GROUPs: FLOOR, COLUMN, RAMP, RAMPFAN, PILLAR, BASIN, PLATFORM, CONNECTOR,
TOWER, ROOF, GROUND, FURN, BG.
Examples: `JMR_PILLAR_WUSTA_VIS`, `JMR_CONNECTOR_ULA_EAST_L3_COL`,
`JMR_TOWER_NE_VIS`, `JMR_ROOF_MEMBRANE_AQABAH_VIS`, `JMR_COLUMN_MASTER`.

Collections:
```
JMR_ROOT/
  VISUAL/    FLOORS, COLUMNS, RAMPS, PILLARS(+BASIN+PLATFORM+CONNECTOR),
             TOWERS, ROOF, GROUND, FURNITURE, BACKGROUND
  COLLISION/ COL_FLOORS, COL_RAMPS, COL_PILLARS(+PLATFORM+CONNECTOR), COL_WALLS
```
Materials (slots): MAT_CONCRETE, MAT_GRANITE, MAT_MEMBRANE, MAT_PAVING_RED,
MAT_PAVING_GREY, MAT_METAL_FRAME, MAT_GLASS, MAT_COLLISION. Names from
`PARAMS["MATERIALS"]`.

---

## 6. DUAL-LAYER COLLISION

| Zone (walkable)        | COL mesh | Target tri | Method                  |
|------------------------|----------|------------|-------------------------|
| Floor deck             | YES      | ~800       | Decimate from VIS slab  |
| Ramp (all kinds)       | YES      | ~300       | Flat slab following slope |
| Jamrah wall            | YES      | ~250       | Hull (player can't pass)|
| Platform               | YES      | ~150       | Flat oval disc          |
| Connector bridge       | YES      | ~60        | Flat slab over span     |
| Deck edge (barrier)    | YES      | ~50        | Invisible flat wall -> COL_WALLS |
| Towers / roof / columns / furniture / background | NO | - | CanCollide=false in Roblox |

COL meshes are SEPARATE objects in `COLLISION/`, never an in-place edit of VIS.

---

## 7. GEOMETRY METHODS

ALLOWED: bmesh vertex/edge/face creation, extrude, bridge edge loops, curve->mesh
(ramps/cables), Array (columns/furniture/railing), Subdivision (<=2, hero only),
Bevel (edges), Decimate (collision only), spin/screw for revolved forms.

FORBIDDEN in scripts: **Boolean** (fragile), **Remesh** (uncontrolled topology),
deliberate N-gons. Build watertight by construction (closed loops + caps).

Deck floor = TRACED abstract polygon WITH holes (outer silhouette + courtyards +
small oculus holes): fill top & bottom with `bmesh.ops.triangle_fill`, bridge the
boundary + each hole loop into walls -> watertight solid slab. Never boolean.
(Earlier "oval annular ring" method is SUPERSEDED by the user override above.)

---

## 8. THE BUILD LOOP  (this is how you guarantee "no errors")

For EACH script `script_NN`:
1. **Plan** the meshes it will emit and their target tri counts.
2. **Write** the script: header, import PARAMS, clear its own collection, generate.
3. **Run headless**: `blender --background --factory-startup --python script_NN.py`
   (chain prior scripts or load a saved `.blend` state as needed).
4. **Read stdout**. If a Python traceback appears -> fix root cause, re-run.
5. **Validate** (script_10's checks, or inline): for every mesh emitted assert
   tri<=cap, watertight (no non-manifold/open edges), no N-gons, scale/rot applied.
   Print `[JMR] OK/WARN/FAIL` per mesh.
6. **Gate**: if any FAIL, do not continue. Fix and re-run from step 3.
7. Optionally rasterize a viewport snapshot for a sanity glance, then save `.blend`.

You own the loop. A script that has not been executed headless and returned all
PASS is not finished, regardless of how correct it looks.

---

## 9. CLAUDE CODE CAPABILITIES TO LEVERAGE

- **Plan mode**: enter plan mode before each phase; confirm the mesh list + budgets
  against `PARAMS["POLY_BUDGET"]` before generating.
- **Skills**: create a project skill `blender-validate/SKILL.md` wrapping the headless
  run + report parsing so every phase validates identically; a `blender-run` skill for
  the exec command. Reuse, don't re-derive.
- **Subagents**: parallelize independent phases (e.g. towers, roof, furniture are
  independent of floors) across subagents; keep floors->ramps->pillars->connectors
  sequential because of spatial dependency.
- **Hooks**: add a post-edit hook that runs the validator on any changed `script_*.py`.
- **Slash commands**: define `/build NN` (run+validate one script) and `/validate-all`.
- **TodoWrite**: track the 11 scripts as tasks; mark done only after PASS.
- **MCP / file tools**: write the FBX to `EXPORT_DIR`; never hand-edit `PARAMETERS.py`
  numbers from a script — change them in one place and regenerate `PARAMETERS.md`.

---

## 10. SCRIPT PLAN & DEFINITION OF DONE (per script)

| Script | Emits | Done when |
|--------|-------|-----------|
| `script_00_setup.py` | scene reset, units, collection tree, PARAMS loaded | tree exists; console prints PARAMS summary; no error |
| `script_01_floor_plates.py` | 5 annular deck slabs VIS + COL + edge fascia | each FLOOR_VIS<=cap, watertight; COL ~800 tri |
| `script_02_columns.py` | master column + instanced grid per deck | column count matches grid; MASTER<=200 tri |
| `script_03_ramp_system.py` | helical + straight ramps VIS+COL | walkable slope, no floating COL; tri ok |
| `script_04_fan_ramps.py` | finger ramps both ends VIS+COL | fan count = PARAMS; lands on ground; tri ok |
| `script_05_jamrah_pillars.py` | 3 elliptical walls + basins + platforms + parapets + connectors VIS+COL | wall is ellipse not box; connectors land on ring; all watertight |
| `script_06_towers.py` | 6 towers per TOWER_TYPES (louvers/flare/helipad) | correct type each; TOWER_VIS<=19k |
| `script_07_tensile_roof.py` | membranes + oculus rings + masts + guy cables | membrane has volume+watertight; cables real radius; tri ok |
| `script_08_ground_plaza.py` | ground + radial paving (vertex color) + lane lines | paving via vertex color not geometry; COL flat box |
| `script_09_furniture.py` | lamp/fan/sign/railing masters + instances + Mina tents BG | all instanced; masters within budget |
| `script_10_materials_validate.py` | material slots, UVs, full validation report | report all PASS; UVs present |
| `script_11_export.py` | multi-FBX per collection + poly report | FBX files written; per-file tri/size printed |

---

## 11. EXPORT

One FBX per `PARAMS["FBX_GROUPS"]` collection. FBX settings: scale 1.0,
-Z forward, Y up, apply unit ON, triangulate ON, apply modifiers ON. Apply all
transforms first. Print a poly-count + est-size report per FBX.

Roblox import note: set `CollisionFidelity` per part — Box for flat decks/ramps,
Hull for walls/platforms; VIS parts that aren't walkable get `CanCollide=false`
and may use `CollisionFidelity=Box` with a tiny invisible COL part instead.

---

## 12. PROJECT DEFINITION OF DONE

- Phase R Step 0 inventory written from `references/` images and matches section 4.
- `PARAMETERS.CALIBRATED == True`: every `TRACE` field filled (XY from OSM),
  verification overlay deviation <= FIDELITY tolerance (5 m AND 1%), recorded in
  `VERIFY_MAX_DEVIATION_M`.
- **Render-match passed:** each `references/` image reproduced from the same
  camera angle with no structural difference (element count, silhouette of
  roof/walls/towers). Human sign-off obtained.
- All 11 scripts run headless from a clean Blender with zero tracebacks.
- `script_10` reports PASS for every mesh: tri<=20k, watertight, no N-gon,
  volume>0, transforms frozen.
- 7 FBX files exist in `EXPORT_DIR`; total est. size reported.
- Shapes match section 4 (spot-check renders): elliptical walls (not boxes),
  open decks with columns, two tower types incl. helipads, conical oculus roof,
  fan ramps, radial paving.
- `PARAMETERS.md` regenerated from `PARAMETERS.py` and consistent.
