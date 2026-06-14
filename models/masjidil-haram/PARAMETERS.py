# PARAMETERS.py — numbers for model: Masjid al-Haram Complex (Masjidil Haram)
# Single source of truth. Components import from here; never hardcode a number.
# Units: METRIC, 1 BU = 1 m, Z = up.  Origin = Kaaba centre (local 0,0,0).

# --- Target state / calibration ----------------------------------------------
TARGET_STATE = "latest (most recent Saudi expansion, as built); conflicts -> ref-clarify"
CALIBRATED = False                  # set True only after master §9 gate passes
VERIFY_MAX_DEVIATION_M = None

# --- Roblox budget (same hard cap for every model) ---------------------------
POLY_HARD_CAP       = 20000
POLY_WARN_THRESHOLD = 19000

# --- Geo anchor (origin of local meters) -------------------------------------
# See references/OSM_REFERENCE.md. Reproject: equirectangular, origin at Kaaba,
# x scaled by cos(lat). Exact node coords come from the OSM export, NOT scraped.
GEO = {
    "ORIGIN_LATLON": (21.42250, 39.82611),   # Kaaba centre
    "M_PER_DEG_LAT": 110574.0,
    "M_PER_DEG_LON": 103600.0,                # = 111320 * cos(21.4225°)
}

# --- TRACE (fill from OSM export / aerial; meters, origin at Kaaba) -----------
# Anchors below are APPROXIMATE (for scale calibration). Replace with traced
# values from references/OSM_REFERENCE.md before building LAYOUT meshes.
TRACE = {
    "OUTLINE_OUTER": [],          # mosque footprint polygon (from OSM)
    "MATAF_CENTER":  (0.0, 0.0),  # = Kaaba
    "MASA_AXIS":     {"safa": None, "marwa": None, "length_m": 450.0, "width_m": 40.0},
    "GATES":         {},          # {name: (x, y)} from OSM entrance nodes
    "FACILITIES":    {},          # {label: (x, y)} numbered WC / wudhu / gathering
    "MINARETS":      [],          # [(x, y), ...]
}

# --- Material slot names ------------------------------------------------------
MATERIALS = {
    "MARBLE":   "MAT_MARBLE",
    "GRANITE":  "MAT_GRANITE",     # Kaaba body
    "KISWAH":   "MAT_KISWAH",      # black/gold cloth band
    "CONCRETE": "MAT_CONCRETE",
    "METAL":    "MAT_METAL_FRAME",
    "GLASS":    "MAT_GLASS",
    "GOLD":     "MAT_GOLD",        # door / mizab
    "GREEN":    "MAT_GREEN",       # Mas'a green-zone marker
}

# =============================================================================
# COMPONENT PARAMETERS — one dict per components/comp_*.py.
# Dimensions are starting points; exact form comes from references/ (see AGENTS §R).
# Each dict MUST define TARGET_TRI (<= POLY_HARD_CAP).
# =============================================================================

KAABA = {
    "TARGET_TRI": 4000,
    "WIDTH_X":   11.0,   # ~11 m
    "WIDTH_Y":   13.0,   # ~13 m
    "HEIGHT":    13.1,   # ~13.1 m
    "DOOR":      {"w": 1.7, "h": 3.3},          # gold door (approx; confirm from refs)
    "HIJR_RADIUS": 8.5,  # Hijr Ismail arc radius N of Kaaba (confirm)
    "MATERIAL_BODY": "GRANITE",
    "MATERIAL_CLOTH": "KISWAH",
}

MATAF = {
    "TARGET_TRI": 12000,
    "LEVELS": 2,         # ground + upper deck (confirm count from refs)
    "INNER_CLEAR": 10.0, # clearance around Kaaba before walking ring (confirm)
    "RING_WIDTH": 45.0,  # marble ring width (confirm)
    "PARAPET_H": 1.1,
    "MATERIAL": "MARBLE",
}

MASA = {
    "TARGET_TRI": 14000,
    "LENGTH":  450.0,    # Safa -> Marwa
    "WIDTH":   40.0,
    "LEVELS":  3,        # basement + ground + upper (confirm from section refs)
    "FLOOR_H": 6.0,
    "MATERIAL": "MARBLE",
    "GREEN_MATERIAL": "GREEN",
}

STRUCTURE = {
    "TARGET_TRI": 18000,   # per emitted mesh; split building into <=cap pieces
    "LEVELS": 4,           # basement, ground, 1, roof (confirm)
    "FLOOR_H": 12.0,
    "MATERIAL": "CONCRETE",
}

COLUMNS = {
    "MASTER_TRI": 200,
    "SIDE": 1.2,           # square column side (confirm)
    "MATERIAL": "MARBLE",
}

ARCHES = {
    "MASTER_TRI": 400,
    "SPAN": 6.0,
    "MATERIAL": "MARBLE",
}

MINARETS = {
    "TARGET_TRI": 12000,   # per minaret
    "COUNT": 13,           # latest count — CONFIRM from references
    "HEIGHT": 139.0,
    "BASE_RADIUS": 4.0,
    "MATERIAL": "MARBLE",
}

GATES = {
    "TARGET_TRI": 6000,
    "MATERIAL": "MARBLE",
    "LABELLED": True,
    # names confirmed/extended from refs/OSM:
    "MAJOR": ["King Abdulaziz", "King Fahd", "Al-Fath", "Umrah", "As-Salam"],
}

LANDMARKS = {
    "TARGET_TRI": 3000,
    "LABELLED": True,
    # numbered WC / wudhu / gathering points; positions from OSM/refs
}

GROUND = {
    "TARGET_TRI": 4000,
    "RADIUS": 400.0,       # plaza extent (confirm)
    "MATERIAL": "CONCRETE",
}

FURNITURE = {
    "MASTER_TRI": 2000,
    # reuse the lamp-post pattern from examples/comp_lamp_post.py
}
