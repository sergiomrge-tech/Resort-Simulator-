// Project Resort R5: native Unity Editor validation of GIS-derived 50 buildings.
// No fabricated screenshots, no gaming implementation or playable EXE claim.
// Execute: Unity.exe -batchmode -quit -force-d3d11 -projectPath <UnityProject>
//   -executeMethod ResortR5UnityQA.Validate -logFile <path>
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

public static class ResortR5UnityQA
{
    private const string OriginalFbx =
        "Assets/ImportedBlender/Copacabana_Real_Blender.fbx";
    private const string DerivedFbx =
        "Assets/Architecture/R5_Pilot50/R5_Copacabana_50_Fachadas_Derivado.fbx";
    private const string ScenePath =
        "Assets/Scenes/R5_Copacabana_50_Predios_EditorQA.unity";

    [Serializable]
    private class Report
    {
        public string status;
        public string unity_version;
        public string renderer;
        public string derived_fbx_sha256;
        public string original_fbx_sha256;
        public string original_blend_sha256;
        public string scene;
        public string screenshot;
        public string screenshot_sha256;
        public string screenshot_status;
        public int original_mesh_count;
        public int derived_mesh_count;
        public int hero_renderers;
        public int distinct_replaced_osm_buildings;
        public long source_triangles;
        public long derived_triangles;
        public bool visual_approval;
        public bool fps_measured;
        public bool playable_exe_compiled;
        public string limitations;
    }

