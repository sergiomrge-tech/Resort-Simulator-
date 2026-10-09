"""R12 original street-level 3D fronts: real OSM lots, no invented buildings.

For 1,418 R8 geolocated facades, add:
- recessed-looking glass lobby doors, layered frames, handles and stone steps;
- retail glazing, mullions, piers, layered shop canopy and textured fictional signs;
- restrained corner treatments and upper fascia.
All geometry kept inside lots at ground, only permitted elevated canopy overhangs.
R7/R8/R9/R10/R11 files and OSM coordinates are read-only.
"""
from __future__ import annotations
import json,math,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools/Blender"))
from generate_r11_architectural_detail import append_prism,stable_id,area,hashfile
ASSIGN=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
PILOT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/Procedural/R7_GALLERY_GENERATION_REPORT.json"
R11=ROOT/"UnityProject/Assets/Architecture/R11_Architecture/R11_Real_Facade_Volumetry_1418.fbx"
R11QA=ROOT/"UnityProject/Assets/Architecture/R11_Architecture/R11_ARCHITECTURE_NATIVE_QA.json"
R8=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_Remaining_1418_Textured_Facades.fbx"
OUT=ROOT/"UnityProject/Assets/Architecture/R12_Storefronts/R12_StreetLevel_1418_Entrances_Storefronts.fbx"
REPORT=ROOT/"UnityProject/Assets/Architecture/R12_Storefronts/R12_STREETLEVEL_NATIVE_QA.json"
ART=ROOT/"ArtSource/Previews/R12_SignArt_QA.json"
MATERIALS={
 "door_glass":(.095,.18,.22),
 "door_frame":(.26,.30,.31),
 "stone_entrance":(.66,.63,.56),
 "warm_interiors":(.35,.24,.15),
 "showcase_glass":(.12,.29,.35),
 "canopy_dark":(.24,.26,.28),
 "awning_trim":(.74,.60,.37),
 "signboard":(.15,.18,.19)
}
def point(a,t,n,u,v,z):
 return (a[0]+t[0]*u+n[0]*v,a[1]+t[1]*u+n[1]*v,z)

def strip_face(buf,a,t,n,u0,u1,v,z0,z1,sign):
 # 2 triangles for a billboard sign with fixed authored art UV. Double-sided
 # visibility is shader-controlled in Unity if a winding is backwards.
 vertices=(point(a,t,n,u0,v,z0),point(a,t,n,u1,v,z0),
           point(a,t,n,u1,v,z1),point(a,t,n,u0,v,z1))
 first=len(buf["v"])
 buf["v"].extend(vertices)
 # Reverse horizontal UV for clockwise OSM footprints: readable from street.
 q=((0.,0.),(1.,0.),(1.,1.),(0.,1.)) if sign>0 else ((1.,0.),(0.,0.),(0.,1.),(1.,1.))
 buf["quad_uv"].extend(q)
 buf["f"].append((first,first+1,first+2,first+3) if sign>0 else (first+3,first+2,first+1,first))

def geo_mat(part):
 name="R12_"+part
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 m.use_nodes=True
 rgb=MATERIALS.get(part,(.16,.18,.20))
 if part.startswith("sign_"):rgb=(.85,.81,.76)
 m.diffuse_color=(*rgb,1)
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*rgb,1)
 bs.inputs["Roughness"].default_value=.22 if "glass" in part else .61
 bs.inputs["Metallic"].default_value=.2 if ("glass" in part or "frame" in part) else .03
 return m

