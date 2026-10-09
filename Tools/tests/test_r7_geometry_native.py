"""Fast native bpy smoke BEFORE generating 50 models. No render or art approval."""
import importlib.util
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("generator",ROOT/"Tools/Blender/generate_r7_buildings.py")
G=importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
from r7_contract import OBJECT_NAME, semantic_part, triangle_points


def tree(spec):
    return BVHTree.FromPolygons(spec["v"],spec["f"],all_triangles=False)


def main():
    G.reset()
    for handedness in (-1,1):
        geo=G.Geometry()
        geo.box("wall",(0,0,0),(1,0),(0,handedness),2,2,2)
        for face in geo.data["wall"]["f"]:
            points=[Vector(geo.data["wall"]["v"][i]) for i in face]
            normal=(points[1]-points[0]).cross(points[2]-points[0]).normalized()
            center=sum(points,Vector())/len(points)
            assert normal.dot(center)>0, "BOX_NORMAL_INWARD"
    # Exercise actual Blender tessellation return values, not version comments.
    verts=[Vector((0,0,3)),Vector((2,0,3)),Vector((1,1,3))]
    assert len(triangle_points(G.tessellate_polygon([verts])[0],verts))==3
    source=json.loads(G.ASSIGNMENTS.read_text(encoding="utf-8"))
    catalog={s["id"]:s for s in json.loads(G.CATALOG.read_text(encoding="utf-8"))["styles"]}
    chosen=G.choose_buildings(source,"gallery",0,50)
    sample=max(chosen,key=lambda r:len(r["style_id"]))
    outputs=[]
    destination=ROOT/"build/R7_NATIVE_SMOKE"
    destination.mkdir(parents=True,exist_ok=True)
    G.OUT=destination
    for reverse in (False,True):
        item=dict(sample)
        if reverse: item["footprint_ring_local_xy_m"]=list(reversed(item["footprint_ring_local_xy_m"]))
        geo,detail=G.building_geometry(item,catalog[item["style_id"]])
        wall=tree(geo.data["wall"])
        # Side-facing panes must have sight lines through wall apertures.
        tested=0
        for face in geo.data["glass"]["f"]:
            points=[Vector(geo.data["glass"]["v"][i]) for i in face]
            normal=(points[1]-points[0]).cross(points[2]-points[0]).normalized()
            if abs(normal.z)>.1: continue
            center=sum(points,Vector())/len(points)
            if wall.ray_cast(center+normal*1.5,-normal,1.499)[0] is None: tested+=1
        assert tested>=detail["windows"], "WINDOW_PANES_OCCLUDED_BY_UNCUT_WALL"
        G.generate_item(item,catalog[item["style_id"]],outputs)
        path=ROOT/outputs[-1]["fbx"]
        # Deliberately retain materials: import creates the suffix regression.
        for obj in list(bpy.context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
        bpy.ops.import_scene.fbx(filepath=str(path))
        imported=[o for o in bpy.context.selected_objects if o.type=="MESH"]
        assert len(imported)==outputs[-1]["mesh_object_count"]
        for obj in imported:
            match=OBJECT_NAME.fullmatch(obj.name)
            assert match, "INDIVIDUAL_FBX_NAME_TRUNCATED: "+obj.name
            assert semantic_part(obj.data.materials[0].name)==match.group("semantic")
            assert obj.data.uv_layers.active is not None
        for obj in list(bpy.context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
    print("R7_NATIVE_SMOKE_PASS",bpy.app.version_string,"winding, openings, tessellation, FBX names/suffixes/UV",flush=True)


if __name__=="__main__": main()
