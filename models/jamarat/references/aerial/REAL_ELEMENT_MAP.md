# Jamarat — REAL element map (user-annotated, AUTHORITATIVE)

Source: ref-clarify on `aerial/REAL_aerial_jamarat-bridge.jpg`, user annotations
2026-06-14 → `_clarify/REAL_aerial_jamarat-bridge__annotated.png` +
`_clarify/REAL_aerial_jamarat-bridge__notes.json` (25 pins + flow arrows).
This OUTRANKS the legacy build and the fan model. Pixel coords are in the
annotated image space (1300×864). Overall flow: one-way, inbound from EAST
(Muzdalifah/Mina) → outbound WEST (toward Makkah).

## Canopies over the spine = 4 total, but only 3 cover jamrah pillars
(West → East along the spine: Aqaba … [transition] … Wusta … Ula)
- **#1 Aqaba (al-Kubra / Big)** — WESTMOST. **Largest** canopy. Single central mast +
  radial steel cables to an **oval ring** at the membrane edge; white **PTFE** membrane.
  **Widest pebble basin** below. Thrown first on 10 Dhulhijjah. `jamrah_id="aqaba"`, canopy
  slightly bigger than #3/#4.
- **#2 Transition plaza** — between Aqaba & Wusta. **NOT a jamrah** — circulation/buffer
  plaza. Same mast+cable+PTFE canopy but **NO pebble basin**; open plaza floor below.
  `jamrah_id="transition_ab"`, no basin.
- **#3 Wusta (Middle)** — center. **Medium** canopy (≈ #4), dome slightly taller than #4;
  standard pebble basin. `jamrah_id="wusta"`.
- **#4 Ula (al-Sughra / Small)** — EASTMOST. **Smallest** canopy; standard basin. Daily
  throwing order starts here (Ula→Wusta→Aqaba). `jamrah_id="ula"` (good NPC spawn start).
- All canopies: central mast + radial cables → oval edge ring + white PTFE membrane (tensile
  umbrella). Sizes: Aqaba > Wusta ≈ Ula; #2 ≈ same, no basin.

## Decks / floors = 5 (repeatedly stated "kelima lantai dek"), ~12 m each (Z 0/12/24/36/48)

## Ramps / flyovers (by FUNCTION — match real, see also REAL_LEVEL_ROAD_SYSTEM.md)
- **#23 Main pedestrian ACCESS ramp (INBOUND)** — fan/"corong" ramp from the EAST
  (Muzdalifah + far Mina/Mina Jadid); climbs gently and connects to **L1 (First Floor,
  one deck above ground)**. Orange inbound arrows.
- **#5 Helix curved pedestrian EXIT ramp (OUTBOUND)** — spirals down from an upper deck
  (≈L2/L3), looping over the ground roads, lands at ground/mid pedestrian level. Curved
  because 12 m/floor needs a gentle gradient (wheelchair-safe). Pink outbound arrows.
- **#6 Elevated EXIT bridge/ramp (OUTBOUND, high level)** — attaches directly to an upper
  deck (≈L2/L3); a long elevated bridge over the Mina camps → pedestrian tunnel (toward
  Makkah/Aziziyah) or slowly ramps down far away. Blue outbound arrows. Separated from inbound.
- **#24 & #25 Top-deck-level parallel roads** — run level with the TOP deck; reachable up via
  the towers (e.g. #11/#12/#13).
- Vehicle roads (buses/cars) run alongside at ground, SEPARATE from pedestrian routes
  (cyan arrows in annotation ≈ vehicle/secondary flow).

## Towers — THREE distinct types (design as 3 master meshes, instanced)
- **Type A — Escalator/Access + Helipad towers** (pins #7,#8,#9,#10,#11,#12,#13,#14,#15,#16,#17
  → ~**11**): large **OVAL** towers; massive escalators + emergency stairs inside (move crowds
  between decks); **flat roof = helipad**; facade = **vertical louvers** (not closed concrete).
- **Type B — Ventilation & Observation towers** (pins #18,#19 → **2**): tall **cylinder** =
  giant exhaust chimney for the tunnels/ground floor; **flared top** = observation / CCTV crowd
  control; small **helipad disc** on roof. (= the old "flare/helipad tower".)
- **Type C — Service & Elevator towers** (pins #20,#21,#22 → **3**): **half-cylinder** (partly
  embedded in the deck); lift + stairs for staff/medical/disabled + utility shaft; facade =
  **small square windows in vertical rows**; roof = lift machine-room (slightly curved/angled).
- Total ≈ **16 towers** (11 A + 2 B + 3 C). Confirm exact positions vs OSM/photo when building.

## To confirm later (user offered more ref-clarify rounds)
- Exact tower positions (bind pins → OSM ways / XY).
- Which specific ramp (OSM way) = inbound-L1 vs exit-helix vs elevated-exit, and exact deck
  level each upper ramp leaves from (L2 vs L3).
- Tunnel (2×) + underground vehicle/pedestrian separation geometry.
