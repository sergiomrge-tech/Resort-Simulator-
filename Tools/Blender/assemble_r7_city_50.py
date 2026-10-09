"""R7: actual Blender scene, original GIS minus exact 50 OSM ways + 50 R7 UV0 FBX.

Requires the safe masked OSM pipeline (r7_mask_city_50.py) first.
Execute via bpy python from checkout root:
  python -c "import bpy,runpy;runpy.run_path('Tools/Blender/assemble_r7_city_50.py',run_name='__main__')"

No user computer needed; source blend and original FBX are never saved/mutated.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r7_contract import semantic_part, object_id, project_uv

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
ORIGINAL_FBX=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
GALLERY=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/Procedural/R7_GALLERY_GENERATION_REPORT.json"
MASK_REPORT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/R7_SOURCE_MASK_QA.json"
FULL_OBJ=ROOT/"build/R7_OSM_MASK/original/data/copacabana_base.obj"
DERIVED_OBJ=ROOT/"build/R7_OSM_MASK/derived/data/copacabana_base.obj"
OUT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx"
PREVIEW=ROOT/"ArtSource/Previews/R7_Copacabana_50_Predios_Blender_Real_QA.png"
REPORT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/R7_BLENDER_SCENE_QA.json"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical(name):
    return name.split(".")[0] if name else "NULL"

def fingerprints(obj):
    mats=[canonical(m.name) if m else "NULL" for m in obj.data.materials]
    bag=Counter()
    for face in obj.data.polygons:
        if len(face.vertices)!=3:
            raise RuntimeError("Original GIS mesh no longer consists of triangles")
        vertices=[]
        for idx in face.vertices:
            p=obj.matrix_world@obj.data.vertices[idx].co
            vertices.append(tuple(round(float(v),3) for v in p))
        bag[(mats[face.material_index],tuple(sorted(vertices)))]+=1
    return bag

def import_obj(path,frame):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.obj_import(filepath=str(path),forward_axis="Y",up_axis="Z")
    meshes=[o for o in bpy.context.selected_objects if o.type=="MESH"]
    if len(meshes)!=1:
        raise RuntimeError("Expected exactly one imported OSM OBJ city")
    meshes[0].matrix_world=frame.copy()
    return meshes[0]

def material(name,color,metal=.0,rough=.72):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    return m

def file_meta(path,is_folder=False):
    uid=hashlib.sha256(("ResortR7:"+path.relative_to(ROOT).as_posix()).encode()).hexdigest()[:32]
    mp=Path(str(path)+".meta")
    if mp.exists():
        return  # Preserve Unity importer settings and GUID on every regeneration.
    if is_folder:
        data="fileFormatVersion: 2\nguid: "+uid+"\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n"
    else:
        data="fileFormatVersion: 2\nguid: "+uid+"\nModelImporter:\n  serializedVersion: 22200\n  externalObjects: {}\n"
    mp.write_text(data,encoding="utf-8")

def main():
    source_hash=sha(ORIGINAL)
    fbx_hash=sha(ORIGINAL_FBX)
    info=json.loads(MASK_REPORT.read_text(encoding="utf-8"))
    gallery=json.loads(GALLERY.read_text(encoding="utf-8"))
    if info["status"]!="R7_FIFTY_OSM_MASK_ALL_ROAD_GEOMETRY_IDENTICAL":
        raise RuntimeError("Original OSM city safety gate missing")
    if info["masked_way_count"]!=50 or gallery["count"]!=50:
        raise RuntimeError("R7 requires exact 50 OSM models")
    if (info["source_geo_original_sha256"]!=source_hash or
        info["source_fbx_original_sha256"]!=fbx_hash or
        info["source_50_models_report_sha256"]!=sha(GALLERY) or
        info["original_obj_sha256"]!=sha(FULL_OBJ) or
        info["derived_obj_sha256"]!=sha(DERIVED_OBJ)):
        raise RuntimeError("Stale/mixed R7 gallery, mask or original GIS inputs")
    if sorted(x["building_id"] for x in gallery["meshes"])!=info["masked_way_ids"]:
        raise RuntimeError("Derived base and FBX collection target different buildings")
    bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL))
    old=[o for o in bpy.context.scene.objects
         if o.type=="MESH" and len(o.data.polygons)>20000]
    if len(old)!=1:raise RuntimeError("Original geographic blender has unknown mesh hierarchy")
    old=old[0]
    matrix=old.matrix_world.copy()
    # Only the original metric XY GIS rotation/translation may be composed.
    basis=matrix.to_3x3()
    if (any(abs(basis.col[i].length-1)>1e-5 for i in range(3)) or
        abs(basis.determinant()-1)>1e-5 or
        (basis.col[2]-Vector((0,0,1))).length>1e-5):
        raise RuntimeError("Original GIS frame is not a metric Z-up rigid transform")
    source=fingerprints(old)
    if len(old.data.polygons)!=26764 or sum(source.values())!=26764:
        raise RuntimeError("Reference Blender GIS source not loaded")
    test=import_obj(FULL_OBJ,matrix)
    original_test = fingerprints(test)
    if original_test != source:
        missing=source-original_test
        extra=original_test-source
        source_roads=sum(n for (mat,face),n in source.items() if mat=="Road")
        obj_roads=sum(n for (mat,face),n in original_test.items() if mat=="Road")
        raise RuntimeError(
            "Original OBJ from OSM pipeline is not exactly the existing Blender city"
            + f"; Blender source triangles={sum(source.values())}, OBJ triangles={sum(original_test.values())}"
            + f"; missing={sum(missing.values())}, extra={sum(extra.values())}"
            + f"; road_source={source_roads}, road_obj={obj_roads}"
            + f"; missing_sample={list(missing.items())[:2]}"
            + f"; extra_sample={list(extra.items())[:2]}")
    bpy.data.objects.remove(test,do_unlink=True)
    city=import_obj(DERIVED_OBJ,matrix)
    derived=fingerprints(city)
    removed=source-derived
    if derived-source or any(x[0]!="Building" for x in removed):
        raise RuntimeError("R7 original Blender GIS lost/changed road or untouched faces")
    if sum(removed.values())!=info["building_faces_removed"]:
        raise RuntimeError("Blender source subtraction differs from 50-ID OSM mask")
    road_before=sum(n for (mat,face),n in source.items() if mat=="Road")
    road_after=sum(n for (mat,face),n in derived.items() if mat=="Road")
    if road_before!=3731 or road_after!=road_before:
        raise RuntimeError("Actual original Blender road faces changed")
    old.hide_set(True)
    old.hide_render=True
    city.name="GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS"
    project_uv(city.data)
    orig_names=[m.name if m else "NULL" for m in city.data.materials]
    for i,n in enumerate(orig_names):
        city.data.materials[i]=(material("R7_OSM_Roads_Source",(.28,.30,.31))
                               if "road" in n.casefold() else
                               material("R7_OSM_Other_Buildings_Source",(.68,.67,.62)))

    models=[]
    objects=[]
    for record in gallery["meshes"]:
        name=record["building_id"]
        path=ROOT/record["fbx"]
        if sha(path)!=record["fbx_sha256"]:
            raise RuntimeError("Generated architectural asset changed: "+name)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.import_scene.fbx(filepath=str(path))
        selected=list(bpy.context.selected_objects)
        models_mesh=[o for o in selected if o.type=="MESH" and len(o.data.polygons)>0]
        if len(models_mesh)<4:
            raise RuntimeError("Missing detailed FBX submeshes for "+name)
        # Source model is centered at OSM centroid with Z-up, and original
        # city object's matrix_world carries the 46 degree GIS rotation.
        c=record["local_osm_centroid_xy_m"]
        transform=matrix@Matrix.Translation(Vector((c[0],c[1],0.0)))
        original_world={id(o):o.matrix_world.copy() for o in models_mesh}
        for ob in models_mesh:
            ob.parent=None
            ob.matrix_world=transform@original_world[id(ob)]
            if len(ob.data.materials)!=1 or ob.data.materials[0] is None:
                raise RuntimeError("R7 semantic material ID lost before city FBX export: "+ob.name)
            semantic=semantic_part(ob.data.materials[0].name)
            ob.name=object_id(name,record["style_id"],semantic)
            ob.data.name=ob.name
            if len(ob.name)>63:
                raise RuntimeError("R7 stable FBX renderer label exceeds 63 chars: "+ob.name)
            objects.append(ob)
        if len(models_mesh)!=record["mesh_object_count"] or any(
            not ob.data.uv_layers.active for ob in models_mesh):
            raise RuntimeError("Per-building FBX lost meshes/UV0 on import: "+name)
        for ob in selected:
            if ob.type!="MESH":
                bpy.data.objects.remove(ob,do_unlink=True)
        models.append({
          "building_id":name,"style_id":record["style_id"],
          "model_mesh_objects":len(models_mesh),
          "model_polygons":sum(len(o.data.polygons) for o in models_mesh),
          "local_centroid_xy_m":c,"source_fbx":record["fbx"],
          "source_fbx_sha256":record["fbx_sha256"]
        })
        print("R7_CITY_BUILDING_PLACED",name,record["style_id"],flush=True)
    if len(models)!=50 or len(objects)<250:
        raise RuntimeError("No 50 complex buildings added to GIS city")

    # Never include the original undisturbed city in output. Its duplicate
    # would create z-fighting and wrong old mass collisions.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [city]+objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=city
    OUT.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT),use_selection=True,
       object_types={"MESH"},axis_forward="-Z",axis_up="Y",
       global_scale=1.0,apply_unit_scale=True,
       bake_space_transform=False,use_mesh_modifiers=True,add_leaf_bones=False,use_custom_props=True)
    if OUT.stat().st_size<500000:
        raise RuntimeError("R7 complete city FBX output failed")
    file_meta(OUT.parent,is_folder=True)
    file_meta(OUT,is_folder=False)

    # Native mesh gates may run quickly with --no-render; no image is claimed.
    render_preview="--no-render" not in sys.argv
    # QA camera targets one of the real OSM building sources in the middle
    # of Copacabana, not a fabricated street. Studio underlay is only preview.
    middle=min(gallery["meshes"],
        key=lambda m:abs(m["local_osm_centroid_xy_m"][0])+abs(m["local_osm_centroid_xy_m"][1])*.5)
    cx,cy=middle["local_osm_centroid_xy_m"]
    target=matrix@Vector((cx,cy,14))
    cam_data=bpy.data.cameras.new("R7_Real_GIS_Inspection_Camera")
    cam=bpy.data.objects.new("R7_Real_GIS_Inspection_Camera",cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location=matrix@Vector((cx+56,cy-67,115))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    cam_data.type="ORTHO"
    cam_data.ortho_scale=148
    cam_data.clip_end=2500
    bpy.context.scene.camera=cam
    sunlight=bpy.data.lights.new("R7_Real_GIS_Sun","SUN")
    sunlight.energy=2.0
    sun=bpy.data.objects.new("R7_Real_GIS_Sun",sunlight)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler=(math.radians(40),math.radians(-20),math.radians(-27))
    world=bpy.data.worlds.new("R7_Real_Copacabana_QA_World")
    world.use_nodes=True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.66,.72,.80,1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.65
    bpy.context.scene.world=world
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=10
    scene.cycles.use_denoising=False
    bpy.context.view_layer.cycles.use_denoising=False
    scene.render.resolution_x=1600
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(PREVIEW)
    scene.view_settings.view_transform="AgX"
    PREVIEW.parent.mkdir(parents=True,exist_ok=True)
    if render_preview:
        bpy.ops.render.render(write_still=True)
    if render_preview and (not PREVIEW.is_file() or PREVIEW.stat().st_size<45000):
        raise RuntimeError("Blender did not generate authentic R7 city camera render")

    if sha(ORIGINAL)!=source_hash or sha(ORIGINAL_FBX)!=fbx_hash:
        raise RuntimeError("ORIGINAL COPACABANA CITY MODIFIED! Reject output")
    qa={
        "status":"R7_50_SOURCE_OSM_BUILDINGS_REPLACED_IN_AUTHENTIC_BLENDER",
        "original_blend_sha256":source_hash,
        "original_fbx_sha256":fbx_hash,
        "source_mask_report_sha256":sha(MASK_REPORT),
        "original_faces":sum(source.values()),
        "old_building_faces_removed":sum(removed.values()),
        "original_road_faces":road_before,
        "retained_road_faces":road_after,
        "derived_base_city_faces":sum(derived.values()),
        "new_architecture_count":len(models),
        "new_architecture_mesh_objects":len(objects),
        "new_architecture_polygons":sum(x["model_polygons"] for x in models),
        "unmodified_original_source_used_as_output":False,
        "source_gis_rotation_matrix_rows":[[round(float(v),6) for v in row] for row in matrix],
        "derived_fbx":str(OUT.relative_to(ROOT)),
        "derived_fbx_bytes":OUT.stat().st_size,
        "derived_fbx_sha256":sha(OUT),
        "preview":str(PREVIEW.relative_to(ROOT)) if render_preview else None,
        "preview_sha256":sha(PREVIEW) if render_preview else None,
        "preview_bytes":PREVIEW.stat().st_size if render_preview else 0,
        "render_engine":"Blender Cycles CPU" if render_preview else "NOT_RENDERED",
        "models":models,
        "limits":"Real Blender rendered derived Copacabana with exactly 50 R7 UV0/semantic models replacing masked OSM ways. NOT final art, playable Windows EXE, native Unity-validated URP materials, benchmark FPS or 1468 fully replaced buildings.",
        "license":"© OpenStreetMap contributors — ODbL 1.0"
    }
    REPORT.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("R7_SCENE_EXPORT_SUCCESS",json.dumps({
        "roads":road_after,"removed_old_building_faces":sum(removed.values()),
        "new_architecture":len(models),"arch_polys":qa["new_architecture_polygons"],
        "fbx_bytes":qa["derived_fbx_bytes"],"preview_bytes":qa["preview_bytes"]}),flush=True)

if __name__=="__main__":
    main()
