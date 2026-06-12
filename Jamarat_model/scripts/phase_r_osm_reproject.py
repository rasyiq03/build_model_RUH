#!/usr/bin/env python3
# =============================================================================
# PHASE R — XY CALIBRATION : OSM -> local meters
# Reads References/osm/jamarat.osm (real georeferenced data, (c) OSM contributors,
# ODbL), reprojects node lat/lon to local meters (equirectangular, x*cos(lat)),
# PCA-aligns so the structure long axis = +Y (AGENTS: Y=length N-S, X=width E-W),
# origin at the bridge-footprint centroid. Extracts:
#   - bridge footprint (man_made=bridge ways)  -> OUTLINE_OUTER candidate
#   - highway ways (road / ramp centerlines)   -> ROAD_AXES / RAMP_AXES
#   - cross-checks extents vs published 950 x 80 m
# Writes: References/osm/local_meters.json + References/osm/osm_overlay.png
# This is CALIBRATION tooling, not a build script (no bpy). Pure stdlib+numpy+mpl.
# =============================================================================
import os, sys, json, math, xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OSM_PATH = os.path.join(ROOT, "References", "osm", "jamarat.osm")
OUT_JSON = os.path.join(ROOT, "References", "osm", "local_meters.json")
OUT_PNG  = os.path.join(ROOT, "References", "osm", "osm_overlay.png")
PUB_LEN, PUB_WID = 950.0, 80.0   # published meters (Y, X)

# ---------------------------------------------------------------- parse OSM ---
def parse_osm(path):
    tree = ET.parse(path)
    root = tree.getroot()
    nodes = {}
    for n in root.findall("node"):
        nodes[n.get("id")] = (float(n.get("lat")), float(n.get("lon")))
    ways = []
    for w in root.findall("way"):
        nd = [c.get("ref") for c in w.findall("nd")]
        tags = {t.get("k"): t.get("v") for t in w.findall("tag")}
        ways.append({"id": w.get("id"), "nodes": nd, "tags": tags})
    return nodes, ways

# ---------------------------------------------------- equirectangular -> m ----
def make_projector(lat0, lon0):
    # meters per degree at reference latitude (WGS84-ish, good to <0.1% over ~1km)
    m_lat = 111132.92 - 559.82*math.cos(2*math.radians(lat0)) \
            + 1.175*math.cos(4*math.radians(lat0))
    m_lon = 111412.84*math.cos(math.radians(lat0)) \
            - 93.5*math.cos(3*math.radians(lat0))
    def proj(lat, lon):
        return ((lon - lon0)*m_lon, (lat - lat0)*m_lat)  # (east_x, north_y)
    return proj, m_lat, m_lon

