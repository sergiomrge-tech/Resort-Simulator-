"""Independent Blender FBX roundtrip for R9: 48 actual trees, OSM shore & parks."""
import json,hashlib,sys,math
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[2]
file=root/"UnityProject/Assets/Architecture/R9_Environment/R9_Real_Coast_Parks_48_Trees.fbx"
rep=json.loads((file.parent/"R9_ENVIRONMENT_NATIVE_QA.json").read_text())
assert rep["fbx_sha256"]==hashlib.sha256(file.read_bytes()).hexdigest()
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(file))
meshes=[x for x in bpy.data.objects if x.type=="MESH"]
tree=[x for x in meshes if x.name.startswith("R9_TREE_")]
surface=[x for x in meshes if x.name.startswith("R9_") and not x.name.startswith("R9_TREE_")]
assert len(meshes)==70,(len(meshes),[x.name for x in meshes])
assert len(tree)==48 and len(surface)==22
assert len(set(x.name for x in tree))==48
assert len({m.name.split(".")[0] for t in tree for m in t.data.materials if m})==4
for t in tree:
 assert len(t.data.polygons)>50,(t.name,len(t.data.polygons))
 assert len(t.data.materials)==4,(t.name,[m.name for m in t.data.materials])
 assert all(m is not None for m in t.data.materials)
 assert all(math.isfinite(v) for vert in t.data.vertices for v in vert.co),t.name
for obj in surface:
 assert len(obj.data.materials)>=1,obj.name
 assert obj.data.uv_layers.active is not None,obj.name
assert rep["mapped_tree_instances"]==48 and rep["frame_m"]==[2000,1000]
assert rep["coast_samples"]==201 and rep["mapped_zones"]=={"park":14,"grass":3,"water":2}
print("R9_NATIVE_ENV_FBX_PASS",json.dumps({"meshes":len(meshes),"trees":len(tree),"surface_parts":len(surface),"material_slots_tree":4,"coast_samples":201,"zones":rep["mapped_zones"],"file_bytes":file.stat().st_size}),flush=True)
