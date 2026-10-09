"""R3: original OSM pipeline reconstructed without touching any road."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"ArtSource/Previews/R3_GIS_Mask_Parity_QA.json"

class OriginalOSMParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(REPORT.read_text(encoding="utf-8"))
    def test_all_road_triangles_and_unselected_faces_identical(self):
        x=self.d
        self.assertEqual(x["status"],"ORIGINAL_OSM_PIPELINE_GEOMETRY_PARITY")
        self.assertEqual(x["before_material_faces"],{"Road":3731,"Building":23033})
        self.assertEqual(x["before_material_faces"]["Road"],x["after_material_faces"]["Road"])
        self.assertEqual(x["removed_road_faces"],0)
        self.assertEqual(x["exact_unchanged_faces_including_all_roads"],sum(x["after_material_faces"].values()))
        self.assertGreater(x["removed_original_building_faces"],10)
        self.assertEqual(x["before_material_faces"]["Building"]-x["after_material_faces"]["Building"],
                         x["removed_original_building_faces"])
    def test_two_real_ids_and_original_blender_immutability(self):
        x=self.d
        self.assertEqual(x["masked_ways"],["way/1048277518","way/1048277521"])
        self.assertEqual(hashlib.sha256((ROOT/x["source_osm"]).read_bytes()).hexdigest(),x["source_osm_sha256"])
        self.assertEqual(hashlib.sha256((ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend").read_bytes()).hexdigest(),x["source_blend_sha256"])
        self.assertEqual(hashlib.sha256((ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx").read_bytes()).hexdigest(),x["source_fbx_sha256"])
        self.assertIn("not yet byte-parity",x["limits"])

if __name__=="__main__":
    unittest.main()
