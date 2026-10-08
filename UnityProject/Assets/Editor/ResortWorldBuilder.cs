using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ResortSimulator.Editor
{
    // All scene editing runs in the Editor, never overwrites arbitrary user scenes.
    public static class ResortWorldBuilder
    {
        public const string Model = "Assets/ImportedOSM/copacabana_base.obj";
        public const string Scene = "Assets/Scenes/Copacabana_Pilot.unity";

        [MenuItem("Resort Simulator/01 - Gerar Copacabana real (blockout)")]
        public static void Generate()
        {
            var disk = Path.Combine(Application.dataPath,
                "ImportedOSM/copacabana_base.obj");
            if (!File.Exists(disk))
                throw new FileNotFoundException("Real OSM asset not yet generated. Run geography CI.", disk);

            AssetDatabase.ImportAsset(Model, ImportAssetOptions.ForceSynchronousImport);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Model);
            if (prefab == null)
                throw new InvalidOperationException("Unity did not import the REAL OSM OBJ.");

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,
                NewSceneMode.Single);

            // Temporary neutral ground for visual reference, not a fake Copacabana beach.
            var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "TEMP_Ground_Reference_NotDEM";
            ground.transform.localScale = new Vector3(2000f, 1f, 1000f);
            ground.transform.position = new Vector3(0f, -1f, 0f);
            var markerMat = new Material(Shader.Find("Standard"));
            markerMat.color = new Color(0.56f, 0.64f, 0.60f);
            ground.GetComponent<Renderer>().sharedMaterial = markerMat;

            var root = new GameObject("GIS_METRIC_Xcoast_Yinland_Zup");
            // OSM pipeline exports Z-up. Unity Y-up after rotation:
            // original (x, y, z) -> (x, z, -y).
            root.transform.rotation = Quaternion.Euler(-90f, 0f, 0f);
            var mesh = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (mesh == null)
                throw new InvalidOperationException("Could not instantiate OSM mesh prefab.");
            mesh.name = "OSM_REAL_Buildings_and_Roads";
            mesh.transform.SetParent(root.transform, false);
            if (mesh.GetComponentsInChildren<Renderer>(true).Length == 0)
                throw new InvalidOperationException("OSM OBJ contains no renderable geometry.");

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.35f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(53f, -35f, 0f);

            var cameraObject = new GameObject("InspectionCamera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(-260, 120, 540);
            cameraObject.transform.LookAt(new Vector3(0, 15, 0));
            var cam = cameraObject.AddComponent<Camera>();
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 3800f;
            cameraObject.AddComponent<AudioListener>();
            cameraObject.AddComponent<CameraFlyController>();

            new GameObject("OPENSTREETMAP_ODBL_LICENSE")
                .AddComponent<GeodataAttribution>();

            Directory.CreateDirectory(Path.Combine(Application.dataPath, "Scenes"));
            if (!EditorSceneManager.SaveScene(scene, Scene))
                throw new IOException("Could not save the generated scene.");

            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(Scene, true)
            };
            AssetDatabase.SaveAssets();
            Debug.Log("Scene generated using REAL OpenStreetMap footprints: " + Scene);
        }

        // GameCI - static entrypoint for a licensed Unity build.
        public static void BuildWindows()
        {
            Generate();
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "../.."));
            string target = Path.Combine(repo,
                "build", "StandaloneWindows64", "ResortSimulator.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(target));
            PlayerSettings.productName = "Resort Simulator";
            PlayerSettings.companyName = "Resort Simulator";
            PlayerSettings.SetScriptingBackend(
                UnityEditor.Build.NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { Scene },
                locationPathName = target,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (report == null || report.summary.result != BuildResult.Succeeded)
                throw new InvalidOperationException("Unity Windows compilation failed. See GameCI logs.");
            if (!File.Exists(target))
                throw new IOException("The EXE was not created: " + target);
            Debug.Log("WINDOWS BUILD VERIFIED: " + target);
        }
    }
}
