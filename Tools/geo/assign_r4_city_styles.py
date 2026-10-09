"""Plan 50 *visual* facade grammars across frozen Copacabana OSM ways.

Offline, deterministic, source-preserving. This stage emits style assignments
only. It does NOT produce geometry, alter GIS meshes, claim true heights,
infer business permits or replace authored hero architecture.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import re
import xml.etree.ElementTree as ET
from pyproj import Transformer
from shapely.geometry import Polygon, box

ROOT = Path(__file__).resolve().parents[2]
OSM = ROOT / "geo/data/copacabana.osm.gz"
CATALOG = ROOT / "ArtSource/ProceduralBuildings/Resort50Styles.json"
OUTPUT = ROOT / "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
REPORT = ROOT / "geo/data/report.json"
FRAME = ROOT / "geo/procedural/R4_SOURCE_FRAME.json"

def frame_transform():
    frame = json.loads(FRAME.read_text(encoding="utf-8"))
    assert frame["game_area_m2"] == 2_000_000
    tf = Transformer.from_crs("EPSG:4326", frame["crs"], always_xy=True)
    east, north = tf.transform(*frame["avenue_reference_lonlat"])
    angle = math.radians(frame["axis_angle_degrees_counterclockwise_from_east"])
    co, si = math.cos(angle), math.sin(angle)
    delta = frame["center_shift_inland_m"]
    cx, cy = east - si * delta, north + co * delta
    length, width = frame["along_coast_length_m"], frame["inland_width_m"]
    region = box(-length/2, -width/2, length/2, width/2)
    def to_local(lon, lat):
        e, n = tf.transform(lon, lat)
        dx, dy = e-cx, n-cy
        return dx*co+dy*si, -dx*si+dy*co
    return to_local, region


def stable_int(building_id: str, salt: str = "") -> int:
    return int.from_bytes(sha256((building_id + "|" + salt).encode("ascii")).digest()[:8], "big")


def segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    t = 0 if denom <= 0 else max(0.0, min(1.0,
        ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def nearest_distance(point, segments):
    return round(min(segment_distance(point, a, b) for a, b in segments), 2) if segments else None


def polygon_area_m2(vertices):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(vertices, vertices[1:]))) / 2


def floor_origin(tags):
    """Never describe missing OSM heights as a measurement."""
    text = tags.get("height", "").strip().replace(",", ".")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*m?", text)
    if m:
        h = float(m.group(1))
        if 1.5 <= h <= 260.0:
            return round(h, 2), "OSM_EXPLICIT_HEIGHT_M", None
    levels = tags.get("building:levels", "").strip().replace(",", ".")
    if re.fullmatch(r"\d+(?:\.\d+)?", levels):
        n = float(levels)
        if 1 <= n <= 80:
            return round(n * 3.0, 2), "OSM_LEVELS_ESTIMATE_3M_PER_FLOOR", n
    return 18.0, "ESTIMATE_NOT_SURVEYED", None


def choose_family(tags: dict[str, str], street_distance: float | None, ident: str):
    """Use OSM tags when available. Otherwise these are visuals, not usages."""
    category = tags.get("building", "yes")
    tourism = tags.get("tourism", "")
    office = tags.get("office", "")
    shop = tags.get("shop", "")
    amenity = tags.get("amenity", "")
    if tourism in ("hotel", "hostel", "guest_house") or category == "hotel":
        return ("hotel_classico", "hotel_contemporaneo")[stable_int(ident, "hotel") % 2], "OSM_USE_HINT"
    if category in ("church", "cathedral", "hospital", "school", "university", "public", "civic") or amenity in ("school", "hospital", "place_of_worship"):
        return "equipamento_especial", "OSM_USE_HINT"
    if office or category in ("office", "commercial"):
        return "escritorio_clinica", "OSM_USE_HINT"
    if shop or category in ("retail", "supermarket", "kiosk"):
        return "misto_loja_terrea", "OSM_USE_HINT"
    # Generic or residential tags give no reliable construction-era/style data.
    # Hash distribution assigns a VISUAL typology, not a verified business use.
    near_waterfront = street_distance is not None and street_distance <= 125
    if near_waterfront:
        weighted = [
            "residencial_orla", "residencial_orla", "residencial_anos70",
            "hotel_classico", "hotel_contemporaneo", "art_deco_carioca",
            "misto_loja_terrea", "residencial_compacto", "predio_historico",
            "residencial_orla",
        ]
    else:
        weighted = [
            "residencial_anos70", "residencial_compacto", "residencial_compacto",
            "predio_historico", "art_deco_carioca", "misto_loja_terrea",
            "escritorio_clinica", "residencial_orla", "residencial_anos70",
            "equipamento_especial",
        ]
    return weighted[stable_int(ident, "zone-family") % len(weighted)], "UNVERIFIED_VISUAL_STYLE_ONLY"


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if catalog["status"] != "FIFTY_PROCEDURAL_RECIPES_ONLY_NOT_FBX_OR_UNITY_PREFABS":
        raise RuntimeError("Refuse to misrepresent ungenerated meshes as assets")
    styles = {s["id"]: s for s in catalog["styles"]}
    if len(styles) != 50:
        raise RuntimeError("Exactly 50 unique recipes required")
    family_styles = {}
    for s in catalog["styles"]:
        family_styles.setdefault(s["family"], []).append(s["id"])
    if len(family_styles) != 10 or any(len(v) != 5 for v in family_styles.values()):
        raise RuntimeError("Expected ten five-variant families")

    to_local, region = frame_transform()
    with gzip.open(OSM, "rb") as fp:
        root = ET.parse(fp).getroot()
    nodes = {n.attrib["id"]: to_local(float(n.attrib["lon"]), float(n.attrib["lat"]))
             for n in root.findall("node") if n.get("id") and n.get("lat") and n.get("lon")}
    streets = []
    building_ways = []
    for w in root.findall("way"):
        tags = {t.get("k"): t.get("v") for t in w.findall("tag")}
        refs = [nd.get("ref") for nd in w.findall("nd")]
        if tags.get("name", "").casefold() == "avenida atlântica" and tags.get("highway"):
            pts = [nodes[ref] for ref in refs if ref in nodes]
            streets.extend(zip(pts, pts[1:]))
        if tags.get("building") not in (None,"no"):
            building_ways.append((w.get("id"), refs, tags))
    if not streets:
        raise RuntimeError("Avenida Atlântica is missing in frozen OSM: don't fake waterfront zones")

    plan = []
    discarded = Counter()
    for osm_id, refs, tags in building_ways:
        if not refs or len(refs) < 4 or refs[0] != refs[-1]:
            discarded["open_ring"] += 1
            continue
        if any(ref not in nodes for ref in refs):
            discarded["missing_osm_node"] += 1
            continue
        try:
            polygon=Polygon([nodes[ref] for ref in refs])
            if not polygon.is_valid:
                polygon=polygon.buffer(0)
            if polygon.is_empty:
                discarded["invalid_geometry"]+=1
                continue
            clipped=polygon.intersection(region)
        except Exception:
            discarded["geometry_error"]+=1
            continue
        def parts(geometry):
            if geometry.is_empty:return
            if geometry.geom_type=="Polygon":
                yield geometry
            elif hasattr(geometry,"geoms"):
                for part in geometry.geoms:
                    yield from parts(part)
        pieces=[part for part in parts(clipped) if part.area>=1.0]
        if not pieces:
            discarded["outside_source_roi"]+=1
            continue
        for part_idx, poly in enumerate(pieces):
            # The true geographic base can split one source way when a polygon
            # crosses the ROI. Every part is assigned a stable unique identity.
            base_id="way/"+osm_id
            ident=base_id if len(pieces)==1 else base_id+"#part"+str(part_idx+1)
            centroid=(poly.centroid.x,poly.centroid.y)
            distance=nearest_distance(centroid,streets)
            family,fidelity=choose_family(tags,distance,ident)
            variants=family_styles[family]
            style_id=variants[stable_int(ident,"style-choice")%len(variants)]
            height,height_type,level_tag=floor_origin(tags)
            plan.append({
                "building_id":ident,
                "style_id":style_id,
                "visual_family":family,
                "seed":stable_int(ident,"stable-procedural-seed")%2147483647,
                "visual_style_basis":fidelity,
                "osm_building_tag":tags["building"],
                "area_footprint_m2":round(poly.area,2),
                "centroid_local_xy_m":[round(centroid[0],3),round(centroid[1],3)],
                "footprint_ring_local_xy_m":[[round(x,3),round(y,3)] for x,y in list(poly.exterior.coords)],
                "interior_rings_local_xy_m":[[[round(x,3),round(y,3)] for x,y in ring.coords] for ring in poly.interiors],
                "avenida_atlantica_distance_m":distance,
                "height_for_visualization_m":height,
                "height_provenance":height_type,
                "osm_levels":level_tag,
                "source_osm_way":base_id,
                "has_final_generated_mesh":False,
                "requires_visual_art_approval":True,
            })
    plan.sort(key=lambda d: (int(d["building_id"].split("/")[1].split("#")[0]),d["building_id"]))
    counts = Counter(x["style_id"] for x in plan)
    families = Counter(x["visual_family"] for x in plan)
    height_sources = Counter(x["height_provenance"] for x in plan)
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if len(plan) < 1200:
        raise RuntimeError("Missing most of the original Copacabana 1468 buildings")
    if len(plan) > report["real_osm_entities_within_roi"]["building"]:
        raise RuntimeError("Generated more buildings than recorded geographic dataset")
    if len(set(x["building_id"] for x in plan)) != len(plan):
        raise RuntimeError("OSM IDs duplicated")
    if len(counts) < 30:
        raise RuntimeError("Insufficient 50-style diversity across buildings")
    output = {
        "status": "R4_REAL_OSM_STYLE_BLUEPRINT_NO_MESH",
        "source_osm": "geo/data/copacabana.osm.gz",
        "source_sha256": sha256(OSM.read_bytes()).hexdigest(),
        "style_catalog": "ArtSource/ProceduralBuildings/Resort50Styles.json",
        "style_catalog_sha256": sha256(CATALOG.read_bytes()).hexdigest(),
        "num_styles_available": len(styles),
        "num_styles_assigned": len(counts),
        "num_buildings_assigned": len(plan),
        "source_building_count_reported": report["real_osm_entities_within_roi"]["building"],
        "discarded_way_reasons": dict(discarded),
        "families_assigned": dict(sorted(families.items())),
        "style_uses": dict(sorted(counts.items())),
        "height_provenance": dict(sorted(height_sources.items())),
        "important": "Visual assignments and 50 recipes ONLY. No generated facade meshes, scene insertion, import into Unity, approved textures, or replacement of GIS. Near-Avenida classification is geometric, not a cadastral statement.",
        "licenses": {"osm": "© OpenStreetMap contributors — ODbL 1.0",
                     "styles": "Original Project Resort"},
        "buildings": plan,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    print("R4_OSM_50_STYLE_BLUEPRINT",
          json.dumps({"count": len(plan), "families": len(families),
                      "styles_used": len(counts), "heights": dict(height_sources),
                      "discarded": dict(discarded)}))


if __name__ == "__main__":
    main()
