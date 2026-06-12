# PHASE R — STEP 0 ELEMENT INVENTORY (reference analysis)

> Mandatory per AGENTS.md §4R.0. Written BEFORE any modeling.
> Source images analyzed: **30 files** in `References/` (note: folder is `References/`,
> case-insensitively resolves the PARAMS `references/` path on Windows).
> Authority ranking (AGENTS §4R): satellite/OSM @ REAL_COORDS > published dims
> (950×80 m, 5×12 m) > Sketchfab fan model > render images.

## Image catalog (what each file gives us)

| File | View | Primary use |
|------|------|-------------|
| `top.jpg` | Sketchfab top-down (textured) | XY topology cross-check, paving, road loop |
| `perspective01.jpg` | aerial, W end | overall oval, fan ramps, tents, towers, metro line |
| `perspective02.jpg` | aerial, over spine | tensile tents row, deck loop, tent city |
| `perspective03.jpg` | ground facade | 5 open decks, louvered tower (L), flared tower (R), masts |
| `perspective04.jpg` | ground, circulation tower | cylindrical escalator building w/ window bands, signage |
| `perspective05.jpg` | ground, courtyard gap | two curved deck arms, paving (red/grey), masts |
| `perspective06.jpg` | **interior under roof** | **jamrah elliptical wall + oval basin rim + oculus ring + membrane** |
| `perspective07.jpg` | aerial over spine | **helipad tower**, row of white tents, deck loop, courts |
| `perspective08.jpg` | ground approach | **fan ramps** (red/grey/yellow lanes), louvered+flared towers, fan poles |
| `wireframe01-02.jpg` | aerial wire | topology: spine tents, deck loop, towers, fan ramps, BG city |
| `wireframe03-05.jpg` | ground wire | tower types, masts+guy cables, open deck floors |
| `wireframe06.jpg` | interior wire | jamrah wall topology + oculus truss ring + basin rim |
| `wireframe07.jpg` | aerial wire | flared/helipad tower caps, membrane saddle grid |
| `wireframe08.jpg` | ground wire | fan-ramp lane grid, lamp poles, fences |
| `wireframe09.jpg` | **TOP-DOWN wire (plan)** | **footprint: lens spine, # of tents, road loop, tower positions** |
| `Screenshot 2026-06-09 181836.png` | **REAL aerial photo** | ground-truth massing: ~5 tents, towers, helipad, road loop, Mina |
| `Screenshot 2026-06-10 0803xx/0806xx.png` | massing-model captions 1–5 | **3 jamarat basins labeled**, tower clusters, ramps, top-down (080628) |
| `signs02_uv.jpg` | signage texture sheet | **names**: SMALL/MIDDLE/BIG JAMARAH, floors 1–4, Escalator Bldg 1–11 |
| `penampakan-jumrah-wustha-...webp` | **REAL interior photo (Wustha)** | real jamrah = elliptical stone wall + padded oval basin + deck oculus |

## Element inventory (form → image → build method)

1. **Overall massing** — elongated stadium-oval ≈ 950 m (Y) × 80 m (X). Central
   lens-shaped jamarat **spine** + surrounding multi-level oval **deck loop** + oval
   **road ring** + **fan ramps** flaring at both ends. *[wireframe09, top.jpg, real
   aerial, 080628]*. Build = annular oval slabs (bridge edge loops, NOT boolean).

2. **Jamrah walls ×3** — tall **elliptical stone WALL/blade**, long axis ACROSS the
   spine, taller at one end (sloped top), set in an **oval basin** with a low padded
   rim. Wall rises through an oculus opening in every deck. Named (S→N) **ULA=Small
   /الصغرى, WUSTA=Middle/الوسطى, AQABAH=Big/الكبرى** — confirmed by `signs02_uv`.
   *[perspective06, wireframe06, real webp, 080438]*. Build = ellipse cross-section
   lofted up with taper, granite material. **Count = 3 (authoritative).**

3. **Basins** — oval catchment pit + low rim wall (padded canvas in real photo) per
   wall; per-floor parapet ring around each deck oculus. *[perspective06, real webp]*.

4. **Platforms** — oval standing deck + throwing parapet around each wall, one per
   accessible floor. *[perspective06, real webp]*. Build = oval annulus + parapet.

5. **Decks / floors ×5** — open parking-garage: slab + square **column grid** + open
   sides + horizontal fascia/railing edge. Annular oval (outer + spine void).
   *[perspective03/05, wireframe05, real aerial]*. 5 levels @ 12 m (published).

6. **Columns** — square concrete columns on a grid; one master, instanced/arrayed
   around perimeter + interior ring. *[perspective03, wireframe03/05]*.

7. **Towers (= "Escalator/Circulation Buildings")** — cylindrical, **multiple types**:
   (a) plain **louvered/window-grid** cylinder; (b) **flared "mushroom-cap"** tower;
   (c) **helipad** tower (flared + circular helipad disc w/ H-mark). Clustered at BOTH
   ends + along the loop. *[perspective03/04/07/08, wireframe03/04/07, 0803xx]*.
   ⚠️ **Reference shows ~10–12 towers; signage lists up to "Escalator Building 11".**
   AGENTS §4 example assumes ~6 (`TOWER_TYPES`). **Count to be set in TRACE.**

8. **Tensile roof** — white **conical/saddle membrane** tents over the spine, each
   with a central rigid **oculus ring** (steel truss ring + radial spokes), tall
   **masts** + **guy cables**. *[perspective06/07, wireframe06/07, real aerial]*.
   ⚠️ **Tent count differs by source: Sketchfab plan (wireframe09)=4, massing model=3,
   real aerial photo≈5.** **Count to be set in TRACE (decision needed).**

