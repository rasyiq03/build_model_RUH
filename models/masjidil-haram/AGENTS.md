# AGENTS.md — RUH Model Spec: Masjid al-Haram Complex (Masjidil Haram)
# Governs ONLY this model. Read together with the master /AGENTS.md.
# On any conflict:
#   user chat  >  references/ (the images)  >  THIS file  >  master /AGENTS.md.
# Version: 1.0   Date: 2026-06-13

> **This spec is a GUIDE, not a cage.** It points Claude Code at the references
> and lists what to build; exact shapes come from `references/` (see §R). Stay
> faithful to the references; when they're unclear or conflict, ask the user via
> the `ref-clarify` skill — do not guess.

> One-line description: The Grand Mosque of Mecca — the worship complex a player
>   walks for Tawaf and Sa'i, including the Kaaba, the Mataf, the Mas'a
>   (Safa–Marwa), the surrounding multi-level mosque, its named gates, and the
>   numbered facility/gathering points.
> Real-world location: Mecca, Saudi Arabia. Origin (Kaaba): 21.42250 N, 39.82611 E.
> Layout-based (real footprint to trace)?  YES — XY from OSM (see §C + references/OSM_REFERENCE.md).
> **TARGET STATE:** **latest / current configuration** (most recent Saudi
>   expansion as built). Where references show different eras, follow the most
>   recent, and **resolve any conflict with the user via `ref-clarify`** (§R).

# >>> USER OVERRIDE 2026-06-13 (ABSOLUTE — supersedes any conflicting text below):
# 1. PRIORITY = the worship area. The Kaaba, Mataf, and Mas'a get the HIGHEST
#    detail and the largest tri budgets. The outer mosque, gates, and facilities
#    are important but built at lower detail.
# 2. LANDMARKS & WAYPOINTS ARE REQUIRED (§W). Named gates (King Abdulaziz, King
#    Fahd, Al-Fath, Umrah, As-Salam, …) and numbered facility/gathering points
#    (WC / wudhu complexes, e.g. "WC 3") must be present as LABELLED, low-poly
#    points of interest with real positions, doubling as orientation / spawn /
#    meeting points in-game.
# 3. ERA = latest. Conflicts between references (era, count, layout) are NOT
#    decided by the agent — run ref-clarify and let the user decide.
# 4. The Abraj Al-Bait clock tower is a SEPARATE model (models/makkah-tower/) —
#    here it is at most low-poly background.
# (Record resolved contradictions below, each citing its _clarify/*__notes.json.)
#   - none yet

---

## R. REFERENCE FOLDER PROTOCOL  (Claude Code: do this BEFORE & DURING building)

`references/` is the **source of truth** for this model's form — above anything
written here. References were provided by the user (originally in Google Drive:
a rough 3D model `grand+mosque+mecca+3d+model` + wireframe renders `wire_masjid_*`).
Sort the provided files into the typed subfolders, then:

**1. Read each type for its purpose, SEPARATELY:**

| Subfolder              | Use it for                                            |
|------------------------|-------------------------------------------------------|
| `references/aerial/`   | footprint, mosque outline, Mataf ring, positions (XY) |
| `references/exterior/` | facades, minarets, domes, silhouette, materials       |
| `references/interior/` | prayer halls, column grid, Mataf levels, Mas'a corridor|
| `references/section/`  | how floors / levels stack vertically (Z)              |
| `references/detail/`   | close-ups: Kaaba/kiswah, columns, gates, lamps        |
| `references/models/`   | the rough 3D model — CROSS-CHECK only (not ground truth)|
| `references/_clarify/` | annotated images + notes + uploads from `ref-clarify`  |

**2. Authority when types describe the same thing:** real layout data
(OSM/satellite — see `references/OSM_REFERENCE.md`) > `aerial/` > `section/` >
`exterior/`+`interior/` photos > `models/` (rough model = hint only).

