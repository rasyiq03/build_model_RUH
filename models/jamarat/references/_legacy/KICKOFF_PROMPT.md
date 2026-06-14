# KICKOFF_PROMPT.md — Paste this into Claude Code to start the build (v2)

Gives you: (1) repo + environment setup incl. the `references/` folder, (2) the
exact kickoff prompt, (3) the iteration contract, (4) a ready Overpass query for
the real OSM coordinates. `AGENTS.md` + `PARAMETERS.py` live in the repo root.

---

## 1. Repo layout (create this BEFORE the first prompt)

```
jamarat-3d/
  AGENTS.md            # agent operating manual (rules — read first)
  PARAMETERS.py        # single source of truth for numbers
  PARAMETERS.md        # human doc, regenerated from .py
  references/          # <-- PUT ALL REFERENCE MATERIAL HERE
    img_01_aerial.png ... img_08_topdown.png   # the 8 renders
    sketchfab_top.png  sketchfab_front.png  sketchfab_side.png  # ortho caps (optional)
    osm/jamarat.osm    # OSM export (real coordinates)
  scripts/             # script_00 .. script_11 (agent writes)
  skills/
    blender-run/SKILL.md
    blender-validate/SKILL.md
  export_fbx/          # output FBX
  state/               # .blend snapshots between phases
```

The agent MUST analyze every image in `references/` before modeling (Phase R
Step 0). Drop the 8 renders + any Sketchfab ortho caps + the OSM export there.

Environment: Blender 4.x on PATH. Headless pattern:

```
blender --background --factory-startup --python scripts/script_NN.py
blender --background state/after_NN.blend --python scripts/script_MM.py   # chained
```

---

## 2. THE KICKOFF PROMPT  (copy everything in this block)

```
You are the Jamarat 3D build agent. Read AGENTS.md and PARAMETERS.py in full
first; AGENTS.md is your operating manual and overrides default habits.

GOAL: procedurally build a modular, Roblox-ready 3D model of the Jamarat Bridge
(Mina) for a playable lempar-jumrah simulation, export as multi-FBX, at REAL
scale (950 x 80 m, 5 floors x 12 m). The final shape must match the references
(operationally: pass the fidelity gate in AGENTS.md Phase R / section 12 —
metric XY match to OSM + per-image render match + human sign-off).

DO THIS IN ORDER:
1. PHASE R STEP 0 — Open and analyze EVERY image in references/ (you have vision).
   Write a per-element inventory (form + which image + build method from
   AGENTS.md section 4). Do not model until this is written and matches section 4.
2. PHASE R XY — Read references/osm/jamarat.osm. Reproject node lat/long to local
   meters (origin at footprint centroid; equirectangular; x scaled by cos(lat)).
   Derive deck outline, road/ramp centerlines, and the 3 jamarah XY positions.
   Cross-check against the published 950 x 80 m. (If the .osm is missing, ask me
   to provide it or run the Overpass query in KICKOFF_PROMPT.md section 4.)
3. PHASE R Z/FORM — From the Sketchfab ortho caps + the 8 renders, read heights
   and cross-section shapes (elliptical jamrah walls, conical roof + oculus ring,
   tower flare/louver/helipad, fan ramps). Front/side give Z; top cross-checks XY.
4. Fill PARAMETERS.TRACE (meters, origin at footprint center) — every field.
5. VERIFICATION GATE: (a) overlay traced skeleton on OSM footprint, deviation
   <= FIDELITY tolerance (5 m AND 1%); (b) render-match each references/ image
   from the same angle, fix until no structural difference; (c) get my sign-off.
   Only then set CALIBRATED = True. Never fabricate a layout number to proceed.
6. Set up skills/blender-run + skills/blender-validate. Use TodoWrite for
   scripts 00..11. For each: plan -> write -> run headless -> fix any traceback
   -> validate (tri<=20k, watertight, no N-gon, volume, frozen transforms) ->
   save state -> next. Parallelize independent phases (towers, roof, furniture)
   with subagents; keep floors->columns->ramps->pillars sequential.
7. Build only allowed methods (AGENTS.md section 7): annular ring by bridging
   edge loops, NEVER boolean; membranes/cables have real volume.

Start with Phase R Step 0 now: list the references/ files, analyze each, and give
me the element inventory + your read of the OSM/published dimensions BEFORE
writing any script. Then propose the plan for script_00.
```

---

## 3. Iteration contract (paste if the agent drifts)

```
Gate reminder: a script is done only after it runs headless with zero tracebacks
AND blender-validate reports PASS for every mesh. Calibration is done only after
the fidelity gate (OSM overlay <= tol, per-image render match, my sign-off). If a
mesh exceeds 20k tris, split it (by loose parts / material), don't decimate away
detail. Show me the validation table and the render-match pairs each time. Report
the measured deviation honestly; do not claim 100% without the gate passing.
```

---

## 4. Overpass query for the real OSM data (run at overpass-turbo.eu, Export -> GeoJSON/.osm)

```
[out:json][timeout:90];
(
  way["building"](21.4155,39.8665,21.4275,39.8795);
  relation["building"](21.4155,39.8665,21.4275,39.8795);
  way["highway"](21.4155,39.8665,21.4275,39.8795);
  way["man_made"="bridge"](21.4155,39.8665,21.4275,39.8795);
);
out body; >; out skel qt;
```

Centered on 21.42139 N, 39.87278 E (Jamaraat Bridge, OSM way 440922995). Save the
result to references/osm/jamarat.osm. Attribution: © OpenStreetMap contributors.


---

## 5. Subagent hint & acceptance

Sequential: R -> 00 -> 01 floors -> 02 columns -> 03 ramps -> 04 fan ramps ->
05 pillars/basins/platforms/connectors. Parallel-safe after 01: 06 towers,
07 roof, 08 ground, 09 furniture. Last: 10 materials+validate, 11 export.

Before "finished": agent confirms AGENTS.md section 12 line by line, attaches the
poly report per FBX, the OSM overlay image, and the render-match pairs for each
references/ image.
