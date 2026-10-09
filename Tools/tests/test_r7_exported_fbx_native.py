"""Independent real Blender FBX re-import gate for R7 Copacabana architecture.
Not a Unity compile, screenshot or artistic acceptance.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools/Blender"))
from r7_contract import semantic_part, SUFFIX, verify_planar_quad_retriangulation
FBX = ROOT / "UnityProject/Assets/Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx"
REPORT = ROOT / "ArtSource/Previews/R7_FBX_UV_NATIVE_QA.json"
ORIG_BLEND = ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
ORIG_FBX = ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
EXPECTED_BLEND = "2384c677bbb2ef8ef6275cb567ec52e69ff4b9e55d204d76eb0b10dfde2e4ac4"
EXPECTED_FBX = "2546ad26546713d40008c395a1a0d00eb2a3f90c1681f0bbbe3ad2c5410d9339"
OBJECT_NAME = re.compile(
    r"^R7B_(?P<way>\d+(?:_part\d+)?)__(?P<style>cop_[a-z0-9_]+)__(?P<semantic>wall|stone|trim|glass|metal|wood|roof|plants|shadow)(?:\.\d+)?$"
)
SEMANTICS = {"wall", "stone", "trim", "glass", "metal", "wood", "roof", "plants", "shadow"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert FBX.is_file() and FBX.stat().st_size > 500000, "Integrated R7 FBX missing"
    assert sha(ORIG_BLEND) == EXPECTED_BLEND, "Original Blender GIS changed"
    assert sha(ORIG_FBX) == EXPECTED_FBX, "Original city FBX changed"
    gallery=json.loads((ROOT/"UnityProject/Assets/Architecture/R7_Pilot50/Procedural/R7_GALLERY_GENERATION_REPORT.json").read_text(encoding="utf-8"))
    expected={r["building_id"][4:].replace("#part","_part"):r for r in gallery["meshes"]}
    assert len(expected)==50 and gallery["count"]==50
    # Independently obtain the original GIS matrix and exact road triangles.
    bpy.ops.wm.open_mainfile(filepath=str(ORIG_BLEND))
    original=next(o for o in bpy.context.scene.objects if o.type=="MESH" and len(o.data.polygons)==26764)
    frame=original.matrix_world.copy()
    roads=[]
    for poly in original.data.polygons:
        if original.data.materials[poly.material_index].name.split(".")[0]=="Road":
            roads.append(sorted(tuple(original.matrix_world@original.data.vertices[i].co) for i in poly.vertices))
    assert len(roads)==3731
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX))
    heroes = [obj for obj in bpy.context.scene.objects
              if obj.type == "MESH" and obj.name.startswith("R7B_")]
    assert len(heroes)==sum(r["mesh_object_count"] for r in expected.values()), "R7 mesh count differs from gallery"
    assert Counter(SUFFIX.sub("",o.name) for o in heroes)==Counter(n for r in expected.values() for n in r["object_names"]), "Lost/duplicate FBX object IDs"
    bases=[o for o in bpy.context.scene.objects if o.type=="MESH" and not o.name.startswith("R7B_")]
    assert len(bases)==1, "Missing/duplicated GIS base"
    base=bases[0]
    assert base.data.uv_layers.active is not None, "GIS base lacks UV0"
    # FBX import can add <3mm numeric roundoff, and Blender 4.5 may reverse
    # the diagonal of coplanar road quads. Both effects are accepted ONLY when
    # the same original road vertices, boundary edges, area and material survive.
    # This does NOT accept moved streets, altered footprints or unknown triangles.
    original_vertices=sorted({point for road in roads for point in road})
    point_index=KDTree(len(original_vertices))
    for idx,position in enumerate(original_vertices):
        point_index.insert(Vector(position),idx)
    point_index.balance()
    before=Counter(("Road",tuple(tri)) for tri in roads)
    after=Counter()
    matched_vertices=set()
    matched_faces=0
    for poly in base.data.polygons:
        if "Roads" not in base.data.materials[poly.material_index].name:
            continue
        assert len(poly.vertices)==3, "Road face topology changed"
        matched_faces+=1
        mapped=[]
        for vertex_index in poly.vertices:
            position=base.matrix_world@base.data.vertices[vertex_index].co
            nearest,source_index,error=point_index.find(position)
            assert source_index is not None and error<.003, (
                "Road vertex shifted more than 3mm in FBX roundtrip")
            matched_vertices.add(source_index)
            mapped.append(original_vertices[source_index])
        assert len(set(mapped))==3, "Road triangle collapsed during FBX roundtrip"
        after[("Road",tuple(sorted(mapped)))]+=1
    assert matched_faces==3731, "Original road triangle count changed"
    assert len(matched_vertices)==len(original_vertices), (
        "One or more original road vertices vanished from FBX")
    road_quad_flips=verify_planar_quad_retriangulation(before,after)
    print("R7_NATIVE_FBX_ROAD_FRAME_PARITY", {
        "original_faces":len(roads),
        "reimported_faces":matched_faces,
        "original_vertices":len(original_vertices),
        "matched_vertices":len(matched_vertices),
        "certified_planar_road_quad_flips":road_quad_flips,
    },flush=True)
    ids, styles, parts = set(), set(), Counter()
    vertices = triangles = uvloops = 0
    bad = []
    for obj in heroes:
        match = OBJECT_NAME.fullmatch(obj.name)
        if match is None:
            bad.append(f"FBX renderer name truncated/invalid: {obj.name}")
            continue
        part = match.group("semantic")
        mats = [m for m in obj.data.materials if m is not None]
        if not mats:
            bad.append(f"No material: {obj.name}")
            continue
        for mat in mats:
            material_part = semantic_part(mat.name)
            if material_part not in SEMANTICS or material_part != part:
                bad.append(f"Wrong material category: {obj.name} => {mat.name}")
        mesh = obj.data
        record=expected[match.group("way")]
        assert record["style_id"]==match.group("style"), "OSM style assignment changed"
        if part=="wall":
            ring=record["source_ring_local_xy_m"]
            inverse=frame.inverted()
            local=[inverse@(obj.matrix_world@v.co) for v in mesh.vertices]
            assert abs(min(p.z for p in local))<.005
            assert abs(max(p.z for p in local)-record["height_visual_m"])<.005
            def segment_distance(p,a,b):
                dx,dy=b[0]-a[0],b[1]-a[1]
                t=max(0,min(1,((p.x-a[0])*dx+(p.y-a[1])*dy)/(dx*dx+dy*dy)))
                return math.hypot(p.x-a[0]-t*dx,p.y-a[1]-t*dy)
            assert all(min(segment_distance(p,a,b) for a,b in zip(ring,ring[1:]))<.005 for p in local), "OSM perimeter/frame shifted"
        uv = mesh.uv_layers.active
        if uv is None or len(uv.data) != len(mesh.loops) or len(uv.data) == 0:
            bad.append(f"Missing UV0: {obj.name}")
            continue
        coords = [loop.uv for loop in uv.data]
        if (not all(math.isfinite(float(c)) for item in coords for c in item)
                or max(float(a[0]) for a in coords) - min(float(a[0]) for a in coords) < 0.001
                or max(float(a[1]) for a in coords) - min(float(a[1]) for a in coords) < 0.001):
            bad.append(f"UV0 non-finite or collapsed: {obj.name}")
        # Per-edge texel scale catches diagonal dominant-axis compression.
        for poly in mesh.polygons:
            loops=list(poly.loop_indices)
            for a,b in zip(loops,loops[1:]+loops[:1]):
                metres=(mesh.vertices[mesh.loops[a].vertex_index].co-mesh.vertices[mesh.loops[b].vertex_index].co).length
                uvmetres=(uv.data[a].uv-uv.data[b].uv).length*2
                assert abs(metres-uvmetres)<max(.002,metres*.001), "UV metric scale lost: "+obj.name
        ids.add(match.group("way"))
        styles.add(match.group("style"))
        parts[part] += 1
        vertices += len(mesh.vertices)
        triangles += sum(max(0, len(p.vertices) - 2) for p in mesh.polygons)
        uvloops += len(uv.data)
    assert not bad, "R7_FBXREREAD_FAILED: " + "; ".join(bad[:16])
    assert len(ids) == 50, f"Expected 50 unique OSM buildings, got {len(ids)}"
    assert len(styles) == 50, f"Expected 50 unique architectural styles, got {len(styles)}"
    assert set(parts)==SEMANTICS, "One of the nine pilot material categories was lost"
    report = {
        "status": "R7_NATIVE_BLENDER_FBX_REIMPORT_UV0_AND_SEMANTIC_PASS",
        "tool": "bpy.ops.import_scene.fbx",
        "derived_fbx": str(FBX.relative_to(ROOT)),
        "derived_fbx_sha256": sha(FBX),
        "original_blender_sha256": sha(ORIG_BLEND),
        "original_fbx_sha256": sha(ORIG_FBX),
        "road_quad_flips":road_quad_flips,
        "distinct_osm_ways": len(ids),
        "distinct_styles": len(styles),
        "mesh_objects": len(heroes),
        "vertices": vertices,
        "triangles": triangles,
        "uv0_loops": uvloops,
        "semantic_parts": dict(sorted(parts.items())),
        "original_road_triangles_after_roundtrip": len(roads),
        "osm_wall_perimeters_and_heights_verified": True,
        "blender_version": bpy.app.version_string,
        "limitations": "Real exported FBX re-imported in Blender, not a Unity URP, scene framing or FPS check. Art still pending human approval."
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("R7_BLENDER_FBX_UV0_SEMANTIC_PASS", json.dumps({
        "ways": len(ids), "meshes": len(heroes), "uv0_loops": uvloops,
        "categories": len(parts)
    }), flush=True)


if __name__ == "__main__":
    main()
