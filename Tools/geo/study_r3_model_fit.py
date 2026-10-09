"""Find conservative original-FBX fit inside exact mapped OSM building rings.

NO prefab insertion into the city: this is an auditable geometry compatibility
study, NOT a terrain, cadastral ownership, surveyed heights or art approval.
All dimensions are from Blender FBX *measured* source geometry.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SITES=ROOT/"geo/pilot/R3_EXACT_OSM_PARCELS.json"
CATALOG=ROOT/"ArtSource/Previews/Owned_CoastalUrbanKit_QA.json"
OUT=ROOT/"geo/pilot/R3_MODEL_FIT_STUDY.json"
PREFERENCES={
    "way/1048277518":"hotel",
    "way/1308635852":"townhouse",
    "way/1048277521":"residencial_sacadas"
}


def in_poly(x,y,ring):
    inside=False
    for a,b in zip(ring,ring[1:]):
        if (a[1]>y)!=(b[1]>y) and x<((b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]):
            inside=not inside
    return inside


def cross(p,q,r):
    return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])


def overlap(a,b,c,d):
    ab1,ab2=cross(a,b,c),cross(a,b,d)
    cd1,cd2=cross(c,d,a),cross(c,d,b)
    return ab1*ab2<-1e-8 and cd1*cd2<-1e-8


def valid_rect(center,dims,rotation,ring,margin=.22):
    co,si=math.cos(rotation),math.sin(rotation)
    hx,hy=dims[0]/2+margin,dims[1]/2+margin
    corners=[
        (center[0]+u*co-v*si,center[1]+u*si+v*co)
        for u,v in ((-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy))
    ]
    if not all(in_poly(x,y,ring) for x,y in corners):
        return False,corners
    if any(overlap(a,b,c,d) for a,b in zip(corners,corners[1:]+corners[:1])
           for c,d in zip(ring,ring[1:])):
        return False,corners
    return True,corners


def propose(site,model):
    ring=site["ring_xy_m"]
    c=site["centroid_local_xy_m"]
    orig=model["dimensions_from_imported_FBX_m"]
    # X and Y horizontal after reading the original authored FBX back into Blender.
    # Altitude Z is NOT taken from OSM and is excluded from fitting.
    w,d=orig[:2]
    optimum=None
    # Prefer genuinely life-size architecture, permit at most 20% shrinkage.
    # 2-metre centroid shift allows geometric centroids in concave parcels.
    for scale in (1.0,.98,.95,.92,.90,.87,.84,.80):
        dims=(w*scale,d*scale)
        proposals=[]
        for deg in range(0,180,5):
            ang=math.radians(deg)
            for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),
                          (2,0),(-2,0),(0,2),(0,-2),
                          (1,1),(-1,-1),(1,-1),(-1,1)):
                center=(c[0]+dx,c[1]+dy)
                good,corners=valid_rect(center,dims,ang,ring)
                if good:
                    proposals.append((math.hypot(dx,dy)+abs(deg-90)*0.0001,center,deg,corners))
        if proposals:
            proposals.sort(key=lambda x:x[0])
            _,center,deg,corners=proposals[0]
            optimum={
               "fit":"GEOMETRIC_FIT_ONLY",
               "scale":scale,
               "yaw_blender_degrees":deg,
               "center_xy_m":[round(x,4) for x in center],
               "proposed_footprint_xy_m":[[round(x,4),round(y,4)] for x,y in corners],
               "horizontal_clearance_m":.22,
               "height_unverified_m":orig[2]*scale,
               "height_measured_from_fbx_not_from_osm":True,
            }
            break
    return optimum or {
      "fit":"NO_CONSERVATIVE_FIT_WITHOUT_GEOMETRY_CHANGES",
      "reason":"Do not deform original architecture, clone over existing GIS mesh or ignore setback.",
    }


def main():
    sites=json.loads(SITES.read_text(encoding="utf-8"))
    qa=json.loads(CATALOG.read_text(encoding="utf-8"))
    if sites["parcel_count"]!=3 or len(qa["models"])!=8:
        raise RuntimeError("Lost authoritative map geometry or authored model library")
    findings={}
    for site in sites["parcels"]:
        name=PREFERENCES[site["id"]]
        model=qa["models"][name]
        position=propose(site,model)
        findings[site["id"]]={
           "osm_building_footprint_id":site["id"],
           "authored_model":name,
           "source_fbx":model["source"],
           "source_fbx_sha256":model["sha256"],
           "original_fbx_dimensions_m":model["dimensions_from_imported_FBX_m"],
           "osm_footprint_m2":site["footprint_area_m2"],
           "placement_study":position,
        }
    result={
      "status":"R3_GEOMETRY_STUDY_NOT_INTEGRATED_IN_WORLD",
      "metric_projection":"EPSG:32723 original rotated local Blender XY",
      "source_footprints":"geo/pilot/R3_EXACT_OSM_PARCELS.json",
      "source_model_measurements":"ArtSource/Previews/Owned_CoastalUrbanKit_QA.json",
      "proposed_count":sum(v["placement_study"]["fit"]=="GEOMETRIC_FIT_ONLY" for v in findings.values()),
      "sites":findings,
      "limits":"No source map removal, no Unity prefab, no actual building height or plot ownership. Fit by 2D rectangle is preliminary."
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("R3_MODEL_FIT_STUDY",json.dumps({k:v["placement_study"] for k,v in findings.items()},ensure_ascii=False))

if __name__=="__main__":
    main()