9. **Fan ramps** — access loops **split into finger ramps** descending to ground at
   both ends; red paving + grey lanes + yellow lane lines. *[perspective08,
   wireframe08, 080438]*. Build = fan of straight sloped slabs per end.

10. **Helical ramps** — spiral ramps looping around towers at the ends.
    *[080715, 080659, wireframe07]*. Build = helix curve + trapezoid profile → mesh.

11. **Ground** — radiating red/grey **paving bands** + yellow lane lines.
    *[perspective08, top.jpg]*. Build = subdivided plane, **vertex color** (no geo).

12. **Furniture** — **Y-branch lamp poles**, tall **cooling-fan poles** (fan head on
    pole), green **signage**. *[perspective05/06/07, signs02_uv]*. Masters, instanced.

13. **Background** — Mina **tent city** (white tent grid), **mountains**, elevated
    **metro line**. *[perspective01/02, wireframe01/02, real aerial]*. Low-poly
    instances; terrain as invisible-wall ring.

## Cross-check vs AGENTS §4: MATCHES, except 3 items to resolve in TRACE
- **Tent count** (membrane roofs): 3 vs 4 vs ~5 across sources — pick for TRACE.
- **Tower count/types**: refs show ~10–12 (signage→11), not ~6 — pick for TRACE.
- **Jamrah walls = 3** confirmed (Ula/Wusta/Aqabah) — no conflict.

## Published dimensions (KNOWN-REAL, no trace needed)
- Length 950 m (Y) × Width 80 m (X); 5 floors @ 12 m (Z 0/12/24/36/48).
- REAL_COORDS 21.42139 N, 39.87278 E (Jamaraat Bridge, OSM way 440922995).

## BLOCKERS for Phase R XY (cannot proceed to layout meshes)
1. **`References/osm/jamarat.osm` is MISSING.** Required for georeferenced XY
   (footprint outline, road/ramp axes, 3 jamarah positions). Per zero-invented-
   coordinates rule, layout numbers cannot be fabricated. Need the human to provide
   the .osm (Overpass query in KICKOFF_PROMPT §4) OR authorize XY from the top-down
   references (wireframe09 / 080628 / top.jpg) at published 950×80 scale.
2. **Calibration gate** needs human sign-off + render-match → `CALIBRATED=True`.

## Rough 3D model (user-supplied, added 2026-06-10)
`References/architectural+complex+3d+model/tripo_convert_*.obj` — Tripo AI
image-to-3D mesh: **971k verts / 1.94M faces**, single un-grouped blob, +PBR
texture set. Normalized (~unit scale), un-oriented. **Authority = shape reference
only** (like Sketchfab fan model; below OSM/renders). NOT usable as deliverable
mesh (too dense, un-separable, not Roblox-conformant). Ortho caps rendered to
`References/rough_ortho/{top,front,side}.png`. **Cross-check result: CONFIRMS the
calibrated TRACE** — central jamarat spine, ~10–12 towers at ends+sides, fan ramps
both ends, flat-and-long massing (footprint ≈ 1.67:1). Used as silhouette reference.

## Flyover vs 5-floor deck analysis (perspective01-08, added 2026-06-10)
Deep re-read of the `perspective*` renders to separate ROADS from the DECK:
- **perspective01** — near end shows **curved flyover ramps** swooping from deck
  level DOWN to the ground plaza (thin sloping ribbons w/ lane markings = roads,
  NOT 5-story). The tented central mass IS the multi-floor deck.
- **perspective02** — elevated road ribbons **weave/curve around** the tented deck
  at mid-height and descend = flyovers, not stacked floors.
- **perspective03 / 05** — confirm the central structure is a true **5-level open
  parking deck** (slab + column grid + open sides).
- **perspective07 / 08** — fan of **sloping finger roads** fanning to ground at the
  ends; helical ramps loop around end towers.
CONCLUSION: the compact central **BODY** = genuine 5 floors; the long **finger/arm
extensions** of the silhouette = **single-level flyover roads that ramp down to
ground** (deck-2 level ≈12 m → ground 0). Build accordingly: floors on BODY_OUTER,
flyovers (FLY_TOP/FLY_BOT) as sloped road slabs in the RAMPS collection.

## Flyover roads + lifts + helipad analysis (added 2026-06-10, all refs re-read)
- **Flyover roads** (080628, top.jpg, perspective01/02/08): **consistent-width**
  road ribbons (NOT wide blobs) forming an **elongated LOOP** (upper arc + lower
  arc) hugging the spine + **fan ramps at both ends**. The wide silhouette lobes
  are deck/courtyard/terrain = NOISE, not roads → do NOT generate them as flyover.
- **Lifts** (perspective03/04, signage "ESCALATOR/CIRCULATION BUILDING, WAY UP"):
  tall **cylindrical towers** with horizontal window bands + internal escalators,
  connecting all floors. Clustered at both ENDS and FLANKING the spine
  ("sampai bagian jamarat"). ~10–12 of them ("Escalator Building 1–11").
- **Helipad** (perspective07): a **cylinder tower carrying a round helipad disc**
  (H/star marking) on top, beside the spine.
- Marking plan for confirmation: `renders/PLAN_flyover_mark.png`
  (roads 1=upper-loop, 2=lower-loop, 3=N-fan, 4=S-fan; 12 lift cylinders; 1 helipad).

## Environment note
- Blender **5.0** installed (`C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`);
  AGENTS assumed 4.x. bpy core API is compatible; will flag any 5.0-specific breakage.
- `blender` not on PATH → skills will call the absolute exe path.
