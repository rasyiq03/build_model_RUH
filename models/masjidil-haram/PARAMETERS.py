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

# --- TRACE (filled from Overpass OSM fetch 2026-06-22; meters, origin at Kaaba) ---
# Reprojection: x=(lon-39.82611)*103600, y=(lat-21.42250)*110574
# OUTLINE_OUTER: 9-point CW polygon derived from OSM relation 1472531 outer ways.
#   Simplified from 596-point full polygon; tolerance ±30 m.
#   Full polygon: references/aerial/osm/polygon_outer_raw.json
#   Extremes: N y=683 (lat 21.42868), S y=-193 (lat 21.42075),
#             W x=-611 (lon 39.82022), E x=174 (lon 39.82779).
TRACE = {
    "OUTLINE_OUTER": [    # outer boundary (CCW, local meters)
        # Dikalibrasi dari ref-clarify satelit annotation 2026-06-27.
        # Kalibrasi: Kaaba(518,551)=local(0,0), Marwa(603,311)=local(105.4,295.9), ~1.237 m/px
        # x=(px-518)*1.237,  y=(551-py)*1.237
        (-153.0,   11.0),  # SW entry    px(394,542)
        (-139.0,   53.0),  # SW-N        px(406,508)
        (-535.0,  204.0),  # W-lower     px(86,386)
        (-523.0,  240.0),  # W           px(95,357)
        (-575.0,  278.0),  # W-far       px(53,326)
        (-580.0,  286.0),  # W-peak      px(49,320)
        (-550.0,  349.0),  # W-upper     px(73,269)
        (-495.0,  422.0),  # WNW         px(118,210)
        (-414.0,  503.0),  # NW          px(183,144)
        (-325.0,  560.0),  # N-NW        px(255,98)
        (-199.0,  616.0),  # N-center    px(357,53)
        (-109.0,  642.0),  # NNE         px(430,32)
        (  -9.0,  654.0),  # NE-peak     px(511,22)
        (  -7.0,  658.0),  # N-top       px(512,19)  ← titik paling utara
        (  -5.0,  598.0),  # NE kink     px(514,68)
        (  45.0,  595.0),  # E-top       px(554,70)
        (  35.0,  329.0),  # E-upper     px(546,285)
        (  63.0,  328.0),  # Mas'a NW    px(569,286)
        (  67.0,  335.0),  # Mas'a N     px(572,280)
        ( 117.0,  339.0),  # Mas'a E-far px(613,277)
        ( 156.0,  -57.0),  # SE          px(644,597)
        ( 153.0,  -75.0),  # SE-S        px(642,612)
        ( 148.0,  -93.0),  # SE-S2       px(638,626)
        ( 127.0, -106.0),  # SE-corner   px(621,637)
        (  37.0, -158.0),  # S-E gate    px(548,679)
        ( -46.0, -140.0),  # S-center    px(481,664)
        (-113.0, -182.0),  # S-W         px(427,698)  ← titik paling selatan
        (-155.0, -171.0),  # SW-S        px(393,689)
        (-212.0,  -78.0),  # SW return   px(347,614)
        (-200.0,  -32.0),  # W-lower     px(356,577)
        (-142.0,    4.0),  # SW inner    px(403,548)
        (-150.0,   21.0),  # SW-entry    px(397,534)
    ],
    "MATAF_CENTER": (0.0, 0.0), # = Kaaba origin
    "MASA_AXIS": {
        "safa":     ( 137.0, -77.5),   # As-Safa peak  (OSM node, local m)
        "marwa":    ( 105.4, 295.9),   # Al-Marwa peak (OSM node, local m)
        "length_m": 374.9,             # straight-line Safa→Marwa (corridor ~450 m)
        "width_m":  40.0,
    },
    "GATES": {                  # {display_name: (x_m, y_m)} from OSM entrance nodes
        "King Abdul Aziz Gate 1": ( -28.0, -160.9),
        "King Fahd Gate 79":      (-213.8, -140.2),
        "Al-Fath Gate 30":        (  41.9,  167.6),
        "Bab Al-Marwah 25":       ( 132.3,  311.7),
        "Quraish Gate 28":        (  84.2,  325.5),
    },
    "FACILITIES": {             # {label: (x_m, y_m)} WC / wudhu / gathering
        "WC 6 (Men)":   (-315.2, -229.9),
        "WC 7 (Women)": (-343.2, -313.5),
        "WC 13 (Men)":  (-112.9,  405.3),
        "WC 14 (Women)":(   2.8,  422.5),
    },
    "MINARETS": [               # (x_m, y_m) — 13 menara total (Wikipedia/Arab News)
        # King Fahd expansion (1988-1993) — 7 menara + 2 Fahd gate = 9 pre-Abdullah
        # Pintu King Fahd / barat jauh — 2 menara mengapit gerbang
        (-198.9, -151.6),      # King Fahd Gate SW
        (-229.0, -128.0),      # King Fahd Gate NW
        # Pintu selatan / King Abdul Aziz — 2 menara
        (  -8.2, -158.0),      # Abdul Aziz Gate E
        ( -43.8, -150.7),      # Abdul Aziz Gate W
        # Sisi timur / tenggara — 1 menara
        ( 118.1,  -98.8),      # SE (dekat Mas'a)
        # Sudut SW ring utama — 1 menara
        ( -72.0, -100.0),      # SW ring
        # Sisi barat (Bab As-Salam / Umrah) — 2 menara
        (-148.2,   51.6),      # barat N
        (-155.7,   17.0),      # barat S
        # Sudut NW ring utama — 1 menara
        ( -57.0,  112.0),      # NW ring
        # Pintu utara (ring utama) — 2 menara
        (  22.1,  163.4),      # utara E
        (  56.4,  156.2),      # utara W
        # Bab Abdullah (ekspansi utara) — 2 menara mengapit outer edge section A (W) dan C (NE)
        # POSISI: ref-clarify masjdiilharam_satelit3 pin1/pin2 (2026-06-28)
        # Kalibrasi: Kaaba≈px(348,382), skala≈2.1 m/px, image 601×504.
        (-585.0,  323.0),      # menara ke-12, outer edge W (section A) — pin1 px(69,228)
        ( -10.0,  660.0),      # menara ke-13, outer edge NE (section C) — pin2 px(341,70)≈P9
    ],
}

