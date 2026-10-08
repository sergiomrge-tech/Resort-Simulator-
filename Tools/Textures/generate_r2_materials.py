"""Original tileable procedural material maps for R2 architectural facades.

Python3 + numpy + pillow, no downloaded third-party artwork. Real texture PNGs
are reusable in Blender (preview) and Unity URP (once the Editor is validated).
Textures are stylized-realistic prototypes, not photogrammetry.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "UnityProject/Assets/Textures/R2_PBR"
REPORT = ROOT / "ArtSource/Previews/Resort_R2_Texturas_PBR_QA.json"
OUTPUT.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

SIZE = 512
MATERIALS = {
    "R2_Calcario_Areia": ((178, 160, 125), 0.68, 0.035, "stone"),
    "R2_Reboco_Marfim": ((216, 211, 193), 0.79, 0.026, "stucco"),
    "R2_Concreto_Quente": ((179, 172, 154), 0.70, 0.036, "concrete"),
    "R2_Concreto_Cinza_Calma": ((105, 110, 109), 0.73, 0.028, "concrete"),
    "R2_Madeira_Tropical": ((115, 71, 40), 0.53, 0.060, "wood"),
    "R2_Ceramica_Terracota": ((140, 73, 50), 0.55, 0.035, "ceramic"),
}

y, x = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
x /= SIZE
y /= SIZE


def periodic_surface(seed: int, kind: str) -> np.ndarray:
    rng = np.random.default_rng(seed)
    field = np.zeros((SIZE, SIZE), dtype=np.float32)
    scales = ((1, 0.36), (3, 0.24), (8, 0.17), (19, 0.14), (47, 0.09))
    for f, amp in scales:
        for _ in range(4):
            kx = int(rng.integers(1, f + 2))
            ky = int(rng.integers(1, f + 2))
            phase = float(rng.uniform(0, 2 * math.pi))
            field += amp * np.sin(2 * math.pi * (kx * x + ky * y) + phase)
    if kind == "wood":
        for i in range(16):
            phase = float(rng.uniform(0, 2 * math.pi))
            field += 0.13 * np.sin(2 * math.pi * ((i + 8) * x + 0.3 * np.sin(2 * math.pi * y)) + phase)
    elif kind == "stone":
        field += 0.08 * np.sin(2 * math.pi * (11 * x + 7 * y))
    elif kind == "stucco":
        field += 0.05 * np.cos(2 * math.pi * (83 * x - 77 * y))
    field = np.tanh(field)
    return field.astype(np.float32)


def png(path: Path, pixels: np.ndarray, mode: str) -> str:
    Image.fromarray(pixels, mode=mode).save(path, optimize=True)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_meta(asset: Path, normal: bool = False, linear: bool = False) -> None:
    # Stable GUIDs across machines and branch checkouts; Unity may expand
    # importer defaults on first real Editor import without changing GUID.
    rel = asset.relative_to(ROOT).as_posix()
    guid = hashlib.sha256(("resort-r2-assets/" + rel).encode("utf-8")).hexdigest()[:32]
    if asset.is_dir():
        body = (
            "fileFormatVersion: 2\\n"
            f"guid: {guid}\\n"
            "folderAsset: yes\\n"
            "DefaultImporter:\\n  externalObjects: {}\\n"
        )
    else:
        body = (
            "fileFormatVersion: 2\\n"
            f"guid: {guid}\\n"
            "TextureImporter:\\n"
            "  externalObjects: {}\\n"
            f"  textureType: {1 if normal else 0}\\n"
            f"  sRGBTexture: {0 if normal or linear else 1}\\n"
        )
    (asset.parent / (asset.name + ".meta")).write_text(body, encoding="utf-8")


def generate() -> None:
    write_meta(ROOT / "UnityProject/Assets/Textures")
    write_meta(OUTPUT)
    qa = {"status": "PASS", "scope": "PROCEDURAL_ORIGINAL_R2_TEXTURES_NOT_UNITY", "resolution": [SIZE, SIZE], "materials": {}}
    for index, (name, (base, rough, relief, kind)) in enumerate(MATERIALS.items()):
        field = periodic_surface(31001 + index * 97, kind)
        light = field * (17 if kind != "wood" else 27)
        rgb = np.empty((SIZE, SIZE, 3), dtype=np.float32)
        for channel, level in enumerate(base):
            rgb[:, :, channel] = level + light * (1 if channel == 0 else 0.87)
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)

        # Tangent-space normal map: tiled finite differences of the SAME height.
        gx = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) * relief * 12
        gy = (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) * relief * 12
        normal = np.stack((-gx, -gy, np.ones_like(field)), axis=-1)
        normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
        normal_rgb = (np.clip(normal * 0.5 + 0.5, 0, 1) * 255).astype(np.uint8)

        rough_map = np.clip(rough + 0.09 * field, 0.12, 0.95)
        rough_rgb = np.round(rough_map * 255).astype(np.uint8)
        smooth = 1.0 - rough_map
        mask = np.empty((SIZE, SIZE, 4), dtype=np.uint8)
        mask[:, :, 0] = 0   # all six materials are dielectrics
        mask[:, :, 1] = np.uint8(np.clip(238 - 14 * np.abs(field), 0, 255))
        mask[:, :, 2] = 255
        mask[:, :, 3] = np.round(smooth * 255).astype(np.uint8)

        files = {
            "Albedo": (rgb, "RGB"),
            "Normal": (normal_rgb, "RGB"),
            "Roughness": (rough_rgb, "L"),
            "Mask": (mask, "RGBA")
        }
        record = {"base_color_rgb": list(base), "roughness": rough, "maps": {}}
        for suffix, (pixels, mode) in files.items():
            path = OUTPUT / (name + "_" + suffix + ".png")
            sha = png(path, pixels, mode)
            write_meta(path, normal=suffix == "Normal", linear=suffix in ("Normal", "Mask", "Roughness"))
            record["maps"][suffix] = {"file": str(path.relative_to(ROOT)), "sha256": sha, "bytes": path.stat().st_size}

        # Check edges correspond under periodic sampling. They need not be identical
        # pixels, but seams must be smooth versus internal gradients.
        edge_error = np.abs(field[:, 0] - field[:, -1]).mean()
        internal_error = np.abs(field[:, 1:] - field[:, :-1]).mean()
        if not np.isfinite(edge_error) or edge_error > internal_error * 3 + 0.01:
            raise RuntimeError(f"Non-tileable procedural map: {name}")
        record["edge_error"] = round(float(edge_error), 6)
        qa["materials"][name] = record
    REPORT.write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("R2 PROCEDURAL MATERIALS GENERATED:", len(qa["materials"]), "materials; 24 PNG maps")


if __name__ == "__main__":
    generate()
