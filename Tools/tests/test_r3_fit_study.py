"""Prevent a future R3 blueprint from placing models outside original OSM outlines."""
import hashlib
import json
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"geo/pilot/R3_MODEL_FIT_STUDY.json"
spec=spec_from_file_location("r3_fit",ROOT/"Tools/geo/study_r3_model_fit.py")
fit=module_from_spec(spec)
spec.loader.exec_module(fit)

class R3FitGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=json.loads(FILE.read_text(encoding="utf-8"))
        sites=json.loads((ROOT/"geo/pilot/R3_EXACT_OSM_PARCELS.json").read_text())
        cls.rings={x["id"]:x["ring_xy_m"] for x in sites["parcels"]}
    def test_each_proposal_has_source_real_fbx_and_conservative_fit(self):
        self.assertEqual(self.study["status"],"R3_GEOMETRY_STUDY_NOT_INTEGRATED_IN_WORLD")
        self.assertEqual(len(self.study["sites"]),3)
        self.assertIn("No Unity prefab",self.study["limits"])
        for oid,v in self.study["sites"].items():
            path=ROOT/v["source_fbx"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),v["source_fbx_sha256"])
            p=v["placement_study"]
            if p["fit"]=="GEOMETRIC_FIT_ONLY":
                self.assertGreaterEqual(p["scale"],.80)
                self.assertLessEqual(p["scale"],1.0)
                self.assertEqual(len(p["proposed_footprint_xy_m"]),4)
                self.assertTrue(all(fit.in_poly(*xy,self.rings[oid])
                                    for xy in p["proposed_footprint_xy_m"]))
                # Recompute the rotated model rectangle, including clearance.
                good,_=fit.valid_rect(p["center_xy_m"],
                    [x*p["scale"] for x in v["original_fbx_dimensions_m"][:2]],
                    __import__("math").radians(p["yaw_blender_degrees"]),
                    self.rings[oid],p["horizontal_clearance_m"]-0.001)
                self.assertTrue(good,oid)
            else:
                self.assertEqual(p["fit"],"NO_CONSERVATIVE_FIT_WITHOUT_GEOMETRY_CHANGES")
    def test_no_fabricated_city_or_actual_heights(self):
        self.assertEqual(self.study["proposed_count"],
          sum(v["placement_study"]["fit"]=="GEOMETRIC_FIT_ONLY" for v in self.study["sites"].values()))
        self.assertIn("no actual building height",self.study["limits"])
        self.assertTrue((ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").is_file())

if __name__=="__main__":
    unittest.main()
