"""Data regressions, never a Unity compilation or artistic approval."""
from pathlib import Path
import unittest,json,hashlib
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'UnityProject/Assets/Architecture/R13_Coastal'
class R13Contract(unittest.TestCase):
 def test_frozen_source(self):
  q=json.loads((OUT/'R13_COVERAGE.json').read_text())
  for p,sha in q['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),sha,p)
  self.assertEqual(q['frame_m'],[2000,1000])
  self.assertEqual(q['source_sha256']['ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend'],'2384c677bbb2ef8ef6275cb567ec52e69ff4b9e55d204d76eb0b10dfde2e4ac4')
 def test_native_gate_and_sector_claims(self):
  q=json.loads((OUT/'R13_COVERAGE.json').read_text())
  self.assertEqual(q['status'],'R13_NATIVE_FBX_REIMPORT_CONTINUITY_UV_PASS_ART_PENDING')
  self.assertEqual(q['native_contiguous_boundaries'],54)
  self.assertEqual(q['furniture_anchor_road_gate'],'PASS_3731_ORIGINAL_TRIANGLES')
  self.assertFalse(q['artistic_gate_approved']);self.assertFalse(q['fps_measured'])
  for s in q['sectors']:
   self.assertEqual(s['visual_gate'],'PENDING')
   self.assertEqual(s['geometry']=='GENERATED_REFINED',s['sector'] in q['refined_sectors'])
   self.assertEqual(s['longitudinal_m'],[s['sector']*200,(s['sector']+1)*200])
 def test_asset_hash(self):
  q=json.loads((OUT/'R13_COVERAGE.json').read_text())
  self.assertEqual(hashlib.sha256((OUT/'R13_OSM_Coastal_Sectors.fbx').read_bytes()).hexdigest(),q['fbx_sha256'])
 def test_pbr_maps(self):
  q=json.loads((ROOT/'UnityProject/Assets/Textures/R13_Coastal/R13_SURFACE_ART.json').read_text())
  self.assertEqual(len(q['textures']),12)
  for texture in q['textures']:
   p=ROOT/texture['path'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),texture['sha256'])
   with Image.open(p) as img:
    self.assertEqual(list(img.size),texture['size']);a=np.asarray(img)
   if texture['kind']=='normal':
    v=a.astype(float)/255*2-1;self.assertLess(float(np.abs(np.linalg.norm(v,axis=-1)-1).max()),.02)
   if texture['kind']=='mask':self.assertTrue(np.all(a[:,:,0]==0));self.assertTrue(np.all(a[:,:,3]>0))
 def test_geographic_boundaries(self):
  q=json.loads((OUT/'R13_COVERAGE.json').read_text())
  for a,b in zip(q['sectors'],q['sectors'][1:]):self.assertEqual(a['coast_endpoints_local_xy'][1],b['coast_endpoints_local_xy'][0])
  self.assertEqual(q['sectors'][0]['local_x_m'][0],-1000);self.assertEqual(q['sectors'][-1]['local_x_m'][1],1000)
 def test_real_blender_asset_capture_provenance(self):
  q=json.loads((ROOT/'ArtSource/Previews/R13_BlenderAssetVisualQA.json').read_text())
  self.assertEqual(q['renderer'],'Blender Cycles');self.assertTrue(q['asset_only']);self.assertFalse(q['unity_capture']);self.assertFalse(q['art_approved'])
  self.assertEqual(len(q['captures']),2)
  for capture in q['captures']:
   p=ROOT/capture['path'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),capture['sha256'])
   with Image.open(p) as img:self.assertEqual(img.size,(1600,900))
if __name__=='__main__':unittest.main()
