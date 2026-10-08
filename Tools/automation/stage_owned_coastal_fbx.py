"""Stage eight verified *original* coastal FBX files inside UnityProject/Assets.

Strict copy from the archived ProjectOwned FBX; stable GUIDs; no downloaded
assets, fake visual approval, fabricated city/OSM positioning, or requirement
for the owner's PC to be running.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ArtSource/LocalProjectOwned/CoastalUrbanKit"
ARCHIVE = ROOT / "ArtSource/LocalProjectOwned/SOURCE_SHA256_MANIFEST.json"
TARGET = ROOT / "UnityProject/Assets/Architecture/OwnedCoastal"
REPORT = ROOT / "docs/arte/R2_OWNED_COASTAL_UNITY_ASSETS.json"
NAMES = (
    "casa_terrea", "sobrado", "loja", "misto",
    "apartamento", "hotel", "townhouse", "residencial_sacadas"
)

def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def file_guid(relative: str) -> str:
    return sha(("resort-coastal-original/" + relative).encode("utf-8"))[:32]


def stable_meta(path: Path, folder: bool) -> None:
    relative = path.relative_to(ROOT).as_posix()
    guid = file_guid(relative)
    text = ("fileFormatVersion: 2\n"
            + "guid: " + guid + "\n"
            + ("folderAsset: yes\nDefaultImporter:\n"
               "  externalObjects: {}\n"
               if folder else
               "ModelImporter:\n"
               "  serializedVersion: 22200\n"
               "  externalObjects: {}\n"))
    meta_path = Path(str(path) + ".meta")
    if meta_path.exists():
        saved = meta_path.read_text(encoding="utf-8")
        if "guid: " + guid not in saved:
            raise RuntimeError("Existing Unity GUID does not match expected stable ID: " + str(meta_path))
    else:
        meta_path.write_text(text, encoding="utf-8")


def main():
    manifest = json.loads(ARCHIVE.read_text(encoding="utf-8-sig"))
    recorded = {x["path"]: x for x in manifest["files"]}
    assert len(NAMES) == 8

    parent = TARGET.parent
    parent.mkdir(parents=True, exist_ok=True)
    TARGET.mkdir(parents=True, exist_ok=True)
    stable_meta(parent, folder=True)
    stable_meta(TARGET, folder=True)

    report = {
        "status": "STAGED_FOR_UNITY_NOT_EDITOR_VALIDATED",
        "source": "ArtSource/LocalProjectOwned/CoastalUrbanKit/",
        "destination": "UnityProject/Assets/Architecture/OwnedCoastal/",
        "source_must_remain_unchanged": True,
        "model_count": len(NAMES),
        "models": {},
        "copyright": "Original Project Resort geometry; see source AUTHOR metadata",
        "limits": "No Unity Editor import, no level placement, no screenshot, no visual approval",
    }

    for name in NAMES:
        src = SOURCE / (name + ".fbx")
        dst = TARGET / (name + ".fbx")
        source_rel = src.relative_to(ROOT).as_posix()
        archived = recorded[source_rel]
        raw = src.read_bytes()
        if not raw.startswith(b"Kaydara FBX Binary"):
            raise RuntimeError("Invalid original FBX header: " + name)
        if len(raw) < 10000:
            raise RuntimeError("Unusually small FBX: " + name)
        if sha(raw) != archived["git_sha256"]:
            raise RuntimeError("Archived FBX source hash mismatch: " + name)
        if dst.exists() and dst.read_bytes() != raw:
            raise RuntimeError("Refusing to overwrite divergent Unity FBX: " + name)
        shutil.copyfile(src, dst)
        stable_meta(dst, folder=False)
        if sha(dst.read_bytes()) != sha(raw):
            raise RuntimeError("Unity staged file differs from ProjectOwned original")
        report["models"][name] = {
            "catalog_id": "coastal_owned_" + name + "_01",
            "original": source_rel,
            "unity_fbx": dst.relative_to(ROOT).as_posix(),
            "bytes": len(raw),
            "sha256": sha(raw),
            "guid": file_guid(dst.relative_to(ROOT).as_posix()),
            "review_status": "PENDING_UNITY_VISUAL_INSPECTION",
        }

    # Prove source geographic files were retained rather than regenerated.
    for path in (
        ROOT / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend",
        ROOT / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx",
    ):
        if not path.is_file():
            raise RuntimeError("Real Copacabana source missing: " + str(path))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print("ORIGINAL_COASTAL_FBX_STAGED_FOR_UNITY", len(report["models"]))


if __name__ == "__main__":
    main()
