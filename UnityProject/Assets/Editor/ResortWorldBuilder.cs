using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortSimulator.Editor
{
    /// <summary>
    /// Deterministic editor scene factory based only on the original Blender OSM FBX.
    /// Call from Resort Simulator menu or Unity batchmode / GameCI.
    /// The scene is a geographic/blockout QA stage, NOT final visual art.
    /// </summary>
    public static class ResortWorldBuilder
    {
        public const string ModelPath = "Assets/ImportedBlender/Copacabana_Real_Blender.fbx";
        public const string ScenePath = "Assets/Scenes/Copacabana_Pilot.unity";
        public const string ImportReportPath = "build/QA/Copacabana_Unity_Import.json";

        [Serializable]
        private sealed class ImportMetrics
        {
            public string sourceFbx;
            public string scene;
            public string generatedUtc;
            public Vector3 boundsCenterMeters;
            public Vector3 boundsSizeMeters;
            public int renderers;
            public int colliderMeshes;
            public int importedVertices;
            public bool realUnityEditorExecution;
            public string visualState;
        }

        [MenuItem("Resort Simulator/01 - Gerar cena Copacabana (geografia OSM)")]
        public static void Generate()
        {
            // A real Scriptable Render Pipeline is required for the final PBR art;
            // URP package presence alone is insufficient.
            ResortRenderingSetup.EnsureConfigured();
            var source = Path.Combine(Application.dataPath, "ImportedBlender/Copacabana_Real_Blender.fbx");
            if (!File.Exists(source))
                throw new FileNotFoundException("Original Copacabana FBX is missing.", source);

            AssetDatabase.ImportAsset(ModelPath, ImportAssetOptions.ForceSynchronousImport);
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
                throw new InvalidOperationException("The original Blender FBX did not import as a model prefab.");

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var root = new GameObject("GIS_COPACABANA_REAL_FBX_METERS");
            // Blender FBX exporter used -Z forward and Y up. No second 90-degree rotation.
            var instance = PrefabUtility.InstantiatePrefab(model) as GameObject;
            if (instance == null)
                throw new InvalidOperationException("Cannot instantiate the original Copacabana model.");
            instance.name = "OSM_REAL_1468_BuildingFootprints_468_RoadSegments";
            instance.transform.SetParent(root.transform, false);

            var renderers = instance.GetComponentsInChildren<MeshRenderer>(true);
            if (renderers.Length == 0)
                throw new InvalidOperationException("Imported Blender FBX has no MeshRenderer.");
            Bounds extent = renderers[0].bounds;
            foreach (var renderer in renderers)
            {
                extent.Encapsulate(renderer.bounds);
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }
            // In Unity world coordinates, geography must be horizontal on X/Z
            // with a comparatively modest elevation on Y, not lying on its side.
            if (extent.size.x < 1200f || extent.size.x > 3200f ||
                extent.size.z < 1200f || extent.size.z > 3200f ||
                extent.size.y < 10f || extent.size.y > 300f)
                throw new InvalidOperationException(
                    "Map FBX is not in plausible Unity X/Z metres or its Y-up conversion failed: " + extent.size);

            // Original mesh already contains separate road/building material slots.
            // Recolor the imported *instance only* for visibility; preserve source FBX.
            var roadMaterial = GetOrCreateQAMaterial("QA_Asfalto", new Color(0.24f, 0.30f, 0.37f));
            var buildingMaterial = GetOrCreateQAMaterial("QA_Edificios_OSM", new Color(0.82f, 0.74f, 0.62f));
            foreach (var renderer in renderers)
            {
                var existing = renderer.sharedMaterials;
                var replacement = new Material[existing.Length];
                for (int i = 0; i < replacement.Length; i++)
                {
                    string slot = existing[i] != null ? existing[i].name.ToLowerInvariant() : "";
                    replacement[i] = slot.Contains("road") || slot.Contains("street")
                        ? roadMaterial : buildingMaterial;
                }
                renderer.sharedMaterials = replacement;
            }

            // One non-convex collider per actual imported mesh; static world only.
            // Do not add per-building Rigidbody or thousands of MeshColliders.
            var filters = instance.GetComponentsInChildren<MeshFilter>(true);
            int collisionMeshes = 0;
            int importedVertices = 0;
            foreach (var filter in filters)
            {
                if (filter.sharedMesh == null)
                    continue;
                importedVertices += filter.sharedMesh.vertexCount;
                var existingCollider = filter.GetComponent<MeshCollider>();
                var collider = existingCollider != null ? existingCollider : filter.gameObject.AddComponent<MeshCollider>();
                collider.sharedMesh = filter.sharedMesh;
                collider.convex = false;
                collisionMeshes++;
            }

            // Ground is explicitly a TEMPORARY reference; surface lies BELOW the
            // minimum model height to avoid concealing any mapped streets.
            float groundTop = extent.min.y - 0.12f;
            var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "TEMP_REFERENCE_GROUND__NOT_REAL_TERRAIN_OR_BEACH";
            ground.transform.position = new Vector3(extent.center.x, groundTop - 0.25f, extent.center.z);
            ground.transform.localScale = new Vector3(extent.size.x + 160f, 0.5f, extent.size.z + 160f);
            ground.GetComponent<Renderer>().sharedMaterial =
                GetOrCreateQAMaterial("QA_Terreno_Provisorio", new Color(0.18f, 0.29f, 0.27f));

            var sunObject = new GameObject("Sun_DayNightCycle");
            var sun = sunObject.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.70f;
            sunObject.AddComponent<DayNightCycle>().SetSun(sun);
            sunObject.transform.rotation = Quaternion.Euler(52f, -32f, 0);
            RenderSettings.sun = sun;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.54f, 0.62f, 0.71f);

            // Spawn on the temporary inspection perimeter, clear of real buildings;
            // the player can enter the map. No fictional buildings are introduced.
            var player = new GameObject("Player_FirstPerson");
            player.transform.position = new Vector3(extent.min.x - 22f, groundTop + 0.04f, extent.center.z);
            player.transform.rotation = Quaternion.LookRotation(Vector3.right, Vector3.up);
            var character = player.AddComponent<CharacterController>();
            character.height = 1.85f;
            character.radius = 0.36f;
            character.center = new Vector3(0f, 0.925f, 0f);
            character.stepOffset = 0.29f;
            character.slopeLimit = 48f;

            var head = new GameObject("ViewPivot").transform;
            head.SetParent(player.transform, false);
            head.localPosition = new Vector3(0f, 1.67f, 0f);
            var cameraObject = new GameObject("MainCamera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.SetParent(head, false);
            cameraObject.transform.localPosition = Vector3.zero;
            var cam = cameraObject.AddComponent<Camera>();
            cam.fieldOfView = 69f;
            cam.nearClipPlane = 0.08f;
            cam.farClipPlane = 4000f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.54f, 0.76f, 0.89f);
            cameraObject.AddComponent<AudioListener>();
            player.AddComponent<PlayerController>().SetCameraPivot(head);

            var attribution = new GameObject("OPENSTREETMAP_ATTRIBUTION_ODBL");
            attribution.AddComponent<GeodataAttribution>();

            // Future visual pass: limit dynamic shadow draw distance rather than
            // shadowing all 2km of city at once.
            QualitySettings.shadowDistance = Mathf.Min(QualitySettings.shadowDistance, 180f);

            Directory.CreateDirectory(Path.Combine(Application.dataPath, "Scenes"));
            var current = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(current, ScenePath))
                throw new IOException("Could not save Copacabana scene: " + ScenePath);

            // This report can only be emitted by a REAL Unity Editor invocation.
            // It is evidence of import-time geometry, not screenshot/FPS validation.
            var projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var reportPath = Path.Combine(projectRoot, ImportReportPath);
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
            var metrics = new ImportMetrics
            {
                sourceFbx = ModelPath,
                scene = ScenePath,
                generatedUtc = DateTime.UtcNow.ToString("O"),
                boundsCenterMeters = extent.center,
                boundsSizeMeters = extent.size,
                renderers = renderers.Length,
                colliderMeshes = collisionMeshes,
                importedVertices = importedVertices,
                realUnityEditorExecution = true,
                visualState = "GEOGRAPHIC_BLOCKOUT_NOT_FINAL_ART"
            };
            File.WriteAllText(reportPath, JsonUtility.ToJson(metrics, true));

            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();

            Debug.Log("R1 COPACABANA SCENE: " + ScenePath +
                      " | FBX bounds(m): " + extent +
                      " | mesh renderers=" + renderers.Length +
                      " | static mesh colliders=" + collisionMeshes +
                      " | visual status=GEOGRAPHIC BLOCKOUT, NOT FINAL ART.");
        }

        // Persist scene materials as real Unity assets. Unsaved new Material instances
        // may disappear when reopening a generated scene or loading a player build.
        // Names and paths are deterministic across repeated Generate() calls.
        private static Material GetOrCreateQAMaterial(string name, Color tint)
        {
            const string folder = "Assets/Materials/QA";
            if (!AssetDatabase.IsValidFolder("Assets/Materials"))
                AssetDatabase.CreateFolder("Assets", "Materials");
            if (!AssetDatabase.IsValidFolder(folder))
                AssetDatabase.CreateFolder("Assets/Materials", "QA");

            string path = folder + "/" + name + ".mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);

            // Merely declaring the URP package in manifest.json does not enable URP.
            bool isUrp = GraphicsSettings.currentRenderPipeline != null;
            Shader shader = isUrp
                ? Shader.Find("Universal Render Pipeline/Lit")
                : Shader.Find("Standard");
            if (shader == null)
                throw new InvalidOperationException(
                    "Shader unavailable for active Unity pipeline. Configure URP explicitly before building.");

            if (mat == null)
            {
                mat = new Material(shader);
                mat.name = name;
                AssetDatabase.CreateAsset(mat, path);
            }
            else
            {
                mat.shader = shader;
            }

            // URP Lit uses _BaseColor; Standard uses _Color. Material.color is not
            // dependable for an arbitrary shader and can create invisible QA tint.
            if (mat.HasProperty("_BaseColor"))
                mat.SetColor("_BaseColor", tint);
            else if (mat.HasProperty("_Color"))
                mat.SetColor("_Color", tint);
            else
                throw new InvalidOperationException("Shader does not expose a supported base color: " + shader.name);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        /// <summary>Unity batchmode / GameCI entrypoint; demands real licensed Unity execution.</summary>
        public static void BuildWindows()
        {
            Generate();
            var projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var destination = Path.Combine(projectRoot, "build", "StandaloneWindows64", "ResortSimulator.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(destination));

            PlayerSettings.productName = "Resort Simulator";
            PlayerSettings.companyName = "Resort Simulator";
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = destination,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (result == null || result.summary.result != BuildResult.Succeeded || !File.Exists(destination))
                throw new InvalidOperationException("Windows build failed or executable missing. Check the Unity Editor log.");
            Debug.Log("UNITY WINDOWS BUILD SUCCESS: " + destination);
        }
    }
}