# --- Material slot names ------------------------------------------------------
MATERIALS = {
    "MARBLE":   "MAT_MARBLE",
    "GRANITE":  "MAT_GRANITE",     # Kaaba body
    "KISWAH":   "MAT_KISWAH",      # black/gold cloth band
    "CONCRETE": "MAT_CONCRETE",
    "METAL":    "MAT_METAL_FRAME",
    "GLASS":    "MAT_GLASS",
    "GOLD":      "MAT_GOLD",        # door / mizab
    "GREEN":     "MAT_GREEN",      # Mas'a green-zone marker
    "DOME_ROOF": "MAT_DOME_ROOF",  # kubah terracotta/maroon (Mas'a pavilion, kios)
}

# =============================================================================
# COMPONENT PARAMETERS — one dict per components/comp_*.py.
# Dimensions are starting points; exact form comes from references/ (see AGENTS §R).
# Each dict MUST define TARGET_TRI (<= POLY_HARD_CAP).
# =============================================================================

KAABA = {
    "TARGET_TRI": 4000,
    # Dimensions verified against published sources (Saudipedia / Wikipedia, 2024):
    "WIDTH_X":   11.03,  # E-W (east-west) = 11.03 m
    "WIDTH_Y":   12.8,   # N-S (north-south) = 12.17-12.86 m; using 12.8 m
    "HEIGHT":    13.1,   # height = 13.1 m
    # Shadharwan: marble plinth base extending around Ka'bah walls
    "SHADHARWAN": {"OFFSET": 0.3, "H": 0.25},
    # Door: NE face (real) → disederhanakan ke +X (timur) dalam model.
    # Muka +X menghadap ke Maqam Ibrahim (timur). Offset ke -Y (selatan) = ujung kiri
    # saat menghadap pintu dari luar. Hajar Aswad di sudut SE (lebih ke selatan).
    # Bottom at 2.0 m above ground.
    "DOOR":      {"w": 1.9, "h": 3.1, "z_base": 2.0},
    "HIJR_RADIUS": 8.5,  # Hijr Ismail centreline radius dari pusat busur (0, hy) — lihat HIJR_ISMAIL dict
    "HIJR_H":      1.31, # Hijr Ismail wall height (m)
    "HIJR_T":      1.5,  # Hijr Ismail wall thickness (m)
    "MAQAM_DIST": 12.0,  # Maqam Ibrahim distance from Ka'bah center (door direction)
    # Kiswah hizam (gold calligraphy belt) — horizontal band on Ka'bah walls
    # Ref: wire_masjid010021 — band visible at ~65% body height
    "HIZAM_Z_FRAC": 0.65,   # fraction of HEIGHT where band centre sits
    "HIZAM_H":      0.55,   # vertical span of the gold band (m)
    "HIZAM_T":      0.025,  # protrusion thickness beyond wall face (m)
    # Roof border frame — raised rim around Ka'bah roof (makes centre look recessed)
    # Ref: masjidilharam010040, wire_masjid010021
    "ROOF_FRAME_W": 0.50,   # width of the raised border strip (m)
    "ROOF_FRAME_H": 0.10,   # how far the frame rises above body top face (m)
    # Hajar Aswad (Black Stone) — oval dome at the SE corner (+hx,-hy)
    # Ref: 010014_annotated "hajar aswad di sebelah kiri pintu" = selatan dari pintu
    # Shape: oval (taller than wide), shallow dome facing diagonally from corner
    "HAJAR_ASWAD_R_H":   0.20,  # horizontal radius of oval (m)
    "HAJAR_ASWAD_R_V":   0.26,  # vertical radius of oval — taller than wide (m)
    "HAJAR_ASWAD_DEPTH": 0.15,  # dome protrusion depth from corner (m)
    "HAJAR_ASWAD_Z":     1.50,  # height of dome centre above Ka'bah floor (m)
    # Door — offset toward south (-Y), NOT centred on east face
    # Ref: 010014_annotated — "di ujung kiri sedikit" (kiri = selatan dari luar muka +X)
    "DOOR_X_OFFSET": 1.50,      # offset ke selatan (-Y) dari tengah muka → ke arah sudut SE (m)
    "MATERIAL_BODY":  "GRANITE",
    "MATERIAL_CLOTH": "KISWAH",
}

