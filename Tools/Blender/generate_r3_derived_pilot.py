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
city=[o for o in bpy.context.scene.objects if o.type=="MESH" and len(o.data.polygons)>20000]
if len(city)!=1:
    raise RuntimeError("Expected one real imported OSM city mesh; abort modification otherwise")
city=city[0]
before=len(city.data.polygons)
names=[m.name if m else "NULL" for m in city.data.materials]
buildslots={i for i,name in enumerate(names) if "build" in name.lower()}
roadslots={i for i,name in enumerate(names) if "road" in name.lower()}
if not buildslots or not roadslots:
    raise RuntimeError("Original source lacks independent Building/Road slots")
roads_before=sum(p.material_index in roadslots for p in city.data.polygons)
parcels={x["id"]:x for x in OSM["parcels"]}
compatible=[(oid,x) for oid,x in FIT["sites"].items()
    if x["placement_study"]["fit"]=="GEOMETRIC_FIT_ONLY"]
if len(compatible)!=2:
    raise RuntimeError("Never assume three replacement buildings: expected precisely two safe fit candidates")

bm=bmesh.new()
bm.from_mesh(city.data)
bm.faces.ensure_lookup_table()
site_removed={}
removals=set()
# Compute source mesh connected components via face shared vertices. Reject a
# component if it escapes its intended OSM polygon or touches a Road face.
for oid,proposal in compatible:
    parcel=parcels[oid]
    ring=parcel["ring_xy_m"]
    bounds=parcel["bounds_xy_m"]
    seeds=[]
    for f in bm.faces:
        if f.material_index not in buildslots: continue
        center=city.matrix_world@f.calc_center_median()
        xy=center.x,center.y
        if (bounds["min_x"]-1.2<=xy[0]<=bounds["max_x"]+1.2 and
            bounds["min_y"]-1.2<=xy[1]<=bounds["max_y"]+1.2 and
            touch(xy,ring)):
            seeds.append(f)
    if len(seeds)<4:
        raise RuntimeError(f"Too few source building face seeds for {oid}: {len(seeds)}")
    found=set()
    for first in seeds:
        if first in found:continue
        pending=[first]
        while pending:
            f=pending.pop()
            if f in found:continue
            found.add(f)
            for v in f.verts:
                for other in v.link_faces:
                    if other not in found:
                        pending.append(other)
    if len(found)<5 or len(found)>140:
        raise RuntimeError(f"Cannot isolate OSM building component safely: {oid}, {len(found)} faces")
    if any(f.material_index not in buildslots for f in found):
        raise RuntimeError(f"Road/land face entered building component {oid} — NOT modifying GIS")
    vertices=set(v for f in found for v in f.verts)
    worldverts=[city.matrix_world@v.co for v in vertices]
    if not worldverts:
        raise RuntimeError("Empty real-building component")
    bb=[min(v.x for v in worldverts),min(v.y for v in worldverts),
        max(v.x for v in worldverts),max(v.y for v in worldverts)]
    if not (bb[0]>=bounds["min_x"]-1.9 and bb[1]>=bounds["min_y"]-1.9
            and bb[2]<=bounds["max_x"]+1.9 and bb[3]<=bounds["max_y"]+1.9):
        raise RuntimeError(f"Source component extends beyond original mapped footprint: {oid}, bounds {bb}")
    if found&removals:
        raise RuntimeError("Two unrelated OSM ways share topology — cannot replace")
    removals.update(found)
    site_removed[oid]={
        "old_building_faces":len(found),
        "source_building_z_bounds_m":[round(min(v.z for v in worldverts),4),
                                      round(max(v.z for v in worldverts),4)],
        "original_component_xy_bounds_m":[round(z,4) for z in bb],
        "source_materials":sorted({names[f.material_index] for f in found}),
        "model":proposal["authored_model"]
    }
if len(removals)<10:
    raise RuntimeError("Replacement did not isolate expected 2 original buildings")
bmesh.ops.delete(bm,geom=list(removals),context="FACES")
bm.to_mesh(city.data)
bm.free()
city.data.update()
roads_after=sum(p.material_index in roadslots for p in city.data.polygons)
if roads_before!=roads_after or before-len(city.data.polygons)!=len(removals):
    raise RuntimeError("Derivative pilot changed source street/other geometry unexpectedly")

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
  "removed_building_faces":len(removals),
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
    "removed_faces":len(removals),"roads_preserved":roads_before==roads_after,
    "buildings_replaced":len(site_removed),"FBX_size":OUT.stat().st_size},ensure_ascii=False))
