"""Hard gate for R3 derived pilot: only 2 isolated building components removed.

No GIF screenshots or fake Unity renderer assertions; inspection is genuine Blender.
"""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"ArtSource/Previews/R3_Piloto_Derivado_QA.json"

class R3DerivedPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads(REPORT.read_text(encoding="utf-8"))
    def test_two_models_without_deleting_osm_roads_or_other_buildings(self):
        x=self.report
        self.assertEqual(x["status"],"DERIVED_PILOT_BLENDER_GIS_NOT_UNITY_VALIDATED")
        self.assertEqual(set(x["replacements"]),{"way/1048277518","way/1048277521"})
        self.assertEqual(x["unmodified_third_site"],"way/1308635852")
        self.assertGreaterEqual(x["removed_building_faces"],10)
        self.assertEqual(x["original_road_faces"],x["retained_road_faces"])
        self.assertEqual(x["original_faces"]-x["removed_building_faces"],x["retained_city_faces"])
        for data in x["replacements"].values():
            self.assertGreaterEqual(data["old_building_faces"],5)
            self.assertEqual(data["source_materials"],["Building"])
            self.assertLess(data["source_building_z_bounds_m"][0],
                            data["source_building_z_bounds_m"][1])
        self.assertGreater(x["authored_model_mesh_objects"],2)
    def test_export_binary_and_original_blender_source_immutable(self):
        x=self.report
        o=ROOT/x["pilot_derived_fbx"]
        self.assertTrue(o.is_file())
        self.assertGreater(o.stat().st_size,350000)
        self.assertEqual(hashlib.sha256(o.read_bytes()).hexdigest(),x["pilot_derived_fbx_sha256"])
        self.assertTrue(o.read_bytes().startswith(b"Kaydara FBX Binary"))
        self.assertTrue(Path(str(o)+".meta").is_file())
        src=ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
        fbx=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),x["source_original_blend_sha256"])
        self.assertEqual(hashlib.sha256(fbx.read_bytes()).hexdigest(),x["source_original_fbx_sha256"])
    def test_render_is_real_and_not_gameplay_screenshot(self):
        x=self.report
        im=ROOT/x["preview"]
        self.assertTrue(im.is_file())
        self.assertEqual(hashlib.sha256(im.read_bytes()).hexdigest(),x["preview_sha256"])
        with Image.open(im) as image:
            self.assertEqual(image.size,(1600,1000))
            small=image.convert("RGB").resize((160,100))
            self.assertGreater(max(ImageStat.Stat(small).stddev),12)
            self.assertGreater(len(small.getcolors(maxcolors=16000) or []),140)
        self.assertIn("Not Unity compiled or final art",x["limits"])
        self.assertEqual(x["engine"],"Blender Cycles CPU")

if __name__=="__main__":
    unittest.main()
