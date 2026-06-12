import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jmr_util as U
import trace_data as T
U.reset_scene()
colls = U.build_collection_tree()
# ground silhouette (outer + courtyards)
g = U.polygon_slab("TEST_SIL", T.SIL_OUTER, T.SIL_HOLES, 0.0, 0.5, colls["GROUND"])
# deck body + courtyard holes + 3 oculus holes
holes = list(T.BODY_HOLES) + [T.OCULUS[k] for k in T.OCULUS]
d = U.polygon_slab("TEST_BODY", T.BODY_OUTER, holes, 12.0, 12.5, colls["FLOORS"])
U.validate_all([g, d], want_frozen=False)
