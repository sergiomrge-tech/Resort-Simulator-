"""QA real de ida e volta do mapa: Blender original -> FBX -> Blender.

Nao depende do Unity, nao modifica a fonte GIS e nao aprova compilacao Unity.
Executar no Blender: blender -b --factory-startup --python Tools/Blender/validate_copacabana_roundtrip.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
FBX = ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
REPORT = ROOT / "geo/data/report.json"
OUT = ROOT / "ArtSource/Previews/Copacabana_FBX_roundtrip_QA.json"


def geometry_stats(label: str) -> dict:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"{label}: nenhum objeto MESH encontrado")
    low = [math.inf] * 3
    high = [-math.inf] * 3
    vertex_count = 0
    face_count = 0
    materials = set()
    for obj in meshes:
        mesh = obj.data
        vertex_count += len(mesh.vertices)
        face_count += len(mesh.polygons)
        materials.update(slot.material.name for slot in obj.material_slots if slot.material)
        # World-space mesh coordinates, not the object origin or an invented rectangle.
        for vert in mesh.vertices:
            point = obj.matrix_world @ vert.co
            for axis in range(3):
                low[axis] = min(low[axis], point[axis])
                high[axis] = max(high[axis], point[axis])
    if vertex_count < 10000 or face_count < 5000:
        raise RuntimeError(f"{label}: geometria insuficiente ({vertex_count} vertices, {face_count} faces)")
    return {
        "mesh_objects": len(meshes),
        "vertices": vertex_count,
        "faces": face_count,
        "bbox_min_m": [round(v, 4) for v in low],
        "bbox_max_m": [round(v, 4) for v in high],
        "dimensions_m": [round(high[i] - low[i], 4) for i in range(3)],
        "materials": sorted(materials),
    }


def verify_bounds(original: dict, roundtrip: dict) -> None:
    # Tolerancia de 0.5m em coordenadas de um mundo de 2km.
    # O reimport FBX do Blender deve voltar ao mesmo referencial Z-up original.
    for key in ("bbox_min_m", "bbox_max_m", "dimensions_m"):
        for axis, (src, dst) in enumerate(zip(original[key], roundtrip[key])):
            if abs(src - dst) > 0.5:
                raise RuntimeError(
                    f"FBX nao preserva {key}[{axis}] em metros: fonte={src}, retorno={dst}."
                    " Possivel escala, rotacao extra ou perda do georreferenciamento."
                )
    for label, stats in (("original", original), ("fbx", roundtrip)):
        if not (1000 <= stats["dimensions_m"][0] <= 3000):
            raise RuntimeError(f"{label}: extensao X inesperada")
        if not (1000 <= stats["dimensions_m"][1] <= 3000):
            raise RuntimeError(f"{label}: extensao Y inesperada")
        if not (10 <= stats["dimensions_m"][2] <= 300):
            raise RuntimeError(f"{label}: extensao vertical inesperada")
    if roundtrip["faces"] < original["faces"] * 0.8:
        raise RuntimeError("FBX perdeu um numero inaceitavel de faces")


def main() -> None:
    assert SOURCE.is_file() and FBX.is_file() and REPORT.is_file(), "Fontes originais ausentes"
    assert FBX.read_bytes()[:18] == b"Kaydara FBX Binary", "FBX binario invalido"
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    assert data["game_area_m2"] == 2_000_000, "Recorte GIS alterado"
    assert data["real_osm_entities_within_roi"]["building"] == 1468, "Footprints originais alterados"

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    original = geometry_stats("blend original")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX))
    roundtrip = geometry_stats("fbx reimportado")
    verify_bounds(original, roundtrip)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "PASS",
        "scope": "BLENDER_FBX_ROUNDTRIP_ONLY_NOT_UNITY",
        "original_blend": str(SOURCE.relative_to(ROOT)),
        "imported_fbx": str(FBX.relative_to(ROOT)),
        "original": original,
        "roundtrip": roundtrip,
        "copyright": "© OpenStreetMap contributors — ODbL 1.0",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ROUNDTRIP VALIDATED: original BLEND -> FBX -> Blender (NOT UNITY)")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
