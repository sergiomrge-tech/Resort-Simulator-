"""Static regression contracts for native Pass2 outputs; not artistic approval."""
from pathlib import Path
import hashlib,json,re,unittest
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
def j(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
class Pass2(unittest.TestCase):
 def test_export_and_frozen_sources(self):
  q=j('UnityProject/Assets/Architecture/R13_Pass2/R13_Pass2_NATIVE.json')
  self.assertEqual(q['native_missing_uv0'],0);self.assertEqual(q['native_contiguous_boundaries'],54)
  for p,h in q['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
  self.assertEqual(hashlib.sha256((ROOT/'UnityProject/Assets/Architecture/R13_Pass2/R13_VisualPass2_Coastal_Sectors.fbx').read_bytes()).hexdigest(),q['fbx_sha256'])
 def test_coverage_honesty(self):
  q=j('ArtSource/Previews/R13_Pass2_Coverage.json');self.assertEqual(q['surface_sectors'],list(range(10)))
  self.assertEqual(q['detailed_sectors'],[4,5,6]);self.assertFalse(q['artistic_gate_approved'])
  for s in q['sectors']:
   self.assertIn(s['status'],['BASE','INTERMEDIARIO']);self.assertFalse(s['QA_evidence']['art_approved'])
   self.assertEqual(s['furniture']['groups'],8 if s['sector'] in ['S04','S05','S06'] else 0)
   for p in s['QA_evidence']['unity_captures']:self.assertTrue((ROOT/'ArtSource/Previews'/p).exists())
 def test_maps_and_importers(self):
  q=j('UnityProject/Assets/Textures/R13_Pass2/R13_Pass2_SURFACE_ART.json');self.assertEqual(len(q['textures']),21)
  guids=set()
  for f in q['textures']:
   p=ROOT/f['path'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
   s=Path(str(p)+'.meta').read_text();self.assertIn('serializedVersion: 13',s);self.assertIn('textureShape: 1',s)
   guid=re.search(r'^guid: (\w+)$',s,re.M).group(1);self.assertNotIn(guid,guids);guids.add(guid)
   self.assertIn('  textureType: 1' if '_normal' in p.name else '  textureType: 0',s)
   self.assertIn('    sRGBTexture: 1' if '_base' in p.name else '    sRGBTexture: 0',s)
  meta=(ROOT/'UnityProject/Assets/Architecture/R13_Pass2/R13_VisualPass2_Coastal_Sectors.fbx.meta').read_text()
  self.assertRegex(meta,r'(?m)^    globalScale: 1$');self.assertIn('useFileUnits: 1',meta)
 def test_sand_has_lower_albedo_and_fine_normal(self):
  for kind in ['sand','wet_sand']:
   p=ROOT/f'UnityProject/Assets/Textures/R13_Pass2/r13_{kind}_base.png'
   data=np.asarray(Image.open(p))/255;self.assertLess(float(data.mean()),.56);self.assertGreater(float(data.mean()),.25)
  p=ROOT/'UnityProject/Assets/Textures/R13_Pass2/r13_sand_mask.png'
  self.assertLess(np.asarray(Image.open(p))[:,:,3].mean()/255,.06)
 def test_real_unity_if_present(self):
  for phase in ['before','after']:
   p=ROOT/f'ArtSource/Previews/R13_Pass2_VisualNativeQA_{phase}.json'
   if not p.exists():continue
   q=json.loads(p.read_text());self.assertEqual(q['unity_version'],'6000.6.2f1');self.assertEqual(q['renderer'],'Direct3D11');self.assertEqual(len(q['captures']),18)
   for f in q['captures']:
    p=ROOT/'ArtSource/Previews'/f['filename'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256']);self.assertEqual(Image.open(p).size,(1600,900));self.assertEqual(f['warmup_frames'],5)
if __name__=='__main__':unittest.main()
