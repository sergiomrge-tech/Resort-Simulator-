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

    def test_inspection_mode_and_real_screenshot_hook(self):
        source = (ASSETS / "Scripts/PlayerController.cs").read_text()
        for needle in (
            "freeFly = !freeFly", "character.enabled = !freeFly",
            "inspectionFlySpeed", "KeyCode.F", "keys.fKey",
            "KeyCode.F12", "keys.f12Key", "ScreenCapture.CaptureScreenshot(file)",
            "Application.persistentDataPath", "Vector3.up * flyUp",
        ):
            self.assertIn(needle, source)
        self.assertIn("Q/E: descer/subir", source)
        self.assertNotIn("RenderTexture", source)

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

    def test_qa_materials_are_persistent_and_support_urp_color(self):
        source = (ASSETS / "Editor/ResortWorldBuilder.cs").read_text(encoding="utf-8")
        self.assertIn('AssetDatabase.CreateAsset(mat, path)', source)
        self.assertIn('AssetDatabase.LoadAssetAtPath<Material>(path)', source)
        self.assertIn('mat.SetColor("_BaseColor", tint)', source)
        self.assertIn('mat.SetColor("_Color", tint)', source)
        self.assertNotIn('mat.color = tint', source)

    def test_blender_fbx_roundtrip_is_mandatory_without_unity_license(self):
        script = (ROOT / "Tools/Blender/validate_copacabana_roundtrip.py").read_text()
        self.assertIn("bpy.ops.wm.open_mainfile", script)
        self.assertIn("bpy.ops.import_scene.fbx", script)
        self.assertIn("verify_bounds(original, roundtrip)", script)
        self.assertIn('scope": "BLENDER_FBX_ROUNDTRIP_ONLY_NOT_UNITY"', script)
        workflow = (ROOT / ".github/workflows/r1-unity-cloud.yml").read_text()
        self.assertIn("blender-fbx-roundtrip:", workflow)
        self.assertIn("Tools/Blender/validate_copacabana_roundtrip.py", workflow)
        # Only a successful Unity license gate may invoke game-ci; Blender QA
        # must remain independent and runnable without that secret.
        blender_job = workflow.split("  blender-fbx-roundtrip:", 1)[1].split("  unity-windows:", 1)[0]
        self.assertNotIn("needs: static-qa", blender_job)
        self.assertNotIn("if: needs.static-qa.outputs.licensed", blender_job)

    def test_urp_is_created_and_activated_for_pbr(self):
        urp = (ASSETS / "Editor/ResortRenderingSetup.cs").read_text()
        builder = (ASSETS / "Editor/ResortWorldBuilder.cs").read_text()
        for needle in (
            "UniversalRendererData", "UniversalRenderPipelineAsset.Create(renderer)",
            "GraphicsSettings.defaultRenderPipeline = pipeline",
            "QualitySettings.renderPipeline = null", "ColorSpace.Linear",
            "AssetDatabase.CreateAsset(pipeline, PipelinePath)",
        ):
            self.assertIn(needle, urp)
        self.assertIn("ResortRenderingSetup.EnsureConfigured()", builder)
        self.assertTrue((ASSETS / "Editor/ResortRenderingSetup.cs.meta").exists())

    def test_import_metrics_created_only_in_real_editor(self):
        builder = (ASSETS / "Editor/ResortWorldBuilder.cs").read_text()
        self.assertIn('ImportReportPath = "build/QA/Copacabana_Unity_Import.json"', builder)
        self.assertIn("realUnityEditorExecution = true", builder)
        self.assertIn("File.WriteAllText(reportPath, JsonUtility.ToJson(metrics, true))", builder)
        self.assertIn("extent.size.z < 1200f", builder)
        self.assertIn("extent.size.y > 300f", builder)
        self.assertNotIn("new Vector3(2000f, 90f, 1000f)", builder)

    def test_windows_artifact_must_be_complete_and_portable(self):
        flow = (ROOT / ".github/workflows/r1-unity-cloud.yml").read_text()
        for must in ("ResortSimulator.exe", "ResortSimulator_Data",
                     "UnityPlayer.dll", "SHA256SUMS.txt",
                     "upload-artifact@v4"):
            self.assertIn(must, flow)
        self.assertIn('if [ -n "${UNITY_EMAIL}" ] && [ -n "${UNITY_PASSWORD}" ]', flow)
        self.assertIn("VALIDATED_WINDOWS_OUTPUT:", flow)
        self.assertIn("runtime smoke on Windows is still pending", flow)

    def test_unity_metadata_and_license_gate(self):
        manifest = json.loads((ROOT / "UnityProject/Packages/manifest.json").read_text())
        self.assertIn("com.unity.render-pipelines.universal", manifest["dependencies"])
        ci = (ROOT / ".github/workflows/r1-unity-cloud.yml").read_text()
        self.assertIn("NOT_BUILT: LICENSE_MISSING", ci)
        self.assertIn("game-ci/unity-builder@v4", ci)
        self.assertIn("StandaloneWindows64", ci)


if __name__ == "__main__":
    unittest.main()
