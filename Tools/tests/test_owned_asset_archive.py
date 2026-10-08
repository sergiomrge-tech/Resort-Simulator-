"""Validate the immutable PC-source archive using only Python stdlib.

This is deliberately independent of the remote desktop, Blender and Unity:
it checks source-archive completeness, file hashes, binary headers, and
original OSM map preservation but never claims gameplay compilation.
"""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ArtSource/LocalProjectOwned"
MANIFEST = SOURCE / "SOURCE_SHA256_MANIFEST.json"


class ProjectOwnedAssetsArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        cls.entries = cls.data["files"]

    def test_manifest_is_complete_and_every_hash_matches(self):
        self.assertEqual(len(self.entries), 38)
        referenced = set()
        for entry in self.entries:
            rel = entry["path"]
            self.assertTrue(rel.startswith("ArtSource/LocalProjectOwned/"))
            self.assertNotIn("..", Path(rel).parts)
            self.assertNotIn(rel, referenced, rel)
            referenced.add(rel)
            actual = ROOT / rel
            self.assertTrue(actual.is_file(), rel)
            self.assertEqual(actual.stat().st_size, entry["bytes"], rel)
            self.assertEqual(hashlib.sha256(actual.read_bytes()).hexdigest(),
                             entry["sha256"], rel)
        available = {p.relative_to(ROOT).as_posix() for p in SOURCE.rglob("*") if p.is_file()}
        self.assertEqual(available - referenced, {
            "ArtSource/LocalProjectOwned/README.md",
            "ArtSource/LocalProjectOwned/SOURCE_SHA256_MANIFEST.json",
        })

    def test_blender_and_fbx_have_real_binary_headers(self):
        types = {".blend": 0, ".fbx": 0, ".png": 0}
        for item in self.entries:
            p = ROOT / item["path"]
            if p.suffix in types:
                types[p.suffix] += 1
                signature = {".blend": b"BLENDER",
                             ".fbx": b"Kaydara FBX Binary",
                             ".png": b"\x89PNG\r\n\x1a\n"}[p.suffix]
                with p.open("rb") as f:
                    self.assertEqual(f.read(len(signature)), signature, str(p))
        self.assertEqual(types, {".blend": 13, ".fbx": 8, ".png": 8})

    def test_author_provenance_and_license_review_not_fake_approval(self):
        kit = (SOURCE / "CoastalUrbanKit/SOURCE.md").read_text(encoding="utf-8")
        kiosk = json.loads((SOURCE / "KioskPremium_20261008/SOURCE.json")
                           .read_text(encoding="utf-8"))
        readme = (SOURCE / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("project-owned geometry", kit)
        self.assertIn("Project-owned original geometry", kiosk["license"])
        self.assertIn("Full visual approval remains pending", readme)
        self.assertIn("no source from proprietary external asset libraries", self.data["scope"].lower())

    def test_original_geographic_map_is_not_replaced(self):
        self.assertTrue((ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").is_file())
        self.assertTrue((ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").is_file())
        self.assertFalse((SOURCE / "Copacabana_Recreated.blend").exists())


if __name__ == "__main__":
    unittest.main()
