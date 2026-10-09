"""Executable regressions without Blender; these do not certify native output."""
import ast
import importlib.util
import json
import math
import random
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


C = module("Tools/Blender/r7_contract.py", "r7_contract")
P = module("Tools/geo/r7_expansion_plan.py", "r7_expansion_plan")


class ArithmeticVector(tuple):
    """Only vector arithmetic for facade unit tests; never a Blender emulator."""
    def __new__(cls, values): return super().__new__(cls, values)
    def __add__(self, other): return ArithmeticVector(a+b for a,b in zip(self,other))
    def __mul__(self, value): return ArithmeticVector(a*value for a in self)
    def __truediv__(self, value): return self*(1/value)
    x=property(lambda self:self[0])
    y=property(lambda self:self[1])


def generator_math():
    tree=ast.parse((ROOT/"Tools/Blender/generate_r7_buildings.py").read_text(encoding="utf-8"))
    names={"Geometry","ring_stats","clamp","choose_buildings","building_geometry"}
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
    # Test the actual wall/window/balcony construction loop; roof tessellation
    # and bpy emission are reserved for the native tests, with no fake output.
    facade=next(n for n in nodes if n.name=="building_geometry")
    cutoff=next(i for i,n in enumerate(facade.body) if isinstance(n,ast.Assign) and
                any(isinstance(t,ast.Name) and t.id=="roof_vertices" for t in n.targets))
    facade.body=facade.body[:cutoff]+[ast.Return(value=ast.Name(id="G",ctx=ast.Load()))]
    namespace={"Vector":ArithmeticVector,"math":math,"random":random,"json":json,
               "MATERIAL_KEYS":C.SEMANTICS,"wall_rectangles":C.wall_rectangles,
               "CATALOG":ROOT/"ArtSource/ProceduralBuildings/Resort50Styles.json","HELD_BACK":P.HELD_BACK}
    code=ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[]))
    exec(compile(code,"actual_generator_facade_math","exec"),namespace)
    return namespace


