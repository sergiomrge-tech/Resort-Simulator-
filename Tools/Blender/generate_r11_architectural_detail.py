"""R11 — procedural *true 3D* architectural details for 1418 geolocated buildings.

Preserves R7/R8 geometry and OSM outlines exactly at ground level.
Deterministic variation seeded by *building_id*, not camera or export order.
Adds elevated volume only: balconies, railings, cornices, ventilation and
rooftop water/technical boxes. Keeps 2km coastline x 1km depth.
Blender 4.5+ headless; GIS and all prior scenes remain immutable.
"""
from __future__ import annotations
import math,json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
import bpy
from mathutils import Matrix,Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
ASSIGN=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
PILOT=ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/Procedural/R7_GALLERY_GENERATION_REPORT.json"
R8QA=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_FACADES_NATIVE_QA.json"
R8=ROOT/"UnityProject/Assets/Architecture/R8_FullCity/R8_Remaining_1418_Textured_Facades.fbx"
OUT=ROOT/"UnityProject/Assets/Architecture/R11_Architecture/R11_Real_Facade_Volumetry_1418.fbx"
REPORT=ROOT/"UnityProject/Assets/Architecture/R11_Architecture/R11_ARCHITECTURE_NATIVE_QA.json"
PARTS=("balcony_slabs","glass_balustrades","metal_railings","cornices","roof_structures","service_units")

def hashfile(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for x in iter(lambda:f.read(1024*1024),b""):h.update(x)
 return h.hexdigest()

def stable_id(seed):
 return int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8],"big")

def area(points):
 return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))*.5

