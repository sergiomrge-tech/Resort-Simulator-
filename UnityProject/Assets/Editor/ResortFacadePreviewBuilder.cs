using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace ResortSimulator.Editor
{
    /// <summary>
    /// Studio QA scene for three authored Blender architectural modules.
    /// Not Copacabana gameplay: no new blocks or streets are placed on the OSM map.
    /// Review designs here, then attach approved assets to verified OSM parcels.
    /// Requires REAL Unity Editor; never claim this scene exists before running.
    /// </summary>
    public static class ResortFacadePreviewBuilder
    {
        public const string ScenePath = "Assets/Scenes/R2_ArchitecturalReview.unity";
        private const string ModelsDir = "Assets/Architecture/R2_Prototypes/";
        private const string MaterialsDir = "Assets/Materials/R2_PBR";
        private static readonly string[] Names =
        {
            "R2_ArtDeco_Orla",
            "R2_Residencial_Varandas",
            "R2_Hotel_Contemporaneo"
        };

        [MenuItem("Resort Simulator/02 - Revisar 3 fachadas no Unity")]
        public static void Generate()
        {
            ResortRenderingSetup.EnsureConfigured();
            EnsureFolder("Assets", "Materials");
            EnsureFolder("Assets/Materials", "R2_PBR");
            EnsureFolder("Assets", "Scenes");

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var showroom = new GameObject("R2_ARCHITECTURAL_PROTOTYPES_NOT_GIS_PLACEMENTS");

            int totalRenderers = 0;
            for (int i = 0; i < Names.Length; i++)
            {
                string path = ModelsDir + Names[i] + ".fbx";
                var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                if (importer == null)
                    throw new FileNotFoundException("R2 source FBX not available: " + path);
                if (importer.materialImportMode != ModelImporterMaterialImportMode.ImportStandard)
                {
                    importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                    importer.SaveAndReimport();
                }
                AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (model == null)
                    throw new InvalidOperationException("Unity did not import R2 FBX: " + path);

                var instance = PrefabUtility.InstantiatePrefab(model) as GameObject;
                if (instance == null)
                    throw new InvalidOperationException("Failed to instantiate R2 FBX: " + path);
                instance.name = Names[i] + "__BLENDER_ORIGINAL";
                instance.transform.SetParent(showroom.transform, false);
                instance.transform.localPosition = new Vector3((i - 1) * 10.6f, 0f, 0f);

                var renderers = instance.GetComponentsInChildren<MeshRenderer>(true);
                if (renderers.Length < 10)
                    throw new InvalidOperationException("R2 facade lacks mesh components: " + path);
                foreach (var renderer in renderers)
                {
                    var sourceMaterials = renderer.sharedMaterials;
                    if (sourceMaterials.Length == 0)
                        throw new InvalidOperationException("Missing source material slots: " + renderer.name);
                    var assigned = new Material[sourceMaterials.Length];
                    for (int k = 0; k < assigned.Length; k++)
                    {
                        var source = sourceMaterials[k];
                        if (source == null || !source.name.StartsWith("R2_", StringComparison.Ordinal))
                            throw new InvalidOperationException(
                                "R2 FBX did not retain expected Blender material names at " +
                                renderer.name + ". Recheck ModelImporter; got: " +
                                (source != null ? source.name : "null"));
                        assigned[k] = GetOrCreatePbrMaterial(source.name);
                    }
                    renderer.sharedMaterials = assigned;
                    renderer.shadowCastingMode = ShadowCastingMode.On;
                    renderer.receiveShadows = true;
                }
                totalRenderers += renderers.Length;

                // Dark inspection plinth outside the original GIS city: never a gameplay parcel.
                var plinth = GameObject.CreatePrimitive(PrimitiveType.Cube);
                plinth.name = "QA_PEDESTAL_NOT_COPACABANA_" + Names[i];
                plinth.transform.SetParent(showroom.transform);
                plinth.transform.position = new Vector3((i - 1) * 10.6f, -0.23f, 0f);
                plinth.transform.localScale = new Vector3(9.0f, 0.32f, 4.2f);
                plinth.GetComponent<MeshRenderer>().sharedMaterial =
                    GetOrCreatePbrMaterial("R2_Concreto_Cinza_Calma");
            }

            var sun = new GameObject("QA_Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.3f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(42f, -32f, 0f);
            RenderSettings.sun = sun;

            var go = new GameObject("QA_Camera");
            go.tag = "MainCamera";
            go.transform.position = new Vector3(0f, 8.0f, -24f);
            go.transform.LookAt(new Vector3(0f, 1.8f, 0f));
            var camera = go.AddComponent<Camera>();
            camera.fieldOfView = 55f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.52f, 0.64f, 0.72f);
            go.AddComponent<AudioListener>();

            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(scene, ScenePath))
                throw new IOException("Could not save facade QA scene: " + ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log("R2 UNITY SCENE GENERATED: " + ScenePath +
                      " | real Blender facade instances=3 | renderers=" + totalRenderers +
                      " | status=STUDIO_QA_NOT_FINAL_ART_NOT_CITY");
        }

        private static Material GetOrCreatePbrMaterial(string name)
        {
            Color tint;
            float metallic;
            float roughness;
            switch (name)
            {
                case "R2_Calcario_Areia": tint = new Color(.72f, .63f, .47f); metallic = 0; roughness = .68f; break;
                case "R2_Reboco_Marfim": tint = new Color(.86f, .83f, .72f); metallic = 0; roughness = .79f; break;
                case "R2_Concreto_Quente": tint = new Color(.71f, .68f, .59f); metallic = 0; roughness = .70f; break;
                case "R2_Vidro_Azul_Fumê": tint = new Color(.12f, .27f, .34f); metallic = .20f; roughness = .12f; break;
                case "R2_Vidro_Cinza_Dark": tint = new Color(.09f, .16f, .19f); metallic = .29f; roughness = .12f; break;
                case "R2_Metal_Bronze": tint = new Color(.47f, .31f, .12f); metallic = .87f; roughness = .26f; break;
                case "R2_Aluminio_Escuro": tint = new Color(.14f, .15f, .16f); metallic = .81f; roughness = .34f; break;
                case "R2_Madeira_Tropical": tint = new Color(.32f, .18f, .095f); metallic = 0; roughness = .53f; break;
                case "R2_Ceramica_Terracota": tint = new Color(.42f, .20f, .13f); metallic = 0; roughness = .55f; break;
                case "R2_Folhagem_Premium": tint = new Color(.11f, .26f, .15f); metallic = 0; roughness = .76f; break;
                case "R2_Concreto_Cinza_Calma": tint = new Color(.38f, .40f, .39f); metallic = 0; roughness = .70f; break;
                default: throw new InvalidOperationException("Unknown R2 material: " + name);
            }

            string path = MaterialsDir + "/" + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
                throw new InvalidOperationException("Cannot create R2 PBR material: URP Lit shader missing");
            if (material == null)
            {
                material = new Material(shader);
                material.name = name;
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
            }
            material.SetColor("_BaseColor", tint);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", 1f - roughness);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void EnsureFolder(string parent, string child)
        {
            if (!AssetDatabase.IsValidFolder(parent + "/" + child))
                AssetDatabase.CreateFolder(parent, child);
        }
    }
}
