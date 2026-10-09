"""Validate R10 coastal additions through an actual native Blender FBX roundtrip."""
import bpy,json,math,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
f=r/"UnityProject/Assets/Architecture/R10_Coastal/R10_Ocean_Foam_Mosaic_Promenade.fbx"
q=json.loads((f.parent/"R10_DETAILS_NATIVE_QA.json").read_text(encoding="utf-8"))
assert q["fbx_sha256"]==hashlib.sha256(f.read_bytes()).hexdigest()
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(f))
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(meshes)==q["fbx_meshes"]==9
assert sum(len(o.data.polygons) for o in meshes)==q["fbx_faces"]==3600
assert q["coast_aligned_length_m"]==2000 and q["map_inland_width_m"]==1000 and q["coast_samples"]==401
assert len([o for o in meshes if o.name.startswith("R10_MOSAIC_WAVE_BAND_")])==3
assert len([o for o in meshes if o.name.startswith("R10_WATER_BREAKING_FOAM_")])==3
for o in meshes:
 assert len(o.data.materials)==1 and o.data.materials[0] is not None,o.name
 assert o.data.uv_layers.active is not None,o.name
 assert len(o.data.polygons)==400,o.name
 assert all(math.isfinite(p) for uv in o.data.uv_layers.active.data for p in uv.uv),o.name
print("R10_NATIVE_FBX_REIMPORT_PASS",{"meshes":len(meshes),"faces":q["fbx_faces"],"wave_mosaics":3,"sea_foam_lines":3,"coast_samples":401,"bytes":f.stat().st_size},flush=True)
