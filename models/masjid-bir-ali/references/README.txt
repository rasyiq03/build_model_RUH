MODEL: Masjid Bir Ali (Masjid Dhul Hulaifah) — the miqat mosque for pilgrims
coming from Medina, ~9 km SW of the Prophet's Mosque. Large walled mosque with
a tall minaret, arcaded courtyards, ablution blocks and ihram-changing rooms.
TARGET STATE: current state. Layout-based (real footprint to trace from OSM).

Drop reference files here, sorted by type (see ../AGENTS.md §R) — empty for now:
  aerial/    top / satellite views (footprint, courtyard layout, minaret position)
  exterior/  facades, minaret, gates, domes, perimeter wall
  interior/  prayer hall, courtyards, columns, ablution area
  section/   cutaways showing how levels / roof stack
  detail/    close-ups: minaret cap, gate, arch, mihrab, lamp
  models/    any rough 3D / OBJ — CROSS-CHECK only (hint, not ground truth)
  _clarify/  (auto) annotated images + notes + uploads from the ref-clarify skill

LAYOUT (footprint, axes, positions) must come from real OSM data — never invented.
Suggested origin: mosque footprint centroid. Fetch the "Masjid Dhul Hulaifah /
Bir Ali" way from OpenStreetMap, reproject to local meters, then trace OUTLINE +
minaret/gate positions into PARAMETERS.TRACE. Z/form comes from the image refs.
When references are unclear or conflict (era/expansion), use ref-clarify — do not guess.
