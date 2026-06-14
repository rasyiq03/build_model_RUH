# =============================================================================
# JAMARAT 3D — Roblox Pipeline
# File: PARAMETERS.py  (v3.0 — REAL SCALE + reference-driven calibration gate)
#
# PEMISAHAN PENTING:
#   LAYOUT  = koordinat/sumbu/footprint -> WAJIB ditrace dari referensi nyata.
#             Tidak boleh dikarang. Field LAYOUT diisi None sampai ditrace.
#   DETAIL  = resolusi/ketebalan/jumlah subdivisi -> low-poly OK, default boleh.
#
# CALIBRATED gate: selama False, agent DILARANG export final (lihat AGENTS Fase R).
# =============================================================================

import math
import trace_data as _T   # auto-generated EXACT abstract footprint (rough model)

# Sudah dikalibrasi dari trace referensi? (di-set True hanya setelah Fase R lolos)
# Fase R LOLOS 2026-06-10: OSM (way 440922995/431634032) reproject + validasi
# 950x80 (OSM 978x88, dev 2.9%) + silhouette gate + human sign-off. Lihat
# PHASE_R_INVENTORY.md & PHASE_R_XY.md. Outline = clean oval (disetujui).
CALIBRATED = True


# -----------------------------------------------------------------------------
# TRACE GENERATORS — bentuk parametrik bersih yang difit ke footprint OSM nyata
# (clean-oval + silhouette gate, disetujui Fase R). Origin = pusat footprint.
# -----------------------------------------------------------------------------
def _ellipse_ring(half_len_y, half_wid_x, n=96, cx=0.0, cy=0.0):
    """Oval ring (racetrack-ish), long axis = Y. Returns list[(x,y)] CCW, open."""
    out = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        out.append((round(cx + half_wid_x * math.cos(t), 3),
                    round(cy + half_len_y * math.sin(t), 3)))
    return out

