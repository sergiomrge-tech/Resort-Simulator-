// Resort R7: deterministic, author-owned URP facade finish for the 50 OSM buildings.
// Run with licensed Unity Editor:
// Unity.exe -batchmode -quit -projectPath <repo>/UnityProject
//   -executeMethod ResortR7FacadeFinish.Build -logFile <log>
// Creates an R7 scene COPY. Never modifies the original Copacabana GIS meshes,
// R5 sources or QA/Windows preview scenes. This is a material-production stage,
// not artistic approval, an FPS benchmark, or a complete game.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ResortR7FacadeFinish
{
    private const string OutputScene = "Assets/Scenes/R7_Copacabana_50_Fachadas_PBR_VisualQA.unity";
    private const string MaterialDir = "Assets/Materials/R7_Facades";
    private const string TextureDir = "Assets/Textures/R7_Facades";
    private const int Size = 256;
    private static readonly Regex BuildingPattern = new Regex(
        @"R7B_(?<way>[0-9]+(?:_part[0-9]+)?)__(?<style>cop_[a-z0-9_]+)__(?<mesh>.+)",
        RegexOptions.Compiled | RegexOptions.CultureInvariant);
    private static readonly Regex StylePattern = new Regex(
        @"^cop_(?<family>[a-z0-9_]+)_(?<variant>0[1-5])$",
        RegexOptions.Compiled | RegexOptions.CultureInvariant);
    private static readonly Regex MaterialPartPattern = new Regex(
        @"R7_(?:[a-z0-9_]+_)?(?<part>wall|stone|trim|glass|metal|wood|roof|plants|shadow)(?:\.[0-9]+)?$",
        RegexOptions.Compiled | RegexOptions.CultureInvariant);
    private static readonly Dictionary<string, Color> Families = new Dictionary<string, Color>
    {
        { "residencial_orla", new Color(.84f,.78f,.67f) },
        { "residencial_anos70", new Color(.76f,.76f,.71f) },
        { "art_deco_carioca", new Color(.89f,.79f,.65f) },
        { "hotel_classico", new Color(.86f,.82f,.71f) },
        { "hotel_contemporaneo", new Color(.74f,.77f,.76f) },
        { "misto_loja_terrea", new Color(.83f,.75f,.66f) },
        { "residencial_compacto", new Color(.79f,.78f,.72f) },
        { "predio_historico", new Color(.87f,.76f,.62f) },
        { "escritorio_clinica", new Color(.77f,.80f,.80f) },
        { "equipamento_especial", new Color(.81f,.77f,.69f) },
    };
    private static readonly Dictionary<string, Material> Cached = new Dictionary<string, Material>();
    private static readonly HashSet<string> ImportedTextures = new HashSet<string>();

    [Serializable]
    private sealed class Report
    {
        public string status;
        public string origin_scene;
        public string generated_scene;
        public string unity_version;
        public string render_shader;
        public bool urp_pipeline_active;
        public string source_blend_sha256;
        public string source_fbx_sha256;
        public int selected_buildings;
        public int distinct_styles;
        public int finished_renderers;
        public int material_semantic_fallbacks;
        public int material_assets;
        public int texture_assets;
        public string[] osm_way_ids;
        public string limitations;
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException("RESORT_R7_FACADE_FAIL: " + message);
    }

    private static void EnsureDirectory(string path)
    {
        string current = "Assets";
        foreach (string part in path.Substring("Assets/".Length).Split('/'))
        {
            string next = current + "/" + part;
            if (!AssetDatabase.IsValidFolder(next))
                AssetDatabase.CreateFolder(current, part);
            current = next;
        }
    }

    private static string Sha256(string path)
    {
        using (var s = File.OpenRead(path))
        using (var hash = SHA256.Create())
            return BitConverter.ToString(hash.ComputeHash(s)).Replace("-", "").ToLowerInvariant();
    }

    // Tiled value noise; periodic lattice makes texture edges seamless.
    private static float Hash(int x, int y, int salt)
    {
        unchecked
        {
            uint v = (uint)(x * 374761393 + y * 668265263 + salt * 224682251);
            v = (v ^ (v >> 13)) * 1274126177u;
            return ((v ^ (v >> 16)) & 0x00ffffff) / 16777215f;
        }
    }
    private static float Noise(float x, float y, int period, int salt)
    {
        int xi = Mathf.FloorToInt(x);
        int yi = Mathf.FloorToInt(y);
        float fx = x - xi;
        float fy = y - yi;
        fx = fx * fx * (3f - 2f * fx);
        fy = fy * fy * (3f - 2f * fy);
        int x0 = ((xi % period) + period) % period;
        int y0 = ((yi % period) + period) % period;
        int x1 = (x0 + 1) % period;
        int y1 = (y0 + 1) % period;
        return Mathf.Lerp(
            Mathf.Lerp(Hash(x0, y0, salt), Hash(x1, y0, salt), fx),
            Mathf.Lerp(Hash(x0, y1, salt), Hash(x1, y1, salt), fx), fy);
    }
    private static float Height(int x, int y, int familySeed, bool stone)
    {
        // Use exactly integer pixel coordinates: 256-pixel texture tiles repeat.
        float u = ((x % Size) + Size) % Size / (float)Size;
        float v = ((y % Size) + Size) % Size / (float)Size;
        float coarse = Noise(u * 8f, v * 8f, 8, familySeed);
        float fine = Noise(u * 32f, v * 32f, 32, familySeed + 101);
        float result = .65f * coarse + .35f * fine;
        if (stone)
        {
            // Stone aggregate rather than noisy plastic.
            float grain = Noise(u * 64f, v * 64f, 64, familySeed + 233);
            result = .45f * result + .55f * grain;
        }
        return result;
    }
    private static byte Byte01(float value)
    {
        return (byte)Mathf.Clamp(Mathf.RoundToInt(value * 255f), 0, 255);
    }

    private static void WriteIfDifferent(string path, byte[] contents)
    {
        if (File.Exists(path) && File.ReadAllBytes(path).SequenceEqual(contents))
            return;
        File.WriteAllBytes(path, contents);
    }

    private static string Texture(string family, bool stone, bool normal)
    {
        string group = stone ? "stone" : "plaster";
        string path = TextureDir + "/R7_" + family + "_" + group +
                      (normal ? "_normal.png" : "_albedo.png");
        if (ImportedTextures.Contains(path)) return path;
        string absolutePath = Path.Combine(Application.dataPath,
            "Textures/R7_Facades", Path.GetFileName(path));
        if (!File.Exists(absolutePath))
        {
            int seed = family.Aggregate(17, (h, ch) => unchecked(h * 31 + (int)ch)) & 0x7fffffff;
            var tex = new Texture2D(Size, Size, TextureFormat.RGBA32, false, true);
            var colors = new Color32[Size * Size];
            for (int y = 0; y < Size; y++)
                for (int x = 0; x < Size; x++)
                {
                    float h = Height(x, y, seed, stone);
                    if (normal)
                    {
                        float dx = Height(x + 1, y, seed, stone) - Height(x - 1, y, seed, stone);
                        float dy = Height(x, y + 1, seed, stone) - Height(x, y - 1, seed, stone);
                        var n = new Vector3(-dx * 2.5f, -dy * 2.5f, 1f).normalized;
                        colors[y * Size + x] = new Color32(
                            Byte01(n.x * .5f + .5f),
                            Byte01(n.y * .5f + .5f),
                            Byte01(n.z * .5f + .5f), 255);
                    }
                    else
                    {
                        byte c = Byte01(Mathf.Lerp(stone ? .46f : .57f, stone ? .70f : .79f, h));
                        colors[y * Size + x] = new Color32(c, c, c, 255);
                    }
                }
            tex.SetPixels32(colors);
            tex.Apply();
            WriteIfDifferent(absolutePath, tex.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(tex);
        }
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
        var importer = AssetImporter.GetAtPath(path) as TextureImporter;
        Require(importer != null, "Generated PNG not imported: " + path);
        bool dirty = false;
        var wantedType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
        if (importer.textureType != wantedType) { importer.textureType = wantedType; dirty = true; }
        if (importer.wrapMode != TextureWrapMode.Repeat) { importer.wrapMode = TextureWrapMode.Repeat; dirty = true; }
        if (!importer.mipmapEnabled) { importer.mipmapEnabled = true; dirty = true; }
        if (importer.anisoLevel != 4) { importer.anisoLevel = 4; dirty = true; }
        if (dirty) importer.SaveAndReimport();
        ImportedTextures.Add(path);
        return path;
    }

    // Imported FBX renderers can be nested under the named Blender object.
    // Search ancestors, as in the R5 Unity QA implementation.
    private static Match FindBuilding(Renderer renderer)
    {
        Transform node = renderer.transform;
        while (node != null)
        {
            Match building = BuildingPattern.Match(node.gameObject.name);
            if (building.Success) return building;
            node = node.parent;
        }
        return null;
    }

    private static Match FindSemanticPart(Renderer renderer, Match building)
    {
        // The canonical source object, intermediate FBX nodes and mesh names
        // can place the Blender material-category suffix at different levels.
        Match result = MaterialPartPattern.Match(building.Groups["mesh"].Value);
        if (result.Success) return result;
        result = MaterialPartPattern.Match(renderer.gameObject.name);
        if (result.Success) return result;
        foreach (var material in renderer.sharedMaterials)
        {
            if (material == null) continue;
            result = MaterialPartPattern.Match(material.name);
            if (result.Success) return result; // Stable semantic ID exported in FBX material slot.
        }
        MeshFilter meshFilter = renderer.GetComponent<MeshFilter>();
        if (meshFilter != null && meshFilter.sharedMesh != null)
            return MaterialPartPattern.Match(meshFilter.sharedMesh.name);
        return result;
    }

    private static string SemanticFromMaterial(Material material)
    {
        Require(material != null, "NULL_MATERIAL_SLOT");
        Match m = MaterialPartPattern.Match(material.name);
        Require(m.Success, "MATERIAL_SEMANTIC_ID_MISSING: " + material.name);
        return m.Groups["part"].Value;
    }

    private static Color Shade(Color baseColor, int variant, string semantic)
    {
        float delta = (variant - 3) * .022f;
        Color c = new Color(
            Mathf.Clamp01(baseColor.r + delta),
            Mathf.Clamp01(baseColor.g + delta * .7f),
            Mathf.Clamp01(baseColor.b + delta * .55f));
        switch (semantic)
        {
            case "wall": return c;
            case "stone": return Color.Lerp(c, new Color(.55f,.53f,.49f), .35f);
            case "trim": return Color.Lerp(c, new Color(.40f,.37f,.34f), .37f);
            case "roof": return Color.Lerp(c, new Color(.36f,.36f,.33f), .55f);
            case "glass": return new Color(.10f + variant * .012f,.23f + variant * .009f,.29f + variant * .01f);
            case "metal": return variant % 2 == 0 ? new Color(.24f,.30f,.33f) : new Color(.35f,.30f,.24f);
            case "wood": return new Color(.35f,.22f,.13f);
            case "plants": return new Color(.18f,.32f,.18f);
            default: return new Color(.085f,.086f,.081f); // recessed shadow
        }
    }

    private static Material Finish(string style, string family, int variant,
                                   string semantic, Shader shader,
                                   HashSet<string> assets, HashSet<string> textures)
    {
        string key = style + "_" + semantic;
        Material cached;
        if (Cached.TryGetValue(key, out cached)) return cached;
        string path = MaterialDir + "/R7_" + key + ".mat";
        var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (mat == null)
        {
            mat = new Material(shader) { name = "R7_" + key };
            AssetDatabase.CreateAsset(mat, path);
        }
        else if (mat.shader != shader) mat.shader = shader;
        Color tint = Shade(Families[family], variant, semantic);
        if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", tint);
        if (mat.HasProperty("_Color")) mat.SetColor("_Color", tint);
        float metallic = semantic == "metal" ? .70f :
                         semantic == "glass" ? .12f : semantic == "trim" ? .04f : 0f;
        float smooth = semantic == "glass" ? .89f :
                       semantic == "metal" ? .72f :
                       semantic == "wood" ? .29f :
                       semantic == "roof" ? .23f :
                       semantic == "stone" ? .25f : .32f;
        if (semantic == "glass")
        {
            tint.a = .58f;
            if (mat.HasProperty("_Surface")) mat.SetFloat("_Surface", 1f);
            if (mat.HasProperty("_Blend")) mat.SetFloat("_Blend", 0f);
            if (mat.HasProperty("_SrcBlend")) mat.SetFloat("_SrcBlend", (float)UnityEngine.Rendering.BlendMode.SrcAlpha);
            if (mat.HasProperty("_DstBlend")) mat.SetFloat("_DstBlend", (float)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            if (mat.HasProperty("_ZWrite")) mat.SetFloat("_ZWrite", 0f);
            mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            mat.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Transparent;
            if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", tint);
        }
        if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", metallic);
        if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", smooth);
        if (mat.HasProperty("_Glossiness")) mat.SetFloat("_Glossiness", smooth);
        if (semantic == "wall" || semantic == "stone" ||
            semantic == "trim" || semantic == "roof")
        {
            bool stone = semantic != "wall";
            string albedoPath = Texture(family, stone, false);
            string normalPath = Texture(family, stone, true);
            var albedo = AssetDatabase.LoadAssetAtPath<Texture2D>(albedoPath);
            var normal = AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath);
            Require(albedo != null && normal != null, "Generated textures missing");
            if (mat.HasProperty("_BaseMap")) mat.SetTexture("_BaseMap", albedo);
            if (mat.HasProperty("_MainTex")) mat.SetTexture("_MainTex", albedo);
            if (mat.HasProperty("_BumpMap")) mat.SetTexture("_BumpMap", normal);
            if (mat.HasProperty("_BumpScale")) mat.SetFloat("_BumpScale", semantic == "wall" ? .22f : .35f);
            mat.EnableKeyword("_NORMALMAP");
            // UV0 generated in Blender by dominant-axis projection at 2 metres per repeat.
            textures.Add(albedoPath);
            textures.Add(normalPath);
        }
        mat.enableInstancing = true;
        EditorUtility.SetDirty(mat);
        Cached[key] = mat;
        assets.Add(path);
        return mat;
    }

    [MenuItem("Resort/R7/Gerar fachadas PBR dos 50 prédios")]
    public static void Build()
    {
        const string DerivedFbx = "Assets/Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx";
        var pipeline = GraphicsSettings.currentRenderPipeline;
        bool urpActive = pipeline != null && pipeline.GetType().Name.Contains("UniversalRenderPipeline");
        if (!urpActive)
        {
            string[] pipelineGuids = AssetDatabase.FindAssets("t:UniversalRenderPipelineAsset");
            if (pipelineGuids.Length == 0)
            {
                // GUI menu creation does not reliably work with -batchmode.
                // Use the public Unity 6 URP creation API; create real persistent assets
                // in the disposable R7 QA project, never in the immutable GIS source.
                EnsureDirectory("Assets/Settings");
                const string rendererPath = "Assets/Settings/R7_QA_UniversalRenderer.asset";
                const string pipelinePath = "Assets/Settings/R7_QA_URP.asset";
                var rendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(rendererPath);
                if (rendererData == null)
                {
                    rendererData = ScriptableObject.CreateInstance<UniversalRendererData>();
                    AssetDatabase.CreateAsset(rendererData, rendererPath);
                }
                var urpAsset = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(pipelinePath);
                if (urpAsset == null)
                {
                    urpAsset = UniversalRenderPipelineAsset.Create(rendererData);
                    AssetDatabase.CreateAsset(urpAsset, pipelinePath);
                }
                AssetDatabase.SaveAssets();
                pipelineGuids = AssetDatabase.FindAssets("t:UniversalRenderPipelineAsset");
            }
            RenderPipelineAsset qaPipeline = null;
            foreach (string guid in pipelineGuids)
            {
                string assetPath = AssetDatabase.GUIDToAssetPath(guid);
                qaPipeline = AssetDatabase.LoadAssetAtPath<RenderPipelineAsset>(assetPath);
                if (qaPipeline != null) break;
            }
            Require(qaPipeline != null, "URP_PIPELINE_ASSET_NOT_FOUND: package presence is insufficient");
            // This branch is the isolated R7 QA copy; do not modify original source projects.
            GraphicsSettings.defaultRenderPipeline = qaPipeline;
            QualitySettings.renderPipeline = qaPipeline;
            pipeline = GraphicsSettings.currentRenderPipeline;
            urpActive = pipeline != null && pipeline.GetType().Name.Contains("UniversalRenderPipeline");
        }
        Require(urpActive, "URP_PIPELINE_ASSET_NOT_ACTIVE: R7 PBR validation refuses Standard fallback");
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        Require(shader != null, "URP/Lit shader missing despite active URP");
        string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
        string sourceBlend = Path.Combine(repo, "ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend");
        string sourceFbx = Path.Combine(Application.dataPath,
            "ImportedBlender/Copacabana_Real_Blender.fbx");
        var derivedAsset = AssetDatabase.LoadAssetAtPath<GameObject>(DerivedFbx);
        Require(derivedAsset != null, "R7_DERIVED_FBX_MISSING: run Blender R7 pipeline first");
        Require(File.Exists(sourceBlend) && File.Exists(sourceFbx), "GIS originals missing");
        string blendBefore = Sha256(sourceBlend), fbxBefore = Sha256(sourceFbx);
        EnsureDirectory(MaterialDir);
        EnsureDirectory(TextureDir);
        Cached.Clear();
        ImportedTextures.Clear();
        var ids = new HashSet<string>();
        var styles = new HashSet<string>();
        var assets = new HashSet<string>();
        var textures = new HashSet<string>();
        // Generate the complete reusable texture library independently of how
        // Blender truncated FBX mesh labels in an individual R7 import.
        foreach (string family in Families.Keys)
            foreach (bool stone in new[] { false, true })
                foreach (bool normal in new[] { false, true })
                    textures.Add(Texture(family, stone, normal));
        int finished = 0;

        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var city = PrefabUtility.InstantiatePrefab(derivedAsset) as GameObject;
        Require(city != null, "Cannot instantiate derived R7 FBX");
        city.name = "R7_DERIVED_REAL_COPACABANA_50_FINISHED";
        var sunObject = new GameObject("R7_QA_Sun");
        var sun = sunObject.AddComponent<Light>();
        sun.type = LightType.Directional; sun.intensity = 1.0f;
        sun.transform.rotation = Quaternion.Euler(42f, -24f, -22f);
        var cameraObject = new GameObject("Main Camera");
        cameraObject.tag = "MainCamera";
        var qaCamera = cameraObject.AddComponent<Camera>();
        var urpCamera = cameraObject.AddComponent<UniversalAdditionalCameraData>();
        urpCamera.renderPostProcessing = true;
        qaCamera.transform.position = new Vector3(0f, 420f, -570f);
        qaCamera.transform.LookAt(new Vector3(0f, 0f, 0f));
        qaCamera.allowHDR = true;
        var volumeObject = new GameObject("R7_QA_Exposure_Tonemapping");
        var volume = volumeObject.AddComponent<Volume>();
        volume.isGlobal = true;
        volume.priority = 100f;
        const string profilePath = "Assets/Materials/R7_Facades/R7_QA_Tonemapping.asset";
        var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(profilePath);
        if (profile == null)
        {
            profile = ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(profile, profilePath);
        }
        volume.sharedProfile = profile;
        if (!profile.TryGet<Tonemapping>(out var tone)) tone = profile.Add<Tonemapping>(true);
        tone.mode.value = TonemappingMode.ACES;
        if (!profile.TryGet<ColorAdjustments>(out var exposure)) exposure = profile.Add<ColorAdjustments>(true);
        exposure.postExposure.value = -.25f;
        exposure.saturation.value = -4f;
        EditorUtility.SetDirty(profile);
        foreach (var root in scene.GetRootGameObjects())
            foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                var building = FindBuilding(renderer);
                if (building == null) continue; // Roads and other 1,418 volumes preserved.
                string style = building.Groups["style"].Value;
                var parts = StylePattern.Match(style);
                Require(parts.Success, "Unexpected R7 architectural style: " + style);
                string family = parts.Groups["family"].Value;
                Require(Families.ContainsKey(family), "Unrecognized family: " + family);
                int variant = int.Parse(parts.Groups["variant"].Value);
                var semantic = FindSemanticPart(renderer, building);
                string part;
                if (semantic.Success) part = semantic.Groups["part"].Value;
                else { throw new InvalidOperationException("MATERIAL_SEMANTIC_ID_MISSING: " + renderer.name); }
                var finish = Finish(style, family, variant, part, shader, assets, textures);
                var existing = renderer.sharedMaterials;
                Require(existing.Length > 0, "Renderer has no submesh material slots");
                for (int i = 0; i < existing.Length; i++)
                {
                    string slotSemantic = SemanticFromMaterial(existing[i]);
                    Require(slotSemantic == part, "MATERIAL_SEMANTIC_MISMATCH: expected=" + part + " actual=" + slotSemantic);
                    existing[i] = finish;
                }
                renderer.sharedMaterials = existing;
                var filter = renderer.GetComponent<MeshFilter>();
                Require(filter != null && filter.sharedMesh != null &&
                    filter.sharedMesh.HasVertexAttribute(UnityEngine.Rendering.VertexAttribute.TexCoord0),
                    "UV0_MISSING: " + renderer.name);
                ids.Add(building.Groups["way"].Value);
                styles.Add(style);
                finished++;
            }
        Require(ids.Count == 50, "R7 requires exactly 50 real OSM ways, found " + ids.Count);
        Require(styles.Count == 50, "R7 requires 50 distinct styles, found " + styles.Count);
        Require(finished >= 300, "Too few classified R7 detailed renderers");
        Require(textures.Count == 40, "Expect 10 families x 2 textures x 2 patterns");
        Require(blendBefore == Sha256(sourceBlend) && fbxBefore == Sha256(sourceFbx),
                "Original Copacabana source changed");
        AssetDatabase.SaveAssets();
        Require(EditorSceneManager.SaveScene(scene, OutputScene, true),
                "Could not create independent R7 visual QA scene");
        var report = new Report
        {
            status = "R7_URP_LIT_UV0_SEMANTIC_QA_PENDING_VISUAL_REVIEW",
            origin_scene = DerivedFbx,
            generated_scene = OutputScene,
            unity_version = Application.unityVersion,
            render_shader = shader.name,
            urp_pipeline_active = urpActive,
            source_blend_sha256 = blendBefore,
            source_fbx_sha256 = fbxBefore,
            selected_buildings = ids.Count,
            distinct_styles = styles.Count,
            finished_renderers = finished,
            material_semantic_fallbacks = 0,
            material_assets = assets.Count,
            texture_assets = textures.Count,
            osm_way_ids = ids.OrderBy(x => x, StringComparer.Ordinal).ToArray(),
            limitations = "Independent scene created from the R7-derived real Copacabana FBX. Requires active URP and UV0 on every architectural renderer; category-specific FBX material slot names are mandatory. No FPS or artistic approval."
        };
        string outDir = Path.Combine(repo, "build/R7_PBR_FacadeQA");
        Directory.CreateDirectory(outDir);
        File.WriteAllText(Path.Combine(outDir, "material_pass.json"),
            JsonUtility.ToJson(report, true) + "\n", Encoding.UTF8);
        Debug.Log("RESORT_R7_PBR_PASS ways=" + ids.Count +
                  " styles=" + styles.Count + " renderers=" + finished + " semanticFallbacks=0" +
                  " materials=" + assets.Count + " texture_assets=" + textures.Count);
    }
}
