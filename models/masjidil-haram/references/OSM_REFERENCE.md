# OSM REFERENCE — Masjid al-Haram (Masjidil Haram)
# Author: compiled for RUH. This is the XY-layout source of truth for the model.
# Master rule: LAYOUT (footprint, axes, positions) comes from real OSM data —
# never invented. Z/form comes from the image references.

## 1. Local coordinate frame

- ORIGIN (local 0,0,0) = **Kaaba centre = 21.42250 N, 39.82611 E** (Wikipedia).
- Reprojection: equirectangular, origin at the Kaaba.
  - 1° latitude  ≈ 110,574 m
  - 1° longitude ≈ 103,600 m   ( = 111,320 × cos(21.4225°), cos ≈ 0.9307 )
  - local_x (E+) = (lon − 39.82611) × 103,600
  - local_y (N+) = (lat − 21.42250) × 110,574
- Axes: Y = N–S, X = E–W, Z = up. Metric, 1 BU = 1 m.

## 2. Metric anchors (for SCALE calibration — not final node coords)

- Mas'a (Safa–Marwa): length ~450 m, width ~40 m, multi-level, axis runs roughly
  N(N-E)–S; Safa at the south end (~130 m SE of the Kaaba), Marwa at the north
  end (~300 m NE of the Kaaba).
- Kaaba: ~11 × 13 m base, ~13.1 m tall, corners aligned to the cardinal directions.
- Zamzam well: ~20 m east of the Kaaba (now under the Mataf).
- Minarets: 13, each ~139 m tall (CONFIRM latest count against references).
- Mosque site area: ~356,000 m² (older figure); the latest Saudi expansion is
  substantially larger — the TARGET STATE is "latest", so take the footprint
  from the OSM export below, not from this number.

> IMPORTANT: the lat/longs above are reliable only for the Kaaba origin. For the
> mosque outline and every element position, use the OSM export (§3) — do NOT
> rely on scraped lat/longs for node coordinates.

## 3. How to fetch the real OSM data (run where there is internet)

Claude Code's environment has internet; fetch the live vector there.

**Option A — Overpass Turbo** (https://overpass-turbo.eu): paste and Run, then
Export → GeoJSON.

```overpassql
[out:json][timeout:90];
// Centre on the Kaaba; radius covers the whole Haram + immediate surroundings.
(
  // the mosque building / outline
  way["amenity"="place_of_worship"](around:650,21.42250,39.82611);
  relation["amenity"="place_of_worship"](around:650,21.42250,39.82611);
  // named gates / entrances (waypoints, §W)
  node["entrance"](around:650,21.42250,39.82611);
  way["entrance"](around:650,21.42250,39.82611);
  // facility / gathering points: toilets & ablution (waypoints, §W)
  node["amenity"="toilets"](around:700,21.42250,39.82611);
  way["amenity"="toilets"](around:700,21.42250,39.82611);
  node["amenity"="place_of_worship"]["wudu"](around:700,21.42250,39.82611);
);
out geom;
```

Then identify the **"Al-Masjid Al-Haram"** way/relation in the result (its
`name`/`name:en` tag) — that is the footprint. Read gate names from the
`entrance`/`name` tags, and WC/wudhu positions from `amenity=toilets`.

**Option B — openstreetmap.org Export**: search "Al-Masjid Al-Haram", open it,
use the Export tab to download the `.osm` for the bounding box around the Kaaba.

**Option C — blosm / blender-osm addon**: import OSM buildings+roads for the
bbox directly into Blender at real scale (then reproject as in §1).

## 4. What to write into PARAMETERS.TRACE (after fetching)

- `OUTLINE_OUTER` ← the mosque footprint polygon (reprojected to local meters).
- `MATAF_CENTER`  ← (0,0) (the Kaaba).
- `MASA_AXIS`     ← Safa & Marwa endpoints (local meters) + length/width.
- `GATES`         ← {name: (x,y)} for the major named gates (and others present).
- `FACILITIES`    ← {label: (x,y)} for numbered WC / wudhu / gathering points.
- `MINARETS`      ← [(x,y), ...] minaret base positions.

## 5. Verification (master §9)

Overlay the traced skeleton (footprint + Mas'a axis + gate/WC points) on the
aerial reference; worst-case deviation ≤ 5 m AND ≤ 1%. Record in
`PARAMETERS.VERIFY_MAX_DEVIATION_M`. If references disagree (era/expansion),
resolve with the user via `ref-clarify` — do not guess.

## Attribution
Map data © OpenStreetMap contributors (ODbL). Include this attribution in-game.
