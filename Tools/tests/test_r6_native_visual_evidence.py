"""R6 native screenshot evidence integrity: hash, dimensions, and truthful failure gates.
The report records previously executed Windows Unity DX11; this test does not run Unity.
"""
import hashlib
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = ROOT / "ArtSource/Previews"
SCREENSHOTS = PREVIEWS / "R6_VisualNativeQA.json"
MATERIALS = PREVIEWS / "R6_Material_Pass_NativeQA.json"


class R6NativeVisualEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qa = json.loads(SCREENSHOTS.read_text(encoding="utf-8-sig"))
        cls.materials = json.loads(MATERIALS.read_text(encoding="utf-8-sig"))

    def test_editor_and_genuine_four_screenshots(self):
        q = self.qa
        self.assertEqual(q["status"], "R6_NATIVE_UNITY_CAPTURE_COMPLETED_ART_GATE_PENDING")
        self.assertEqual(q["unity_version"], "6000.6.2f1")
        self.assertEqual(q["renderer"], "Direct3D11")
        self.assertEqual(len(q["screenshots"]), 4)
        for record in q["screenshots"]:
            path = PREVIEWS / record["filename"]
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertGreater(path.stat().st_size, 25000)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record["sha256"])
            with path.open("rb") as stream:
                self.assertEqual(stream.read(8), b"\x89PNG\r\n\x1a\n")
                self.assertEqual(stream.read(4), b"\x00\x00\x00\r")
                self.assertEqual(stream.read(4), b"IHDR")
                self.assertEqual(struct.unpack(">II",stream.read(8)),(1600,900))
        self.assertEqual(len({shot["osm_way"] for shot in q["screenshots"]}),3)

    def test_uv_visual_gate_is_blocked_despite_native_pass(self):
        q = self.qa
        self.assertEqual(q["recognized_buildings"], 50)
        self.assertEqual(q["recognized_renderers"], 370)
        self.assertEqual(q["meshes_without_uv0"], 370)
        self.assertEqual(q["materials_using_r6"], 370)
        self.assertEqual(q["shader_pipeline"], "BUILT_IN_STANDARD_FALLBACK")
        self.assertFalse(q["artistic_gate_passed"])
        self.assertFalse(q["fps_measured"])
        self.assertEqual(self.materials["selected_buildings"],50)
        self.assertEqual(self.materials["distinct_styles"],50)
        self.assertEqual(self.materials["finished_renderers"],370)
        self.assertEqual(self.materials["material_part_name_fallbacks"],370)
        self.assertEqual(self.materials["material_assets"],160)
        self.assertEqual(self.materials["texture_assets"],40)
        self.assertFalse(self.materials["urp_pipeline_active"])

    def test_originals_unchanged_and_documented(self):
        expected={
            ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend":
            self.materials["source_blend_sha256"],
            ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx":
            self.materials["source_fbx_sha256"],
        }
        for file,sha in expected.items():
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),sha)
        text=(ROOT / "docs/arte/R6_RESULTADO_UNITY_NATIVE_20261009.md").read_text()
        self.assertIn("REPROVADA",text)
        self.assertIn("370/370",text)


if __name__ == "__main__":
    unittest.main()
