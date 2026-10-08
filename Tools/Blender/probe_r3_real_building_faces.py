"""Inspect existing real Copacabana Blender geometry at three exact OSM sites.

This is deliberately diagnostic/read-only: does not delete any faces or
introduce a replacement building. It answers whether source faces can be
isolated safely prior to an architectural hero-building swap.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/"geo/pilot/R3_EXACT_OSM_PARCELS.json"
REPORT=ROOT/"ArtSource/Previews/R3_Pilot_OSM_Geometry_Probe.json"


def edge_distance(point,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1]
    denom=vx*vx+vy*vy
    t=0 if denom<1e-12 else max(0,min(1,((point[0]-a[0])*vx+(point[1]-a[1])*vy)/denom))
    return math.hypot(point[0]-(a[0]+t*vx),point[1]-(a[1]+t*vy))


def inside(point, ring):
    x,y=point
    hit=False
    for a,b in zip(ring,ring[1:]):
        if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            hit=not hit
    return hit


data=json.loads(INPUT.read_text(encoding="utf-8"))
parcels=data["parcels"]
for p in parcels:
    p["ring"]=p["ring_xy_m"]
    p["hits"]=0
    p["boundary_hits"]=0
    p["roof_faces"]=0
    p["zmin"]=1e12
    p["zmax"]=-1e12
    p["source_materials"]={}
    p["sample_source_faces"]=[]

model_objects=[x for x in bpy.data.objects if x.type=="MESH" and len(x.data.polygons)>0]
if not model_objects:
    raise RuntimeError("No genuine BlenderGIS mesh found in opened Copacabana source")
report={"status":"INSPECTED_SOURCE_NOT_MODIFIED","original_mesh_objects":len(model_objects),
        "total_source_faces":sum(len(x.data.polygons) for x in model_objects),
        "materials":{},"parcels":[],"geometry_safe_to_replace":False,
        "no_mutation":"READ_ONLY_BPY_NO_WRITE_BLEND_OR_FBX"}
for obj in model_objects:
    matnames=[x.name if x else "null" for x in obj.data.materials]
    for name in matnames:report["materials"][name]=report["materials"].get(name,0)
    for poly in obj.data.polygons:
        matname=matnames[poly.material_index] if poly.material_index<len(matnames) else "unknown"
        report["materials"][matname]=report["materials"].get(matname,0)+1
        world=obj.matrix_world@poly.center
        xy=world.x,world.y
        for site in parcels:
            bounds=site["bounds_xy_m"]
            if not (bounds["min_x"]-1<=xy[0]<=bounds["max_x"]+1 and
                    bounds["min_y"]-1<=xy[1]<=bounds["max_y"]+1):
                continue
            ring=site["ring"]
            dist=min(edge_distance(xy,a,b) for a,b in zip(ring,ring[1:]))
            is_inside=inside(xy,ring)
            if is_inside or dist<=0.45:
                site["hits"]+=1
                if dist<=0.45:site["boundary_hits"]+=1
                if (obj.matrix_world.to_3x3()@poly.normal).z>.5:site["roof_faces"]+=1
                site["zmin"]=min(site["zmin"],world.z)
                site["zmax"]=max(site["zmax"],world.z)
                site["source_materials"][matname]=site["source_materials"].get(matname,0)+1
                if len(site["sample_source_faces"])<5:
                    site["sample_source_faces"].append({"mesh":obj.name,"face_id":poly.index,"xy":[round(x,2) for x in xy],"z":round(world.z,2),"material":matname})

for site in parcels:
    materials=site["source_materials"]
    brief={k:site[k] for k in (
        "id","hits","boundary_hits","roof_faces","source_materials","sample_source_faces"
    )}
    brief["zmin"]=round(site["zmin"],2) if site["hits"] else None
    brief["zmax"]=round(site["zmax"],2) if site["hits"] else None
    brief["has_existing_building_geometry"]=sum(v for k,v in materials.items() if "build" in k.lower())>0
    report["parcels"].append(brief)
report["geometry_safe_to_replace"]=all(x["has_existing_building_geometry"] and x["roof_faces"]>=1 for x in report["parcels"])
report["limits"]="Face centroid proximity is diagnostic only; replacement requires component isolation verification, not this probe."
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("R3_PILOT_GEOMETRY_PROBE:",json.dumps(report,ensure_ascii=False))