MATAF = {
    "TARGET_TRI": 12000,
    "LEVELS": 1,         # 1 layer ground floor (alas/base slab only)
    "FLOOR_H": 6.0,      # same as STRUCTURE — levels align
    # r_outer = INNER_CLEAR + RING_WIDTH.  Real data (2026-06-24, web):
    #   latest Saudi expansion Mataf diameter ≈ 95.2 m → radius ≈ 47.6 m.
    #   Ottoman/1968 Mataf diameter ≈ 64.8 m → radius ≈ 32.4 m.
    #   Closest tawaf circuit ≈ 12 m from Ka'bah centre.
    # Sources: hajjumrahplanner.com/mataf, madainproject.com/mataf, thepilgrim.co/mataf
    "INNER_CLEAR":  9.0,   # nominal inner radius (only used to compute r_outer)
    "RING_WIDTH": 38.0,    # r_outer = 9+38 = 47 m ≈ latest Mataf radius (diameter ~95 m)
    "PARAPET_H": 1.1,
    "SLAB_T":      0.3,    # slab thickness
    "SEGS":        64,     # more segments for smoother circle at r=47 m
    # Prayer lines — 9 rings at 4 m spacing from r=12 m to r=44 m
    # Ref: masjidilharam010038 + real tawaf layout
    "PRAYER_RADII": [12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0, 44.0],  # metres from Ka'bah centre
    "PRAYER_W":     0.08,  # width of each prayer line slab (m)
    "PRAYER_H":     0.02,  # height above Mataf floor (m)
    "MATERIAL": "MARBLE",
}

