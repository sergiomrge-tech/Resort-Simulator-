"""R6 source/data contract checks. Not a native Unity compilation or render test."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "UnityProject/Assets/Editor/ResortR6FacadeFinish.cs"
R5 = ROOT / "UnityProject/Assets/Architecture/R5_Pilot50/R5_BLENDER_SCENE_QA.json"
GALLERY = ROOT / "UnityProject/Assets/Architecture/R4_Procedural/R4_GALLERY_GENERATION_REPORT.json"
ORIGINAL_BLEND = ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
ORIGINAL_FBX = ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"


class R6FacadeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = SCRIPT.read_text(encoding="utf-8")
        cls.gallery = json.loads(GALLERY.read_text(encoding="utf-8"))
        cls.r5 = json.loads(R5.read_text(encoding="utf-8"))

    def test_r5_upstream_fifty_models_have_fifty_styles_ten_families(self):
        gallery = self.gallery["meshes"]
        replaced = self.r5["models"]
        self.assertEqual(len(gallery), 50)
        self.assertEqual(len(replaced), 50)
        self.assertEqual(len({x["building_id"] for x in gallery}), 50)
        self.assertEqual(len({x["style_id"] for x in gallery}), 50)
        self.assertEqual(len({x["family"] for x in gallery}), 10)
        self.assertEqual(
            {(x["building_id"], x["style_id"]) for x in gallery},
            {(x["building_id"], x["style_id"]) for x in replaced})
        self.assertTrue(ORIGINAL_BLEND.is_file() and ORIGINAL_FBX.is_file())

    def test_material_style_parser_matches_upstream_identifiers(self):
        pattern = re.compile(r"^cop_(?P<family>[a-z0-9_]+)_(?P<variant>0[1-5])$")
        for mesh in self.gallery["meshes"]:
            m = pattern.fullmatch(mesh["style_id"])
            self.assertIsNotNone(m, mesh["style_id"])
            self.assertEqual(m.group("family"), mesh["family"])
        self.assertIn('R5_REPLACED_way_', self.code)
        self.assertIn('BuildingPattern.Match(renderer.gameObject.name)', self.code)
        self.assertIn('MaterialPartPattern.Match(building.Groups["mesh"].Value)', self.code)

    def test_pbr_semantics_and_actual_tileable_maps_are_implemented(self):
        for category in ("wall", "stone", "trim", "glass", "metal",
                         "wood", "roof", "plants", "shadow"):
            self.assertIn(category, self.code)
        for value in ("Universal Render Pipeline/Lit", '"_BaseColor"',
                      '"_BaseMap"', '"_BumpMap"', '"_Metallic"',
                      '"_Smoothness"', '"_BumpScale"', '"_NORMALMAP"',
                      "TextureWrapMode.Repeat", "TextureImporterType.NormalMap",
                      "importer.mipmapEnabled = true", "mat.enableInstancing = true",
                      "ImportedTextures.Contains(path)", "Texture2D(Size, Size",
                      "WriteIfDifferent(absolutePath, tex.EncodeToPNG())"):
            self.assertIn(value, self.code)
        self.assertIn("Require(textures.Count == 40", self.code)
        self.assertIn("Require(ids.Count == 50", self.code)
        self.assertIn("Require(styles.Count == 50", self.code)

    def test_sources_and_existing_scenes_are_never_saved_in_place(self):
        self.assertIn("EditorSceneManager.OpenScene(SourceScene", self.code)
        self.assertIn("EditorSceneManager.SaveScene(scene, OutputScene, true)", self.code)
        self.assertNotIn("SaveScene(scene, SourceScene", self.code)
        self.assertNotIn("BuildPipeline.BuildPlayer(", self.code)
        self.assertIn('blendBefore == Sha256(sourceBlend) && fbxBefore == Sha256(sourceFbx)', self.code)
        self.assertIn('VISUAL_QA_PENDING', self.code)
        self.assertNotIn("visual_approval = true", self.code)
        self.assertTrue(Path(str(SCRIPT) + ".meta").is_file())

    def test_r6_does_not_erase_unreplaced_city_mass(self):
        self.assertIn("if (!building.Success) continue;", self.code)
        self.assertIn("Roads and other 1,418 volumes preserved.", self.code)
        self.assertIn("selected_buildings = ids.Count", self.code)
        self.assertIn("distinct_styles = styles.Count", self.code)


if __name__ == "__main__":
    unittest.main()
