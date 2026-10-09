// R7 native Unity visual QA through URP SubmitRenderRequest on a real GPU.
// Must be run AFTER ResortR7FacadeFinish.Build, on a licensed Windows Unity Editor.
// This is an inspection tool, not evidence of Steam-ready visuals or measured FPS.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

public static class ResortR7VisualCapture
{
    private const string ScenePath = "Assets/Scenes/R7_Copacabana_50_Fachadas_PBR_VisualQA.unity";
    private static readonly Regex Named = new Regex(
        @"R7B_(?<osm>[0-9]+(?:_part[0-9]+)?)__(?<style>cop_[a-z0-9_]+)__",
        RegexOptions.Compiled | RegexOptions.CultureInvariant);

    [Serializable]
    private sealed class Shot
    {
        public string filename;
        public string sha256;
        public string osm_way;
        public string style;
        public string viewpoint;
        public long bytes;
    }
    [Serializable]
    private sealed class Report
    {
        public string status;
        public string unity_version;
        public string renderer;
        public string gpu;
        public string shader_pipeline;
        public string scene;
        public int recognized_buildings;
        public int recognized_renderers;
        public int meshes_without_uv0;
        public int materials_using_r7;
        public string derived_fbx_sha256;
        public Shot[] screenshots;
        public bool artistic_gate_passed = false;
        public bool fps_measured = false;
        public string limitations;
    }
    private sealed class Group
    {
        public string id;
        public string style;
        public Bounds bounds;
        public int parts;
    }
    [Serializable] private sealed class MaterialPass
    {
        public int finished_renderers;
        public string derived_fbx_sha256;
    }