MASA = {
    "TARGET_TRI": 14000,
    "LENGTH":  450.0,    # Safa -> Marwa
    "WIDTH":   40.0,
    "LEVELS":  3,        # 3 lantai
    "FLOOR_H": 8.0,      # 8 m floor-to-floor (3×8=24 m = STRUCTURE 4×6 m — tinggi sejajar)
    "MATERIAL": "MARBLE",
    "GREEN_MATERIAL": "GREEN",
}

STRUCTURE = {
    "TARGET_TRI": 18000,   # per emitted mesh
    "LEVELS":   4,         # 4 lantai utama — confirmed ref-clarify masjidilharam010032
    "FLOOR_H":  6.0,       # 6 m floor-to-floor (= ARCHES PIER_H)
    "SLAB_H":   0.5,       # tebal slab lantai (m) — permukaan jalan = lvl*FLOOR_H + SLAB_H
    # Outer wall irregular polygon — derived from ref-clarify annotation + 3-pin calibration
    # Scale: 0.1348 m/px, Kaaba at pixel (951,985), image 2122×2016.
    # Conversion: x_m=(px-951)*0.1348, y_m=(985-py)*0.1348
    # Source: masjidilharam010032__notes.json (2026-06-23)
    "OUTER_POLY": [
        ( -53.0,  104.0),  # NW
        (   7.0,  128.0),  # N  (r≈128 m)
        (  72.0,  108.0),  # NE
        (  84.0,   97.0),  # NE-E bevel
        ( 129.0,    2.0),  # E  (r≈129 m, Mas'a side)
        ( 109.0,  -70.0),  # SE
        (   2.0, -126.0),  # S  (r≈126 m)
        ( -68.0, -107.0),  # SW
        ( -83.0,  -75.0),  # W-lower (flat west wall)
        ( -77.0,   51.0),  # W-upper (r≈92 m — recessed west section)
    ],
    "PARAPET_H":      1.2,
    "ROOF_PARAPET_H": 1.5,
    "MATERIAL": "CONCRETE",
}

HIJR_ISMAIL = {
    "TARGET_TRI": 10000,
    # Arc wall — Ref: masjidilharam010043, 010045
    # Real: radius ~8.44 m dari pusat busur (= midpoint muka utara Ka'bah, BUKAN pusat Ka'bah).
    # Pusat busur = (0, Ka'bah_hy) = (0, 6.4). Diameter dalam = 2×(RADIUS-THICKNESS/2) ≈ 15.45 m.
    "RADIUS":    8.5,     # radius centreline dari pusat busur Hijr = (0, hy) (m)
    "HEIGHT":    1.31,    # tinggi dinding — real: 1.31 m (Wikipedia/Saudipedia) (m)
    "THICKNESS": 1.5,     # ketebalan dinding — real: 1.2–1.5 m; pakai 1.5 m (m)
    "N_SEGS":   16,       # segmen polygon busur — 16 for 180° arc = ~11° per panel
    # Gate frame di tiap ujung busur — Ref: masjidilharam010046
    "GATE_W":    1.80,    # lebar bersih bukaan gerbang (m)
    "GATE_PILLAR_W": 0.30,# lebar pilar gate (m)
    "GATE_ARCH_H":   0.35,# tinggi ekstra lengkungan dekoratif di atas gate (m)
    # Lamp post — Ref: masjidilharam010042, 010044
    "LAMP_COUNT": 4,      # jumlah lamp post sepanjang busur
    "MATERIAL":   "MARBLE",
    "GATE_MATERIAL":  "MARBLE",
    "LAMP_MATERIAL":  "METAL",
}

