"""R13 regression gates for actual Unity 6000.6.2f1 importer and native GPU captures.

Runs on a clean GitHub checkout without Unity installed; it validates
provenance and exact-byte evidence generated in the real Windows Editor.
"""
import json,hashlib,re,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/"UnityProject/Assets"
PRE=ROOT/"ArtSource/Previews"
def j(path):return json.loads(path.read_text(encoding="utf-8-sig"))
class R13NativeUnityContracts(unittest.TestCase):
 def test_texture_importers_are_true_2d_and_guids_stable(self):
  texture_dir=ASSET/"Textures/R13_Coastal"
  metas=sorted(texture_dir.glob("r13_*.png.meta"))
  self.assertEqual(len(metas),12)
  ids=set()
  for file in metas:
   s=file.read_text(encoding="utf-8-sig")
   match=re.search(r"(?m)^guid: ([a-f0-9]{32})$",s)
   self.assertIsNotNone(match,file.name)
   self.assertNotIn(match.group(1),ids)
   ids.add(match.group(1))
   self.assertIn("TextureImporter:",s,file.name)
   self.assertIn("serializedVersion: 13",s,file.name)
   self.assertIn("textureShape: 1",s,file.name)
   self.assertNotIn("textureShape: 2",s,file.name)
   normal=file.name.endswith("_normal.png.meta")
   base=file.name.endswith("_base.png.meta")
   self.assertIn("  textureType: 1" if normal else "  textureType: 0",s,file.name)
   self.assertIn("    sRGBTexture: 1" if base else "    sRGBTexture: 0",s,file.name)
 def test_fbx_metre_scale_is_explicit(self):
  file=ASSET/"Architecture/R13_Coastal/R13_OSM_Coastal_Sectors.fbx.meta"
  s=file.read_text(encoding="utf-8-sig")
  self.assertRegex(s,r"(?m)^guid: [a-f0-9]{32}$")
  self.assertIn("ModelImporter:",s)
  self.assertIn("serializedVersion: 24600",s)
  self.assertRegex(s,r"(?m)^    globalScale: 1$")
  self.assertRegex(s,r"(?m)^    useFileUnits: 1$")
  self.assertNotIn("    globalScale: 100",s)
 def test_real_unity_import_and_provenance(self):
  q=j(PRE/"R13_UnityTechnicalQA.json")
  self.assertEqual(q["status"],"R13_UNITY_TECHNICAL_PASS_ART_PENDING")
  self.assertEqual(q["unity_version"],"6000.6.2f1")
  self.assertEqual(q["renderer"],"Direct3D11")
  self.assertEqual(q["meshes"],120)
  self.assertEqual(q["road_triangles"],3731)
  self.assertEqual(q["trees"],48)
  self.assertEqual(q["missing_uv0"],0)
  self.assertEqual(q["shader_errors"],0)
  self.assertFalse(q["artistic_gate_approved"])
  self.assertFalse(q["fps_measured"])
  f=ASSET/"Architecture/R13_Coastal/R13_OSM_Coastal_Sectors.fbx"
  self.assertEqual(q["fbx_sha256"],hashlib.sha256(f.read_bytes()).hexdigest())
 def test_native_unity_comparison_12_frames(self):
  q=j(PRE/"R13_VisualNativeQA.json")
  self.assertEqual(q["status"],"R13_REAL_UNITY_CAPTURED_ART_PENDING")
  self.assertEqual(q["unity_version"],"6000.6.2f1")
  self.assertEqual(q["renderer"],"Direct3D11")
  self.assertFalse(q["artistic_gate_approved"])
  self.assertFalse(q["fps_measured"])
  self.assertFalse(q["playmode_water_animation_tested"])
  frames=q["captures"]
  self.assertEqual(len(frames),12)
  for version in ("before","after"):
   sub=j(PRE/f"R13_VisualNativeQA_{version}.json")
   self.assertEqual(len(sub["captures"]),6)
   self.assertEqual([x["sha256"] for x in sub["captures"]],
                    [x["sha256"] for x in frames if f"_{version}_" in x["filename"]])
  seen=set()
  for frame in frames:
   n=frame["filename"]
   self.assertNotIn(n,seen)
   seen.add(n)
   self.assertRegex(n,r"^R13_S05_(before|after)_(day|late)_(walk|coast|shore)_RealUnity\.png$")
   self.assertEqual(frame["warmup_frames"],5)
   p=PRE/n
   raw=p.read_bytes()
   self.assertEqual(raw[:8],b"\x89PNG\r\n\x1a\n")
   self.assertEqual(struct.unpack(">II",raw[16:24]),(1600,900))
   self.assertGreater(len(raw),50000)
   self.assertEqual(hashlib.sha256(raw).hexdigest(),frame["sha256"])
   self.assertEqual(frame["source_scene"],
    "Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity"
    if "_before_" in n else
    "Assets/Scenes/R13_Copacabana_200m_Premium.unity")
  self.assertEqual(len(seen),12)
  for i in range(6):
   before,after=frames[i],frames[i+6]
   self.assertEqual(before["lighting"],after["lighting"])
   for component in ("position","target"):
    for axis in ("x","y","z"):
     self.assertAlmostEqual(before[component][axis],after[component][axis],places=3)
if __name__=="__main__":unittest.main()
