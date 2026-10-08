"""Reconstruct exact OSM footprint rings in the original Blender local frame.

No external map request: only the immutable geo/data/copacabana.osm.gz and
archived georeference are used. No guesses about heights, rights or zoning.
"""
from __future__ import annotations
import gzip
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
OSM = ROOT / "geo/data/copacabana.osm.gz"
FRAME = ROOT / "geo/pilot/COPACABANA_FRAME_SOURCE.json"
INPUT = ROOT / "geo/pilot/R2_PILOT_BUILDING_CANDIDATES.json"
OUTPUT = ROOT / "geo/pilot/R3_EXACT_OSM_PARCELS.json"


def ring_properties(vertices):
    area2 = cx = cy = 0.0
    for (ax, ay), (bx, by) in zip(vertices, vertices[1:]):
        cross = ax*by-bx*ay
        area2 += cross
        cx += (ax+bx)*cross
        cy += (ay+by)*cross
    if abs(area2) < 2.0:
        raise RuntimeError("Degenerate OSM footprint area")
    return abs(area2)*0.5, (cx/(3*area2),cy/(3*area2))


def convert_frame(config):
    tf = Transformer.from_crs("EPSG:4326", config["crs"], always_xy=True)
    east,north = tf.transform(*config["avenue_reference_lonlat"])
    ang = math.radians(config["axis_angle_degrees_counterclockwise_from_east"])
    co,si = math.cos(ang),math.sin(ang)
    cx = east-si*config["center_shift_inland_m"]
    cy = north+co*config["center_shift_inland_m"]
    def convert(lon,lat):
        e,n = tf.transform(lon,lat)
        de,dn = e-cx,n-cy
        return (de*co+dn*si, -de*si+dn*co)
    return convert


def main():
    config = json.loads(FRAME.read_text(encoding="utf-8"))
    previous = json.loads(INPUT.read_text(encoding="utf-8"))
    if previous["status"] != "CANDIDATES_NOT_APPROVED" or len(previous["candidates"]) != 3:
        raise RuntimeError("Expected exactly three frozen pilot parcel candidates")
    expected = {x["osm_id"].split("/")[1]:x for x in previous["candidates"]}
    conv = convert_frame(config)
    with gzip.open(OSM,"rb") as stream:
        root = ET.parse(stream).getroot()
    nodes = {}
    for node in root.findall("node"):
        if node.get("id") and node.get("lon") and node.get("lat"):
            nodes[node.get("id")] = conv(float(node.get("lon")),float(node.get("lat")))
    records=[]
    for way in root.findall("way"):
        oid=way.get("id")
        if oid not in expected: continue
        tags={t.get("k"):t.get("v") for t in way.findall("tag")}
        if tags.get("building") in (None,"no","roof","carport","shed","garage","garages"):
            raise RuntimeError("Selected OSM way is not an enclosed building")
        refs=[nd.get("ref") for nd in way.findall("nd")]
        if len(refs)<4 or refs[0]!=refs[-1] or any(ref not in nodes for ref in refs):
            raise RuntimeError("Selected OSM way has an invalid/partial closed ring")
        ring=[nodes[ref] for ref in refs]
        area, center = ring_properties(ring)
        old = expected[oid]
        if abs(area-old["footprint_area_m2"])>0.10:
            raise RuntimeError("Area mismatch with previously confirmed candidate "+oid)
        error = math.dist(center,old["centroid_local_m"])
        if error>0.02:
            raise RuntimeError("Coordinate projection no longer matches original: "+str(error))
        if not (-150<center[0]<150 and -310<center[1]<-10):
            raise RuntimeError("Building center lies outside the pilot")
        records.append({
          "id":"way/"+oid,
          "category":tags["building"],
          "vertex_count":len(ring)-1,
          "ring_xy_m":[[round(x,6),round(y,6)] for x,y in ring],
          "centroid_local_xy_m":[round(z,6) for z in center],
          "footprint_area_m2":round(area,3),
          "bounds_xy_m":{
            "min_x":round(min(v[0] for v in ring),4),
            "min_y":round(min(v[1] for v in ring),4),
            "max_x":round(max(v[0] for v in ring),4),
            "max_y":round(max(v[1] for v in ring),4)
          },
          "actual_height_m":None,
          "existing_map_building_present":"PENDING_BLENDER_PROBE",
          "source":"frozen OSM way, EPSG:32723 rotated local metres"
        })
    if len(records)!=3 or len({x["id"] for x in records})!=3:
        raise RuntimeError("At least one of three OSM parcels missing")
    records.sort(key=lambda x:x["id"])
    output={
      "status":"EXACT_OSM_FOOTPRINTS_GEOMETRY_ONLY",
      "source_osm":"geo/data/copacabana.osm.gz",
      "source_frame":"geo/pilot/COPACABANA_FRAME_SOURCE.json",
      "bounds_300x300_xy_m":previous["pilot_300x300m_local_bounds"],
      "geography":"Copacabana RJ. Blender X/Y horizontal, Z up. FBX Unity X/Z horizontal, Y up.",
      "models_available":"Nine authored FBX assets in Assets/Architecture, but not positioned/approved",
      "parcel_count":3,
      "parcels":records,
      "copyright":"© OpenStreetMap contributors; ODbL 1.0",
      "limits":"Footprints are mapped building shapes, NOT legal parcel boundaries, height surveys, or purchase rights."
    }
    OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("R3_EXACT_FOOTPRINTS_VALIDATED",*[f"{r['id']} area={r['footprint_area_m2']} m2, {r['vertex_count']} vertices" for r in records])

if __name__=="__main__":
    main()