MAQAM_IBRAHIM = {
    "TARGET_TRI": 1500,
    # Cungkup Maqam Ibrahim — batu pijakan Nabi Ibrahim saat membangun Ka'bah.
    # Posisi: searah pintu Ka'bah (+X timur), ~15 m dari pusat Ka'bah (lebih renggang).
    # Dunia nyata: ~12–15 m dari Ka'bah centre, dalam area Mataf, tepat di depan pintu.
    # 010014_annotated: "maqam ibrahim sudah benar namun beri jarak sedikit lebih renggang"
    "POS_X": 15.0,   # 15 m ke timur — lebih renggang dari Ka'bah (naik dari 12 m) (m)
    "POS_Y": -1.5,   # sejajar offset pintu (-Y selatan) → tepat di depan pintu (m)
    # Geometri (dari refs + web: tinggi ±2.5 m, footprint ±1.3×1.3 m)
    "RADIUS":  0.65,  # radius badan oktagonal dari sumbu tengah (m)
    "HEIGHT":  2.50,  # tinggi total lantai → puncak, di atas z0 (m)
    "DOME_H":  0.40,  # tinggi kubah di atas badan lurus (m)
    "BASE_H":  0.20,  # tinggi plint marmer (m)
    "BASE_R":  0.85,  # radius plint (sedikit lebih lebar dari badan) (m)
    "N_SIDES": 8,     # penampang oktagonal
    "MATERIAL_BASE": "MARBLE",
    "MATERIAL_BODY": "GOLD",
}

COLUMNS = {
    "MASTER_TRI": 200,      # satu kolom ≤200 tri
    "TARGET_TRI": 12000,    # per mesh (inner ~49×96≈4700 + outer ~124×96≈11900 — objek terpisah)
    "RADIUS":  0.35,        # jari-jari shaft oktagonal (m)
    "BASE_R":  0.50,        # jari-jari base plinth & capital (m)
    "SPACING": 6.0,         # jarak pusat-ke-pusat kolom (m) — = ARCHES.SPAN
    "WALL_T":  1.2,         # ketebalan dinding luar — sama dgn STRUCTURE
    "COL_OFFSET": 1.5,      # jarak kolom luar dari inner face dinding (m)
    "MATERIAL": "MARBLE",
}

ARCHES = {
    "MASTER_TRI": 400,
    "TARGET_TRI": 12000,    # per mesh (inner ~49×64≈3136 + outer ~124×64≈7936 — objek terpisah)
    "SPAN": 6.0,            # jarak pusat-ke-pusat kolom (m)
    "Z_SPRING": 4.0,        # tinggi titik spring arch dari lantai (m)
    "Z_KEY":    5.7,        # tinggi keystone dari lantai (m)
    "DEPTH":    0.5,        # kedalaman arch ke dalam dinding (m)
    "N_SEG":    8,          # segmen per arch
    "MATERIAL": "MARBLE",
}

MINARETS = {
    "TARGET_TRI": 12000,   # per minaret
    "COUNT": 13,           # 13 menara — sesuai sig.jpg + konfigurasi nyata Masjidil Haram
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
    "MASTER_TRI": 200,      # satu tiang lampu ≤200 tri
    "TARGET_TRI": 8000,     # per level mesh (~50 tiang × ~96 tri)
    "POLE_H":     5.0,      # tinggi tiang lampu (m) — muat di bawah slab z=6m
    "POLE_R":     0.08,     # jari-jari tiang (m)
    "BASE_R":     0.20,     # jari-jari base plinth (m)
    "BASE_H":     0.25,     # tinggi base plinth (m)
    "HEAD_R":     0.30,     # jari-jari kepala lampu (m)
    "HEAD_H":     0.25,     # tinggi kepala lampu (m)
    "SPACING":   12.0,      # jarak antar tiang (m) — di sekeliling ring r=50 m
    "RING_R":    50.0,      # radius ring tiang lampu dari Kaaba (m)
    "MATERIAL":  "METAL",
}

