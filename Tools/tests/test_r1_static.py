import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "UnityProject/Assets"
MODEL = ASSETS / "ImportedBlender/Copacabana_Real_Blender.fbx"


class R1GeographyStaticTests(unittest.TestCase):
    def test_original_real_blender_model_present_and_not_tiny(self):
        self.assertGreater(MODEL.stat().st_size, 400_000)
        self.assertEqual(MODEL.open("rb").read(18), b"Kaydara FBX Binary")
        self.assertTrue((ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").exists())

    def test_geography_source_is_real_and_two_square_kilometres(self):
        report = json.loads((ROOT / "geo/data/report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["game_area_m2"], 2_000_000)
        self.assertEqual(report["real_osm_entities_within_roi"]["building"], 1468)
        self.assertEqual(report["real_osm_entities_within_roi"]["road"], 468)

    def test_scene_builder_uses_real_fbx_and_no_secondary_rotation(self):
        text = (ASSETS / "Editor/ResortWorldBuilder.cs").read_text()
        self.assertIn("Assets/ImportedBlender/Copacabana_Real_Blender.fbx", text)
        self.assertIn("PrefabUtility.InstantiatePrefab(model)", text)
        self.assertIn("CharacterController", text)
        self.assertIn("SaveScene(current, ScenePath)", text)
        self.assertNotRegex(text, r"root\.transform\.rotation\s*=\s*Quaternion\.Euler\(-90f")
        self.assertIn("bounds", text.lower())

    def test_player_controls_exist(self):
        code = (ASSETS / "Scripts/PlayerController.cs").read_text()
        for word in ("CharacterController", "Keyboard.current", "Mouse.current",
                     "Mouse X", "jumpHeight", "gravity", "WASD"):
            self.assertIn(word, code)
        self.assertIn("#if ENABLE_INPUT_SYSTEM", code)
        self.assertIn("#elif ENABLE_LEGACY_INPUT_MANAGER", code)

    def test_day_night_is_independent_and_active(self):
        code = (ASSETS / "Scripts/DayNightCycle.cs").read_text()
        for word in ("SetHour", "SetSun", "ApplyLighting", "Mathf.Sin", "sun.intensity"):
            self.assertIn(word, code)
        self.assertNotIn("EconomyManager", code)

    def test_original_asset_has_fixed_import_guid(self):
        meta = (MODEL.parent / (MODEL.name + ".meta")).read_text()
        self.assertRegex(meta, r"guid: [0-9a-f]{32}")
        self.assertEqual(len(set(re.findall(r"guid: ([0-9a-f]{32})",
                                            "\n".join(p.read_text() for p in ASSETS.rglob("*.meta"))))),
                         len(re.findall(r"guid: ([0-9a-f]{32})",
                                        "\n".join(p.read_text() for p in ASSETS.rglob("*.meta")))))

    def test_unity_metadata_and_license_gate(self):
        manifest = json.loads((ROOT / "UnityProject/Packages/manifest.json").read_text())
        self.assertIn("com.unity.render-pipelines.universal", manifest["dependencies"])
        ci = (ROOT / ".github/workflows/r1-unity-cloud.yml").read_text()
        self.assertIn("NOT_BUILT: LICENSE_MISSING", ci)
        self.assertIn("game-ci/unity-builder@v4", ci)
        self.assertIn("StandaloneWindows64", ci)


if __name__ == "__main__":
    unittest.main()
