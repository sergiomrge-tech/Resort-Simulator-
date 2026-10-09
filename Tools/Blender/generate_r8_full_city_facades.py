"""R8: create textured 3D facades for every OSM mass still blank in R7.
All 1,418 backgrounds receive real window, door, trim and roof geometry.
Geometry stays on the exact OSM footprint; source R7 and GIS remain immutable.
Blender headless: blender -b -t 4 --python Tools/Blender/generate_r8_full_city_facades.py
"""
import json, math, hashlib
from collections import defaultdict, Counter
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
ASSIGN=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
PILOT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/Procedural/R7_GALLERY_GENERATION_REPORT.json"
R7=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx"
R7QA=ROOT/"ArtSource/Previews/R7_FBX_UV_NATIVE_QA.json"
OUT=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_Remaining_1418_Textured_Facades.fbx"
REPORT=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_FACADES_NATIVE_QA.json"
STYLEPARTS=("wall","shadow","glass","trim","roof","metal","stone")
FAMILY_BASE={
 "residencial_orla":(.76,.71,.60),"residencial_anos70":(.67,.68,.65),
 "art_deco_carioca":(.84,.72,.56),"hotel_classico":(.81,.77,.68),
 "hotel_contemporaneo":(.67,.72,.74),"misto_loja_terrea":(.76,.65,.57),
 "residencial_compacto":(.70,.71,.69),"predio_historico":(.78,.64,.54),
 "escritorio_clinica":(.69,.75,.77),"equipamento_especial":(.70,.65,.58)
}

def sha(path):
 with open(path,"rb") as f:
  h=hashlib.sha256()
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
  return h.hexdigest()

def polyarea(pts):
 return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))*.5

def q_face(d,points):
 v=d["v"]; f=d["f"]; idx=len(v)
 v.extend([tuple(p) for p in points])
 f.append(tuple(range(idx,idx+len(points))))

def face(d,a,b,c,e):
 q_face(d,(a,b,c,e))

def vertical(d,a,b,z0,z1,flip=False):
 corners=[(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)]
 # OSM rings may be clockwise: inward-facing backfaces disappeared in Unity.
 q_face(d,corners[::-1] if flip else corners)

def rail(d,a,t,n,u,z,width,height,depth=0.0,flip=False):
 # façade-oriented rectangle in geometric world: UVs are generated per face
 ax=a[0]+t[0]*(u-width*.5)+n[0]*depth
 ay=a[1]+t[1]*(u-width*.5)+n[1]*depth
 bx=ax+t[0]*width; by=ay+t[1]*width
 vertical(d,(ax,ay),(bx,by),z,z+height,flip)

def facade_material(style,part):
 name="R8_"+style+"__"+part
 obj=bpy.data.materials.get(name)
 if obj:return obj
 family=style[4:-3]
 variant=int(style[-2:])
 c=FAMILY_BASE[family]
 offset=(variant-3)*.017
 rgb=tuple(max(.04,min(.91,x+offset)) for x in c)
 if part=="glass":rgb=(.07,.13+.012*variant,.17+.012*variant)
 elif part=="shadow":rgb=(.035,.040,.045)
 elif part=="trim":rgb=tuple(x*.72 for x in rgb)
 elif part=="roof":rgb=tuple(x*.60 for x in rgb)
 elif part=="metal":rgb=(.20,.24,.26)
 elif part=="stone":rgb=tuple(x*.80+.07 for x in rgb)
 obj=bpy.data.materials.new(name)
 obj.diffuse_color=(*rgb,1)
 obj.use_nodes=True
 bs=obj.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*rgb,1)
 bs.inputs["Roughness"].default_value=.18 if part=="glass" else .7
 bs.inputs["Metallic"].default_value=.22 if part in ("glass","metal") else .02
 return obj