def main():
    if not os.path.exists(OSM_PATH):
        sys.exit(f"[PHASE_R] MISSING {OSM_PATH} — fetch OSM first.")
    nodes, ways = parse_osm(OSM_PATH)
    bridge_ways = [w for w in ways if w["tags"].get("man_made") == "bridge"]
    hw_ways     = [w for w in ways if "highway" in w["tags"]]
    print(f"[PHASE_R] nodes={len(nodes)} ways={len(ways)} "
          f"bridge_ways={len(bridge_ways)} highway_ways={len(hw_ways)}")
    if not bridge_ways:
        sys.exit("[PHASE_R] no man_made=bridge ways found.")

    # origin = centroid of all bridge-way node coords
    bnode_ids = {nid for w in bridge_ways for nid in w["nodes"]}
    blat = np.array([nodes[i][0] for i in bnode_ids if i in nodes])
    blon = np.array([nodes[i][1] for i in bnode_ids if i in nodes])
    lat0, lon0 = float(blat.mean()), float(blon.mean())
    proj, m_lat, m_lon = make_projector(lat0, lon0)
    print(f"[PHASE_R] origin lat0={lat0:.6f} lon0={lon0:.6f} "
          f"| m/deg lat={m_lat:.1f} lon={m_lon:.1f}")

    def way_xy(w):
        return np.array([proj(*nodes[i]) for i in w["nodes"] if i in nodes])

    # PCA over bridge points -> rotate so major axis = +Y
    bpts = np.array([proj(la, lo) for la, lo in zip(blat, blon)])
    bpts -= bpts.mean(axis=0)
    cov = np.cov(bpts.T)
    evals, evecs = np.linalg.eigh(cov)          # ascending
    major = evecs[:, np.argmax(evals)]          # long-axis direction
    ang = math.atan2(major[1], major[0])        # angle of major axis vs +x
    rot = ang - math.pi/2                        # rotate major axis onto +Y
    c, s = math.cos(-rot), math.sin(-rot)
    R = np.array([[c, -s], [s, c]])
    def aligned(p):                              # apply rotation about origin
        return (R @ np.asarray(p).T).T

    bpts_a = aligned(bpts)
    ext_y = float(bpts_a[:,1].max() - bpts_a[:,1].min())   # length
    ext_x = float(bpts_a[:,0].max() - bpts_a[:,0].min())   # width
    print(f"[PHASE_R] bridge extent (PCA-aligned): "
          f"length Y={ext_y:.1f} m  width X={ext_x:.1f} m")
    print(f"[PHASE_R] published: length={PUB_LEN} width={PUB_WID} | "
          f"dev L={abs(ext_y-PUB_LEN):.1f}m ({abs(ext_y-PUB_LEN)/PUB_LEN*100:.1f}%) "
          f"W={abs(ext_x-PUB_WID):.1f}m")

    # ---- collect aligned geometry (recenter on bridge mean, then rotate) ----
    bmean_xy = np.array([proj(la, lo) for la, lo in zip(blat, blon)]).mean(axis=0)
    def to_local(w):
        xy = way_xy(w)
        if len(xy) < 1:
            return None
        return aligned(xy - bmean_xy)

    bridge_local = [{"id": w["id"], "tags": w["tags"], "xy": to_local(w).tolist()}
                    for w in bridge_ways if to_local(w) is not None]
    hw_local = [{"id": w["id"], "tags": w["tags"], "xy": to_local(w).tolist()}
                for w in hw_ways if to_local(w) is not None]

    # jamarah XY: OSM rarely tags the walls. Search names; else mark None.
    jam = {}
    for w in ways:
        nm = (w["tags"].get("name", "") + w["tags"].get("name:en", "")).lower()
        for key, alias in (("ula", ("ula","sughra","small","صغرى")),
                           ("wusta", ("wusta","wusta","middle","وسطى")),
                           ("aqabah", ("aqabah","kubra","big","large","كبرى"))):
            if any(a in nm for a in alias):
                xy = to_local(w)
                if xy is not None:
                    jam[key] = xy.mean(axis=0).tolist()
    print(f"[PHASE_R] jamarah found in OSM by name: {list(jam.keys()) or 'NONE'}")

    # ---- write JSON ----
    data = {
        "attribution": "(c) OpenStreetMap contributors (ODbL)",
        "origin_latlon": [lat0, lon0],
        "rotation_rad_applied": rot,
        "m_per_deg": [m_lat, m_lon],
        "extent_aligned_m": {"length_Y": ext_y, "width_X": ext_x},
        "published_m": {"length_Y": PUB_LEN, "width_X": PUB_WID},
        "bridge_ways": bridge_local,
        "highway_ways": hw_local,
        "jamarah_named": jam,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[PHASE_R] wrote {OUT_JSON}")

    # ---- overlay PNG ----
    fig, ax = plt.subplots(figsize=(7, 12))
    for w in hw_local:
        xy = np.array(w["xy"]); ax.plot(xy[:,0], xy[:,1], color="0.7", lw=0.6, zorder=1)
    for w in bridge_local:
        xy = np.array(w["xy"]); ax.plot(xy[:,0], xy[:,1], color="C3", lw=1.2, zorder=3)
    for k, p in jam.items():
        ax.scatter(*p, c="C0", s=60, zorder=5); ax.annotate(k, p)
    ax.set_aspect("equal"); ax.set_title(
        f"Jamarat OSM -> local m (PCA aligned)\nL={ext_y:.0f}m W={ext_x:.0f}m  (c) OSM")
    ax.set_xlabel("X width (m)"); ax.set_ylabel("Y length (m)"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT_PNG, dpi=110)
    print(f"[PHASE_R] wrote {OUT_PNG}")

if __name__ == "__main__":
    main()
