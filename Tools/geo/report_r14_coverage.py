"""Report actual generated R14 inventory. Visual gates bind to exact FBX bytes."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def main():
    c=read('UnityProject/Assets/Architecture/R14_Urban/R14_CONNECTORS_NATIVE.json')
    a=read('UnityProject/Assets/Architecture/R14_Urban/R14_ART_NATIVE.json')
    previous=read('ArtSource/Previews/R13_Pass2_Coverage.json')
    native=ROOT/'ArtSource/Previews/R14_UnityTechnicalQA.json';captures=ROOT/'ArtSource/Previews/R14_VisualNativeQA.json'
    unity=read(native.relative_to(ROOT)) if native.exists() else {}
    photos=read(captures.relative_to(ROOT)) if captures.exists() else {}
    valid=all(unity.get(k)==v for k,v in [('connector_fbx_sha256',c['fbx_sha256']),('art_fbx_sha256',a['fbx_sha256'])])
    bound=valid and all(photos.get(k)==v for k,v in [('connector_fbx_sha256',c['fbx_sha256']),('art_fbx_sha256',a['fbx_sha256'])])
    sectors=[]
    for i in range(10):
        sector=f'S{i:02d}';old=previous['sectors'][i];cr=c['sectors'][i]
        places=[p for p in a['placements'] if p['sector']==sector];facades=[f for f in a['facades'] if f['sector']==sector]
        cn=[n for n in c['mesh_faces'] if n.startswith('R14_'+sector+'_')];an=[n for n in a['mesh_faces'] if n.startswith('R14_'+sector+'_')]
        bounds=a.get('native_mesh_bounds_local_m',{})
        outside=[n for n in an if n in bounds and (bounds[n][0][1]<-500 or bounds[n][1][1]>500)]
        shots=[p['filename'] for p in photos.get('captures',[]) if p['filename'].startswith('R14_'+sector+'_after') and bound]
        before_shots=[p['filename'] for p in photos.get('captures',[]) if p['filename'].startswith('R14_'+sector+'_before') and bound]
        sectors.append({'sector':sector,'status':'INTERMEDIARIO' if cn or an or old['status']=='INTERMEDIARIO' else 'BASE',
          'previous_status':old['status'],'local_x_m':cr['local_x_m'],'connector_meshes':len(cn),'connector_triangles':sum(c['mesh_faces'][n] for n in cn),'parts':cr['parts'],
          'art_meshes_including_lod':len(an),'art_triangles_including_lod':sum(a['mesh_faces'][n] for n in an),
          'art_meshes_outside_inland_frame':outside,'coastal_art_bounds_gate':'PENDING_R13_COAST_FRAME_RECONCILIATION' if outside else 'WITHIN_INLAND_FRAME',
          'urban_groups_new':sum(p['kind']=='urban_group' for p in places),'palms_new':sum(p['kind']=='palm' for p in places),
          'kiosks_new':sum(p['kind']=='kiosk' for p in places),'kiosk_variants':[p['variant'] for p in places if p['kind']=='kiosk'],
          'facades_new':len(facades),'facade_osm_ids':[p['osm_id'] for p in facades],
          'original_osm_trees_total':48,'r13_groups_preserved':old['furniture']['groups'],
          'ramps_inferred':len(cr['ramps']),'fictional_planting':True,'promenade_road_gap':cr.get('promenade_landward_edge_to_road_sample_distance_m',{}),
          'qa':{'connectors_native':c['status'],'art_native':a['status'],'unity_gate':'PASS_NATIVE' if valid else 'PENDING',
                'unity_captures':shots,'unity_before_captures':before_shots,'visual_gate':'CAPTURED_REVIEW_PENDING' if shots else 'PENDING','art_approved':False}})
    q={'stage':'R14_URBAN_FINISH_PARTIAL_ART_PENDING','base_commit':'5217a65','frame_m':[2000,1000],
       'connector_fbx_sha256':c['fbx_sha256'],'art_fbx_sha256':a['fbx_sha256'],'sectors':sectors,
       'connectors_meshes':c['meshes'],'art_meshes':a['meshes'],'source_invariants':c.get('native_source_invariants','PENDING'),
       'unity_native_gate':'PASS_NATIVE' if valid else 'PENDING','r14_unity_png_count':len(photos.get('captures',[])) if bound else 0,
       'r14_unity_after_png_count':sum(len(s['qa']['unity_captures']) for s in sectors),
       'fps_measured':False,'gameplay_integrated':False,'artistic_gate_approved':False,
       'limits':c['limitations']+['Connector LOD decimation and gap closure across missing GIS substrate pending; no premium approval.']}
    (ROOT/'ArtSource/Previews/R14_SectorCoverage.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('R14_REAL_COVERAGE',c['meshes'],a['meshes'],'new groups',sum(s['urban_groups_new'] for s in sectors),'Unity',q['r14_unity_png_count'])
if __name__=='__main__':main()
