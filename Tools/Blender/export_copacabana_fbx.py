"""Export existing BlenderGIS Copacabana map to Unity-friendly FBX.

Source is the previously validated Blender .blend; no reconstructed fake city.
Run: blender -b ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend \
    --python Tools/Blender/export_copacabana_fbx.py
"""
import bpy
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
source = root / "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"
report = root / "geo/data/report.json"
dest = root / "UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"
dest.parent.mkdir(parents=True, exist_ok=True)
if not source.is_file():
    raise RuntimeError("Original Copacabana Blender .blend missing.")
if not report.is_file():
    raise RuntimeError("Original OSM report missing.")
metadata = json.loads(report.read_text(encoding="utf-8"))
assert metadata["game_area_m2"] == 2_000_000
assert metadata["real_osm_entities_within_roi"]["building"] >= 1000
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if not meshes:
    raise RuntimeError("Real Blender map contains no mesh.")
bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
# Blender Z-up to Unity Y-up via FBX exporter conversion.
bpy.ops.export_scene.fbx(
    filepath=str(dest),
    use_selection=True,
    object_types={"MESH"},
    axis_forward="-Z",
    axis_up="Y",
    global_scale=1.0,
    apply_unit_scale=True,
    bake_space_transform=False,
    path_mode="AUTO",
    use_mesh_modifiers=True,
    add_leaf_bones=False
)
if dest.stat().st_size < 100_000:
    raise RuntimeError("Unexpectedly small FBX export.")
print(f"BLENDER-TO-UNITY MAP OK: {len(meshes)} mesh(es), {dest.stat().st_size} bytes")
print("ORIGINAL BLEND PRESERVED:", source)
print("OSM attribution: © OpenStreetMap contributors, ODbL 1.0")
