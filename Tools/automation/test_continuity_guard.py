import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).with_name("continuity_guard.py")
spec = importlib.util.spec_from_file_location("continuity_guard", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ContinuityGuardTests(unittest.TestCase):
    def test_repo_baseline_integrity(self):
        baseline = json.loads((ROOT / "docs/checkpoints/ASSET_BASELINE.json").read_text())
        report = guard.evaluate(ROOT, baseline)
        failures = [x for x in report["checks"] if not x["pass"]]
        self.assertEqual(failures, [])
        self.assertEqual(report["status"], "PASS")
        self.assertGreaterEqual(len(report["checks"]), 12)

    def test_git_blob_hash_matches_git_rules(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "sample.txt"
            p.write_bytes(b"hello world\n")
            self.assertEqual(guard.git_blob_hash(p),
                             "3b18e512dba79e4c8300dd08aeb37f8e728b8dad")

    def test_missing_binary_fails_without_fabricating_files(self):
        baseline = {
            "report": "geo/data/report.json",
            "map_area_m2": 2_000_000,
            "entities": {"building": 1468},
            "assets": [{"id": "missing", "path": "missing.blend",
                        "min_bytes": 10, "git_blob_sha1": None}],
        }
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "geo/data").mkdir(parents=True)
            (root / "geo/data/report.json").write_text(json.dumps({
                "game_area_m2": 2_000_000,
                "real_osm_entities_within_roi": {"building": 1468}
            }))
            result = guard.evaluate(root, baseline)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any(x["check"] == "asset-missing-exists" and not x["pass"]
                                for x in result["checks"]))

    def test_wrong_area_fails_even_with_assets(self):
        baseline = json.loads((ROOT / "docs/checkpoints/ASSET_BASELINE.json").read_text())
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "geo/data").mkdir(parents=True)
            (root / "geo/data/report.json").write_text(json.dumps({
                "game_area_m2": 4_000_000,
                "real_osm_entities_within_roi": baseline["entities"]
            }))
            result = guard.evaluate(root, baseline)
            self.assertFalse(next(x for x in result["checks"]
                                  if x["check"] == "map-area-2km2")["pass"])


if __name__ == "__main__":
    unittest.main()
