"""Independent real Blender FBX reimport and longitudinal/metric UV gates."""
from pathlib import Path
import bpy, sys, json, hashlib, math
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/Blender'))
from generate_r9_urban_environment import read_osm,coast_at_x,GEO_ROT
OUT=ROOT/'UnityProject/Assets/Architecture/R13_Coastal'
q=json.loads((OUT/'R13_COVERAGE.json').read_text(encoding='utf-8'))
assert q['frame_m']==[2000,1000]
assert len(q['sectors'])==10
assert hashlib.sha256((OUT/'R13_OSM_Coastal_Sectors.fbx').read_bytes()).hexdigest()==q['fbx_sha256']
for path,sha in q['source_sha256'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
assert len(json.loads((ROOT/'geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json').read_text(encoding='utf-8'))['buildings'])==1468
veg=json.loads((ROOT/'geo/procedural/R9_VEGETATION_SELECTED.json').read_text(encoding='utf-8'))
assert veg['selected_count']==48 and veg['source_real_road_triangles']==3731
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(OUT/'R13_OSM_Coastal_Sectors.fbx'))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
assert len(meshes)==q['meshes']<=250
actual={o.name:len(o.data.polygons) for o in meshes}
assert sum(actual.values())==q['faces'],(sum(actual.values()),q['faces'],{n:(q['mesh_faces'].get(n),v) for n,v in actual.items() if v!=q['mesh_faces'].get(n)})
assert {o.name:len(o.data.polygons) for o in meshes}==q['mesh_faces']
for ob in meshes:
    assert len(ob.data.materials)==1 and ob.data.materials[0],ob.name
    assert ob.data.uv_layers.active and len(ob.data.uv_layers.active.data)==len(ob.data.loops),ob.name
    assert all(math.isfinite(v) for p in ob.data.uv_layers.active.data for v in p.uv),ob.name
    assert all(math.isfinite(v) for p in ob.data.vertices for v in p.co),ob.name
for sector in q['refined_sectors']:
    for part in ('limestone','timber','metal','leaves','soil'):
        counts=[len(next(o for o in meshes if o.name==f'R13_S{sector:02d}_{part}'+('' if level==0 else f'_LOD{level}')).data.polygons) for level in range(3)]
        assert counts[0]>counts[1]>counts[2]>0,(sector,part,counts)
# Independent boundaries from reimported geometry, not just the generation JSON.
inv=GEO_ROT.inverted()
boundaries={}
for s in range(10):
    for part in ('wet_sand','sand','mosaic','sand_service','ocean_near','ocean_far'):
        ob=next(o for o in meshes if o.name==f'R13_S{s:02d}_{part}')
        points=[inv @ (ob.matrix_world @ v.co) for v in ob.data.vertices]
        lo=-1000+s*200; hi=lo+200
        assert abs(min(v.x for v in points)-lo)<.002 and abs(max(v.x for v in points)-hi)<.002
        ends=[]
        for x in (lo,hi):
            ends.append(sorted(tuple(round(float(c),3) for c in v) for v in points if abs(v.x-x)<.002))
        boundaries[s,part]=ends
        if s: assert boundaries[s-1,part][1]==ends[0],(s,part,'coastal seam gap')
        if part=='mosaic':
            us=[u.uv.x for u in ob.data.uv_layers.active.data]
            assert abs((max(us)-min(us))*12-200)<.01,(s,'metric mosaic UV stretched')
        # All surface polygons point up after FBX transform.
        assert all((ob.matrix_world.to_3x3() @ p.normal).z>.9 for p in ob.data.polygons),ob.name
for sector in q['sectors']:
    sector['native_gate']='PASS_REIMPORT_CONTINUITY_UV'
q['status']='R13_NATIVE_FBX_REIMPORT_CONTINUITY_UV_PASS_ART_PENDING'
q['native_blender_version']=bpy.app.version_string
q['native_reimport_meshes']=len(meshes)
q['native_missing_uv0']=0
q['native_contiguous_boundaries']=54
# Compare actual furniture anchors with ORIGINAL road triangles, not guessed widths.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend'))
city=next(o for o in bpy.data.objects if o.type=='MESH' and len(o.data.polygons)==26764)
roads=[]
for p in city.data.polygons:
    if 'road' in city.data.materials[p.material_index].name.lower():
        v=[city.data.vertices[i].co for i in p.vertices]
        roads.append([(float(a.x),float(a.y)) for a in v])
assert len(roads)==3731
def in_tri(p,tri):
    signs=[(p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0]) for a,b in zip(tri,tri[1:]+tri[:1])]
    return not min(signs)<0<max(signs)
for place in q['placements']:
    x,y=place['local_xy']
    for dx,dy in ((-2,-1),(0,0),(6,0),(10,0),(10,1)):
        assert not any(in_tri((x+dx,y+dy),tri) for tri in roads),('furniture in road',place)
q['furniture_anchor_road_gate']='PASS_3731_ORIGINAL_TRIANGLES'
(OUT/'R13_COVERAGE.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
print('R13_NATIVE_REIMPORT_PASS',len(meshes),q['faces'],'54 shared boundaries; UV0 finite; sources intact',flush=True)
