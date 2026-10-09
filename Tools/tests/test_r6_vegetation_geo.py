"""R6 GIS pilot integrity, determinism, spacing and original-source protection."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Tools/geo/generate_r6_vegetation.py"
OUTPUT = ROOT / "geo/procedural/R6_VEGETATION_INSTANCES.json"
BLEND = ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
FBX = ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
OSM = ROOT / "geo/data/copacabana.osm.gz"
EXPECTED = {
    "blend": "2384C677BBB2EF8EF6275CB567EC52E69FF4B9E55D204D76EB0B10DFDE2E4AC4",
    "fbx": "2546AD26546713D40008C395A1A0D00EB2A3F90C1681F0BBBE3AD2C5410D9339",
    "osm": "8FA230FC41B40234D4E37E17AA18B1BB697A20E33750293D440E110E8EE0BD8F",
}
SPEC = importlib.util.spec_from_file_location("r6_vegetation", SCRIPT)
r6 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r6)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class R6VegetationGeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.instances = cls.payload["instances"]

    def test_original_blender_fbx_and_osm_sources_have_expected_hashes(self):
        self.assertEqual(sha(BLEND), EXPECTED["blend"])
        self.assertEqual(sha(FBX), EXPECTED["fbx"])
        self.assertEqual(sha(OSM), EXPECTED["osm"])

    def test_source_frame_preserves_real_area_and_46_degree_transform(self):
        frame_json = json.loads((ROOT / "geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf-8"))
        self.assertEqual(frame_json["axis_angle_degrees_counterclockwise_from_east"], 46.0)
        self.assertEqual(frame_json["along_coast_length_m"] * frame_json["inland_width_m"], 2_000_000)
        self.assertEqual(self.payload["source"]["axis_angle_degrees_counterclockwise_from_east"], 46.0)
        self.assertEqual(self.payload["source"]["area_m2"], 2_000_000)
        self.assertEqual(self.payload["counts"]["osm_tree_nodes_in_snapshot"], 632)
        self.assertGreaterEqual(self.payload["counts"]["valid_after_gis_guards"], 48)

    def test_only_unique_osm_nodes_with_clearance_and_roi_bounds(self):
        ids = [item["osm_id"] for item in self.instances]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.instances), 48)
        xy = []
        for item in self.instances:
            self.assertRegex(item["osm_id"], r"^node/\d+$")
            self.assertEqual(item["origin"], "OpenStreetMap natural=tree point; ODbL 1.0")
            x, y = item["coordinates"]["local_m_xy"]
            self.assertTrue(-1000 <= x <= 1000 and -500 <= y <= 500)
            guards = item["guards"]
            self.assertGreaterEqual(guards["road_centerline_distance_m"], guards["road_clearance_required_m"])
            self.assertGreaterEqual(guards["minimum_road_clearance_margin_m"], 0.0)
            self.assertGreaterEqual(guards["building_edge_distance_m"], 1.5)
            xy.append((x, y))
        for i, p in enumerate(xy):
            for q in xy[i+1:]:
                self.assertGreaterEqual(math.dist(p, q), 3.0)

    def test_seed_and_output_are_deterministic(self):
        for item in self.instances:
            self.assertEqual(item["seed"], r6.seed_for(item["osm_id"].split("/")[-1]))
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "instances.json"
            r6.main(["--pilot-count", "48", "--output", str(target)])
            self.assertEqual(target.read_bytes(), OUTPUT.read_bytes())

    def test_density_sample_has_no_duplicate_positions(self):
        positions = [tuple(x["coordinates"]["local_m_xy"]) for x in self.instances]
        self.assertEqual(len(positions), len(set(positions)))
        categories = self.payload["counts"]["categories"]
        self.assertIn("arvore_de_rua_osm", categories)
        self.assertIn("arvore_em_calcada_ou_lote_osm", categories)


if __name__ == "__main__":
    unittest.main()
