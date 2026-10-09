"""R3 optional derived pilot: replace TWO validated OSM building components safely.

DOES NOT edit original Copacabana .blend/.fbx; creates separately named derived
pilot scene + preview, ONLY after connected-component topology validation proves
each site is isolated. No third site model is placed (missing base geometry).
This is a Blender design study, not a Unity screenshot or approved game asset.
"""
from __future__ import annotations
import bpy
import bmesh
import json
import math
import hashlib
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
ORIGINAL_FBX=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
OSM=json.loads((ROOT/"geo/pilot/R3_EXACT_OSM_PARCELS.json").read_text(encoding="utf-8"))
FIT=json.loads((ROOT/"geo/pilot/R3_MODEL_FIT_STUDY.json").read_text(encoding="utf-8"))
SOURCE_ARCH=ROOT/"ArtSource/LocalProjectOwned/CoastalUrbanKit"
OUT=ROOT/"UnityProject/Assets/Architecture/R3_Pilot/R3_Orla_Piloto_Derivado.fbx"
PNG=ROOT/"ArtSource/Previews/R3_Piloto_Derivado_2_Arquiteturas_Blender_QA.png"
REPORT=ROOT/"ArtSource/Previews/R3_Piloto_Derivado_QA.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mat(name, color,metal=0,rough=.6):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*color,1)
    n.inputs["Metallic"].default_value=metal
    n.inputs["Roughness"].default_value=rough
    return m

def inpoly(p,ring):
    x,y=p
    hit=False
    for a,b in zip(ring,ring[1:]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            hit=not hit
    return hit

def edge_dist(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=0 if den<1e-12 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))

def touch(p,ring,dist=.46):
    return inpoly(p,ring) or min(edge_dist(p,a,b) for a,b in zip(ring,ring[1:]))<=dist

oldblend=sha(ORIGINAL)
oldfbx=sha(ORIGINAL_FBX)
from collections import Counter

def canonical_name(name):
    return (name or "NULL").split(".")[0]

def triangle_signature(obj):
    materials=[canonical_name(m.name) if m else "NULL" for m in obj.data.materials]
    result=Counter()
    for p in obj.data.polygons:
        if len(p.vertices)!=3:
            raise RuntimeError("Original GIS geometry was not triangulated")
        category=materials[p.material_index]
        coords=[]
        for vertex_index in p.vertices:
            v=obj.matrix_world@obj.data.vertices[vertex_index].co
            coords.append(tuple(round(float(z),3) for z in v))
        result[(category,tuple(sorted(coords)))]+=1
    return result

def import_original_obj(path):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.obj_import(filepath=str(path),forward_axis="Y",up_axis="Z")
    imported=[o for o in bpy.context.selected_objects if o.type=="MESH"]
    if len(imported)!=1:
        raise RuntimeError("Expected 1 canonical original city OBJ mesh, got "+str(len(imported)))
    return imported[0]

orig_meshes=[o for o in bpy.context.scene.objects
             if o.type=="MESH" and len(o.data.polygons)>20000]
if len(orig_meshes)!=1:
    raise RuntimeError("Original BlenderGIS scene lacks a single authoritative city source")
old_city=orig_meshes[0]
before=len(old_city.data.polygons)
old_signatures=triangle_signature(old_city)
if before!=26764:
    raise RuntimeError("Blender source face count changed unexpectedly")

original_obj=ROOT/"build/R3_OSM_PARITY/unfiltered/data/copacabana_base.obj"
masked_obj=ROOT/"build/R3_OSM_PARITY/masked/data/copacabana_base.obj"
if not original_obj.is_file() or not masked_obj.is_file():
    raise RuntimeError("Rebuild source and two-ID masked OBJ first; never fabricate city mesh")

reimported=import_original_obj(original_obj)
reconstructed=triangle_signature(reimported)
if old_signatures!=reconstructed:
    def fingerprint_stats(sig):
        points=[v for (mat,verts) in sig for v in verts]
        counts={m:sum(n for (mm,_),n in sig.items() if mm==m)
                for (m,_) in sig}
        return {"faces":sum(sig.values()),"materials":counts,
                "bbox":[min(x[0] for x in points),min(x[1] for x in points),
                        max(x[0] for x in points),max(x[1] for x in points)],
                "sample":list(sig.keys())[:2]}
    print("R3_SOURCE_TRIANGLE_MISMATCH_DIAGNOSTIC",json.dumps({
          "original_blend":fingerprint_stats(old_signatures),
          "reconstructed_OBJ":fingerprint_stats(reconstructed)}),flush=True)
    unexpected=(reconstructed-old_signatures)
    missing=(old_signatures-reconstructed)
    raise RuntimeError(
        "Original frozen OSM pipeline did NOT reconstruct BlenderGIS exactly; refusing replacement. "
        f"missing triangles={sum(missing.values())}, added={sum(unexpected.values())}")
bpy.data.objects.remove(reimported,do_unlink=True)

