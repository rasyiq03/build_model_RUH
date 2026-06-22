# AGENTS.md — RUH Model Spec: Jamarat Bridge Complex
# Generated from models/_TEMPLATE/AGENTS.md. Governs ONLY this model.
# Read together with the master /AGENTS.md (universal rules). On any conflict:
#   user chat  >  references/ (the images)  >  THIS file  >  master /AGENTS.md.
# Version: 1.0   Date: 2026-06-13

> **This spec is a GUIDE, not a cage.** It points Claude Code at the reference
> material and lists what to build; it deliberately does NOT freeze exact shapes.
> The real shapes come from `references/` (see §R). Stay faithful to the
> references; when they're unclear, ask the user (§R) — do not guess.

> One-line description: The multi-level Jamaraat Bridge in Mina — the stoning ritual complex with 3 elliptical Jamrah walls (Ula/Sughra, Wusta, Aqabah/Kubra) set in oval basins, surrounded by a 5-level open deck loop, tensile-tent roofs, circulation/escalator towers, and fan ramps.
> Real-world location / coords (if any): Jamaraat Bridge, Mina — 21.42139 N, 39.87278 E (OSM way 440922995).
> Layout-based (has a real footprint to trace)?  YES — published footprint ≈ 950 m (Y) × 80 m (X), 5 floors @ 12 m (Z 0/12/24/36/48). OSM way 440922995 available in references/aerial/osm/.
> **TARGET STATE:** Current expanded multi-level bridge (~2010s–2020s configuration, 5 decks) — build this state. If references mix eras, that is a contradiction → §R.

# >>> USER OVERRIDE 2026-06-13 (ABSOLUTE — supersedes any conflicting text below):
# MUST match the REAL, CURRENT (latest) Jamaraat Bridge — faithful to real conditions:
#   - REAL access roads / FLYOVERS (jalan layang) feeding the multi-level decks — model them, not omit.
#   - Roof is NOT a single oval: it is the real set of TENSILE MEMBRANE tents (saddle/cone
#     canopies) — real tent geometry, not a solid oval/cone simplification.
#   - Real building MASSING/footprint (from OSM + real aerial), NOT the legacy "stadium-oval" assumption.
#   The legacy build's simplifications (oval deck loop, solid-cone tents, standalone helical ramps,
#   reference-guessed jamrah/tower/roof positions — see _legacy/BUILD_REPORT.md) are REJECTED as
#   the target; they are reference only. Derive real shape from OSM + real photos; where the real
#   form is unclear, get real references / ask via ref-clarify — do NOT fall back to the fan model.
#   COVERAGE: include the flyover network + surrounding Mina roads as far as OSM data goes, but keep it
#   sensible (not the whole city) — the structure + its real approach/ramp system + immediate Mina roads.
#   ROAD FUNCTION (critical): roads/ramps must be correct by FUNCTION, not just XY location. Real Jamaraat
#   approaches are assigned by LEVEL & direction — some ramps lead to the level-3 deck, others to the
#   level-5 deck (one-way pilgrim routing). Each modelled ramp MUST connect to the CORRECT deck level it
#   really serves, with the correct travel direction. This level/direction mapping is NOT in OSM's 2D ways —
#   establish it from real references + ref-clarify (user marks which ramp → which floor) before building.
# NOTE: A prior build of this model exists (calibrated, CALIBRATED=True at the time).
# Its calibration record + traced data is archived in references/_legacy/ (see §C).
# That archive is a STARTING POINT to avoid re-calibrating from scratch; the live
# references/ images remain authoritative on any conflict.
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

Authority: real OSM layout (`aerial/osm/`) + real photos (`aerial/Screenshot…181836.png`,
`interior/penampakan…webp`) are GROUND TRUTH. Everything else (perspective/wireframe
renders, `models/` Tripo + massing screenshots) is a fan/massing model — CROSS-CHECK
HINT only (§R authority order). Full prior analysis: `references/_legacy/PHASE_R_INVENTORY.md`.

