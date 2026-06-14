# AGENTS.md — RUH Model Spec: Makkah Royal Clock Tower (Abraj Al-Bait)
# Generated from models/_TEMPLATE/AGENTS.md. Governs ONLY this model.
# Read together with the master /AGENTS.md (universal rules). On any conflict:
#   user chat  >  references/ (the images)  >  THIS file  >  master /AGENTS.md.
# Version: 1.0   Date: 2026-06-13

> **This spec is a GUIDE, not a cage.** It points Claude Code at the reference
> material and lists what to build; it deliberately does NOT freeze exact shapes.
> The real shapes come from `references/` (see §R). Stay faithful to the
> references; when they're unclear, ask the user (§R) — do not guess.

> One-line description: Makkah Royal Clock Tower (Abraj Al-Bait) — the giant clock-tower
> hotel overlooking Masjidil Haram: a central skyscraper carrying four huge clock faces +
> crowned dome/spire/crescent, flanked by a cluster of shorter towers on a large
> multi-storey arcaded podium/mall.
> Real-world location / coords (if any): Abraj Al-Bait, Mecca — ~21.4187 N, 39.8256 E
> (just S of the Kaaba; CONFIRM via OSM before tracing).
> Layout-based (has a real footprint to trace)?  YES — podium footprint + tower-base
> positions from OSM. Height is the hero dimension (clock tower ~601 m); read tower
> height + clock-face size from references.
> **TARGET STATE:** Completed current state (clock tower + 7 hotel towers + podium) —
> build this state. If references mix eras, that is a contradiction → §R.

# >>> USER OVERRIDE 2026-06-13 (ABSOLUTE — supersedes any conflicting text below):
# none yet.
# NOTE: references/ here are ALL renders of a Hum3D fan model (watermarked) — CROSS-CHECK
# HINT ONLY, not ground truth. No real photo or OSM trace is in the folder yet; fetch OSM
# + confirm real clock-face/height dims (and resolve any fan-model inaccuracies) via
# ref-clarify before committing layout/scale.
# (Hard corrections + resolved contradictions go here, each referencing the
#  ref-clarify __notes.json that settled it.)

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

Authority: NO real photo / OSM in folder yet — every image is a Hum3D fan-model render
(CROSS-CHECK HINT only). `exterior/` = textured form views, `models/` = wireframe/topology
views of the same model, `aerial/` = textured top/3-4 views (layout hint), `detail/` =
clock-crown + gate close-ups. Confirm real dims (height, clock-face Ø) + OSM footprint
before trusting scale.

| Element | Looks like (which ref type/file) | bpy build method (ruh_common) |
|---------|----------------------------------|-------------------------------|
| Clock tower (hero) | Tall slender tower w/ stepped setbacks, four huge round **clock faces** near top, then arched belfry, blue **dome**, gold **spire + crescent** finial (`exterior/…1920_0001.jpg`, `exterior/…1920_0002.jpg`, `detail/b0d4e63f….jpg`) | stacked capped boxes (shaft + setbacks) + cylinder/cone crown + dome (spin) + crescent |
| Clock faces ×4 | Large white dials, one per cardinal face of the belfry block, gold/maroon surround + Arabic script band above (`detail/b0d4e63f….jpg`, `exterior/…1920_0002.jpg`) | inset disc on each face; texture/decal for dial |
| Crown dome + spire | Onion-ish blue dome + tapering gold spire topped by crescent (`detail/b0d4e63f….jpg`, `exterior/37dcbaba….jpg`) | spin/screw revolve + capped cone + crescent mesh |
| Hotel towers (cluster) | ~6–7 shorter towers around the central tower, flat tops w/ small **helipad/tented caps**, beige stone + blue glass bands, arched window grids (`aerial/…0020.jpg`, `exterior/…0012.jpg`, `models/…0019.jpg`) | capped boxes per tower w/ setbacks; instanced window grid; count → TRACE |
| Podium / mall base | Large multi-storey **arcaded** base block under the towers: rows of pointed arches at ground, ranks of arched windows above, big central **arched portal/gate** (`exterior/…0006.jpg`, `exterior/…0008.jpg`, `detail/ac6614fd….jpg`) | extruded box mass + arched arcade module (instanced) |
| Facade modules | Repeating arched-window bays + vertical mullion strips + cornice caps on every tower (`models/…0007.jpg`, `models/…0013.jpg`) | one master bay panel, Array across faces |
| Overall composition | Central tower rises from the middle-rear of the podium; towers fan outward; whole complex sits on one wide podium footprint (`aerial/…0018.jpg`, `aerial/…0020.jpg`, `aerial/94ff7880….jpg`) | place per OSM/traced footprint; respect §4 20k-tri cap per MeshPart |

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

- XY source: **OSM (to fetch)** — Abraj Al-Bait footprint, ~21.4187 N, 39.8256 E.
  Not yet in references/ (the folder holds only fan-model renders). Fetch + reproject
  to local meters (origin at podium centroid) before any layout mesh.
- Z / form source: `exterior/` renders for silhouette/setbacks; real published height
  (clock tower ≈ 601 m, clock face Ø ≈ 43 m) to be CONFIRMED via ref-clarify — the
  fan model's proportions are a hint, not ground truth.
- Fidelity target: footprint deviation ≤ 5 m AND ≤ 1% vs OSM. Height/clock-face Ø within
  references' best achievable; record what's used.
- TRACE fields to fill in PARAMETERS.py: PODIUM_OUTLINE, TOWER_POSITIONS (clock tower +
  ~6–7 hotel towers), TOWER_HEIGHTS, CLOCK_FACE_DIAMETER.
- `CALIBRATED = True` only after OSM overlay + render-match + human sign-off (master §9).
- **OPEN ITEMS (resolve via ref-clarify before/at build):**
  1. Real height + clock-face diameter (don't trust fan-model scale).
  2. Exact hotel-tower count (refs show a central tower + ~6–7 around) → set in TRACE.
  3. OSM footprint not yet fetched.
- Recorded max deviation: `VERIFY_MAX_DEVIATION_M = None`
- Resolved contradictions (cite `_clarify/*__notes.json`): none yet.

---

## D. COMPONENT LIST  (each is one verifiable components/comp_*.py — master §6)

| Component file            | Emits                         | TRI_CAP | Collection   | Done when (besides [RUH] OK) |
|---------------------------|-------------------------------|---------|--------------|------------------------------|
| comp_{{PART_1}}.py        | {{EMITS_1}}                   | {{N}}   | {{COLL_1}}   | {{EXTRA_CHECK_1}}            |
| comp_{{PART_2}}.py        | {{EMITS_2}}                   | {{N}}   | {{COLL_2}}   | {{EXTRA_CHECK_2}}            |
| …                         | …                             | …       | …            | …                            |

Build order (respect spatial dependency): {{e.g. layout/floors → structure → details → furniture}}
Orchestrator: `generate_mekkah-tower.py` — its REGISTRY lists every component above.

---

## E. COLLECTIONS USED

VISUAL: {{LIST_VIS_COLLECTIONS}}
COLLISION: {{LIST_COL_COLLECTIONS}}   (separate `*_COL` objects; never edit VIS in place)

---

## F. EXPORT

One FBX per collection into `models/mekkah-tower/exports/`.
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
- [ ] `generate_mekkah-tower.py` runs from a clean Blender, zero tracebacks, OVERALL `OK`.
- [ ] Each references/ image render-matched (no structural difference); human sign-off.
- [ ] FBX files exist in exports/ with poly/size report.
- [ ] Shapes match the references on a spot-check render: {{KEY_SILHOUETTES_TO_VERIFY}}.
