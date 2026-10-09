"""Native roundtrip of real coastal kit meshes and all placement envelopes."""
from pathlib import Path
import bpy,sys,json,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tools/geo'),str(ROOT/'Tools/Blender')]
from r14_geometry import load_domains, Polygon
OUT=ROOT/'UnityProject/Assets/Architecture/R14_Urban'
def main():
    q=json.loads((OUT/'R14_ART_NATIVE.json').read_text());a,roads,lots,rows,prom,domains,ramps=load_domains()
    assert hashlib.sha256((OUT/'R14_Coastal_Art_Seven_Sectors.fbx').read_bytes()).hexdigest()==q['fbx_sha256']
    for p,h in q['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    for place in q['placements']:
        a=place['xy'];t=place['t'];n=place['n'];u,v=place['envelope_uv_m']
        poly=Polygon([(a[0]+t[0]*xx+n[0]*yy,a[1]+t[1]*xx+n[1]*yy) for xx,yy in ((-u,-v),(u,-v),(u,v),(-u,v))])
        assert prom.covers(poly) and not poly.intersects(roads.buffer(.35)) and not poly.intersects(lots.buffer(.5)),place
    assert {p['variant'] for p in q['placements'] if p['kind']=='kiosk'}=={0,1,2}
    assert len({r['osm_id'] for r in q['facades']})==len(q['facades'])
    assert {r['osm_id'] for r in q['facades']}<={r['building_id'] for r in rows}
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(OUT/'R14_Coastal_Art_Seven_Sectors.fbx'))
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    from generate_r9_urban_environment import GEO_ROT
    inv=GEO_ROT.inverted();bounds={}
    actual={o.name:len(o.data.polygons) for o in meshes}
    assert actual==q['mesh_faces'],{k:(q['mesh_faces'].get(k),v) for k,v in actual.items() if v!=q['mesh_faces'].get(k)}
    for o in meshes:
        pts=[inv @ (o.matrix_world @ v.co) for v in o.data.vertices]
        bounds[o.name]=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
        assert o.data.uv_layers.active and len(o.data.uv_layers.active.data)==len(o.data.loops),o.name
        assert all(math.isfinite(v) for uv in o.data.uv_layers.active.data for v in uv.uv)
        assert len(o.data.materials)==1 and o.data.materials[0]
        assert all(p.area>1e-8 for p in o.data.polygons),o.name
        if not '_LOD' in o.name:
            counts=[len(next(p for p in meshes if p.name==o.name+suffix).data.polygons) for suffix in ('','_LOD1','_LOD2')]
            assert counts[0]>counts[1]>counts[2]>0,(o.name,counts)
    q.update(status='R14_ART_NATIVE_FBX_REIMPORT_PASS_ART_PENDING',native_blender_version=bpy.app.version_string,native_missing_uv0=0,native_placement_envelopes_checked=len(q['placements']),native_lod_batches=len(meshes)//3,
       native_material_slots={o.name:[m.name for m in o.data.materials] for o in meshes},native_mesh_bounds_local_m=bounds)
    (OUT/'R14_ART_NATIVE.json').write_text(json.dumps(q,indent=2)+'\n')
    print('R14_ART_NATIVE_PASS',len(meshes),len(q['placements']),len(q['facades']),flush=True)
if __name__=='__main__':main()
