"""Verifies actual Blender-rendered GIS preview and three exact OSM site rings."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"ArtSource/Previews/R3_Orla_300m_Blender_QA.json"

class R3RealGISPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(REPORT.read_text(encoding="utf-8"))
    def test_genuine_blender_source_unmodified_and_three_osm_sites(self):
        d=self.d
        self.assertEqual(d["status"],"GENUINE_BLENDER_GIS_WITH_OSM_OVERLAYS")
        self.assertEqual(d["visual_stage"],"OSM_PARCEL_LOCATION_QA_ONLY")
        self.assertEqual(d["render_engine"],"Blender Cycles CPU")
        self.assertGreaterEqual(d["city_faces"],26000)
        self.assertEqual({s["id"] for s in d["sites"]},
          {"way/1048277518","way/1308635852","way/1048277521"})
        for s in d["sites"]:
            self.assertEqual(s["ring_xy_m"][0],s["ring_xy_m"][-1])
        src=ROOT/d["source_blend"]
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),d["source_blend_sha256"])
        fbx=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
        self.assertEqual(hashlib.sha256(fbx.read_bytes()).hexdigest(),d["source_fbx_sha256"])
    def test_real_png_pixel_variation_and_scope(self):
        d=self.d
        png=ROOT/d["preview"]
        self.assertTrue(png.is_file())
        self.assertEqual(hashlib.sha256(png.read_bytes()).hexdigest(),d["preview_sha256"])
        with Image.open(png) as image:
            self.assertEqual(image.size,(1600,1100))
            sample=image.convert("RGB").resize((160,110))
            self.assertGreater(max(ImageStat.Stat(sample).stddev),15)
            self.assertGreater(len(sample.getcolors(maxcolors=17600) or []),110)
        self.assertIn("No replacement/new buildings",d["limits"])
        self.assertIn("OpenStreetMap",d["copyright"])

if __name__=="__main__":
    unittest.main()
