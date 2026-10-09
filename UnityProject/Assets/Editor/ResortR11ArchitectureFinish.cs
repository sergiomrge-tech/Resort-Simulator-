// R11: integrate validated native Blender volumetry without changing GIS or R10.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;

public static class ResortR11ArchitectureFinish {
 const string FBX="Assets/Architecture/R11_Architecture/R11_Real_Facade_Volumetry_1418.fbx";
 const string QA="Assets/Architecture/R11_Architecture/R11_ARCHITECTURE_NATIVE_QA.json";
 const string Output="Assets/Scenes/R11_Copacabana_Arquitetura_Volumetrica.unity";
 static readonly Regex Name=new Regex(
   @"^R11_(?<style>cop_[a-z0-9_]+)__(?<part>balcony_slabs|glass_balustrades|metal_railings|cornices|roof_structures|service_units)(?:\.\d+)*$",
   RegexOptions.Compiled|RegexOptions.CultureInvariant);
 [Serializable] class Manifest {
   public string status;
   public string fbx_sha256;
   public int map_length_coast_m,map_inland_width_m;
   public int real_osm_buildings_from_r8,original_r7_detailed,full_city_total,style_count;
   public int meshes,faces,balconies,roof_units,service_units,cornices,balcony_buildings;
 }
 [Serializable] class Report {
   public string status,unity_version,gpu,renderer,input_scene,output_scene,fbx_sha256;
   public int all_buildings,old_road_triangles,vegetation_osm_count,architecture_renderers,architecture_styles,shaders_invalid,uv0_missing;
   public int balconied_buildings,balconies,rooftop_units,cornices;
   public bool visual_gate_approved=false;
   public bool fps_measured=false;
 }
 static void Require(bool good,string why){
   if(!good)throw new InvalidOperationException("RESORT_R11_BLOCKED:"+why);
 }
 static string SourceScene(){
   var scenes=AssetDatabase.FindAssets("R10_Copacabana t:Scene",new[]{"Assets/Scenes"})
     .Select(AssetDatabase.GUIDToAssetPath)
     .Where(x=>Path.GetFileName(x).StartsWith("R10_Copacabana_",StringComparison.Ordinal))
     .ToArray();
   Require(scenes.Length==1,"EXPECTED_SINGLE_R10_GEOGRAPHIC_SCENE");
   return scenes[0];
 }
 static string Sha(string path){
   using(var fs=File.OpenRead(path))using(var h=SHA256.Create())
     return BitConverter.ToString(h.ComputeHash(fs)).Replace("-","").ToLowerInvariant();
 }
 static Material MaterialFor(string style,string part){
   string path;
   switch(part){
    case "balcony_slabs":path="Assets/Materials/R10_Facades/R10_"+style+"__wall.mat";break;
    case "glass_balustrades":path="Assets/Materials/R10_Facades/R10_"+style+"__glass.mat";break;
    case "metal_railings":case "service_units":
      path="Assets/Materials/R7_Facades/R7_"+style+"_metal.mat";break;
    case "cornices":
      path="Assets/Materials/R7_Facades/R7_"+style+"_trim.mat";break;
    case "roof_structures":
      path="Assets/Materials/R10_Facades/R10_"+style+"__roof.mat";break;
    default:throw new InvalidOperationException("MISSING_R11_PART_MATERIAL_"+part);
   }
   var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
   Require(mat!=null && mat.shader!=null &&
     mat.shader.name=="Universal Render Pipeline/Lit","MISSING_R11_REAL_PBR_MATERIAL:"+path);
   return mat;
 }
 [MenuItem("Resort/R11/Instalar arquitetura real volumetrica nos 1418 predios")]
 public static void Build(){
   string baseScene=SourceScene();
   Require(AssetDatabase.LoadAssetAtPath<GameObject>(FBX)!=null,"FBX_NOT_GENERATED_IN_NATIVE_BLENDER");
   string file=Path.Combine(Application.dataPath,FBX.Substring(7));
   string qaFile=Path.Combine(Application.dataPath,QA.Substring(7));
   Require(File.Exists(file) && File.Exists(qaFile),"R11_ASSETS_NOT_MATERIALIZED");
   var manifest=JsonUtility.FromJson<Manifest>(File.ReadAllText(qaFile));
   Require(manifest!=null && manifest.status=="R11_GEOMETRY_NATIVE_BLENDER_PASS_UNITY_PENDING" &&
     manifest.map_length_coast_m==2000 && manifest.map_inland_width_m==1000 &&
     manifest.real_osm_buildings_from_r8==1418 && manifest.original_r7_detailed==50 &&
     manifest.full_city_total==1468 && manifest.style_count==50 &&
     manifest.balconies>=4000 && manifest.roof_units>1000 &&
     manifest.meshes>150 && manifest.faces>100000,"R11_GEOGRAPHY_OR_GEOMETRY_MISMATCH");
   string sha=Sha(file);
   Require(sha==manifest.fbx_sha256,"R11_FBX_HAS_CHANGED_SINCE_BLENDER_QA");
   var scene=EditorSceneManager.OpenScene(baseScene,OpenSceneMode.Single);
   Require(scene.isLoaded,"R10_SCENE_LOAD_FAIL");
   var baseline=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
   var roads=baseline.SingleOrDefault(r=>r.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS",StringComparison.Ordinal));
   Require(roads!=null && roads.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,
     "REAL_GIS_ROADS_REGRESSION");
   Require(baseline.Count(r=>r.name.StartsWith("R9_TREE_",StringComparison.Ordinal))==48,
     "EXISTING_TREES_CHANGED");
   Require(baseline.Count(r=>r.name.StartsWith("R8_cop_",StringComparison.Ordinal))==350,
     "R8_DERIVED_ARCHITECTURE_LOST");
   var model=AssetDatabase.LoadAssetAtPath<GameObject>(FBX);
   var root=PrefabUtility.InstantiatePrefab(model) as GameObject;
   Require(root!=null,"COULD_NOT_LOAD_NATIVE_R11_FBX");
   root.name="R11_3D_BALCONIES_CORNICES_ROOFTOPS_OSM_1418";
   int count=0,missingUV=0,badShader=0;
   var styles=new HashSet<string>(StringComparer.Ordinal);
   var parts=new HashSet<string>(StringComparer.Ordinal);
   foreach(var mr in root.GetComponentsInChildren<MeshRenderer>(true)){
     var match=Name.Match(mr.name);
     Require(match.Success,"UNKNOWN_R11_MATERIAL_MESH:"+mr.name);
     var style=match.Groups["style"].Value;
     var part=match.Groups["part"].Value;
     styles.Add(style);parts.Add(part);
     var filter=mr.GetComponent<MeshFilter>();
     if(filter==null || filter.sharedMesh==null ||
       !filter.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0) ||
       filter.sharedMesh.uv.Length!=filter.sharedMesh.vertexCount)missingUV++;
     Require(mr.sharedMaterials.Length==1,"R11_SEMANTIC_MATERIAL_SLOT_COUNT_CHANGED:"+mr.name);
     var mat=MaterialFor(style,part);
     if(mat.shader==null || mat.shader.name!="Universal Render Pipeline/Lit")badShader++;
     mr.sharedMaterials=new[]{mat};
     // Limited shadows for new secondary details, inherited urban lighting is unchanged.
     mr.shadowCastingMode=ShadowCastingMode.On;
     mr.receiveShadows=true;
     count++;
   }
   Require(count==manifest.meshes && styles.Count==50 && parts.Count==6 &&
     missingUV==0 && badShader==0,"R11_MESH_STYLE_UV_OR_SHADERS_NOT_APPROVED");
   Require(EditorSceneManager.SaveScene(scene,Output,false),"R11_UNITY_SCENE_SAVE_FAIL");
   AssetDatabase.SaveAssets();
   string dir=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
   var output=Path.Combine(dir,"build/R11_ArchitectureQA");
   Directory.CreateDirectory(output);
   var result=new Report{
     status="R11_UNITY_REAL_VOLUMETRY_URP_TECHNICAL_PASS_VISUAL_PENDING",
     unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
     renderer=SystemInfo.graphicsDeviceType.ToString(),
     input_scene=baseScene,output_scene=Output,fbx_sha256=sha,
     all_buildings=1468,old_road_triangles=3731,vegetation_osm_count=48,
     architecture_renderers=count,architecture_styles=styles.Count,
     shaders_invalid=badShader,uv0_missing=missingUV,
     balconied_buildings=manifest.balcony_buildings,balconies=manifest.balconies,
     rooftop_units=manifest.roof_units,cornices=manifest.cornices
   };
   File.WriteAllText(Path.Combine(output,"R11_UnityArchitectureQA.json"),JsonUtility.ToJson(result,true)+"\n",Encoding.UTF8);
   Debug.Log("RESORT_R11_UNITY_ARCHITECTURE_PASS renderers="+count+" styles="+styles.Count+
     " balconies="+manifest.balconies+" rooftops="+manifest.roof_units+
     " roads=3731 trees=48 uvMissing=0");
 }
}
