# AGENTS.md — RUH Model Spec: Masjid Al-Khaif (Mina)
# Generated from models/_TEMPLATE/AGENTS.md. Governs ONLY this model.
# Read together with the master /AGENTS.md (universal rules). On any conflict:
#   user chat  >  references/ (the images)  >  THIS file  >  master /AGENTS.md.
# Version: 1.0   Date: 2026-06-13

> **This spec is a GUIDE, not a cage.** It points Claude Code at the reference
> material and lists what to build; it deliberately does NOT freeze exact shapes.
> The real shapes come from `references/` (see §R). Stay faithful to the
> references; when they're unclear, ask the user (§R) — do not guess.

> One-line description: {{ONE_LINE_DESCRIPTION}}
> Real-world location / coords (if any): {{REAL_COORDS_OR_NA}}
> Layout-based (has a real footprint to trace)?  {{YES_OR_NO}}
> **TARGET STATE:** {{which era / configuration this model represents, e.g.
>   "current ~2020s state"}} — build this state. If references mix eras, that is
>   a contradiction → §R.

# >>> USER OVERRIDE 2026-06-13 (ABSOLUTE — supersedes any conflicting text below):
# {{OVERRIDE_TEXT_OR_"none yet"}}
# (Hard corrections + resolved contradictions go here, each referencing the
#  ref-clarify __notes.json that settled it. Leave a clear 'none yet' if empty.)

---

## R. REFERENCE FOLDER PROTOCOL  (Claude Code: do this BEFORE & DURING building)

`references/` is the **source of truth** for this model's form — above anything
written in this file. This file tells you *what* to build and *where to look*;
the *exact shape* you read from the references.

**1. References are split by type. Read each for its purpose, SEPARATELY** — do
not blindly blend types together:

| Subfolder              | Use it for                                            |
|------------------------|-------------------------------------------------------|
| `references/aerial/`   | footprint, overall layout, element positions (XY)     |
| `references/exterior/` | outer form, facades, silhouette, materials, colour    |
| `references/interior/` | walkable space: rooms, corridors, column grid, levels |
| `references/section/`  | how floors / levels stack vertically (Z)              |
| `references/detail/`   | close-ups for master meshes (column, gate, lamp, …)   |
| `references/models/`   | rough 3D / OBJ if provided — CROSS-CHECK only (fan-made hint, not ground truth) |
| `references/_clarify/` | annotated images + notes produced by `ref-clarify`    |

A type may be just images. Ortho screenshots and OBJ are **optional**, not required.

**2. Authority when types describe the same thing:** real layout data
(OSM/satellite/measured) > `aerial/` > `section/` > `exterior/`+`interior/` photos
> `models/` (rough model = hint only).

**3. CONTRADICTION or AMBIGUITY → ASK THE USER. Do not guess, do not silently
pick one.** If two references disagree (shape, count, level number, era), or you
cannot identify an element, run the `ref-clarify` skill:

```bash
python .claude/skills/ref-clarify/scripts/ref_annotate.py \
    "references/<type>/<image>" \
    --question "<exactly what is unclear>" \
    --out-dir references/_clarify
```

It opens the image for the user to annotate (numbered pins + comments, boxes,
arrows) and writes `*__annotated.png` + `*__notes.json`. Read both back, treat
the user's answer as authoritative, and **record the resolution** in the
USER OVERRIDE block or §C (cite the `__notes.json`).

**4. Missing reference for an element?** You may web-search for a supplementary
reference, but `references/` stays primary — and you must flag the gap and your
assumption to the user before relying on web material.

**5. Don't over-strictify.** Where the references are clear, follow them. Where
they're silent on a minor DETAIL (e.g. exact fillet count), a sensible default is
fine. Where they're silent or unclear on FORM/LAYOUT, use ref-clarify rather than
inventing.

---

## A. REFERENCE INVENTORY  (fill after reading references/ — see master §9 step 0)

One line per element, written from the actual files (not memory). This is a
starting map; the references themselves remain authoritative.

