"""Run by Blender (real FBX roundtrip): blender -b --python Tools/tests/test_r8_native_fbx.py"""
import sys,json,math,re,hashlib
from pathlib import Path
from collections import Counter
import bpy

ROOT=Path(__file__).resolve().parents[2]
FBX=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_Remaining_1418_Textured_Facades.fbx"
REPORT=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_FACADES_NATIVE_QA.json"
PAT=re.compile(r"^R8_(cop_[a-z0-9_]+)__(wall|glass|stone|trim|roof|metal|shadow)(?:\.\d+)?$")
with REPORT.open(encoding="utf-8") as f:report=json.load(f)
sha=hashlib.sha256(FBX.read_bytes()).hexdigest()
assert sha==report["r8_fbx_sha256"],"Generated FBX hash differs from manifest"
bpy.ops.import_scene.fbx(filepath=str(FBX))
meshes=[ob for ob in bpy.data.objects if ob.type=="MESH" and ob.name.startswith("R8_")]
assert len(meshes)==report["fbx_meshes"]==350,("Expected 350 batched meshes",len(meshes))
styles=set()
totals=Counter()
faces=0
for ob in meshes:
 m=PAT.match(ob.name)
 assert m is not None,("FBX lost its semantic mesh name",ob.name)
 styles.add(m.group(1));totals[m.group(2)]+=1
 mesh=ob.data
 assert len(mesh.materials)==1 and mesh.materials[0] is not None,("Missing material",ob.name)
 assert mesh.uv_layers.active is not None and len(mesh.uv_layers.active.data)>0,("Missing UV0",ob.name)
 for vertex in mesh.vertices:
  assert all(math.isfinite(v) for v in vertex.co),("Invalid coordinates",ob.name)
 assert all(math.isfinite(v) for uv in mesh.uv_layers.active.data for v in uv.uv),("Invalid UV0",ob.name)
 faces+=len(mesh.polygons)
assert styles and len(styles)==50 and totals==dict((p,50) for p in ("wall","shadow","glass","trim","roof","metal","stone")),totals
assert faces==report["geometry_faces"],("FBX face count differs from source",faces,report["geometry_faces"])
assert report["target_area_m"]==[2000,1000] and len(set(report["ids_r8"]))==1418
assert report["full_city_total"]==1468 and report["windows_generated"]>100000
print("R8_NATIVE_FBX_REIMPORT_PASS",json.dumps({"meshes":len(meshes),"styles":len(styles),"faces":faces,"windows":report["windows_generated"],"coverage":report["full_city_total"],"map":"2000m coast x 1000m inland"}),flush=True)
