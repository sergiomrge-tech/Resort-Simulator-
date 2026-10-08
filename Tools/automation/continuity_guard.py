"""Read-only anti-regression guard for the Resort Simulator original OSM assets.

No third-party Python dependencies. Executable on local checkouts and GitHub Actions.
It NEVER writes to the repository, changes branches, installs software or merges PRs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINE = ROOT / "docs/checkpoints/ASSET_BASELINE.json"


def git_blob_hash(path: Path) -> str:
    """Replicate the Git blob SHA1 of bytes at path, without relying on git.exe."""
    blob = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(blob)).encode("ascii") + b"\0" + blob).hexdigest()


def evaluate(root: Path, baseline: dict) -> dict:
    checks: list[dict] = []

    def check(label: str, ok: bool, detail: str) -> None:
        checks.append({"check": label, "pass": bool(ok), "detail": detail})

    report_path = root / baseline["report"]
    if not report_path.is_file():
        check("osm-report-exists", False, "Missing " + baseline["report"])
        osm = {}
    else:
        try:
            osm = json.loads(report_path.read_text(encoding="utf-8"))
            check("osm-report-exists", True, baseline["report"])
        except (OSError, json.JSONDecodeError) as err:
            osm = {}
            check("osm-report-valid-json", False, str(err))

    check("map-area-2km2", osm.get("game_area_m2") == baseline["map_area_m2"],
          "got=%r expected=%r" % (osm.get("game_area_m2"), baseline["map_area_m2"]))
    counts = osm.get("real_osm_entities_within_roi", {})
    for key, minimum in baseline["entities"].items():
        number = counts.get(key)
        check("osm-" + key, isinstance(number, int) and number == minimum,
              f"got={number} expected={minimum}")

    for asset in baseline["assets"]:
        path = root / asset["path"]
        isfile = path.is_file()
        check("asset-" + asset["id"] + "-exists", isfile, asset["path"])
        if not isfile:
            continue
        size = path.stat().st_size
        check("asset-" + asset["id"] + "-size", size >= asset["min_bytes"],
              f"{size} bytes; threshold {asset['min_bytes']}")
        expected = asset.get("git_blob_sha1")
        if expected:
            actual = git_blob_hash(path)
            check("asset-" + asset["id"] + "-blob-unchanged", actual == expected,
                  f"sha1={actual} expected={expected}")

    return {
        "status": "PASS" if all(record["pass"] for record in checks) else "FAIL",
        "utc_time": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "git_sha": os.environ.get("GITHUB_SHA", "local-checkout"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "checks": checks,
        "scope": "OSM source and file integrity ONLY. Not a Unity build/visual validation.",
    }


def pr_status(repo: str, token: str, numbers: tuple[int, ...] = (4, 5)) -> dict:
    """Optional read-only API check; network errors are nonfatal to map integrity."""
    out: dict = {}
    if not repo or not token:
        return {"status": "not_requested"}
    for number in numbers:
        url = f"https://api.github.com/repos/{repo}/pulls/{number}"
        request = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ResortSimulator-ContinuityGuard",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.load(response)
            out[str(number)] = {
                "state": data.get("state"), "draft": data.get("draft"),
                "merged": data.get("merged_at") is not None,
                "head_sha": data.get("head", {}).get("sha"),
                "html_url": data.get("html_url")
            }
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError,
                TimeoutError, OSError) as error:
            out[str(number)] = {"status": "unavailable", "error_class": type(error).__name__}
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--output", type=Path, default=Path("continuity_report.json"))
    parser.add_argument("--github", action="store_true")
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    result = evaluate(args.root, baseline)
    if args.github:
        result["open_pr_status"] = pr_status(os.getenv("GITHUB_REPOSITORY", ""),
                                             os.getenv("GITHUB_TOKEN", ""))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    failed = [item["check"] for item in result["checks"] if not item["pass"]]
    print(f"RESORT CONTINUITY: {result['status']} - {len(result['checks'])} checks; "
          f"{len(failed)} failing. Result at {args.output}")
    if failed:
        print("FAILED:", ", ".join(failed))
    print("No Unity compilation or screenshots were performed by this audit.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
