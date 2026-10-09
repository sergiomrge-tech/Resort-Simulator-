"""Blender 4.5+: real 2 x 1 km OSM coast, parks and 48 tree instances.
Source footprint, R7/R8 architecture, existing roads and frame stay unchanged.
Run: blender -b -t 4 --python Tools/Blender/generate_r9_urban_environment.py
"""
from __future__ import annotations
from pathlib import Path
import bpy, math, json, hashlib, sys, gzip, xml.etree.ElementTree as ET, importlib.util
from mathutils import Matrix,Vector
from mathutils.geometry import tessellate_polygon
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools/geo"))
sys.path.insert(0,str(ROOT/"Tools/Blender"))
from generate_r6_vegetation import Frame
from r9_tree_canopy import enrich_tropical_canopy
GEO=ROOT/"geo/procedural/R4_SOURCE_FRAME.json"
OSM=ROOT/"geo/data/copacabana.osm.gz"
VEG=ROOT/"geo/procedural/R9_VEGETATION_SELECTED.json"
OUT=ROOT/"UnityProject/Assets/Architecture/R9_Environment/R9_Real_Coast_Parks_48_Trees.fbx"
REPORT=ROOT/"UnityProject/Assets/Architecture/R9_Environment/R9_ENVIRONMENT_NATIVE_QA.json"
FRAME=json.loads(GEO.read_text(encoding="utf-8"))
frame=Frame(FRAME)
ANGLE=math.radians(FRAME["axis_angle_degrees_counterclockwise_from_east"])
GEO_ROT=Matrix.Rotation(ANGLE,4,"Z")

def hashfile(path):
 h=hashlib.sha256()
 with path.open("rb") as fp:
  for c in iter(lambda:fp.read(1024*1024),b""):h.update(c)
 return h.hexdigest()

def mat(label,hex_color,metal=0,rough=.9):
 name="R9_"+label
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 rgb=tuple(int(hex_color[i:i+2],16)/255 for i in (0,2,4))
 m.diffuse_color=(*rgb,1.0)
 m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*rgb,1)
 bs.inputs["Metallic"].default_value=metal
 bs.inputs["Roughness"].default_value=rough
 return m

def make(name,vertices,faces,material,coords_uv=True):
 mesh=bpy.data.meshes.new(name+"_Mesh")
 mesh.from_pydata(vertices,[],faces)
 mesh.update()
 mesh.materials.append(material)
 if coords_uv:
  uv=mesh.uv_layers.new(name="UVMap")
  for poly in mesh.polygons:
   for li in poly.loop_indices:
    v=mesh.vertices[mesh.loops[li].vertex_index].co
    uv.data[li].uv=(float(v.x)/2.,float(v.y)/2.)
 ob=bpy.data.objects.new(name,mesh)
 bpy.context.collection.objects.link(ob)
 ob.matrix_world=GEO_ROT.copy()
 return ob

def rect(name,x0,y0,x1,y1,z,material):
 return make(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[(0,1,2,3)],material)

def strip(name,samples,y_bottom_fn,y_top_fn,z,material):
 verts=[];faces=[]
 for i,(x,y) in enumerate(samples):
  low=y_bottom_fn(x,y);high=y_top_fn(x,y)
  verts.extend(((x,low,z),(x,high,z)))
  if i:
   j=i*2
   faces.append((j-2,j,j+1,j-1))
 return make(name,verts,faces,material)

def polygon_clip(subject,xmin=-1000,xmax=1000,ymin=-500,ymax=500):
 def clip(points,axis,limit,keep_greater):
  if not points:return []
  result=[]
  for a,b in zip(points[-1:]+points[:-1],points):
   va=a[axis]; vb=b[axis]
   inside_a=va>=limit if keep_greater else va<=limit
   inside_b=vb>=limit if keep_greater else vb<=limit
   if inside_a!=inside_b:
    t=(limit-va)/(vb-va)
    result.append(tuple(a[k]+t*(b[k]-a[k]) for k in (0,1)))
   if inside_b:result.append(b)
  return result
 p=list(subject)
 for ax,limit,gt in ((0,xmin,True),(0,xmax,False),(1,ymin,True),(1,ymax,False)):
  p=clip(p,ax,limit,gt)
 if p and math.dist(p[0],p[-1])<1e-5:p.pop()
 return p

