# Jamaraat Bridge — REAL level & road/flyover system (ground-truth notes)

Compiled 2026-06-13 from authoritative public sources (see bottom). This is REAL
reference data for the USER OVERRIDE requirement: roads/ramps must be correct by
FUNCTION (which approach feeds which deck level + one-way direction), not just XY.
Treat as ground truth alongside OSM; verify the per-ramp geometry against OSM +
user ref-clarify before building.

## Levels
- **5 floors today**, each **~12 m** high (foundation built to support up to 12).
  (One source titled it "six levels" — likely counting ground/podium + 5; resolve
  the count vs OSM/ref-clarify. Working value: 5 decks @ 12 m, Z = 0/12/24/36/48.)
- Capacity target ~5 million pilgrims; designed flow ~300,000 pilgrims/hour.

## Approach → level mapping (one-way; crowds from different roads never cross)
- **Floor 1 (lowest):** pilgrims from the **Mina direction**, via approach roads from
  **Souq Arab & Souq Al-Jouharah**, north of the tent city.
- **Floor 2:** pilgrims from **south Mina**, via the **Southern Pedestrian Road & King
  Faisal Street**.
- **Floor 3:** pilgrims from **central Mina, King Fahd Street**, and the **Mina hill
  slopes**; entry/exit via large **escalators** + stairs.
- **Floor 4:** pilgrims from the **King Abdulaziz Street** direction.
- **Floor 5 (top / roof):** the three Jamarat are covered here by **tents/umbrellas**
  (tensile membrane canopies) for shade/heat — this is the ROOF the user means by
  "atap tenda, bukan oval". (Confirm floor-5 approach/exit routing via ref-clarify.)

## Counts / infrastructure (real)
- ~**12 entrances**, **12 exit roads** from **4 directions**; **2 tunnels** (pedestrian/
  vehicle separation); **19 ramps**, total length ≈ **7.7 km**, widths **24–42 m**.
- Helipads on top; air-conditioning + water-spray cooling (~29 °C target).
- The 3 Jamarat are **elliptical walls** (not pillars) rising through all decks: Ula
  (smallest), Wusta (middle), Aqabah (largest).

## OSM ways present (from references/aerial/osm/, see osm_bridges_labeled.png)
Multiple bridge polygons w/ size + a height-ish tag (h10/h20) — likely the deck +
flyover/ramp network at different levels:
- 431634032  978×88  h10   ← main long deck (~the published 950×80 m body)
- 431617753  1030×155 h10
- 431617751  634×289  h20
- 440922995  523×132  h20
- 431617754  224×116  h20
- 431617755  299×63   h10
- 431617758  266×23   h10
- 431617759  272×26   h10
The h10/h20 tag MAY indicate level/height band — use as a hint, confirm which way =
which deck level + direction via ref-clarify (the 2D OSM ways don't state the level).

## ✅ CONFIRMED via ref-clarify 2026-06-13 (user = authoritative; see _clarify/osm_bridges_labeled__notes.json + 3 uploaded real photos)
Overall flow is **one-way East (Mina) → West (toward Makkah)**. Final level/approach map
(user's naming; 5 decks, Ground = L1 … roof = L5):
- **L1 / Ground** ← main Mina roads N/E (**Jl. Souq Al-Arab & Jl. Al-Jawhara**); exit toward Makkah via lower route.
- **L2** ← **south Mina, mainly Jl. King Faisal**.
- **L3** ← **central Mina, Jl. King Fahd** + **hill-slope** pilgrims via **external escalators**.
- **L4** ← **Jl. King Abdulaziz** direction.
- **L5 (roof)** ← pilgrims from **highland/hill tents (e.g. Al-Muaisim area)**; covered by giant **tent canopy** (sun shade).
- **h10/h20 OSM tags = ELEVATION in metres, NOT floor index** (floor spacing ~10–12 m): h10 ≈ 10 m (≈L2), h20 ≈ 20 m (≈L3). Use to infer which way sits at which level.
- **Main deck vs ramp in OSM:** main deck = wide closed polygon (`highway=pedestrian`,`bridge=yes`); ramps = single/double lines (`highway=footway/path`, often `incline=up/down` or `highway=steps` for escalators).
- **MISSING from OSM polygons (user-added, must model):** near the jamarat spine — **2 lift/elevator buildings** + **1 additional access road** (marked green/blue, box #1 in the annotated map). The prominent **cylindrical towers** in the real photos = the escalator/lift/circulation buildings.

### Real-photo readings (uploaded; in aerial/REAL_aerial_*.jpg + exterior/REAL_decks_ramps_oneway.jpeg)
- Structure = **multi-level OPEN decks** (slab + columns + open sides), ~4–5 decks + tented roof ⇒ **5 levels**, each ~12 m (Z 0/12/24/36/48).
- Roof = **a ROW of 4 white tensile MEMBRANE umbrella canopies** over the spine (USER-CONFIRMED 2026-06-13: **4 tents, not 5**) — NOT one oval shell.
- **Curved flyover ramps** sweep in from several directions and spiral down to ground (one-way); separate wide **vehicle roads** (buses) run alongside, plus pedestrian approaches.
- Prominent **cylindrical escalator/lift towers** cluster around the spine + deck edges.

## Open items to resolve (ref-clarify / OSM)
1. Exact level count (5 vs "6") and Z of each deck.
2. Bind each OSM bridge way → its real deck level + one-way travel direction
   (map the Floor 1–4 approach list above onto the labeled ways).
3. Floor-5 (roof) access/exit routing + tent layout.
4. How wide to extend the surrounding Mina road network (user: "luas tapi jangan
   terlalu luas" — structure + approaches + immediate Mina roads).

## Sources
- Saudipedia — "How Many Floors Does the Jamaraat Bridge Have?": https://saudipedia.com/en/how-many-floors-does-the-jamaraat-bridge-have
- Saudi Gazette — "Jamarat Bridge divided into six levels": https://saudigazette.com.sa/article/163296
- Arab News — award-winning Jamarat Bridge: https://www.arabnews.com/node/2119591/saudi-arabia
- Wikipedia — Jamaraat Bridge: https://en.wikipedia.org/wiki/Jamaraat_Bridge
