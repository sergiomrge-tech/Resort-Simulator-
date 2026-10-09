"""Author a compact tropical vegetation kit and true Blender QA render.

Run with Blender's Python (bpy) or ``python -c 'import bpy,runpy; ...'``.
All plant forms are authored as custom curved/tapered meshes; no third-party
models, textures, plug-ins, or source-map files are used.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ArtSource/Vegetation/R6"
PREVIEW = ROOT / "ArtSource/Previews/R6_Vegetation_Kit_Blender.png"
REPORT = OUT / "R6_VEGETATION_KIT_REPORT.json"
SPECIES = ("palmeira_copacabana", "arvore_tropical_ampla", "arvore_tropical_densa", "arbusto_tropical")
LOD_FACTORS = {"LOD0": 1.0, "LOD1": 0.55, "LOD2": 0.25}


def color(hex_value):
    value = hex_value.lstrip("#")
    srgb = [int(value[i:i+2], 16)/255.0 for i in (0, 2, 4)]
    return tuple((v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4) for v in srgb) + (1.0,)


def material(name, hex_value, roughness=0.76, subsurface=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color(hex_value)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color(hex_value)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    return mat


def append_tube(verts, faces, points, radii, sides=8):
    """Smooth tapered curved tube generated from a centerline."""
    pts = [Vector(p) for p in points]
    base = len(verts)
    for i, point in enumerate(pts):
        tangent = (pts[min(i+1, len(pts)-1)] - pts[max(0, i-1)]).normalized()
        ref = Vector((0, 0, 1)) if abs(tangent.z) < 0.92 else Vector((1, 0, 0))
        u = tangent.cross(ref).normalized()
        v = tangent.cross(u).normalized()
        for j in range(sides):
            a = 2*math.pi*j/sides
            pos = point + radii[i]*(math.cos(a)*u + math.sin(a)*v)
            verts.append(tuple(pos))
    for i in range(len(pts)-1):
        for j in range(sides):
            a = base+i*sides+j
            b = base+i*sides+(j+1)%sides
            faces.append((a, b, b+sides, a+sides))
    faces.append(tuple(base+j for j in range(sides-1, -1, -1)))
    top = base+(len(pts)-1)*sides
    faces.append(tuple(top+j for j in range(sides)))


def append_leaf(verts, faces, start, end, width, bend, segments=8):
    """Lanceolate leaf with a curved midrib, raised central ridge and taper."""
    s, e = Vector(start), Vector(end)
    axis = e-s
    if axis.length < 1e-5:
        return
    axis.normalize()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.94 else Vector((1, 0, 0))
    side = axis.cross(ref).normalized()
    base = len(verts)
    for i in range(segments+1):
        t = i/segments
        center = s.lerp(e, t) + Vector(bend)*(t*t)
        shape = (math.sin(math.pi*t)**0.72) * width
        ridge = Vector((0, 0, 0.045*math.sin(math.pi*t)))
        verts.extend((tuple(center-side*shape), tuple(center+ridge), tuple(center+side*shape)))
    for i in range(segments):
        a = base+i*3
        b = a+3
        faces.extend(((a, b, b+1, a+1), (a+1, b+1, b+2, a+2)))


def make_mesh_object(name, verts, faces, mats, collection):
    mesh = bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def palm_mesh(name, lod, collection, bark, leaf, seed):
    rng = random.Random(seed)
    scale = LOD_FACTORS[lod]
    levels = max(5, round(10*scale))
    trunk_v, trunk_f, trunk_path = [], [], []
    for i in range(levels+1):
        t = i/levels
        trunk_path.append((0.10*math.sin(t*1.2), 0.025*math.sin(t*2.5), 0.10+5.0*t))
    append_tube(trunk_v, trunk_f, trunk_path, [0.38*(1-t)**0.55+0.11 for t in [i/levels for i in range(levels+1)]], sides=max(6, round(10*scale)))
    verts, faces = trunk_v, trunk_f
    fronds = max(5, round(13*scale))
    segments = max(5, round(9*scale))
    for i in range(fronds):
        angle = 2*math.pi*i/fronds + rng.uniform(-0.08, 0.08)
        root = Vector((0.1*math.sin(1.2), 0, 4.85))
        length = rng.uniform(2.3, 3.0)
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        end = root + radial*length + Vector((0, 0, rng.uniform(-1.35, -0.5)))
        append_leaf(verts, faces, root, end, 0.23*scale+0.12, (0, 0, -0.8), segments)
        # Fine paired leaflets create the characteristic feathered palm silhouette.
        for j in range(1, max(4, round(10*scale))):
            t = j/max(4, round(10*scale))
            center = root.lerp(end, t)
            span = 0.55*math.sin(math.pi*t)
            for side_sign in (-1, 1):
                leaflet_end = center + Vector((-radial.y, radial.x, 0))*span*side_sign + Vector((0, 0, -0.16))
                append_leaf(verts, faces, center, leaflet_end, 0.055*scale+0.018, (0, 0, -0.035), max(3, segments//2))
    obj = make_mesh_object(name, verts, faces, [bark, leaf], collection)
    # Keep trunk faces on the bark and all blade faces on leaf material.
    trunk_face_count = len(trunk_f)
    for poly in obj.data.polygons[trunk_face_count:]:
        poly.material_index = 1
    for poly in obj.data.polygons[:trunk_face_count]:
        poly.material_index = 0
    return obj


def broadleaf_mesh(name, lod, collection, bark, leaves, dense, seed):
    rng = random.Random(seed)
    scale = LOD_FACTORS[lod]
    verts, faces, trunk_faces = [], [], 0
    trunk_levels = max(5, round(9*scale))
    trunk_points = []
    for i in range(trunk_levels+1):
        t = i/trunk_levels
        trunk_points.append((0.10*math.sin(t*2.0), 0.07*math.sin(t*3), 0.12+3.5*t))
    append_tube(verts, faces, trunk_points, [0.29*(1-i/trunk_levels)**0.7+0.055 for i in range(trunk_levels+1)], sides=max(6, round(9*scale)))
    trunk_faces = len(faces)
    branch_count = max(4, round((7 if dense else 6)*scale))
    for i in range(branch_count):
        angle = (i/branch_count)*2*math.pi + rng.uniform(-0.23, 0.23)
        z = rng.uniform(2.0, 3.25)
        reach = rng.uniform(0.9, 1.55) * (1.2 if dense else 1.0)
        points = [(0.08*math.sin(z/3.5), 0.04, z),
                  (math.cos(angle)*reach*0.42, math.sin(angle)*reach*0.42, z+0.34),
                  (math.cos(angle)*reach, math.sin(angle)*reach, z+0.75)]
        append_tube(verts, faces, points, [0.105, 0.072, 0.032], sides=max(5, round(7*scale)))
    woody_faces = len(faces)
    leaf_count = max(16, round((70 if dense else 54)*scale))
    for i in range(leaf_count):
        angle = rng.random()*2*math.pi
        radius = rng.random()**0.65*(1.7 if dense else 1.45)
        z = rng.uniform(2.8, 5.05)
        start = (math.cos(angle)*radius*0.55, math.sin(angle)*radius*0.55, z-0.25)
        end = (math.cos(angle)*radius, math.sin(angle)*radius, z+rng.uniform(-0.2, 0.55))
        color_index = rng.randrange(len(leaves))
        append_leaf(verts, faces, start, end, rng.uniform(0.14, 0.23)*scale+0.07, (math.cos(angle)*0.14, math.sin(angle)*0.14, -0.05), max(4, round(7*scale)))
    obj = make_mesh_object(name, verts, faces, [bark]+leaves, collection)
    for poly in obj.data.polygons[:woody_faces]:
        poly.material_index = 0
    for poly in obj.data.polygons[woody_faces:]:
        poly.material_index = 1 + (poly.index % len(leaves))
    return obj


def shrub_mesh(name, lod, collection, leaves, seed):
    rng = random.Random(seed)
    scale = LOD_FACTORS[lod]
    verts, faces = [], []
    leaves_n = max(10, round(38*scale))
    for i in range(leaves_n):
        angle = rng.random()*2*math.pi
        rad = rng.uniform(0.18, 0.82)
        z = rng.uniform(0.25, 1.05)
        start = (math.cos(angle)*rad*0.3, math.sin(angle)*rad*0.3, z*0.45)
        end = (math.cos(angle)*rad, math.sin(angle)*rad, z)
        append_leaf(verts, faces, start, end, rng.uniform(0.12, 0.2)*scale+0.06,
                    (math.cos(angle)*0.08, math.sin(angle)*0.08, 0.0), max(4, round(7*scale)))
    obj = make_mesh_object(name, verts, faces, leaves, collection)
    for poly in obj.data.polygons:
        poly.material_index = poly.index % len(leaves)
    return obj


def build_collection(species, trunk, greens):
    col = bpy.data.collections.new("R6_"+species)
    bpy.context.scene.collection.children.link(col)
    lod_objects = {}
    for lod, factor in LOD_FACTORS.items():
        object_name = f"{species}_{lod}"
        if species == "palmeira_copacabana":
            obj = palm_mesh(object_name, lod, col, trunk, greens[0], 6100+int(factor*100))
        elif species == "arvore_tropical_ampla":
            obj = broadleaf_mesh(object_name, lod, col, trunk, greens, False, 4200+int(factor*100))
        elif species == "arvore_tropical_densa":
            obj = broadleaf_mesh(object_name, lod, col, trunk, greens, True, 8300+int(factor*100))
        else:
            obj = shrub_mesh(object_name, lod, col, greens, 2600+int(factor*100))
        lod_objects[lod] = obj
    return col, lod_objects


def use_only(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def export_species(species, lod_objects, folder):
    export_dir = folder / "FBX"
    export_dir.mkdir(parents=True, exist_ok=True)
    objects = list(lod_objects.values())
    use_only(objects)
    target = export_dir / (species+"_LOD0-2.fbx")
    bpy.ops.export_scene.fbx(filepath=str(target), use_selection=True,
        object_types={"MESH"}, apply_unit_scale=True, bake_space_transform=False,
        axis_forward="-Z", axis_up="Y", add_leaf_bones=False, path_mode="AUTO")
    for obj in objects:
        obj.hide_set(True)
        obj.hide_render = True
        obj.select_set(False)
    return target


def setup_preview(specimens, materials):
    scene = bpy.context.scene
    preview_col = bpy.data.collections.new("R6_Render_Stage")
    scene.collection.children.link(preview_col)
    # Place one member of each instantiable species on a neutral photographic stage.
    x_positions = [-6.0, -2.0, 2.0, 5.3]
    for i, species in enumerate(SPECIES):
        source = specimens[species]["LOD0"]
        obj = source.copy()
        obj.data = source.data.copy()
        obj.name = "RenderSpecimen_"+species
        preview_col.objects.link(obj)
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.location.x = x_positions[i]
        if species == "arbusto_tropical":
            obj.scale = (1.7, 1.7, 1.7)
    ground_mat = materials["ground"]
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.04))
    ground = bpy.context.object
    ground.name = "RenderStage_Ground"
    for col in list(ground.users_collection):
        col.objects.unlink(ground)
    preview_col.objects.link(ground)
    ground.data.materials.append(ground_mat)
    bpy.ops.object.camera_add(location=(8, -18, 8.5))
    camera = bpy.context.object
    camera.name = "R6_Vegetation_QA_Camera"
    for col in list(camera.users_collection): col.objects.unlink(camera)
    preview_col.objects.link(camera)
    direction = Vector((0, 0, 2.4))-camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 16.5
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(-4, -6, 12))
    key = bpy.context.object
    for col in list(key.users_collection): col.objects.unlink(key)
    preview_col.objects.link(key)
    key.data.energy, key.data.shape, key.data.size = 1800, "DISK", 10
    key.rotation_euler = (math.radians(22), 0, math.radians(-18))
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.07, 0.08)
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(PREVIEW)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != bpy.context.scene.collection.name:
            bpy.data.collections.remove(collection)
    mats = {
        "bark": material("R6_Bark_Warm_Brown", "70503B", 0.9),
        "green_1": material("R6_Leaf_Deep_Emerald", "245D35", 0.72, 0.025),
        "green_2": material("R6_Leaf_Sunlit_Tropical", "4A8748", 0.74, 0.035),
        "green_3": material("R6_Leaf_Young_Growth", "88A957", 0.77, 0.04),
        "ground": material("R6_Stage_Sandstone_Neutral", "BEB8A8", 0.95),
    }
    greens = [mats["green_1"], mats["green_2"], mats["green_3"]]
    specimens, exports = {}, []
    for species in SPECIES:
        _, lod_objects = build_collection(species, mats["bark"], greens)
        specimens[species] = lod_objects
        exports.append(export_species(species, lod_objects, OUT))
    setup_preview(specimens, mats)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"R6_Vegetation_Kit.blend"))
    bpy.ops.render.render(write_still=True)
    report = {
        "status": "R6_BLENDER_AUTHORED_SPECIES_KIT",
        "renderer": "Blender Cycles CPU",
        "source": "Original Python-authored custom meshes and shader-node materials; no external assets.",
        "species": [],
        "exports": [],
        "blend": {"path": "ArtSource/Vegetation/R6/R6_Vegetation_Kit.blend"},
        "preview": {"path": "ArtSource/Previews/R6_Vegetation_Kit_Blender.png", "kind": "genuine Blender Cycles render; not a Unity screenshot"},
        "limitations": ["Species/variant meshes are authoring originals; botanical species are not inferred from untagged OSM nodes.", "LOD variants are geometry-density tiers; Unity LODGroup hookup and in-game material/import validation remain pending.", "No Unity-licensed build, scene integration, FPS, or memory measurements are claimed."]
    }
    for species, lods in specimens.items():
        report["species"].append({"id": species, "lods": [
            {"name": lod, "object": obj.name, "vertices": len(obj.data.vertices),
             "polygons": len(obj.data.polygons), "bounds_m": [round(float(v), 3) for v in obj.dimensions]}
            for lod, obj in lods.items()]})
    for path in exports:
        report["exports"].append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                                   "sha256": sha(path), "binary_fbx": path.read_bytes()[:18] == b"Kaydara FBX Binary"})
    report["blend"]["bytes"] = (OUT/"R6_Vegetation_Kit.blend").stat().st_size
    report["blend"]["sha256"] = sha(OUT/"R6_Vegetation_Kit.blend")
    report["preview"]["bytes"] = PREVIEW.stat().st_size
    report["preview"]["sha256"] = sha(PREVIEW)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"blend": report["blend"], "exports": report["exports"], "preview": report["preview"]}, indent=2))


if __name__ == "__main__":
    main()
