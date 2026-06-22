# generate_jamarat_textured.py — orchestrator for "Jamarat Bridge Complex" (TEXTURED).
# Same single-source geometry as generate_jamarat.py + the materials.py texture pass.
# Run: blender --background --factory-startup --python models/jamarat/generate_jamarat_textured.py
#
# Geometry is NOT duplicated here: this reuses generate_jamarat.build(textured=True),
# which calls materials.apply_all() (procedural for most, image maps for granite +
# membrane). See materials.py + memory/jamarat-texture-multi-version.md.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))      # ruh/
sys.path += [HERE, os.path.join(HERE, "components"), ROOT]

import generate_jamarat as base


if __name__ == "__main__":
    base.main(textured=True)
