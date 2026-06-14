# OSM way → deck-level binding (Jamarat trace XY)

Frame: PCA-aligned local meters (`local_meters.json`), origin ≈ (21.42089 N, 39.87244 E),
Y = long axis (~length), X = width. Published core deck = 950 (Y) × 80 (X). Z up.

## Hard OSM facts (parsed from local_meters.json + jamarat.osm)
**OSM encodes only TWO height bands (10 m & 20 m), NOT the 5 decks.** So OSM gives the
footprint + a coarse 2-level hint only; the full 5-deck stack (Z 0/12/24/36/48) and each
ramp's real level (L1–L5) come from the user's functional map (REAL_LEVEL_ROAD_SYSTEM.md)
+ real photos. **Only 1 tower** is in OSM (way 758592950) → the ~16 towers must be placed
from the user-annotated aerial, not OSM.

| OSM way | size Lx×Ly (m) | height | layer | centroid (x,y) | geometry hint | HYPOTHESIS (confirm w/ user) |
|---------|----------------|--------|-------|----------------|---------------|------------------------------|
| **431634032** | 102×979 | 10 | 1 | (-113, 129) | long thin, west, full length | **core multi-level DECK spine** (the jamarat building footprint ≈ 950×80) |
| 440922995 | 145×521 | 20 | 1 | (18, -19) | central, upper | central **upper deck / flyover** over the core |
| 431617753 | 151×1031 | 10 | 1 | (139, 116) | east, very long | **east approach road/deck** |
| 431617751 | 503×414 | 20 | 1 | (-26, -250) | south, very wide | **south interchange / fan-ramp** (upper) |
| 431617754 | 201×129 | 20 | 1 | (-67, 270) | north, upper | **north interchange / ramp** (upper) |
| 431617755 | 59×299 | 10 | 1 | (24, 531) | far north, lower | **north approach road** (lower) |
| 431617759 | 81×265 | 10 | 1 | (21, -435) | far south, lower | **south approach road** (lower) |
| 431617758 | 97×257 | 10 | **-1** | (-76, -426) | far south, layer −1 | **south TUNNEL / underground** approach |

Escalator ways (`highway=steps conveying=yes`): 676129858, 676130171 (+ steps 795251558).
Lone OSM tower: way 758592950 (`man_made=tower, building=yes`).

## User functional level map (from REAL_LEVEL_ROAD_SYSTEM.md, authoritative)
L1/Ground ← Souq Al-Arab/Al-Jawhara (Mina N/E) · L2 ← King Faisal (Mina S) ·
L3 ← King Fahd + hill escalators (Mina center) · L4 ← King Abdulaziz · L5 roof ← highland tents.

## ✅ CONFIRMED via ref-clarify 2026-06-14 (osm_bridges_labeled__notes.json, pins #1-4)
- **South interchange = 4 DESCENT ramps, one-way L3 → L1** (user marked 4 pins on the
  southern convergence where ways **431617751 (blue), 431617759 (brown), 431617758 (purple)**
  + the south end of **431634032 (pink)** meet). I.e. pilgrims exit the upper L3 deck and
  these southern ramps bring them DOWN to ground L1.
- Still UNCONFIRMED (user left blank this round): north ways (431617755, 431617754), east
  431617753, central 440922995, the core 431634032 body level, and ALL ~16 tower positions.

## ✅ ROUND 2 ref-clarify 2026-06-14 (osm_bridges_labeled__notes.json, pins #1-8) — level per road
Verbatim user statements + best-guess way attribution (confidence). Overall: upper decks are
fed by the h20 interchanges; exits descend to L1; the core jamarat sits central.
- **#1 "JAMARAT ADA DI SINI" (central)** → core deck = central **440922995 + 431634032** (HIGH).
- **#2 "turun L3→L1, nyambung ke L3 di bawah jalan #5"** → central road, **440922995** (MED).
- **#3 "turun dari Lantai 5"** → **431634032** (pink core/west spine) descends from L5 (MED).
- **#4 "menyatu dengan lantai puncak (L5)"** → **431617751** (blue, h20) connects to TOP deck L5 (MED-HIGH).
- **#5 "menyatu dengan lantai puncak (L5)" (+user added road lines)** → **431617754** (green, h20) → L5 (MED-HIGH).
- **#6 "turun L2→L1"** → **431617755** (red, north) descent L2→L1 (MED).
- **#7 "L3→L1"** → **431617759** (brown, south) (HIGH).
- **#8 "L3→L1"** → **431617758** (purple, south; also tunnel layer −1) (HIGH).
- 431617753 (east approach) → RESOLVED round 3: enters **L3** via green-zone 754, reconnects to L3 at blue-zone 751.

## ✅ ROUND 3 ref-clarify 2026-06-14 (TOWERS_userplaced_*) — towers + way 753
- **16 towers placed by user** on the OSM plan (pins + circles), types CONFIRMED:
  **11 × A** (escalator/access + helipad; louvered facade), **2 × B** (ventilation/observation
  "flare", chimney + obs deck + small helipad), **3 × C** (service/lift; half-cylinder, small
  square windows). Exact plan XY = `osm/TOWERS_userplaced_annotated.png` (+ `_notes.json`).
- **way 753 = L3** (east, via 754→751). All 8 OSM ways now level-bound.
Note: 431617751 is a big interchange — connects UP to L5 (#4) AND has the south descent ramps
to L1 (round-1). Both true: it's the interchange + its descent fingers.
NB: pin→way attribution is by on-map position; finalize exact way-IDs at render-match when tracing geometry.

## TO CONFIRM later → then write into PARAMETERS.TRACE
1. Bind each way above → its real deck level + one-way direction (correct/replace hypothesis).
2. Place the ~16 towers (A escalator/helipad ×~11, B ventilation ×2, C service/lift ×3) on the map.
3. Confirm which way = the core jamarat deck vs pure ramp/road.
