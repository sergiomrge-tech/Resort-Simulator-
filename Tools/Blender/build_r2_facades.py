"""Resort Simulator R2 — 3 modular facade prototypes, Blender procedural PBR.

Distinct architectural families inspired by Copacabana, not copied facades:
  Art Deco hotel, residential balconies, contemporary beachfront hotel.
No existing GIS building or road is removed/replaced by this script.
This is a PROTOTYPE, not the final art approval or a Unity screenshot.

Run: blender -b --factory-startup --python Tools/Blender/build_r2_facades.py
"""
from __future__ import annotations
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "UnityProject/Assets/Architecture/R2_Prototypes"
PREV = ROOT / "ArtSource/Previews"
DEST.mkdir(parents=True, exist_ok=True)
PREV.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
material_cache = {}

def pbr(name, rgba, metallic=0.0, roughness=0.55):
    if name in material_cache:
        return material_cache[name]
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = tuple(rgba)  # FBX material preview fallback
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    material_cache[name] = mat
    return mat

SAND = pbr("R2_Calcario_Areia", (0.72, 0.63, 0.47, 1), roughness=0.68)
IVORY = pbr("R2_Reboco_Marfim", (0.86, 0.83, 0.72, 1), roughness=0.79)
CREAM = pbr("R2_Concreto_Quente", (0.71, 0.68, 0.59, 1), roughness=0.70)
GLASS = pbr("R2_Vidro_Azul_Fumê", (0.12, 0.27, 0.34, 1), metallic=0.20, roughness=0.12)
GLASS_DARK = pbr("R2_Vidro_Cinza_Dark", (0.09, 0.16, 0.19, 1), metallic=0.29, roughness=0.12)
BRASS = pbr("R2_Metal_Bronze", (0.47, 0.31, 0.12, 1), metallic=0.87, roughness=0.26)
ALUMINUM = pbr("R2_Aluminio_Escuro", (0.14, 0.15, 0.16, 1), metallic=0.81, roughness=0.34)
WOOD = pbr("R2_Madeira_Tropical", (0.32, 0.18, 0.095, 1), roughness=0.53)
TERRACOTTA = pbr("R2_Ceramica_Terracota", (0.42, 0.20, 0.13, 1), roughness=0.55)
PLANT = pbr("R2_Folhagem_Premium", (0.11, 0.26, 0.15, 1), roughness=0.76)
CONCRETE = pbr("R2_Concreto_Cinza_Calma", (0.38, 0.40, 0.39, 1), roughness=0.70)
GROUND = pbr("QA_Piso_Exposicao", (0.26, 0.29, 0.31, 1), roughness=0.84)

members = {}
current = None