PARAMS = {

    # =========================================================================
    # REFERENCE — sumber kebenaran & angka publik terverifikasi
    # =========================================================================
    "REFERENCE": {
        "SKETCHFAB_UID": "ec0db00a3587489c9e2f18ebe5a289d3",
        "REAL_COORDS": (21.42139, 39.87278),   # lat, long (Wikipedia)
        "SCALE_MODE": "REAL",                   # 1 BU = 1 meter, ukuran asli
        # Angka publik terverifikasi (Saudipedia/IslamiCity/Wikipedia):
        "REAL_LENGTH": 950.0,                   # m (sumbu Y)
        "REAL_WIDTH":   80.0,                   # m (sumbu X)
        "REAL_FLOOR_COUNT": 5,
        "REAL_FLOOR_HEIGHT": 12.0,              # m per lantai
        "JAMARAT_ORDER_SOUTH_TO_NORTH": ["ULA", "WUSTA", "AQABAH"],  # konfirmasi via trace

        # --- IMAGE REFERENCES (bentuk 3D / Z) ---
        # Agent WAJIB membuka & menganalisis SETIAP file di folder ini sebelum
        # membangun, lalu menyusun inventory elemen (lihat AGENTS Fase R Step 0).
        "IMAGES_DIR": "references/",
        "IMAGES_EXPECTED": (
            "8 render (2 aerial, fasad ground, antar-menara, interior jamrah, "
            "aerial helipad, approach ground, top-down plan) + screenshot ortho "
            "Sketchfab (top/front/side) bila ada. Semua file di IMAGES_DIR dipakai."
        ),

        # --- OSM (koordinat XY nyata) ---
        "OSM": {
            "WAY_ID": 440922995,                # Jamaraat Bridge (OSM way)
            "BBOX_S_W_N_E": (21.4155, 39.8665, 21.4275, 39.8795),  # untuk Overpass
            "EXPORT_PATH": "references/osm/jamarat.osm",   # taruh export di sini
            "ATTRIBUTION": "© OpenStreetMap contributors (ODbL)",
        },

        # --- FIDELITY GATE (target "100% bentuk sama", versi terukur) ---
        "FIDELITY": {
            "XY_TOLERANCE_M": 5.0,        # deviasi absolut maks vs OSM
            "XY_TOLERANCE_PCT": 1.0,      # deviasi maks % dari dimensi elemen
            "RENDER_MATCH_REQUIRED": True,  # render tiap sudut referensi & banding
            "HUMAN_SIGNOFF_REQUIRED": True, # konfirmasi visual akhir oleh manusia
        },
    },

    # =========================================================================
    # KNOWN-REAL — konstanta absolut (tidak perlu ditrace)
    # =========================================================================
    "BUILDING_LENGTH": 950.0,   # Y
    "BUILDING_WIDTH":   80.0,   # X
    "BUILDING_ORIGIN": (0.0, 0.0, 0.0),

    "FLOOR_COUNT": 5,
    "FLOOR_HEIGHT": 0.5,        # tebal slab (detail)
    "FLOOR_GAP":   12.0,        # floor-to-floor (REAL)
    "FLOOR_Z":         {1: 0.0,  2: 12.0,  3: 24.0,  4: 36.0,  5: 48.0},
    "FLOOR_SURFACE_Z": {1: 0.5,  2: 12.5,  3: 24.5,  4: 36.5,  5: 48.5},

    "POLY_LIMIT_PER_MESH": 20000,
    "POLY_WARN_THRESHOLD": 19500,

    # =========================================================================
    # LAYOUT (PENDING TRACE) — diisi dari screenshot ortho. JANGAN dikarang.
    # Semua koordinat dalam METER, origin di pusat footprint (0,0).
    # =========================================================================
    # FILLED Fase R 2026-06-10. OUTER/VOID = clean oval fit ke OSM deck-loop
    # (way 431617751 = 634x289 m -> OUTER 634x288). PILLARS/ROOF/TOWERS =
    # reference-derived (3 jamrah tak ada di OSM; ditrace dari foto interior +
    # massing model + foto udara nyata). Origin di pusat footprint, METER.
    "TRACE": {
        # === EXACT abstract footprint, traced from the user's rough 3D model ===
        # (References/rough_ortho/rough_top.png via OpenCV). NOT an oval.
        "SILHOUETTE":  _T.SIL_OUTER,    # full road/plaza network footprint (ground)
        "SIL_HOLES":   _T.SIL_HOLES,    # open courtyards in the silhouette
        "BODY_OUTER":  _T.BODY_OUTER,   # 5-floor deck body (silhouette, fingers clipped)
        "BODY_HOLES":  _T.BODY_HOLES,   # courtyards within the deck body
        "OCULUS":      _T.OCULUS,       # small throwing openings at the 3 jamarah
        # flyover ROADS = silhouette fingers beyond the body, ramp down to ground:
        "FLY_TOP":     _T.FLY_TOP, "FLY_BOT": _T.FLY_BOT,
        "BODY_HALF_Y": _T.BODY_HALF_Y, "FLY_TIP_Y": _T.FLY_TIP_Y,
        # legacy keys kept for code that still expects an outline list:
        "OUTLINE_OUTER": _T.BODY_OUTER,
        "OUTLINE_VOID":  (_T.BODY_HOLES[0] if _T.BODY_HOLES else _T.OCULUS["WUSTA"]),

        # 3 dinding jamrah (S->N): ULA, WUSTA, AQABAH. Long axis = X (lintang spine).
        # Spasi nyata: Ula->Wusta ~135 m, Wusta->Aqabah ~247 m (terpusat di void).
        "PILLARS": {
            "ULA":    {"pos": (0.0, -191.0), "length": 26.0, "thick": 4.0, "angle_deg": 90.0},
            "WUSTA":  {"pos": (0.0,  -56.0), "length": 26.0, "thick": 4.0, "angle_deg": 90.0},
            "AQABAH": {"pos": (0.0,  192.0), "length": 26.0, "thick": 4.0, "angle_deg": 90.0},
        },

        # Jalan (ground), dikoreksi agar sesuai referensi Screenshot 080628:
        # cincin LOOP yang memeluk dek + jalan APPROACH menyebar (fan) di kedua ujung.
        "ROAD_AXES": {
            "LOOP": {"half_len_y": 335.0, "half_wid_x": 165.0, "width": 14.0},
            "APPROACH": {
                "N": {"origin": (0.0,  330.0), "count": 4, "spread_deg": 90.0,
                      "length": 180.0, "width": 11.0},
                "S": {"origin": (0.0, -330.0), "count": 4, "spread_deg": 90.0,
                      "length": 180.0, "width": 11.0},
            },
        },

        # Ramp: mulut fan di kedua ujung + helix di sekitar menara ujung.
        "RAMP_AXES": {
            "FAN_N": {"mouth": (0.0,  470.0), "deck_join": (0.0,  300.0),
                      "count": 5, "spread_deg": 70.0, "width": 8.0},
            "FAN_S": {"mouth": (0.0, -470.0), "deck_join": (0.0, -300.0),
                      "count": 5, "spread_deg": 70.0, "width": 8.0},
            "HELIX": [{"center": (-150.0,  250.0), "r_in": 10.0, "r_out": 20.0},
                      {"center": ( 150.0, -250.0), "r_in": 10.0, "r_out": 20.0}],
        },

        # Atap tensile: 4 tenda sepanjang spine (HARUS 4). peak (x,y) + footprint.
        # Bentuk = ROUNDED-SQUARE bergerigi (squircle+scallop), BUKAN oval/bulat.
        # Ukuran lebih kecil supaya TIDAK 100% menutupi spine (ada celah antar tenda).
        "ROOF_MEMBRANES": [
            {"peak": (12.0, -178.0), "foot_len_y": 44.0, "foot_wid_x": 24.0},
            {"peak": (12.0,  -60.0), "foot_len_y": 44.0, "foot_wid_x": 24.0},
            {"peak": (12.0,   60.0), "foot_len_y": 44.0, "foot_wid_x": 24.0},
            {"peak": (12.0,  178.0), "foot_len_y": 44.0, "foot_wid_x": 24.0},
        ],

        # Menara (~12, match references). type: PLAIN|FLARED|HELIPAD.
        "TOWERS": [
            {"pos": (-110.0,  300.0), "type": "FLARED"},
            {"pos": ( 110.0,  300.0), "type": "PLAIN"},
            {"pos": (-150.0,  220.0), "type": "PLAIN"},
            {"pos": ( 150.0,  220.0), "type": "PLAIN"},
            {"pos": (-160.0,   60.0), "type": "FLARED"},
            {"pos": ( 160.0,   60.0), "type": "HELIPAD"},
            {"pos": (-160.0,  -60.0), "type": "PLAIN"},
            {"pos": ( 160.0,  -60.0), "type": "PLAIN"},
            {"pos": (-150.0, -220.0), "type": "PLAIN"},
            {"pos": ( 150.0, -220.0), "type": "PLAIN"},
            {"pos": (-110.0, -300.0), "type": "PLAIN"},
            {"pos": ( 110.0, -300.0), "type": "FLARED"},
        ],

        # Deviasi terukur saat verifikasi (clean-oval vs OSM deck-loop way 431617751).
        "VERIFY_MAX_DEVIATION_M": 1.0,   # OUTER 634x288 vs OSM 634x289
        "VERIFY_TOLERANCE_M": 5.0,       # lihat REFERENCE.FIDELITY (otoritatif)
        "VERIFY_METHOD": "clean-oval + silhouette gate; metric pada extent 950x80 "
                         "(OSM 978x88, dev 2.9%) + deck-loop 634x289; human sign-off.",
    },

    # =========================================================================
    # DETAIL (low-poly OK) — knob resolusi/ketebalan, boleh default
    # =========================================================================
    # Floor
    "FLOOR_OUTER_VERTS": 96, "VOID_VERTS": 96, "FLOOR_EDGE_FASCIA": 0.8,
    # Columns
    "COLUMN_SIZE": 1.2, "COLUMN_SPACING": 12.0, "COLUMN_RING_INSET": 2.0, "COLUMN_CHAMFER": 0.08,
    # Pillar wall cross-section (bentuk; panjang/posisi dari TRACE)
    "PILLAR_HEIGHT_TOTAL": 60.0, "PILLAR_WALL_VERTS": 24,
    "PILLAR_WALL_THICK_BASE": 4.0, "PILLAR_WALL_THICK_TOP": 2.5,
    "PILLAR_LONG_AXIS": "X",
    # Platform + basin
    "PLATFORM_OVAL_RATIO": 0.6, "PLATFORM_THICKNESS": 0.3, "PLATFORM_VERTS": 48,
    "PLATFORM_PARAPET_HEIGHT": 1.1, "PLATFORM_PARAPET_THICK": 0.4,
    "BASIN_RIM_HEIGHT": 0.9,
    # Connector
    "CONNECTOR": {"WIDTH": 6.0, "THICKNESS": 0.3, "PLATFORM_OVERLAP": 1.5,
                  "RING_OVERLAP": 2.0, "DIRECTIONS": ["EAST", "WEST"], "RAILING_HEIGHT": 1.1},
    # Towers
    "TOWER_RADIUS": 6.0, "TOWER_VERTS": 48, "TOWER_TOTAL_HEIGHT": 54.0,
    "TOWER_LOUVER_COUNT": 36, "TOWER_LOUVER_DEPTH": 0.25,
    "TOWER_FLARE_RADIUS": 11.0, "TOWER_FLARE_HEIGHT": 3.0,
    "HELIPAD_RADIUS": 10.0, "HELIPAD_THICK": 0.6,
    # Ramps
    "RAMP_HELIX_RADIUS_INNER": 10.0, "RAMP_HELIX_RADIUS_OUTER": 20.0,
    "RAMP_HELIX_LANE_COUNT": 4, "RAMP_HELIX_GRADIENT": 0.08, "RAMP_THICKNESS": 0.4,
    "RAMP_FAN_COUNT": 5, "RAMP_FAN_WIDTH": 8.0, "RAMP_FAN_SPREAD_DEG": 70.0,
    # Roof
    "MEMBRANE_THICK": 0.1, "MEMBRANE_GRID_U": 28, "MEMBRANE_GRID_V": 32,
    "MEMBRANE_PEAK_Z": 60.0,   # tinggi puncak relatif ground (detail; refine via trace front-view)
    "MEMBRANE_RIM_Z": 49.5,
    "OCULUS_RING_RADIUS": 5.0, "OCULUS_RING_TUBE": 0.4, "OCULUS_RING_SEG": 32,
    "OCULUS_TRUSS_SPOKES": 16,
    "MAST_PER_TENT": 8,        # tiang per tenda (6-10, koreksi user) — di keliling footprint
    "MAST_RADIUS": 0.6, "MAST_HEIGHT": 30.0, "MAST_RING_RADIUS": 22.0,
    "GUY_CABLE_RADIUS": 0.06, "GUY_CABLE_BEVEL_RES": 4,
    # Ground + furniture
    "GROUND_SUBDIVISIONS": 8, "GROUND_Z": 0.0, "PAVING_BAND_COUNT": 14, "LANE_LINE_WIDTH": 0.2,
    "LAMP_POLE_HEIGHT": 8.0, "LAMP_SPACING": 10.0, "FAN_POLE_HEIGHT": 4.0, "FAN_HEAD_RADIUS": 0.8,
    "SIGN_WIDTH": 2.0, "SIGN_HEIGHT": 0.8,
    "TENT_MINA_COUNT": 500, "TERRAIN_RING_RADIUS": 600.0,

    # =========================================================================
    # POLY BUDGET (hero mesh didorong mendekati cap)
    # =========================================================================
    "POLY_BUDGET": {
        "FLOOR_VIS": 16000, "FLOOR_COL": 800, "COLUMN_MASTER": 200,
        "RAMP_VIS": 18000, "RAMP_COL": 300, "RAMP_FAN_VIS": 12000, "RAMP_FAN_COL": 300,
        "PILLAR_VIS": 12000, "PILLAR_COL": 250, "PLATFORM_VIS": 6000, "PLATFORM_COL": 150,
        "CONNECTOR_VIS": 400, "CONNECTOR_COL": 60,
        "TOWER_VIS": 19000, "TOWER_FLARE_VIS": 8000, "HELIPAD_VIS": 3000,
        "MEMBRANE_VIS": 19000, "OCULUS_RING_VIS": 9000, "MAST_SET_VIS": 5000, "GUY_CABLE_VIS": 4000,
        "GROUND_VIS": 18000, "LAMP_MASTER": 600, "FAN_MASTER": 300, "SIGN_MASTER": 120, "TENT_MASTER": 120,
    },

    # =========================================================================
    # EXPORT + MATERIALS
    # =========================================================================
    "FBX_SCALE": 1.0, "FBX_AXIS_FORWARD": "-Z", "FBX_AXIS_UP": "Y",
    "FBX_APPLY_UNIT": True, "FBX_TRIANGULATE": True, "FBX_USE_MESH_MODIFIERS": True,
    "EXPORT_DIR": "./export_fbx/",
    # One FBX per group (AGENTS §11). group -> source collection names.
    "FBX_GROUPS": {
        "STRUCTURE": ["JMR_FLOORS", "JMR_COLUMNS", "JMR_COL_FLOORS", "JMR_COL_WALLS"],
        "RAMPS":     ["JMR_RAMPS", "JMR_COL_RAMPS"],
        "JAMARAT":   ["JMR_PILLARS", "JMR_COL_PILLARS"],
        "TOWERS":    ["JMR_TOWERS"],
        "ROOF":      ["JMR_ROOF"],
        "GROUND":    ["JMR_GROUND"],
        "FURNITURE": ["JMR_FURNITURE", "JMR_BACKGROUND"],
    },
    "MATERIALS": {"CONCRETE": "MAT_CONCRETE", "GRANITE": "MAT_GRANITE", "MEMBRANE": "MAT_MEMBRANE",
                  "PAVING_RED": "MAT_PAVING_RED", "PAVING_GREY": "MAT_PAVING_GREY",
                  "METAL_FRAME": "MAT_METAL_FRAME", "GLASS": "MAT_GLASS", "COLLISION_DBG": "MAT_COLLISION"},
}


