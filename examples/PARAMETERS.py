# examples/PARAMETERS.py
# Example parameters for the reference component (examples/comp_lamp_post.py).
# This is NOT a model — it only demonstrates the "no magic numbers" pattern.
# A real model keeps its own PARAMETERS.py under models/<model>/.
# Units: METRIC, 1 BU = 1 m, Z = up.

POLY_HARD_CAP        = 20000
POLY_WARN_THRESHOLD  = 19000

MATERIALS = {
    "CONCRETE": "MAT_CONCRETE",
    "GRANITE":  "MAT_GRANITE",
    "METAL":    "MAT_METAL_FRAME",
    "GLASS":    "MAT_GLASS",
    "BRASS":    "MAT_BRASS",
    "MARBLE":   "MAT_MARBLE",
}

# Y-branch lamp post (meters) — the reference component's parameters.
LAMP = {
    "TARGET_TRI":   2000,
    "BASE_RADIUS":  0.28,
    "BASE_HEIGHT":  0.35,
    "POLE_RADIUS":  0.10,
    "POLE_HEIGHT":  5.00,
    "ARM_LENGTH":   1.10,   # horizontal reach of each Y arm
    "ARM_RISE":     0.45,   # vertical rise over that reach
    "ARM_RADIUS":   0.06,
    "HEAD_RADIUS":  0.22,   # widest radius of the downward lamp head
    "HEAD_HEIGHT":  0.30,
    "SEGMENTS":     16,     # radial resolution for round parts
    "MATERIAL":     "METAL",
}
