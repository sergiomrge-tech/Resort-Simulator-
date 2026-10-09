"""Evidence and importer regression contracts; never premium/benchmark approval."""
from pathlib import Path
import json,hashlib,re,unittest
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def j(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
class R14(unittest.TestCase):
 def test_frozen_originals(self):
  q=j('ArtSource/Previews/R14_SourceAudit.json')
  self.assertEqual(len(q['road_triangles']),3731);self.assertEqual(q['footprints'],1468);self.assertEqual(q['original_trees'],48)
  for p,h in q['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
 def test_native_export_and_seams(self):
  q=j('UnityProject/Assets/Architecture/R14_Urban/R14_CONNECTORS_NATIVE.json')
  self.assertEqual(q['status'],'R14_NATIVE_FBX_REIMPORT_PASS_ART_PENDING');self.assertEqual(q['native_missing_uv0'],0)
  self.assertEqual(q['meshes'],31);self.assertEqual(len(q['sectors']),10);self.assertGreater(q['native_top_triangles_checked'],90000)
  self.assertLess(q['native_uv_metric_max_error'],.035)
  self.assertTrue(q['native_boundaries']);self.assertTrue(all(b['max_gap_m']<.002 for b in q['native_boundaries']))
  self.assertEqual(q['frame_m'],[2000,1000]);self.assertEqual(q['curb_rise_m'],.14)
  self.assertEqual(hashlib.sha256((ROOT/'UnityProject/Assets/Architecture/R14_Urban/R14_GIS_Urban_Connectors.fbx').read_bytes()).hexdigest(),q['fbx_sha256'])
 def test_actual_art_inventory(self):
  q=j('UnityProject/Assets/Architecture/R14_Urban/R14_ART_NATIVE.json')
  self.assertEqual(q['status'],'R14_ART_NATIVE_FBX_REIMPORT_PASS_ART_PENDING');self.assertEqual(q['native_missing_uv0'],0)
  self.assertEqual(q['native_lod_batches'],35);self.assertEqual(q['meshes'],105)
  self.assertEqual(sum(p['kind']=='urban_group' for p in q['placements']),49)
  self.assertEqual(sum(p['kind']=='palm' for p in q['placements']),12)
  self.assertEqual(sum(p['kind']=='kiosk' for p in q['placements']),7)
  self.assertEqual({p['variant'] for p in q['placements'] if p['kind']=='kiosk'},{0,1,2})
  self.assertEqual(len(q['facades']),37);self.assertEqual(len({r['osm_id'] for r in q['facades']}),37)
  self.assertEqual(hashlib.sha256((ROOT/'UnityProject/Assets/Architecture/R14_Urban/R14_Coastal_Art_Seven_Sectors.fbx').read_bytes()).hexdigest(),q['fbx_sha256'])
 def test_honest_coverage(self):
  q=j('ArtSource/Previews/R14_SectorCoverage.json');self.assertEqual([s['sector'] for s in q['sectors']],[f'S{i:02d}' for i in range(10)])
  self.assertFalse(q['fps_measured']);self.assertFalse(q['artistic_gate_approved']);self.assertFalse(q['gameplay_integrated'])
  self.assertEqual(sum(s['urban_groups_new'] for s in q['sectors']),49)
  for s in q['sectors']:
   self.assertIn(s['status'],['BASE','INTERMEDIARIO']);self.assertFalse(s['qa']['art_approved'])
   if s['previous_status']=='INTERMEDIARIO':self.assertEqual(s['r13_groups_preserved'],8);self.assertEqual(s['urban_groups_new'],0)
 def test_complete_texture_importers(self):
  q=j('UnityProject/Assets/Textures/R14_Urban/R14_SURFACE_ART.json');self.assertEqual(len(q['textures']),24);seen=set()
  for f in q['textures']:
   p=ROOT/f['path'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
   with Image.open(p) as image:self.assertEqual(image.size,(1024,1024))
   s=Path(str(p)+'.meta').read_text();guid=re.search(r'^guid: (\w+)$',s,re.M).group(1);self.assertNotIn(guid,seen);seen.add(guid)
   self.assertIn('serializedVersion: 13',s);self.assertIn('textureShape: 1',s);self.assertIn('enableMipMap: 1',s)
   self.assertIn('  textureType: 1' if f['kind']=='normal' else '  textureType: 0',s)
   self.assertIn('    sRGBTexture: 1' if f['kind']=='base' else '    sRGBTexture: 0',s)
 def test_model_import_units(self):
  for p in (ROOT/'UnityProject/Assets/Architecture/R14_Urban').glob('*.fbx.meta'):
   s=p.read_text();self.assertRegex(s,r'(?m)^    globalScale: 1$');self.assertIn('useFileUnits: 1',s)
 def test_pedestrian_pbr_detail(self):
  for key in ('asphalt','sidewalk','curbstone','gutter','stonetile'):
   base=np.asarray(Image.open(ROOT/f'UnityProject/Assets/Textures/R14_Urban/r14_{key}_base.png'))
   self.assertGreater(float(base.std()),1.5);self.assertLess(float(base.mean()),155)
   mask=np.asarray(Image.open(ROOT/f'UnityProject/Assets/Textures/R14_Urban/r14_{key}_mask.png'))
   self.assertLess(float(mask[:,:,3].mean())/255,.25);self.assertEqual(int(mask[:,:,0].max()),0)
 def test_unity_if_present(self):
  p=ROOT/'ArtSource/Previews/R14_UnityTechnicalQA.json'
  if not p.exists():self.skipTest('Unity gate pending, no native report')
  q=json.loads(p.read_text());self.assertEqual(q['unity_version'],'6000.6.2f1');self.assertEqual(q['renderer'],'Direct3D11');self.assertEqual(q['urp_version'],'17.6.0')
  for key in ('missing_uv0','shader_errors','missing_material_slots','default_materials'):self.assertEqual(q[key],0)
  self.assertEqual(q['road_triangles'],3731);self.assertEqual(q['original_trees'],48)
 def test_capture_pairing_if_present(self):
  p=ROOT/'ArtSource/Previews/R14_VisualNativeQA.json'
  if not p.exists():self.skipTest('Capture gate pending, no invented frames')
  q=json.loads(p.read_text());self.assertEqual(len(q['captures']),72)
  before=j('ArtSource/Previews/R14_VisualNativeQA_before.json');after=j('ArtSource/Previews/R14_VisualNativeQA_after.json')
  for a,b in zip(before['captures'],after['captures']):
   for key in ('position','target','lighting','sun_euler','sun_intensity','sun_shadow_strength','width','height','field_of_view'):self.assertEqual(a[key],b[key])
  for row in q['captures']:
   p=ROOT/'ArtSource/Previews'/row['filename'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['sha256']);self.assertEqual(Image.open(p).size,(1600,900));self.assertEqual(row['warmup_frames'],5)
if __name__=='__main__':unittest.main()
