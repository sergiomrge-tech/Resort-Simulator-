"""Validate saved *actual Unity QA* PNG headers, hashes, geodata and flags.
Captures are executed in the Windows Unity Editor, not forged by this test.
"""
import hashlib,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PRE=ROOT/"ArtSource/Previews"
class R10UnityCaptureProvenance(unittest.TestCase):
 def test_technical_report_and_frozen_map(self):
  tech=json.loads((PRE/"R10_UnityTechnicalQA.json").read_text(encoding="utf-8-sig"))
  self.assertEqual(tech["status"],"R10_UNITY_URP_COPACABANA_ART_TECHNICAL_PASS_VISUAL_GATE_PENDING")
  self.assertEqual(tech["unity_version"],"6000.6.2f1")
  self.assertEqual(tech["renderer"],"Direct3D11")
  self.assertEqual(tech["geographic_roads_triangles"],3731)
  self.assertEqual(tech["detailed_background_facades"],350)
  self.assertEqual(tech["trees"],48)
  self.assertEqual(tech["promenade_meshes"],9)
  self.assertEqual(tech["facade_material_variants"],150)
  self.assertEqual(tech["coast_samples"],401)
  self.assertTrue(tech["sea_shader_compiled"])
  self.assertFalse(tech["aerial_shadows_temporarily_disabled"])
  self.assertFalse(tech["visual_gate_approved"])
  self.assertFalse(tech["fps_measured"])
  frame=json.loads((ROOT/"geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf-8-sig"))
  self.assertEqual(frame["along_coast_length_m"],2000)
  self.assertEqual(frame["inland_width_m"],1000)
 def test_real_unity_image_byte_hash_and_resolution(self):
  info=json.loads((PRE/"R10_VisualNativeQA.json").read_text(encoding="utf-8-sig"))
  self.assertEqual(info["status"],"R10_REAL_URP_ART_CAPTURED_VISUAL_GATE_PENDING")
  self.assertEqual(info["renderer"],"Direct3D11")
  self.assertEqual(info["r8_facade_renderers"],350)
  self.assertEqual(info["r9_osm_trees"],48)
  self.assertEqual(info["r10_coastal_meshes"],9)
  self.assertEqual(info["source_road_triangles"],3731)
  self.assertEqual(len(info["captures"]),5)
  names=set()
  for item in info["captures"]:
   self.assertTrue(item["filename"].startswith("R10_"))
   self.assertNotIn(item["filename"],names)
   names.add(item["filename"])
   raw=(PRE/item["filename"]).read_bytes()
   self.assertTrue(raw.startswith(b"\x89PNG\r\n\x1a\n"))
   self.assertEqual(struct.unpack(">II",raw[16:24]),(1600,900))
   self.assertEqual(hashlib.sha256(raw).hexdigest(),item["sha256"])
   self.assertEqual(len(raw),item["bytes"])
   self.assertGreater(len(raw),180000)
if __name__=="__main__":unittest.main()
