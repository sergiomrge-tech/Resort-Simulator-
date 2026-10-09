"""Actual Blender FBX roundtrip of R11 real architecture, no fake previews."""
import bpy,json,math,re,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
f=r/"UnityProject/Assets/Architecture/R11_Architecture/R11_Real_Facade_Volumetry_1418.fbx"
qa=json.loads((f.parent/"R11_ARCHITECTURE_NATIVE_QA.json").read_text(encoding="utf-8"))
assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==qa["fbx_sha256"]
assert qa["source_hashes"]["r8_fbx"]==hashlib.sha256(
 (r/"UnityProject/Assets/Architecture/R8_FullCity/R8_Remaining_1418_Textured_Facades.fbx").read_bytes()).hexdigest()
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(f))
meshes=[obj for obj in bpy.data.objects if obj.type=="MESH" and obj.name.startswith("R11_")]
pat=re.compile(r"^R11_(cop_[a-z0-9_]+)__(balcony_slabs|glass_balustrades|metal_railings|cornices|roof_structures|service_units)(?:\.\d+)?$")
assert len(meshes)==qa["meshes"]==210,(len(meshes),qa["meshes"])
style_parts=set()
facets=0
for obj in meshes:
 m=pat.match(obj.name)
 assert m,("Bad semantic named renderer",obj.name)
 style_parts.add((m.group(1),m.group(2)))
 mesh=obj.data
 assert len(mesh.materials)==1 and mesh.materials[0] is not None,("Blank",obj.name)
 assert mesh.uv_layers.active is not None,("Missing UV0",obj.name)
 assert len(mesh.uv_layers.active.data)==len(mesh.loops)
 assert len(mesh.polygons)>0
 assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co),obj.name
 assert all(math.isfinite(v) for uv in mesh.uv_layers.active.data for v in uv.uv),obj.name
 facets+=len(mesh.polygons)
assert facets==qa["faces"]==306180
assert qa["real_osm_buildings_from_r8"]==1418 and qa["original_r7_detailed"]==50
assert qa["full_city_total"]==1468 and qa["map_length_coast_m"]==2000 and qa["map_inland_width_m"]==1000
assert qa["balconies"]==6048 and qa["roof_units"]==1414 and qa["cornices"]==1355
assert len(style_parts)==210
print("R11_NATIVE_REAL_FBX_REIMPORT_PASS",json.dumps({
 "batch_meshes":len(meshes),"polygons":facets,"balconies":qa["balconies"],
 "rooftops":qa["roof_units"],"cornices":qa["cornices"],"source_buildings":1468,
 "map_m":[2000,1000],"bytes":f.stat().st_size
}),flush=True)