city=import_original_obj(masked_obj)
derived_signatures=triangle_signature(city)
removed=old_signatures-derived_signatures
added=derived_signatures-old_signatures
if added or any(k[0]!="Building" for k in removed):
    raise RuntimeError("Masked original pipeline changed streets or introduced unknown geometry")
removals_count=sum(removed.values())
if removals_count!=23 or before-len(city.data.polygons)!=removals_count:
    raise RuntimeError("Original mask did not remove exactly 23 building triangles")
roads_before=sum(n for (material,tri),n in old_signatures.items()
                                              if material=="Road")
roads_after=sum(n for (material,tri),n in derived_signatures.items()
                if material=="Road")
if roads_before!=3731 or roads_after!=roads_before:
    raise RuntimeError("Actual BlenderGIS street triangles were not perfectly preserved")
old_city.hide_render=True
old_city.hide_set(True)
city.name="GIS_DERIVED_OSM_ORIGINAL_PIPELINE_MINUS_2_WAYS"
names=[m.name if m else "NULL" for m in city.data.materials]
buildslots={i for i,n in enumerate(names) if "build" in n.lower()}
roadslots={i for i,n in enumerate(names) if "road" in n.lower()}
if not buildslots or not roadslots:
    raise RuntimeError("Masked source lost Building/Road material provenance")
parcels={x["id"]:x for x in OSM["parcels"]}
compatible=[(oid,x) for oid,x in FIT["sites"].items()
   if x["placement_study"]["fit"]=="GEOMETRIC_FIT_ONLY"]
if {x[0] for x in compatible}!={"way/1048277518","way/1048277521"}:
    raise RuntimeError("Only the two approved OSM ways are eligible to be replaced")
site_removed={}
for oid,proposal in compatible:
    parcel=parcels[oid]
    vertices=parcel["vertex_count"]
    wall_triangles=2*vertices
    roof_triangles=vertices-2
    site_removed[oid]={
       "old_building_faces":wall_triangles+roof_triangles,
       "original_roof_faces":roof_triangles,
       "original_roof_area_m2":parcel["footprint_area_m2"],
       "osm_reference_area_m2":parcel["footprint_area_m2"],
       "source_building_z_bounds_m":[0,18],
       "original_component_xy_bounds_m":[
          parcel["bounds_xy_m"]["min_x"],parcel["bounds_xy_m"]["min_y"],
          parcel["bounds_xy_m"]["max_x"],parcel["bounds_xy_m"]["max_y"]],
       "source_materials":["Building"],
       "model":proposal["authored_model"],
       "source_height_note":"18 m was a visualization estimate, NOT an actual measured height"
    }
if sum(x["old_building_faces"] for x in site_removed.values())!=removals_count:
    raise RuntimeError("Expected two building OSM way triangle counts do not sum to exactly removed geometry")
# Assign distinct palette purely for Blender QA, preserving all real original
# unmodified FBX file contents. Runtime PBR map import is separate.
mat_city_road=mat("R3_Pilot_Road_Source",(.20,.24,.28),0,.88)
mat_city_house=mat("R3_Pilot_Building_Source",(.67,.66,.62),0,.78)
for i,n in enumerate(names):
    city.data.materials[i]=(mat_city_road if i in roadslots else mat_city_house)
city.name="GIS_DERIVED_2_OSM_BUILDINGS_REMOVED_NO_ORIGINAL_CHANGED"

hero_objects=[]
for oid,study in compatible:
    model_name=study["authored_model"]
    model_path=SOURCE_ARCH/(model_name+".fbx")
    if sha(model_path)!=study["source_fbx_sha256"]:
        raise RuntimeError("Source FBX from user-authored library changed")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.import_scene.fbx(filepath=str(model_path))
    imported=list(bpy.context.selected_objects)
    meshes=[obj for obj in imported if obj.type=="MESH"]
    if not meshes:
        raise RuntimeError("Genuine author FBX import has no meshes: "+model_name)
    points=[obj.matrix_world@Vector(corner) for obj in meshes for corner in obj.bound_box]
    low=Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)))
    high=Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)))
    fit=study["placement_study"]
    scal=fit["scale"]
    angle=math.radians(fit["yaw_blender_degrees"])
    center=fit["center_xy_m"]
    old_ground=site_removed[oid]["source_building_z_bounds_m"][0]
    transform=(Matrix.Translation(Vector((center[0],center[1],old_ground)))
       @ Matrix.Rotation(angle,4,"Z")
       @ Matrix.Scale(scal,4)
       @ Matrix.Translation(Vector((-(low.x+high.x)*.5,-(low.y+high.y)*.5,-low.z))))
    for ob in meshes:
        original_world=ob.matrix_world.copy()
        ob.parent=None
        ob.matrix_world=transform@original_world
        ob.name="R3_OWNED_"+model_name+"__OSM_"+oid.split("/")[1]
        for slot in ob.material_slots:
            if not slot.material:continue
            n=slot.material.name.split(".")[0].lower()
            if "glass" in n:color=(.12,.26,.31);metal=.22;rough=.14
            elif "metal" in n:color=(.20,.24,.28);metal=.72;rough=.29
            elif "wood" in n:color=(.29,.18,.10);metal=0;rough=.50
            elif "trim" in n:color=(.53,.38,.19);metal=.55;rough=.35
            elif "concrete" in n:color=(.68,.64,.56);metal=0;rough=.74
            else:color=(.85,.79,.69);metal=0;rough=.70
            slot.material=mat("R3_QA_"+model_name+"_"+n, color,metal,rough)
        hero_objects.append(ob)
    for ob in imported:
        if ob.type!="MESH":
            bpy.data.objects.remove(ob,do_unlink=True)

