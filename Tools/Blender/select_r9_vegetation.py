"""Road-polygon gate against R7 original real OSM road FBX (not estimated road width).
Select 48 from 120 measured OSM tree nodes, without shifting any position.
Requires generated R7 FBX; outputs deterministic 48 selected tree IDs for R9.
"""
import bpy,json,hashlib,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
city=root/"UnityProject/Assets/Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx"
src=root/"geo/procedural/R9_VEGETATION_CANDIDATES_120.json"
out=root/"geo/procedural/R9_VEGETATION_SELECTED.json"
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(city))
gis=next(o for o in bpy.data.objects if o.type=="MESH" and o.name.startswith("GIS_OSM_REAL_MAP_"))
road_slot=next(i for i,m in enumerate(gis.data.materials) if m and "Roads" in m.name)
tri=[]
for face in gis.data.polygons:
 if face.material_index==road_slot and len(face.vertices)==3:
  points=[tuple(gis.data.vertices[k].co)[:2] for k in face.vertices]
  xs=[p[0] for p in points];ys=[p[1] for p in points]
  tri.append((min(xs),max(xs),min(ys),max(ys),points))
assert len(tri)==3731

def point_segment_distance(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1]
 den=dx*dx+dy*dy
 if den<=1e-15:return math.dist(p,a)
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def road_clearance(p):
 best=1e9
 for x0,x1,y0,y1,pts in tri:
  # Ignore triangles whose AABB is > 1.3m from a tree.
  if not x0-1.26<=p[0]<=x1+1.26 or not y0-1.26<=p[1]<=y1+1.26:continue
  a,b,c=pts
  signs=[(p[0]-v[0])*(w[1]-v[1])-(p[1]-v[1])*(w[0]-v[0])
         for v,w in ((a,b),(b,c),(c,a))]
  if not (min(signs)<0<max(signs)):return 0.
  best=min(best,*[point_segment_distance(p,v,w) for v,w in ((a,b),(b,c),(c,a))])
 return best

data=json.loads(src.read_text(encoding="utf-8"))
assert len(data["instances"])==120
accepted=[]
excluded=[]
for t in data["instances"]:
 p=t["coordinates"]["local_m_xy"]
 d=road_clearance(p)
 if d<1.25:
  excluded.append({"osm_id":t["osm_id"],"reason":"real_osm_road_face_or_1_25m_safety_margin","actual_road_distance_m":round(d,3)})
  continue
 if len(accepted)==48:continue
 t["guards"]["actual_source_osm_road_clearance_min_m"]=round(d,3) if d<1e8 else "no_road_nearby"
 accepted.append(t)
assert len(accepted)==48
assert len({x["osm_id"] for x in accepted})==48
original_pilot=json.loads((root/"geo/procedural/R6_VEGETATION_INSTANCES.json").read_text(encoding="utf-8"))
original_ids={x["osm_id"] for x in original_pilot["instances"]}
qa={
 "status":"R9_SELECTED_48_TRUE_OSM_TREES_REAL_ROAD_MESH_GUARDED",
 "source_real_road_triangles":len(tri),
 "safety_margin_m":1.25,"selection_candidates":120,"selected_count":48,
 "replaced_pilot_ids":sorted(original_ids-{x["osm_id"] for x in accepted}),
 "added_nonroad_ids":sorted({x["osm_id"] for x in accepted}-original_ids),
 "rejected_by_original_road":excluded,
 "sources":{"r7_fbx":hashlib.sha256(city.read_bytes()).hexdigest(),"r9_120":hashlib.sha256(src.read_bytes()).hexdigest()},
 "instances":accepted,
 "limitations":"No adjusted coordinates. True OSM tree nodes only. Existing roads triangles source from derived R7 preserve original GIS. No curb lines or underground utility survey."
}
out.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("R9_ROAD_TREE_GUARD_PASS",json.dumps({"selected":len(accepted),"source_road_tris":len(tri),"excluded":len(excluded),"replaced_original":len(qa["replaced_pilot_ids"]),"new_nodes":len(qa["added_nonroad_ids"])}),flush=True)
