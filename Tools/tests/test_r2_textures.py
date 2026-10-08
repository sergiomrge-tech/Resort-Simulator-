"""Real image tests for R2 PBR maps; no fake Unity compilation claims."""
import hashlib
import json
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/"ArtSource/Previews/Resort_R2_Texturas_PBR_QA.json"
EXPECTED={
    "R2_Calcario_Areia", "R2_Reboco_Marfim", "R2_Concreto_Quente",
    "R2_Concreto_Cinza_Calma", "R2_Madeira_Tropical", "R2_Ceramica_Terracota"
}


class R2TextureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads(QA.read_text(encoding="utf-8"))

    def test_all_procedural_materials_have_four_real_maps(self):
        self.assertEqual(set(self.report["materials"]), EXPECTED)
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["scope"], "PROCEDURAL_ORIGINAL_R2_TEXTURES_NOT_UNITY")
        for name, info in self.report["materials"].items():
            self.assertEqual(set(info["maps"]), {"Albedo","Normal","Roughness","Mask"})
            for suffix, details in info["maps"].items():
                path=ROOT/details["file"]
                self.assertTrue(path.is_file(), str(path))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), details["sha256"])
                self.assertGreater(path.stat().st_size, 512)
                with Image.open(path) as image:
                    self.assertEqual(image.size,(512,512))
                    self.assertEqual(image.mode,{"Albedo":"RGB","Normal":"RGB","Roughness":"L","Mask":"RGBA"}[suffix])

    def test_texture_metadata_guids_and_color_spaces(self):
        import re
        guids = set()
        for name, info in self.report["materials"].items():
            for suffix, details in info["maps"].items():
                meta = Path(str(ROOT / details["file"]) + ".meta")
                self.assertTrue(meta.is_file(), str(meta))
                content = meta.read_text(encoding="utf-8")
                match = re.search(r"guid: ([0-9a-f]{32})", content)
                self.assertIsNotNone(match)
                self.assertNotIn(match.group(1), guids)
                guids.add(match.group(1))
                self.assertIn("TextureImporter:", content)
                self.assertIn(
                    f"sRGBTexture: {1 if suffix == 'Albedo' else 0}",
                    content)
                self.assertIn(
                    f"textureType: {1 if suffix == 'Normal' else 0}",
                    content)
        self.assertTrue((ROOT / "UnityProject/Assets/Textures.meta").is_file())
        self.assertTrue((ROOT / "UnityProject/Assets/Textures/R2_PBR.meta").is_file())

    def test_albedo_variance_and_tangent_space_normal(self):
        for name, info in self.report["materials"].items():
            with Image.open(ROOT/info["maps"]["Albedo"]["file"]) as im:
                a=np.array(im)
                self.assertGreater(a.std(), 4.0, name)
            with Image.open(ROOT/info["maps"]["Normal"]["file"]) as im:
                n=np.asarray(im,dtype=float)
                self.assertGreater(n[:,:,2].mean(), 190, name)
                self.assertGreater(n[:,:,0].std()+n[:,:,1].std(), 0.5, name)

    def test_mask_is_smoothness_alpha_and_albedo_opaque(self):
        for name, info in self.report["materials"].items():
            with Image.open(ROOT/info["maps"]["Mask"]["file"]) as im:
                m=np.array(im)
                self.assertEqual(m[:,:,0].max(),0, name)
                self.assertGreater(m[:,:,3].std(), 0.5, name)

    def test_preserves_existing_geographic_source(self):
        self.assertTrue((ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").exists())
        self.assertTrue((ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").exists())


if __name__=="__main__":
    unittest.main()
