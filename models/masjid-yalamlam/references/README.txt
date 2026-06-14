MODEL: Masjid Yalamlam (As-Sa'diyah) — the miqat mosque for pilgrims coming from
the Yemen direction, ~100 km SSE of Mecca. Modern mosque with minaret(s),
courtyard, and service blocks (smaller / simpler than Bir Ali).
TARGET STATE: current state. Layout-based (real footprint to trace from OSM).

Drop reference files here, sorted by type (see ../AGENTS.md §R) — empty for now:
  aerial/    top / satellite views (footprint, courtyard layout, minaret position)
  exterior/  facades, minaret(s), gates, domes, perimeter wall
  interior/  prayer hall, courtyard, columns, ablution area
  section/   cutaways showing how levels / roof stack
  detail/    close-ups: minaret cap, gate, arch, mihrab, lamp
  models/    any rough 3D / OBJ — CROSS-CHECK only (hint, not ground truth)
  _clarify/  (auto) annotated images + notes + uploads from the ref-clarify skill

LAYOUT must come from real OSM data — never invented. Fetch the Yalamlam miqat
mosque way from OpenStreetMap, reproject to local meters, trace OUTLINE + positions
into PARAMETERS.TRACE. Z/form from the image refs. Unclear/conflict → ref-clarify.
NOTE: confirm the exact mosque (Yalamlam / As-Sa'diyah) with the user before tracing.
