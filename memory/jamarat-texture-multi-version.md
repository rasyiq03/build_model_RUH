---
name: jamarat-texture-multi-version
description: User wants MULTIPLE texture versions of the jamarat model (stylized Material-enum + PBR), so components must include UV unwrap
metadata:
  type: project
---

For the jamarat model, the user wants **beberapa versi** (multiple texture versions), decided 2026-06-15: i.e. both a stylized **Roblox Material enum + Color** version AND a **PBR SurfaceAppearance** version produced from the same geometry.

**Why:** Texturing is NOT done in Blender — the build pipeline (Blender → FBX per collection → Roblox Studio) only assigns empty named material slots (PARAMETERS.MATERIALS: MAT_CONCRETE/GRANITE/MEMBRANE/...). Appearance is applied downstream in Roblox. Material-enum needs no UV; PBR needs UV unwrap + texture image maps.

**FINALIZED 2026-06-15 — two versions = two Blender SCRIPTS (no FBX committed; user exports FBX from Blender later):**
1. `generate_jamarat.py` — POLOS: geometry + empty named material slots (current behavior).
2. `generate_jamarat_textured.py` — TEXTURED: same geometry + full materials.

**Architecture (user-confirmed):** Single-source geometry, two thin orchestrators.
- `components/comp_*.py` = ONE shared set, called by a shared REGISTRY, IDENTICAL for both versions (no texture/UV code in components). NEVER duplicate geometry across the two scripts (anti-drift).
- **UV unwrap moved to the texture pass** (refined 2026-06-15), NOT in every component: only objects using image-textured materials (GRANITE, MEMBRANE) get a smart UV project inside `materials.py`. Procedural materials use Generated/Object coords (no UV). Keeps components single-source & lighter.
- `materials.py` = texturing module: builds Principled BSDF node trees per `PARAMETERS.MATERIALS` key. `generate_jamarat_textured.py` = build geometry + apply this pass.

**Texture source = CAMPURAN (user-confirmed):** PBR **procedural** (base color + roughness/metallic, no external image) for the majority; **image texture** files only for highlight elements = **granite jamrah walls (MAT_GRANITE)** + **membrane canopies (MAT_MEMBRANE)**. Image files for those two are a pending dependency (Polyhaven/authored) — until provided, stub the image-texture slot with a documented path + procedural fallback.
