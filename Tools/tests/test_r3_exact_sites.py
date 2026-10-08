"""R3 cloud-only data/geometry safety gate. No fake Unity/visual approval."""
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SITES=ROOT/"geo/pilot/R3_EXACT_OSM_PARCELS.json"
PROBE=ROOT/"ArtSource/Previews/R3_Pilot_OSM_Geometry_Probe.json"
EXPECTED={"way/1048277518","way/1308635852","way/1048277521"}

def polygon_area(ring):
    return abs(sum(x*v-y*u for (x,y),(u,v) in zip(ring,ring[1:])))/2

class R3ExactSitesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(SITES.read_text(encoding="utf-8"))
        cls.probe=json.loads(PROBE.read_text(encoding="utf-8"))
    def test_three_real_osm_rings_from_frozen_source(self):
        self.assertEqual(self.data["parcel_count"],3)
        sites=self.data["parcels"]
        self.assertEqual({x["id"] for x in sites},EXPECTED)
        original=json.loads((ROOT/"geo/pilot/R2_PILOT_BUILDING_CANDIDATES.json").read_text())
        before={x["osm_id"]:x for x in original["candidates"]}
        for s in sites:
            pts=s["ring_xy_m"]
            self.assertGreaterEqual(len(pts),4)
            self.assertEqual(pts[0],pts[-1])
            self.assertAlmostEqual(polygon_area(pts),s["footprint_area_m2"],delta=.15)
            self.assertLess(math.dist(before[s["id"]]["centroid_local_m"],s["centroid_local_xy_m"]),.025)
            self.assertIsNone(s["actual_height_m"])
    def test_model_source_integrity_and_geographic_limits(self):
        self.assertTrue((ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").exists())
        self.assertTrue((ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").exists())
        self.assertIn("NOT legal parcel boundaries",self.data["limits"])
        self.assertIn("OpenStreetMap",self.data["copyright"])
        self.assertEqual(self.data["status"],"EXACT_OSM_FOOTPRINTS_GEOMETRY_ONLY")
    def test_blender_probe_observes_original_source_only(self):
        self.assertEqual(self.probe["status"],"INSPECTED_SOURCE_NOT_MODIFIED")
        self.assertEqual(self.probe["no_mutation"],"READ_ONLY_BPY_NO_WRITE_BLEND_OR_FBX")
        self.assertGreaterEqual(self.probe["total_source_faces"],26000)
        self.assertEqual({x["id"] for x in self.probe["parcels"]},EXPECTED)
        self.assertIn("replacement requires component isolation",self.probe["limits"])
        for item in self.probe["parcels"]:
            self.assertGreaterEqual(item["hits"],0)
            self.assertGreaterEqual(item["boundary_hits"],0)
            self.assertIsInstance(item["source_materials"],dict)

if __name__=="__main__":
    unittest.main()
