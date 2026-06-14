# RUH — 3D model build foundation (Blender → FBX → Roblox)

This repo is the **foundation** for building the complex 3D models of **RUH**, a
playable Hajj & Umrah simulator. It does not contain a finished model yet — it
contains the rules, helpers, and tooling so that each model is built the same
disciplined, verifiable way.

## Run from here

Open Claude Code (and run all commands) from this folder (`ruh/`, the repo root).
That's where shared imports resolve and where the `ref-clarify` skill is found.

## What's here

```
AGENTS.md            Master rules — read this first. How EVERY model is built.
ruh_common.py        Shared bmesh helpers + the VALIDATOR (used by every component).
scaffold_model.py    Generate a new models/<model>/ skeleton from the template.
.claude/skills/
  ref-clarify/       Skill: when a reference image is unclear/contradictory, open it
                     for the user to annotate instead of guessing.
examples/
  comp_lamp_post.py  Reference component — the pattern every comp_*.py copies.
  PARAMETERS.py      Example params for that component.
models/
  _TEMPLATE/         The per-model spec template (AGENTS.md + PARAMETERS.py).
  <model>/           Each model is an independent directory (created by the scaffolder).
```

## Add a new model

```bash
python scaffold_model.py masjidil-haram "Masjidil Haram Complex"
```

This creates `models/masjidil-haram/` with `AGENTS.md`, `PARAMETERS.py`,
typed `references/` subfolders, `components/`, and a starter orchestrator. Then
fill the model's `AGENTS.md` (its shapes come from `references/` — see that
file's §R Reference Folder Protocol), and build components one by one.

## Build & verify a model

```bash
# whole model
blender --background --factory-startup --python models/<model>/generate_<model>.py
# one component in isolation
blender --background --factory-startup --python models/<model>/components/comp_<part>.py
```

Each component self-validates against the Roblox import rules (≤20k tris,
watertight, no n-gons, transforms frozen) and prints `[RUH] OK | WARN | FAIL`.
Red means stop and fix.

## Clarify an unclear reference

```bash
python .claude/skills/ref-clarify/scripts/ref_annotate.py \
    "models/<model>/references/aerial/top.jpg" \
    --question "What is unclear?" --out-dir models/<model>/references/_clarify
```

Opens the image in the browser; the user pins/draws/comments; Claude Code reads
the annotated image + notes back. (Pure Python stdlib — no install. Needs a
desktop where a browser can open.)

## Read next

- `AGENTS.md` — the master operating manual (universal rules).
- `models/_TEMPLATE/AGENTS.md` — the per-model spec template you fill per model.