**3. CONTRADICTION or AMBIGUITY → ASK THE USER via `ref-clarify`. Do not guess.**
This complex is mid-expansion, so references from different years WILL disagree
(minaret count, new wings, Mas'a levels). For any such conflict, or an element
you cannot identify:

```bash
python .claude/skills/ref-clarify/scripts/ref_annotate.py \
    "models/masjidil-haram/references/<type>/<image>" \
    --question "<exactly what is unclear>" \
    --out-dir models/masjidil-haram/references/_clarify
```

Read back `*__annotated.png` + `*__notes.json` (including `uploaded_references`
— the user may upload a clearer photo/plan as their answer; treat it as
authoritative and file it under the right `references/<type>/`). Record the
resolution in the USER OVERRIDE block or §C.

**4. Missing reference?** Web-search for a supplement, but `references/` stays
primary; flag the gap + your assumption to the user (or just run ref-clarify).

---

## A. REFERENCE INVENTORY  (fill/confirm after sorting references/ — master §9 step 0)

One line per element from the actual files. The references remain authoritative.

> **Reference set migrated 2026-06-13** (78 files). AUTHORITY: these images are ALL
> renders of a fan 3D model (`models/` Tripo .obj + the `ifinger-3d…`, `masjidalharam*`,
> `wire_masjid_*` render series) — CROSS-CHECK HINT only, NOT ground truth. There is **no
> real photo or OSM image** in the folder; `references/OSM_REFERENCE.md` remains the XY-layout
> source of truth, and real layout/scale must come from OSM (master §9). Resolve any
> fan-vs-real conflict via ref-clarify. NB: the fan model renders the **inner old-Ottoman
> Mataf ring only** (octagonal galleried courtyard) — it does NOT include the modern Saudi
> outer expansions/Mas'a fully; treat coverage gaps against OSM, don't copy the model's extent.

| Element              | Looks like (which ref type/file)                         | bpy build method                |
|----------------------|----------------------------------------------------------|---------------------------------|
| Kaaba                | Black cuboid, gold door, kiswah band, marble shadharwan base (`detail/masjidalharam010014.jpg`,`detail/masjidalharam010018.jpg`,`interior/masjidalharam010012*.jpg`) | capped box + kiswah + door detail |
| Hijr Ismail          | Low curved (semicircular) white wall beside Kaaba (`interior/masjidalharam010002.jpg`,`detail/masjidalharam010014.jpg`) | curved low wall (arc → solid)   |
| Maqam Ibrahim        | Small glass-and-metal canopy near Kaaba (`interior/masjidalharam010012.jpg`,`interior/…010015.jpg`) | glass cylinder + metal frame    |
| Mataf                | White marble ring around Kaaba w/ tawaf path lines, ringed by octagonal multi-level arcade (`interior/masjidalharam010002/010011/010015/010017.jpg`,`aerial/masjidalharam010029.jpg`) | marble annulus + parapet, per level |
| Mataf arcade galleries | Octagonal stacked arched colonnade enclosing the Mataf; lower Ottoman arcade + upper floors (`interior/masjidalharam010016/010017.jpg`,`aerial/…010028.jpg`) | annular arch-bay arrays per floor + columns |
| Mas'a (Safa–Marwa)   | Long straight gallery, multi-level, green-zone — NOT in fan model; see OSM_REFERENCE (`section/`,`aerial/` if added) | corridor floors + level stack + markers |
| Haram structure      | Ring of colonnaded prayer halls, pointed-arch facades, multi-floor, blue-grey marble cladding (`exterior/masjidalharam010004/010009/010013.jpg`,`exterior/…_010003/_010016.jpg`) | annular slabs + column grid + arches |
| Domes / kiosks       | Rows of red/maroon ribbed domes + green octagonal pavilion roofs over halls (`detail/masjidalharam010027.jpg`,`exterior/…010023/010026.jpg`,`aerial/`) | spin/screw dome on drum; pavilion = capped octagon roof |
| Minarets             | Tall stone-clad towers, ringed balconies, green octagonal canopy + gold finial (`exterior/masjidalharam010024.jpg`,`exterior/ifinger…(1).jpg`,`aerial/`) | tower master + balconies, instanced |
| Named gates          | Large pointed-arch portals in marble facade (King Fahd etc.) (`exterior/ifinger…(1).jpg`,`exterior/masjidalharam010003/010022.jpg`,`exterior/…_010005.jpg`) | gate master(s), placed + labelled |
| Facility/WC points   | Numbered ablution/toilet blocks & gathering spots (`aerial/`; mostly from OSM) | low-poly block + label (POI)   |
| Ground / plaza       | Paved courtyards around the mosque (`aerial/`)           | subdivided plane + paving + invisible-wall ring |
| Furniture            | Lamp poles, lantern bollards, signage (`detail/`,`interior/`) | instanced (see examples/comp_lamp_post.py) |

---

## B. ELEMENT GUIDE  (pointers — derive exact form from references/, §R)

Shapes are NOT pinned. Detail priority: **Kaaba/Mataf/Mas'a = highest**;
structure/minarets = medium; gates/facilities/ground = low (labelled landmarks).

| Element            | Read shape from         | Build method (ruh_common)                          |
|--------------------|-------------------------|----------------------------------------------------|
| Kaaba              | detail + exterior       | capped box (~11×13×13.1 m); kiswah as material band; gold door inset; Black Stone corner marker |
| Hijr Ismail        | detail + aerial         | arc swept into a low solid wall N side of Kaaba    |
| Maqam Ibrahim      | detail                  | small glass cylinder + metal frame                 |
| Mataf              | aerial + section        | flat marble annulus around Kaaba; repeat per level with parapet ring + edge fascia |
| Mas'a              | interior + section + aerial | straight multi-level corridor; floor slabs per level; green-zone marked via material; Safa & Marwa rock outcrops at the ends |
| Haram structure    | interior + section + exterior | annular floor slabs (bridge edge loops, never boolean) per level; perimeter walls; split into ≤cap meshes |
| Columns            | interior + detail       | one master column → Array/instanced on the grid    |
| Arches             | interior + detail       | one master arch → instanced along colonnades       |
| Minarets           | exterior                | cylinder/taper master + balcony rings + cap; instanced (count from refs) |
| Gates (§W)         | exterior + detail       | gate master(s) (arched portal) placed at real positions; labelled |
| Facility/WC (§W)   | aerial                  | low-poly block at real position; labelled POI       |
| Ground / plaza     | aerial                  | subdivided plane; paving via vertex colour; invisible-wall ring at boundary |

Overall massing: an elongated complex centred on the Kaaba — Mataf ring inside a
multi-level colonnaded building, with the Mas'a gallery running off one side;
**confirm the exact outline from `aerial/` + OSM, and via ref-clarify if unsure.**

---

## W. LANDMARKS & WAYPOINTS  (REQUIRED — see USER OVERRIDE)

These are orientation / spawn / meeting points players rely on. Build each as a
low-poly object **plus a label** (the in-game name), positioned from OSM
(`entrance` nodes, `amenity=toilets`) or from references; unclear ones → ref-clarify.

- **Named gates** (at least the major ones; full set + numbers from refs/OSM):
  King Abdulaziz, King Fahd, Al-Fath, Umrah (Bab al-Umrah), As-Salam.
- **Facility / gathering points**: numbered WC & wudhu complexes (e.g. "WC 3")
  and other regroup spots the references call out.

Emit these in `comp_gates.py` and `comp_landmarks.py` (§D). Keep them low-poly;
the value is correct **position + label**, not geometric detail.

---

## C. CALIBRATION & TRACE  (layout-based)

- XY source: **OSM** — see `references/OSM_REFERENCE.md` (origin = Kaaba
  21.42250 N, 39.82611 E; equirectangular reprojection, x scaled by cos(lat)).
- Z / form source: `section/` + `exterior/` references.
- Fidelity target (as strict as references allow): footprint deviation
  ≤ 5 m AND ≤ 1%. If references can't support that, record best achievable.
- TRACE fields to fill in PARAMETERS.py: `OUTLINE_OUTER` (mosque footprint),
  `MATAF_CENTER` (= Kaaba), `MASA_AXIS` (Safa→Marwa endpoints), `GATES`
  (named gate positions), `FACILITIES` (numbered WC/gathering positions),
  `MINARETS` (positions).
- `CALIBRATED = True` only after metric overlay + render-match + human sign-off
  (master §9). Unsure at any step → ref-clarify.
- Recorded max deviation: `VERIFY_MAX_DEVIATION_M = <fill>`
- Resolved contradictions (cite `_clarify/*__notes.json`): none yet

---

## D. COMPONENT LIST  (each is one verifiable components/comp_*.py — master §6)

Build order respects dependency: ground/footprint → structure → Mataf → Mas'a →
Kaaba & details → columns/arches → minarets → gates → landmarks → furniture.

| Component file            | Emits                                             | TRI_CAP | Collection   | Done when (besides [RUH] OK) |
|---------------------------|---------------------------------------------------|---------|--------------|------------------------------|
| comp_ground.py            | plaza/ground + paving + invisible-wall ring       | 4000    | GROUND       | paving via vertex colour; boundary ring closes |
| comp_haram_structure.py   | multi-level annular slabs + perimeter walls (split into ≤cap meshes) | 18000/mesh | STRUCTURE | walkable levels; each mesh watertight; COL slabs |
| comp_mataf.py             | marble Mataf ring per level + parapets             | 12000   | MATAF        | levels match refs; flat & walkable; COL disc |
| comp_masaa.py             | Mas'a corridor floors per level + Safa/Marwa ends + green-zone | 14000 | MASAA | ~450 m length, multi-level; walkable; COL slabs |
| comp_kaaba.py             | Kaaba cube + kiswah + door + Black Stone + Hijr Ismail + Mizab | 4000 | KAABA | cube ~11×13×13.1 m; NOT walk-through (hull COL) |
| comp_maqam_ibrahim.py     | Maqam Ibrahim canopy                               | 1500    | KAABA        | placed near Kaaba per refs |
| comp_columns.py           | master column + instanced grid (all levels)        | 200 (master) | COLUMNS  | count matches grid; instanced |
| comp_arches.py            | master arch + instanced along colonnades           | 400 (master) | COLUMNS  | instanced; no n-gons |
| comp_minarets.py          | minaret master + instances (count from refs)       | 12000/minaret | MINARETS | correct count & positions |
| comp_gates.py             | named gate master(s) placed + labelled (§W)        | 6000    | GATES        | major gates present at real positions, labelled |
| comp_landmarks.py         | numbered WC/wudhu + gathering POIs, labelled (§W)  | 3000    | LANDMARKS    | POIs at real positions, labelled |
| comp_furniture.py         | lamp poles, signage (instanced)                    | 2000 (masters) | FURNITURE | instanced; masters within budget |

Orchestrator: `generate_masjidil_haram.py` — its REGISTRY lists every component above.
(Large elements such as the structure emit MULTIPLE meshes; each must be ≤ its cap.)

---

## E. COLLECTIONS USED

VISUAL: KAABA, MATAF, MASAA, STRUCTURE, COLUMNS, MINARETS, GATES, LANDMARKS, GROUND, FURNITURE
COLLISION: COL_STRUCTURE, COL_MATAF, COL_MASAA, COL_KAABA, COL_GATES, COL_WALLS
(separate `*_COL` objects; never edit VIS in place)

---

## F. EXPORT

One FBX per collection into `models/masjidil-haram/exports/`.
FBX settings: scale 1.0, -Z forward, Y up, apply unit ON, triangulate ON, apply
modifiers ON, all transforms applied first. Print poly-count + est-size per FBX.
Roblox CollisionFidelity: Box for flat decks/Mataf/Mas'a/ground; Hull for the
Kaaba and gate masses; non-walkable VIS (minarets, arches, furniture, landmarks
geometry) gets `CanCollide=false`. Enable StreamingEnabled in-game (large model).

---

## G. DEFINITION OF DONE (this model)

- [ ] §R followed: references sorted by type; contradictions resolved via ref-clarify and recorded.
- [ ] Reference inventory (§A) confirmed against the references.
- [ ] Landmarks & Waypoints (§W) present: major named gates + numbered facility/gathering POIs, labelled, at real positions.
- [ ] `CALIBRATED == True`, footprint deviation recorded (`VERIFY_MAX_DEVIATION_M`).
- [ ] Every component in §D runs headless standalone → `[RUH] OK`.
- [ ] `generate_masjidil_haram.py` runs from a clean Blender, zero tracebacks, OVERALL `OK`.
- [ ] Render-match against references (worship area especially); human sign-off.
- [ ] FBX files in exports/ with poly/size report.
- [ ] Spot-check render: Kaaba cube + Mataf ring + multi-level Mas'a + colonnaded structure + correct minaret count + labelled gates/WC points.
