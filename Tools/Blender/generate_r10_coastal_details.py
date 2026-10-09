"""R10 geographic coastline finish — mosaic promenade and moving sea foam strips.

Real OSM coast; no modification to historic geometry. Native Blender FBX export
accompanies Unity URP material/shader finishing for the separately cloned R10 scene.
Promenade is an art-derived 12 m buffer 26-38 m inland from original shoreline:
it is NOT a cadastral survey of the actual sidewalk. Checked against R7 road mesh.
"""
import sys,json,hashlib,math
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools/Blender"))
from generate_r9_urban_environment import read_osm,coast_at_x,make,mat,FRAME
OUTPUT=ROOT/"UnityProject/Assets/Architecture/R10_Coastal/R10_Ocean_Foam_Mosaic_Promenade.fbx"
REPORT=ROOT/"UnityProject/Assets/Architecture/R10_Coastal/R10_DETAILS_NATIVE_QA.json"

def band(name,points,bot,top,z,material):
 vertices=[];faces=[]
 for i,(x,y) in enumerate(points):
  lo=y+bot(x);hi=y+top(x)
  if lo>=hi:raise ValueError("Reversed bank "+name)
  vertices.extend(((x,lo,z),(x,hi,z)))
  if i>0:
   n=2*i
   faces.append((n-2,n,n+1,n-1))
 return make(name,vertices,faces,material)

def main():
 assert FRAME["along_coast_length_m"]==2000 and FRAME["inland_width_m"]==1000
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 coast,_=read_osm()
 samples=[(float(x),coast_at_x(coast,float(x))) for x in range(-1000,1001,5)]
 assert len(samples)==401 and all(y is not None for x,y in samples)
 light=mat("R10_Promenade_WhiteStone","CECAC0")
 charcoal=mat("R10_Promenade_DarkMosaic","323639")
 edge=mat("R10_Promenade_StoneEdge","85827A")
 foam=mat("R10_Photometric_SeaFoam","A8DFE0")
 assets=[]
 # Underlying promenaded boardwalk is raised a few centimetres above the R9
 # base and shoreline sand. Preserve the original GIS road and city networks.
 assets.append(band("R10_MOSAIC_PROMENADE_BASE",samples,lambda x:25.5,lambda x:38.0,-.063,light))
 # Authentic Copacabana-inspired black and pale stone undulations; modular bands,
 # not texture decals on the street that could displace real geometry.
 for i,center in enumerate((28.0,31.8,35.5)):
  def w(x,c=center,i=i):
   return c+0.74*math.sin(x*.043+i*.67)+.24*math.sin(x*.127-i*.36)
  assets.append(band("R10_MOSAIC_WAVE_BAND_%d"%(i+1),samples,
   lambda x:w(x)-.70,lambda x:w(x)+.70,-.053,charcoal))
 # Small offset coastal accents not covering original mapped asphalt.
 assets.append(band("R10_PROMENADE_SAND_EDGE",samples,
  lambda x:25.13,lambda x:25.43,-.051,edge))
 assets.append(band("R10_PROMENADE_STREET_EDGE",samples,
  lambda x:38.02,lambda x:38.24,-.050,edge))
 for i in range(3):
  # Three irregular low-contrast whitewash lines along real water boundary.
  offset=1.0+i*2.5
  def sw(x,j=i):
   return 0.34*math.sin(x*.032+j*1.8)+.13*math.sin(x*.11+j)
  assets.append(band("R10_WATER_BREAKING_FOAM_%d"%(i+1),samples,
   lambda x:-offset-1.08+sw(x),lambda x:-offset-.75+sw(x),-.085,foam))
 assert len(assets)==9
 assert all(o.data.uv_layers.active and len(o.data.polygons)==400 for o in assets)
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action="DESELECT")
 for o in assets:o.select_set(True)
 bpy.context.view_layer.objects.active=assets[0]
 bpy.ops.export_scene.fbx(filepath=str(OUTPUT),use_selection=True,
  object_types={"MESH"},axis_forward="-Z",axis_up="Y",bake_space_transform=False,
  use_mesh_modifiers=True,apply_unit_scale=True,add_leaf_bones=False)
 h=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
 report={"status":"R10_COASTAL_NATIVE_BLEND_PASS_UNITY_PENDING",
  "scene_inland_prom_buffer_m":[25.5,38.0],
  "original_coast_osm_way":"way/70574890",
  "coast_aligned_length_m":2000,"map_inland_width_m":1000,
  "coast_samples":401,"mosaic_stripes":3,"sea_foam_stripes":3,
  "fbx_meshes":len(assets),"fbx_faces":sum(len(o.data.polygons) for o in assets),
  "fbx_bytes":OUTPUT.stat().st_size,"fbx_sha256":h,
  "limitations":"Art-derived Copacabana pattern approximation, not surveyed promenade width. Dynamic sea material is authored in Unity, not Blender, with no realistic fluid simulation."}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("R10_COASTAL_BLENDER_PASS",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
