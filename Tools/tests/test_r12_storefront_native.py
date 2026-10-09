"""Independent Blender import: R12 shopfronts in true FBX 3D, UV/text materials."""
import bpy,hashlib,json,re,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
f=root/"UnityProject/Assets/Architecture/R12_Storefronts/R12_StreetLevel_1418_Entrances_Storefronts.fbx"
qa=json.loads((f.parent/"R12_STREETLEVEL_NATIVE_QA.json").read_text(encoding="utf-8"))
assert qa["fbx_sha256"]==hashlib.sha256(f.read_bytes()).hexdigest()
assert qa["coast_m"]==2000 and qa["inland_m"]==1000 and qa["osm_full_city"]==1468
assert qa["doors"]>1350 and qa["storefronts"]>=300
assert qa["fictional_sign_panels"]==qa["storefronts"]
art=json.loads((root/"ArtSource/Previews/R12_SignArt_QA.json").read_text(encoding="utf-8"))
assert art["count"]==12
for png in art["signs"]:
 p=root/png["path"]
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==png["sha256"]
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(f))
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(meshes)==qa["mesh_parts"]>17
assert sum(len(o.data.polygons) for o in meshes)==qa["mesh_faces"]
signs=[o for o in meshes if re.match(r"^R12_sign_\d\d",o.name)]
assert len(signs)>=9
for o in meshes:
 mesh=o.data
 assert len(mesh.materials)==1 and mesh.materials[0],o.name
 assert mesh.uv_layers.active and len(mesh.uv_layers.active.data)==len(mesh.loops),o.name
 assert len(mesh.vertices)>0 and len(mesh.polygons)>0
 assert all(math.isfinite(x) for v in mesh.vertices for x in v.co),o.name
 assert all(math.isfinite(x) for uv in mesh.uv_layers.active.data for x in uv.uv),o.name
for o in signs:
 uv=o.data.uv_layers.active.data
 assert all(-.00001<=c<=1.00001 for v in uv for c in v.uv),(o.name,"SIGN_ART_UV_BAD")
 assert all(len(poly.vertices)==4 for poly in o.data.polygons),(o.name,"SIGN_NOT_QUAD")
print("R12_NATIVE_STOREFRONT_FBX_REIMPORT_PASS",json.dumps({
 "meshes":len(meshes),"triangulation_faces":qa["mesh_faces"],
 "doors":qa["doors"],"stores":qa["storefronts"],
 "glass_showcases":qa["showcase_windows"],"sign_mesh_types":len(signs),
 "fbx_bytes":f.stat().st_size
}),flush=True)