def poly(name,coords,z,material):
 pts=polygon_clip(coords)
 if len(pts)<3:return None
 vectors=[Vector((x,y,z)) for x,y in pts]
 triangles=tessellate_polygon([vectors])
 if not triangles:return None
 index={tuple(round(v,6) for v in a):i for i,a in enumerate(vectors)}
 verts=[tuple(v) for v in vectors]
 faces=[]
 for tri in triangles:
  ids=[int(p) if isinstance(p,int) else index[tuple(round(v,6) for v in p)] for p in tri]
  a,b,c=(vectors[q] for q in ids)
  cross=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
  faces.append(tuple(ids if cross>0 else ids[::-1]))
 return make(name,verts,faces,material)

def read_osm():
 root=ET.parse(gzip.open(OSM,"rb")).getroot()
 nodes={n.get("id"):(float(n.get("lon")),float(n.get("lat"))) for n in root.findall("node")}
 coastline=None
 zones=[]
 for way in root.findall("way"):
  tags={t.get("k"):t.get("v") for t in way.findall("tag")}
  ids=[n.get("ref") for n in way.findall("nd")]
  if not ids or any(n not in nodes for n in ids):continue
  coords=[frame.local(*nodes[ref]) for ref in ids]
  if tags.get("natural")=="coastline":
   coastline=coords
   continue
  kind=("grass" if tags.get("landuse")=="grass" else
        "park" if tags.get("leisure") in ("park","garden") else
        "park" if tags.get("natural") in ("wood","scrub") else
        "water" if tags.get("natural")=="water" else None)
  if not kind or len(coords)<4 or coords[0]!=coords[-1]:continue
  if max(x for x,y in coords)<-1000 or min(x for x,y in coords)>1000:continue
  if max(y for x,y in coords)<-500 or min(y for x,y in coords)>500:continue
  zones.append((way.get("id"),kind,coords))
 return coastline,zones

def coast_at_x(coast,x):
 candidates=[]
 for a,b in zip(coast,coast[1:]):
  if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(a[0]-b[0])>1e-6:
   frac=(x-a[0])/(b[0]-a[0])
   candidates.append(a[1]+frac*(b[1]-a[1]))
 if not candidates:return None
 # The coastline is a single OpenStreetMap way in the chosen source ROI.
 if len(candidates)>1:raise RuntimeError("OSM shoreline crosses same X repeatedly")
 return candidates[0]

def place_trees():
 pilot=json.loads(VEG.read_text(encoding="utf-8"))
 assert pilot["selected_count"]==48 and pilot["source_real_road_triangles"]==3731
 source_to_mesh={}
 for species in ("arvore_tropical_ampla","arvore_tropical_densa"):
  f=ROOT/"ArtSource/Vegetation/R6/FBX"/(species+"_LOD0-2.fbx")
  bpy.ops.object.select_all(action="DESELECT")
  bpy.ops.import_scene.fbx(filepath=str(f))
  imported=[obj for obj in bpy.context.selected_objects if obj.type=="MESH"]
  model=next((ob for ob in imported if ob.name==species+"_LOD0"),None)
  assert model is not None,("Missing real LOD0 tree",species,[o.name for o in imported])
  source_to_mesh[species]=(enrich_tropical_canopy(model.data,species),model.matrix_world.copy())
  for o in imported:bpy.data.objects.remove(o,do_unlink=True)
 names=[]
 for entry in pilot["instances"]:
  species=entry["asset_lod_collection"]
  assert species in source_to_mesh
  mesh,source_matrix=source_to_mesh[species]
  loc=entry["coordinates"]["local_m_xy"]
  x,y=loc
  assert -1000<=x<=1000 and -500<=y<=500
  assert entry["osm_id"].startswith("node/")
  theta=math.radians(entry["orientation"]["yaw_degrees"])
  # Unique exported mesh avoids FBX shared-mesh/object material-slot conflicts.
  obj=bpy.data.objects.new("R9_TREE_"+entry["osm_id"].replace("/","_")+"_"+species,mesh.copy())
  bpy.context.collection.objects.link(obj)
  obj.matrix_world=GEO_ROT @ Matrix.Translation(Vector((x,y,-.075))) @ Matrix.Rotation(theta,4,"Z") @ source_matrix
  names.append(obj.name)
 assert len(names)==48 and len(set(names))==48
 return names