DOMES = {
    "TARGET_TRI": 8000,     # per object (MAJOR dan MINOR masing-masing 1 objek)
    # z_base = STRUCTURE.LEVELS * STRUCTURE.FLOOR_H + 0.3 (roof slab) = 24.3 m
    # dihitung di comp_domes.py agar tidak duplikat konstanta
    #
    # Ground truth ref: masjidalharam_010019__notes.json (2026-06-26):
    #   "yang kecil ada 7 yang besar ada 1"  → 1 MAJOR + 7 MINOR = 8 total.
    #   "tidak ada, hanya ada kubah safa marwa" → sektor timur (Mas'a) kosong.
    #   Distribusi pin: 3 di selatan, 2 di barat, 3 di utara (arc S→W→N, ~180° CW).
    #   Kubah merah di connector building → bukan bagian ring, komponen terpisah.
    "MAJOR": {
        "COUNT":        1,        # tepat 1 kubah besar
        "RING_R":      72.0,      # posisi di tengah lebar ring (inner=47, outer≈83 m)
        "DRUM_R":       7.0,
        "DOME_R":       9.0,
        "DOME_H":      11.0,
        "DRUM_H":       3.5,
        "STEP_H":       0.5,
        "N_SIDES":     16,
        "N_LAT":       12,
        "THETA_START":  3.14159,  # π = arah barat (-X) — posisi kubah besar
        "ARC":          0.0,      # COUNT=1 → ARC tidak dipakai
    },
    "MINOR": {
        "COUNT":        7,        # tepat 7 kubah kecil
        "RING_R":      70.0,      # sedikit lebih dalam dari MAJOR
        "DRUM_R":       4.5,
        "DOME_R":       6.0,
        "DOME_H":       8.0,
        "DRUM_H":       2.5,
        "STEP_H":       0.4,
        "N_SIDES":     12,
        "N_LAT":       10,
        "THETA_START":  4.712,    # 3π/2 = arah selatan (-Y) — titik awal arc
        "ARC":         -3.14159,  # -π = 180° CW → selatan → barat → utara
    },
    "MATERIAL": "DOME_ROOF",
}

EXPANSION_WINGS = {
    "TARGET_TRI": 8000,
    # Ref aerial 010001, 010002, 010004 — sayap multi-lantai antara ring dan batas luar.
    # Outer boundary = TRACE.OUTLINE_OUTER (32 titik, CCW dari satelit).
    # Inner boundary = projected dari STRUCTURE.OUTER_POLY via ray dari origin.
    # Sisi timur (Mas'a) DIKECUALIKAN — sudah dibangun oleh comp_masaa.
    # Tinggi = LEVELS × STRUCTURE.FLOOR_H = 4 × 6 = 24 m (sejajar seluruh lantai ring).
    "LEVELS":          4,   # match STRUCTURE.LEVELS — ring dan wings setinggi
    "PARAPET_H":       1.2,
    "ROOF_PARAPET_H":  1.5,
    "MATERIAL": "CONCRETE",
}

MASAA_CONNECTOR = {
    "TARGET_TRI": 3000,
    # Ref: masjidilharam010049 — box multi-level + dome kecil di atap + kiosk bawah.
    # Ref: masjidalharam_010019__notes.json — kubah merah di connector, terpisah dari ring.
    # Tinggi = 3 × MASA.FLOOR_H (8 m) = 24 m — sejajar lantai Mas'a.
    "WIDTH_EW":  25.0,
    "DEPTH_NS":  20.0,
    "HEIGHT":    24.0,
    "SLAB_T":     0.3,
    "DOME": {
        "DRUM_R":  3.5,
        "DOME_R":  5.0,
        "DOME_H":  5.5,
        "DRUM_H":  2.0,
        "STEP_H":  0.4,
        "N_SIDES": 12,
        "N_LAT":   8,
    },
    "KIOSK_W":         8.0,
    "KIOSK_D":         6.0,
    "KIOSK_H":         3.5,
    "KIOSK_OFFSET_EW": -12.0,
    "KIOSK_OFFSET_NS":  -8.0,
    "SOUTH_CX": 123.0,
    "SOUTH_CY": -74.0,
    "NORTH_CX": 106.0,
    "NORTH_CY": 279.0,
    "MATERIAL":       "CONCRETE",
    "DOME_MATERIAL":  "DOME_ROOF",
}

