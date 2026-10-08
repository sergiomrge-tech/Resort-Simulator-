"""CI QA for cloud reconstruction of owner's detailed kiosk, not Unity compile."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/"ArtSource/Previews/Owned_KioskPremium_QA.json"
PNG=ROOT/"ArtSource/Previews/Owned_KioskPremium_Blender_QA.png"
FBX=ROOT/"UnityProject/Assets/Architecture/OwnedKiosk/KioskPremium_Detailed.fbx"
SCRIPT=ROOT/"ArtSource/LocalProjectOwned/KioskPremium_20261008/build_kiosk_premium.py"
SOURCED=ROOT/"ArtSource/LocalProjectOwned/KioskPremium_20261008/SOURCE.json"

class OwnedKioskRebuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v=json.loads(QA.read_text(encoding="utf-8"))

    def test_recreated_original_mesh_geometry_and_source_provenance(self):
        v=self.v
        old=json.loads(SOURCED.read_text(encoding="utf-8"))
        self.assertEqual(v["status"],"PASS")
        self.assertIn("BLENDER_NOT_UNITY",v["scope"])
        self.assertEqual(v["source_script_sha256"],hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
        self.assertEqual(v["source_components"],old["components"])
        self.assertGreater(v["triangles"],50000)
        self.assertGreater(v["polygons"],20000)
        self.assertTrue(v["source_components"]>=300)

    def test_real_binary_fbx_is_staged_with_stable_unity_guid(self):
        v=self.v
        self.assertTrue(FBX.is_file())
        self.assertGreater(FBX.stat().st_size,75000)
        with FBX.open("rb") as s:
            self.assertEqual(s.read(18),b"Kaydara FBX Binary")
        self.assertEqual(hashlib.sha256(FBX.read_bytes()).hexdigest(),v["unity_fbx_sha256"])
        self.assertEqual(FBX.stat().st_size,v["unity_fbx_bytes"])
        meta=Path(str(FBX)+".meta").read_text()
        self.assertIn("guid: "+v["unity_fbx_guid"],meta)
        self.assertRegex(v["unity_fbx_guid"],r"^[a-f0-9]{32}$")
        self.assertTrue(Path(str(FBX.parent)+".meta").is_file())

    def test_preview_contains_actual_nonempty_blender_render(self):
        v=self.v
        self.assertTrue(PNG.is_file())
        self.assertEqual(hashlib.sha256(PNG.read_bytes()).hexdigest(),v["preview_sha256"])
        self.assertIn("Blender Cycles CPU",v["render_engine"])
        with Image.open(PNG) as im:
            self.assertEqual(im.size,(1600,900))
            small=im.convert("RGB").resize((160,90))
            self.assertGreater(max(ImageStat.Stat(small).stddev),12)
            self.assertGreater(len(small.getcolors(maxcolors=160*90) or []),150)

    def test_original_gis_is_not_replaced_and_no_false_unity_claim(self):
        self.assertTrue((ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").is_file())
        self.assertTrue((ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").is_file())
        self.assertIn("not Unity compiled",self.v["limits"])
        self.assertIn("Original",self.v["license"])


if __name__=="__main__":
    unittest.main()
