"""R5 geographic and native Blender QA: never pass with duplicated OSM buildings."""
import hashlib
import json
import unittest
from pathlib import Path

from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"UnityProject/Assets/Architecture/R5_Pilot50"
MASK=BASE/"R5_SOURCE_MASK_QA.json"
SCENE=BASE/"R5_BLENDER_SCENE_QA.json"
GALLERY=ROOT/"UnityProject/Assets/Architecture/R4_Procedural/R4_GALLERY_GENERATION_REPORT.json"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

class R5RealOSMPlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=json.loads(MASK.read_text(encoding="utf-8"))
        cls.b=json.loads(SCENE.read_text(encoding="utf-8"))
        cls.g=json.loads(GALLERY.read_text(encoding="utf-8"))
    def test_original_roads_and_other_buildings_identical_in_blender(self):
        a,b=self.a,self.b
        self.assertEqual(a["status"],"R5_FIFTY_OSM_MASK_ALL_ROAD_GEOMETRY_IDENTICAL")
        self.assertEqual(b["status"],"R5_50_SOURCE_OSM_BUILDINGS_REPLACED_IN_AUTHENTIC_BLENDER")
        self.assertEqual(a["masked_way_count"],50)
        self.assertEqual(a["source_material_faces"]["Road"],3731)
        self.assertEqual(a["derived_material_faces"]["Road"],3731)
        self.assertEqual(a["road_faces_removed"],0)
        self.assertEqual(b["original_road_faces"],b["retained_road_faces"])
        self.assertEqual(b["retained_road_faces"],3731)
        self.assertEqual(b["original_faces"],26764)
        self.assertEqual(b["old_building_faces_removed"],a["building_faces_removed"])
        self.assertEqual(b["derived_base_city_faces"],a["identical_unmasked_tris"])
        self.assertEqual(b["original_faces"]-b["old_building_faces_removed"],
                         b["derived_base_city_faces"])
        self.assertFalse(b["unmodified_original_source_used_as_output"])
    def test_fifty_unique_authored_models_and_real_centroids(self):
        b=self.b
        self.assertEqual(b["new_architecture_count"],50)
        self.assertEqual(len(b["models"]),50)
        self.assertEqual(len({x["building_id"] for x in b["models"]}),50)
        self.assertEqual(sorted(x["building_id"] for x in b["models"]),
                         self.a["masked_way_ids"])
        source={x["building_id"]:x for x in self.g["meshes"]}
        self.assertGreater(b["new_architecture_mesh_objects"],200)
        self.assertGreater(b["new_architecture_polygons"],500000)
        for x in b["models"]:
            model=source[x["building_id"]]
            self.assertEqual(x["style_id"],model["style_id"])
            self.assertEqual(x["local_centroid_xy_m"],model["local_osm_centroid_xy_m"])
            self.assertEqual(x["model_polygons"],model["polygons_generated"])
            self.assertEqual(x["source_fbx_sha256"],model["fbx_sha256"])
    def test_real_unity_source_file_and_real_blender_scene_export(self):
        b=self.b
        self.assertEqual(sha(ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"),
                         b["original_blend_sha256"])
        self.assertEqual(sha(ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"),
                         b["original_fbx_sha256"])
        self.assertEqual(sha(MASK),b["source_mask_report_sha256"])
        export=ROOT/b["derived_fbx"]
        self.assertTrue(export.is_file())
        self.assertTrue(export.read_bytes().startswith(b"Kaydara FBX Binary"))
        self.assertGreater(export.stat().st_size,500000)
        self.assertEqual(sha(export),b["derived_fbx_sha256"])
        self.assertTrue(Path(str(export)+".meta").is_file())
        self.assertTrue(Path(str(export.parent)+".meta").is_file())
        self.assertIn("NOT final art",b["limits"])
    def test_genuine_blender_preview_and_geographic_rotation(self):
        b=self.b
        self.assertEqual(b["render_engine"],"Blender Cycles CPU")
        self.assertEqual(len(b["source_gis_rotation_matrix_rows"]),4)
        self.assertGreater(abs(b["source_gis_rotation_matrix_rows"][0][1]),.3)
        preview=ROOT/b["preview"]
        self.assertTrue(preview.is_file())
        self.assertEqual(sha(preview),b["preview_sha256"])
        with Image.open(preview) as im:
            self.assertEqual(im.size,(1600,900))
            sample=im.convert("RGB").resize((160,90))
            self.assertGreater(max(ImageStat.Stat(sample).stddev),10)
            self.assertGreater(len(sample.getcolors(maxcolors=14400) or []),110)

if __name__=="__main__":
    unittest.main()
