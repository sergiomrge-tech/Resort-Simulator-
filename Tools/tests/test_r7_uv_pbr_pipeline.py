import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class R7PipelineSourceTests(unittest.TestCase):
    def test_uv_and_semantic_categories_are_created_before_fbx_export(self):
        source = (ROOT / "Tools/Blender/generate_r7_buildings.py").read_text(encoding="utf-8")
        self.assertIn('mesh.uv_layers.new(name="UVMap")', source)
        self.assertIn("uv.data[li].uv=(co[axes[0]]/2.0,co[axes[1]]/2.0)", source)
        for semantic in ("wall", "stone", "trim", "glass", "metal", "wood", "roof", "plants", "shadow"):
            self.assertRegex(source, rf'"{semantic}":mat\(prefix\+"{semantic}"')
        self.assertIn('obj["r7_semantic_id"]="R7_"+key', source)
        self.assertIn('mesh.materials.append(materials[key])', source)
        self.assertIn("bpy.ops.export_scene.fbx", source)

    def test_r7_paths_are_isolated_and_source_hashes_are_enforced(self):
        source = (ROOT / "Tools/Blender/assemble_r7_city_50.py").read_text(encoding="utf-8")
        self.assertIn("R7_Copacabana_50_Fachadas_Derivado.fbx", source)
        self.assertIn("R7_BLENDER_SCENE_QA.json", source)
        self.assertIn("if sha(ORIGINAL)!=source_hash or sha(ORIGINAL_FBX)!=fbx_hash:", source)
        self.assertIn("road_before!=3731 or road_after!=road_before", source)
        self.assertIn("46 degree GIS rotation", source)
        self.assertIn('ob.name="R7B_"+osm_token', source)
        self.assertIn('len(ob.name)>63', source)
        self.assertNotIn('OUT=ROOT/"UnityProject/Assets/Architecture/R5_Pilot50/', source)

    def test_r7_mask_stays_on_real_osm_and_preserves_roads(self):
        source = (ROOT / "Tools/geo/r7_mask_city_50.py").read_text(encoding="utf-8")
        self.assertIn('"status":"R7_FIFTY_OSM_MASK_ALL_ROAD_GEOMETRY_IDENTICAL"', source)
        self.assertIn('"road_faces_removed":0', source)
        self.assertIn('"identical_unmasked_tris":sum(s_after.values())', source)
        self.assertIn("RESORT_R5_SKIP_OSM_IDS", source)
        report = json.loads((ROOT / "UnityProject/Assets/Architecture/R5_Pilot50/R5_SOURCE_MASK_QA.json").read_text(encoding="utf-8"))
        self.assertEqual(report["masked_way_count"], 50)
        self.assertEqual(report["source_material_faces"]["Road"], 3731)

    def test_unity_gate_requires_urp_uv0_and_slot_semantics_without_fallback(self):
        source = (ROOT / "UnityProject/Assets/Editor/ResortR7FacadeFinish.cs").read_text(encoding="utf-8")
        self.assertIn('"Universal Render Pipeline/Lit"', source)
        self.assertIn("GraphicsSettings.defaultRenderPipeline = qaPipeline", source)
        self.assertIn('QualitySettings.renderPipeline = qaPipeline', source)
        self.assertIn("UniversalRenderPipelineAsset.Create(rendererData)", source)
        self.assertIn("AssetDatabase.CreateAsset(rendererData, rendererPath)", source)
        self.assertNotIn('EditorApplication.ExecuteMenuItem(', source)
        self.assertIn("URP_PIPELINE_ASSET_NOT_FOUND", source)
        self.assertIn("UV0_MISSING", source)
        self.assertIn("MATERIAL_SEMANTIC_ID_MISSING", source)
        self.assertIn("MATERIAL_SEMANTIC_MISMATCH", source)
        self.assertIn("TonemappingMode.ACES", source)
        self.assertIn("postExposure.value = -.25f", source)
        self.assertIn("TonemappingMode", source)
        self.assertIn('tint.a = .58f', source)
        self.assertIn("existing[i] = finish", source)
        self.assertIn(r"R7B_(?<way>[0-9]+(?:_part[0-9]+)?)", source)
        self.assertNotIn('Shader.Find("Standard")', source)
        self.assertNotIn("InferR5Part(renderer); inferredFallbacks++", source)

    def test_deterministic_expansion_is_gated_at_50(self):
        source = (ROOT / "Tools/geo/r7_expansion_plan.py").read_text(encoding="utf-8")
        self.assertIn("len(by_id) != 1468", source)
        self.assertIn("len(pilot) != 50", source)
        self.assertIn("len(rows) != 1418", source)
        self.assertIn("R7_DETERMINISTIC_EXPANSION_PLAN_NOT_MATERIALIZED", source)
        self.assertIn("Do not apply any batch to the full map", source)

    def test_assignment_source_has_1468_unique_osm_ways_and_50_styles(self):
        assignment = json.loads((ROOT / "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json").read_text(encoding="utf-8"))
        ids = [row["building_id"] for row in assignment["buildings"]]
        self.assertEqual(len(ids), 1468)
        self.assertEqual(len(set(ids)), 1468)
        self.assertTrue(all(re.fullmatch(r"way/\d+(?:#part[1-9]\d*)?", value) for value in ids))
        gallery = json.loads((ROOT / "UnityProject/Assets/Architecture/R4_Procedural/R4_GALLERY_GENERATION_REPORT.json").read_text(encoding="utf-8"))
        self.assertEqual(gallery["count"], 50)
        self.assertEqual(len({row["style_id"] for row in gallery["meshes"]}), 50)


if __name__ == "__main__":
    unittest.main()
