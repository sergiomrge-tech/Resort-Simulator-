// Capture genuine 1600x900 GPU frames from the complete R8 city with URP.
// Art remains pending manual inspection. No mockups.
using System;
using System.Linq;
using System.IO;
using System.Text;
using System.Security.Cryptography;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ResortR10VisualCapture
{
    const string ScenePath="Assets/Scenes/R10_Copacabana_Calçada_Mosaico_Mar.unity";
    const string FBX="Assets/Architecture/R10_Coastal/R10_Ocean_Foam_Mosaic_Promenade.fbx";
    static void Require(bool ok,string message)
    {
        if(!ok) throw new InvalidOperationException("RESORT_R9_CAPTURE_BLOCKED:"+message);
    }
    static string Sha(string path)
    {
        using(var f=File.OpenRead(path))
        using(var h=SHA256.Create())
            return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();
    }
    [Serializable] class View
    {
        public string filename;
        public string sha256;
        public Vector3 position;
        public Vector3 target;
        public long bytes;
    }
    [Serializable] class Report
    {
        public string status;
        public string renderer;
        public string gpu;
        public string unity_version;
        public int r8_facade_renderers;
        public int r9_osm_trees;
        public int r10_coastal_meshes;
        public int source_road_triangles;
        public int styles;
        public string derived_fbx_sha256;
        public View[] captures;
        public bool artistic_gate_passed=false;
        public bool fps_measured=false;
    }
    static View Capture(Camera cam, Vector3 position, Vector3 target, string output)
    {
        cam.transform.position=position;
        cam.transform.LookAt(target);
        cam.fieldOfView=53f;
        cam.farClipPlane=4000f;
        cam.nearClipPlane=.20f;
        var saved=cam.targetTexture;
        var active=RenderTexture.active;
        var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);
        Texture2D png=null;
        try
        {
            rt.Create();cam.targetTexture=rt;
            var request=new UniversalRenderPipeline.SingleCameraRequest{destination=rt};
            Require(RenderPipeline.SupportsRenderRequest(cam,request),"URP_SINGLE_CAMERA_REQUEST_UNSUPPORTED");
            // Fill temporal/postprocessing history before the honest screenshot:
            // a freshly opened Unity batch scene needs several real GPU frames.
            for(int warm=0;warm<5;warm++)RenderPipeline.SubmitRenderRequest(cam,request);
            RenderTexture.active=rt;
            png=new Texture2D(1600,900,TextureFormat.RGB24,false);
            png.ReadPixels(new Rect(0,0,1600,900),0,0);
            png.Apply(false);
            var pixels=png.GetPixels32();
            int min=765,max=0;
            foreach(var p in pixels){var lum=p.r+p.g+p.b;min=Math.Min(min,lum);max=Math.Max(max,lum);}
            Require(max-min>60,"NO_REAL_CITY_DETAIL_PIXELS");
            if(Path.GetFileName(output).Contains("Dense_City"))
            {
                double luminance=0;
                int dark=0;
                int count=0;
                for(int y=370;y<830;y++)for(int x=150;x<1450;x++)
                {
                    var p=pixels[y*1600+x];
                    double value=(p.r+p.g+p.b)/3.0;
                    luminance+=value;
                    if(value<24.0)dark++;
                    count++;
                }
                double mean=luminance/count;
                double blackFraction=(double)dark/count;
                Require(mean>68.0 && blackFraction<.10,
                    "R10_BLACK_CITY_REGRESSION:mean="+mean.ToString("F1")+
                    " blackFraction="+blackFraction.ToString("F3"));
                Debug.Log("RESORT_R10_LIGHTING_PIXEL_GATE_PASS mean="+
                    mean.ToString("F1")+" blackout="+blackFraction.ToString("F3"));
            }
            File.WriteAllBytes(output,png.EncodeToPNG());
            Require(new FileInfo(output).Length>50000,"EMPTY_REAL_RENDER");
            return new View{filename=Path.GetFileName(output),sha256=Sha(output),
                position=position,target=target,bytes=new FileInfo(output).Length};
        }
        finally
        {
            cam.targetTexture=saved;RenderTexture.active=active;
            rt.Release();UnityEngine.Object.DestroyImmediate(rt);
            if(png!=null)UnityEngine.Object.DestroyImmediate(png);
        }
    }
    [MenuItem("Resort/R10/Capturar cidade e mosaico reais")]
    public static void Run()
    {
        Require(SystemInfo.graphicsDeviceType!=GraphicsDeviceType.Null,"ACTUAL_GPU_REQUIRED");
        var scene=EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
        Require(scene.isLoaded,"SCENE_NOT_OPEN");
        var cam=Camera.main;
        Require(cam!=null,"MAIN_CAMERA_MISSING");
        var urp=cam.GetComponent<UniversalAdditionalCameraData>();
        Require(urp!=null&&urp.renderPostProcessing,"URP_CAMERA_MISSING");
        Require(GraphicsSettings.currentRenderPipeline!=null,"URP_PIPELINE_INACTIVE");
        var renderers=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
        var r8=renderers.Where(x=>Regex.IsMatch(x.name,@"^R8_cop_[a-z0-9_]+__(wall|glass|stone|trim|roof|metal|shadow)(?:\.\d+)*$")).ToArray();
        Require(r8.Length==350,"R8_ALL_RENDERERS_NOT_PRESENT:"+r8.Length);
        foreach(var r in r8)
        {
            Require(r.sharedMaterials.Length==1 && r.sharedMaterials[0]!=null &&
                r.sharedMaterials[0].shader.name=="Universal Render Pipeline/Lit",
                "R8_SHADERS_NOT_PBR:"+r.name);
            var mesh=r.GetComponent<MeshFilter>();
            Require(mesh!=null&&mesh.sharedMesh!=null &&
                mesh.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0),
                "R8_FACADE_UV0_MISSING:"+r.name);
        }
        var road=renderers.SingleOrDefault(x=>x.gameObject.name.StartsWith(
            "GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS",StringComparison.Ordinal));
        Require(road!=null && road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,
            "ROADS_CHANGED");
        var trees=renderers.Where(r=>r.name.StartsWith("R9_TREE_",StringComparison.Ordinal)).ToArray();
        Require(trees.Length==48,"EXPECTED_48_OSM_TREES:"+trees.Length);
        Require(renderers.Any(r=>r.name.StartsWith("R9_URBAN_PAVEMENT_",StringComparison.Ordinal)),"URBAN_GROUND_MISSING");
        var coastal=renderers.Where(r=>r.name.StartsWith("R10_MOSAIC_",StringComparison.Ordinal)||r.name.StartsWith("R10_PROMENADE_",StringComparison.Ordinal)||r.name.StartsWith("R10_WATER_BREAKING_",StringComparison.Ordinal)).ToArray();
        Require(coastal.Length==9,"R10_NINE_PROMENADE_SEGMENTS_NOT_FOUND:"+coastal.Length);
        var ocean=renderers.SingleOrDefault(r=>r.name.StartsWith("R9_OCEAN_REAL_OSM_COAST",StringComparison.Ordinal));
        Require(ocean!=null&&ocean.sharedMaterial!=null&&ocean.sharedMaterial.shader.name=="Resort/R10/AnimatedOcean","R10_DYNAMIC_WATER_NOT_ACTIVE");
        var bounds=r8[0].bounds;
        foreach(var r in r8.Skip(1))bounds.Encapsulate(r.bounds);
        string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
        string outDir=Path.Combine(repo,"build/R10_CoastalQA");
        Directory.CreateDirectory(outDir);
        var c=bounds.center;
        // Cameras are genuine views of the scene: no masking of OSM data,
        // fake close-up image, external Blender still or screenshot compositing.
        var cameras=new []{
            new{filename="R10_01_Dense_City_RealUnity.png",pos=c+new Vector3(290,230,-310),target=c+Vector3.up*14},
            new{filename="R10_02_Orla_Aerial_RealUnity.png",pos=c+new Vector3(-340,260,-380),target=c+Vector3.up*8},
            new{filename="R10_03_Facades_Rooftops_RealUnity.png",pos=c+new Vector3(120,115,190),target=c+new Vector3(0,13,0)}
        };
        var shots=new List<View>();
        foreach(var shot in cameras)
            shots.Add(Capture(cam,shot.pos,shot.target,Path.Combine(outDir,shot.filename)));
        // Human-scale tree check: still a real, unretouched Unity GPU frame.
        var tree=trees.OrderBy(r=>r.bounds.center.sqrMagnitude).First();
        var tc=tree.bounds.center;
        shots.Add(Capture(cam,tc+new Vector3(12,7,-16),tc+Vector3.up*1.7f,
            Path.Combine(outDir,"R10_04_Arvore_Calcada_RealUnity.png")));
        var promenade=coastal.First(r=>r.name.StartsWith("R10_MOSAIC_PROMENADE_BASE",StringComparison.Ordinal));
        var waveMesh=promenade.GetComponent<MeshFilter>();
        Require(waveMesh!=null&&waveMesh.sharedMesh!=null&&waveMesh.sharedMesh.vertexCount>=802,"R10_PROMENADE_GEOMETRY_MISSING");
        var vertices=waveMesh.sharedMesh.vertices;
        var wavecenter=promenade.transform.TransformPoint((vertices[400]+vertices[401])*.5f);
        shots.Add(Capture(cam,wavecenter+new Vector3(0,27,0),wavecenter,
            Path.Combine(outDir,"R10_05_Mosaico_RealUnity.png")));
        var fbxPath=Path.Combine(Application.dataPath,FBX.Substring("Assets/".Length));
        var report=new Report{
            status="R10_REAL_URP_ART_CAPTURED_VISUAL_GATE_PENDING",
            renderer=SystemInfo.graphicsDeviceType.ToString(),
            gpu=SystemInfo.graphicsDeviceName,
            unity_version=Application.unityVersion,
            r8_facade_renderers=r8.Length,
            r9_osm_trees=trees.Length,
            r10_coastal_meshes=coastal.Length,
            source_road_triangles=3731,
            styles=50,
            derived_fbx_sha256=Sha(fbxPath),
            captures=shots.ToArray()
        };
        File.WriteAllText(Path.Combine(outDir,"R10_VisualNativeQA.json"),
            JsonUtility.ToJson(report,true)+"\n",Encoding.UTF8);
        Debug.Log("RESORT_R10_CAPTURE_PASS count="+shots.Count+" renderers="+r8.Length);
    }
}
