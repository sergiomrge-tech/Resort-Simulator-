"""Independent QA for eight exact ProjectOwned FBX copies staged for Unity."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ROOT_DATA=ROOT/"ArtSource/LocalProjectOwned/CoastalUrbanKit"
DST=ROOT/"UnityProject/Assets/Architecture/OwnedCoastal"
REPORT=ROOT/"docs/arte/R2_OWNED_COASTAL_UNITY_ASSETS.json"


class CoastalFBXStagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(REPORT.read_text(encoding="utf-8"))

    def test_eight_distinct_original_source_files_copied_bitwise(self):
        self.assertEqual(self.data["status"], "STAGED_FOR_UNITY_NOT_EDITOR_VALIDATED")
        self.assertEqual(self.data["model_count"],8)
        self.assertEqual(set(self.data["models"]),{
            "casa_terrea","sobrado","loja","misto",
            "apartamento","hotel","townhouse","residencial_sacadas"
        })
        for name,v in self.data["models"].items():
            src=ROOT/v["original"]
            dst=ROOT/v["unity_fbx"]
            self.assertTrue(src.is_file() and dst.is_file())
            self.assertEqual(src.read_bytes(),dst.read_bytes(),name)
            self.assertEqual(src.stat().st_size,v["bytes"])
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),v["sha256"])
            self.assertTrue(src.read_bytes().startswith(b"Kaydara FBX Binary"))

    def test_unique_guids_and_no_conflicting_metadata(self):
        items=self.data["models"]
        guids=[]
        for name,v in items.items():
            meta=(DST / (name+".fbx.meta")).read_text(encoding="utf-8")
            match=re.search(r"guid: ([a-f0-9]{32})",meta)
            self.assertIsNotNone(match)
            self.assertEqual(match.group(1),v["guid"])
            guids.append(match.group(1))
            self.assertIn("ModelImporter:",meta)
        self.assertEqual(len(set(guids)),8)
        for folder in (DST, DST.parent):
            self.assertTrue(Path(str(folder)+".meta").exists())

    def test_no_false_claims_and_still_original_geography(self):
        self.assertIn("No Unity Editor import",self.data["limits"])
        self.assertEqual({x["review_status"] for x in self.data["models"].values()},
                         {"PENDING_UNITY_VISUAL_INSPECTION"})
        self.assertTrue((ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").exists())
        self.assertTrue((ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").exists())


if __name__=="__main__":
    unittest.main()
