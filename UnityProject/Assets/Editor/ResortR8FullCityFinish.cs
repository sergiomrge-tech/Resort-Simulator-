// R8: Replace every untextured background building with procedural 3D facades.
// Does not modify R7 FBX, original GIS, R7 QA scene, roads, or main gameplay.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;

public static class ResortR8FullCityFinish
{
    const string R7Scene = "Assets/Scenes/R7_Copacabana_50_Fachadas_PBR_VisualQA.unity";
    const string R8Scene = "Assets/Scenes/R8_Copacabana_1468_All_Facades.unity";
    const string NewFbx = "Assets/Architecture/R8_FullCity/R8_Remaining_1418_Textured_Facades.fbx";
    const string RoadAsset = "Assets/Architecture/R8_FullCity/R8_Original_Roads_Only.asset";
    const string Report = "Assets/Architecture/R8_FullCity/R8_FACADES_NATIVE_QA.json";
    const string BaseName = "GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS";
    static readonly Regex Named = new Regex(
        @"^R8_(?<style>cop_[a-z0-9_]+)__(?<part>wall|glass|stone|trim|roof|metal|shadow)(?:\.\d+)*$",
        RegexOptions.Compiled | RegexOptions.CultureInvariant);

    [Serializable] class R8Manifest
    {
        public string status;
        public string r8_fbx_sha256;
        public int r7_detailed_building_count;
        public int r8_background_building_count;
        public int full_city_total;
        public int style_count;
        public int fbx_meshes;
        public int windows_generated;
        public int geometry_faces;
        public int coast_length_m;
        public int inland_depth_m;
    }
    [Serializable] class R8UnityReport
    {
        public string status;
        public string unity_version;
        public string gpu;
        public string r8_fbx_sha256;
        public string scene;
        public int all_buildings;
        public int newly_detailed_buildings;
        public int prior_r7_detailed_buildings;
        public int recognized_r8_meshes;
        public int verified_road_triangles;
        public int windows_generated_blender;
        public int uv0_missing;
        public int wrong_shader_materials;
        public bool art_approved=false;
        public bool fps_measured=false;
    }
    static void Require(bool condition, string code)
    {
        if (!condition) throw new InvalidOperationException("RESORT_R8_BLOCKED: "+code);
    }
    static string Sha(string filename)
    {
        using (var fs=File.OpenRead(filename))
        using (var hasher=SHA256.Create())
            return BitConverter.ToString(hasher.ComputeHash(fs)).Replace("-","").ToLowerInvariant();
    }
    static Match NameOf(Transform current)
    {
        for (var t=current; t!=null; t=t.parent)
        {
            var match=Named.Match(t.name);
            if (match.Success) return match;
        }
        return Match.Empty;
    }
    [MenuItem("Resort/R8/Eliminar blocos sem fachadas (1468 prédios)")]
    public static void Build()
    {
        Require(AssetDatabase.LoadAssetAtPath<SceneAsset>(R7Scene)!=null,
            "R7_QA_SCENE_MISSING");
        Require(AssetDatabase.LoadAssetAtPath<GameObject>(NewFbx)!=null,
            "R8_REAL_BLENDER_FBX_MISSING");
        string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
        string reportPath=Path.Combine(Application.dataPath, Report.Substring("Assets/".Length));
        string fbxPath=Path.Combine(Application.dataPath, NewFbx.Substring("Assets/".Length));
        Require(File.Exists(reportPath) && File.Exists(fbxPath),"R8_FILES_NOT_MATERIALIZED");
        var manifest=JsonUtility.FromJson<R8Manifest>(File.ReadAllText(reportPath));
        Require(manifest!=null &&
            manifest.status=="R8_FULL_1418_FACADES_BLENDER_GENERATED_NOT_UNITY_APPROVED" &&
            manifest.r8_background_building_count==1418 && manifest.r7_detailed_building_count==50 &&
            manifest.full_city_total==1468 && manifest.style_count==50 &&
            manifest.fbx_meshes>250 && manifest.windows_generated>20000 &&
            manifest.coast_length_m==2000 && manifest.inland_depth_m==1000,
            "R8_MANIFEST_INVALID_OR_DIFFERENT_MAP");
        string fbxHash=Sha(fbxPath);
        Require(fbxHash==manifest.r8_fbx_sha256,"R8_FBX_HASH_MISMATCH");

        var importer=AssetImporter.GetAtPath(NewFbx) as ModelImporter;
        Require(importer!=null,"R8_IMPORTER_MISSING");
        if (!importer.isReadable)
        {
            importer.isReadable=true;
            importer.SaveAndReimport();
        }
        var scene=EditorSceneManager.OpenScene(R7Scene,OpenSceneMode.Single);
        Require(scene.isLoaded,"R7_SCENE_NOT_LOADABLE");
        // Original R7 detailed buildings are left untouched; GIS building
        // mass triangles alone disappear, preserving the exact original roads.
        var baseFilter=scene.GetRootGameObjects()
            .SelectMany(x=>x.GetComponentsInChildren<MeshFilter>(true))
            .Where(x=>x.gameObject.name.StartsWith(BaseName,StringComparison.Ordinal)).ToArray();
        Require(baseFilter.Length==1 && baseFilter[0].sharedMesh!=null,
            "SINGLE_SOURCE_GIS_BASE_NOT_FOUND");
        var baseMesh=baseFilter[0].sharedMesh;
        var baseRenderer=baseFilter[0].GetComponent<MeshRenderer>();
        Require(baseRenderer!=null,"BASE_RENDERER_MISSING");
        int roadSlot=-1, buildingSlot=-1;
        var originalMaterials=baseRenderer.sharedMaterials;
        Require(originalMaterials.Length==baseMesh.subMeshCount,"BASE_GIS_SUBMESH_SLOT_MISMATCH");
        for(int i=0;i<originalMaterials.Length;i++)
        {
            Require(originalMaterials[i]!=null,"BASE_MATERIAL_NULL");
            string name=originalMaterials[i].name;
            if(name.StartsWith("R7_OSM_Roads_",StringComparison.Ordinal)) roadSlot=i;
            if(name.StartsWith("R7_OSM_Other_Buildings_",StringComparison.Ordinal)) buildingSlot=i;
        }
        Require(roadSlot>=0 && buildingSlot>=0 && roadSlot!=buildingSlot,
            "ORIGINAL_ROAD_AND_BUILDING_CLASSES_NOT_DETECTED");
        var roads=baseMesh.GetTriangles(roadSlot);
        Require(roads.Length/3==3731 && baseMesh.GetTriangles(buildingSlot).Length>0,
            "STREET_PRESERVATION_TRIANGLE_GATE");
        var duplicate=UnityEngine.Object.Instantiate(baseMesh);
        duplicate.name="R8_Original_3731_Road_Faces";
        duplicate.subMeshCount=1;
        duplicate.SetTriangles(roads,0,true);
        var existing=AssetDatabase.LoadAssetAtPath<Mesh>(RoadAsset);
        if (existing!=null)
            Require(AssetDatabase.DeleteAsset(RoadAsset),"COULD_NOT_REFRESH_DERIVED_ROAD_ONLY_ASSET");
        AssetDatabase.CreateAsset(duplicate,RoadAsset);
        baseFilter[0].sharedMesh=duplicate;
        baseRenderer.sharedMaterials=new [] {originalMaterials[roadSlot]};
        var oldCollider=baseFilter[0].GetComponent<MeshCollider>();
        if(oldCollider!=null) oldCollider.sharedMesh=duplicate;

        var overlayPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(NewFbx);
        var overlay=PrefabUtility.InstantiatePrefab(overlayPrefab) as GameObject;
        Require(overlay!=null,"R8_OVERLAY_INSTANTIATE_FAILED");
        overlay.name="R8_ALL_1418_OSM_BUILDINGS_WITH_TEXTURED_FACADES";
        int count=0, badUv=0, badShader=0;
        var styles=new HashSet<string>();
        var rendererMeshes=overlay.GetComponentsInChildren<MeshRenderer>(true);
        foreach(var renderer in rendererMeshes)
        {
            var match=NameOf(renderer.transform);
            Require(match.Success,"UNKNOWN_R8_BACKGROUND_MESH:"+renderer.name);
            string style=match.Groups["style"].Value;
            string part=match.Groups["part"].Value;
            styles.Add(style);
            string finishPath="Assets/Materials/R7_Facades/R7_"+style+"_"+part+".mat";
            var finish=AssetDatabase.LoadAssetAtPath<Material>(finishPath);
            Require(finish!=null,"MISSING_REAL_URP_FINISH:"+finishPath);
            if(finish.shader==null || finish.shader.name!="Universal Render Pipeline/Lit")
                badShader++;
            var filter=renderer.GetComponent<MeshFilter>();
            if (filter==null || filter.sharedMesh==null ||
                !filter.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0) ||
                filter.sharedMesh.uv.Length!=filter.sharedMesh.vertexCount)
                badUv++;
            var slots=renderer.sharedMaterials;
            Require(slots.Length==1,"R8_SEMANTIC_SUBMESH_SLOT_LOST:"+renderer.name);
            renderer.sharedMaterials=new []{finish};
            count++;
        }
        Require(count==manifest.fbx_meshes && styles.Count==50,
            "R8_50_STYLES_OR_MESH_COUNT_MISMATCH");
        Require(badUv==0 && badShader==0,"R8_UV0_OR_PBR_GATE_FAILED");
        int detailed=scene.GetRootGameObjects()
            .SelectMany(x=>x.GetComponentsInChildren<MeshRenderer>(true))
            .Count(r=>r.name.StartsWith("R7B_",StringComparison.Ordinal));
        // FBX submeshes may be inside intermediate groups, so cross-check
        // detailed 50 source via 370 mesh renderers (not all child object names).
        var r7Count=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<MeshRenderer>(true))
            .Count(r=>r.transform.parent!=null &&
                (r.name.StartsWith("R7B_",StringComparison.Ordinal) ||
                 r.transform.parent.name.StartsWith("R7B_",StringComparison.Ordinal)));
        Require(r7Count>=300,"R7_DETAILED_ASSETS_LOST");
        Require(EditorSceneManager.SaveScene(scene,R8Scene,false),"R8_SCENE_SAVE_FAILED");
        AssetDatabase.SaveAssets();
        string folder=Path.Combine(repo,"build/R8_FULL_CITY_QA");
        Directory.CreateDirectory(folder);
        var result=new R8UnityReport{
            status="R8_UNITY_ALL_FACADES_URP_PASS_ART_PENDING",
            unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
            r8_fbx_sha256=fbxHash,scene=R8Scene,all_buildings=1468,
            newly_detailed_buildings=1418,prior_r7_detailed_buildings=50,
            recognized_r8_meshes=count,verified_road_triangles=roads.Length/3,
            windows_generated_blender=manifest.windows_generated,
            uv0_missing=badUv,wrong_shader_materials=badShader
        };
        File.WriteAllText(Path.Combine(folder,"R8_UnityNoBlankQA.json"),
            JsonUtility.ToJson(result,true)+"\n",Encoding.UTF8);
        Debug.Log("RESORT_R8_NO_BLANK_PASS buildings=1468 backgrounds=1418 "+
                  "renderers="+count+" styles="+styles.Count+
                  " roadTriangles="+(roads.Length/3)+" windows="+manifest.windows_generated);
    }
}
