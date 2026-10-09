// Project Resort R3: real Unity Editor validation and reproducible preview scene.
// This is a native Unity Editor operation, not a synthetic screenshot.
// Source: Assets/Architecture/R3_Pilot/R3_Orla_Piloto_Derivado.fbx.
// Run Unity -batchmode -quit -projectPath <UnityProject> -executeMethod ResortR3UnityValidation.Validate
// This method NEVER replaces the original GIS Blender file or original FBX.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

public static class ResortR3UnityValidation
{
    private const string DerivedModel = "Assets/Architecture/R3_Pilot/R3_Orla_Piloto_Derivado.fbx";
    private const string SourceCityModel = "Assets/ImportedBlender/Copacabana_Real_Blender.fbx";
    private const string ScenePath = "Assets/Scenes/R3_Copacabana_Piloto_EditorQA.unity";
    private const string MaterialsDir = "Assets/Materials/R3_QA";
    private const string CandidateHotelId = "1048277518";
    private const string CandidateResidentialId = "1048277521";

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new InvalidOperationException("R3 UNITY VALIDATION FAILED: " + message);
    }

    private static string ToJsonNumber(float value)
    {
        return value.ToString("0.####", CultureInfo.InvariantCulture);
    }

    private static string VectorJson(Vector3 p)
    {
        return "[" + ToJsonNumber(p.x) + "," + ToJsonNumber(p.y) + "," +
               ToJsonNumber(p.z) + "]";
    }

    private static string FileSha256(string path)
    {
        using (SHA256 sha = SHA256.Create())
        using (FileStream file = File.OpenRead(path))
            return BitConverter.ToString(sha.ComputeHash(file)).Replace("-", "").ToLowerInvariant();
    }

    private static Material GetQaMaterial(string key, Color color, float metallic, float smoothness)
    {
        if (!AssetDatabase.IsValidFolder("Assets/Materials"))
            AssetDatabase.CreateFolder("Assets", "Materials");
        if (!AssetDatabase.IsValidFolder(MaterialsDir))
            AssetDatabase.CreateFolder("Assets/Materials", "R3_QA");
        string path = MaterialsDir + "/" + key + ".mat";
        Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (mat == null)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (GraphicsSettings.currentRenderPipeline == null || shader == null)
                shader = Shader.Find("Standard");
            Require(shader != null, "Unity Standard/URP shader not available");
            mat = new Material(shader) { name = key };
            AssetDatabase.CreateAsset(mat, path);
        }

        if (mat.HasProperty("_BaseColor"))
            mat.SetColor("_BaseColor", color);
        if (mat.HasProperty("_Color"))
            mat.SetColor("_Color", color);
        if (mat.HasProperty("_Metallic"))
            mat.SetFloat("_Metallic", metallic);
        if (mat.HasProperty("_Smoothness"))
            mat.SetFloat("_Smoothness", smoothness);
        if (mat.HasProperty("_Glossiness"))
            mat.SetFloat("_Glossiness", smoothness);
        EditorUtility.SetDirty(mat);
        return mat;
    }

    private static Bounds AggregateBounds(Renderer[] renderers)
    {
        Bounds b = renderers[0].bounds;
        for (int i = 1; i < renderers.Length; i++)
            b.Encapsulate(renderers[i].bounds);
        return b;
    }

    private static bool IsHero(string objectName)
    {
        return objectName.Contains("R3_OWNED_") &&
               (objectName.Contains(CandidateHotelId) ||
                objectName.Contains(CandidateResidentialId));
    }

    public static void Validate()
    {
        string repoRoot = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
        string citySource = Path.Combine(repoRoot, "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend");
        string cityFbxSource = Path.Combine(Application.dataPath, "ImportedBlender/Copacabana_Real_Blender.fbx");
        string derivedFbxPath = Path.Combine(Application.dataPath, "Architecture/R3_Pilot/R3_Orla_Piloto_Derivado.fbx");
        string qaFolder = Path.Combine(repoRoot, "build", "UnityR3NativeQA");
        Directory.CreateDirectory(qaFolder);

        Require(File.Exists(citySource), "original Blender source is missing");
        Require(File.Exists(cityFbxSource), "original OSM FBX is missing");
        Require(File.Exists(derivedFbxPath), "the derived model is missing");

        string blenderHashBefore = FileSha256(citySource);
        string originalFbxHashBefore = FileSha256(cityFbxSource);
        string derivedHash = FileSha256(derivedFbxPath);
        Debug.Log("R3_NATIVE_EDITOR_START Unity=" + Application.unityVersion + " hash=" + derivedHash);

        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        GameObject sourcePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(SourceCityModel);
        GameObject derivedPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(DerivedModel);
        Require(sourcePrefab != null && derivedPrefab != null, "FBX model import returned null");

        MeshFilter[] sourceFilters = sourcePrefab.GetComponentsInChildren<MeshFilter>(true);
        MeshFilter[] derivedFilters = derivedPrefab.GetComponentsInChildren<MeshFilter>(true);
        Require(sourceFilters.Length > 0, "source map has no meshes");
        Require(derivedFilters.Length >= 3, "derived scene lacks city and two hero meshes");

        long sourceTriangles = 0;
        foreach (MeshFilter f in sourceFilters)
            if (f.sharedMesh != null)
                sourceTriangles += f.sharedMesh.triangles.Length / 3;
        long derivedTriangles = 0;
        foreach (MeshFilter f in derivedFilters)
            if (f.sharedMesh != null)
                derivedTriangles += f.sharedMesh.triangles.Length / 3;
        Require(sourceTriangles >= 26000, "original city import has inadequate triangles");
        Require(derivedTriangles > 26000, "derived city import has inadequate triangles");

        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        GameObject instance = PrefabUtility.InstantiatePrefab(derivedPrefab) as GameObject;
        Require(instance != null, "could not instantiate R3 FBX prefab");
        instance.name = "R3 Copacabana Original OSM Derivative (Blender Geometry)";
        Renderer[] renderers = instance.GetComponentsInChildren<Renderer>(true);
        Require(renderers.Length >= 3, "no meaningful imported renderer collection");

        Renderer[] hero = renderers.Where(x => IsHero(x.gameObject.name)).ToArray();
        // Blender FBX import may introduce one hierarchy wrapper: accept named parents too.
        if (hero.Length < 2)
            hero = renderers.Where(x =>
                IsHero(x.gameObject.name) ||
                (x.transform.parent != null && IsHero(x.transform.parent.name))).ToArray();
        Require(hero.Length >= 2, "two original R3 author building models are not both imported");

        Bounds heroBounds = AggregateBounds(hero);
        Bounds entireScene = AggregateBounds(renderers);
        Require(entireScene.size.x > 1000f && entireScene.size.z > 1000f,
            "geographic model does not preserve kilometer-scale map");
        Require(heroBounds.size.x < 140f && heroBounds.size.z < 140f,
            "two architectural imports positioned outside expected pilot");

        Material roads = GetQaMaterial("R3_OSM_Roads_Inspection", new Color(0.26f, 0.27f, 0.29f), .02f, .15f);
        Material oldBuildings = GetQaMaterial("R3_OSM_Buildings_Inspection", new Color(.73f, .70f, .64f), 0f, .28f);
        Material glazing = GetQaMaterial("R3_Author_Glazing_Inspection", new Color(.17f, .34f, .39f), .16f, .83f);
        Material wood = GetQaMaterial("R3_Author_Wood_Inspection", new Color(.36f, .23f, .13f), 0f, .38f);
        Material finish = GetQaMaterial("R3_Author_Finish_Inspection", new Color(.90f, .84f, .74f), 0f, .38f);
        Material metallic = GetQaMaterial("R3_Author_Metal_Inspection", new Color(.36f, .39f, .42f), .65f, .69f);

        foreach (Renderer rend in renderers)
        {
            Material[] originalMaterials = rend.sharedMaterials;
            Material[] replacementMaterials = new Material[originalMaterials.Length];
            for (int i = 0; i < originalMaterials.Length; i++)
            {
                string materialName = originalMaterials[i] != null ? originalMaterials[i].name.ToLowerInvariant() : "";
                string rendererName = rend.gameObject.name.ToLowerInvariant();
                if (rendererName.Contains("gis_derived") && materialName.Contains("road"))
                    replacementMaterials[i] = roads;
                else if (rendererName.Contains("gis_derived"))
                    replacementMaterials[i] = oldBuildings;
                else if (materialName.Contains("glass"))
                    replacementMaterials[i] = glazing;
                else if (materialName.Contains("wood"))
                    replacementMaterials[i] = wood;
                else if (materialName.Contains("metal"))
                    replacementMaterials[i] = metallic;
                else
                    replacementMaterials[i] = finish;
            }
            rend.sharedMaterials = replacementMaterials;
        }

        GameObject sunlight = new GameObject("QA Real Unity Sun - not final art");
        Light sun = sunlight.AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.intensity = 1.5f;
        sunlight.transform.eulerAngles = new Vector3(52f, -25f, 0f);
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(.63f, .70f, .77f);

        GameObject camObj = new GameObject("R3 Camera - real Unity editor evidence");
        Camera camera = camObj.AddComponent<Camera>();
        camObj.tag = "MainCamera";
        camera.orthographic = true;
        camera.orthographicSize = 98f;
        camera.nearClipPlane = .15f;
        camera.farClipPlane = 4500f;
        camera.backgroundColor = new Color(.67f, .76f, .87f);
        camera.clearFlags = CameraClearFlags.Skybox;
        Vector3 aim = heroBounds.center;
        aim.y += 4f;
        camObj.transform.position = aim + new Vector3(95f, 185f, -145f);
        camObj.transform.LookAt(aim);

        if (!AssetDatabase.IsValidFolder("Assets/Scenes"))
            AssetDatabase.CreateFolder("Assets", "Scenes");
        bool saved = EditorSceneManager.SaveScene(scene, ScenePath);
        Require(saved, "Unity could not save actual R3 scene");

        string screenshotPath = Path.Combine(qaFolder, "R3_Piloto_Real_Unity_Editor_QA.png");
        string renderStatus = "NOT_RENDERED";
        string closeupScreenshotPath = Path.Combine(qaFolder, "R3_Piloto_Hotel_Residencial_Unity_Closeup_QA.png");
        string closeupRenderStatus = "NOT_RENDERED";
        RenderTexture rt = null;
        Texture2D tex = null;
        try
        {
            rt = new RenderTexture(1600, 900, 24, RenderTextureFormat.ARGB32);
            rt.Create();
            camera.targetTexture = rt;
            camera.Render();
            RenderTexture.active = rt;
            tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0);
            tex.Apply(false);
            File.WriteAllBytes(screenshotPath, tex.EncodeToPNG());
            Require(new FileInfo(screenshotPath).Length > 35000, "Unity screenshot is blank/too small");
            renderStatus = "GENUINE_UNITY_CAMERA_RENDER";

            // A second, genuinely rendered camera view brings the architectural
            // pair into frame. The earlier wide shot remains as geographical QA.
            // Reuse the same native render target to avoid fake screenshot edits.
            try
            {
                camera.orthographicSize = 39f;
                camObj.transform.position = aim + new Vector3(46f, 72f, -72f);
                camObj.transform.LookAt(aim);
                camera.Render();
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0);
                tex.Apply(false);
                File.WriteAllBytes(closeupScreenshotPath, tex.EncodeToPNG());
                Require(new FileInfo(closeupScreenshotPath).Length > 30000,
                        "Unity architectural closeup is blank/too small");
                closeupRenderStatus = "GENUINE_UNITY_CAMERA_RENDER";
                Require(EditorSceneManager.SaveScene(scene, ScenePath),
                        "Unity could not save closeup QA camera placement");
            }
            catch (Exception closeupError)
            {
                Debug.LogWarning("R3_CLOSEUP_RENDER_NOT_AVAILABLE: " + closeupError);
                closeupRenderStatus = "NOT_RENDERED";
            }
        }
        catch (Exception ex)
        {
            Debug.LogWarning("R3_NATIVE_RENDER_NOT_AVAILABLE: " + ex);
            renderStatus = "NOT_RENDERED";
        }
        finally
        {
            camera.targetTexture = null;
            RenderTexture.active = null;
            if (rt != null)
            {
                rt.Release();
                UnityEngine.Object.DestroyImmediate(rt);
            }
            if (tex != null)
                UnityEngine.Object.DestroyImmediate(tex);
        }

        Require(blenderHashBefore == FileSha256(citySource), "Blender .blend source was modified");
        Require(originalFbxHashBefore == FileSha256(cityFbxSource), "original geographic FBX was modified");

        string reportPath = Path.Combine(qaFolder, "R3_Unity_Editor_QA_Report.json");
        string report = "{\n" +
            "  \"status\": \"NATIVE_UNITY_EDITOR_IMPORTED_AND_SCENE_SAVED\",\n" +
            "  \"unity_version\": \"" + Application.unityVersion + "\",\n" +
            "  \"original_source_sha256\": \"" + blenderHashBefore + "\",\n" +
            "  \"original_fbx_sha256\": \"" + originalFbxHashBefore + "\",\n" +
            "  \"derived_fbx_sha256\": \"" + derivedHash + "\",\n" +
            "  \"source_mesh_filters\": " + sourceFilters.Length + ",\n" +
            "  \"derived_mesh_filters\": " + derivedFilters.Length + ",\n" +
            "  \"hero_renderers\": " + hero.Length + ",\n" +
            "  \"source_triangles\": " + sourceTriangles + ",\n" +
            "  \"derived_triangles\": " + derivedTriangles + ",\n" +
            "  \"city_bounding_size\": " + VectorJson(entireScene.size) + ",\n" +
            "  \"hero_bounding_center\": " + VectorJson(heroBounds.center) + ",\n" +
            "  \"hero_bounding_size\": " + VectorJson(heroBounds.size) + ",\n" +
            "  \"scene\": \"" + ScenePath + "\",\n" +
            "  \"render_status\": \"" + renderStatus + "\",\n" +
            "  \"closeup_render_status\": \"" + closeupRenderStatus + "\",\n" +
            "  \"visual_approval\": false,\n" +
            "  \"limits\": \"Scene is a genuine Unity Editor QA setup, not final gameplay or art.\"\n" +
            "}\n";
        File.WriteAllText(reportPath, report, Encoding.UTF8);
        AssetDatabase.SaveAssets();
        Debug.Log("R3_NATIVE_UNITY_EDITOR_QA_PASS: " + reportPath + " render=" + renderStatus + " closeup=" + closeupRenderStatus);
    }
}