def part(name, x, y, z, w, depth, height, material, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    obj = bpy.context.object
    obj.name = f"{current}_{name}" if current else name
    obj.dimensions = (w, depth, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Soft_edges_realism", "BEVEL")
        mod.width = min(bevel, w * 0.15, depth * 0.3, height * 0.15)
        mod.segments = 2
        obj.modifiers.new("Weighted_normals", "WEIGHTED_NORMAL")
    if current:
        members[current].append(obj)
    return obj

def sphere(name, x, y, z, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=radius, location=(x, y, z))
    obj = bpy.context.object
    obj.name = f"{current}_{name}"
    obj.data.materials.append(mat)
    members[current].append(obj)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj

def window(name, x, z, w, h, frame, glass=GLASS, y=-0.16):
    part(name+"_glass", x, y-0.022, z, w, 0.045, h, glass, 0.012)
    thickness = 0.085
    part(name+"_L", x-w/2, y-0.085, z, thickness, 0.105, h+0.11, frame)
    part(name+"_R", x+w/2, y-0.085, z, thickness, 0.105, h+0.11, frame)
    part(name+"_top", x, y-0.085, z+h/2, w+0.10, 0.105, thickness, frame)
    part(name+"_bottom", x, y-0.085, z-h/2, w+0.12, 0.11, thickness, frame)
    part(name+"_transom", x, y-0.105, z+h*0.16, w, 0.08, 0.055, frame)
    part(name+"_mullion", x, y-0.11, z, 0.05, 0.07, h, frame)

def start(name):
    global current
    current = name
    members[name] = []

def art_deco():
    start("R2_ArtDeco_Orla")
    part("fachada_marfim", 0, 0.10, 1.78, 6.6, 0.44, 3.56, IVORY, 0.04)
    part("rodape_pedra", 0, -0.16, 0.17, 6.7, 0.17, 0.34, SAND)
    for x in (-2.75, 0.0, 2.75):
        part(f"pilastra_{x}", x, -0.19, 1.74, 0.36, 0.32, 3.3, SAND)
        for offset in (-0.07, 0.07):
            part(f"canelura_{x}_{offset}", x+offset, -0.367, 1.76, 0.022, 0.022, 2.95, BRASS, 0.003)
    for x in (-1.38, 1.38):
        window(f"janela_alta_{x}", x, 1.84, 1.43, 2.17, BRASS, GLASS_DARK)
        part(f"peitoril_esculpido_{x}", x, -0.34, 0.59, 1.72, 0.28, 0.16, SAND)
    part("moldura_superior", 0, -0.20, 3.35, 6.85, 0.43, 0.21, SAND, 0.03)
    part("friso_bronze", 0, -0.38, 3.19, 6.8, 0.07, 0.035, BRASS, 0.01)
    for x in (-2.70, -2.46, 2.46, 2.70):
        part(f"degrau_friso_{x}", x, -0.34, 3.46, 0.10, 0.09, 0.14, BRASS)

def residencial():
    start("R2_Residencial_Varandas")
    part("fachada_concreto", 0, 0.13, 1.71, 6.4, 0.44, 3.42, CREAM, 0.035)
    for x in (-2.7, 2.7):
        part(f"estrutura_lateral_{x}", x, -0.14, 1.76, 0.28, 0.28, 3.50, IVORY)
    part("porta_de_correr", 0, -0.18, 1.65, 4.35, 0.06, 2.70, GLASS)
    for x in (-2.2, -1.1, 0.0, 1.1, 2.2):
        part(f"caixilho_vertical_{x}", x, -0.255, 1.69, 0.075, 0.115, 2.77, ALUMINUM)
    part("verga_porta", 0, -0.27, 3.02, 4.5, 0.12, 0.12, ALUMINUM)
    part("laje_varanda", 0, -0.78, 0.69, 5.60, 1.50, 0.23, IVORY, 0.04)
    part("acabamento_laje", 0, -1.48, 0.69, 5.66, 0.12, 0.18, SAND)
    for x in [round(-2.65 + i*0.265, 3) for i in range(21)]:
        part(f"gradil_{x}", x, -1.51, 1.14, 0.037, 0.065, 0.76, ALUMINUM, 0.006)
    part("corrimao_bronze", 0, -1.52, 1.56, 5.54, 0.14, 0.085, BRASS)
    for x in (-2.1, 2.1):
        part(f"jardineira_{x}", x, -1.12, 1.00, 0.76, 0.52, 0.25, TERRACOTTA)
        for shift in (-0.18, 0.0, 0.18):
            sphere(f"folhagem_{x}_{shift}", x+shift, -1.14, 1.26, 0.18, PLANT)
    part("forro_amadeirado", 0, -0.76, 3.30, 5.55, 1.37, 0.12, WOOD)

def hotel():
    start("R2_Hotel_Contemporaneo")
    part("estrutura_terreo", 0, 0.15, 1.76, 7.0, 0.5, 3.52, TERRACOTTA, 0.045)
    part("vidro_fachada", 0, -0.19, 1.82, 5.9, 0.085, 2.93, GLASS_DARK)
    for x in (-3.08, -2.36, -1.18, 0.0, 1.18, 2.36, 3.08):
        part(f"mullion_aluminio_{x}", x, -0.34, 1.84, 0.095, 0.14, 3.04, ALUMINUM)
    for z in (0.42, 1.42, 2.40, 3.18):
        part(f"travessa_{z}", 0, -0.33, z, 6.25, 0.15, 0.095, ALUMINUM)
    part("marquise_horizontal", 0, -0.60, 3.28, 7.2, 1.0, 0.15, IVORY, 0.05)
    part("filete_marquise", 0, -1.12, 3.19, 7.15, 0.06, 0.055, BRASS)
    for i, x in enumerate((-2.62, -1.32, 1.32, 2.62)):
        part(f"brise_vertical_{i}", x, -0.67, 1.89, 0.15, 0.63, 2.72, WOOD, 0.02)
        for z in (0.61, 0.94, 1.27, 1.60, 1.93, 2.26, 2.59, 2.92):
            part(f"brise_travessa_{i}_{z}", x, -0.97, z, 0.30, 0.075, 0.035, BRASS)
    part("base_pedra", 0, -0.17, 0.14, 7.15, 0.17, 0.28, CONCRETE)
    part("totem_lateral", 3.24, -0.44, 1.89, 0.21, 0.38, 2.70, BRASS)

art_deco()
residencial()
hotel()

def metrics(objects):
    verts = 0
    faces = 0
    used = set()
    for obj in objects:
        verts += len(obj.data.vertices)
        faces += len(obj.data.polygons)
        used.update(slot.material.name for slot in obj.material_slots if slot.material)
    return {"objects": len(objects), "vertices": verts, "faces": faces, "materials": sorted(used)}

def sha256(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()

report = {"status": "PASS", "scope": "BLENDER_R2_PROTOTYPE_NOT_UNITY", "modules": {}}
for name, objects in members.items():
    stats = metrics(objects)
    if stats["objects"] < 18 or stats["faces"] < 120 or len(stats["materials"]) < 4:
        raise RuntimeError(f"{name} generic prototype rejected: {stats}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    path = DEST / (name + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={"MESH"},
        axis_forward="-Z", axis_up="Y", global_scale=1.0,
        apply_unit_scale=True, bake_space_transform=False,
        use_mesh_modifiers=True, path_mode="AUTO", add_leaf_bones=False)
    if not path.exists() or path.stat().st_size < 12000:
        raise RuntimeError(f"{name}: export incomplete")
    stats["fbx_bytes"] = path.stat().st_size
    stats["sha256"] = sha256(path)
    stats["path"] = str(path.relative_to(ROOT))
    report["modules"][name] = stats

# Studio arrangement exists ONLY for a genuine Blender preview; exported FBX origins stay local.
for index, (_, objects) in enumerate(members.items()):
    delta = (index - 1) * 10.6
    for obj in objects:
        obj.location.x += delta
for x in (-10.6, 0.0, 10.6):
    current = None
    part(f"QA_BASE_{x}", x, -0.5, -0.19, 8.8, 4.0, 0.34, GROUND, 0.08)

world = bpy.data.worlds.new("R2_Studio_Sky")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.64, 0.72, 0.82, 1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
light_data = bpy.data.lights.new("QA_Area_softbox", "AREA")
light_obj = bpy.data.objects.new("QA_Area_softbox", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-5, -8, 14)
light_data.energy = 2400
light_data.shape = "DISK"
light_data.size = 10.0
sun_data = bpy.data.lights.new("QA_Sun_rim", "SUN")
sun_obj = bpy.data.objects.new("QA_Sun_rim", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(34), math.radians(-20), math.radians(-28))
sun_data.energy = 1.4

camera_data = bpy.data.cameras.new("QA_Camera")
camera = bpy.data.objects.new("QA_Camera", camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (0, -32, 13)
target = Vector((0, -0.45, 1.5))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 36
bpy.context.scene.camera = camera

scene = bpy.context.scene
# Cycles CPU works in a GitHub headless runner without a GPU/GUI.
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.cycles.use_denoising = False
bpy.context.view_layer.cycles.use_denoising = False
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREV / "Resort_R2_Fachadas_Premium_Blender_QA.png")
scene.view_settings.view_transform = "AgX"
scene.camera.data.lens = 50
scene.render.film_transparent = False
bpy.ops.render.render(write_still=True)
image = Path(scene.render.filepath)
if image.stat().st_size < 30000:
    raise RuntimeError("Rendered preview unexpectedly small")
report["preview_png"] = str(image.relative_to(ROOT))
report["preview_sha256"] = sha256(image)
report["render_engine"] = "Blender Cycles CPU (real Blender render, not Unity)"
report["style"] = "realismo estilizado premium — prototypes, not approved final assets"
report["copyright"] = "Original architecture; does not incorporate third-party textures"
qa = PREV / "Resort_R2_Fachadas_Premium_QA.json"
qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("R2 BLENDER PROTOTYPES VALIDATED:", json.dumps(report, ensure_ascii=False))
