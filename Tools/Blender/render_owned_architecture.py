"""Render a REAL Blender QA contact sheet of eight project-owned coastal FBX buildings.

The input FBX is read directly from ArtSource/LocalProjectOwned (now on GitHub).
The display transforms are *preview only*; exported geographic/FBX files stay
byte-for-byte untouched. Not a Unity screenshot or art-direction approval.

Run: blender -b --factory-startup --python Tools/Blender/render_owned_architecture.py
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
OWNED = ROOT / "ArtSource/LocalProjectOwned/CoastalUrbanKit"
PREVIEW = ROOT / "ArtSource/Previews/Owned_CoastalUrbanKit_Blender_QA.png"
REPORT = ROOT / "ArtSource/Previews/Owned_CoastalUrbanKit_QA.json"
NAMES = (
    "casa_terrea", "sobrado", "loja", "misto",
    "apartamento", "hotel", "townhouse", "residencial_sacadas",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def material(name, color, metallic=0.0, roughness=0.7):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    principled = m.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1.0)
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return m


def box(name, location, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    bevel = o.modifiers.new("QA soft edge", "BEVEL")
    bevel.width = 0.065
    bevel.segments = 2
    o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o


def collect_world_bounds(meshes):
    low = [math.inf, math.inf, math.inf]
    high = [-math.inf, -math.inf, -math.inf]
    for obj in meshes:
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            for axis in range(3):
                low[axis] = min(low[axis], p[axis])
                high[axis] = max(high[axis], p[axis])
    return low, high


bpy.ops.wm.read_factory_settings(use_empty=True)
stone = material("QA_Studio_Dark_Stone", (0.155, 0.185, 0.205))
text_mat = material("QA_Studio_Label_Ivory", (0.89, 0.83, 0.70))
underlay = material("QA_Floor_Background", (0.21, 0.24, 0.27))

report = {
    "status": "PASS",
    "scope": "ORIGINAL_PROJECT_OWNED_FBX_BLENDER_REVIEW_NOT_UNITY",
    "studio": "Blender Cycles CPU original FBX meshes, layout-only scaling and placement",
    "asset_names_ordered": list(NAMES),
    "models": {},
}
sources_before = {name: sha256(OWNED / (name + ".fbx")) for name in NAMES}

for index, name in enumerate(NAMES):
    path = OWNED / (name + ".fbx")
    if not path.is_file() or path.stat().st_size < 12000:
        raise RuntimeError("Missing or suspicious source FBX: " + str(path))
    if path.read_bytes()[:18] != b"Kaydara FBX Binary":
        raise RuntimeError("Source must be an authentic binary FBX: " + name)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.import_scene.fbx(filepath=str(path))
    imported = list(bpy.context.selected_objects)
    meshes = [o for o in imported if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("FBX has no real geometry: " + name)
    nverts = sum(len(o.data.vertices) for o in meshes)
    nfaces = sum(len(o.data.polygons) for o in meshes)
    if nverts < 50 or nfaces < 20:
        raise RuntimeError("Inadequate geometry for studio QA: " + name)

    low, high = collect_world_bounds(meshes)
    dims = [high[k] - low[k] for k in range(3)]
    if min(dims) <= 0:
        raise RuntimeError("Flat/invalid geometry in FBX: " + name)
    materials = sorted({slot.material.name for o in meshes
                        for slot in o.material_slots if slot.material is not None})
    report["models"][name] = {
        "source": str(path.relative_to(ROOT)),
        "sha256": sources_before[name],
        "bytes": path.stat().st_size,
        "meshes": len(meshes),
        "vertices": nverts,
        "polygons": nfaces,
        "dimensions_from_imported_FBX_m": [round(d, 4) for d in dims],
        "materials": materials,
        "approval": "CANDIDATE_PENDING_REAL_UNITY_VISUAL_GATE",
    }

    # Preview-only fit: models may be 1- or multi-storey. Scale to contact sheet
    # *after* measuring original metric bounds. Do NOT export modified models.
    display_scale = min(7.4 / dims[0], 5.3 / dims[1], 5.7 / dims[2], 1.6)
    # Arrange as a 4-column x 2-row architectural studio contact sheet.
    studio_x = (index % 4 - 1.5) * 9.1
    studio_y = (index // 4 - 0.5) * 11.1
    center = Vector(((low[0]+high[0])*.5, (low[1]+high[1])*.5, low[2]))
    transform = (
        Matrix.Translation(Vector((studio_x, studio_y, 0.18)))
        @ Matrix.Scale(display_scale, 4)
        @ Matrix.Translation(-center)
    )
    for obj in meshes:
        world = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = transform @ world
        for slot in obj.material_slots:
            if slot.material and not slot.material.use_nodes:
                m = slot.material
                m.use_nodes = True
                node = m.node_tree.nodes.get("Principled BSDF")
                if node:
                    node.inputs["Base Color"].default_value = m.diffuse_color
                    node.inputs["Roughness"].default_value = 0.58
    report["models"][name]["studio_scale_preview_only"] = round(display_scale, 6)

    box("QA_PEDASTAL_"+name, (studio_x, studio_y, -0.10),
        (8.4, 8.9, 0.25), stone)
    # Labels are display-only; independent of FBX and Unity geometry.
    bpy.ops.object.text_add(location=(studio_x-3.6, studio_y-4.18, 0.075),
                            rotation=(math.pi/2, 0, 0))
    label = bpy.context.object
    label.data.body = name.replace("_", " ").upper()
    label.data.size = 0.38
    label.data.materials.append(text_mat)

# Verify that the imported assets were never modified.
for name, before in sources_before.items():
    if sha256(OWNED / (name+".fbx")) != before:
        raise RuntimeError("A source FBX was modified: " + name)

box("QA_STUDIO_FLOOR", (0, 0, -0.42), (42, 23, 0.35), underlay)
world = bpy.data.worlds.new("QA_Environment")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.48, 0.60, 0.73, 1)
bg.inputs["Strength"].default_value = 0.7

def area_light(name, xyz, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = xyz
    direction = Vector((0, 0, 0)) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

area_light("QA Key Softbox", (-12, -9, 17), 4200, 13)
area_light("QA Fill", (17, 5, 12), 2100, 11)
sun_data = bpy.data.lights.new("QA Sun", "SUN")
sun_data.energy = 1.5
sun = bpy.data.objects.new("QA Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(38), -0.1, math.radians(-25))

camera_data = bpy.data.cameras.new("QA Studio Camera")
camera = bpy.data.objects.new("QA Studio Camera", camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (15, -30, 27)
target = Vector((0, 0, 1.65))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 46
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.cycles.use_denoising = False
bpy.context.view_layer.cycles.use_denoising = False
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW)
scene.render.film_transparent = False
if hasattr(scene.view_settings, "view_transform"):
    scene.view_settings.view_transform = "AgX"
PREVIEW.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.render.render(write_still=True)
if not PREVIEW.is_file() or PREVIEW.stat().st_size < 40000:
    raise RuntimeError("Blender did not produce valid real render")

report["preview"] = str(PREVIEW.relative_to(ROOT))
report["preview_sha256"] = sha256(PREVIEW)
report["preview_bytes"] = PREVIEW.stat().st_size
report["original_map_untouched"] = (
    (ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").is_file()
    and (ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").is_file()
)
if not report["original_map_untouched"]:
    raise RuntimeError("Original Copacabana map unexpectedly missing")
report["copyright"] = "User-owned originals; any separate reference textures require independent license review"
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("REAL BLENDER COASTAL ARCHITECTURE QA:", json.dumps({
    "models": len(report["models"]), "preview": report["preview"],
    "hash": report["preview_sha256"],
    "polygons": {k: v["polygons"] for k,v in report["models"].items()},
}, ensure_ascii=False))
