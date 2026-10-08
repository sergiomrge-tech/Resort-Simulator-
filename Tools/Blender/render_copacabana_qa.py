"""Render REAL, existing Copacabana Blender geometry from its actual extent.

This script never invents buildings. The existing .blend is the sole geometric
source. Renders only a QA blockout, not a finished gameplay screenshot.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "ArtSource" / "Previews"
OUTDIR.mkdir(parents=True, exist_ok=True)
source = ROOT / "ArtSource" / "Blender" / "Copacabana_BlenderGIS_UTM23S.blend"
if not source.exists():
    raise FileNotFoundError(f"Original Blender map not found: {source}")

scene = bpy.context.scene
meshes = [obj for obj in scene.objects if obj.type == "MESH" and obj.data and
          len(obj.data.vertices) > 0]
if not meshes:
    raise RuntimeError("NO REAL OSM MESH in Blender scene: previous gray preview is invalid.")

# Depend on world-space geometry bounds. Do not assume origin, rotation or scale.
allbounds = []
records = []
total_vertices = 0
total_faces = 0
for obj in meshes:
    obj.hide_render = False
    world = obj.matrix_world
    allbounds.extend(world @ Vector(corner) for corner in obj.bound_box)
    total_vertices += len(obj.data.vertices)
    total_faces += len(obj.data.polygons)
    records.append({
        "name": obj.name, "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "materials": [m.name if m else None for m in obj.data.materials],
        "location": [round(v, 2) for v in world.translation]
    })
if total_faces < 500:
    raise RuntimeError(f"Geometry incomplete: only {total_faces} faces.")
minimum = Vector(tuple(min(v[i] for v in allbounds) for i in range(3)))
maximum = Vector(tuple(max(v[i] for v in allbounds) for i in range(3)))
center = (minimum + maximum) * .5
dims = maximum - minimum
if not 200 < max(dims.x, dims.y) < 20000:
    raise RuntimeError(f"Unexpected geometry extents: {tuple(dims)}")

print("GEOMETRY_BOUNDS", tuple(round(v, 2) for v in minimum),
      tuple(round(v, 2) for v in maximum), flush=True)
print("GEOMETRY_COUNT", len(meshes), total_vertices, total_faces, flush=True)

# Use actual mesh material assignments. Colors are only visual identification.
for obj in meshes:
    for material in obj.data.materials:
        if not material:
            continue
        name = material.name.lower()
        if "road" in name:
            tint = (0.37, 0.45, 0.55, 1)
        elif "land" in name or "beach" in name:
            tint = (0.31, 0.48, 0.37, 1)
        else:
            tint = (0.84, 0.67, 0.48, 1)
        material.diffuse_color = tint
        material.use_nodes = True
        node = material.node_tree.nodes.get("Principled BSDF")
        if node:
            node.inputs["Base Color"].default_value = tint
            node.inputs["Roughness"].default_value = .88

# Supporting surfaces only: not buildings, not claimed as OSM geometry.
# A contrasting plain ground makes roadlines and extruded buildings readable.
ground_z = minimum.z - 0.8
bpy.ops.mesh.primitive_cube_add(size=1, location=(
    center.x, center.y, ground_z - .5))
ground = bpy.context.object
ground.name = "TEMP_QA_GROUND_NOT_DEM"
ground.dimensions = (dims.x + 160, dims.y + 160, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
ground_material = bpy.data.materials.new("QA_background_ground_not_real")
ground_material.diffuse_color = (0.16, 0.25, 0.27, 1)
ground_material.use_nodes = True
p = ground_material.node_tree.nodes.get("Principled BSDF")
if p:
    p.inputs["Base Color"].default_value = (0.16, 0.25, 0.27, 1)
ground.data.materials.append(ground_material)

# Fresh QA camera; no dependence on stale Blender saved camera.
cam_data = bpy.data.cameras.new("QA_AERIAL_CAMERA")
cam = bpy.data.objects.new("QA_AERIAL_CAMERA", cam_data)
scene.collection.objects.link(cam)
cam.location = center + Vector((-0.50*dims.x, -0.95*dims.y,
                                 max(dims.x, dims.y)*1.15))
target = center + Vector((0, 0, -min(0, dims.z*.15)))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
cam_data.type = "ORTHO"
cam_data.ortho_scale = max(dims.x, dims.y)*1.65
cam_data.clip_end = max(dims.x, dims.y)*10
scene.camera = cam

light_data = bpy.data.lights.new("QA_Daylight",type="SUN")
light_object = bpy.data.objects.new("QA_Daylight",light_data)
scene.collection.objects.link(light_object)
light_object.rotation_euler = (math.radians(38), math.radians(-25), math.radians(-18))
light_data.energy = 1.15

world = bpy.data.worlds.new("QA_DaySky")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (.62,.74,.84,1)
bg.inputs["Strength"].default_value = .35
scene.render.engine = "CYCLES"
scene.cycles.samples = 12
scene.cycles.use_denoising = False
bpy.context.view_layer.cycles.use_denoising = False
scene.render.resolution_x = 1600
scene.render.resolution_y = 950
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = str(OUTDIR / "Copacabana_REAL_BLOCO_3D_QA_COLOR.png")
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0
bpy.ops.render.render(write_still=True)

report = {
    "source_blend": str(source.relative_to(ROOT)),
    "osm_based_geometry": True,
    "is_real_blender_render": True,
    "is_final_gameplay": False,
    "is_final_art": False,
    "blender_mesh_objects": len(meshes),
    "vertices": total_vertices,
    "faces": total_faces,
    "bbox_min": list(minimum),
    "bbox_max": list(maximum),
    "camera_location": list(cam.location),
    "camera_target": list(target),
    "materials_note": "Colors adapted for QA readability; original OSM geometry unchanged.",
    "objects": records[:40],
    "license": "© OpenStreetMap contributors; ODbL 1.0",
}
(OUTDIR / "Copacabana_QA_report.json").write_text(
    json.dumps(report, indent=2,ensure_ascii=False),encoding="utf8")
print("RENDER_SAVED", scene.render.filepath, flush=True)
