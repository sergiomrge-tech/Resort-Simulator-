"""End-to-end recorded R5 evidence: original GIS geometry, 50 FBX & real Unity DX11.

GitHub Actions verifies the native editor outputs committed after direct execution
on an authorized PC. This test does NOT pretend GitHub ran Unity or FPS benchmarks.
"""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
R5=ROOT/"UnityProject/Assets/Architecture/R5_Pilot50"
SOURCE=ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
ORIGINAL=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

class R5NativeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((R5/"R5_SOURCE_MASK_QA.json").read_text())
        cls.blender=json.loads((R5/"R5_BLENDER_SCENE_QA.json").read_text())
        cls.native=json.loads((ROOT/"ArtSource/Previews/R5_Unity_DX11_Native_QA.json").read_text(encoding="utf-8-sig"))
    def test_two_original_source_hashes_remain_immutable(self):
        self.assertEqual(self.original["source_geo_original_sha256"],sha(SOURCE))
        self.assertEqual(self.original["source_fbx_original_sha256"],sha(ORIGINAL))
        self.assertEqual(self.blender["original_blend_sha256"],sha(SOURCE))
        self.assertEqual(self.blender["original_fbx_sha256"],sha(ORIGINAL))
        self.assertEqual(self.native["original_blend_sha256"],sha(SOURCE))
        self.assertEqual(self.native["original_fbx_sha256"],sha(ORIGINAL))
    def test_exact_osm_mask_and_valid_combined_fbx(self):
        self.assertEqual(self.original["masked_way_count"],50)
        self.assertEqual(self.original["road_faces_removed"],0)
        self.assertEqual(self.blender["new_architecture_count"],50)
        self.assertEqual(self.blender["retained_road_faces"],3731)
        self.assertEqual(self.blender["new_architecture_polygons"],577770)
        path=ROOT/self.blender["derived_fbx"]
        self.assertTrue(path.read_bytes().startswith(b"Kaydara FBX Binary"))
        self.assertEqual(sha(path),self.blender["derived_fbx_sha256"])
    def test_authentic_native_unity_version_scene_and_import_stats(self):
        n=self.native
        self.assertEqual(n["status"],"NATIVE_UNITY_EDITOR_IMPORTED_AND_SCENE_SAVED")
        self.assertEqual(n["unity_version"],"6000.6.2f1")
        self.assertEqual(n["renderer"],"Direct3D11")
        self.assertEqual(n["distinct_replaced_osm_buildings"],50)
        self.assertEqual(n["hero_renderers"],370)
        self.assertEqual(n["source_triangles"],26764)
        self.assertGreater(n["derived_triangles"],1100000)
        self.assertEqual(n["derived_fbx_sha256"],self.blender["derived_fbx_sha256"])
        self.assertFalse(n["visual_approval"])
        self.assertFalse(n["fps_measured"])
        self.assertFalse(n["playable_exe_compiled"])
        scene=ROOT/"UnityProject"/n["scene"]
        self.assertTrue(scene.is_file())
        self.assertGreater(scene.stat().st_size,10000)
        self.assertIn("R5",scene.read_text(encoding="utf-8"))
        self.assertTrue(Path(str(scene)+".meta").is_file())
    def test_real_directx11_screenshots_are_nonuniform_pixel_data(self):
        n=self.native
        for filename,hashkey,statuskey in (
            ("screenshot","screenshot_sha256","screenshot_status"),
            ("closeup_screenshot","closeup_screenshot_sha256","closeup_screenshot_status")):
            self.assertEqual(n[statuskey],"GENUINE_UNITY_CAMERA_RENDER")
            file=ROOT/n[filename]
            self.assertTrue(file.is_file())
            self.assertEqual(sha(file),n[hashkey])
            with Image.open(file) as image:
                self.assertEqual(image.size,(1600,900))
                sample=image.convert("RGB").resize((160,90))
                self.assertGreater(max(ImageStat.Stat(sample).stddev),10)
                self.assertGreater(len(sample.getcolors(maxcolors=14400) or []),60)
    def test_visual_approval_remains_blocked(self):
        n=self.native
        self.assertIn("not final approved",n["qa_observation"])
        self.assertEqual(self.blender["status"],
          "R5_50_SOURCE_OSM_BUILDINGS_REPLACED_IN_AUTHENTIC_BLENDER")
        self.assertIn("NOT final art",self.blender["limits"])

if __name__=="__main__":
    unittest.main()
