---
name: blender-run
description: Run a Jamarat build script headless in Blender 5.0 and capture stdout.
---

# blender-run

Headless execution wrapper for the Jamarat pipeline. Blender is NOT on PATH;
use the absolute exe.

## Blender executable
```
C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

## Run a single script (clean scene)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background --factory-startup --python scripts/script_NN_xxx.py
```

## Chain from a saved state (.blend produced by a prior script)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background state/after_NN.blend --python scripts/script_MM_xxx.py
```

## Contract
- A script is DONE only when stdout shows zero Python traceback AND every
  `[JMR]` line is `OK`/`WARN` (never `FAIL`).
- Each script ends by printing `[JMR] SCRIPT NN DONE` and saving `state/after_NN.blend`.
- On a traceback: read it, fix the ROOT cause in the script, re-run. Never proceed past red.
- `--factory-startup` guarantees idempotent runs (no user prefs/addons leak in).

## Notes
- Scripts add the repo root to `sys.path` and `import PARAMETERS as P`.
- All meshes import the constants from `PARAMETERS.py` — no magic numbers in scripts.
