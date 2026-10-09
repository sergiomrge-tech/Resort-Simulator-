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

public static class ResortR12VisualCapture
{
    const string ScenePath="Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity";
    const string FBX="Assets/Architecture/R12_Storefronts/R12_StreetLevel_1418_Entrances_Storefronts.fbx";
    static void Require(bool ok,string message)
    {
        if(!ok) throw new InvalidOperationException("RESORT_R12_CAPTURE_BLOCKED:"+message);
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
        public int r11_detail_renderers;
        public int r12_street_renderers;
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
                Debug.Log("RESORT_R12_LIGHTING_PIXEL_GATE_PASS mean="+
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
    static bool FindDetailAnchor(MeshRenderer[] renderers,string part,out Vector3 point,out Vector3 outward)
    {
        point=Vector3.zero;
        outward=Vector3.forward;
        float best=float.MaxValue;
        foreach(var renderer in renderers.Where(r=>r.name.StartsWith("R11_cop_",StringComparison.Ordinal)
             && r.name.Contains("__"+part)))
        {
            var f=renderer.GetComponent<MeshFilter>();
            if(f==null||f.sharedMesh==null)continue;
            var m=f.sharedMesh;
            var vs=m.vertices;
            var triangles=m.triangles;
            for(int i=0;i+2<triangles.Length;i+=3)
            {
                Vector3 a=renderer.transform.TransformPoint(vs[triangles[i]]);
                Vector3 b=renderer.transform.TransformPoint(vs[triangles[i+1]]);
                Vector3 c=renderer.transform.TransformPoint(vs[triangles[i+2]]);
                Vector3 cross=Vector3.Cross(b-a,c-a);
                if(cross.magnitude<.14f)continue;
                Vector3 n=cross.normalized;
                if(Mathf.Abs(n.y)>.23f)continue;
                var p=(a+b+c)/3f;
                if(p.y<7f||p.y>65f||Mathf.Abs(p.x)>900f||Mathf.Abs(p.z)>900f)continue;
                // Stable camera near the map center, prefer faces with actual frontal area.
                float metric=new Vector2(p.x,p.z).sqrMagnitude+
                    Mathf.Abs(p.y-19f)*90f;
                if(metric>=best)continue;
                best=metric;
                point=p;
                outward=n;
            }
        }
        return best<float.MaxValue;
    }
    static bool FindShopSignAnchor(MeshRenderer[] shopMeshes,out Vector3 point,out Vector3 outward)
    {
        point=Vector3.zero;outward=Vector3.forward;
        float best=float.MaxValue;
        foreach(var renderer in shopMeshes.Where(r=>r.name.StartsWith("R12_sign_",StringComparison.Ordinal)))
        {
            var filter=renderer.GetComponent<MeshFilter>();
            if(filter==null||filter.sharedMesh==null)continue;
            var mesh=filter.sharedMesh;
            var vertices=mesh.vertices;
            var tris=mesh.triangles;
            for(int i=0;i+2<tris.Length;i+=6)
            {
                var a=renderer.transform.TransformPoint(vertices[tris[i]]);
                var b=renderer.transform.TransformPoint(vertices[tris[i+1]]);
                var c=renderer.transform.TransformPoint(vertices[tris[i+2]]);
                Vector3 n=Vector3.Cross(b-a,c-a);
                if(n.sqrMagnitude<.03f || Mathf.Abs(n.normalized.y)>.3f)continue;
                var mid=(a+b+c)/3f;
                if(mid.y<1.8f||mid.y>5f||Mathf.Abs(mid.x)>820||Mathf.Abs(mid.z)>820)continue;
                float cost=new Vector2(mid.x,mid.z).sqrMagnitude;
                if(cost>=best)continue;
                best=cost;point=mid;outward=n.normalized;
            }
        }
        return best<float.MaxValue;
    }
    [MenuItem("Resort/R12/Capturar vitrines e ruas reais")]
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
        var detail=renderers.Where(r=>r.name.StartsWith("R11_cop_",StringComparison.Ordinal)).ToArray();
        Require(detail.Length==210,"R11_REIMPORT_210_MESHES_MISSING:"+detail.Length);
        Require(detail.All(r=>r.sharedMaterial!=null&&r.sharedMaterial.shader.name=="Universal Render Pipeline/Lit"),
            "R11_BLANK_SHADERS_OR_MATERIALS");
        var shops=renderers.Where(r=>r.name.StartsWith("R12_",StringComparison.Ordinal)).ToArray();
        Require(shops.Length==19,"R12_SHOP_FRONT_END_MESH_COUNT_INVALID:"+shops.Length);
        Require(shops.All(r=>r.sharedMaterial!=null&&r.sharedMaterial.shader.name=="Universal Render Pipeline/Lit"),
            "R12_NO_TEXTURE_OR_SHADER");
        var bounds=r8[0].bounds;
        foreach(var r in r8.Skip(1))bounds.Encapsulate(r.bounds);
        string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
        string outDir=Path.Combine(repo,"build/R12_StreetQA");
        Directory.CreateDirectory(outDir);
        var c=bounds.center;
        // Cameras are genuine views of the scene: no masking of OSM data,
        // fake close-up image, external Blender still or screenshot compositing.
        var cameras=new []{
            new{filename="R12_01_Dense_City_RealUnity.png",pos=c+new Vector3(290,230,-310),target=c+Vector3.up*14},
            new{filename="R12_02_Orla_Aerial_RealUnity.png",pos=c+new Vector3(-340,260,-380),target=c+Vector3.up*8},
            new{filename="R12_03_Facades_Rooftops_RealUnity.png",pos=c+new Vector3(120,115,190),target=c+new Vector3(0,13,0)}
        };
        var shots=new List<View>();
        foreach(var shot in cameras)
            shots.Add(Capture(cam,shot.pos,shot.target,Path.Combine(outDir,shot.filename)));
        // Human-scale tree check: still a real, unretouched Unity GPU frame.
        var tree=trees.OrderBy(r=>r.bounds.center.sqrMagnitude).First();
        var tc=tree.bounds.center;
        shots.Add(Capture(cam,tc+new Vector3(12,7,-16),tc+Vector3.up*1.7f,
            Path.Combine(outDir,"R12_04_Arvore_Calcada_RealUnity.png")));
        var promenade=coastal.First(r=>r.name.StartsWith("R10_MOSAIC_PROMENADE_BASE",StringComparison.Ordinal));
        var waveMesh=promenade.GetComponent<MeshFilter>();
        Require(waveMesh!=null&&waveMesh.sharedMesh!=null&&waveMesh.sharedMesh.vertexCount>=802,"R10_PROMENADE_GEOMETRY_MISSING");
        var vertices=waveMesh.sharedMesh.vertices;
        var wavecenter=promenade.transform.TransformPoint((vertices[400]+vertices[401])*.5f);
        shots.Add(Capture(cam,wavecenter+new Vector3(0,27,0),wavecenter,
            Path.Combine(outDir,"R12_05_Mosaico_RealUnity.png")));
        Vector3 point,normal;
        Require(FindDetailAnchor(detail,"balcony_slabs",out point,out normal),"R11_BALCONY_3D_ANCHOR_NOT_FOUND");
        shots.Add(Capture(cam,point+normal*9f+Vector3.up*2.8f,point+Vector3.up*1.0f,
            Path.Combine(outDir,"R12_06_Varandas_RealUnity.png")));
        Require(FindDetailAnchor(detail,"roof_structures",out point,out normal),"R11_ROOFTOP_3D_ANCHOR_NOT_FOUND");
        shots.Add(Capture(cam,point+normal*12f+Vector3.up*6f,point+Vector3.up*0.8f,
            Path.Combine(outDir,"R12_07_Coberturas_RealUnity.png")));
        Vector3 sp,sn;
        Require(FindShopSignAnchor(shops,out sp,out sn),"R12_NO_REAL_GEOREFERENCED_SIGN_TO_CAPTURE");
        shots.Add(Capture(cam,sp+sn*11.0f+Vector3.up*.6f,sp-Vector3.up*.5f,
            Path.Combine(outDir,"R12_08_Fachada_Comercial_RealUnity.png")));
        shots.Add(Capture(cam,sp+sn*5.2f-Vector3.up*.35f,sp-Vector3.up*.9f,
            Path.Combine(outDir,"R12_09_Vitrine_Letreiro_RealUnity.png")));
        var fbxPath=Path.Combine(Application.dataPath,FBX.Substring("Assets/".Length));
        var report=new Report{
            status="R12_REAL_STREET_SHOPFRONTS_CAPTURED_ART_PENDING",
            renderer=SystemInfo.graphicsDeviceType.ToString(),
            gpu=SystemInfo.graphicsDeviceName,
            unity_version=Application.unityVersion,
            r8_facade_renderers=r8.Length,
            r9_osm_trees=trees.Length,
            r10_coastal_meshes=coastal.Length,
            r11_detail_renderers=detail.Length,
            r12_street_renderers=shops.Length,
            source_road_triangles=3731,
            styles=50,
            derived_fbx_sha256=Sha(fbxPath),
            captures=shots.ToArray()
        };
        File.WriteAllText(Path.Combine(outDir,"R12_VisualNativeQA.json"),
            JsonUtility.ToJson(report,true)+"\n",Encoding.UTF8);
        Debug.Log("RESORT_R12_CAPTURE_PASS count="+shots.Count+" streets="+shops.Length);
    }
}