def add_building(item,geometry,counts):
 sid=item["style_id"]
 h=max(3.0,min(100.0,float(item["height_for_visualization_m"])))
 pts=[tuple(map(float,p)) for p in item["footprint_ring_local_xy_m"]]
 if len(pts)>1 and math.dist(pts[0],pts[-1])<.001: pts=pts[:-1]
 area=polyarea(pts)
 if len(pts)<3 or abs(area)<.02:raise ValueError("DEGENERATE_OSM_FOOTPRINT:"+item["building_id"])
 # No extensions beyond georeferenced lot geometry; all features are coplanar or recessed.
 sign=1 if area>0 else -1
 def vr(d,a,b,z0,z1):
  return vertical(d,a,b,z0,z1,flip=sign<0)
 def rr(d,a,t,n,u,z,width,height,depth=0.0):
  return rail(d,a,t,n,u,z,width,height,depth,flip=sign<0)
 floors=max(1,min(28,round(h/3.2)))
 is_coast="orla" in sid or "hotel" in sid
 is_commercial="loja" in sid or "escritorio" in sid
 windows=0
 for a,b in zip(pts,pts[1:]+pts[:1]):
  dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
  if length<.15:continue
  t=(dx/length,dy/length)
  n=(sign*t[1],-sign*t[0])
  g=lambda part: geometry[(sid,part)]
  # Real footprint wall, no blank anonymous fallback material.
  vr(g("wall"),a,b,0,h)
  # Crown/rim and plinth follow real perimeter.
  rr(g("roof"),a,t,n,length*.5,h-.36,length,.36,.012)
  rr(g("stone"),a,t,n,length*.5,0,length,.36,.014)
  bays=min(12,max(1,int(length/3.10)))
  if length<2.9:continue
  bay_step=length/bays
  ww=min((1.35 if is_coast else 1.12), bay_step*.63)
  if ww<.44:continue
  for floor in range(floors):
   floor_step=h/floors
   mid=(floor+.49)*floor_step
   wh=max(.62,min(1.75,floor_step*.62))
   # Outline and pane at very small positive depth avoid z-fighting,
   # preserving OSM parcel outline. Actual windows use 2 façade layers.
   for bay in range(bays):
    u=(bay+.5)*bay_step
    if floor==0 and bay==bays//2:
     dw=min(ww*1.23,1.95)
     dh=min(floor_step*.82,2.65)
     z=max(.10,floor_step*.10)
     rr(g("shadow"),a,t,n,u,z,dw,dh,.022)
     rr(g("glass"),a,t,n,u,z+.07,dw*.88,dh*.90,.035)
     rr(g("trim"),a,t,n,u,z+dh-.12,dw+.18,.16,.046)
     continue
    z=max(.53,mid-wh*.5)
    if z+wh>h-.38:continue
    # Dark recessed surround + colored glass + horizontal lintel/sill.
    rr(g("shadow"),a,t,n,u,z-.12,ww+.25,wh+.24,.018)
    rr(g("glass"),a,t,n,u,z,ww,wh,.035)
    rr(g("trim"),a,t,n,u,z+wh,ww+.29,.095,.042)
    rr(g("stone"),a,t,n,u,z-.15,ww+.31,.095,.047)
    # Slim vertical mullions distinguish residential from ribbon glass.
    if is_commercial or bay%3==0:
     rr(g("metal"),a,t,n,u,z,.045,wh,.045)
    windows+=1
  # Horizontal floor band breaks giant blank wall fields on all elevations.
  for floor in range(1,floors):
   if floor%3==0 or (is_coast and floor%2==0):
    rr(g("trim"),a,t,n,length*.5,floor*h/floors-.06,length,.085,.026)
 # Roof follows polygon exactly, including its nonrectangular perimeter.
 roof=[Vector((x,y,h)) for x,y in pts]
 for tri in tessellate_polygon([roof]):
  triangle=[tuple(v) if isinstance(v,Vector) else tuple(roof[int(v)]) for v in tri]
  if len(triangle)!=3:raise RuntimeError("Roof tessellation failed")
  a,b,c=triangle
  cross=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  q_face(geometry[(sid,"roof")],triangle if cross>0 else triangle[::-1])
 counts[sid]+=1
 return windows

def uv(mesh):
 layer=mesh.uv_layers.new(name="UVMap")
 for poly in mesh.polygons:
  vv=[mesh.vertices[i].co for i in poly.vertices]
  edge=vv[1]-vv[0]
  if edge.length<.0001:continue
  axis=edge.normalized()
  normal=poly.normal
  across=normal.cross(axis).normalized()
  if across.length<.001:across=Vector((0,0,1))
  for loop_index in poly.loop_indices:
   p=mesh.vertices[mesh.loops[loop_index].vertex_index].co
   layer.data[loop_index].uv=(p.dot(axis)/2.,p.dot(across)/2.)

