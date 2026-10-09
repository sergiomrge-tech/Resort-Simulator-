#!/usr/bin/env python3
"""Build a deterministic, GIS-guarded vegetation pilot from the frozen OSM snapshot.

No positions are synthesized: every exported instance is an OSM natural=tree node.
The small WGS84/UTM implementation below mirrors R5's EPSG:32723 + 46 degree
source-frame transform, avoiding a runtime GIS package dependency for this tool.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
FRAME_PATH = ROOT / "geo/procedural/R4_SOURCE_FRAME.json"
OSM_PATH = ROOT / "geo/data/copacabana.osm.gz"
DEFAULT_OUTPUT = ROOT / "geo/procedural/R6_VEGETATION_INSTANCES.json"
EARTH_A = 6378137.0
EARTH_E2 = 0.0066943799901413165
K0 = 0.9996


def utm23s(lon: float, lat: float) -> tuple[float, float]:
    """WGS84 longitude/latitude to EPSG:32723 (Transverse Mercator)."""
    phi, lam = math.radians(lat), math.radians(lon)
    lam0 = math.radians(-45.0)
    ep2 = EARTH_E2 / (1.0 - EARTH_E2)
    n = EARTH_A / math.sqrt(1.0 - EARTH_E2 * math.sin(phi) ** 2)
    t = math.tan(phi) ** 2
    c = ep2 * math.cos(phi) ** 2
    a = math.cos(phi) * (lam - lam0)
    e4, e6 = EARTH_E2**2, EARTH_E2**3
    m = EARTH_A * ((1 - EARTH_E2/4 - 3*e4/64 - 5*e6/256) * phi
        - (3*EARTH_E2/8 + 3*e4/32 + 45*e6/1024) * math.sin(2*phi)
        + (15*e4/256 + 45*e6/1024) * math.sin(4*phi)
        - (35*e6/3072) * math.sin(6*phi))
    east = 500000 + K0*n*(a + (1-t+c)*a**3/6 + (5-18*t+t*t+72*c-58*ep2)*a**5/120)
    north = K0*(m+n*math.tan(phi)*(a*a/2 + (5-t+9*c+4*c*c)*a**4/24
        + (61-58*t+t*t+600*c-330*ep2)*a**6/720)) - 10000000
    return east, north


class Frame:
    def __init__(self, config: dict):
        self.config = config
        self.angle = math.radians(float(config["axis_angle_degrees_counterclockwise_from_east"]))
        self.c, self.s = math.cos(self.angle), math.sin(self.angle)
        ref_lon, ref_lat = config["avenue_reference_lonlat"]
        ax, ay = utm23s(float(ref_lon), float(ref_lat))
        shift = float(config["center_shift_inland_m"])
        self.cx, self.cy = ax - self.s * shift, ay + self.c * shift
        self.length = float(config["along_coast_length_m"])
        self.width = float(config["inland_width_m"])

    def local(self, lon: float, lat: float) -> tuple[float, float]:
        east, north = utm23s(lon, lat)
        dx, dy = east - self.cx, north - self.cy
        return dx*self.c + dy*self.s, -dx*self.s + dy*self.c

    def in_roi(self, p: tuple[float, float], margin: float = 0) -> bool:
        x, y = p
        return (-self.length/2 + margin <= x <= self.length/2 - margin
                and -self.width/2 + margin <= y <= self.width/2 - margin)


def point_segment_distance(p, a, b) -> float:
    dx, dy = b[0]-a[0], b[1]-a[1]
    denom = dx*dx + dy*dy
    if denom == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/denom))
    return math.hypot(p[0] - (a[0]+t*dx), p[1] - (a[1]+t*dy))


def point_in_polygon(p, ring) -> bool:
    inside = False
    x, y = p
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i+1) % len(ring)]
        if ((y1 > y) != (y2 > y)) and x < (x2-x1)*(y-y1)/(y2-y1) + x1:
            inside = not inside
    return inside


def distance_to_lines(p, lines) -> float:
    return min((point_segment_distance(p, a, b) for line in lines
                for a, b in zip(line, line[1:])), default=float("inf"))


DEFAULT_ROAD_WIDTH_M = {
    "motorway": 14.0, "trunk": 13.0, "primary": 11.0, "secondary": 9.0,
    "tertiary": 7.5, "unclassified": 6.0, "residential": 6.0,
    "living_street": 4.5, "service": 4.5, "pedestrian": 3.0,
    "cycleway": 2.0, "footway": 1.8, "path": 1.8, "steps": 1.6,
    "corridor": 1.6,
}


def road_clearance(tags: dict, outside_edge_m: float) -> float:
    """Centerline setback from tagged width or conservative highway class."""
    try:
        width_text = str(tags.get("width") or "")
        width = float(width_text.lower().replace("meters", "").replace("meter", "").replace("m", "").strip())
        if width <= 0:
            raise ValueError
    except (TypeError, ValueError):
        width = DEFAULT_ROAD_WIDTH_M.get(tags.get("highway", ""), 4.0)
    return width/2 + outside_edge_m


def road_guard(p, roads):
    nearest_distance, nearest_required = float("inf"), 0.0
    minimum_margin = float("inf")
    for line, required in roads:
        distance = distance_to_lines(p, [line])
        minimum_margin = min(minimum_margin, distance-required)
        if distance < nearest_distance:
            nearest_distance, nearest_required = distance, required
    return nearest_distance, nearest_required, minimum_margin


def distance_to_polygons(p, polygons) -> float:
    if any(point_in_polygon(p, ring) for ring in polygons):
        return 0.0
    return min((point_segment_distance(p, a, b) for ring in polygons
                for a, b in zip(ring, ring[1:])), default=float("inf"))


def _tagmap(element):
    return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}


def read_osm(frame: Frame, path: Path, road_edge_margin_m: float):
    with gzip.open(path, "rb") as stream:
        root = ET.parse(stream).getroot()
    if root.tag != "osm":
        raise ValueError("Fonte não é XML OSM")
    node_elements = root.findall("node")
    nodes = {n.get("id"): (float(n.get("lon")), float(n.get("lat")))
             for n in node_elements if n.get("id") and n.get("lon") and n.get("lat")}
    local_nodes = {key: frame.local(*ll) for key, ll in nodes.items()}
    roads, buildings, green_areas, forbidden_areas, coast = [], [], [], [], []
    road_tags = Counter()
    for way in root.findall("way"):
        tags = _tagmap(way)
        refs = [nd.get("ref") for nd in way.findall("nd")]
        if len(refs) < 2 or any(ref not in local_nodes for ref in refs):
            continue
        coords = [local_nodes[r] for r in refs]
        closed = len(coords) >= 4 and coords[0] == coords[-1]
        if tags.get("highway"):
            roads.append((coords, road_clearance(tags, road_edge_margin_m)))
            road_tags[tags["highway"]] += 1
        if tags.get("natural") == "coastline":
            coast.append(coords)
        if tags.get("building") not in (None, "no") and closed:
            buildings.append(coords)
        if closed:
            land_values = " ".join(tags.get(k, "") for k in
                ("leisure", "landuse", "natural", "amenity", "tourism")).lower()
            if any(word in land_values for word in ("park", "garden", "grass", "forest", "wood", "scrub", "recreation_ground")):
                green_areas.append(coords)
            if any(word in land_values for word in ("beach", "sand", "water", "wetland", "sea", "basin", "reservoir")):
                forbidden_areas.append(coords)
    trees = []
    for node in node_elements:
        tags = _tagmap(node)
        if tags.get("natural") == "tree" and node.get("id") in local_nodes:
            lon, lat = nodes[node.get("id")]
            trees.append({"id": node.get("id"), "lon": lon, "lat": lat,
                          "local": local_nodes[node.get("id")], "tags": tags})
    return trees, roads, buildings, green_areas, forbidden_areas, coast, road_tags


def seed_for(osm_id: str) -> int:
    return int.from_bytes(hashlib.sha256(("R6|OSM|"+osm_id).encode()).digest()[:4], "big")


def species_for(tags: dict, seed: int) -> str:
    clues = " ".join(tags.get(k, "") for k in ("species", "genus", "taxon", "name")).lower()
    if any(word in clues for word in ("palm", "palmeira", "arecaceae", "cocos", "roystonea", "syagrus", "phoenix")):
        return "palmeira_copacabana"
    return ("arvore_tropical_ampla", "arvore_tropical_densa")[seed % 2]


def category_for(p, green, roads) -> str:
    if distance_to_polygons(p, green) <= 1.0:
        return "canteiro_ou_area_verde_osm"
    if distance_to_lines(p, roads) <= 4.0:
        return "arvore_de_rua_osm"
    return "arvore_em_calcada_ou_lote_osm"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-count", type=int, default=48)
    parser.add_argument("--min-spacing-m", type=float, default=3.0)
    parser.add_argument("--road-edge-margin-m", type=float, default=0.75,
                        help="extra space outside OSM road width/class around the centerline")
    parser.add_argument("--building-clearance-m", type=float, default=1.5)
    parser.add_argument("--coastline-clearance-m", type=float, default=8.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if args.pilot_count < 1 or min(args.min_spacing_m, args.road_edge_margin_m,
            args.building_clearance_m, args.coastline_clearance_m) < 0:
        parser.error("contagem deve ser positiva e distâncias não negativas")
    config = json.loads(FRAME_PATH.read_text(encoding="utf-8"))
    frame = Frame(config)
    trees, roads, buildings, green, forbidden, coast, road_tags = read_osm(frame, OSM_PATH, args.road_edge_margin_m)
    rejection = Counter()
    valid = []
    for tree in trees:
        p = tree["local"]
        if not frame.in_roi(p):
            rejection["fora_do_roi"] += 1; continue
        if any(point_in_polygon(p, ring) for ring in forbidden):
            rejection["dentro_de_areia_agua_ou_area_incompativel_osm"] += 1; continue
        road_dist, road_required, road_margin = road_guard(p, roads)
        if road_margin < 0:
            rejection["muito_proximo_ao_eixo_viario"] += 1; continue
        building_dist = distance_to_polygons(p, buildings)
        if building_dist < args.building_clearance_m:
            rejection["dentro_ou_junto_a_edificacao"] += 1; continue
        coast_dist = distance_to_lines(p, coast)
        if coast and coast_dist < args.coastline_clearance_m:
            rejection["muito_proximo_a_linha_de_costa"] += 1; continue
        valid.append({**tree, "road_distance_m": road_dist,
                      "road_required_m": road_required, "road_margin_m": road_margin,
                      "building_distance_m": building_dist,
                      "coastline_distance_m": coast_dist})
    valid.sort(key=lambda t: int(t["id"]))
    selected = []
    # Deterministic farthest-point sampling spreads the small pilot across the ROI.
    if valid:
        selected.append(valid[0])
        remaining = valid[1:]
        while remaining and len(selected) < args.pilot_count:
            best = max(remaining, key=lambda t: (min(math.dist(t["local"], s["local"]) for s in selected), -int(t["id"])))
            remaining.remove(best)
            nearest = min(math.dist(best["local"], s["local"]) for s in selected)
            if nearest < args.min_spacing_m:
                rejection["duplicada_ou_densidade_minima"] += 1
                continue
            selected.append(best)
    instances = []
    for tree in selected:
        seed = seed_for(tree["id"])
        species = species_for(tree["tags"], seed)
        x, y = tree["local"]
        instances.append({
            "osm_id": "node/" + tree["id"], "osm_tags": tree["tags"],
            "type": species, "category": category_for(tree["local"], green, [line for line, _ in roads]),
            "coordinates": {"geographic_wgs84_lon_lat": [round(tree["lon"], 8), round(tree["lat"], 8)],
                            "local_m_xy": [round(x, 3), round(y, 3)]},
            "orientation": {"yaw_degrees": round((seed / 2**32) * 360.0, 3)},
            "seed": seed, "origin": "OpenStreetMap natural=tree point; ODbL 1.0",
            "guards": {"road_centerline_distance_m": round(tree["road_distance_m"], 2),
                       "road_clearance_required_m": round(tree["road_required_m"], 2),
                       "minimum_road_clearance_margin_m": round(tree["road_margin_m"], 2),
                       "building_edge_distance_m": round(tree["building_distance_m"], 2),
                       "coastline_distance_m": None if math.isinf(tree["coastline_distance_m"]) else round(tree["coastline_distance_m"], 2)},
            "asset_lod_collection": species
        })
    payload = {
        "schema": "resort.vegetation.instances.v1",
        "status": "R6_OSM_GUARDED_PILOT",
        "source": {"file": "geo/data/copacabana.osm.gz",
                   "sha256": hashlib.sha256(OSM_PATH.read_bytes()).hexdigest(),
                   "frame_file": "geo/procedural/R4_SOURCE_FRAME.json",
                   "frame_sha256": hashlib.sha256(FRAME_PATH.read_bytes()).hexdigest(),
                   "crs": config["crs"], "axis_angle_degrees_counterclockwise_from_east": config["axis_angle_degrees_counterclockwise_from_east"],
                   "area_m2": config["game_area_m2"], "attribution": "© OpenStreetMap contributors — ODbL 1.0"},
        "settings": {"pilot_cap": args.pilot_count, "min_spacing_m": args.min_spacing_m,
                     "road_edge_margin_m": args.road_edge_margin_m,
                     "road_width_source": "OSM width tag; otherwise conservative highway class estimate",
                     "building_clearance_m": args.building_clearance_m,
                     "coastline_clearance_m": args.coastline_clearance_m,
                     "selection": "stable-id seed then deterministic farthest-point sampling"},
        "counts": {"osm_tree_nodes_in_snapshot": len(trees), "valid_after_gis_guards": len(valid),
                   "pilot_instances": len(instances), "rejected": dict(sorted(rejection.items())),
                   "categories": dict(sorted(Counter(i["category"] for i in instances).items())),
                   "species": dict(sorted(Counter(i["type"] for i in instances).items())),
                   "road_way_types": dict(sorted(road_tags.items()))},
        "limitations": ["OSM points describe mapped trees, not surveyed trunk footprints or species unless tagged.",
            "Road centerline exclusion uses OSM width when available, otherwise conservative road-class width estimates plus the configured outside-edge margin; curb lines, sidewalk polygons, utility lines, and tree pits were not provided.",
            "Building clearance uses available closed OSM building ways only; relation footprints and missing/incomplete ways are not reconstructed.",
            "Beach/water exclusions use tagged OSM polygons; the snapshot does not provide complete sand/water coverage or DEM elevations.",
            "Unspecified broadleaf species and yaw are visual kit assignments from stable per-node seeds, not botanical identification or measured trunk orientation.",
            "Pilot records are not yet attached to Unity or the original BlenderGIS/FBX geometry."],
        "instances": instances
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), **payload["counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