# =============================================================================
# HELPERS
# =============================================================================
def get_floor_z(floor_num: int, surface: bool = True) -> float:
    return PARAMS["FLOOR_SURFACE_Z" if surface else "FLOOR_Z"][floor_num]

def _require_calibrated(field: str):
    if not CALIBRATED or PARAMS["TRACE"].get(field) is None:
        raise RuntimeError(
            f"[JMR] LAYOUT '{field}' belum dikalibrasi. Jalankan Fase R "
            f"(trace referensi -> isi PARAMS['TRACE'] -> set CALIBRATED=True) dulu. "
            f"Dilarang membangun geometri layout dari angka karangan.")

def get_pillars() -> dict:
    _require_calibrated("PILLARS"); return PARAMS["TRACE"]["PILLARS"]

def get_outline(which: str = "OUTER") -> list:
    key = "OUTLINE_OUTER" if which.upper() == "OUTER" else "OUTLINE_VOID"
    _require_calibrated(key); return PARAMS["TRACE"][key]

def get_towers() -> list:
    _require_calibrated("TOWERS"); return PARAMS["TRACE"]["TOWERS"]

def check_poly_budget(mesh_name: str, tri_count: int) -> bool:
    limit, warn = PARAMS["POLY_LIMIT_PER_MESH"], PARAMS["POLY_WARN_THRESHOLD"]
    if tri_count > limit:
        print(f"[JMR] FAIL: {mesh_name} = {tri_count} (limit {limit})"); return False
    tag = "WARN" if tri_count > warn else "OK"
    print(f"[JMR] {tag}: {mesh_name} = {tri_count}"); return True