ABDULLAH_EXPANSION = {
    "TARGET_TRI": 18000,
    # Perluasan Raja Abdullah / Ekspansi Saudi Ketiga, 2011-2015.
    # SUMBER TERVERIFIKASI:
    #   - Saudipedia.com: 6 lantai sholat, 2 menara baru (menara ke-10 & 11)
    #   - Wikipedia/Arab News: area tanah ~300.000 m², kapasitas 300.000 jemaah
    #   - SPA.gov.sa: lokasi sisi UTARA (Shamiya) kompleks
    # KOORDINAT POLY_OUTER: DIUKUR dari gambar satelit Google Maps (masjidilharam_satelit.png)
    #   via ref-clarify annotation (2026-06-27).
    #   Kalibrasi: Pin1=Kaaba(518,551)=local(0,0), Pin2=Marwa(603,311)=local(105.4,295.9)
    #   Skala = 1.237 m/px.  Formula: x=(px-518)*1.237, y=(551-py)*1.237
    #   Batas selatan di-trim ke y=140m (tepat di luar OUTER_POLY E-ring utara y≈128m).
    "FLOOR_H":       6.0,    # lantai ke lantai (m)
    "LEVELS":        2,      # lantai TAMBAHAN di atas expansion_wings (4 base + 2 = 6 total) — Saudipedia: 6 lantai sholat
    "SLAB_T":        0.4,
    "PARAPET_H":     1.2,
    "ROOF_PARAPET_H": 1.5,
    "CORR_W":       20.0,    # lebar saluran/koridor antar 3 sayap (m) — gap di P4 dan P8
    # CCW polygon, local meters.  Dari ref-clarify satelit annotation 2026-06-27 (sesi ke-2).
    # Hanya bagian UTARA kompleks (Abdullah expansion area).
    # Inner boundary (sisi yg menyentuh E-ring) dihitung via ray projection ke OUTER_POLY.
    "POLY_OUTER": [
        (-535.0,  204.0),  # P0  SW       px(86,386)
        (-575.0,  278.0),  # P1  W-far    px(53,326)   ← paling barat
        (-550.0,  349.0),  # P2  W-mid    px(73,269)
        (-495.0,  422.0),  # P3  WNW      px(118,210)
        (-414.0,  503.0),  # P4  NW       px(183,144)
        (-325.0,  560.0),  # P5  N-NW     px(255,98)
        (-199.0,  616.0),  # P6  N-center px(357,53)
        (-109.0,  642.0),  # P7  NNE      px(430,32)
        (  -9.0,  654.0),  # P8  NE       px(511,22)
        (  -7.0,  658.0),  # P9  N-top    px(512,19)   ← titik paling utara
        (  -5.0,  598.0),  # P10 NE kink  px(514,68)
        (  45.0,  595.0),  # P11 E-top    px(554,70)
        (  35.0,  329.0),  # P12 E-lower  px(546,285)  ← batas dengan Mas'a
    ],
    # Bab Abdullah minarets (ke-12 & ke-13 dari total 13) — flanking Bab Abdullah di NW
    # Sumber: "two minarets, bringing total to 11" (2011 announce) + 2 King Salman = 13 total
    # POSISI perlu ref-clarify — estimasi dari P4 POLY_OUTER area (~NW corner -414,503)
    "MINARETS": [
        {"cx": -585.0, "cy": 323.0},   # menara ke-12, outer W edge section A — ref-clarify satelit3 pin1 (2026-06-28)
        {"cx":  -10.0, "cy": 660.0},   # menara ke-13, outer NE edge section C — ref-clarify satelit3 pin2 (2026-06-28)
    ],
    "MINARET_H":        135.0,    # CONFIRMED: SPA.gov.sa / Saudipedia — Bab Abdullah minarets = 135 m (bukan 89 m; 89 m = King Fahd Gate)
    "MINARET_R_BASE":     3.5,
    "MINARET_R_TOP":      2.2,
    "MINARET_CAP_H":     12.0,
    "MINARET_N":          12,
    "MATERIAL":          "CONCRETE",
    "MINARET_MATERIAL":  "MARBLE",
}
