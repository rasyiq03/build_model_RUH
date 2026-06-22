# PARAMETERS.py — numbers for model: Jamarat Bridge Complex
# Single source of truth. Components import from here; never hardcode a number.
# Units: METRIC, 1 BU = 1 m, Z = up.
#
# STATUS: DRAFT TRACE (hypothesis) 2026-06-14. Built from:
#   - REAL functional data (authoritative, user-annotated): references/aerial/REAL_LEVEL_ROAD_SYSTEM.md
#     + references/aerial/REAL_ELEMENT_MAP.md + references/aerial/osm/ (OSM way geometry).
#   - Legacy calibrated numbers ported from references/_legacy/PARAMETERS.py, CORRECTED to the user's
#     real findings (4 canopies = 3 jamrah + 1 transition plaza; jamrah labels; 3 tower types).
# "# VERIFY@render" marks a hypothesis to confirm at the render-match gate (master §9) before CALIBRATED=True.

import math
import os
import json

# --- Real OSM footprint loader (GROUND TRUTH for deck/road shape) -------------
# Polygons are already reprojected to local meters + rotated (long axis = Y) in
# references/aerial/osm/local_meters.json ("rotation_rad_applied"). This is the
# authoritative non-oval footprint (legacy oval = REJECTED, see AGENTS USER OVERRIDE).
_OSM_LOCAL_METERS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "references", "aerial", "osm", "local_meters.json",
)
# 5-FLOOR DECK building footprint = central platform ONLY.
# USER CLARIFY 2026-06-15 (_clarify/osm_bridges_labeled__notes.json): the long arm
# (431634032) is a ROAD/ramp, NOT a 5-floor stack. The 5-floor building is the central
# platform (user marked red) that carries all 3 jamrah + 4 canopies + towers = way 440922995.
# Long arms / approaches (431634032, 431617753, 751/754/755/758/759) -> comp_roads/comp_ramps_*.
# TODO: user notes the N (green 431617754) & S (blue 431617751) interchanges have some 5-floor
#       sections too -> add those platform portions to the deck later (not their road arms).
DECK_OSM_WAYS = ["440922995"]   # central jamarat platform (contains Ula/Wusta/Aqaba + canopies)


