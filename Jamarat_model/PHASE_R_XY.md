# PHASE R — XY CALIBRATION (OSM reprojection results)

Source: `References/osm/jamarat.osm` — fetched from Overpass API (real data,
© OpenStreetMap contributors, ODbL). 1913 nodes, 304 ways, 8 `man_made=bridge`,
162 highways. Tools: `scripts/phase_r_osm_reproject.py`, `phase_r_inspect_bridges.py`,
`phase_r_fit_trace.py`. Overlays: `References/osm/osm_overlay.png`,
`osm_bridges_labeled.png`, `proposed_overlay.png`.

## The 8 bridge decks (PCA extent, local meters)

| Way | L×W (m) | height | role |
|-----|---------|--------|------|
| **440922995** "جسر الجمرات" | 523×132 | 20 | **named core bridge / central deck** |
| **431634032** | 978×88 | 10 | long through-deck → **validates published 950×80** |
| 431617753 | 1030×155 | 10 | parallel through-deck (NE arm) |
| 431617751 | 634×289 | 20 | **wide deck-loop bulge** (SE) |
| 431617754 | 224×116 | 20 | NW deck/platform |
| 431617755 | 299×63 | 10 | NW ramp slab |
| 431617758 / 431617759 | ~270×25 | 10 | **fan-ramp fingers** (SE) |

## Validated facts
- **Published 950 × 80 m is CONFIRMED** by OSM way 431634032 (978×88 m): dev
  L≈28 m (2.9%), W≈8 m. The "80 m" is the **spine through-deck width**.
- 5 floors @ 12 m and REAL_COORDS (21.42139 N, 39.87278 E) stand.
- Origin set at core-deck centroid; long axis aligned to +Y via way 431634032.

## Honest finding (the calibration tension)
OSM models Jamarat as **~8 overlapping multi-level slabs** forming a **curved,
banana-shaped complex ≈ 1070 m × 520 m** (incl. parallel through-decks + ramp
fingers). The "iconic" 5-floor deck-loop the references show is the **central
core ≈ 580 × 290 m**. **This real footprint does NOT reduce to a clean
single-axis stadium-oval within the 5 m / 1 % gate** — a clean oval deviates
50–190 m from the OSM sprawl (it is a different idealization, not an error).

Also: the **3 jamarah walls are NOT in OSM** (they sit inside the deck). Their
XY is **reference-derived** (interpolated on the spine centerline, real spacing
Ula→Wusta ≈ 135 m, Wusta→Aqabah ≈ 247 m), with no OSM ground-truth to gate against.

## Proposed TRACE (concrete, see `References/osm/proposed_trace.json`)
- `OUTLINE_OUTER`: deck-loop oval ~ 640 (Y) × 290 (X) — the playable hero loop.
- `OUTLINE_VOID`: central spine opening ~ 430 (Y) × 64 (X) over the jamarat.
- `PILLARS`: ULA (0,−191), WUSTA (0,−56), AQABAH (0,+192); wall long-axis = X,
  length 26 m, base thick 4 m (form from interior refs perspective06/webp).
- Fan-ramp mouths: RAMP_N (0,+470), RAMP_S (0,−470) — full length ≈ 950 m.

## Gate reconciliation needed (decision in chat)
The literal 5 m/1 % outline gate is unachievable vs OSM's idealized sprawl. The
overall **length/width metric DOES pass** (950×80 confirmed). Recommend the
outline gate be **silhouette/topology match + human sign-off** (per AGENTS §4R.4b/c),
while keeping the metric check on overall extents and jamarah spacing.
