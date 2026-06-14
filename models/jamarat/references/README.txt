MODEL: Jamarat Bridge Complex (Mina) — see ../AGENTS.md for the filled reference
inventory (§A) and calibration record (§C). References are ALREADY POPULATED here,
migrated from the prior build.

Folder map (see ../AGENTS.md §R):
  aerial/    REAL ground truth — osm/ (OSM way 440922995 + traces/overlays) and the
             real aerial photo (Screenshot 2026-06-09 181836.png). LAYOUT source of truth.
  exterior/  perspective01-05,07,08.jpg — textured form/facade renders (fan model → hint).
  interior/  perspective06.jpg + penampakan…wustha…webp (REAL interior photo of a jamrah).
  detail/    signs02_uv.jpg — signage names (Ula/Wusta/Aqabah, floors, Escalator Bldg 1-11).
  section/   (empty — no cutaway available yet)
  models/    Tripo rough 3D model + ortho + wireframes + labeled massing screenshots —
             CROSS-CHECK only (fan-made hint, NOT ground truth).
  _legacy/   prior-build calibration record + traced data (PHASE_R_INVENTORY.md,
             PHASE_R_XY.md, BUILD_REPORT.md, PARAMETERS.py, trace_data.py,
             guide_roads.py, plan_renders/). Starting point — re-verify before reuse.
  _clarify/  (auto) ref-clarify outputs.

Authority: OSM + real photos > everything else. Open contradictions (tent count,
tower count) listed in ../AGENTS.md §C — resolve via ref-clarify before building.