# Export exact source mesh minus only the two isolated OSM building components,
# plus two physically distinct architectural assets, as A NEW SIDE-CAR FBX.
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
for ob in hero_objects+[city]:ob.select_set(True)
bpy.context.view_layer.objects.active=city
bpy.ops.export_scene.fbx(
    filepath=str(OUT),use_selection=True,object_types={"MESH"},
    axis_forward="-Z",axis_up="Y",global_scale=1.0,apply_unit_scale=True,
    bake_space_transform=False,use_mesh_modifiers=True,add_leaf_bones=False)
if OUT.stat().st_size<350000:
    raise RuntimeError("Derived city pilot FBX incomplete")
guid=hashlib.sha256(b"resort-r3-derived-urban-osm-map-v1").hexdigest()[:32]
for path,is_folder in ((OUT.parent,True),(OUT,False)):
    g=hashlib.sha256(("R3/"+path.relative_to(ROOT).as_posix()).encode()).hexdigest()[:32]
    if path==OUT:g=guid
    meta=Path(str(path)+".meta")
    meta.write_text("fileFormatVersion: 2\nguid: "+g+"\n"+(
      "folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n" if is_folder
      else "ModelImporter:\n  serializedVersion: 22200\n  externalObjects: {}\n"
    ),encoding="utf-8")

# Preview after FBX export; the added ground plane is QA ONLY, not part of FBX.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-165,-1.1))
ground=bpy.context.object
ground.name="QA_BACKGROUND_GROUND_NOT_GEOGRAPHIC"
ground.dimensions=(440,490,1)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
ground.data.materials.append(mat("R3_QA_Ground",(.28,.33,.29),0,.79))
world=bpy.data.worlds.new("R3_Derived_Sky")
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.62,.73,.84,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.7
light=bpy.data.lights.new("R3_Daylight","SUN")
light.energy=1.65
sun=bpy.data.objects.new("R3_Daylight",light)
bpy.context.collection.objects.link(sun)
sun.rotation_euler=(math.radians(38),math.radians(-23),math.radians(-22))
cd=bpy.data.cameras.new("R3_Derived_Camera")
cam=bpy.data.objects.new("R3_Derived_Camera",cd)
bpy.context.collection.objects.link(cam)
target=Vector((25,-220,7))
cam.location=target+Vector((100,-130,250))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
cd.type="ORTHO"
cd.ortho_scale=320
cd.clip_end=1900
scene=bpy.context.scene
scene.camera=cam
scene.render.engine="CYCLES"
scene.cycles.samples=12
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(PNG)
scene.view_settings.view_transform="Standard"
PNG.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.render.render(write_still=True)
if PNG.stat().st_size<45000:
    raise RuntimeError("Derived real Blender render failed")
if sha(ORIGINAL)!=oldblend or sha(ORIGINAL_FBX)!=oldfbx:
    raise RuntimeError("Original geographic Blender/FBX source mutated")

report={
  "status":"DERIVED_PILOT_BLENDER_GIS_NOT_UNITY_VALIDATED",
  "source_original_blend_sha256":oldblend,
  "source_original_fbx_sha256":oldfbx,
  "original_faces":before,
  "original_road_faces":roads_before,
  "retained_road_faces":roads_after,
  "removed_building_faces":removals_count,
  "retained_city_faces":len(city.data.polygons),
  "replacements":site_removed,
  "unmodified_third_site":"way/1308635852",
  "authored_model_mesh_objects":len(hero_objects),
  "pilot_derived_fbx":"UnityProject/Assets/Architecture/R3_Pilot/R3_Orla_Piloto_Derivado.fbx",
  "pilot_derived_fbx_sha256":sha(OUT),
  "pilot_derived_fbx_bytes":OUT.stat().st_size,
  "preview":"ArtSource/Previews/R3_Piloto_Derivado_2_Arquiteturas_Blender_QA.png",
  "preview_sha256":sha(PNG),
  "preview_bytes":PNG.stat().st_size,
  "engine":"Blender Cycles CPU",
  "limits":"In-memory derived geometry for study only. Two original building components isolated; no roads deleted. Original files preserved. Not Unity compiled or final art."
}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("R3_DERIVED_CITY_PILOT_SOURCE_SAFE",json.dumps({
    "removed_faces":removals_count,"roads_preserved":roads_before==roads_after,
    "buildings_replaced":len(site_removed),"FBX_size":OUT.stat().st_size},ensure_ascii=False))
