"""Aerial Blender evidence: REAL GIS city and EXACT OSM pilot rings.

This is a camera rendering of the existing BlenderGIS geometry with inspection
outlines/labels only. There are NO invented beaches, buildings, roads or fake
gameplay screenshots. The original Blender and FBX bytes remain intact.
"""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SITES = ROOT/"geo/pilot/R3_EXACT_OSM_PARCELS.json"
PROBE = ROOT/"ArtSource/Previews/R3_Pilot_OSM_Geometry_Probe.json"
PREVIEW = ROOT/"ArtSource/Previews/R3_Orla_300m_OSM_Real_Blender_QA.png"
REPORT = ROOT/"ArtSource/Previews/R3_Orla_300m_Blender_QA.json"
SOURCE = ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
SOURCE_FBX = ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_hash=sha(SOURCE)
fbx_hash=sha(SOURCE_FBX)
data=json.loads(SITES.read_text(encoding="utf-8"))
probe=json.loads(PROBE.read_text(encoding="utf-8"))
hits={r["id"]:r for r in probe["parcels"]}
if len(data["parcels"])!=3 or len(hits)!=3:
    raise RuntimeError("Missing exact three evidence backed OSM site polygons")
city=[o for o in bpy.data.objects if o.type=="MESH" and len(o.data.polygons)>0]
if not city or sum(len(o.data.polygons) for o in city)<25000:
    raise RuntimeError("Real source city geometry not loaded; do not render a mockup")

def pbr(name, rgba, metallic=0, rough=.7, emission_strength=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=rgba
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=rough
    if emission_strength>0:
        bs.inputs["Emission Color"].default_value=rgba
        bs.inputs["Emission Strength"].default_value=emission_strength
    m.diffuse_color=rgba
    return m

building=pbr("R3_QA_Buildings_RealSource",(.69,.65,.59,1),rough=.85)
road=pbr("R3_QA_Roads_RealSource",(.23,.27,.30,1),rough=.88)
land=pbr("R3_QA_Land_RealSource",(.25,.33,.28,1),rough=.84)
for ob in city:
    for idx, old in enumerate(ob.data.materials):
        name=(old.name if old else "").lower()
        ob.data.materials[idx]=(road if "road" in name or "street" in name
                                else land if "land" in name or "beach" in name
                                else building)
    ob.hide_render=False

colors=[
  (.15,.91,.77,1),
  (1.00,.68,.22,1),
  (.93,.29,.50,1),
]
highlights=[]
for idx, site in enumerate(data["parcels"]):
    evidence=hits[site["id"]]
    col=colors[idx]
    z=max(1.0,evidence["zmax"] or 1.0)+1.3
    curve=bpy.data.curves.new("REAL_OSM_RING_"+site["id"].replace("/","_"),"CURVE")
    curve.dimensions="3D"
    curve.resolution_u=3
    curve.bevel_depth=.47
    curve.resolution_u=6
    curve.bevel_resolution=2
    spline=curve.splines.new("POLY")
    ring=site["ring_xy_m"]
    spline.points.add(len(ring)-2)
    for p,pt in zip(spline.points,ring[:-1]):
        p.co=(pt[0],pt[1],z,1.0)
    spline.use_cyclic_u=True
    obj=bpy.data.objects.new(curve.name,curve)
    bpy.context.collection.objects.link(obj)
    mat=pbr("R3_QA_Outline_"+str(idx),col,rough=.4,emission_strength=1.6)
    curve.materials.append(mat)

    text=bpy.data.curves.new("R3 site label","FONT")
    text.body=f"OSM {idx+1}: {site['id'].split('/')[1]}"
    text.size=4.8
    text.extrude=.002
    label=bpy.data.objects.new("R3_PILOT_OSM_ANNOTATION_ONLY",text)
    bpy.context.collection.objects.link(label)
    label.location=(site["centroid_local_xy_m"][0]-13,site["centroid_local_xy_m"][1],z+2.8)
    text.materials.append(mat)
    highlights.append({"id":site["id"],"ring_xy_m":ring,"display_z":round(z,3),
                       "face_hits":evidence["hits"],"source_has_building":evidence["has_existing_building_geometry"]})

# Neutral backplane is strictly an inspection underlay, never represented as a
# surveyed beach, sea level, sidewalk, or rebuilt road.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-150,-1.1))
ground=bpy.context.object
ground.name="TEMP_QA_BACKGROUND_NOT_GEOGRAPHIC_TERRAIN"
ground.dimensions=(550,610,1)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
ground.data.materials.append(land)

world=bpy.data.worlds.new("R3_QA_Sky")
bpy.context.scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.63,.73,.86,1)
bg.inputs["Strength"].default_value=.65
sun_data=bpy.data.lights.new("R3_QA_Daylight","SUN")
sun_data.energy=1.8
sun=bpy.data.objects.new("R3_QA_Daylight",sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler=(math.radians(34),math.radians(-14),math.radians(-21))

camera_data=bpy.data.cameras.new("R3_Aerial_Real_OSM")
camera=bpy.data.objects.new("R3_Aerial_Real_OSM",camera_data)
bpy.context.collection.objects.link(camera)
target=Vector((0,-160,9))
camera.location=target+Vector((105,-110,410))
camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
camera_data.type="ORTHO"
camera_data.ortho_scale=418
camera_data.clip_end=2000
bpy.context.scene.camera=camera
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=12
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=1600
scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(PREVIEW)
scene.view_settings.view_transform="Standard"
bpy.ops.render.render(write_still=True)
if PREVIEW.stat().st_size<50000:
    raise RuntimeError("Real Blender geographic QA render too small/failed")
if sha(SOURCE)!=source_hash or sha(SOURCE_FBX)!=fbx_hash:
    raise RuntimeError("The original geographic source was unexpectedly altered")

report={
  "status":"GENUINE_BLENDER_GIS_WITH_OSM_OVERLAYS",
  "visual_stage":"OSM_PARCEL_LOCATION_QA_ONLY",
  "source_blend":"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend",
  "source_blend_sha256":source_hash,
  "source_fbx_sha256":fbx_hash,
  "preview":"ArtSource/Previews/R3_Orla_300m_OSM_Real_Blender_QA.png",
  "preview_sha256":sha(PREVIEW),
  "preview_bytes":PREVIEW.stat().st_size,
  "city_faces":sum(len(o.data.polygons) for o in city),
  "sites":highlights,
  "render_engine":"Blender Cycles CPU",
  "limits":"No replacement/new buildings, no Unity scene/screenshot, footprint not land title, QA underlay not real terrain.",
  "copyright":"© OpenStreetMap contributors — ODbL 1.0"
}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("R3_REAL_CITY_BLENDER_OVERLAY_QA",json.dumps({
    "sites":len(highlights),"faces":report["city_faces"],"preview_sha256":report["preview_sha256"]}))
