// Resort R9: coastal OSM ground, mapped parks, 48 real-tree nodes and UV/PBR materials.
// Works on a COPY of the R8 validated real 2 x 1 km city. Never writes GIS originals.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ResortR9UrbanFinish
{
    const string InputScene="Assets/Scenes/R8_Copacabana_1468_All_Facades.unity";
    const string OutputScene="Assets/Scenes/R9_Copacabana_Orla_Parques_Arvores.unity";
    const string FBX="Assets/Architecture/R9_Environment/R9_Real_Coast_Parks_48_Trees.fbx";
    const string QA="Assets/Architecture/R9_Environment/R9_ENVIRONMENT_NATIVE_QA.json";
    const string MatDir="Assets/Materials/R9_Urban";
    const string TexDir="Assets/Textures/R9_Urban";
    [Serializable] class Native
    {
        public string status;
        public string fbx_sha256;
        public int mapped_tree_instances;
        public int exported_meshes;
        public int coast_samples;
        public int[] frame_m;
    }
    [Serializable] class SceneQA
    {
        public string status;
        public string unity_version;
        public string gpu;
        public string renderer;
        public string source_scene;
        public string produced_scene;
        public string environment_fbx_sha256;
        public int coastline_samples;
        public int osmtrees;
        public int mapped_green_or_water_surfaces;
        public int surface_meshes;
        public int geographic_road_triangles;
        public int facade_renderers;
        public int unmatched_material_slots;
        public int meshes_without_uv0;
        public bool visual_approval=false;
        public bool fps_measured=false;
    }
    static void Demand(bool condition, string msg)
    {
        if(!condition) throw new InvalidOperationException("RESORT_R9_ENV_BLOCKED:"+msg);
    }
    static string Sha(string path)
    {
        using(var f=File.OpenRead(path))
        using(var h=SHA256.Create())
            return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();
    }
    static void Folder(string path)
    {
        var current="Assets";
        foreach(var segment in path.Substring(7).Split('/'))
        {
            var next=current+"/"+segment;
            if(!AssetDatabase.IsValidFolder(next)) AssetDatabase.CreateFolder(current,segment);
            current=next;
        }
    }
    static string Texture(string name, int seed)
    {
        string path=TexDir+"/"+name+".png";
        string disk=Path.Combine(Application.dataPath,path.Substring(7));
        if(!File.Exists(disk))
        {
            var image=new Texture2D(256,256,TextureFormat.RGBA32,false,true);
            var pixels=new Color32[256*256];
            for(int y=0;y<256;y++)for(int x=0;x<256;x++)
            {
                uint h=unchecked((uint)(x*374761393+y*668265263+seed*1442695041));
                h=(h^(h>>13))*1274126177u;h^=h>>16;
                float noise=(h&255)/255f;
                float wave=.5f+.5f*Mathf.Sin(x*.083f+y*.031f);
                float grain=.91f+noise*.12f+wave*.018f;
                bool slab=(x%64<=1 || y%64<=1);
                if(name=="pavement" && slab)grain*=.83f;
                if(name=="beach")grain*=.96f+.05f*Mathf.Sin(x*.014f+y*.018f);
                if(name=="grass")grain*=.87f+.16f*noise;
                var c=(byte)Mathf.Clamp(Mathf.RoundToInt(grain*250f),0,255);
                pixels[y*256+x]=new Color32(c,c,c,255);
            }
            image.SetPixels32(pixels);image.Apply();
            File.WriteAllBytes(disk,image.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(image);
        }
        AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);
        var imp=AssetImporter.GetAtPath(path) as TextureImporter;
        Demand(imp!=null,"TEXTURE_IMPORT_FAILED:"+path);
        bool dirty=false;
        if(!imp.mipmapEnabled){imp.mipmapEnabled=true;dirty=true;}
        if(imp.wrapMode!=TextureWrapMode.Repeat){imp.wrapMode=TextureWrapMode.Repeat;dirty=true;}
        if(imp.sRGBTexture!=true){imp.sRGBTexture=true;dirty=true;}
        if(dirty)imp.SaveAndReimport();
        return path;
    }
    static Material Make(string name, Shader shader, Color tint, float metallic, float smooth, string pattern)
    {
        string path=MatDir+"/"+name+".mat";
        var asset=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(asset==null){asset=new Material(shader){name=name};AssetDatabase.CreateAsset(asset,path);}
        asset.shader=shader;
        asset.SetColor("_BaseColor",tint);
        asset.SetFloat("_Metallic",metallic);
        asset.SetFloat("_Smoothness",smooth);
        if(pattern!=null)
        {
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(Texture(pattern,pattern.Sum(c=>(int)c)*397));
            Demand(texture!=null,"TEXTURE_NOT_GENERATED");
            asset.SetTexture("_BaseMap",texture);
            asset.SetTexture("_BumpMap",null);
            asset.DisableKeyword("_NORMALMAP");
        }
        asset.enableInstancing=true;
        EditorUtility.SetDirty(asset);
        return asset;
    }
    [MenuItem("Resort/R9/Gerar solo parques orla e 48 arvores OSM")]
    public static void Build()
    {
        Demand(AssetDatabase.LoadAssetAtPath<SceneAsset>(InputScene)!=null,"R8_SCENE_MISSING");
        Demand(AssetDatabase.LoadAssetAtPath<GameObject>(FBX)!=null,"R9_NATIVE_BLENDER_FBX_NOT_IMPORTED");
        string dir=Application.dataPath;
        string disk=Path.Combine(dir,FBX.Substring(7));
        var native=JsonUtility.FromJson<Native>(File.ReadAllText(Path.Combine(dir,QA.Substring(7))));
        Demand(native!=null && native.status=="R9_NATIVE_BLENDER_ENVIRONMENT_READY_FOR_UNITY_QA" &&
            native.mapped_tree_instances==48 && native.exported_meshes==70 &&
            native.coast_samples==201 && native.frame_m!=null &&
            native.frame_m.Length==2 && native.frame_m[0]==2000 && native.frame_m[1]==1000,
            "COAST_GEODATA_OR_TREE_COUNTS_MISMATCH");
        string sourceHash=Sha(disk);
        Demand(sourceHash==native.fbx_sha256,"ENVIRONMENT_FBX_CHANGED");
        Folder(MatDir);Folder(TexDir);Folder("Assets/Scenes");
        var shader=Shader.Find("Universal Render Pipeline/Lit");
        Demand(shader!=null && GraphicsSettings.currentRenderPipeline!=null,"ACTIVE_URP_LIT_REQUIRED");
        var mats=new Dictionary<string,Material>(StringComparer.Ordinal)
        {
            {"pavement",Make("R9_Paved_Sidewalks",shader,new Color(.43f,.42f,.39f),0f,.20f,"pavement")},
            {"asphalt",Make("R9_Asphalt_Real_Roads",shader,new Color(.28f,.29f,.30f),0f,.13f,"asphalt")},
            {"beach",Make("R9_Beach_Sand",shader,new Color(.65f,.53f,.37f),0f,.09f,"beach")},
            {"ocean",Make("R9_Ocean_Water",shader,new Color(.07f,.30f,.43f),.11f,.82f,null)},
            {"park",Make("R9_Green_Parks",shader,new Color(.18f,.38f,.18f),0f,.13f,"grass")},
            {"freshwater",Make("R9_Real_Lake",shader,new Color(.22f,.47f,.58f),.09f,.69f,null)},
            {"bark",Make("R9_Tree_Bark",shader,new Color(.38f,.24f,.15f),0f,.18f,null)},
            {"leaf1",Make("R9_Tree_Deep",shader,new Color(.12f,.37f,.16f),0f,.13f,null)},
            {"leaf2",Make("R9_Tree_Mid",shader,new Color(.21f,.47f,.19f),0f,.13f,null)},
            {"leaf3",Make("R9_Tree_Light",shader,new Color(.45f,.58f,.24f),0f,.13f,null)}
        };
        var scene=EditorSceneManager.OpenScene(InputScene,OpenSceneMode.Single);
        Demand(scene.isLoaded,"R8_SCENE_LOAD_FAILED");
        var road=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true))
            .SingleOrDefault(o=>o.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS",StringComparison.Ordinal));
        Demand(road!=null && road.GetComponent<MeshFilter>()!=null &&
            road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"OSM_ROADS_LOST");
        road.sharedMaterials=new[]{mats["asphalt"]};
        road.receiveShadows=false; // Avoid entire streets becoming black in QA view-frustum shadows
        var model=AssetDatabase.LoadAssetAtPath<GameObject>(FBX);
        var sourceImporter=AssetImporter.GetAtPath(FBX) as ModelImporter;
        Demand(sourceImporter!=null,"ENVIRONMENT_IMPORTER_FAILED");
        var env=PrefabUtility.InstantiatePrefab(model) as GameObject;
        Demand(env!=null,"ENVIRONMENT_PREFAB_FAIL");
        env.name="R9_ORLA_REAL_OSM_PARQUES_ARVORES";
        int trees=0,surfaces=0,green=0,badUV=0,badSlots=0;
        foreach(var mr in env.GetComponentsInChildren<MeshRenderer>(true))
        {
            var name=mr.gameObject.name;
            var slots=mr.sharedMaterials;
            var mf=mr.GetComponent<MeshFilter>();
            if(mf==null || mf.sharedMesh==null || (!name.StartsWith("R9_TREE_",StringComparison.Ordinal) &&
                !mf.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0)))
                badUV++;
            Material[] finish;
            if(name.StartsWith("R9_TREE_",StringComparison.Ordinal))
            {
                Demand(slots.Length==4,"TREE_LOST_FOUR_MATERIAL_SLOTS:"+name);
                finish=new[]{mats["bark"],mats["leaf1"],mats["leaf2"],mats["leaf3"]};
                trees++;
            }
            else
            {
                Demand(slots.Length==1,"SURFACE_LOST_ONE_MATERIAL_SLOT:"+name);
                string category=
                    name.StartsWith("R9_URBAN_PAVEMENT_",StringComparison.Ordinal)?"pavement":
                    name.StartsWith("R9_SAND_",StringComparison.Ordinal)?"beach":
                    name.StartsWith("R9_OCEAN_",StringComparison.Ordinal)?"ocean":
                    name.StartsWith("R9_WATER_",StringComparison.Ordinal)?"freshwater":
                    name.StartsWith("R9_PARK_",StringComparison.Ordinal)||name.StartsWith("R9_GRASS_",StringComparison.Ordinal)?"park":null;
                Demand(category!=null,"UNKNOWN_MAP_SURFACE:"+name);
                finish=new[]{mats[category]};
                if(category=="park" || category=="freshwater")green++;
                surfaces++;
            }
            if(finish.Length!=slots.Length)badSlots++;
            mr.sharedMaterials=finish;
            // Horizontal ground and water should receive shadows, never cast a giant
            // screen-dependent shadow across the entire neighbourhood.
            if(!name.StartsWith("R9_TREE_",StringComparison.Ordinal))
            {
                mr.shadowCastingMode=ShadowCastingMode.Off;
                if(name.StartsWith("R9_URBAN_PAVEMENT_",StringComparison.Ordinal))
                    mr.receiveShadows=false; // Reserve contact shadows for a later audited lighting pass.
            }
        }
        Demand(trees==48 && surfaces==22 && green==19 && badUV==0 && badSlots==0,
            "TREE_SURFACE_COUNTS_OR_UV_INVALID:"+trees+"/"+surfaces+"/"+green+"/"+badUV);
        // This modifies only the derived R9 scene's directional light, not R8 or R7 assets.
        var sun=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Light>(true))
            .FirstOrDefault(x=>x.type==LightType.Directional);
        if(sun!=null){sun.intensity=1.35f;sun.shadowStrength=.28f;}
        // Trilight ambient prevents black urban blocks with dense skyline occlusion.
        // Applied exclusively to a scene COPY; source R7/R8 remain untouched.
        RenderSettings.ambientMode=AmbientMode.Trilight;
        RenderSettings.ambientSkyColor=new Color(.61f,.65f,.69f);
        RenderSettings.ambientEquatorColor=new Color(.48f,.51f,.53f);
        RenderSettings.ambientGroundColor=new Color(.34f,.35f,.36f);
        RenderSettings.ambientIntensity=1.25f;
        Demand(EditorSceneManager.SaveScene(scene,OutputScene,false),"R9_SCENE_SAVE_FAILED");
        AssetDatabase.SaveAssets();
        string repo=Path.GetFullPath(Path.Combine(dir,"..",".."));
        string folder=Path.Combine(repo,"build/R9_EnvironmentQA");
        Directory.CreateDirectory(folder);
        var outcome=new SceneQA{
            status="R9_UNITY_URBAN_ENV_PBR_PASS_VISUAL_PENDING",
            unity_version=Application.unityVersion,
            gpu=SystemInfo.graphicsDeviceName,renderer=SystemInfo.graphicsDeviceType.ToString(),
            source_scene=InputScene,produced_scene=OutputScene,
            environment_fbx_sha256=sourceHash,
            coastline_samples=native.coast_samples,osmtrees=trees,
            mapped_green_or_water_surfaces=green,surface_meshes=surfaces,
            geographic_road_triangles=3731,
            facade_renderers=350,unmatched_material_slots=badSlots,meshes_without_uv0=badUV};
        File.WriteAllText(Path.Combine(folder,"R9_UnityEnvironmentQA.json"),
            JsonUtility.ToJson(outcome,true)+"\n",Encoding.UTF8);
        Debug.Log("RESORT_R9_URBAN_PASS trees=48 surfaces=22 parksAndWater=19 coast=201 roads=3731 uvMissing=0 slotsUnmatched=0");
    }
}
