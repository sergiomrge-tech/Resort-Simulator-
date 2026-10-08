"""Locate REAL OSM building footprints for a 300 x 300m coastal visual pilot.

Uses only the frozen OpenStreetMap snapshot and EXACT original local UTM frame.
Reports georeferenced candidate IDs and centroids; DOES NOT move buildings or
insert architectural modules in the city. No re-download and no randomness.
"""
from __future__ import annotations

import gzip
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "geo/data/copacabana.osm.gz"
FRAME_PATH = ROOT / "geo/pilot/COPACABANA_FRAME_SOURCE.json"
OUTPUT = ROOT / "geo/pilot/R2_PILOT_BUILDING_CANDIDATES.json"

# This strip intentionally contains both the Avenida Atlantica frontage and
# the waterfront edge. Exact sea/beach coverage needs later render validation.
WINDOW = {"min_x": -150.0, "max_x": 150.0, "min_y": -310.0, "max_y": -10.0}


class LocalFrame:
    def __init__(self, info):
        crs=info["crs"]
        self.proj = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        self.inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
        lon, lat = info["avenue_reference_lonlat"]
        east, north = self.proj.transform(lon, lat)
        angle=math.radians(info["axis_angle_degrees_counterclockwise_from_east"])
        self.c=math.cos(angle)
        self.s=math.sin(angle)
        shift=info["center_shift_inland_m"]
        self.cx = east - self.s * shift
        self.cy = north + self.c * shift

    def point(self, lon, lat):
        e,n=self.proj.transform(lon,lat)
        dx,dy=e-self.cx,n-self.cy
        return dx*self.c+dy*self.s, -dx*self.s+dy*self.c

    def geo(self, x, y):
        east=self.cx+x*self.c-y*self.s
        north=self.cy+x*self.s+y*self.c
        return self.inv.transform(east,north)


def centroid_area(coords):
    # Signed polygon centroid: supports concave footprints without geometry
    # simplification. Invalid or degenerate OSM shapes are excluded.
    twice_area=0.0
    cx=cy=0.0
    for (ax,ay),(bx,by) in zip(coords,coords[1:]):
        cross=ax*by-bx*ay
        twice_area+=cross
        cx+=(ax+bx)*cross
        cy+=(ay+by)*cross
    if abs(twice_area) < 1.0:
        return None
    return cx/(3*twice_area), cy/(3*twice_area), abs(twice_area)/2


def to_segment_distance(x,y,ax,ay,bx,by):
    vx,vy=bx-ax,by-ay
    denom=vx*vx+vy*vy
    if denom<1e-9: return math.hypot(x-ax,y-ay)
    t=max(0,min(1,((x-ax)*vx+(y-ay)*vy)/denom))
    return math.hypot(x-(ax+t*vx),y-(ay+t*vy))


def main():
    config=json.loads(FRAME_PATH.read_text(encoding="utf-8"))
    assert config["game_area_m2"] == 2_000_000
    frame=LocalFrame(config)
    with gzip.open(SOURCE,"rb") as f:
        root=ET.parse(f).getroot()
    if root.tag!="osm":
        raise ValueError("Not an OSM snapshot")
    nodes={}
    for el in root.findall("node"):
        if el.get("lon") and el.get("lat"):
            nodes[el.get("id")] = frame.point(float(el.get("lon")),float(el.get("lat")))
    roads=[]
    buildings=[]
    for el in root.findall("way"):
        tags={t.get("k"):t.get("v") for t in el.findall("tag")}
        ids=[n.get("ref") for n in el.findall("nd")]
        if len(ids)<2 or any(i not in nodes for i in ids):
            continue
        pts=[nodes[i] for i in ids]
        name=tags.get("name","")
        if tags.get("highway") and ("Atlântica" in name or "Atlantica" in name):
            roads.extend(((ax,ay,bx,by) for (ax,ay),(bx,by) in zip(pts,pts[1:])))
        if tags.get("building") in (None,"no") or len(pts)<4 or pts[0]!=pts[-1]:
            continue
        ca=centroid_area(pts)
        if ca is None: continue
        x,y,area=ca
        if not (WINDOW["min_x"]<=x<=WINDOW["max_x"] and
                WINDOW["min_y"]<=y<=WINDOW["max_y"] and 35<=area<=4500):
            continue
        buildings.append({
            "osm_id": "way/"+el.get("id"),
            "centroid_local_m": [round(x,3),round(y,3)],
            "centroid_lonlat": [round(z,8) for z in frame.geo(x,y)],
            "footprint_area_m2": round(area,2),
            "bbox_size_m": [round(max(p[0] for p in pts)-min(p[0] for p in pts),2),
                             round(max(p[1] for p in pts)-min(p[1] for p in pts),2)],
            "building_tag": tags.get("building"),
            "height_tag": tags.get("height"),
            "levels_tag": tags.get("building:levels"),
            "note": "OSM mapped footprint; no surveyed height implied"
        })
    if not roads:
        raise RuntimeError("No real Avenida Atlantica segments in snapshot; refuse guessed street")
    for item in buildings:
        x,y=item["centroid_local_m"]
        d=min(to_segment_distance(x,y,*seg) for seg in roads)
        item["distance_to_avenida_atlantica_m"]=round(d,2)
    buildings=[x for x in buildings if x["distance_to_avenida_atlantica_m"]<=150]
    buildings.sort(key=lambda x:(x["distance_to_avenida_atlantica_m"] +
           abs(x["centroid_local_m"][0])*.12, x["osm_id"]))
    selected=[]
    for item in buildings:
        x,y=item["centroid_local_m"]
        if any(math.hypot(x-b["centroid_local_m"][0],y-b["centroid_local_m"][1])<18 for b in selected):
            continue
        selected.append(item)
        if len(selected)==3: break
    if len(selected)!=3:
        raise RuntimeError(f"Only {len(selected)} mapped distinct buildings in the 300x300m pilot; check verified coordinates")
    output={
        "status":"CANDIDATES_NOT_APPROVED",
        "source_osm":"geo/data/copacabana.osm.gz",
        "frame":"geo/pilot/COPACABANA_FRAME_SOURCE.json",
        "measurement":"projected EPSG:32723 to original local X/Y metres (Blender Z-up)",
        "pilot_300x300m_local_bounds":WINDOW,
        "candidate_count_within_bounds":len(buildings),
        "candidates":selected,
        "limits":"No building meshes replaced, no terrain created, no Unity compile or render, no claimed exact heights.",
        "license":"© OpenStreetMap contributors — ODbL 1.0"
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("REAL OSM PILOT CANDIDATES:",json.dumps(selected,ensure_ascii=False))


if __name__=="__main__":
    main()