def main():
 a=json.loads(ASSIGN.read_text(encoding="utf-8"))
 pilot=json.loads(PILOT.read_text(encoding="utf-8"))
 report=json.loads(R7QA.read_text(encoding="utf-8"))
 assert report["derived_fbx_sha256"]==sha(R7),"R7 mismatch"
 assert report["distinct_osm_ways"]==50
 pids={m["building_id"] for m in pilot["meshes"]}
 rows=[x for x in a["buildings"] if x["building_id"] not in pids]
 assert len(rows)==1418 and len(pids)==50 and len(a["buildings"])==1468
 # Fixed coast width and coast length; do not silently crop the map.
 frame=json.loads((ROOT/"geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf-8"))
 assert frame["along_coast_length_m"]==2000 and frame["inland_width_m"]==1000
 original_hashes={
  "r7_fbx_sha256":sha(R7),
  "source_blend_sha256":sha(ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"),
  "source_osm_sha256":sha(ROOT/"geo/data/copacabana.osm.gz"),
  "assignments_sha256":sha(ASSIGN)}
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 geometry=defaultdict(lambda:{"v":[],"f":[]})
 counts=Counter(); windows=0
 for idx,item in enumerate(rows):
  windows+=add_building(item,geometry,counts)
  if idx%250==249:print("R8_PROGRESS",idx+1,"/1418",flush=True)
 objects=[]
 for (sid,part),item in sorted(geometry.items()):
  if not item["f"]:continue
  name="R8_"+sid+"__"+part
  mesh=bpy.data.meshes.new(name)
  mesh.from_pydata(item["v"],[],item["f"])
  mesh.materials.append(facade_material(sid,part))
  mesh.update()
  uv(mesh)
  obj=bpy.data.objects.new(name,mesh)
  bpy.context.collection.objects.link(obj)
  objects.append(obj)
 assert sum(counts.values())==1418 and windows>20000
 # Position in R7-compatible UTM/OSM frame: rotate 46 degrees, no scaling.
 import mathutils
 theta=math.radians(frame["axis_angle_degrees_counterclockwise_from_east"])
 original_matrix=mathutils.Matrix.Rotation(theta,4,"Z")
 for obj in objects: obj.matrix_world=original_matrix.copy()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action="DESELECT")
 for obj in objects:obj.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(OUT),use_selection=True,
  object_types={"MESH"},axis_forward="-Z",axis_up="Y",
  apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False)
 mesh_faces=sum(len(o.data.polygons) for o in objects)
 manifest={
  "status":"R8_FULL_1418_FACADES_BLENDER_GENERATED_NOT_UNITY_APPROVED",
  "source":original_hashes,"target_area_m":[2000,1000],
  "coast_length_m":2000,"inland_depth_m":1000,
  "r7_detailed_building_count":50,
  "r8_background_building_count":sum(counts.values()),
  "full_city_total":sum(counts.values())+len(pids),
  "style_count":len(counts),"fbx_meshes":len(objects),
  "windows_generated":windows,"geometry_faces":mesh_faces,
  "ids_r8":sorted(x["building_id"] for x in rows),
  "r8_fbx_sha256":sha(OUT),"r8_fbx_bytes":OUT.stat().st_size,
  "r8_fbx":str(OUT.relative_to(ROOT)).replace("\\","/"),
  "notes":"Native Blender mesh creation and FBX export. Must validate URP materials, road-only source masking and capture in actual Unity before release."
 }
 REPORT.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("R8_GENERATOR_PASS",json.dumps({k:manifest[k] for k in ["full_city_total","style_count","fbx_meshes","windows_generated","geometry_faces","r8_fbx_bytes"]}),flush=True)
 assert all(sha(p)==v for p,v in [(R7,original_hashes["r7_fbx_sha256"]),(ASSIGN,original_hashes["assignments_sha256"])])
if __name__=="__main__":main()