def append_prism(buffer,point,t,n,u0,u1,v0,v1,z0,z1):
 """Six outward-facing closed sides with arbitrary signed tangent-to-normal."""
 assert 0<u1-u0<2100 and 0<v1-v0<20 and 0<z1-z0<40
 def p(u,v,z):
  return (point[0]+t[0]*u+n[0]*v,point[1]+t[1]*u+n[1]*v,z)
 vertices=[
  p(u0,v0,z0),p(u1,v0,z0),p(u1,v1,z0),p(u0,v1,z0),
  p(u0,v0,z1),p(u1,v0,z1),p(u1,v1,z1),p(u0,v1,z1)
 ]
 cx=sum(p[0] for p in vertices)/8
 cy=sum(p[1] for p in vertices)/8
 cz=sum(p[2] for p in vertices)/8
 faces=((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
 start=len(buffer["v"])
 buffer["v"].extend(vertices)
 for face in faces:
  a,b,c=(Vector(vertices[i]) for i in face[:3])
  normal=(b-a).cross(c-a)
  fc=sum((Vector(vertices[i]) for i in face),Vector())/len(face)
  outward=fc-Vector((cx,cy,cz))
  buffer["f"].append(tuple(start+i for i in (face if normal.dot(outward)>0 else face[::-1])))

def add_side(item,building,geo,counters):
 bid=building["building_id"]
 style=building["style_id"]
 h=max(3.,min(100.,float(building["height_for_visualization_m"])))
 pts=[tuple(map(float,q)) for q in building["footprint_ring_local_xy_m"]]
 if len(pts)>1 and math.dist(pts[0],pts[-1])<.001:pts.pop()
 ar=area(pts)
 if len(pts)<3 or abs(ar)<.02:raise ValueError("INVALID_REAL_OSM_LOT "+bid)
 sign=1 if ar>0 else -1
 seed=stable_id(bid)
 floors=max(1,min(28,round(h/3.2)))
 inc=h/floors
 family=style[4:-3]
 geo_for=lambda typ:geo[(style,typ)]
 edges=[]
 for idx,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
  dx=b[0]-a[0];dy=b[1]-a[1]
  length=math.hypot(dx,dy)
  if length<5.8:continue
  t=(dx/length,dy/length)
  n=(sign*t[1],-sign*t[0])
  edges.append((idx,a,t,n,length))
 # Only large segments: avoid alcoves/irregular alley geometry.
 edges.sort(key=lambda x:x[4],reverse=True)
 # Distinguish coastal balconies, hotels, Art Deco pilasters and historical stucco.
 balcony_family=any(x in family for x in ("residencial","hotel","misto"))
 is_art_deco="art_deco" in family or "historico" in family or "hotel_classico" in family
 is_modern="contemporaneo" in family or "escritorio" in family
 balconies=0;units=0;cornices=0
 top_edges=edges[:(2 if balcony_family and seed%3==0 else 1)]
 if balcony_family and floors>=3:
  for edge_idx,a,t,n,length in top_edges:
   # Exact same R8 fenestration lattice: every balcony is centered on a REAL window.
   bay_count=min(12,max(1,int(length/3.10)))
   step=length/bay_count
   selected_floors=range(1,floors-1,2 if (seed>>4)%2==0 else 3)
   for floor in selected_floors:
    if floor>10 and floor%4!=1:continue
    z=floor*inc+0.18
    eligible=[bay for bay in range(bay_count) if (bay+(seed%3))%2==0]
    if len(eligible)>3:eligible=eligible[:3]
    for bay in eligible:
     if (seed+bay+floor)%11==0:continue
     mid=(bay+.5)*step
     width=min(step*.81,1.92)
     # Elevated 0.58-0.74 m balcony overhang: no change to OSM ground footprint.
     # It never changes building footprint or building centroid.
     depth=.74 if is_modern else .58
     append_prism(geo_for("balcony_slabs"),a,t,n,mid-width*.5,mid+width*.5,-.10,depth,z,z+.17)
     # Two deep triangular-looking support volumes bring visible depth under slabs.
     for bracket in (-.32,.32):
      u=mid+bracket*width
      append_prism(geo_for("cornices"),a,t,n,u-.06,u+.06,-.04,depth*.58,z-.27,z)
     baluster_h=min(1.03,inc*.35)
     if is_modern:
      append_prism(geo_for("glass_balustrades"),a,t,n,mid-width*.5+.08,mid+width*.5-.08,depth-.045,depth,z+.17,z+.17+baluster_h)
     else:
      # Outer parapet and spaced cylindrical-looking vertical uprights
      append_prism(geo_for("metal_railings"),a,t,n,mid-width*.5,mid+width*.5,depth-.035,depth,z+.17+baluster_h-.075,z+.17+baluster_h)
      for j in range(4):
       u=mid-width*.5+width*(j+.25)/4
       append_prism(geo_for("metal_railings"),a,t,n,u,u+.045,depth-.04,depth,z+.17,z+.17+baluster_h)
     balconies+=1
     counters["balconies"]+=1
 if is_art_deco or (seed%3==0):
  for edge_idx,a,t,n,length in edges[:2]:
   # Raised continuous cornice breaks up identical flat rooftop silhouettes.
   cornice_height=.19+.035*(seed%3)
   append_prism(geo_for("cornices"),a,t,n,.06,length-.06,-.07,.13,h-.46,h-.46+cornice_height)
   cornices+=1
 # Rooftop facilities are **inside** real building extents: no road collisions.
 # Choose a contained center (centroid is often outside concave polygons):
 # triangulate polygon, choose centroid of triangle with most area.
 poly=[Vector((x,y,h)) for x,y in pts]
 triangles=tessellate_polygon([poly])
 candidates=[]
 for tri in triangles:
  q=[Vector(v) if isinstance(v,Vector) else poly[int(v)] for v in tri]
  area_tri=abs((q[1]-q[0]).cross(q[2]-q[0]).z)*.5
  candidates.append((area_tri,(q[0]+q[1]+q[2])/3,q))
 if h>=7 and candidates:
  _,point,roof_triangle=max(candidates,key=lambda x:x[0])
  # Avoid roof footprint edge by limiting within inscribed local triangle.
  a,b,c=roof_triangle
  edge1=Vector(b)-Vector(a);edge2=Vector(c)-Vector(a)
  # axis aligned in largest roof triangle, with width limited to 1/5 edge lengths
  l1=edge1.length;l2=edge2.length
  if min(l1,l2)>1.3:
   t=(edge1.x/l1,edge1.y/l1); n=(edge2.x/l2,edge2.y/l2)
   # t/n aren't necessarily perpendicular. Ellipse box lies inside triangle if
   # each fractional extent uses <= 0.25 of its independent edge vectors.
   u0=min(.48,l1*.07); u1=min(1.6,l1*.22)
   v0=min(.48,l2*.07); v1=min(1.6,l2*.22)
   origin=(a.x,a.y)
   append_prism(geo_for("roof_structures"),origin,edge1.normalized().xy,edge2.normalized().xy,
                u0,u1,v0,v1,h+.12,h+1.30+(seed%3)*.42)
   units+=1
   if is_modern or (seed>>2)%3==0:
    # rooftop mechanical unit: recessed from actual building edges
    w1=min(l1*.08,.58);w2=min(l2*.08,.60)
    if u1+w1 < l1*.42:
     append_prism(geo_for("service_units"),origin,t,n,u1+.10,u1+.10+w1,v0,v0+w2,h+.09,h+.73)
     counters["services"]+=1
 counters["buildings"]+=1
 counters["roof_units"]+=units
 counters["cornices"]+=cornices
 if balconies: counters["buildings_with_balconies"]+=1
 if cornices: counters["buildings_with_cornices"]+=1
 return balconies

def uv_map(mesh):
 uv=mesh.uv_layers.new(name="UVMap")
 for polygon in mesh.polygons:
  ids=polygon.vertices
  vertices=[mesh.vertices[i].co for i in ids]
  ab=vertices[1]-vertices[0]
  if ab.length<1e-5:continue
  xaxis=ab.normalized()
  zaxis=polygon.normal.cross(xaxis).normalized()
  for li in polygon.loop_indices:
   p=mesh.vertices[mesh.loops[li].vertex_index].co
   uv.data[li].uv=(p.dot(xaxis)/1.8,p.dot(zaxis)/1.8)

def generic_mat(style,part):
 label="R11_"+style+"__"+part
 m=bpy.data.materials.get(label) or bpy.data.materials.new(label)
 m.use_nodes=True
 colors={"balcony_slabs":(.66,.64,.60),"glass_balustrades":(.20,.41,.52),
 "metal_railings":(.26,.29,.31),"cornices":(.76,.72,.64),
 "roof_structures":(.58,.55,.52),"service_units":(.25,.27,.30)}
 rgb=colors[part]
 m.diffuse_color=(*rgb,1)
 m.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(*rgb,1)
 return m

def main():
 a=json.loads(ASSIGN.read_text(encoding="utf-8"))
 pilot=json.loads(PILOT.read_text(encoding="utf-8"))
 r8=json.loads(R8QA.read_text(encoding="utf-8"))
 ids={x["building_id"] for x in pilot["meshes"]}
 buildings=[b for b in a["buildings"] if b["building_id"] not in ids]
 assert len(buildings)==1418 and len(ids)==50
 assert len(a["buildings"])==1468
 assert r8["r8_fbx_sha256"]==hashfile(R8) and r8["full_city_total"]==1468
 frame=json.loads((ROOT/"geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf-8"))
 assert frame["along_coast_length_m"]==2000 and frame["inland_width_m"]==1000
 before={"r8_fbx":hashfile(R8),"style_assignments":hashfile(ASSIGN)}
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 buffers=defaultdict(lambda:{"v":[],"f":[]})
 stats=Counter()
 for i,item in enumerate(buildings,1):
  add_side(i,item,buffers,stats)
  if i%250==0:print("R11_PROGRESS",i,"/1418",flush=True)
 # Styles are batched. No 1418 node/drawcall inflation from per-building meshes.
 styles={b["style_id"] for b in buildings}
 objects=[]
 rotation=Matrix.Rotation(math.radians(frame["axis_angle_degrees_counterclockwise_from_east"]),4,"Z")
 for (style,part),data in sorted(buffers.items()):
  if not data["f"]:continue
  name="R11_"+style+"__"+part
  mesh=bpy.data.meshes.new(name)
  mesh.from_pydata(data["v"],[],data["f"])
  mesh.materials.append(generic_mat(style,part))
  mesh.update()
  uv_map(mesh)
  obj=bpy.data.objects.new(name,mesh)
  bpy.context.collection.objects.link(obj)
  obj.matrix_world=rotation.copy()
  objects.append(obj)
 assert len(objects)>150 and stats["buildings"]==1418 and stats["balconies"]>300 and stats["roof_units"]>200
 OUT.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action="DESELECT")
 for obj in objects:obj.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(OUT),use_selection=True,object_types={"MESH"},
  axis_forward="-Z",axis_up="Y",apply_unit_scale=True,
  bake_space_transform=False,add_leaf_bones=False)
 result={
  "status":"R11_GEOMETRY_NATIVE_BLENDER_PASS_UNITY_PENDING",
  "map_length_coast_m":2000,"map_inland_width_m":1000,
  "real_osm_buildings_from_r8":len(buildings),"original_r7_detailed":len(ids),
  "full_city_total":1468,"style_count":len(styles),
  "meshes":len(objects),"faces":sum(len(o.data.polygons) for o in objects),
  "balconies":stats["balconies"],"roof_units":stats["roof_units"],
  "service_units":stats["services"],"cornices":stats["cornices"],
  "balcony_buildings":stats["buildings_with_balconies"],
  "source_hashes":before,"fbx_sha256":hashfile(OUT),"fbx_bytes":OUT.stat().st_size,
  "part_types":sorted(set(p for s,p in buffers)),
  "limitations":"Secondary geometry approximation elevated above immutable OSM footprints, not surveyed balcony/roof records; no sculptural hero facades or photo-accurate architectural match."
 }
 REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 assert hashfile(R8)==before["r8_fbx"] and hashfile(ASSIGN)==before["style_assignments"]
 print("R11_NATIVE_BUILD_PASS",json.dumps({k:result[k] for k in ["meshes","faces","balconies","roof_units","service_units","cornices","balcony_buildings","fbx_bytes"]}),flush=True)
if __name__=="__main__":main()
