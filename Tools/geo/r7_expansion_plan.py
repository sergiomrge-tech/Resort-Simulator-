"""Deterministic OSM expansion manifest; does not materialize buildings."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSIGN = ROOT / "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
R7_MASK = ROOT / "UnityProject/Assets/Architecture/R7_Pilot50/R7_SOURCE_MASK_QA.json"
BASELINE_MASK = ROOT / "UnityProject/Assets/Architecture/R5_Pilot50/R5_SOURCE_MASK_QA.json"
OUT = ROOT / "geo/procedural/R7_EXPANSION_PLAN.json"
HELD_BACK = {"way/1048277518", "way/1048277521"}


def expansion_rows(buildings, pilot):
    by_id = {b["building_id"]: b for b in buildings}
    if len(by_id) != 1468 or len(buildings) != 1468 or len(pilot) != 50 or not pilot <= set(by_id):
        raise RuntimeError("OSM expansion source/pilot count mismatch")
    rows = sorted((b for b in buildings if b["building_id"] not in pilot),
                  key=lambda b: b["building_id"])
    if len(rows) != 1418:
        raise RuntimeError("Expected exactly 1,418 remaining real OSM buildings")
    return rows


def main():
    source = json.loads(ASSIGN.read_text(encoding="utf-8"))
    mask_path = R7_MASK if R7_MASK.is_file() else BASELINE_MASK
    pilot_report = json.loads(mask_path.read_text(encoding="utf-8"))
    buildings = source["buildings"]
    pilot = set(pilot_report["masked_way_ids"])
    rows = expansion_rows(buildings, pilot)
    actual_r7 = mask_path == R7_MASK
    if actual_r7 and pilot_report["status"] != "R7_FIFTY_OSM_MASK_ALL_ROAD_GEOMETRY_IDENTICAL":
        raise RuntimeError("R7 mask status invalid")
    plan = {
        "status": "R7_DETERMINISTIC_EXPANSION_PLAN_NOT_MATERIALIZED",
        "target_total": 1468,
        "pilot_selected_count": 50,
        "pilot_materialized_count": 50 if actual_r7 else 0,
        "pilot_selection_status": "R7_BLENDER_GENERATED_UNITY_QA_PENDING" if actual_r7 else "R5_BASELINE_SELECTION_R7_NOT_GENERATED",
        "native_unity_gate_passed": False,
        "supervisor_visual_approval": False,
        "remaining_count": 1418,
        "source_assignments_sha256": hashlib.sha256(ASSIGN.read_bytes()).hexdigest(),
        "pilot_mask_sha256": hashlib.sha256(mask_path.read_bytes()).hexdigest(),
        "pilot_mask_source": str(mask_path.relative_to(ROOT)),
        "source_data_ref": "geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json (includes original OSM footprint rings)",
        "source": "OSM ways and frozen real footprint/height/style assignment; ODbL 1.0",
        "compatibility": "Preserve source polygon, centroid, geospatial frame, estimated height provenance and frozen family/style. R7 generator recesses most facade attachments; polygon-level collision proof remains pending real Blender/Unity inspection.",
        "batch_index_frame": "Sorted remaining IDs in this manifest only; NOT raw --mode city --start",
        "reserved_manual_review_ids": sorted(HELD_BACK),
        "batches": [{"plan_start": i, "count": min(50, len(rows)-i),
                     "building_ids": [r["building_id"] for r in rows[i:i+50]]}
                    for i in range(0, len(rows), 50)],
        "buildings": [{**{k: b[k] for k in (
            "building_id", "style_id", "visual_family", "height_for_visualization_m",
            "height_provenance", "area_footprint_m2", "centroid_local_xy_m")},
            "automatic_generation_allowed": b["building_id"] not in HELD_BACK} for b in rows],
        "gate": "Do not apply any batch to the full map until 50-building visual review and measured Unity performance are approved.",
    }
    OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("R7_EXPANSION_PLAN", len(rows), "remaining;", len(plan["batches"]),
          "deterministic batches; not applied")


if __name__ == "__main__":
    main()
