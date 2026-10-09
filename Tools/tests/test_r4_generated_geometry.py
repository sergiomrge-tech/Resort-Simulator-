"""Auditable R4 actual 3D geometry gates (not a Unity runtime/playable build)."""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"ArtSource/ProceduralBuildings/Resort50Styles.json"
ASSIGN=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
OUT=ROOT/"UnityProject/Assets/Architecture/R4_Procedural"
REPORT=OUT/"R4_PILOT_GENERATION_REPORT.json"

class R4RealGeneratedMeshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads(REPORT.read_text(encoding="utf-8"))
        cls.catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.plan=json.loads(ASSIGN.read_text(encoding="utf-8"))
    def test_ten_actual_osm_footprints_and_unique_style_families(self):
        r=self.report
        self.assertEqual(r["status"],"ACTUAL_PROCEDURAL_BLENDER_FBX_GENERATED_NOT_UNITY_VALIDATED")
        self.assertEqual(r["mode"],"pilot")
        self.assertEqual(r["count"],10)
        self.assertEqual(len(r["meshes"]),10)
        self.assertEqual(len({x["family"] for x in r["meshes"]}),10)
        self.assertEqual(len({x["building_id"] for x in r["meshes"]}),10)
        self.assertEqual(r["total_source_buildings"],1468)
        orig={x["building_id"]:x for x in self.plan["buildings"]}
        for m in r["meshes"]:
            self.assertEqual(m["style_id"],orig[m["building_id"]]["style_id"])
            self.assertEqual(m["seed"],orig[m["building_id"]]["seed"])
            self.assertEqual(m["source_ring_local_xy_m"],orig[m["building_id"]]["footprint_ring_local_xy_m"])
            self.assertIn(m["height_provenance"],
               ("OSM_EXPLICIT_HEIGHT_M","OSM_LEVELS_ESTIMATE_3M_PER_FLOOR","ESTIMATE_NOT_SURVEYED"))
            self.assertIsNone(m["measured_height_m"])
    def test_meshes_are_complex_real_binary_fbx_placed_with_stable_unity_meta(self):
        for building in self.report["meshes"]:
            path=ROOT/building["fbx"]
            self.assertTrue(path.is_file(),path)
            self.assertTrue(path.read_bytes().startswith(b"Kaydara FBX Binary"))
            self.assertGreater(path.stat().st_size,25000)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),building["fbx_sha256"])
            self.assertEqual(path.stat().st_size,building["fbx_bytes"])
            meta=Path(str(path)+".meta")
            self.assertIn("guid: "+building["unity_asset_guid"],meta.read_text())
            self.assertGreater(building["polygons_generated"],100)
            self.assertGreater(building["vertices_generated"],400)
            self.assertGreater(building["windows"],5)
            self.assertGreater(building["solid_boxes"],30)
            self.assertGreaterEqual(building["balconies"],0)
            self.assertGreaterEqual(building["roof_features"],1)
        self.assertTrue(Path(str(OUT)+".meta").exists())
        self.assertTrue(Path(str(OUT/"FBX")+".meta").exists())
    def test_real_blender_pixels_and_immutable_real_city(self):
        r=self.report
        self.assertEqual(len(r["real_blender_previews"]),1)
        shot=r["real_blender_previews"][0]
        self.assertEqual(shot["building_count"],10)
        image=ROOT/shot["path"]
        self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),shot["sha256"])
        with Image.open(image) as im:
            self.assertEqual(im.size,(1800,1080))
            small=im.convert("RGB").resize((180,108))
            self.assertGreater(max(ImageStat.Stat(small).stddev),12)
            self.assertGreater(len(small.getcolors(maxcolors=180*108) or []),250)
        self.assertEqual(hashlib.sha256(CATALOG.read_bytes()).hexdigest(),r["catalog_sha256"])
        self.assertEqual(hashlib.sha256(ASSIGN.read_bytes()).hexdigest(),r["assignments_sha256"])
        for name,expected in (
            ("ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend",r["source_map_sha256"]),
            ("UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx",r["source_city_fbx_sha256"])):
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)
        self.assertEqual(r["excluded_R3_hero_ids"],["way/1048277518","way/1048277521"])
        self.assertIn("not a Unity-built/imported map",r["limits"])

if __name__=="__main__":
    unittest.main()