def add_shop(building,buf,counts,sign_counts):
 bid=building["building_id"]; sid=building["style_id"]; fam=sid[4:-3]
 h=max(3.,min(100.,float(building["height_for_visualization_m"])))
 pts=[tuple(map(float,p)) for p in building["footprint_ring_local_xy_m"]]
 if len(pts)>1 and math.dist(pts[0],pts[-1])<.001:pts.pop()
 sign=1 if area(pts)>0 else -1
 edges=[]
 for idx,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
  length=math.dist(a,b)
  if length<4.7:continue
  t=((b[0]-a[0])/length,(b[1]-a[1])/length)
  n=(sign*t[1],-sign*t[0])
  edges.append((length,idx,a,t,n))
 if not edges:
  counts["short_unfronted"]+=1;return
 length,index,a,t,n=max(edges,key=lambda x:x[0])
 floor_step=h/max(1,min(28,round(h/3.2)))
 bays=min(12,max(1,int(length/3.10)))
 bay_step=length/bays
 mid=(bays//2+.5)*bay_step
 is_commercial=any(s in fam for s in ("misto_loja","escritorio_clinica","hotel_"))
 is_hotel="hotel_" in fam
 is_medical="escritorio" in fam
 is_heritage="historico" in fam or "art_deco" in fam
 special="equipamento_especial" in fam
 v=lambda part:buf[(part)]
 # Entrance sits on exact R8 central-bay doorway. Layered lintel, wall jamb,
 # glossy dark door leaf, warm interior top light and real handles.
 doorwidth=min(1.65,bay_step*.75)
 d0=mid-doorwidth*.5;d1=mid+doorwidth*.5
 top=min(floor_step*.10+2.58,floor_step-.31)
 base=max(.08,floor_step*.10)
 if top<=base+1.5:return
 append_prism(v("stone_entrance"),a,t,n,d0-.32,d1+.32,-.075,.13,top+.03,top+.30)
 for u in (d0-.22,d1+.16):
  append_prism(v("stone_entrance"),a,t,n,u,u+.12,-.065,.14,base,top+.06)
 append_prism(v("door_frame"),a,t,n,d0,d1,.075,.13,base,top)
 append_prism(v("door_glass"),a,t,n,d0+.095,d1-.095,.128,.158,base+.13,top-.12)
 append_prism(v("door_frame"),a,t,n,mid-.024,mid+.024,.16,.19,base+.13,top-.12)
 # polished brass push handles
 for u in (mid-.14,mid+.13):
  append_prism(v("awning_trim"),a,t,n,u,u+.025,.193,.23,base+.80,base+1.17)
 # Accessible appearance: stone threshold raised only 0.08m (not a functional ramp).
 append_prism(v("stone_entrance"),a,t,n,d0-.22,d1+.22,-.10,.28,.035,.11)
 counts["entrances"]+=1
 if is_commercial:
  counts["commercial_fronts"]+=1
  # Ground-level, frontage-specific retail glazing; do not erase geographic wall.
  slots=0
  for bay in range(bays):
   if bay==bays//2:continue
   # Keep a bay next to the main entry vacant for classic hotel vestibule.
   if is_hotel and abs(bay-bays//2)<2:continue
   u=(bay+.5)*bay_step
   width=min(2.44,bay_step*.79)
   if width<.6:continue
   z0=.28;z1=min(top-.75,2.20)
   if z1<=z0+.85:continue
   append_prism(v("door_frame"),a,t,n,u-width*.5-.075,u+width*.5+.075,.07,.115,z0-.10,z1+.12)
   append_prism(v("showcase_glass"),a,t,n,u-width*.5,u+width*.5,.117,.155,z0,z1)
   append_prism(v("door_frame"),a,t,n,u-.028,u+.028,.158,.179,z0,z1)
   append_prism(v("warm_interiors"),a,t,n,u-width*.5+.11,u+width*.5-.11,.156,.19,z0+.10,z0+.26)
   slots+=1
  counts["showcase_windows"]+=slots
  # A projecting architectural canopy ABOVE all glass. Slight roof design detail.
  span=min(length-1.05,9.4)
  center=length*.5
  append_prism(v("canopy_dark"),a,t,n,center-span*.5,center+span*.5,-.045,.82,top-.53,top-.39)
  append_prism(v("awning_trim"),a,t,n,center-span*.5,center+span*.5,.75,.84,top-.59,top-.53)
  for edge_u in (center-span*.5+.06,center+span*.5-.19):
   append_prism(v("awning_trim"),a,t,n,edge_u,edge_u+.13,.65,.80,top-.57,top-.33)
  counts["commercial_awnings"]+=1
  # 12 original generic Portuguese panels, assigned deterministically; imagery
  # stays fictional and is never claimed to represent a real OSM storefront.
  eligible=(6,7,0,8) if is_hotel else (8,9,4,6) if is_medical else (0,1,2,3,4,5,7,10,11)
  sk=eligible[stable_id(bid+"sign")%len(eligible)]
  sb=buf[("sign_%02d"%sk)]
  signwidth=min(6.3,max(2.1,length-1.4))
  signheight=.44
  strip_face(sb,a,t,n,center-signwidth*.5,center+signwidth*.5,.21,
             max(2.05,top-.29),min(h-.08,max(2.05,top-.29)+.44),sign)
  sign_counts[str(sk)]+=1
  counts["readable_sign_panels"]+=1
 else:
  counts["residential_lobbies"]+=1
  # Residential lobby distinguishes apartments from anonymous storefronts.
  append_prism(v("stone_entrance"),a,t,n,d0-.40,d1+.40,-.055,.42,top+.12,top+.26)
  for u in (d0-.38,d1+.24):
   append_prism(v("stone_entrance"),a,t,n,u,u+.12,.15,.32,base,top+.18)
  if is_heritage or special:
   append_prism(v("awning_trim"),a,t,n,d0-.42,d1+.42,.36,.44,top+.13,top+.17)
  counts["lobby_canopies"]+=1
 # Ground facade grooves and elevated weatherline:
 append_prism(v("stone_entrance"),a,t,n,.12,length-.12,.010,.06,floor_step-.30,floor_step-.17)
 counts["fronts"]+=1

def apply_uv(mesh,data,part):
 layer=mesh.uv_layers.new(name="UVMap")
 if part.startswith("sign_"):
  # Quad strips and 4 corner UVs. Avoid any generic projection changing letters.
  assert len(data["quad_uv"])==len(data["v"]) and len(mesh.polygons)*4==len(mesh.loops)
  for face in mesh.polygons:
   for li in face.loop_indices:
    vertex_index=mesh.loops[li].vertex_index
    layer.data[li].uv=data["quad_uv"][vertex_index]
 else:
  for poly in mesh.polygons:
   ids=[mesh.vertices[i].co for i in poly.vertices]
   edge=ids[1]-ids[0]
   if edge.length<1e-5:continue
   axis=edge.normalized();perp=poly.normal.cross(axis).normalized()
   if perp.length<.001:perp=Vector((0,0,1))
   for li in poly.loop_indices:
    p=mesh.vertices[mesh.loops[li].vertex_index].co
    layer.data[li].uv=(p.dot(axis)/2.,p.dot(perp)/2.)

def main():
 source=json.loads(ASSIGN.read_text(encoding="utf-8"))
 pilot=json.loads(PILOT.read_text(encoding="utf-8"))
 prior=json.loads(R11QA.read_text(encoding="utf-8"))
 signart=json.loads(ART.read_text(encoding="utf-8"))
 assert prior["status"]=="R11_GEOMETRY_NATIVE_BLENDER_PASS_UNITY_PENDING"
 assert prior["fbx_sha256"]==hashfile(R11)
 assert len(signart["signs"])==12
 ids={x["building_id"] for x in pilot["meshes"]}
 buildings=[b for b in source["buildings"] if b["building_id"] not in ids]
 assert len(buildings)==1418 and len(source["buildings"])==1468
 frame=json.loads((ROOT/"geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf-8"))
 assert frame["along_coast_length_m"]==2000 and frame["inland_width_m"]==1000
 read_only={str(p.relative_to(ROOT)):hashfile(p) for p in (ASSIGN,R8,R11)}
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 buffers=defaultdict(lambda:{"v":[],"f":[],"quad_uv":[]})
 counts=Counter();sign_counts=Counter()
 for i,b in enumerate(buildings,1):
  add_shop(b,buffers,counts,sign_counts)
  if i%300==0:print("R12_PROGRESS",i,"/1418",flush=True)
 rotation=Matrix.Rotation(math.radians(frame["axis_angle_degrees_counterclockwise_from_east"]),4,"Z")
 objs=[]
 for part,data in sorted(buffers.items()):
  if not data["f"]:continue
  key=part if isinstance(part,str) else str(part)
  mesh=bpy.data.meshes.new("R12_"+key)
  mesh.from_pydata(data["v"],[],data["f"]);mesh.update()
  mesh.materials.append(geo_mat(key))
  apply_uv(mesh,data,key)
  obj=bpy.data.objects.new("R12_"+key,mesh)
  bpy.context.collection.objects.link(obj)
  obj.matrix_world=rotation.copy()
  objs.append(obj)
 assert counts["entrances"]>=1350 and counts["commercial_fronts"]>=320
 assert counts["readable_sign_panels"]==counts["commercial_fronts"]
 assert counts["showcase_windows"]>500
 assert len(objs)>=19 and len(sign_counts)>=9
 OUT.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action="DESELECT")
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0]
 bpy.ops.export_scene.fbx(filepath=str(OUT),use_selection=True,object_types={"MESH"},
   axis_forward="-Z",axis_up="Y",apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False)
 for path,sha in read_only.items():assert hashfile(ROOT/path)==sha,"MUTATED_READONLY_SOURCE "+path
 result={
  "status":"R12_NATIVE_OSM_SHOPFRONT_FBX_GENERATED_UNITY_PENDING",
  "coast_m":2000,"inland_m":1000,"osm_full_city":1468,"r8_source_buildings":1418,
  "mesh_parts":len(objs),"mesh_faces":sum(len(o.data.polygons) for o in objs),
  "storefronts":counts["commercial_fronts"],"lobbies":counts["residential_lobbies"],
  "doors":counts["entrances"],"showcase_windows":counts["showcase_windows"],
  "awnings":counts["commercial_awnings"],"fictional_sign_panels":counts["readable_sign_panels"],
  "sign_types_used":dict(sign_counts),"source_hashes":read_only,
  "fbx_bytes":OUT.stat().st_size,"fbx_sha256":hashfile(OUT),
  "limitations":"Decorative doors are opaque wall overlays, not physical openings/navigable shops. All store signage fictional. No verified ground-floor tenancy, curb survey or legal accessibility audit."
 }
 REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("R12_NATIVE_STOREFRONT_PASS",json.dumps({k:result[k] for k in ("mesh_parts","mesh_faces","storefronts","lobbies","doors","showcase_windows","awnings","fictional_sign_panels","fbx_bytes")}),flush=True)
if __name__=="__main__":main()