    private static void Assert(bool test,string message)
    {
        if (!test)throw new InvalidOperationException("RESORT_R5_NATIVE_QA_FAILED: "+message);
    }
    private static string Sha256(string file)
    {
        using (var hash=SHA256.Create())
        using (var f=File.OpenRead(file))
            return BitConverter.ToString(hash.ComputeHash(f)).Replace("-","").ToLowerInvariant();
    }
    private static Material Mat(string name,Color color,float metallic,float gloss)
    {
        const string dir="Assets/Materials/R5_Inspection";
        if (!AssetDatabase.IsValidFolder("Assets/Materials"))
            AssetDatabase.CreateFolder("Assets","Materials");
        if (!AssetDatabase.IsValidFolder(dir))
            AssetDatabase.CreateFolder("Assets/Materials","R5_Inspection");
        string path=dir+"/"+name+".mat";
        Material m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if (m==null)
        {
            Shader shader=Shader.Find("Universal Render Pipeline/Lit");
            if (shader==null || GraphicsSettings.currentRenderPipeline==null)
                shader=Shader.Find("Standard");
            Assert(shader!=null,"No Unity URP/Standard shader");
            m=new Material(shader);
            m.name=name;
            AssetDatabase.CreateAsset(m,path);
        }
        if(m.HasProperty("_BaseColor"))m.SetColor("_BaseColor",color);
        if(m.HasProperty("_Color"))m.SetColor("_Color",color);
        if(m.HasProperty("_Metallic"))m.SetFloat("_Metallic",metallic);
        if(m.HasProperty("_Smoothness"))m.SetFloat("_Smoothness",gloss);
        if(m.HasProperty("_Glossiness"))m.SetFloat("_Glossiness",gloss);
        EditorUtility.SetDirty(m);
        return m;
    }
    private static string FindId(Renderer renderer)
    {
        Transform tr=renderer.transform;
        while (tr!=null)
        {
            string n=tr.gameObject.name;
            int start=n.IndexOf("R5_REPLACED_way_",StringComparison.Ordinal);
            if(start>=0)
            {
                start+="R5_REPLACED_way_".Length;
                int end=n.IndexOf("__",start,StringComparison.Ordinal);
                if(end>start)return n.Substring(start,end-start);
            }
            tr=tr.parent;
        }
        return null;
    }
    private static long Triangles(MeshFilter[] filters)
    {
        long n=0;
        foreach(var f in filters)
            if(f.sharedMesh!=null)
                n+=f.sharedMesh.triangles.Length/3;
        return n;
    }
    public static void Validate()
    {
        string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
        string modelPath=Path.Combine(Application.dataPath,
            "Architecture/R5_Pilot50/R5_Copacabana_50_Fachadas_Derivado.fbx");
        string originalPath=Path.Combine(Application.dataPath,
            "ImportedBlender/Copacabana_Real_Blender.fbx");
        string blendPath=Path.Combine(repo,"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend");
        string qa=Path.Combine(repo,"build","R5_UnityNativeQA");
        Directory.CreateDirectory(qa);
        Assert(File.Exists(modelPath),"R5 integrated city FBX missing");
        Assert(File.Exists(originalPath),"original city FBX missing");
        Assert(File.Exists(blendPath),"original Blender GIS file missing");
        var report=new Report();
        report.status="NATIVE_UNITY_EDITOR_IMPORT_IN_PROGRESS";
        report.unity_version=Application.unityVersion;
        report.original_fbx_sha256=Sha256(originalPath);
        report.original_blend_sha256=Sha256(blendPath);
        report.derived_fbx_sha256=Sha256(modelPath);
        report.renderer=SystemInfo.graphicsDeviceType.ToString();
        report.visual_approval=false;
        report.fps_measured=false;
        report.playable_exe_compiled=false;
        report.limitations="Native Unity Editor import/render only, not a full playable scene, artistic approval or FPS benchmark.";

        Debug.Log("R5_NATIVE_UNITY_START graphics="+report.renderer+" hash="+report.derived_fbx_sha256);
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var source=AssetDatabase.LoadAssetAtPath<GameObject>(OriginalFbx);
        var derivative=AssetDatabase.LoadAssetAtPath<GameObject>(DerivedFbx);
        Assert(source!=null && derivative!=null,"Imported FBX models not visible in Unity");
        var sourceMesh=source.GetComponentsInChildren<MeshFilter>(true);
        var derivedMesh=derivative.GetComponentsInChildren<MeshFilter>(true);
        report.original_mesh_count=sourceMesh.Length;
        report.derived_mesh_count=derivedMesh.Length;
        report.source_triangles=Triangles(sourceMesh);
        report.derived_triangles=Triangles(derivedMesh);
        Assert(report.source_triangles>=26764,"Original GIS city malformed");
        Assert(report.derived_triangles>300000,"Derived OSM city lost procedural architecture");
        Debug.Log("R5_NATIVE_MESHES source="+report.source_triangles+
                  " derived="+report.derived_triangles+
                  " modelMeshes="+report.derived_mesh_count);

        Scene scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        var world=PrefabUtility.InstantiatePrefab(derivative) as GameObject;
        Assert(world!=null,"Unity could not instantiate actual R5 FBX");
        world.name="R5 Copacabana - 50 OSM buildings reauthored (technical QA)";
        var renderers=world.GetComponentsInChildren<Renderer>(true);
        Assert(renderers.Length>150,"50 architectural assets not included");
        var heroes=renderers.Where(x=>FindId(x)!=null).ToArray();
        var ids=new HashSet<string>(
            heroes.Select(FindId).Where(x=>!string.IsNullOrEmpty(x)));
        report.hero_renderers=heroes.Length;
        report.distinct_replaced_osm_buildings=ids.Count;
        Debug.Log("R5_NATIVE_IMPORTED_IDS "+ids.Count+" hero renderers="+heroes.Length);
        Assert(ids.Count==50,"Expected exactly 50 unique reauthored OSM IDs; found "+ids.Count);
        Assert(heroes.Length>=200,"Expected detailed architectural submeshes");

        var mapRoad=Mat("R5_Road_QA",new Color(.25f,.27f,.29f),.02f,.12f);
        var mapBuilding=Mat("R5_Old_Buildings_QA",new Color(.74f,.70f,.64f),0,.27f);
        var wall=Mat("R5_Facade_QA",new Color(.85f,.80f,.70f),0,.44f);
        var stone=Mat("R5_Facade_Stone_QA",new Color(.69f,.65f,.57f),0,.3f);
        var glass=Mat("R5_Architectural_Glass_QA",new Color(.14f,.27f,.32f),.14f,.86f);
        var metal=Mat("R5_Architectural_Metal_QA",new Color(.27f,.28f,.28f),.68f,.62f);
        var plants=Mat("R5_Planters_QA",new Color(.19f,.31f,.16f),0,.22f);
        foreach(var ren in renderers)
        {
            var mats=ren.sharedMaterials;
            bool oldMap=FindId(ren)==null;
            for(int i=0;i<mats.Length;i++)
            {
                string name=mats[i]!=null?mats[i].name.ToLowerInvariant():"";
                mats[i]=oldMap?(name.Contains("road")?mapRoad:mapBuilding):
                        name.Contains("glass")?glass:
                        name.Contains("metal")?metal:
                        name.Contains("plant")?plants:
                        name.Contains("stone")||name.Contains("roof")?stone:wall;
            }
            ren.sharedMaterials=mats;
        }
        var sunObj=new GameObject("R5 Unity QA Daylight");
        var sun=sunObj.AddComponent<Light>();
        sun.type=LightType.Directional;
        sun.intensity=1.55f;
        sunObj.transform.rotation=Quaternion.Euler(48f,-25f,0);
        RenderSettings.ambientMode=AmbientMode.Flat;
        RenderSettings.ambientLight=new Color(.60f,.68f,.74f);
        var cameraObj=new GameObject("R5 Native Unity Camera");
        cameraObj.tag="MainCamera";
        var cam=cameraObj.AddComponent<Camera>();
        cam.orthographic=true;
        cam.orthographicSize=72f;
        cam.nearClipPlane=.1f;
        cam.farClipPlane=4200f;
        cam.backgroundColor=new Color(.62f,.72f,.84f);
        cam.clearFlags=CameraClearFlags.Skybox;
        var close=heroes.OrderBy(x=>new Vector2(x.bounds.center.x,x.bounds.center.z).sqrMagnitude).First();
        Vector3 aim=close.bounds.center;
        aim.y=Mathf.Max(10f,aim.y*.5f);
        cameraObj.transform.position=aim+new Vector3(50,98,-90);
        cameraObj.transform.LookAt(aim);

        if(!AssetDatabase.IsValidFolder("Assets/Scenes"))
            AssetDatabase.CreateFolder("Assets","Scenes");
        Assert(EditorSceneManager.SaveScene(scene,ScenePath),"QA scene could not be saved");
        report.scene=ScenePath;
        string screenshot=Path.Combine(qa,"R5_50_Fachadas_Real_Unity_Camera_QA.png");
        report.screenshot_status="NOT_RENDERED";
        RenderTexture tex=null;
        Texture2D image=null;
        try
        {
            tex=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);
            tex.Create();
            cam.targetTexture=tex;
            cam.Render();
            RenderTexture.active=tex;
            image=new Texture2D(1600,900,TextureFormat.RGB24,false);
            image.ReadPixels(new Rect(0,0,1600,900),0,0);
            image.Apply(false);
            File.WriteAllBytes(screenshot,image.EncodeToPNG());
            Assert(new FileInfo(screenshot).Length>45000,
                "Native Unity screenshot too small to be meaningful");
            report.screenshot_status="GENUINE_UNITY_CAMERA_RENDER";
            report.screenshot="build/R5_UnityNativeQA/R5_50_Fachadas_Real_Unity_Camera_QA.png";
            report.screenshot_sha256=Sha256(screenshot);
        }
        catch(Exception e)
        {
            Debug.LogWarning("R5_UNITY_RENDER_FAILED: "+e);
        }
        finally
        {
            cam.targetTexture=null;
            RenderTexture.active=null;
            if(tex!=null){tex.Release();UnityEngine.Object.DestroyImmediate(tex);}
            if(image!=null)UnityEngine.Object.DestroyImmediate(image);
        }
        Assert(report.original_fbx_sha256==Sha256(originalPath),
            "Source original FBX was modified");
        Assert(report.original_blend_sha256==Sha256(blendPath),
            "Source original BlenderGIS was modified");
        report.status="NATIVE_UNITY_EDITOR_IMPORTED_AND_SCENE_SAVED";
        File.WriteAllText(Path.Combine(qa,"R5_Unity_Editor_QA.json"),
            JsonUtility.ToJson(report,true)+"\n",Encoding.UTF8);
        AssetDatabase.SaveAssets();
        Debug.Log("R5_NATIVE_UNITY_EDITOR_QA_PASS count="+ids.Count+
                  " render="+report.screenshot_status+" triangles="+report.derived_triangles);
    }
}
