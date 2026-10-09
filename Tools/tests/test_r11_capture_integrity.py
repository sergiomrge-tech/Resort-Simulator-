"""R11 Unity screenshots are real byte-hashed 1600x900 URP captures, not mocks."""
import hashlib,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREVIEW=ROOT/"ArtSource/Previews"
class R11Validation(unittest.TestCase):
 def test_unity_scene_preserved_origin(self):
  q=json.loads((PREVIEW/"R11_UnityArchitectureQA.json").read_text(encoding="utf-8-sig"))
  self.assertEqual(q["status"],"R11_UNITY_REAL_VOLUMETRY_URP_TECHNICAL_PASS_VISUAL_PENDING")
  self.assertEqual(q["unity_version"],"6000.6.2f1")
  self.assertEqual(q["renderer"],"Direct3D11")
  self.assertEqual(q["all_buildings"],1468)
  self.assertEqual(q["old_road_triangles"],3731)
  self.assertEqual(q["vegetation_osm_count"],48)
  self.assertEqual(q["architecture_renderers"],210)
  self.assertEqual(q["architecture_styles"],50)
  self.assertEqual(q["balconies"],6048)
  self.assertEqual(q["balconied_buildings"],888)
  self.assertEqual(q["rooftop_units"],1414)
  self.assertEqual(q["cornices"],1355)
  self.assertEqual(q["uv0_missing"],0)
  self.assertEqual(q["shaders_invalid"],0)
  self.assertFalse(q["visual_gate_approved"])
  self.assertFalse(q["fps_measured"])
 def test_real_gpu_pngs_and_hashes(self):
  qa=json.loads((PREVIEW/"R11_VisualNativeQA.json").read_text(encoding="utf-8-sig"))
  self.assertEqual(qa["status"],"R11_REAL_URP_DETAILS_CAPTURED_ART_PENDING")
  self.assertEqual(qa["renderer"],"Direct3D11")
  self.assertEqual(qa["r11_detail_renderers"],210)
  self.assertEqual(qa["r8_facade_renderers"],350)
  self.assertEqual(qa["r9_osm_trees"],48)
  self.assertEqual(qa["r10_coastal_meshes"],9)
  self.assertEqual(qa["source_road_triangles"],3731)
  self.assertEqual(len(qa["captures"]),7)
  seen=set()
  for entry in qa["captures"]:
   name=entry["filename"]
   self.assertTrue(name.startswith("R11_") and name.endswith("_RealUnity.png"))
   self.assertNotIn(name,seen)
   seen.add(name)
   data=(PREVIEW/name).read_bytes()
   self.assertEqual(data[:8],b"\x89PNG\r\n\x1a\n")
   self.assertEqual(struct.unpack(">II",data[16:24]),(1600,900))
   self.assertEqual(hashlib.sha256(data).hexdigest(),entry["sha256"])
   self.assertEqual(len(data),entry["bytes"])
   self.assertGreater(len(data),50000)
if __name__=="__main__":unittest.main()
