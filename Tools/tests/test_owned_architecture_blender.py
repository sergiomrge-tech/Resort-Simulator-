"""Only assert what actual Blender FBX import + render proves, not Unity results."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "ArtSource/Previews/Owned_CoastalUrbanKit_QA.json"
PREVIEW = ROOT / "ArtSource/Previews/Owned_CoastalUrbanKit_Blender_QA.png"
NAMES = {
    "casa_terrea", "sobrado", "loja", "misto",
    "apartamento", "hotel", "townhouse", "residencial_sacadas"
}


class CoastalArchitectureBlenderQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(QA.read_text(encoding="utf-8"))

    def test_eight_project_owned_typologies_with_metric_bounds(self):
        data = self.data
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["scope"], "ORIGINAL_PROJECT_OWNED_FBX_BLENDER_REVIEW_NOT_UNITY")
        self.assertEqual(set(data["models"]), NAMES)
        for name, m in data["models"].items():
            self.assertGreater(m["vertices"], 50, name)
            self.assertGreater(m["polygons"], 20, name)
            self.assertGreater(m["meshes"], 0, name)
            self.assertEqual(len(m["dimensions_from_imported_FBX_m"]), 3)
            self.assertTrue(all(d > 0 for d in m["dimensions_from_imported_FBX_m"]), name)
            self.assertEqual(m["approval"], "CANDIDATE_PENDING_REAL_UNITY_VISUAL_GATE")

    def test_source_fbx_are_immutable_originals(self):
        for name, m in self.data["models"].items():
            path = ROOT / m["source"]
            self.assertEqual(path, ROOT / "ArtSource/LocalProjectOwned/CoastalUrbanKit" / (name + ".fbx"))
            with path.open("rb") as stream:
                self.assertEqual(stream.read(18), b"Kaydara FBX Binary")
            self.assertEqual(path.stat().st_size, m["bytes"], name)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), m["sha256"], name)

    def test_actual_render_is_colorful_and_not_empty(self):
        self.assertTrue(PREVIEW.is_file())
        self.assertEqual(hashlib.sha256(PREVIEW.read_bytes()).hexdigest(), self.data["preview_sha256"])
        with Image.open(PREVIEW) as im:
            self.assertEqual(im.size, (1600, 1000))
            small = im.convert("RGB").resize((200, 125))
            values = ImageStat.Stat(small)
            self.assertGreater(max(values.stddev), 12)
            self.assertGreater(len(small.getcolors(maxcolors=200*125) or []), 100)

    def test_no_fake_unity_approval_and_original_map_remains(self):
        self.assertTrue(self.data["original_map_untouched"])
        self.assertIn("Blender", self.data["studio"])
        self.assertTrue((ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").exists())
        self.assertTrue((ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").exists())


if __name__ == "__main__":
    unittest.main()
