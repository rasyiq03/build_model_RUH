# PARAMETERS.py — numbers for model: Masjid Al-Nimrah (Arafah)
# Single source of truth. Components import from here; never hardcode a number.
# Units: METRIC, 1 BU = 1 m, Z = up.

# --- Roblox budget (same hard cap for every model) ---------------------------
POLY_HARD_CAP       = 20000
POLY_WARN_THRESHOLD = 19000

# --- Calibration gate (layout-based models) ----------------------------------
TARGET_STATE = "{{era / configuration, e.g. current ~2020s}}"  # build this state
CALIBRATED = False          # set True only after master §9 gate passes
VERIFY_MAX_DEVIATION_M = None

# --- Material slot names -----------------------------------------------------
MATERIALS = {
    "CONCRETE": "MAT_CONCRETE",
    "GRANITE":  "MAT_GRANITE",
    "METAL":    "MAT_METAL_FRAME",
    "GLASS":    "MAT_GLASS",
    "MARBLE":   "MAT_MARBLE",
    # add model-specific materials here
}

# --- TRACE (fill from references / OSM; "N/A" if detail-only) -----------------
TRACE = {
    # "OUTLINE_OUTER": [...],
    # "AXES": {...},
    # "POSITIONS": {...},
}

# =============================================================================
# COMPONENT PARAMETERS — one dict per components/comp_*.py
# Each MUST define TARGET_TRI (<= POLY_HARD_CAP).
# =============================================================================

# {{PART_1}} = {
#     "TARGET_TRI": 2000,
#     ...
# }
