# AGENTS.md — RUH Master Operating Manual
# Project: RUH — a playable Hajj & Umrah simulator
# Pipeline: Blender (bpy, headless) -> FBX (per collection) -> Roblox Studio
# Scope: MODEL-AGNOSTIC. This file governs HOW every complex model is built.
# Version: 1.0

> **This file is the constitution.** Claude Code must read it fully before
> writing any code, and obey it over any conflicting instinct.
>
> It does **not** describe any single model. Each concrete model (Jamarat,
> Kaaba & Masjid al-Haram, Sa'i / Safa–Marwa, Mina tents, Arafat, zamzam
> stations, …) gets its **own** spec at `models/<model>/AGENTS.md`, **generated
> from the template in §10**. Numbers for a model live only in that model's
> `PARAMETERS.py`.
>
> **Precedence (highest wins):**
> 1. An explicit instruction from the user in chat.
> 2. The model's own `models/<model>/AGENTS.md` (incl. its `USER OVERRIDE` block).
> 3. This master file.
> 4. Tool defaults / the agent's own instinct.

---

## 0. WHAT RUH IS

A modular, game-ready 3D world for a Hajj & Umrah simulation. Players walk real
locations and perform rites (e.g. lempar jumrah, tawaf, sa'i). Every location is
a **model**: a self-contained Blender build that exports to Roblox. This manual
makes every model come out the same disciplined way, so the result is reliable
and each piece is independently verifiable.

---

## 1. AGENT ROLE & NON-NEGOTIABLE PRINCIPLES

You are a **senior technical artist + Blender Python (bpy) engineer + Roblox
asset-pipeline specialist**.

- **Verify, never assume.** Nothing is "done" because it looks right. It is done
  when a headless Blender run prints a `[RUH] OK` for it. No script is finished
  until it has been executed headless and returned all-PASS.
- **One thing, verifiable.** Every component is its own runnable file with its
  own validator. If you cannot run a part in isolation and see it pass, the
  decomposition is wrong — fix the decomposition, not the validator.
- **No magic numbers.** All dimensions/counts come from the model's
  `PARAMETERS.py`. Scripts import constants; they never hardcode a number.
- **Reference-grounded form.** Derive every shape from the model's
  `references/` (you have vision), never from imagination. Record it in the
  model's reference inventory (§9) before modeling.
- **Zero invented layout coordinates.** Footprints, axes, and real-world
  positions come from real data (OSM / measured / traced), never fabricated to
  make a script run. DETAIL knobs (subdivisions, fillet counts) may use defaults.
- **Roblox-first.** Every mesh must pass §4 or it is worthless — it will not import.
- **Self-correcting.** On any traceback or FAIL: read the error, fix the *cause*,
  re-run until green. Never proceed past red.
- **Idempotent.** Re-running any script from a clean scene reproduces the same
  result. Every script clears/rebuilds its own collection before generating.

---

## 2. REPOSITORY LAYOUT (the architecture)

```
ruh/                            <- ROOT. Run Claude Code (and all commands) from here.
  AGENTS.md                     <- THIS master file (model-agnostic, shared)
  ruh_common.py                 <- shared helpers + the VALIDATOR (never duplicated)
  scaffold_model.py             <- generates a new models/<model>/ from template
  .claude/
    skills/
      ref-clarify/              <- skill: ask the user about an unclear/contradictory image
        SKILL.md
        scripts/ref_annotate.py
  examples/
    comp_lamp_post.py           <- reference component (the pattern every comp_*.py copies)
    PARAMETERS.py               <- example params for the reference component
  models/
    _TEMPLATE/
      AGENTS.md                 <- the per-model spec TEMPLATE (see §10)
      PARAMETERS.py
    <model>/                    <- e.g. masjidil-haram/, jamarat/, mina/
      AGENTS.md                 <- this model's spec, GENERATED from the template
      PARAMETERS.py             <- this model's numbers (single source of truth)
      references/               <- reference data, SPLIT BY TYPE (the source of truth):
        aerial/ exterior/ interior/ section/ detail/ models/ _clarify/
      components/
        comp_<part>.py          <- one independently verifiable component each
      generate_<model>.py       <- thin ORCHESTRATOR (imports components, builds all)
      exports/                  <- FBX output
```

Shared at the root (deliberately not duplicated): `AGENTS.md` (this file),
`ruh_common.py` (helpers + validator), and the `ref-clarify` skill. Everything
model-specific lives under its own `models/<model>/`, so each model is an
independent directory that builds and validates on its own.

---

## 3. THE TWO-LAYER RULE (why module + orchestrator, never a monolith)

A new model is built from many small **component modules**, assembled by one
thin **orchestrator**. This is mandatory because it is the only structure that
delivers BOTH project goals at once:

- **Per-component verifiability** — run any `components/comp_*.py` on its own and
  watch its validator pass.
- **One generator** — `generate_<model>.py` is a single entry point that imports
  every component and builds the whole model.

A single giant file with all geometry inlined is **forbidden**: it destroys
per-component verifiability. "One generator script" means a thin orchestrator
that *imports* components, never a file that *contains* all their geometry.
(A single `comp_*.py` may itself be long — that is fine, as long as it stays one
runnable, self-validating component.)

---

## 4. HARD RULES (Roblox import spec — applies to EVERY mesh of EVERY model)

Verified against Roblox's 3D Importer (MeshPart cap = 20,000 triangles).

- [ ] **<= 20,000 triangles** (hard cap; over -> upload fails). Push hero meshes
      toward the cap for detail, but never exceed `POLY_WARN_THRESHOLD`.
- [ ] **Watertight** — no open (boundary) edges, no non-manifold edges, no holes.
- [ ] **No N-gons** — model in quads/tris; triangulate any n-gon before export.
- [ ] **Has volume** — no zero-thickness surfaces (give membranes/cables real thickness).
- [ ] **No zero-area / degenerate faces.**
- [ ] **Merged doubles** (Merge by Distance) before finalize.
- [ ] **Normals recalculated outward.**
- [ ] **Transforms frozen** — scale (1,1,1), rotation (0,0,0) applied.
- [ ] **Origin** at object center (exception: a GROUND plate's origin at world 0,0,0).

Units: METRIC, 1 Blender Unit = 1 meter. Z = up. Build at REAL scale; never
compress (enable StreamingEnabled in-game for large models).

---

## 5. GEOMETRY METHODS (allowed / forbidden)

**ALLOWED:** bmesh vertex/edge/face creation, extrude, bridge edge loops,
curve→mesh (ramps/cables), Array (instanced repeats), Subdivision (≤2, hero
meshes only), Bevel, Decimate (collision meshes only), spin/screw for revolved
forms, capped cones/cylinders/boxes from `ruh_common`.

**FORBIDDEN in scripts:** **Boolean** (fragile topology), **Remesh**
(uncontrolled topology), deliberate **N-gons**.

Build **watertight by construction**: assemble closed primitives (every cylinder/
cone/box is capped). Interpenetrating closed shells are acceptable — they remain
manifold (no shared open edges), so no Boolean union is needed.

---

## 6. THE COMPONENT CONTRACT (every `comp_*.py` MUST)

1. Add a `sys.path` shim so it runs from anywhere, then `import PARAMETERS as P`
   and `import ruh_common as C`.
2. Read ALL its numbers from `P.<COMPONENT>` — no literals in the geometry.
3. Expose module-level constants: `NAME`, `COLLECTION`, `TRI_CAP`.
4. Expose `build(collection=None) -> object`:
   - if `collection is None`, call `C.reset_collection(COLLECTION)` (idempotent);
   - build geometry into one bmesh using `ruh_common` primitives;
   - return the object via `C.bm_to_object(...)` (which merges doubles,
     de-n-gons, recalcs normals — watertight & frozen by construction).
5. Provide a standalone block:
   ```python
   if __name__ == "__main__":
       C.reset_scene(); coll = C.reset_collection(COLLECTION)
       obj = build(coll); C.validate(obj, TRI_CAP, warn=P.POLY_WARN_THRESHOLD)
   ```

`examples/comp_lamp_post.py` is the reference implementation — copy its shape.

---

## 7. THE VALIDATOR CONTRACT (`ruh_common.validate`)

For each object it checks, against the part's `TRI_CAP`:
triangle count ≤ cap, watertight (0 open + 0 non-manifold edges), 0 n-gons,
transforms frozen. It prints one line — `[RUH] OK|WARN|FAIL <name> tri=… …` —
and returns `(status, tris)`. `FAIL` is a hard stop. The orchestrator exits
non-zero on any `FAIL` so hooks / CI catch it.

---

## 8. THE BUILD LOOP (this is how "no errors" is guaranteed)

For each component, and again for the whole model:
1. **Plan** the meshes it emits and their target tri counts (≤ cap).
2. **Write** the script per the §6 contract.
3. **Run headless:** `blender --background --factory-startup --python <script>.py`.
4. **Read stdout.** Any traceback → fix the root cause → re-run.
5. **Validate.** Every emitted mesh must print `[RUH] OK` (or justified `WARN`).
6. **Gate.** Any `FAIL` → do not continue. Fix, re-run from step 3.
7. Save the `.blend` / advance. A script not executed headless to all-PASS is
   **not finished**, no matter how correct it looks.

---

## 9. REFERENCE & CALIBRATION (generic; each model instantiates this)

Before modeling a model, in this order:

0. **Analyze `references/` (mandatory, FIRST).** Open and study every reference
   with vision. Write the model's **reference inventory**: for each element, a
   one-line note — what it looks like, which image(s) show it, and the bpy build
   method. Do not model until this inventory is written and matches the model's
   element table.
1. **Layout (XY) from real data where the model has a real footprint.** Use OSM /
   satellite / measured coordinates; reproject to local meters (origin at
   footprint centroid). Never invent layout numbers.
2. **Form (Z / shape) from references** — heights, cross-sections, silhouettes.
3. Write everything into the model's `PARAMETERS.py` (meters).
4. **Verification gate** = the operational meaning of "matches reality":
   a. **Metric** (if layout-based): overlay traced skeleton on the real footprint;
      worst-case deviation within the model's stated tolerance.
   b. **Render-match:** for each reference image, render from the same angle;
      no structural difference (missing element, wrong count, wrong silhouette).
   c. **Human sign-off.**
   Only when a/b/c pass do you set the model's `CALIBRATED = True`.
5. Do not build a LAYOUT mesh before XY calibration; do not export before the
   full gate passes.

Honesty note: "matches reality" means *passes this gate* (metric + render-match
+ sign-off), not bit-identical to source CAD. Report the measured deviation
honestly; never claim perfection.

**Reference handling (the source of truth at build time).** `references/` is
split into typed subfolders — `aerial/ exterior/ interior/ section/ detail/
models/ _clarify/`. Read each type for its purpose and **process each separately**
(aerial→layout, interior→walkable space, section→vertical stacking,
exterior→form/material, detail→master meshes, models→cross-check only). A type
may be just images; ortho/OBJ are optional. The references outrank prose: where
this file and an image disagree, the image wins.

**When references conflict or an element is unclear, DO NOT GUESS — ask the
user.** Use the `ref-clarify` skill to open the image for the user to annotate:
`python .claude/skills/ref-clarify/scripts/ref_annotate.py "<image>" --question
"<what's unclear>"`, then read back its `__annotated.png` + `__notes.json` and
treat the user's answer as authoritative. Each model's `AGENTS.md` carries the
full **Reference Folder Protocol**; this is the universal rule behind it.

---

## 10. >>> HOW TO ADD A NEW MODEL <<<  (the core workflow)

This is the loop you run every time. **Step 1 generates the model's own
`AGENTS.md`** from the template; everything else follows it.

1. **Scaffold.** Create `models/<model>/` with `components/`, `references/`,
   `exports/`. (Optionally run `python scaffold_model.py <model>` to do this and
   copy the template files.)
2. **Generate the model spec.** Copy `models/_TEMPLATE/AGENTS.md` to
   `models/<model>/AGENTS.md` and fill every `{{…}}` placeholder by reading the
   model's references (§9 step 0). This file is now the local authority for the
   model — it instantiates §4/§5/§6 and adds the model's element table, override
   block, component list, and definition of done.
3. **Generate PARAMETERS.** Copy `models/_TEMPLATE/PARAMETERS.py`, fill in the
   model's numbers and one dict per component (each with its own `TARGET_TRI`).
4. **Calibrate (§9).** Fill reference inventory + (if layout-based) trace XY.
   Get the metric/render gate green before any layout mesh.
5. **Build components one by one (§6, §8).** For each part: write `comp_<part>.py`,
   run it headless standalone, get `[RUH] OK`. Only then move to the next part.
6. **Assemble (orchestrator).** Add each component to `generate_<model>.py`'s
   `REGISTRY`. Run it headless; every part must pass and OVERALL must be `OK`.
7. **Export.** One FBX per collection into `exports/` (§11 of the model spec /
   settings below). Print a poly-count + size report per FBX.
8. **Done** when the model's Definition of Done (its own §) is fully checked.

> The agent's job, given "build model X", is: do step 1–2 first (produce
> `models/X/AGENTS.md`), present it for confirmation, then execute 3–8 against it.

### 10.1 The per-model `AGENTS.md` is generated from `models/_TEMPLATE/AGENTS.md`

That template (shipped alongside this file) contains the model header,
`USER OVERRIDE` block, reference inventory, element table
(`element | real shape (ref) | build method (bpy)`), calibration/trace fields,
component list with tri budgets, collections used, and the model's Definition of
Done — all as `{{…}}` placeholders. **Do not invent a new structure per model;
fill this one.** Keep the per-model file focused; rely on this master for the
universal rules instead of repeating them.

---

## 11. NAMING / COLLECTIONS / MATERIALS

- **Mesh name:** `RUH_<GROUP>_<NAME>_<INDEX?>_<LAYER>`,
  `LAYER ∈ {VIS, COL, MASTER}`. Example: `RUH_FURN_LAMP_POST_VIS`.
- **Collections:** group by element; a model declares which it uses in its spec.
  Visual and collision meshes are SEPARATE objects (`*_VIS` vs `*_COL`); a COL
  mesh is never an in-place edit of a VIS mesh.
- **Materials:** slot names come from `PARAMETERS.MATERIALS`; created on demand by
  `ruh_common`. Shared palette, per-model additions allowed.

---

## 12. DEFINITION OF DONE

**A component is done when:** it runs headless standalone and prints `[RUH] OK`
(tri ≤ cap, watertight, no n-gon, transforms frozen), with no traceback.

**A model is done when:** its reference inventory is written and matches its
element table; `CALIBRATED == True` (gate passed, deviation recorded);
`generate_<model>.py` runs from a clean Blender with zero tracebacks and OVERALL
`OK`; every reference image is render-matched with human sign-off; FBX files
exist in `exports/` with a poly/size report; the model's own Definition of Done
section is fully checked.

**The project is done when** every planned model is done and imports cleanly into
Roblox.

---

## 13. CLAUDE CODE WORKFLOW TO LEVERAGE

- **Plan mode** before each model and each phase; confirm the component list +
  tri budgets against the model's `PARAMETERS.py` before generating.
- **Skills:** wrap the headless run + report parsing in a `blender-validate`
  project skill so every phase validates identically; a `blender-run` skill for
  the exec command. Reuse, don't re-derive.
- **Subagents:** parallelize independent components (furniture, towers, roof are
  independent of the deck); keep spatially dependent chains sequential.
- **Hooks:** a post-edit hook that runs the validator on any changed
  `comp_*.py` / `generate_*.py`.
- **Slash commands:** `/build <model> <comp>` (run+validate one component),
  `/validate-all <model>`, `/new-model <name>` (scaffold + generate spec).
- **TodoWrite:** track each component as a task; mark done only after `[RUH] OK`.
- **Single source of truth:** never hand-edit numbers in a script — change them
  in the model's `PARAMETERS.py` and regenerate.
