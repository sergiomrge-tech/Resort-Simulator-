import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / ".agents" / "skills"
REQUIRED = {
    "geo-copacabana-fiel", "blender-sem-pc", "unity-github-sem-pc",
    "predios-premium-pbr", "orla-resort-vertical-slice",
    "otimizar-cidade-unity", "catalogar-assets-licenca", "qa-capturas-sem-fraude"
}


class SkillsContractTest(unittest.TestCase):
    def test_all_skills_exist_and_have_frontmatter(self):
        found = {p.parent.name for p in DIRECTORY.glob("*/SKILL.md")}
        self.assertEqual(found, REQUIRED)
        for path in DIRECTORY.glob("*/SKILL.md"):
            content = path.read_text(encoding="utf8")
            self.assertTrue(content.startswith("---\n"), path)
            self.assertRegex(content, r"(?m)^name: [a-z0-9-]+$")
            self.assertRegex(content, r"(?m)^description: .{15,}$")
            self.assertIn("## Critério de saída", content, path)
            self.assertIn("## Referências", content, path)

    def test_all_catalog_refs_are_real(self):
        index = (ROOT / "docs/SKILLS_DE_PRODUCAO.md").read_text(encoding="utf8")
        for item in REQUIRED:
            self.assertIn(f".agents/skills/{item}/SKILL.md", index)
        self.assertTrue((ROOT / "docs/assets/REGISTRO_ASSETS.csv").exists())
        self.assertTrue((ROOT / "AGENTS.md").exists())

    def test_original_assets_exist_and_do_not_depend_on_pc(self):
        self.assertGreater((ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").stat().st_size, 2_000_000)
        self.assertGreater((ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").stat().st_size, 400_000)

    def test_provenance_licenses_are_not_faked(self):
        csv = (ROOT / "docs/assets/REGISTRO_ASSETS.csv").read_text(encoding="utf8")
        self.assertIn("ODbL 1.0", csv)
        self.assertIn("nao_validado_unity", csv)


if __name__ == "__main__":
    unittest.main()
