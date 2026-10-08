"""Record immutable *Git committed* bytes for authored asset archive.

The importer on Windows preserved the original source SHA256 in 'sha256'.
Git's autocrlf sometimes changes text bytes during commit. This script adds
'git_sha256' and 'git_bytes' for the exact files available in GitHub.
It never mutates source assets, only the manifest.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "ArtSource/LocalProjectOwned/SOURCE_SHA256_MANIFEST.json"


def main():
    data = json.loads(PATH.read_text(encoding="utf-8-sig"))
    assert len(data["files"]) == 38
    for item in data["files"]:
        rel = item["path"]
        assert rel.startswith("ArtSource/LocalProjectOwned/")
        assert ".." not in Path(rel).parts
        current = (ROOT / rel).read_bytes()
        item["git_bytes"] = len(current)
        item["git_sha256"] = hashlib.sha256(current).hexdigest()
    data["checksum_note"] = (
        "sha256/bytes = originally exported PC bytes; "
        "git_sha256/git_bytes = exact GitHub stored bytes, "
        "which may differ on text after Git line-ending normalization."
    )
    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print("GIT_ARCHIVE_MANIFEST_READY", len(data["files"]))


if __name__ == "__main__":
    main()