def load_osm_ways():
    """Return {way_id: [(x,y), ...]} for every bridge_way, in local meters.
    The closing duplicate point (last == first) is dropped."""
    with open(_OSM_LOCAL_METERS, encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for w in data["bridge_ways"]:
        pts = [(round(x, 3), round(y, 3)) for x, y in w["xy"]]
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        out[w["id"]] = pts
    return out

POLY_HARD_CAP       = 20000
POLY_WARN_THRESHOLD = 19000

# --- Calibration gate ---------------------------------------------------------
TARGET_STATE = "current expanded Jamaraat Bridge, 5 decks + tensile tents (latest ~2010s-2020s)"
CALIBRATED = False          # set True only after OSM overlay + render-match + human sign-off
VERIFY_MAX_DEVIATION_M = None

# --- Known-real constants (published + OSM-confirmed; no trace needed) ---------
BUILDING_LENGTH = 950.0     # Y (long axis)
BUILDING_WIDTH  = 80.0      # X
ORIGIN          = (0.0, 0.0, 0.0)
FLOOR_COUNT     = 5
FLOOR_GAP       = 12.0      # floor-to-floor (~12 m real)
FLOOR_Z         = {1: 0.0, 2: 12.0, 3: 24.0, 4: 36.0, 5: 48.0}   # L1 ground ... L5 roof (tents)
REAL_COORDS       = (21.42139, 39.87278)                          # Wikipedia / OSM way 440922995
OSM_ORIGIN_LATLON = (21.420887412621358, 39.872441130097094)     # local_meters.json frame origin

# --- Material slots -----------------------------------------------------------
MATERIALS = {
    "CONCRETE": "MAT_CONCRETE", "GRANITE": "MAT_GRANITE", "MEMBRANE": "MAT_MEMBRANE",
    "PAVING_RED": "MAT_PAVING_RED", "PAVING_GREY": "MAT_PAVING_GREY",
    "METAL": "MAT_METAL_FRAME", "GLASS": "MAT_GLASS",
}


# --- Parametric helper: racetrack (NOT a pure oval) ---------------------------
def racetrack(half_len_y, half_wid_x, seg_round=24, cx=0.0, cy=0.0):
    """Racetrack ring: straight sides along Y + rounded semicircle ends. Returns
    list[(x,y)] (closed loop, open list). Long axis = Y. Closer to the real deck
    than an ellipse. VERIFY@render: refine real (non-oval) edges from OSM/aerial."""
    r = half_wid_x
    sy = max(half_len_y - r, 0.0)        # half-length of the straight part
    pts = [(cx + r, cy - sy), (cx + r, cy + sy)]              # right straight, bottom->top
    for i in range(1, seg_round):                            # top semicircle right->left
        a = math.pi * i / seg_round
        pts.append((cx + r * math.cos(a), cy + sy + r * math.sin(a)))
    pts += [(cx - r, cy + sy), (cx - r, cy - sy)]            # left straight, top->bottom
    for i in range(1, seg_round):                            # bottom semicircle left->right
        a = math.pi + math.pi * i / seg_round
        pts.append((cx + r * math.cos(a), cy - sy + r * math.sin(a)))
    return [(round(x, 3), round(y, 3)) for x, y in pts]


# =============================================================================
# TRACE — layout from real data (OSM + user-annotated photos). METER, origin = footprint center.
# =============================================================================
TRACE = {
    # --- Core multi-level DECK footprint (5 decks stacked at FLOOR_Z) ----------
    # Racetrack fit to published real 950x80 (legacy metric dev ~1 m vs OSM deck-loop).
    # VERIFY@render: real deck is not a clean oval — refine from OSM ways 431634032/440922995 + aerial.
    "DECK_HALF_LEN_Y": 475.0,             # 950 / 2
    "DECK_HALF_WID_X": 40.0,              # 80 / 2
    "DECK_SPINE_VOID_HALF_X": 14.0,       # central open slot the jamrah rise through  # VERIFY@render

    # --- 3 JAMRAH walls (elliptical blades, long axis across spine = X) --------
    # Along +Y: ULA (-Y end, smallest) -> WUSTA -> [transition gap ~248 m] -> AQABAH (+Y end, biggest).
    # VERIFY@render: which physical end faces Makkah (user: Aqaba = toward Makkah end).
    "JAMRAH": {
        "ULA":    {"id": "ula",   "pos": (0.0, -191.0), "len_x": 24.0, "thick_y": 4.0, "basin": True, "size": "small"},
        "WUSTA":  {"id": "wusta", "pos": (0.0,  -56.0), "len_x": 26.0, "thick_y": 4.0, "basin": True, "size": "mid"},
        "AQABAH": {"id": "aqaba", "pos": (0.0,  192.0), "len_x": 30.0, "thick_y": 4.5, "basin": True, "size": "big"},
    },
    "JAMRAH_HEIGHT_TOTAL": 52.0,          # tops ~4 m above top deck (48), UNDER the canopy membrane

    # --- 4 tensile umbrella canopies (3 over jamrah + 1 transition plaza) ------
    # Ported from legacy ROOF_MEMBRANES (peaks -178/-60/+60/+178) — matches user's "4 canopies".
    # Real canopies = large NEAR-CIRCULAR white umbrella discs forming a row that
    # nearly touches (aerial/REAL_aerial_jamarat-bridge.jpg) — NOT small spine-long
    # ovals. foot_len_y (Y, along spine) ~= foot_wid_x (X, across); Aqaba biggest.
    # (user 2026-06-15: fix ratio+size). VERIFY@render: exact diameter/overlap.
    # Real canopies (user 2026-06-16): SMOOTH TAUT membranes; the EDGE CURVATURE
    # FOLLOWS THE MAST COUNT — each perimeter mast = a cusp, the footprint is the
    # polygon THROUGH the masts (more masts = rounder). Mast POSITIONS user-marked
    # (ref-clarify canopy_compare3__notes.json -> models/jamarat/canopy_masts.json).
    # "masts" is informational; comp_canopies derives count+positions from that json.
    "CANOPIES": [
        {"over": "ula",        "peak": (0.0, -178.0), "masts": 11, "basin": True},
        {"over": "wusta",      "peak": (0.0,  -60.0), "masts": 9,  "basin": True},
        {"over": "transition", "peak": (0.0,   60.0), "masts": 11, "basin": False},  # plaza, NO basin
        {"over": "aqaba",      "peak": (0.0,  178.0), "masts": 13, "basin": True},   # biggest
    ],
    "CANOPY_PEAK_Z": 68.0, "CANOPY_RIM_Z": 56.0,   # membrane sits ABOVE jamrah tops (52) — no poke-through

    # --- Towers: 3 TYPES (~16). positions APPROX (from user photo annotation) ---
    # type: A_ESC_HELIPAD (oval, louver, helipad roof; ~11) | B_VENT_OBS (flared chimney + disc; 2)
    #       | C_SERVICE_LIFT (half-cylinder, square windows; 3).  VERIFY@render: exact XY from aerial.
    "TOWERS": [
        {"pos": (-150.0,  300.0), "type": "A_ESC_HELIPAD"},
        {"pos": ( 150.0,  300.0), "type": "A_ESC_HELIPAD"},
        {"pos": (-160.0,  150.0), "type": "A_ESC_HELIPAD"},
        {"pos": ( 160.0,  150.0), "type": "A_ESC_HELIPAD"},
        {"pos": (-160.0,    0.0), "type": "A_ESC_HELIPAD"},
        {"pos": ( 160.0,    0.0), "type": "A_ESC_HELIPAD"},
        {"pos": (-160.0, -150.0), "type": "A_ESC_HELIPAD"},
        {"pos": ( 160.0, -150.0), "type": "A_ESC_HELIPAD"},
        {"pos": (-150.0, -300.0), "type": "A_ESC_HELIPAD"},
        {"pos": ( 150.0, -300.0), "type": "A_ESC_HELIPAD"},
        {"pos": (   0.0,  360.0), "type": "A_ESC_HELIPAD"},
        {"pos": ( 200.0,  120.0), "type": "B_VENT_OBS"},
        {"pos": (-200.0, -120.0), "type": "B_VENT_OBS"},
        {"pos": ( -60.0,  -56.0), "type": "C_SERVICE_LIFT"},   # near spine (user: lift bldgs at spine)
        {"pos": (  60.0,  -56.0), "type": "C_SERVICE_LIFT"},
        {"pos": (   0.0,  192.0), "type": "C_SERVICE_LIFT"},
    ],

    # --- Ramps / flyovers by FUNCTION (one-way E in -> W out) ------------------
    # CONFIRMED 2026-06-14: south interchange ramps descend L3 -> L1 (user ref-clarify).
    # Others = hypothesis from REAL_LEVEL_ROAD_SYSTEM.md. VERIFY@render.
    "RAMPS": {
        "INBOUND_FAN": {"from_dir": "E (Muzdalifah/Mina)", "to_level": 1, "osm_hint": "431617753",
                        "mouth": (0.0, -470.0), "deck_join": (0.0, -300.0), "count": 4, "spread_deg": 70.0, "width": 10.0},  # VERIFY
        "SOUTH_EXIT":  {"function": "descent fan", "from_level": 3, "to_level": 1, "confirmed": True,
                        "osm_ways": ["431617751", "431617759", "431617758"], "fingers": 4},  # CONFIRMED
        "HELIX_EXIT":  {"function": "descent helix", "from_level": 3, "to_level": 1,  # VERIFY
                        "centers": [(-150.0, 250.0), (150.0, -250.0)], "r_in": 10.0, "r_out": 20.0},
        "ELEVATED_EXIT_BRIDGE": {"function": "long elevated outbound", "from_level": 3,  # VERIFY
                        "osm_hint": "440922995", "to": "Mina tunnel / toward Makkah"},
        "TOP_DECK_ROADS": {"function": "roads level with top deck", "level": 5, "access": "via towers"},  # VERIFY
    },

    # --- OSM way -> level binding (user ref-clarify rounds 1+2; see osm/way_level_binding.md) ---
    # attribution by on-map position (finalize exact way-IDs at render-match when tracing geometry).
    "ROAD_LEVEL_MAP": {
        "431634032": {"role": "core/west deck spine (JAMARAT here); descends from L5", "level": "core/5->1", "height_m": 10, "confirmed": True},   # #1,#3
        "440922995": {"role": "central core deck; road descends L3->L1",              "level": "core/3->1", "height_m": 20, "confirmed": True},   # #1,#2
        "431617751": {"role": "interchange: connects UP to top deck L5 + south descent fingers to L1", "level": "5 + 3->1", "height_m": 20, "confirmed": True},  # #4 + round1
        "431617754": {"role": "north interchange: connects to top deck L5",           "level": 5,           "height_m": 20, "confirmed": True},   # #5
        "431617755": {"role": "north approach: descent L2->L1",                       "level": "2->1",      "height_m": 20, "confirmed": True},   # #6
        "431617759": {"role": "south approach/descent",                              "level": "3->1",      "height_m": 10, "confirmed": True},   # #7, round1
        "431617758": {"role": "south descent + tunnel (layer -1)",                   "level": "3->1/-1",   "height_m": 10, "confirmed": True},   # #8, round1
        "431617753": {"role": "east approach: enters L3 via green-zone 754, then reconnects to L3 at blue-zone 751", "level": 3, "height_m": 10, "confirmed": True},  # user round 3
    },
    # Towers: 16 total, user-placed on osm/TOWERS_userplaced_annotated.png (+ _notes.json).
    # Counts/types CONFIRMED (user round 3): 11x A_ESC_HELIPAD + 2x B_VENT_OBS + 3x C_SERVICE_LIFT.
    # Exact plan XY: read from that annotated map at trace/render time (pins are in OSM-plot pixel space).
    "TOWER_COUNTS_CONFIRMED": {"A_ESC_HELIPAD": 11, "B_VENT_OBS": 2, "C_SERVICE_LIFT": 3},
    "COVERAGE_NOTE": "structure + its approach/ramp system + immediate Mina roads (per OSM); "
                     "NOT the whole city (user: 'luas tapi jangan terlalu luas').",
    "VERIFY_METHOD": "OSM overlay (footprint vs ways 431634032/440922995) + render-match each real aerial "
                     "+ human sign-off; re-run before setting CALIBRATED=True.",
}

# =============================================================================
# COMPONENT PARAMETERS — one dict per components/comp_*.py (each TARGET_TRI <= cap)
# Targets from AGENTS.md §D. DETAIL knobs (verts/thickness) may use sensible defaults.
# =============================================================================
DECKS        = {"TARGET_TRI": 18000, "OUTER_VERTS": 96, "SLAB_THICK": 0.5, "FASCIA": 0.8, "PARAPET_H": 1.1}
# Columns: PERIMETER PIERS ONLY — interior is intentionally COLUMN-FREE.
# DATA (web, 2026-06-15): the current Jamaraat Bridge was designed for column-free
# interior spaces, clear spans 60-100 m (max 97 m) so pilgrims see all 3 jamrah from
# anywhere; deck = box girders @9 m + cross diaphragms @12 m, supported at the edges.
# So NO interior grid (old 12 m grid of 314 thin posts = REJECTED). Big edge piers,
# spaced ~PERIM_SPACING along the perimeter, inset slightly from the edge.
COLUMNS      = {"TARGET_TRI": 16000, "SIZE": 2.5, "PERIM_SPACING": 12.0, "RING_INSET": 2.2}
JAMRAH_WALLS = {"TARGET_TRI": 16000, "WALL_VERTS": 24, "THICK_BASE": 4.0, "THICK_TOP": 2.5,
                "BASIN_RIM_H": 0.9, "PLATFORM_THICK": 0.3, "PLATFORM_PARAPET_H": 1.1}
CANOPIES     = {"TARGET_TRI": 18000, "MEMBRANE_THICK": 0.1, "GRID_U": 28, "GRID_V": 32,
                "RING_RADIUS": 5.0, "RING_TUBE": 0.4, "MAST_PER_TENT": 8, "MAST_RADIUS": 0.6,
                "MAST_HEIGHT": 30.0, "CABLE_RADIUS": 0.06}
TOWER_ESCALATOR   = {"TARGET_TRI": 14000, "RADIUS": 6.0, "VERTS": 48, "HEIGHT": 54.0, "OVAL_RATIO": 1.4,
                     "LOUVER_COUNT": 36, "LOUVER_DEPTH": 0.25, "HELIPAD_RADIUS": 10.0}
TOWER_VENTILATION = {"TARGET_TRI": 12000, "RADIUS": 4.0, "VERTS": 36, "HEIGHT": 58.0,
                     "FLARE_RADIUS": 9.0, "FLARE_HEIGHT": 4.0, "DISC_RADIUS": 6.0}
TOWER_SERVICE     = {"TARGET_TRI": 12000, "RADIUS": 4.5, "VERTS": 32, "HEIGHT": 50.0, "WINDOW_ROWS": 12, "EMBED": True}
RAMPS_INBOUND = {"TARGET_TRI": 16000, "WIDTH": 10.0, "THICKNESS": 0.4, "GRADIENT": 0.08}
RAMPS_EXIT    = {"TARGET_TRI": 16000, "WIDTH": 8.0, "THICKNESS": 0.4, "HELIX_LANES": 4, "GRADIENT": 0.08}
ROADS         = {"TARGET_TRI": 18000, "WIDTH_LOOP": 14.0, "WIDTH_APPROACH": 11.0, "THICKNESS": 0.4}
GROUND        = {"TARGET_TRI": 8000, "SUBDIVISIONS": 8, "Z": 0.0, "PAVING_BANDS": 14, "LANE_LINE_W": 0.2}
FURNITURE     = {"TARGET_TRI": 6000, "LAMP_H": 8.0, "LAMP_SPACING": 10.0, "FAN_POLE_H": 4.0,
                 "FAN_HEAD_R": 0.8, "SIGN_W": 2.0, "SIGN_H": 0.8}
BACKGROUND    = {"TARGET_TRI": 12000, "MINA_TENT_COUNT": 500, "TERRAIN_RING_R": 600.0}

# --- FBX export groups (one FBX per group / collection) -----------------------
FBX_GROUPS = {
    "STRUCTURE": ["STRUCTURE"], "RAMPS": ["RAMPS"], "JAMARAT": ["JAMARAT"], "TOWERS": ["TOWERS"],
    "ROOF": ["ROOF"], "GROUND": ["GROUND"], "FURNITURE": ["FURNITURE"], "BACKGROUND": ["BACKGROUND"],
}
