textures/ — image maps for the TEXTURED version only (generate_jamarat_textured.py).

Texture source for this model = CAMPURAN (user-confirmed 2026-06-15):
  - Most materials are PROCEDURAL (no image file needed) — built in code by materials.py.
  - Only the HIGHLIGHT elements use image maps. Drop the files here:

      granite_basecolor.jpg   granite_roughness.jpg   granite_normal.jpg     <- MAT_GRANITE (jamrah walls)
      membrane_basecolor.jpg  membrane_roughness.jpg  membrane_normal.jpg    <- MAT_MEMBRANE (PTFE canopies)

  Filenames are read from materials.py -> TEX_FILES. basecolor is required to
  trigger the image path; roughness/normal are optional (omit -> not connected).

If a file is missing, materials.py falls back to a PROCEDURAL look automatically
and prints a [RUH] note — the textured build still runs, just without that photo map.

Suggested sources: Polyhaven (CC0) granite/concrete, or author your own. Keep them
seamless/tileable. The POLOS version (generate_jamarat.py) ignores this folder.
