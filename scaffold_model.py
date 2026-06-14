#!/usr/bin/env python3
# scaffold_model.py — generate a new models/<slug>/ from _TEMPLATE.
# This makes "adding a model" literally one command (master §10 step 1-2).
#
#   python scaffold_model.py kaaba "Kaaba & Masjid al-Haram"
#
# It copies the template AGENTS.md + PARAMETERS.py (substituting the obvious
# placeholders), creates components/ references/ exports/, and drops a starter
# orchestrator. You then fill the remaining {{...}} by reading references.
import sys, os, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "models", "_TEMPLATE")


def main():
    if len(sys.argv) < 2:
        print("usage: python scaffold_model.py <slug> [\"Display Name\"]")
        raise SystemExit(2)

    slug = sys.argv[1].strip().lower()
    name = sys.argv[2] if len(sys.argv) > 2 else slug.replace("_", " ").title()
    dest = os.path.join(ROOT, "models", slug)
    if os.path.exists(dest):
        print(f"[RUH] model '{slug}' already exists at {dest}")
        raise SystemExit(1)

    for sub in ("components", "exports"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    # references split by type (matches the Reference Folder Protocol)
    for sub in ("aerial", "exterior", "interior", "section", "detail", "models", "_clarify"):
        os.makedirs(os.path.join(dest, "references", sub), exist_ok=True)
    open(os.path.join(dest, "components", "__init__.py"), "w").close()

    today = datetime.date.today().isoformat()
    subs = {
        "{{MODEL_NAME}}": name,
        "{{MODEL_SLUG}}": slug,
        "{{DATE}}": today,
        "{{VERSION}}": "1.0",
    }

    def copy_filled(src_name, dst_name):
        with open(os.path.join(TEMPLATE, src_name), encoding="utf-8") as f:
            text = f.read()
        for k, v in subs.items():
            text = text.replace(k, v)
        with open(os.path.join(dest, dst_name), "w", encoding="utf-8") as f:
            f.write(text)

    copy_filled("AGENTS.md", "AGENTS.md")
    copy_filled("PARAMETERS.py", "PARAMETERS.py")

    # A Python module filename must not contain hyphens; the folder may.
    pyname = slug.replace("-", "_")

    # starter orchestrator (thin; you add components to REGISTRY as you build them)
    orch = f'''# generate_{pyname}.py — thin orchestrator for model "{name}".
# Run: blender --background --factory-startup --python models/{slug}/generate_{pyname}.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))      # ruh/
sys.path += [HERE, os.path.join(HERE, "components"), ROOT]

import PARAMETERS as P
import ruh_common as C

# from components import comp_<part>   # <- import each component here

REGISTRY = [
    # (label, build_fn, collection_name, tri_cap)
    # ("<part>", comp_<part>.build, comp_<part>.COLLECTION, comp_<part>.TRI_CAP),
]


def main():
    C.reset_scene()
    colls = {{name: C.reset_collection(name) for name in {{row[2] for row in REGISTRY}}}}
    results = []
    for label, build_fn, coll_name, cap in REGISTRY:
        obj = build_fn(colls[coll_name])
        results.append((label, *C.validate(obj, cap, warn=P.POLY_WARN_THRESHOLD)))
    print(f"\\n{{C.TAG}} ===== BUILD SUMMARY ({name}) =====")
    overall = "OK"
    for label, status, tris in results:
        print(f"{{C.TAG}} {{status:4}} {{label:24}} tri={{tris}}")
        if status == "FAIL":
            overall = "FAIL"
    print(f"{{C.TAG}} OVERALL: {{overall}}")
    if overall == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
'''
    with open(os.path.join(dest, f"generate_{pyname}.py"), "w", encoding="utf-8") as f:
        f.write(orch)

    print(f"[RUH] scaffolded models/{slug}/")
    print(f"[RUH] next: fill models/{slug}/AGENTS.md placeholders from references/,")
    print(f"[RUH]       then build components one by one (master §10).")


if __name__ == "__main__":
    main()
