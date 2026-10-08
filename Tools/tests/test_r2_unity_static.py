"""Static Unity wiring checks for R2; not a compilation substitute."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "UnityProject/Assets"
EDITOR = ASSETS / "Editor/ResortFacadePreviewBuilder.cs"
MODELS = ASSETS / "Architecture/R2_Prototypes"
EXPECTED = (
    "R2_ArtDeco_Orla",
    "R2_Residencial_Varandas",
    "R2_Hotel_Contemporaneo",
)


class R2UnitySourceTests(unittest.TestCase):
    def test_all_three_fbx_are_ready_with_persistent_guids(self):
        for name in EXPECTED:
            fbx = MODELS / (name + ".fbx")
            self.assertGreater(fbx.stat().st_size, 12000)
            with fbx.open("rb") as file:
                self.assertEqual(file.read(18), b"Kaydara FBX Binary")
            meta = (MODELS / (name + ".fbx.meta")).read_text()
            self.assertRegex(meta, r"guid: [0-9a-f]{32}")
            self.assertIn("materialImportMode: 1", meta)
        ids = re.findall(r"guid: ([0-9a-f]{32})",
                         "\n".join(p.read_text() for p in ASSETS.rglob("*.meta")))
        self.assertEqual(len(ids), len(set(ids)), "Duplicated GUIDs in Unity metadata")

    def test_visual_preview_has_distinct_models_and_urp(self):
        code = EDITOR.read_text()
        for name in EXPECTED:
            self.assertIn(name, code)
        self.assertIn("ResortRenderingSetup.EnsureConfigured();", code)
        self.assertIn("ModelImporterMaterialImportMode.ImportStandard", code)
        self.assertIn("GetOrCreatePbrMaterial", code)
        self.assertIn('material.SetFloat("_Metallic"', code)
        self.assertIn('material.SetFloat("_Smoothness"', code)
        self.assertIn('material.SetColor("_BaseColor"', code)
        self.assertIn("AssetDatabase.CreateAsset(material, path)", code)
        self.assertIn("EditorSceneManager.SaveScene", code)
        self.assertIn("R2_ARCHITECTURAL_PROTOTYPES_NOT_GIS_PLACEMENTS", code)
        self.assertTrue((EDITOR.parent / (EDITOR.name + ".meta")).is_file())

    def test_does_not_overwrite_original_copacabana_or_r1_scene(self):
        code = EDITOR.read_text()
        self.assertIn('R2_ArchitecturalReview.unity', code)
        self.assertNotIn('Copacabana_Pilot.unity', code)
        self.assertNotIn("Assets/ImportedBlender/Copacabana_Real_Blender.fbx", code)
        self.assertTrue((ASSETS / "ImportedBlender/Copacabana_Real_Blender.fbx").is_file())


if __name__ == "__main__":
    unittest.main()
