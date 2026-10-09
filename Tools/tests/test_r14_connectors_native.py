"""Independent Blender FBX roundtrip: metres, normals, UV, GIS exclusion, seams."""
from pathlib import Path
import bpy,sys,json,math,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tools/geo'),str(ROOT/'Tools/Blender')]
from r14_geometry import load_domains, box, Point
from generate_r9_urban_environment import GEO_ROT
OUT=ROOT/'UnityProject/Assets/Architecture/R14_Urban'
def main():
    q=json.loads((OUT/'R14_CONNECTORS_NATIVE.json').read_text())
    a,roads,lots,rows,prom,domains,ramps=load_domains()
    from shapely import prepare
    road_interior=roads.buffer(-.002);prepare(road_interior);prepare(lots)
    assert len(rows)==1468 and len(a['road_triangles'])==3731
    assert q['frame_m']==[2000,1000] and q['angle_degrees']==46
    for p,h in q['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert hashlib.sha256((OUT/'R14_GIS_Urban_Connectors.fbx').read_bytes()).hexdigest()==q['fbx_sha256']
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(OUT/'R14_GIS_Urban_Connectors.fbx'))
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    assert len(meshes)==q['meshes']
    assert {o.name:len(o.data.polygons) for o in meshes}==q['mesh_faces']
    inv=GEO_ROT.inverted();boundaries={};checked=0;max_uv_error=0
    for ob in meshes:
        s=int(ob.name[5:7]);key=ob.name[8:];lo=-1000+s*200;hi=lo+200
        assert len(ob.data.materials)==1 and ob.data.materials[0].name.startswith('R14_'+key)
        assert ob.data.uv_layers.active and len(ob.data.uv_layers.active.data)==len(ob.data.loops)
        assert all(math.isfinite(c) for uv in ob.data.uv_layers.active.data for c in uv.uv)
        pts=[inv @ (ob.matrix_world @ v.co) for v in ob.data.vertices]
        assert min(v.x for v in pts)>=lo-.002 and max(v.x for v in pts)<=hi+.002,ob.name
        assert min(v.y for v in pts)>=-500.002 and max(v.y for v in pts)<=500.002
        assert max(v.z for v in pts)<.201 and min(v.z for v in pts)>-.026
        valid=domains[key].intersection(box(lo,-500,hi,500))
        assert valid.intersection(lots).area<1e-6
        if key!='gutter':assert valid.intersection(roads).area<1e-6
        # Independent footprint/road test from reimported top triangle centroids.
        for p in ob.data.polygons:
            vertices=[pts[i] for i in p.vertices]
            n=(vertices[1]-vertices[0]).cross(vertices[2]-vertices[0])
            assert n.length>1e-9,(ob.name,'degenerate')
            if n.normalized().z>.8:
                center=sum(vertices,Vector())/3;point=Point(center.x,center.y)
                assert not lots.contains(point),(ob.name,'footprint')
                if key!='gutter':assert not road_interior.contains(point),(ob.name,'road')
                # Actual UV edge distances / actual 3D metres must be sane.
                uvs=[ob.data.uv_layers.active.data[i].uv for i in p.loop_indices]
                for i in range(3):
                    distance=(vertices[i]-vertices[(i+1)%3]).length
                    uvlength=(uvs[i]-uvs[(i+1)%3]).length*2
                    if distance>.01:
                        error=abs(uvlength/distance-1);max_uv_error=max(max_uv_error,error)
                        assert error<.035,(ob.name,'UV stretch',error)
                checked+=1
            elif n.normalized().z<-.8:
                assert all(abs(v.z+.025)<.002 for v in vertices),(ob.name,'inverted top',[list(v) for v in vertices],list(n.normalized()))
        # Unique vertex positions at cut boundaries, measured after FBX import.
        boundaries[s,key]=[sorted(set((round(v.y,3),round(v.z,3)) for v in pts if abs(v.x-x)<.002)) for x in (lo,hi)]
    seam_checks=[]
    for s in range(1,10):
        for key in domains:
            left=boundaries.get((s-1,key),[[],[]])[1];right=boundaries.get((s,key),[[],[]])[0]
            # Segmentization may sample cuts differently. Check point-to-segment
            # coverage independently in 2D boundary profiles, tolerance 2mm.
            if left or right:
                from shapely.geometry import MultiPoint
                l=MultiPoint(left);r=MultiPoint(right)
                d=l.hausdorff_distance(r) if left and right else float('inf')
                assert d<.002,(s,key,'seam',d)
                seam_checks.append({'boundary':s,'part':key,'max_gap_m':d})
    q.update(status='R14_NATIVE_FBX_REIMPORT_PASS_ART_PENDING',native_blender_version=bpy.app.version_string,
       native_missing_uv0=0,native_meshes=len(meshes),native_top_triangles_checked=checked,
       native_uv_metric_max_error=max_uv_error,native_boundaries=seam_checks,native_source_invariants='PASS',
       native_material_slots={o.name:[m.name for m in o.data.materials] for o in meshes},
       native_lot_and_road_exclusion='PASS_REIMPORTED_TOP_TRIANGLE_CENTROIDS')
    for s in q['sectors']:s['native_gate']='PASS_REIMPORT_GIS_UV_NORMALS'
    (OUT/'R14_CONNECTORS_NATIVE.json').write_text(json.dumps(q,indent=2)+'\n')
    print('R14_NATIVE_REIMPORT_PASS',len(meshes),checked,'seams',len(seam_checks),flush=True)
if __name__=='__main__':main()
