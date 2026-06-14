# AGENTS.md — RUH Model Spec: Masjid Al-Nimrah (Arafah)
# Generated from models/_TEMPLATE/AGENTS.md. Governs ONLY this model.
# Read together with the master /AGENTS.md (universal rules). On any conflict:
#   user chat  >  references/ (the images)  >  THIS file  >  master /AGENTS.md.
# Version: 1.0   Date: 2026-06-13

> **This spec is a GUIDE, not a cage.** It points Claude Code at the reference
> material and lists what to build; it deliberately does NOT freeze exact shapes.
> The real shapes come from `references/` (see §R). Stay faithful to the
> references; when they're unclear, ask the user (§R) — do not guess.

> One-line description: Masjid Al-Nimrah (Masjid Namirah) in Arafat — a very large
> rectangular walled mosque (site of the Arafah sermon + combined Dhuhr/Asr): long
> arcaded prayer halls with rows of green-topped roof bays, 6 tall pink/white minarets,
> a few white domes, a yellow-brick perimeter wall with arched niches, gateway pavilions,
> mushroom cooling-fan funnels, and big open paved courtyards.
> Real-world location / coords (if any): Arafat, Mecca — ~21.3549 N, 39.9534 E
> (CONFIRM via OSM before tracing).
> Layout-based (has a real footprint to trace)?  YES — large rectangular footprint +
> minaret/dome/gate positions from OSM; real aerials present in references/aerial/.
> **TARGET STATE:** Current expanded mosque — build this state. If references mix eras,
> that is a contradiction → §R.

# >>> USER OVERRIDE 2026-06-13 (ABSOLUTE — supersedes any conflicting text below):
# none yet.
# NOTE: references/ has 3 REAL aerial photos (aerial/Masjid_Namirah_SPA…, masjid-namirah-1*,
# masjid-namirah-1024x454) + 1 REAL interior photo (interior/images.jpeg) = GROUND TRUTH.
# All other images (01-23, sig/signature*, wire*) are renders of a fan 3D model = CROSS-CHECK
# HINT only. OSM footprint not fetched yet. Resolve any fan-vs-real conflict via ref-clarify.
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

Authority: `aerial/` REAL photos (Masjid_Namirah_SPA…, masjid-namirah-1*, …1024x454) +
`interior/images.jpeg` are GROUND TRUTH. Fan-model renders (`exterior/01-23, sig/signature*`,
`aerial/02,03,11,14,21-23`, `models/wire*`) are CROSS-CHECK HINT only. Where they disagree,
the real photos win.

| Element | Looks like (which ref type/file) | bpy build method (ruh_common) |
|---------|----------------------------------|-------------------------------|
| Overall footprint | Big **rectangular** walled compound, long axis ~E–W, prayer-hall block on one half + open courtyards on the other; rows of green-topped roof bays (`aerial/Masjid_Namirah_SPA….webp`, `aerial/masjid-namirah-1024x454.jpg`, `aerial/21.jpg`) | one large slab/box footprint + inner court voids; trace from OSM |
| Prayer-hall roof bays | Many parallel long **gabled/flat bays** with small green roof strips + skylight rows over the covered hall (`aerial/21.jpg`, `exterior/10.jpg`, `aerial/Masjid_Namirah_SPA….webp`) | arrayed long capped boxes (bays) on the hall slab |
| Minarets ×6 | Tall slender **pink-and-white banded** minarets, ringed balconies, onion-bulb cap + finial; placed around the perimeter/gates (`exterior/15.jpg`, `detail/17.jpg`, `aerial/masjid-namirah-1.jpg`) | stacked capped cylinders (taper) + balcony rings + spin-revolved bulb cap |
| Domes | A few **white ribbed/smooth domes** over key bays near the wall (`exterior/20.jpg`, `exterior/04.jpg`, `models/wire01.jpg`) | spin/screw half-sphere on a drum |
| Perimeter wall | **Yellow-brick** boundary wall, ranks of small **pointed-arch niches/windows**, crenellated parapet (`exterior/19.jpg`, `exterior/05.jpg`, `aerial/masjid-namirah-1.jpg`) | extruded wall box + arrayed arched-niche module + parapet |
| Arcades / facade bays | Long rows of **pointed-arch** columned arcades along the hall faces; tall arched window panels w/ lattice (`exterior/18.jpg`, `exterior/09.jpg`, `exterior/16.jpg`) | one arch-bay master + Array; lattice as texture/inset |
| Gateway pavilions | Projecting **white portal blocks** in the wall: framed arch group + cornice, columned porch (`exterior/19.jpg`, `exterior/09.jpg`) | box mass + arched portal module |
| Cooling-fan funnels | Tall **mushroom/inverted-cone** funnel units on columns in the courtyards (`exterior/06.jpg`, `exterior/08.jpg`, `detail/17.jpg`) | cylinder pole + capped inverted cone head; instanced |
| Courtyard + outbuildings | Wide paved open courts; separate low service blocks + a long colonnaded annex outside the wall (`aerial/22.jpg`, `aerial/23.jpg`, `exterior/08.jpg`) | flat slab (vertex color) + simple boxes |
| Interior (walkable) | Hypostyle hall: white arched bays + columns, red carpet, signage pillars (`interior/images.jpeg`) | column grid + arched ceiling bays (for walkable interior if modeled) |

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

- XY source: **OSM (to fetch)** — Masjid Namirah, Arafat, ~21.3549 N, 39.9534 E.
  Real aerials in `aerial/` give footprint + roof-bay grid for cross-check, but the
  metric trace must come from OSM (reproject to local meters, origin at footprint centroid).
- Z / form source: `exterior/` renders for facade/minaret/dome silhouette; real aerials
  for roof layout; `interior/images.jpeg` for the hall section.
- Fidelity target: footprint deviation ≤ 5 m AND ≤ 1% vs OSM.
- TRACE fields to fill in PARAMETERS.py: OUTLINE_OUTER, COURT vs HALL split, MINARET_POSITIONS
  (×6), DOME_POSITIONS, GATE_POSITIONS, FAN_FUNNEL_POSITIONS.
- `CALIBRATED = True` only after OSM overlay + render-match + human sign-off (master §9).
- **OPEN ITEMS (resolve via ref-clarify):** OSM footprint not yet fetched; confirm minaret
  count (renders show 6) + exact roof-bay count against the real aerials; fan model is a
  HINT, the real aerials are authoritative on layout/proportion.
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
Orchestrator: `generate_masjid-al-nimrah.py` — its REGISTRY lists every component above.

---

## E. COLLECTIONS USED

VISUAL: {{LIST_VIS_COLLECTIONS}}
COLLISION: {{LIST_COL_COLLECTIONS}}   (separate `*_COL` objects; never edit VIS in place)

---

## F. EXPORT

One FBX per collection into `models/masjid-al-nimrah/exports/`.
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
- [ ] `generate_masjid-al-nimrah.py` runs from a clean Blender, zero tracebacks, OVERALL `OK`.
- [ ] Each references/ image render-matched (no structural difference); human sign-off.
- [ ] FBX files exist in exports/ with poly/size report.
- [ ] Shapes match the references on a spot-check render: {{KEY_SILHOUETTES_TO_VERIFY}}.