| Element            | Looks like (which ref type/file)                | bpy build method (ruh_common)   |
|--------------------|-------------------------------------------------|---------------------------------|
| {{ELEMENT_1}}      | {{LOOKS_LIKE_1}} (`{{REF_1}}`)                  | {{BUILD_METHOD_1}}              |
| {{ELEMENT_2}}      | {{LOOKS_LIKE_2}} (`{{REF_2}}`)                  | {{BUILD_METHOD_2}}              |
| …                  | …                                               | …                               |

---

## B. ELEMENT GUIDE  (pointers — derive exact form from references/, §R)

Shapes are intentionally NOT pinned. For each element: which reference type(s) to
read, and the build method. Unclear → ref-clarify.

| Element            | Read shape from (references/ type)  | Build method (bpy / ruh_common)          |
|--------------------|-------------------------------------|------------------------------------------|
| {{ELEMENT_1}}      | {{TYPES_1, e.g. exterior+detail}}   | {{METHOD_1}}                             |
| {{ELEMENT_2}}      | {{TYPES_2}}                         | {{METHOD_2}}                             |
| …                  | …                                   | …                                        |

Overall massing: {{describe loosely from aerial+exterior; confirm via ref-clarify if unsure}}

---

## C. CALIBRATION & TRACE  (only if layout-based; else "N/A — detail-only model")

- XY source: {{OSM_WAY / SATELLITE / MEASURED / N/A}}
- Z / form source: {{section + exterior references}}
- Fidelity target (as strict as the references allow): deviation ≤ {{XY_TOL_M}} m
  AND ≤ {{XY_TOL_PCT}} %. If references can't support that precision, record the
  best achievable and note it — don't fake a number.
- TRACE fields to fill in PARAMETERS.py: {{OUTLINE / AXES / POSITIONS / …}}
- `CALIBRATED = True` only after metric overlay + render-match + human sign-off
  (master §9). Unsure at any step → ref-clarify.
- Recorded max deviation: `VERIFY_MAX_DEVIATION_M = {{___}}`
- Resolved contradictions (cite `_clarify/*__notes.json`): {{___ / none}}

---

## D. COMPONENT LIST  (each is one verifiable components/comp_*.py — master §6)

| Component file            | Emits                         | TRI_CAP | Collection   | Done when (besides [RUH] OK) |
|---------------------------|-------------------------------|---------|--------------|------------------------------|
| comp_{{PART_1}}.py        | {{EMITS_1}}                   | {{N}}   | {{COLL_1}}   | {{EXTRA_CHECK_1}}            |
| comp_{{PART_2}}.py        | {{EMITS_2}}                   | {{N}}   | {{COLL_2}}   | {{EXTRA_CHECK_2}}            |
| …                         | …                             | …       | …            | …                            |

Build order (respect spatial dependency): {{e.g. layout/floors → structure → details → furniture}}
Orchestrator: `generate_masjid-al-khaif.py` — its REGISTRY lists every component above.

---

## E. COLLECTIONS USED

VISUAL: {{LIST_VIS_COLLECTIONS}}
COLLISION: {{LIST_COL_COLLECTIONS}}   (separate `*_COL` objects; never edit VIS in place)

---

## F. EXPORT

One FBX per collection into `models/masjid-al-khaif/exports/`.
FBX settings: scale 1.0, -Z forward, Y up, apply unit ON, triangulate ON, apply
modifiers ON, all transforms applied first. Print poly-count + est-size per FBX.
Roblox CollisionFidelity per part: {{BOX_FOR_… / HULL_FOR_…}}; non-walkable VIS
parts get `CanCollide=false`.

---

## G. DEFINITION OF DONE (this model)

- [ ] §R followed: references read by type; contradictions resolved via ref-clarify and recorded.
- [ ] Reference inventory (§A) written and consistent with the references.
- [ ] {{CALIBRATED == True with deviation recorded  /  "N/A — detail-only"}}.
- [ ] Every component in §D runs headless standalone → `[RUH] OK`.
- [ ] `generate_masjid-al-khaif.py` runs from a clean Blender, zero tracebacks, OVERALL `OK`.
- [ ] Each references/ image render-matched (no structural difference); human sign-off.
- [ ] FBX files exist in exports/ with poly/size report.
- [ ] Shapes match the references on a spot-check render: {{KEY_SILHOUETTES_TO_VERIFY}}.
