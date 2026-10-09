# SOL 6.1 — R7 correction checkpoint (09/10/2026)

## Purpose and honesty
This branch `codex/sol61-geradores-r7` corrects the geometry, semantic materials,
UVs and visual QA pipeline of the **real Copacabana** Resort simulator. The
original geographic BlenderGIS `.blend` and original FBX are immutable.
Everything here remains an independent development candidate, NOT an approved
game release or photorealistic artwork.

## Existing/native results observed by supervisor on Windows

On licensed Unity **6000.6.2f1**, Direct3D11, NVIDIA RTX 4060 Ti, using the
previous R7-derived FBX (SHA256 `576b01384531361a5218ee211c2d4f6176615440ac7f1bcd59e9547e96435a67`)
with SOL61's updated Unity C# editor material script snapshot:

- `ResortR7FacadeFinish.Build` **PASS** on real Unity: 50 OSM buildings and
  50 styles; 370 architectural renderer parts; semantic material fallback 0;
  **372 materials** including 2 background city categories; 40 texture maps.
- `ResortR7VisualCapture.Run` **PASS** on real Unity GPU / active
  `UniversalRenderPipelineAsset`: 4 genuine Unity captures; 0 renderers without
  UV0. Those captures still use the **previous R7 FBX geometry**. A new,
  generated SOL61 mesh is NOT validated by these tests.
- Manual visual QA **FAIL**, because ~1,418 background buildings remain simplified
  masses and the pedestrian camera view is physically obstructed. Applying
  better URP materials improved white overexposure but is not a replacement
  for architectural reconstruction or raycast-valid camera placement.
- Files produced by the native run are in the supervisor's disposable
  `D:\ProjectResort_R5_UnityQA\build\R7_PBR_FacadeQA`. Do not label these
  images as Sol geometry results or Unity gameplay FPS.

## Local source and geometry tests
The supervisor executed:

```text
python -m unittest discover -s Tools/tests -p test_r7_contract.py -v
python -m unittest discover -s Tools/tests -p test_r7_uv_pbr_pipeline.py -v
python -m py_compile Tools/Blender/r7_contract.py Tools/Blender/generate_r7_buildings.py Tools/Blender/assemble_r7_city_50.py Tools/geo/r7_expansion_plan.py Tools/geo/r7_mask_city_50.py Tools/tests/test_r7_geometry_native.py
git diff --check
```

**12/12 contract tests and 8/8 R7 pipeline tests passed**, Python compilation
passed and no whitespace errors from `git diff --check`. These are not native
Blender re-import or Unity tests of the **new** Sol-generated FBX.

## Scope and critical follow-up gates
- Read `AGENTS.md`, `docs/DIRECAO_ARTISTICA.md` and GIS provenance first.
- Corrected generation must preserve 50 OSM footprint IDs and their geographic
  positions, all existing roads, the original 46° coordinate rotation, 9 material
  semantics and UV0, with normalized outward facade normals and actual apertures.
- The independent GitHub CI on this branch must run Blender **bpy native smoke**,
  generate 50 buildings, assemble FBX and re-import it, checking SHA256 and
  material/UV/footprint gates before claiming any success. Do NOT merge or expand
  the remaining 1,418 buildings before approval of 50.
- Import NEW Sol-generated FBX into the disposable Unity QA project, compile the
  Editor tools, rerun `-executeMethod ResortR7FacadeFinish.Build` then
  `ResortR7VisualCapture.Run`, inspect actual screenshots (especially street
  view), and only then decide artistic approval. FPS is not yet measured.
- If Blender CI or Unity fails, log the exact exception and correct in this
  branch; do not use fallback shaders as a pass condition.

© OpenStreetMap contributors (ODbL 1.0). All source provenance applies.
