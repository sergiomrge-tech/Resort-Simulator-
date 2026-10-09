"""Evidence that all fifty real 3D architectural recipes were generated in Blender."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"UnityProject/Assets/Architecture/R4_Procedural"
REPORT=BASE/"R4_GALLERY_GENERATION_REPORT.json"
CATALOG=ROOT/"ArtSource/ProceduralBuildings/Resort50Styles.json"

class R4FullFiftyMeshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(REPORT.read_text(encoding="utf-8"))
        cls.cat=json.loads(CATALOG.read_text(encoding="utf-8"))
    def test_exactly_fifty_real_distinct_architectures(self):
        data=self.data
        self.assertEqual(data["status"],"ACTUAL_PROCEDURAL_BLENDER_FBX_GENERATED_NOT_UNITY_VALIDATED")
        self.assertEqual(data["mode"],"gallery")
        self.assertEqual(data["count"],50)
        self.assertEqual(data["skipped_count"],0)
        self.assertEqual({m["style_id"] for m in data["meshes"]},
                         {s["id"] for s in self.cat["styles"]})
        self.assertEqual(len({m["fbx"] for m in data["meshes"]}),50)
        self.assertEqual(len({m["unity_asset_guid"] for m in data["meshes"]}),50)
        for m in data["meshes"]:
            self.assertGreater(m["polygons_generated"],100)
            self.assertGreater(m["windows"],5)
            self.assertEqual(hashlib.sha256((ROOT/m["fbx"]).read_bytes()).hexdigest(),m["fbx_sha256"])
            self.assertTrue((ROOT/m["fbx"]).read_bytes().startswith(b"Kaydara FBX Binary"))
    def test_five_real_blender_rendered_sheets_show_50_buildings(self):
        pics=self.data["real_blender_previews"]
        self.assertEqual(len(pics),5)
        self.assertEqual(sum(x["building_count"] for x in pics),50)
        for item in pics:
            f=ROOT/item["path"]
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),item["sha256"])
            self.assertGreater(item["bytes"],45000)
            self.assertEqual(item["engine"],"CYCLES")
            with Image.open(f) as im:
                self.assertEqual(im.size,(1800,1080))
                sd=ImageStat.Stat(im.convert("RGB").resize((160,100))).stddev
                self.assertGreater(max(sd),10)
    def test_original_gis_sources_and_art_catalog_unchanged(self):
        src=ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
        fbx=ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
        d=self.data
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),d["source_map_sha256"])
        self.assertEqual(hashlib.sha256(fbx.read_bytes()).hexdigest(),d["source_city_fbx_sha256"])
        self.assertEqual(hashlib.sha256(CATALOG.read_bytes()).hexdigest(),d["catalog_sha256"])
        self.assertIn("not a Unity-built/imported map",d["limits"])
if __name__=="__main__":
    unittest.main()
