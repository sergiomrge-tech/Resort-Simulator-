"""Validation of 50 original procedural recipes and frozen OSM assignment.

No claim of 3D model generation, Blender import, Unity render or visual approval.
"""
import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools/geo"))
from assign_r4_city_styles import stable_int, floor_origin, choose_family

CATALOG=ROOT/"ArtSource/ProceduralBuildings/Resort50Styles.json"
PLANS=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
OSM=ROOT/"geo/data/copacabana.osm.gz"

class R4ProceduralStyleQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.plan=json.loads(PLANS.read_text(encoding="utf-8"))
    def test_fifty_real_structurally_distinct_facade_recipes(self):
        c=self.catalog
        self.assertEqual(c["status"],"FIFTY_PROCEDURAL_RECIPES_ONLY_NOT_FBX_OR_UNITY_PREFABS")
        self.assertEqual(len(c["families"]),10)
        self.assertEqual(len(c["styles"]),50)
        self.assertEqual(len({x["id"] for x in c["styles"]}),50)
        self.assertEqual({x["family"] for x in c["styles"]},{x["id"] for x in c["families"]})
        for family in {x["family"] for x in c["styles"]}:
            subset=[x for x in c["styles"] if x["family"]==family]
            self.assertEqual(len(subset),5)
            for k in ("window_pattern","balcony_type","ground_floor","parapet_type","roof_detail",
                      "window_frame_depth_m","facade_recess_m","color_preset"):
                self.assertGreaterEqual(len({str(s[k]) for s in subset}),3)
        for style in c["styles"]:
            self.assertFalse(style["actual_mesh_generated"])
            self.assertGreater(style["window_frame_depth_m"],0.04)
            self.assertGreater(style["facade_recess_m"],0.09)
    def test_assignments_use_source_osm_ids_and_no_fabricated_heights(self):
        p=self.plan
        self.assertEqual(p["status"],"R4_REAL_OSM_STYLE_BLUEPRINT_NO_MESH")
        self.assertEqual(p["source_sha256"],hashlib.sha256(OSM.read_bytes()).hexdigest())
        self.assertEqual(p["style_catalog_sha256"],hashlib.sha256(CATALOG.read_bytes()).hexdigest())
        self.assertEqual(p["num_styles_available"],50)
        self.assertGreaterEqual(p["num_styles_assigned"],30)
        self.assertGreaterEqual(p["num_buildings_assigned"],1200)
        self.assertLessEqual(p["num_buildings_assigned"],1468)
        self.assertEqual(len(p["buildings"]),p["num_buildings_assigned"])
        self.assertEqual(len({x["building_id"] for x in p["buildings"]}),len(p["buildings"]))
        self.assertEqual(set(x["style_id"] for x in p["buildings"]),set(p["style_uses"]))
        self.assertEqual(sum(p["style_uses"].values()),len(p["buildings"]))
        self.assertTrue(all(x["has_final_generated_mesh"] is False for x in p["buildings"]))
        self.assertTrue(all(x["requires_visual_art_approval"] for x in p["buildings"]))
        self.assertEqual(sum(p["height_provenance"].values()),p["num_buildings_assigned"])
        self.assertIn("ESTIMATE_NOT_SURVEYED",p["height_provenance"])
        for building in p["buildings"]:
            self.assertEqual(building["height_for_visualization_m"],18.0
                if building["height_provenance"]=="ESTIMATE_NOT_SURVEYED"
                else building["height_for_visualization_m"])
            self.assertEqual(building["seed"],stable_int(building["building_id"],"stable-procedural-seed")%2147483647)
            self.assertEqual(building["source_osm_way"],building["building_id"].split("#")[0])
            self.assertEqual(building["footprint_ring_local_xy_m"][0],
                             building["footprint_ring_local_xy_m"][-1])
            cx,cy=building["centroid_local_xy_m"]
            self.assertTrue(-1000.01<=cx<=1000.01)
            self.assertTrue(-500.01<=cy<=500.01)
        self.assertIn("No generated facade meshes",p["important"])
    def test_stable_hash_and_unverified_building_use(self):
        self.assertEqual(stable_int("way/1048277518","stable-procedural-seed"),
                         stable_int("way/1048277518","stable-procedural-seed"))
        self.assertNotEqual(stable_int("way/1048277518","stable-procedural-seed"),
                            stable_int("way/1048277521","stable-procedural-seed"))
        self.assertEqual(floor_origin({})[1],"ESTIMATE_NOT_SURVEYED")
        self.assertEqual(floor_origin({"building:levels":"8"})[0:2],
                         (24.0,"OSM_LEVELS_ESTIMATE_3M_PER_FLOOR"))
        self.assertEqual(floor_origin({"height":"12m"})[0:2],(12.0,"OSM_EXPLICIT_HEIGHT_M"))
        self.assertEqual(floor_origin({"height":"eleven"})[1],"ESTIMATE_NOT_SURVEYED")
        self.assertEqual(choose_family({"building":"yes"},25.0,"way/981")[1],
                         "UNVERIFIED_VISUAL_STYLE_ONLY")
        self.assertEqual(choose_family({"building":"hotel"},25.0,"way/981")[1],
                         "OSM_USE_HINT")

if __name__=="__main__":
    unittest.main()