def calibration_status() -> str:
    pending = [k for k in ("OUTLINE_OUTER","OUTLINE_VOID","PILLARS","ROAD_AXES",
               "RAMP_AXES","ROOF_MEMBRANES","TOWERS") if PARAMS["TRACE"][k] is None]
    return ("CALIBRATED" if CALIBRATED and not pending
            else f"AWAITING TRACE -> pending: {', '.join(pending) if pending else 'set CALIBRATED=True'}")


if __name__ == "__main__":
    r = PARAMS["REFERENCE"]
    print("=" * 60)
    print("PARAMETERS.py v3.0 — REAL SCALE")
    print("=" * 60)
    print(f"Sumber: Sketchfab UID {r['SKETCHFAB_UID']} | coords {r['REAL_COORDS']}")
    print(f"REAL: {r['REAL_LENGTH']}m x {r['REAL_WIDTH']}m, "
          f"{r['REAL_FLOOR_COUNT']} lantai @ {r['REAL_FLOOR_HEIGHT']}m")
    print(f"Floor Z (slab): {PARAMS['FLOOR_Z']}")
    print(f"Poly cap: {PARAMS['POLY_LIMIT_PER_MESH']} | warn {PARAMS['POLY_WARN_THRESHOLD']}")
    print(f"Kalibrasi: {calibration_status()}")
    try:
        get_pillars()
    except RuntimeError as e:
        print("Gate OK ->", str(e).split('. ')[0])
    print("=" * 60)
    print("PARAMETERS.py v3.0 loaded OK")


# Sketchfab UID ec0db00a3587489c9e2f18ebe5a289d3