class ContractTests(unittest.TestCase):
    def test_actual_box_normals_are_outward_for_both_handed_frames(self):
        namespace=generator_math()
        for handedness in (-1,1):
            geo=namespace["Geometry"]()
            geo.box("wall",(0,0,0),(1,0),(0,handedness),2,2,2)
            for face in geo.data["wall"]["f"]:
                pts=[geo.data["wall"]["v"][i] for i in face]
                a=[pts[1][i]-pts[0][i] for i in range(3)]
                b=[pts[2][i]-pts[0][i] for i in range(3)]
                n=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
                center=[sum(p[i] for p in pts)/len(pts) for i in range(3)]
                self.assertGreater(sum(x*y for x,y in zip(n,center)),0)

    def test_all_50_actual_facade_loops_accept_both_osm_windings(self):
        namespace=generator_math()
        data=json.loads((ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json").read_text(encoding="utf-8"))
        styles={s["id"]:s for s in json.loads(namespace["CATALOG"].read_text(encoding="utf-8"))["styles"]}
        for row in namespace["choose_buildings"](data,"gallery",0,50):
            for reverse in (False,True):
                item=dict(row)
                if reverse: item["footprint_ring_local_xy_m"]=list(reversed(row["footprint_ring_local_xy_m"]))
                with self.subTest(way=item["building_id"],reverse=reverse):
                    geo=namespace["building_geometry"](item,styles[item["style_id"]])
                    self.assertGreater(geo.windows,3)
                    self.assertTrue(geo.data["wall"]["f"])
                    self.assertTrue(geo.data["glass"]["f"])

    def test_duplicate_material_suffixes(self):
        for key in C.SEMANTICS:
            for suffix in ("", ".001", ".052", ".001.002"):
                self.assertEqual(C.semantic_part("R7_hotel_contempora_05_"+key+suffix), key)
        for invalid in ("Standard", "wall", "R7_glass_bad", "R7_wall.abc"):
            with self.assertRaises(ValueError): C.semantic_part(invalid)

    def test_short_ids_for_every_frozen_building_and_category(self):
        data = json.loads((ROOT / "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json").read_text(encoding="utf-8"))
        for row in data["buildings"]:
            for part in C.SEMANTICS:
                name = C.object_id(row["building_id"], row["style_id"], part)
                self.assertLessEqual(len(name), 63)
                self.assertEqual(C.OBJECT_NAME.fullmatch(name).group("semantic"), part)

    def test_reject_invalid_semantic_or_fake_way(self):
        for way,style,part in (("way/1__style_2", "cop_hotel_classico_01", "wall"),
                               ("way/1", "cop_hotel_classico_01", "generic")):
            with self.assertRaises(ValueError): C.object_id(way, style, part)

    def test_tessellation_handles_vectors_and_indices(self):
        verts = [(0,0,3), (2,0,3), (1,1,3)]
        self.assertEqual(C.triangle_points((0,1,2), verts), verts)
        self.assertEqual(C.triangle_points(tuple(verts), verts), verts)

    def test_rotated_uvs_have_same_metric_scale(self):
        for degrees in (0, 17, 46, 90, 135, 223):
            angle = math.radians(degrees)
            normal = (math.cos(angle), math.sin(angle), 0)
            tangent = (-normal[1], normal[0], 0)
            a = C.metric_uv((0,0,0), normal)
            b = C.metric_uv(tuple(2*x for x in tangent), normal)
            c = C.metric_uv((0,0,2), normal)
            self.assertAlmostEqual(math.dist(a,b), 1)
            self.assertAlmostEqual(math.dist(a,c), 1)

    def test_sloped_uvs_preserve_in_plane_length(self):
        normal = (0, .6, .8)
        self.assertAlmostEqual(math.dist(C.metric_uv((0,0,0),normal),
                                        C.metric_uv((0,-1.6,1.2),normal)), 1)

    def test_wall_holes_are_open_and_area_is_conserved(self):
        holes = [(1,3,1,3), (4,6,0,2), (1,3,4,5)]
        rects = list(C.wall_rectangles(7,6,holes))
        self.assertAlmostEqual(sum((b-a)*(d-c) for a,b,c,d in rects), 42-4-4-2)
        for a,b,c,d in rects:
            for x0,x1,z0,z1 in holes:
                self.assertFalse(min(b,x1)>max(a,x0) and min(d,z1)>max(c,z0))

    def test_wall_rejects_overlap_and_out_of_bounds(self):
        for holes in ([(-1,2,1,3)], [(1,2,1,7)], [(1,3,1,3),(2,4,2,4)]):
            with self.assertRaises(ValueError): list(C.wall_rectangles(7,6,holes))

    def test_gallery_has_real_unique_assignments_without_cloning(self):
        # Execute the actual pure selector from the generator, without importing bpy.
        tree = ast.parse((ROOT / "Tools/Blender/generate_r7_buildings.py").read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="choose_buildings")
        namespace = {"json":json, "CATALOG":ROOT/"ArtSource/ProceduralBuildings/Resort50Styles.json",
                     "HELD_BACK":{"way/1048277518","way/1048277521"}}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_generator_selector", "exec"), namespace)
        data = json.loads((ROOT / "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json").read_text(encoding="utf-8"))
        selected = namespace["choose_buildings"](data,"gallery",0,50)
        self.assertEqual(len(selected),50)
        self.assertEqual(len({r["building_id"] for r in selected}),50)
        self.assertEqual(len({r["style_id"] for r in selected}),50)
        self.assertTrue(all(r in data["buildings"] for r in selected))

    def test_expansion_covers_remaining_once_and_marks_reserved(self):
        source = json.loads((ROOT / "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json").read_text(encoding="utf-8"))
        baseline = json.loads(P.BASELINE_MASK.read_text(encoding="utf-8"))
        pilot = set(baseline["masked_way_ids"])
        rows = P.expansion_rows(source["buildings"], pilot)
        self.assertEqual(len(rows),1418)
        self.assertFalse(pilot & {r["building_id"] for r in rows})
        self.assertEqual(pilot | {r["building_id"] for r in rows}, {r["building_id"] for r in source["buildings"]})
        self.assertTrue(P.HELD_BACK <= {r["building_id"] for r in rows})
        with self.assertRaises(RuntimeError): P.expansion_rows(source["buildings"]+[source["buildings"][0]],pilot)


if __name__ == "__main__": unittest.main()
