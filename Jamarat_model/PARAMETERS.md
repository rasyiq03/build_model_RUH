# PARAMETERS.md — Human reference (v3.1, REAL SCALE + references + OSM)
# DERIVED from PARAMETERS.py (authoritative). Regenerate when .py changes.

## Reference strategy (how "100% same" is achieved & proven)
- **FORM (Z / shape):** the agent MUST analyze every image in `references/`
  (8 renders + optional Sketchfab ortho caps) in Phase R Step 0 and build each
  element to match — counts, silhouettes, proportions from the images.
- **XY (footprint, roads, 3 jamarah positions):** from **OpenStreetMap** real
  coordinates (Jamaraat Bridge = OSM way 440922995, bbox in PARAMS), reprojected
  lat/long -> meters. No tracing. Attribution: © OpenStreetMap contributors.
- **Cross-check:** Google Earth at 21.42139N, 39.87278E (optional).

## Fidelity gate (operational meaning of "100% bentuk sama")
`REFERENCE["FIDELITY"]`: XY deviation vs OSM <= 5 m AND <= 1%; **render-match**
each reference image from the same camera angle (no structural difference);
**human sign-off**. Only then `CALIBRATED = True`. Honest caveat: this is
indistinguishable-on-review fidelity, not bit-identical to non-public CAD.

## Scale (REAL)
950 m (Y) x 80 m (X), 5 floors @ 12 m. FLOOR_Z = {1:0,2:12,3:24,4:36,5:48}.
Roblox imports at this size — enable StreamingEnabled.

## LAYOUT vs DETAIL
- **LAYOUT** (`PARAMS["TRACE"]`): footprint, road/ramp axes, pillar pos+angle+len,
  roof outlines, tower pos/type. **None until calibrated** — zero invented coords.
- **DETAIL**: subdivisions, thickness, louver/grid counts — low-poly defaults OK.

## Calibration gate
**`CALIBRATED = True` (Fase R PASSED 2026-06-10).** OSM fetched (Overpass, way
440922995/431634032), reprojected to local m; published **950×80 confirmed**
(OSM 978×88, dev 2.9%). Outline approach = **clean oval + silhouette gate**
(approved): OUTER 634×288 vs OSM deck-loop 634×289 → dev ≈ 1 m. Jamarah XY +
roof + towers are **reference-derived** (not in OSM). Human sign-off obtained.
See `PHASE_R_INVENTORY.md`, `PHASE_R_XY.md`, `References/osm/*overlay.png`.

## Key constants (full dict in PARAMETERS.py)
```
BUILDING_LENGTH=950  BUILDING_WIDTH=80  FLOOR_COUNT=5  FLOOR_GAP=12
POLY_LIMIT_PER_MESH=20000  POLY_WARN_THRESHOLD=19500
REFERENCE.IMAGES_DIR="references/"  REFERENCE.OSM.WAY_ID=440922995
FIDELITY: XY_TOL=5m/1%, RENDER_MATCH=True, HUMAN_SIGNOFF=True
```

## Filled trace (Fase R, calibrated)
- OUTLINE_OUTER = oval 634(Y)×288(X) m; OUTLINE_VOID = oval 470×150 m.
- PILLARS: ULA(0,−191) WUSTA(0,−56) AQABAH(0,+192); wall long-axis X, len 26 m.
- ROAD_AXES: oval ring 720×370 m. RAMP_AXES: FAN_N/S mouths ±470, 2 helix.
- ROOF_MEMBRANES: 5 tents along spine (peaks Y −200..+200). TOWERS: 12 (PLAIN/
  FLARED/HELIPAD). VERIFY_MAX_DEVIATION_M = 1.0 m (tol 5 m).
