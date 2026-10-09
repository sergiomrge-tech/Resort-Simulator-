"""R7: remove exactly the 50 already-authored procedural FBX source ways.

Rebuilds the original OSM city geometrically; compares triangle multisets
rather than counts alone. No original asset is mutated and no streets may
change. The derived OBJ alone is NOT a Unity scene or art approval.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"build/R7_OSM_MASK"
REPORT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/R7_SOURCE_MASK_QA.json"
SOURCE=ROOT/"Tools/geo/r5_original_osm_pipeline.py"
GALLERY=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/Procedural/R7_GALLERY_GENERATION_REPORT.json"
ASSIGN=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
FRAME=ROOT/"geo/procedural/R4_SOURCE_FRAME.json"
OSM=ROOT/"geo/data/copacabana.osm.gz"

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def obj_signatures(path):
    vertices=[None]
    counts=Counter()
    signatures=Counter()
    mat="NULL"
    with path.open(encoding="utf-8") as fp:
        for line in fp:
            if line.startswith("v "):
                vertices.append(tuple(line.split()[1:4]))
            elif line.startswith("usemtl "):
                mat=line.strip().split()[1]
            elif line.startswith("f "):
                indices=[int(s.split("/")[0]) for s in line.split()[1:]]
                if len(indices)!=3:raise RuntimeError("Source city unexpectedly contains a non-triangle")
                signatures[(mat,tuple(sorted(vertices[idx] for idx in indices)))]+=1
                counts[mat]+=1
    return counts,signatures,len(vertices)-1

def reconstruct(directory,skip):
    directory.mkdir(parents=True,exist_ok=True)
    dest=directory/"data"
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(SOURCE,directory/"pipeline.py")
    shutil.copyfile(FRAME,directory/"region.json")
    shutil.copyfile(OSM,dest/"copacabana.osm.gz")
    env=os.environ.copy()
    env["RESORT_R5_SKIP_OSM_IDS"]=",".join(skip)
    result=subprocess.run([sys.executable,str(directory/"pipeline.py")],
        cwd=directory,env=env,capture_output=True,text=True,check=False)
    if result.returncode:
        raise RuntimeError("Original GIS OSM rebuild failed: "+
                           result.stdout[-2500:]+result.stderr[-4000:])
    path=dest/"copacabana_base.obj"
    if not path.is_file() or path.stat().st_size<120000:
        raise RuntimeError("Unusable OSM OBJ")
    return path

def main():
    a=json.loads(ASSIGN.read_text(encoding="utf-8"))
    g=json.loads(GALLERY.read_text(encoding="utf-8"))
    if a["num_buildings_assigned"]!=1468 or g["count"]!=50:
        raise RuntimeError("Expected immutable 1,468/50 GIS catalog and FBX collection")
    ids=[m["building_id"] for m in g["meshes"]]
    if len(ids)!=50 or len(set(ids))!=50 or any(re.fullmatch(r"way/\d+",k) is None for k in ids):
        raise RuntimeError("Exactly 50 distinct whole OSM ways required, no clipped way fragments")
    indexed={b["building_id"]:b for b in a["buildings"]}
    if any(k not in indexed for k in ids):
        raise RuntimeError("Model without a matching real OSM footprint")
    if {"way/1048277518","way/1048277521"}&set(ids):
        raise RuntimeError("Refuse to overwrite reserved R3 pilot buildings")
    for model in g["meshes"]:
        source=ROOT/model["fbx"]
        if not source.is_file() or sha(source)!=model["fbx_sha256"]:
            raise RuntimeError("One R7 UV0 FBX is missing/corrupt")
        if model["style_id"]!=indexed[model["building_id"]]["style_id"]:
            raise RuntimeError("Style mismatch between full geodata and model")
    original=reconstruct(OUT/"original",[])
    masked=reconstruct(OUT/"derived",sorted(ids))
    before,s_before,v0=obj_signatures(original)
    after,s_after,v1=obj_signatures(masked)
    if before!={"Building":23033,"Road":3731} or v0!=62980:
        raise RuntimeError("Source GIS map failed original geometric census")
    removed=s_before-s_after
    added=s_after-s_before
    if added:raise RuntimeError("City mask created unknown/new triangles")
    if any(key[0]!="Building" for key in removed):
        raise RuntimeError("City mask reached original road/terrain geometry")
    if removed and sum(removed.values())<50:
        raise RuntimeError("Fewer than 50 building faces removed for 50 OSM models")
    if before["Road"]!=after["Road"] or after["Building"]>=before["Building"]:
        raise RuntimeError("Original city material counts invalid after selective masking")
    if {k:n for k,n in s_before.items() if k[0]=="Road"} != {
       k:n for k,n in s_after.items() if k[0]=="Road"}:
        raise RuntimeError("Street geometric signature changed (even though counts may match)")
    if sum(s_after.values())!=sum(s_before.values())-sum(removed.values()):
        raise RuntimeError("Unselected city geometry mutated")
    old_blend=ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
    old_fbx=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
    report={
        "status":"R7_FIFTY_OSM_MASK_ALL_ROAD_GEOMETRY_IDENTICAL",
        "source_geo_original_sha256":sha(old_blend),
        "source_fbx_original_sha256":sha(old_fbx),
        "source_osm_sha256":sha(OSM),
        "source_style_assignments_sha256":sha(ASSIGN),
        "source_50_models_report_sha256":sha(GALLERY),
        "masked_way_count":len(ids),
        "masked_way_ids":sorted(ids),
        "source_material_faces":dict(before),
        "derived_material_faces":dict(after),
        "road_faces_removed":0,
        "building_faces_removed":sum(removed.values()),
        "identical_unmasked_tris":sum(s_after.values()),
        "original_city_vertices":v0,
        "derived_city_vertices":v1,
        "original_obj_sha256":sha(original),
        "derived_obj_sha256":sha(masked),
        "derived_obj":"build/R7_OSM_MASK/derived/data/copacabana_base.obj",
        "bounds_crs":"EPSG:32723 with source BlenderGIS 46-degree object rotation",
        "important":"This establishes byte-quantized OSM triangle parity, not native Unity/Steam playability or final visual quality."
    }
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("R7_MASK_PARITY",json.dumps({k:report[k] for k in
        ("masked_way_count","source_material_faces","derived_material_faces",
         "road_faces_removed","building_faces_removed","identical_unmasked_tris")}),flush=True)

if __name__=="__main__":
    main()
