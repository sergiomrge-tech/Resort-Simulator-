"""R3: deterministically reconstruct source and masked OSM OBJ in Github Actions.

This uses the *exact* old Project Resort GIS writer, saved with provenance at
Tools/geo/r3_original_osm_pipeline.py. It NEVER downloads new OSM. The masked
OBJ differs from unfiltered only in two selected OSM ways; roads must match
exactly, face by face. The original BLEND/FBX is not overwritten.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Tools/geo/r3_original_osm_pipeline.py"
FRAME=ROOT/"geo/pilot/COPACABANA_FRAME_SOURCE.json"
OSM=ROOT/"geo/data/copacabana.osm.gz"
STUDY=ROOT/"geo/pilot/R3_MODEL_FIT_STUDY.json"
WORK=ROOT/"build/R3_OSM_PARITY"
REPORT=ROOT/"ArtSource/Previews/R3_GIS_Mask_Parity_QA.json"

def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

def read_obj(path):
    vertices=[None]
    counts=Counter()
    signatures=Counter()
    mat="NONE"
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("v "):
                vertices.append(tuple(line.split()[1:4]))
            elif line.startswith("usemtl "):
                mat=line.split()[1]
            elif line.startswith("f "):
                verts=[]
                for idx in line.split()[1:]:
                    v=vertices[int(idx.split("/")[0])]
                    verts.append(v)
                if len(verts)!=3:
                    raise RuntimeError("Expected all source OBJ surfaces triangulated")
                counts[mat]+=1
                signatures[(mat,tuple(sorted(verts)))]+=1
    return counts,signatures,len(vertices)-1

def generate(out_dir,skip):
    out_dir.mkdir(parents=True,exist_ok=True)
    data=out_dir/"data"
    data.mkdir(exist_ok=True)
    shutil.copyfile(SCRIPT,out_dir/"pipeline.py")
    shutil.copyfile(FRAME,out_dir/"region.json")
    shutil.copyfile(OSM,data/"copacabana.osm.gz")
    env=os.environ.copy()
    env["RESORT_R3_SKIP_OSM_IDS"]=",".join(skip)
    completed = subprocess.run([sys.executable,str(out_dir/"pipeline.py")],cwd=str(out_dir),
                   env=env,check=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if completed.returncode:
        raise RuntimeError("Original GIS writer failed (stdout/stderr):\n" +
                           completed.stdout[-3000:] + "\n" + completed.stderr[-4000:])
    obj=data/"copacabana_base.obj"
    if not obj.is_file() or obj.stat().st_size<200000:
        raise RuntimeError("Original OSM pipeline did not generate a valid city OBJ")
    return obj

def main():
    study=json.loads(STUDY.read_text(encoding="utf-8"))
    skip=sorted(oid for oid,s in study["sites"].items()
                if s["placement_study"]["fit"]=="GEOMETRIC_FIT_ONLY")
    if skip!=["way/1048277518","way/1048277521"]:
        raise RuntimeError("Mask must include exactly the two verified FBX-compatible sites")
    original=generate(WORK/"unfiltered",[])
    derived=generate(WORK/"masked",skip)
    before,sig_before,nverts_before=read_obj(original)
    after,sig_after,nverts_after=read_obj(derived)
    if before["Road"]!=3731 or before["Building"]!=23033 or sum(before.values())!=26764:
        raise RuntimeError(f"Regenerated original OSM city is NOT identical in material face counts: {before}")
    if before["Road"]!=after["Road"]:
        raise RuntimeError("Regeneration unexpectedly modified road face count")
    removed=sig_before-sig_after
    added=sig_after-sig_before
    if added:
        raise RuntimeError(f"Derivative adds original-building faces/roads not in source: {len(added)}")
    if any(mat!="Building" for mat,_ in removed):
        raise RuntimeError("Mask would delete road or non-building geography")
    if after["Building"]>=before["Building"] or before["Building"]-after["Building"]<10:
        raise RuntimeError("Mask did not exclude two verified original OSM buildings")
    # The exact face-signature multiset, not just counts, must survive.
    if sum(sig_before.values())-sum(removed.values())!=sum(sig_after.values()):
        raise RuntimeError("Unmasked triangles were not preserved exactly")
    road_signatures={t:v for t,v in sig_before.items() if t[0]=="Road"}
    if road_signatures!={t:v for t,v in sig_after.items() if t[0]=="Road"}:
        raise RuntimeError("Even one road triangle changed: source geography corrupted")
    report={
       "status":"ORIGINAL_OSM_PIPELINE_GEOMETRY_PARITY",
       "source_pipeline":"Tools/geo/r3_original_osm_pipeline.py",
       "source_osm":"geo/data/copacabana.osm.gz",
       "source_osm_sha256":sha(OSM),
       "source_blend_sha256":sha(ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"),
       "source_fbx_sha256":sha(ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"),
       "masked_ways":skip,
       "before_material_faces":dict(before),
       "after_material_faces":dict(after),
       "removed_original_building_faces":sum(removed.values()),
       "removed_road_faces":0,
       "exact_unchanged_faces_including_all_roads":sum(sig_after.values()),
       "before_obj_sha256":sha(original),
       "after_obj_sha256":sha(derived),
       "before_obj_vertices":nverts_before,
       "after_obj_vertices":nverts_after,
       "source_blender_face_count_expected":26764,
       "limits":"This compares OSM pipeline geometry, not yet byte-parity with original Blender source. Future gate must verify Blender triangle parity before exporting any derivative Unity FBX.",
    }
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("R3_ORIGINAL_PIPELINE_MASK_PARITY",json.dumps(report,ensure_ascii=False))

if __name__=="__main__":
    main()
