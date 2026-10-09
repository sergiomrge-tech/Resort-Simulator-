"""Build factual per-sector coverage from the exported census and verified PNGs.
Missing Unity evidence stays PENDING; no artistic approval is inferred.
"""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
PRE=ROOT/'ArtSource/Previews'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 q=json.loads((ROOT/'UnityProject/Assets/Architecture/R13_Pass2/R13_Pass2_NATIVE.json').read_text())
 art=json.loads((ROOT/'UnityProject/Assets/Textures/R13_Pass2/R13_Pass2_SURFACE_ART.json').read_text())
 frames=[]
 for phase in ('before','after'):
  path=PRE/f'R13_Pass2_VisualNativeQA_{phase}.json'
  if path.exists():
   report=json.loads(path.read_text());assert report['unity_version']=='6000.6.2f1' and report['renderer']=='Direct3D11'
   for f in report['captures']:
    assert sha(PRE/f['filename'])==f['sha256'];frames.append(f)
 assignments=json.loads((ROOT/'geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json').read_text())['buildings']
 rows=[]
 for s in q['sectors']:
  n=s['sector'];detail=n in q['refined_sectors'];prefix=f'R13_S{n:02d}_'
  places=[p for p in q['placements'] if p['sector']==n]
  shots=[f['filename'] for f in frames if f'_S{n:02d}_after_' in f['filename']]
  ids=[r['building_id'] for r in assignments if r['building_id'] in q['facade_osm_ids'] and s['local_x_m'][0]<=r['centroid_local_xy_m'][0]<s['local_x_m'][1]]
  rows.append({'sector':f'S{n:02d}','status':'INTERMEDIARIO' if detail else 'BASE',
   'model_count':sum(k.startswith(prefix) for k in q['mesh_faces']),
   'materials':['sand','wet_sand','mosaic','ocean','asphalt','pavement']+(['limestone','timber','metal','leaves','soil'] if detail else []),
   'vegetation':{'planters':len(places),'original_osm_trees_total':48,'tree_uv0_gate':'PENDING_UNITY'},
   'furniture':{'groups':len(places),'families':['bench','planter','bin','cycle_stand','lantern'] if detail else []},
   'sea_sand_mosaic':{'generated':True,'native_gate':s['native_gate'],'continuous_boundaries_total':q.get('native_contiguous_boundaries',0)},
   'adjacent_buildings':{'decorative_facade_count':len(ids),'osm_ids':ids,'accessible_interiors':False},
   'QA_evidence':{'native':'UnityProject/Assets/Architecture/R13_Pass2/R13_Pass2_NATIVE.json','unity_captures':shots,'visual_gate':'CAPTURED_REVIEW_PENDING' if shots else 'PENDING','art_approved':False}})
 technical=PRE/'R13_Pass2_UnityTechnicalQA.json'
 if technical.exists():
  t=json.loads(technical.read_text());assert t['fbx_sha256']==q['fbx_sha256'] and t['missing_uv0']==0 and t['tree_missing_uv0']==0 and t['texture2d_count']==21
  for r in rows:r['vegetation']['tree_uv0_gate']='PASS_UNITY_DERIVED'
 result={'frame_m':[2000,1000],'fbx_sha256':q['fbx_sha256'],'surface_sectors':q['surface_sectors'],'detailed_sectors':q['refined_sectors'],'pbr_texture_count':len(art['textures']),'artistic_gate_approved':False,'sectors':rows}
 (PRE/'R13_Pass2_Coverage.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print('R13_PASS2_FACTUAL_COVERAGE',len(rows),'sectors',len(frames),'verified GPU frames')
if __name__=='__main__':main()