    private static void Require(bool condition, string detail)
    {
        if (!condition) throw new InvalidOperationException("RESORT_R7_CAPTURE_FAILED: " + detail);
    }
    private static string Sha(string path)
    {
        using (var stream = File.OpenRead(path))
        using (var hash = SHA256.Create())
            return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
    private static Match Find(Renderer r)
    {
        for (Transform t = r.transform; t != null; t = t.parent)
        {
            var m = Named.Match(t.gameObject.name);
            if (m.Success) return m;
        }
        return null;
    }
    private static Shot Capture(Camera cam, Bounds b, string id, string style,
                                string viewpoint, string output, bool streetLevel)
    {
        float width = Mathf.Max(b.size.x, b.size.z);
        float distance = Mathf.Max(22, width * 2.2f);
        Vector3 target = b.center;
        if (streetLevel)
        {
            cam.transform.position = new Vector3(
                b.center.x + distance * .7f, b.min.y + 2.2f,
                b.center.z - distance * .8f);
            target = new Vector3(b.center.x, b.min.y + Mathf.Max(5f,b.size.y * .34f), b.center.z);
            cam.fieldOfView = 58f;
        }
        else
        {
            cam.transform.position = new Vector3(
                b.center.x + distance * .8f,
                b.min.y + Mathf.Max(b.size.y * .8f, distance * .65f),
                b.center.z - distance);
            cam.fieldOfView = 49f;
        }
        cam.transform.LookAt(target);
        cam.orthographic = false;
        cam.nearClipPlane = .2f;
        cam.farClipPlane = 3300f;
        cam.clearFlags = CameraClearFlags.SolidColor;
        var tex = new RenderTexture(1600, 900, 24, RenderTextureFormat.ARGB32);
        Texture2D image = null;
        var previousTarget = cam.targetTexture;
        var previousActive = RenderTexture.active;
        try
        {
            tex.Create();
            cam.targetTexture = tex;
            var request = new UniversalRenderPipeline.SingleCameraRequest { destination = tex };
            Require(RenderPipeline.SupportsRenderRequest(cam, request), "URP_RENDER_REQUEST_UNSUPPORTED");
            RenderPipeline.SubmitRenderRequest(cam, request);
            RenderTexture.active = tex;
            image = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0,0,1600,900),0,0);
            image.Apply(false);
            var pixels = image.GetPixels32();
            int darkest = 765, brightest = 0, dark = 0, light = 0;
            foreach (var pixel in pixels)
            {
                int luminance = pixel.r + pixel.g + pixel.b;
                darkest = Math.Min(darkest, luminance);
                brightest = Math.Max(brightest, luminance);
                if (luminance < 15) dark++;
                if (luminance > 750) light++;
            }
            Require(brightest - darkest > 60 && dark < pixels.Length * .95f && light < pixels.Length * .95f,
                "FRAME_EMPTY_OR_CLIPPED: " + output);
            File.WriteAllBytes(output,image.EncodeToPNG());
            Require(new FileInfo(output).Length > 25000, "PNG appears empty: " + output);
            return new Shot
            {
                filename = Path.GetFileName(output),
                sha256 = Sha(output),
                bytes = new FileInfo(output).Length,
                osm_way = id,
                style = style,
                viewpoint = viewpoint
            };
        }
        finally
        {
            cam.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            tex.Release();
            UnityEngine.Object.DestroyImmediate(tex);
            if (image != null) UnityEngine.Object.DestroyImmediate(image);
        }
    }

    [MenuItem("Resort/R7/Capturar QA real da Unity")]
    public static void Run()
    {
        Require(SystemInfo.graphicsDeviceType != GraphicsDeviceType.Null, "REAL_GPU_REQUIRED: remove -nographics");
        Require(AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath)!=null,
            "R7 scene not generated; call ResortR7FacadeFinish.Build first");
        Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        Require(scene.isLoaded, "Cannot load R7 visual QA scene");
        Camera cam = Camera.main;
        Require(cam != null, "R7 scene has no tagged MainCamera");
        string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
        string folder=Path.Combine(repo,"build/R7_PBR_FacadeQA");
        string passPath=Path.Combine(folder,"material_pass.json");
        Require(File.Exists(passPath), "R7_MATERIAL_PASS_MISSING");
        var materialPass=JsonUtility.FromJson<MaterialPass>(File.ReadAllText(passPath));
        string derivedHash=Sha(Path.Combine(Application.dataPath,
            "Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx"));
        Require(materialPass!=null && materialPass.derived_fbx_sha256==derivedHash,
            "R7_MATERIAL_PASS_STALE: rebuild scene for this FBX");
        var cameraData=cam.GetComponent<UniversalAdditionalCameraData>();
        Require(cameraData!=null && cameraData.renderPostProcessing,"URP_POST_PROCESS_CAMERA_MISSING");
        var volumes=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<Volume>(true));
        Require(volumes.Any(v=>v.isGlobal && v.sharedProfile!=null &&
            v.sharedProfile.TryGet<Tonemapping>(out var tone) && tone.mode.overrideState && tone.mode.value==TonemappingMode.ACES &&
            v.sharedProfile.TryGet<ColorAdjustments>(out var exposure) && exposure.postExposure.overrideState),
            "R7_SAVED_EXPOSURE_TONEMAPPING_MISSING");
        var grouped = new Dictionary<string,Group>();
        int renderers=0,uvMissing=0,matsR7=0,invalidMaterials=0;
        foreach (var root in scene.GetRootGameObjects())
            foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                Match match=Find(renderer);
                if(match==null)
                {
                    foreach(var material in renderer.sharedMaterials)
                        Require(material!=null && material.shader!=null && material.shader.name=="Universal Render Pipeline/Lit",
                            "BACKGROUND_URP_LIT_MATERIAL_MISSING: "+renderer.name);
                    continue;
                }
                renderers++;
                string id=match.Groups["osm"].Value;
                Group group;
                if(!grouped.TryGetValue(id,out group))
                {
                    group = new Group
                    {
                        id=id,
                        style=match.Groups["style"].Value,
                        bounds=renderer.bounds,
                        parts=0
                    };
                    grouped.Add(id,group);
                }
                else group.bounds.Encapsulate(renderer.bounds);
                group.parts++;
                var filter = renderer.GetComponent<MeshFilter>();
                if(filter == null || filter.sharedMesh == null ||
                    !filter.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0))
                    uvMissing++;
                foreach(var material in renderer.sharedMaterials)
                    if(material!=null && material.name.StartsWith("R7_",StringComparison.Ordinal) &&
                        material.shader!=null && material.shader.name=="Universal Render Pipeline/Lit") matsR7++;
                    else invalidMaterials++;
            }
        Require(grouped.Count==50, "Native Unity R7 scene lost OSM buildings: "+grouped.Count);
        Require(renderers==materialPass.finished_renderers, "R7 saved scene renderer count changed: "+renderers);
        Require(matsR7>=300,"R7 URP/Lit materials not attached to expected meshes: "+matsR7);
        Require(uvMissing==0,"UV0_GATE_FAILED: "+uvMissing+" architectural renderers lack UV0");
        Require(invalidMaterials==0,"URP_LIT_MATERIAL_GATE_FAILED: "+invalidMaterials);
        Require(GraphicsSettings.currentRenderPipeline!=null &&
            GraphicsSettings.currentRenderPipeline.GetType().Name.Contains("UniversalRenderPipeline"),
            "URP_PIPELINE_GATE_FAILED: active URP asset required");
        Directory.CreateDirectory(folder);
        var shots=new List<Shot>();
        string[] families={"art_deco_carioca","residencial_orla","hotel_contemporaneo"};
        for (int i=0;i<families.Length;i++)
        {
            var family=families[i];
            var target=grouped.Values.Where(x=>x.style.Contains(family))
                .OrderBy(x=>x.bounds.center.sqrMagnitude).FirstOrDefault();
            Require(target!=null,"No matching OSM style "+family);
            string filename="R7_0"+(i+1)+"_"+family+"_RealUnity.png";
            shots.Add(Capture(cam,target.bounds,target.id,target.style,
                "OBLIQUE_45_REAL_UNITY",Path.Combine(folder,filename),false));
            if(i==0)
                shots.Add(Capture(cam,target.bounds,target.id,target.style,
                    "PEDESTRIAN_CAMERA_REAL_UNITY",
                    Path.Combine(folder,"R7_04_Pedestrian_RealUnity.png"),true));
        }
        var report=new Report
        {
            status="R7_NATIVE_UNITY_CAPTURE_COMPLETED_ART_GATE_PENDING",
            unity_version=Application.unityVersion,
            renderer=SystemInfo.graphicsDeviceType.ToString(),
            gpu=SystemInfo.graphicsDeviceName,
            shader_pipeline=GraphicsSettings.currentRenderPipeline==null?
                "BUILT_IN_STANDARD_FALLBACK":
                GraphicsSettings.currentRenderPipeline.GetType().Name,
            scene=ScenePath,
            recognized_buildings=grouped.Count,
            recognized_renderers=renderers,
            meshes_without_uv0=uvMissing,
            materials_using_r7=matsR7,
            derived_fbx_sha256=derivedHash,
            screenshots=shots.ToArray(),
            limitations="Native Unity GPU URP SubmitRenderRequest. Capture fails for missing UV0, wrong shader, null GPU or empty frames. ART NOT APPROVED until human visual review. No gameplay or FPS measurement."
        };
        File.WriteAllText(Path.Combine(folder,"R7_VisualNativeQA.json"),
            JsonUtility.ToJson(report,true)+"\n",Encoding.UTF8);
        Debug.Log("RESORT_R7_NATIVE_CAPTURE_PASS screenshotCount="+shots.Count+
            " buildings="+grouped.Count+" renderers="+renderers+
            " meshes_without_uv0="+uvMissing+" pipeline="+report.shader_pipeline);
    }
}