> **AUTHORITATIVE real element map (user-annotated 2026-06-14):**
> `references/aerial/REAL_ELEMENT_MAP.md` (+ `_clarify/REAL_aerial_jamarat-bridge__annotated.png`).
> Where the rows below disagree with it, the element map + the user wins. Key real facts:
> 4 canopies (3 jamrah: Aqaba=W/biggest, Wusta=mid, Ula=E/smallest; + 1 transition-plaza
> canopy w/o basin); 5 decks @ 12 m; 3 tower TYPES (~11 escalator/helipad + 2 ventilation/
> observation + 3 service/lift ≈ 16); ramps by function (inbound fan→L1, helix exit, elevated
> exit bridge, top-deck parallel roads); one-way E(in)→W(out).

| Element | Looks like (which ref type/file) | bpy build method (ruh_common) |
|---------|----------------------------------|-------------------------------|
| Overall massing | Elongated multi-level bridge ≈ 950×80 m: central jamarat **spine** (3 walls) + multi-level **decks** + real **access roads / FLYOVERS** (jalan layang) ramping between deck levels and ground. **Derive the real outline from OSM (`aerial/osm/`) + the real aerial (`aerial/Screenshot…181836.png`) — do NOT assume a clean "oval"** (legacy oval = rejected, see USER OVERRIDE). | slabs from OSM-traced edge loops (no boolean); flyovers as real sloped road ribbons from OSM ways |
| Canopies ×4 (3 jamrah + 1 plaza) | **NOT a single oval** — **4 white tensile PTFE umbrella canopies** along the spine: **3 over jamrah** (Aqaba=W/**largest**, Wusta=mid, Ula=E/**smallest**) each w/ central mast + radial cables to an oval edge ring + **pebble basin** below; **+1 TRANSITION-PLAZA canopy** (between Aqaba & Wusta) w/ **NO basin**, open plaza floor (`aerial/REAL_aerial_jamarat-bridge.jpg`, `_clarify/REAL_aerial_jamarat-bridge__annotated.png`, `aerial/REAL_ELEMENT_MAP.md`). | tensile membrane shells (curve→mesh/subdiv saddle, real thickness) + edge ring + mast + cables; 3 w/ basin, 1 w/o; **count = 4 (3 jamrah + 1 plaza), user-confirmed** |
| Towers — 3 TYPES (~16) | **A) Escalator/Helipad** (~11): large **oval** towers, escalators+stairs inside, **flat helipad roof**, **vertical-louver** facade. **B) Ventilation/Observation** (2): tall cylinder exhaust chimney, **flared top** (CCTV/observation), small helipad disc. **C) Service/Lift** (3): **half-cylinder** (part-embedded), lift+stairs+utility shaft, **small square windows** in vertical rows, lift-machine-room roof (`aerial/REAL_ELEMENT_MAP.md`, `aerial/REAL_aerial_jamarat-bridge.jpg`, `exterior/REAL_decks_ramps_oneway.jpeg`) | 3 master meshes (oval-louver tower / flared chimney+disc / half-cyl windowed) instanced; counts per element map, confirm XY |
| Flyover ramps (by level) | **Curved one-way flyover ramps** sweeping in from several directions, spiralling down to ground; each serves a SPECIFIC deck level (L1–L5) per `aerial/REAL_LEVEL_ROAD_SYSTEM.md`; separate wide vehicle roads alongside (`aerial/REAL_aerial_jamarat-bridge.jpg`, `exterior/REAL_decks_ramps_oneway.jpeg`, `aerial/osm/`) | sloped road slabs from OSM ways, each connected to its correct deck level + direction |
| Jamrah walls ×3 | Tall **elliptical stone wall/blade**, long axis across spine, sloped top, in an oval pebble basin; rises through an oculus in each deck. Order along spine **W→E: Aqaba/Kubra (W, biggest) → Wusta (mid) → Ula/Sughra (E, smallest)** (corrects legacy S→N). Daily throw order Ula→Wusta→Aqaba; day-10 = Aqaba only (`interior/perspective06.jpg`, `interior/penampakan…webp`, `detail/signs02_uv.jpg`, `aerial/REAL_ELEMENT_MAP.md`) | ellipse cross-section lofted up with taper; granite |
| Basins | Oval catchment pit + low padded rim wall per jamrah; per-floor parapet ring around each deck oculus (`interior/perspective06.jpg`, `interior/penampakan…webp`) | oval annulus + low rim |
| Decks / floors ×5 | Open parking-garage decks: slab + square column grid + open sides + fascia/railing edge; annular oval (outer + spine void), 5 levels @ 12 m (`exterior/perspective03.jpg`, `exterior/perspective05.jpg`, `aerial/Screenshot…181836.png`) | annular oval slabs + arrayed columns |
| Columns | **PERIMETER PIERS ONLY — interior intentionally COLUMN-FREE** (DATA web 2026-06-15: clear spans 60-100 m so pilgrims see all 3 jamrah from anywhere; deck box girders @9 m supported at edges). Big square edge piers, NOT a dense interior grid (old 12 m grid of ~314 thin posts = REJECTED) (`exterior/perspective03.jpg`, `models/wireframe03/05.jpg`) | capped box piers sampled along the deck-polygon perimeter |
| ~~Towers (legacy guess)~~ | SUPERSEDED → see "Towers — 3 TYPES" row above + `aerial/REAL_ELEMENT_MAP.md`. (legacy fan-model said ~10–12 generic) | — |
| ~~Tensile roof (legacy)~~ | SUPERSEDED → see "Canopies ×4" row above. (legacy used solid cone frustums — rejected) | — |
| Ramps (by FUNCTION) | **#23 inbound fan ramp** from E (Muzdalifah/Mina) → climbs to **L1**; **#5 helix exit ramp** spirals down from upper deck → ground; **#6 elevated exit bridge** from upper deck → over Mina camps to tunnel/Makkah; **#24/#25 top-deck-level parallel roads** (`aerial/REAL_ELEMENT_MAP.md`, `aerial/REAL_LEVEL_ROAD_SYSTEM.md`, `aerial/osm/`) | sloped road slabs from OSM ways, each tied to its correct deck level + one-way direction |
| Ground paving | Radiating red/grey paving bands + yellow lane lines (`exterior/perspective08.jpg`, `models/top.jpg`) | subdivided plane, vertex color (no geo) |
| Furniture | Y-branch lamp poles, tall cooling-fan poles, green signage (`exterior/perspective05/07.jpg`, `detail/signs02_uv.jpg`) | masters + instanced (see examples/comp_lamp_post.py) |
| Background | Mina tent city, mountains, elevated metro line (`exterior/perspective01/02.jpg`, `aerial/Screenshot…181836.png`) | low-poly instances; terrain ring |

---

## B. ELEMENT GUIDE  (pointers — derive exact form from references/, §R)

Shapes are intentionally NOT pinned. For each element: which reference type(s) to
read, and the build method. Unclear → ref-clarify.

Element-by-element shape + build method are now captured authoritatively in **§A** and in
**`references/aerial/REAL_ELEMENT_MAP.md`** (user-annotated) — read those; this section is just
the type→source pointer:

| Element | Read shape from (references/ type) | Build method (bpy / ruh_common) |
|---------|------------------------------------|----------------------------------|
| Layout / decks / ramps | `aerial/osm/` + `aerial/REAL_LEVEL_ROAD_SYSTEM.md` + real aerials | OSM-traced slabs + sloped road slabs |
| Jamrah walls + canopies | `aerial/REAL_ELEMENT_MAP.md` + `interior/` + real aerials | lofted ellipse walls + tensile membrane canopies |
| Towers (3 types) | `aerial/REAL_ELEMENT_MAP.md` + real aerials | 3 master meshes, instanced |
| Furniture / ground / bg | `exterior/` + real aerials | instanced masters + vertex-color paving |

Overall massing: elongated multi-level bridge ≈950×80 m, central 3-jamrah spine under 4 PTFE
canopies, 5 open decks, 3 tower types, one-way ramps E(in)→W(out). Derive exact form from OSM +
real aerials (NOT the legacy oval / fan model).

---

## C. CALIBRATION & TRACE  (only if layout-based; else "N/A — detail-only model")

- XY source: **OSM way 440922995** (`references/aerial/osm/jamarat.osm`), reprojected
  to local meters (`references/aerial/osm/local_meters.json`). Published dims
  950 m (Y) × 80 m (X); 5 floors @ 12 m (Z 0/12/24/36/48) — known-real, no trace.
- Z / form source: `exterior/` + `interior/` photos & renders (heights from published 12 m floors).
- Fidelity target: deviation ≤ 5 m AND ≤ 1% on the traced footprint vs OSM.
- TRACE fields to fill in PARAMETERS.py: OUTLINE_OUTER, road/ramp AXES, 3 JAMRAH POSITIONS,
  tower POSITIONS, tent POSITIONS, **ROAD_LEVEL_MAP** (each ramp/approach → its real deck
  level + one-way direction — see `references/aerial/REAL_LEVEL_ROAD_SYSTEM.md`; bind to the
  labeled OSM ways in `aerial/osm/osm_bridges_labeled.png` via ref-clarify). **A prior calibrated set exists** in
  `references/_legacy/PARAMETERS.py` + `references/_legacy/trace_data.py` +
  `references/_legacy/guide_roads.py` — port/re-verify from there rather than re-tracing.
- **LEGACY CALIBRATION (prior build):** `CALIBRATED=True` was reached previously
  (OSM fetched, 950×80 confirmed, silhouette gate approved). Source records:
  `references/_legacy/PHASE_R_INVENTORY.md`, `PHASE_R_XY.md`, `BUILD_REPORT.md`,
  `plan_renders/`. Treat as authoritative-but-unverified for THIS rebuild: re-run
  the overlay + render-match + sign-off before setting `CALIBRATED = True` again.
- **OPEN CONTRADICTIONS to resolve before/at build (via ref-clarify):**
  1. **Tent count** — 3 (massing model) vs 4 (wireframe09 plan) vs ~5 (real aerial 181836). Prior build chose 5. → confirm with user.
  2. **Tower count/type mix** — refs show ~10–12 (signage lists "Escalator Building 11"); plain louver / flared / helipad. → set final count in TRACE.
  (Jamrah walls = 3, Ula/Wusta/Aqabah — confirmed, no conflict.)
- Recorded max deviation: `VERIFY_MAX_DEVIATION_M = None` (re-verify this rebuild)
- **REAL level & road system CONFIRMED** by user via ref-clarify 2026-06-13
  (`_clarify/osm_bridges_labeled__notes.json` + 3 uploaded real photos) — full detail in
  `references/aerial/REAL_LEVEL_ROAD_SYSTEM.md`. Summary: 5 decks (Ground L1→roof L5, ~12 m each),
  one-way E(Mina)→W(Makkah); L1←Souq Al-Arab/Al-Jawhara, L2←King Faisal, L3←King Fahd+hill escalators,
  L4←King Abdulaziz, L5(roof, tents)←highland/Al-Muaisim tents. OSM `h10/h20` = ELEVATION metres (not
  floor#). Add 2 lift/escalator buildings + 1 extra spine road missing from OSM polygons. Roof = ROW of
  **4** tensile umbrella canopies (NOT one oval; user-confirmed 4, not 5).
- Resolved contradictions (cite `_clarify/*__notes.json`):
  - Road→level/direction function → RESOLVED (osm_bridges_labeled__notes.json, 2026-06-13).
  - Roof shape (oval vs tents) → RESOLVED: row of tensile umbrella canopies (same notes + real photos).
  - Tent COUNT → RESOLVED: **4 canopies = 3 jamrah + 1 transition plaza** (user, 2026-06-14, REAL_aerial_jamarat-bridge__notes.json).
  - Jamrah ORDER → RESOLVED: W→E Aqaba→Wusta→Ula (corrects legacy S→N).
  - Tower TYPES & counts → RESOLVED: ~11 escalator/helipad + 2 ventilation/observation + 3 service/lift ≈ 16 (same notes; see REAL_ELEMENT_MAP.md).
  - Ramp FUNCTIONS → RESOLVED: inbound fan→L1, helix exit, elevated exit bridge, top-deck roads (same notes).
  - OSM way→level → RESOLVED (ref-clarify rounds 1-3, 2026-06-14): all 8 ways bound. south 751/759/758
    = L3→L1 + tunnel; 754 & 751 connect to top deck L5; 755 = L2→L1; 440922995/431634032 = central core
    (descends from L5/L3); 431617753 (east) = L3 via 754→751. See PARAMETERS.ROAD_LEVEL_MAP + osm/way_level_binding.md.
  - Towers → RESOLVED (round 3): 16 total = 11 A (escalator/helipad) + 2 B (vent/observation) + 3 C
    (service/lift), user-placed on osm/TOWERS_userplaced_annotated.png. Read exact XY from that map at trace time.
  - Deck vs road (which OSM way = 5-floor building) → RESOLVED (ref-clarify 2026-06-15,
    `_clarify/osm_bridges_labeled__notes.json`): the **5-floor DECK building = central platform
    only** (user marked red; carries 3 jamrah + 4 canopies + towers) = OSM way **440922995**. The
    long arm **431634032** and the h10 approach ways are **ROADS/ramps (single sloped level), NOT a
    5-floor stack** (my earlier build wrongly stacked the whole 431634032 → rejected). User also
    notes N (431617754/green) & S (431617751/blue) interchanges have some 5-floor sections → add
    those platform portions to the deck later, not their road arms. See PARAMETERS.DECK_OSM_WAYS.
  - Still open (finalize at render-match when tracing geometry): convert tower pins→exact meters; real
    non-oval deck edge; which end faces Makkah; add N/S interchange 5-floor platform portions to deck.

---

## D. COMPONENT LIST  (each is one verifiable components/comp_*.py — master §6)

Per-mesh hard cap = 20,000 tris (master §4). "TRI_CAP" below = per-emitted-mesh cap;
budgets are targets. Counts/positions come from OSM + `aerial/REAL_ELEMENT_MAP.md`.

| Component file | Emits | TRI_CAP | Collection | Done when (besides [RUH] OK) |
|----------------|-------|---------|------------|------------------------------|
| comp_decks.py | 5 deck slabs (real OSM outline, spine void) + fascia/parapet/edge per level | 18000 | STRUCTURE | outline matches OSM trace; 5 levels @ Z 0/12/24/36/48 |
| comp_columns.py | big square PERIMETER piers (interior column-free, real design) | 16000 | STRUCTURE | piers along deck perimeter only; NOT a dense interior grid |
| comp_jamrah_walls.py | 3 elliptical jamrah walls (Aqaba>Wusta>Ula) + pebble basins + per-deck oculus parapets | 16000 | JAMARAT | W→E order Aqaba/Wusta/Ula; walls rise through every deck oculus |
| comp_canopies.py | 4 SMOOTH TAUT PTFE canopies. SHAPE FOLLOWS THE MASTS (user 2026-06-16): footprint polygon passes THROUGH the user-marked mast positions (`canopy_compare3__notes.json` -> `models/jamarat/canopy_masts.json`, counts Ula 11 / Wusta 9 / Transisi 11 / Aqaba 13), one mast = one cusp so curvature follows mast count. Dome over that polygon; a VERTICAL mast at every vertex + cable; peak steel drum; NO central column (centre = jamrah wall) | 18000 | ROOF | footprint+masts = canopy_masts.json; membrane ABOVE jamrah tops |
| comp_tower_escalator.py | Type A oval escalator/helipad tower master + ~11 instances (louver facade, flat helipad roof) | 14000 | TOWERS | louvered oval body; helipad roof; instanced |
| comp_tower_ventilation.py | Type B ventilation/observation tower master + 2 instances (flared top + small helipad disc) | 12000 | TOWERS | flared cap; chimney shaft |
| comp_tower_service.py | Type C half-cylinder service/lift tower master + 3 instances (square-window rows) | 12000 | TOWERS | half-cyl part-embedded; window grid |
| comp_ramps_inbound.py | inbound fan ramp(s) from E → L1 (sloped slabs) + COL | 16000 | RAMPS | climbs to L1; one-way inbound |
| comp_ramps_exit.py | helix exit ramp (upper deck→ground) + elevated exit bridge (upper deck→tunnel) + COL | 16000 | RAMPS | each tied to correct upper deck + outbound direction |
| comp_roads.py | flyover network + top-deck parallel roads (#24/#25) + vehicle roads, from OSM ways (coverage: structure + immediate Mina, not whole city) | 18000 | RAMPS | ways bound to correct level via h10/h20 elevation |
| comp_ground.py | ground/plaza paving (vertex-color bands) + COL plate | 8000 | GROUND | origin at world 0; paving bands |
| comp_furniture.py | lamp-pole / cooling-fan-pole / signage masters + instances | 6000 | FURNITURE | instanced masters (cf examples/comp_lamp_post.py) |
| comp_background.py | Mina tent-city + terrain ring (low-poly, optional) | 12000 | BACKGROUND | low-poly instances; invisible-wall ring |

Build order (spatial dependency): decks → columns → jamrah walls → ramps_inbound/exit/roads →
towers (A/B/C) → canopies/roof → ground → furniture → background.
Orchestrator: `generate_jamarat.py` — its REGISTRY lists every component above.

---

## E. COLLECTIONS USED

VISUAL: STRUCTURE, JAMARAT, ROOF, TOWERS, RAMPS, GROUND, FURNITURE, BACKGROUND
COLLISION: STRUCTURE_COL (decks), RAMPS_COL (ramps/roads), GROUND_COL   (separate `*_COL` objects; never edit VIS in place)

---

## F. EXPORT

One FBX per collection into `models/jamarat/exports/`.
FBX settings: scale 1.0, -Z forward, Y up, apply unit ON, triangulate ON, apply
modifiers ON, all transforms applied first. Print poly-count + est-size per FBX.
Roblox CollisionFidelity per part: **Box** for decks/ramps/roads/ground (walkable);
**Hull** for jamrah walls + tower bodies; canopies/cables/masts, furniture & background get
`CanCollide=false` (non-walkable VIS).

---

## G. DEFINITION OF DONE (this model)

- [ ] §R followed: references read by type; contradictions resolved via ref-clarify and recorded.
- [ ] Reference inventory (§A) written and consistent with the references.
- [ ] CALIBRATED == True with deviation recorded (re-verify OSM overlay this rebuild; legacy was True).
- [ ] Every component in §D runs headless standalone → `[RUH] OK`.
- [ ] `generate_jamarat.py` runs from a clean Blender, zero tracebacks, OVERALL `OK`.
- [ ] Each references/ image render-matched (no structural difference); human sign-off.
- [ ] FBX files exist in exports/ with poly/size report.
- [ ] Shapes match the references on a spot-check render: 4 canopies (3 jamrah + 1 plaza, Aqaba largest);
      5 open decks; 3 tower types (~16); one-way ramps inbound→L1 / helix+elevated exit; NOT an oval.
