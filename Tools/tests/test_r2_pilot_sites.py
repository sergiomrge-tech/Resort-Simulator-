"""Source-grounded validation for three R2 pilot OSM parcels."""
import gzip
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
PILOT=ROOT/"geo/pilot/R2_PILOT_BUILDING_CANDIDATES.json"
OSM=ROOT/"geo/data/copacabana.osm.gz"

class PilotOSMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(PILOT.read_text(encoding="utf-8"))
        with gzip.open(OSM,"rb") as src:
            root=ET.parse(src).getroot()
        cls.tags={way.get("id"): {t.get("k"):t.get("v") for t in way.findall("tag")}
                  for way in root.findall("way")}

    def test_three_mapped_distinct_ids_not_guesswork(self):
        selected=self.data["candidates"]
        self.assertEqual(len(selected),3)
        self.assertEqual(len({x["osm_id"] for x in selected}),3)
        for x in selected:
            self.assertTrue(x["osm_id"].startswith("way/"))
            oid=x["osm_id"].split("/",1)[1]
            self.assertIn(oid,self.tags)
            self.assertNotIn(self.tags[oid].get("building"),(None,"no","roof","carport","garage","garages","shed"))
            self.assertGreater(x["footprint_area_m2"],35)
            self.assertLessEqual(x["distance_to_avenida_atlantica_m"],150)
            self.assertEqual(len(x["centroid_lonlat"]),2)

    def test_pilot_dimensions_are_300x300_m_and_frame_matches_original(self):
        frame=json.loads((ROOT/"geo/pilot/COPACABANA_FRAME_SOURCE.json").read_text())
        self.assertEqual(frame["crs"],"EPSG:32723")
        self.assertEqual(frame["game_area_m2"],2_000_000)
        x=self.data["pilot_300x300m_local_bounds"]
        self.assertAlmostEqual(x["max_x"]-x["min_x"],300)
        self.assertAlmostEqual(x["max_y"]-x["min_y"],300)
        for candidate in self.data["candidates"]:
            cx,cy=candidate["centroid_local_m"]
            self.assertLessEqual(x["min_x"],cx)
            self.assertLessEqual(cx,x["max_x"])
            self.assertLessEqual(x["min_y"],cy)
            self.assertLessEqual(cy,x["max_y"])

    def test_no_claim_of_actual_building_height(self):
        self.assertEqual(self.data["status"],"CANDIDATES_NOT_APPROVED")
        self.assertIn("no Unity compile",self.data["limits"])
        self.assertIn("OpenStreetMap",self.data["license"])

if __name__=="__main__":
    unittest.main()
