"""Validation of genuine Blender-generated R2 facades (not Unity QA)."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / "ArtSource/Previews/Resort_R2_Fachadas_Premium_Blender_QA.png"
REPORT = ROOT / "ArtSource/Previews/Resort_R2_Fachadas_Premium_QA.json"
FOLDER = ROOT / "UnityProject/Assets/Architecture/R2_Prototypes"
EXPECTED = (
    "R2_ArtDeco_Orla",
    "R2_Residencial_Varandas",
    "R2_Hotel_Contemporaneo",
)


class R2FacadeQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_three_distinct_original_facades_present(self):
        self.assertEqual(set(self.data["modules"]), set(EXPECTED))
        self.assertEqual(self.data["status"], "PASS")
        self.assertEqual(self.data["scope"], "BLENDER_R2_PROTOTYPE_NOT_UNITY")
        for name in EXPECTED:
            mesh = self.data["modules"][name]
            self.assertGreaterEqual(mesh["objects"], 18, name)
            self.assertGreater(mesh["faces"], 120, name)
            self.assertGreaterEqual(len(mesh["materials"]), 4, name)
        # Distinct architectural languages, not a copy with three names.
        material_sets = {tuple(sorted(self.data["modules"][x]["materials"])) for x in EXPECTED}
        self.assertEqual(len(material_sets), len(EXPECTED))

    def test_fbx_binary_fingerprint_and_sha256(self):
        for name in EXPECTED:
            path = FOLDER / f"{name}.fbx"
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 12000, name)
            with path.open("rb") as f:
                self.assertEqual(f.read(18), b"Kaydara FBX Binary", name)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, self.data["modules"][name]["sha256"])

    def test_preview_is_real_non_uniform_blender_render(self):
        self.assertTrue(PREVIEW.is_file())
        self.assertEqual(hashlib.sha256(PREVIEW.read_bytes()).hexdigest(), self.data["preview_sha256"])
        self.assertIn("Blender Cycles CPU", self.data["render_engine"])
        with Image.open(PREVIEW) as im:
            self.assertEqual(im.size, (1280, 720))
            small = im.convert("RGB").resize((160, 90))
            colors = small.getcolors(maxcolors=160 * 90)
            self.assertGreater(len(colors or []), 180)
            self.assertGreater(max(ImageStat.Stat(small).stddev), 18)

    def test_no_original_copacabana_geography_modified(self):
        self.assertTrue((ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").is_file())
        self.assertTrue((ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").is_file())
        # R2 is only a set of reusable facades. No invented streets added.
        self.assertFalse((FOLDER / "Copacabana_Rebuilt.fbx").exists())


if __name__ == "__main__":
    unittest.main()
