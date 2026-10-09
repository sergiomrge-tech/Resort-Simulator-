"""R12 visual provenance: real Unity GPU frame hashes & original fictional art PNG."""
from pathlib import Path
import json,struct,hashlib,unittest
ROOT=Path(__file__).resolve().parents[2]
PRE=ROOT/"ArtSource/Previews"
def load(path):return json.loads(path.read_text(encoding="utf-8-sig"))
class R12Capture(unittest.TestCase):
 def test_real_qa_and_frozen_map(self):
  q=load(PRE/"R12_UnityStreetQA.json")
  self.assertEqual(q["status"],"R12_URP_STREETLEVEL_TECHNICAL_PASS_ART_VISUAL_PENDING")
  self.assertEqual(q["renderer"],"Direct3D11")
  self.assertEqual(q["unity_version"],"6000.6.2f1")
  self.assertEqual((q["map_coast_m"],q["map_inland_m"]),(2000,1000))
  self.assertEqual(q["total_buildings"],1468)
  self.assertEqual(q["road_triangles"],3731)
  self.assertEqual(q["trees"],48)
  self.assertEqual(q["r11_renderers"],210)
  self.assertEqual(q["r12_renderers"],19)
  self.assertEqual(q["entrances"],1411)
  self.assertEqual(q["storefronts"],320)
  self.assertEqual(q["glass_showcases"],1627)
  self.assertEqual(q["awnings"],320)
  self.assertEqual(q["fictional_signs"],320)
  self.assertEqual(q["sign_asset_count"],12)
  self.assertEqual(q["invalid_materials"],0)
  self.assertEqual(q["missing_uv0"],0)
  self.assertFalse(q["fps_measured"])
  self.assertFalse(q["artistic_gate_approved"])
 def test_original_art_hashes(self):
  cases=(("R12_SignArt_QA.json","signs",(1024,256),12),
   ("R12_GlassArt_QA.json","textures",(512,1024),2))
  for report,name,size,count in cases:
   q=load(PRE/report)
   self.assertEqual(len(q[name]),count)
   for image in q[name]:
    path=ROOT/image["path"]
    data=path.read_bytes()
    self.assertEqual(data[:8],b"\x89PNG\r\n\x1a\n")
    self.assertEqual(struct.unpack(">II",data[16:24]),size)
    self.assertEqual(hashlib.sha256(data).hexdigest(),image["sha256"])
    self.assertEqual(len(data),image["bytes"])
 def test_real_unity_captures(self):
  report=load(PRE/"R12_VisualNativeQA.json")
  self.assertEqual(report["status"],"R12_REAL_STREET_SHOPFRONTS_CAPTURED_ART_PENDING")
  self.assertEqual(report["renderer"],"Direct3D11")
  self.assertEqual(report["r12_street_renderers"],19)
  self.assertEqual(report["r11_detail_renderers"],210)
  self.assertEqual(report["source_road_triangles"],3731)
  self.assertEqual(len(report["captures"]),9)
  names=set()
  for row in report["captures"]:
   name=row["filename"]
   self.assertNotIn(name,names)
   names.add(name)
   self.assertTrue(name.startswith("R12_") and name.endswith("RealUnity.png"))
   data=(PRE/name).read_bytes()
   self.assertEqual(data[:8],b"\x89PNG\r\n\x1a\n")
   self.assertEqual(struct.unpack(">II",data[16:24]),(1600,900))
   self.assertEqual(len(data),row["bytes"])
   self.assertEqual(hashlib.sha256(data).hexdigest(),row["sha256"])
   self.assertGreater(len(data),100000)
  self.assertIn("R12_08_Fachada_Comercial_RealUnity.png",names)
  self.assertIn("R12_09_Vitrine_Letreiro_RealUnity.png",names)
if __name__=="__main__":unittest.main()
