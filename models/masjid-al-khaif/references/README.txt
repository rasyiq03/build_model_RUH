MODEL: Masjid Al-Khaif — the large mosque in Mina, near the smallest Jamrah,
associated with the Prophet's prayer during Hajj. Big rectangular mosque with a
central green dome, four corner minarets, and wide arcaded prayer halls/courtyard.
TARGET STATE: current state. Layout-based (real footprint to trace from OSM).

Drop reference files here, sorted by type (see ../AGENTS.md §R) — empty for now:
  aerial/    top / satellite views (footprint, courtyard grid, minaret positions)
  exterior/  facades, minarets, central dome, gates, arcades
  interior/  prayer halls, columns, courtyard, mihrab
  section/   cutaways showing how levels / roof stack
  detail/    close-ups: dome, minaret cap, gate, arch, lamp
  models/    any rough 3D / OBJ — CROSS-CHECK only (hint, not ground truth)
  _clarify/  (auto) annotated images + notes + uploads from the ref-clarify skill

LAYOUT must come from real OSM data — never invented. Fetch the "Masjid al-Khayf"
way from OpenStreetMap, reproject to local meters, trace OUTLINE + minaret/dome/gate
positions into PARAMETERS.TRACE. Z/form from the image refs. Unclear/conflict → ref-clarify.
NOTE: sits in Mina near this project's Jamarat model — keep world scale consistent if
both are placed in one scene later.
