"""Rebuild and export the *original authored* detailed Project Resort kiosk, cloud-only.

Source of truth is ArtSource/LocalProjectOwned/KioskPremium_20261008/build_kiosk_premium.py.
Run in Blender 4+ headless. The authored script was originally written for absolute
Windows D: paths: this wrapper replaces only the two output roots in memory.
No external models or textures, no PC dependencies, no fake Unity screenshots.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ArtSource/LocalProjectOwned/KioskPremium_20261008/build_kiosk_premium.py"
SOURCE_JSON = ROOT / "ArtSource/LocalProjectOwned/KioskPremium_20261008/SOURCE.json"
WORK = ROOT / "build/kiosk_cloud"
WORK_FACILITY = WORK / "simulador_stub"
WORK_SOURCE = WORK / "original_kiosk"
FBX = ROOT / "UnityProject/Assets/Architecture/OwnedKiosk/KioskPremium_Detailed.fbx"
PNG = ROOT / "ArtSource/Previews/Owned_KioskPremium_Blender_QA.png"
REPORT = ROOT / "ArtSource/Previews/Owned_KioskPremium_QA.json"

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def guid_for(path):
    return hashlib.sha256(
        ("resort-premium-kiosk-original/"+path.relative_to(ROOT).as_posix()).encode("utf-8")
    ).hexdigest()[:32]

def metadata(path, is_folder=False):
    guid = guid_for(path)
    content = ("fileFormatVersion: 2\n"
               + "guid: " + guid + "\n"
               + ("folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n"
                  if is_folder else
                  "ModelImporter:\n  serializedVersion: 22200\n  externalObjects: {}\n"))
    meta = Path(str(path)+".meta")
    if meta.exists() and "guid: "+guid not in meta.read_text():
        raise RuntimeError("Existing kiosk Unity GUID changed unexpectedly")
    meta.write_text(content, encoding="utf-8")
    return guid


def regenerate_original():
    source = SOURCE.read_text(encoding="utf-8")
    original_root = "root=Path('D:/sergi/Documents/Simulador-predial/FacilityOps')"
    original_lib = "lib=Path('D:/ProjectResort_AssetLibrary/ProjectOwned/KioskPremium_20261008');lib.mkdir(parents=True,exist_ok=True)"
    assert source.count(original_root) == 1
    assert source.count(original_lib) == 1
    workroot = WORK_FACILITY.as_posix()
    worklib = WORK_SOURCE.as_posix()
    safe = source.replace(original_root, "root=Path("+repr(workroot)+")")
    safe = safe.replace(original_lib, "lib=Path("+repr(worklib)+");lib.mkdir(parents=True,exist_ok=True)")
    if "D:/sergi/" in safe or "D:/ProjectResort" in safe:
        raise RuntimeError("Unmapped local desktop path remains in kiosk script")
    (WORK_FACILITY/"Assets/_Game/Resources/Art/Resort/Props").mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # The script was authored and preserved by the owner; not an arbitrary
    # downloaded executable. Its exact SHA is recorded for provenance.
    exec(compile(safe, str(SOURCE), "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})
    generated = WORK_FACILITY/"Assets/_Game/Resources/Art/Resort/Props/KioskShellF02.fbx"
    info = json.loads((WORK_SOURCE/"SOURCE.json").read_text())
    if not generated.is_file():
        raise RuntimeError("Original kiosk authoring script did not generate FBX")
    return generated, info


def material_color(mat, rgb, metal=0, rough=0.6):
    mat.diffuse_color=(*rgb,1)
    mat.use_nodes=True
    principled=mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value=(*rgb,1)
    principled.inputs["Metallic"].default_value=metal
    principled.inputs["Roughness"].default_value=rough


generated, generated_info = regenerate_original()
expected = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
if generated_info["components"] != expected["components"]:
    raise RuntimeError("Original kiosk components changed: "+str(generated_info))
if generated_info["triangles"] < 50000 or generated_info["polygons"] < 20000:
    raise RuntimeError("Kiosk is not detailed enough to qualify as original")
if not generated.read_bytes().startswith(b"Kaydara FBX Binary"):
    raise RuntimeError("Blender did not generate binary FBX")

FBX.parent.mkdir(parents=True,exist_ok=True)
FBX.write_bytes(generated.read_bytes())
metadata(FBX.parent,True)
guid=metadata(FBX)

# Render ACTUAL geometry re-opened from the original authored .blend,
# containing 307 independent objects before optimized FBX join.
bpy.ops.wm.open_mainfile(filepath=str(WORK_SOURCE/"KioskPremium.blend"))
palette = {
    "Kiosk_Wood": ((0.32, 0.18, 0.095), 0, 0.48),
    "Kiosk_Plaster": ((0.80, 0.75, 0.66), 0, 0.78),
    "Kiosk_Stone": ((0.47, 0.42, 0.33), 0, 0.48),
    "Kiosk_Metal": ((0.18, 0.20, 0.22), 0.65, 0.36),
    "Kiosk_Steel": ((0.38, 0.40, 0.41), 0.72, 0.26),
    "Kiosk_Roof": ((0.17, 0.21, 0.22), 0.23, 0.6),
    "Kiosk_Ceramic": ((0.75, 0.69, 0.57), 0.03, 0.33),
}
for name,(rgb,metal,rough) in palette.items():
    mat=bpy.data.materials.get(name)
    if mat is None:
        raise RuntimeError("Original kiosk missing expected material: "+name)
    material_color(mat,rgb,metal,rough)

# Only a neutral studio floor/lighting is appended; not original FBX geometry.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-2.5,-0.25))
floor=bpy.context.object
floor.name="QA_STUDIO_FLOOR_NOT_GAME_ASSET"
floor.dimensions=(24,21,.45)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
m=bpy.data.materials.new("QA_Studio_Dark")
material_color(m,(.17,.20,.22),0,.75)
floor.data.materials.append(m)

world=bpy.data.worlds.new("QA_Kiosk_Sky")
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.56,.68,.80,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.85

for name,location,energy,size in (
    ("QA_Key_Area", (-12,16,18),3300,11),
    ("QA_Fill_Area", (14,3,12),1850,9),
):
    ld=bpy.data.lights.new(name,"AREA")
    ld.energy=energy
    ld.shape="DISK"
    ld.size=size
    obj=bpy.data.objects.new(name,ld)
    bpy.context.collection.objects.link(obj)
    obj.location=location
    target=Vector((0,-2,1.5))-obj.location
    obj.rotation_euler=target.to_track_quat("-Z","Y").to_euler()
sun_data=bpy.data.lights.new("QA_Sun","SUN")
sun_data.energy=1.4
sun=bpy.data.objects.new("QA_Sun",sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler=(math.radians(45), -.30, math.radians(-30))

cam_data=bpy.data.cameras.new("QA_Camera")
cam=bpy.data.objects.new("QA_Camera",cam_data)
bpy.context.collection.objects.link(cam)
cam.location=(19,22,14)
cam.rotation_euler=(Vector((0,-2,1.55))-cam.location).to_track_quat("-Z","Y").to_euler()
cam_data.type="ORTHO"
cam_data.ortho_scale=29
bpy.context.scene.camera=cam

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=16
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(PNG)
scene.render.film_transparent=False
if hasattr(scene.view_settings,"view_transform"):
    scene.view_settings.view_transform="AgX"
PNG.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.render.render(write_still=True)
if PNG.stat().st_size < 35000:
    raise RuntimeError("Rendered Blender kiosk preview is unexpectedly small")
source_count=sum(1 for o in scene.objects if o.type=="MESH" and o.name!="QA_STUDIO_FLOOR_NOT_GAME_ASSET")
if source_count != expected["components"]:
    raise RuntimeError("Original detailed kiosk object count was not preserved in .blend")

report={
    "status":"PASS",
    "scope":"REBUILT_FROM_PROJECT_OWNED_AUTHORING_CODE_BLENDER_NOT_UNITY",
    "source_script":str(SOURCE.relative_to(ROOT)),
    "source_script_sha256":hash_file(SOURCE),
    "archived_original_blend": "ArtSource/LocalProjectOwned/KioskPremium_20261008/KioskPremium.blend",
    "source_components":source_count,
    "polygons":generated_info["polygons"],
    "triangles":generated_info["triangles"],
    "unity_fbx":str(FBX.relative_to(ROOT)),
    "unity_fbx_sha256":hash_file(FBX),
    "unity_fbx_bytes":FBX.stat().st_size,
    "unity_fbx_guid":guid,
    "preview":str(PNG.relative_to(ROOT)),
    "preview_sha256":hash_file(PNG),
    "preview_bytes":PNG.stat().st_size,
    "render_engine":"Blender Cycles CPU; source geometry, preview-specific materials",
    "limits":"FBX staged, not Unity compiled/imported, not attached to Copacabana world, visual approval pending",
    "license":"Original author-made kiosk; PBR runtime texture assets not transferred or approved in this render"
}
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("ORIGINAL_PREMIUM_KIOSK_BLENDER_QA:",json.dumps({
    "components":source_count,"polygons":generated_info["polygons"],
    "triangles":generated_info["triangles"],"fbx_sha":report["unity_fbx_sha256"],
    "preview_sha":report["preview_sha256"]},ensure_ascii=False))