def main():
 assert FRAME["along_coast_length_m"]==2000 and FRAME["inland_width_m"]==1000
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 materials={
  "pavement":mat("pavement_stone","B6B4AB"),
  "sand":mat("beach_sand","CFB38B"),
  "ocean":mat("ocean_blue","2A7691",.08,.22),
  "park":mat("park_green","557A49"),
  "water":mat("freshwater","487D90",.08,.2),
 }
 objects=[]
 objects.append(rect("R9_URBAN_PAVEMENT_2000x1000",-1000,-500,1000,500,-.17,materials["pavement"]))
 coast,zones=read_osm()
 assert coast is not None and len(coast)>50
 coastline_samples=[]
 for x in range(-1000,1001,10):
  y=coast_at_x(coast,x)
  assert y is not None and -1150<y<-350,(x,y)
  coastline_samples.append((x,y))
 # True OSM shoreline; water is below the shoreline and visible offshore.
 objects.append(strip("R9_OCEAN_REAL_OSM_COAST",coastline_samples,lambda x,y:-1150,lambda x,y:y,-.10,materials["ocean"]))
 # 50m interior sand band following coastline, outside all original road surfaces
 objects.append(strip("R9_SAND_REAL_OSM_COAST",coastline_samples,lambda x,y:y,lambda x,y:y+42.,-.13,materials["sand"]))
 zone_counts=Counter()
 for way_id,category,coords in zones:
  z=-.09 if category!="water" else -.07
  a=poly("R9_"+category.upper()+"_OSM_"+way_id,coords,z,materials["water" if category=="water" else "park"])
  if a is not None:objects.append(a);zone_counts[category]+=1
 trees=place_trees()
 export=[o for o in bpy.data.objects if o.type=="MESH"]
 assert len(trees)==48 and len(export)==len(objects)+48
 OUT.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action="DESELECT")
 for o in export:o.select_set(True)
 bpy.context.view_layer.objects.active=export[0]
 bpy.ops.export_scene.fbx(filepath=str(OUT),use_selection=True,object_types={"MESH"},
  axis_forward="-Z",axis_up="Y",global_scale=1,apply_unit_scale=True,
  bake_space_transform=False,use_mesh_modifiers=True,add_leaf_bones=False)
 qa={
  "status":"R9_NATIVE_BLENDER_ENVIRONMENT_READY_FOR_UNITY_QA",
  "frame_m":[2000,1000],"original_coastline_way":"way/70574890",
  "coast_samples":len(coastline_samples),"coast_y_limits":[round(min(y for x,y in coastline_samples),2),round(max(y for x,y in coastline_samples),2)],
  "mapped_zones":dict(zone_counts),"mapped_tree_instances":len(trees),
  "real_road_tree_clearance_gate_m":1.25,"canopy_mesh_variant":"R9_DENSE_ORGANIC_LEAF_GEOMETRY",
  "trees_real_osm_ids":trees,"exported_meshes":len(export),
  "source_sha256":{"osm":hashfile(OSM),"frame":hashfile(GEO),"vegetation_positions":hashfile(VEG)},
  "fbx_sha256":hashfile(OUT),"fbx_bytes":OUT.stat().st_size,
  "fbx":str(OUT.relative_to(ROOT)).replace("\\","/"),
  "limitations":"Scene stage built from OSM coast/parks and 48 selected tagged tree coordinates. Mapped tree species are aesthetic; coastline sand width 42m is illustrative, not surveyed beach boundary. Terrain is a horizontal urban underlay, not surveyed elevation. Unity visuals and FPS pending."
 }
 REPORT.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("R9_BLENDER_URBAN_PASS",json.dumps({k:qa[k] for k in ["exported_meshes","mapped_tree_instances","mapped_zones","coast_samples","fbx_bytes"]}),flush=True)
if __name__=="__main__":main()
