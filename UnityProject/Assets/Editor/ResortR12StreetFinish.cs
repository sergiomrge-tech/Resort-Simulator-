// R12: independent OSM street-level architectural layer on R11, with original sign textures.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;
public static class ResortR12StreetFinish {
 const string FBX="Assets/Architecture/R12_Storefronts/R12_StreetLevel_1418_Entrances_Storefronts.fbx";
 const string QA="Assets/Architecture/R12_Storefronts/R12_STREETLEVEL_NATIVE_QA.json";
 const string Output="Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity";
 const string MatDir="Assets/Materials/R12_Street";
 [Serializable] class Manifest {
  public string status,fbx_sha256;
  public int coast_m,inland_m,osm_full_city,r8_source_buildings,mesh_parts,mesh_faces,storefronts,lobbies,doors,showcase_windows,awnings,fictional_sign_panels;
 }
 [Serializable] class Report {
  public string status,unity_version,gpu,renderer,source_scene,output_scene,fbx_sha256;
  public int map_coast_m,map_inland_m,total_buildings,road_triangles,trees,r11_renderers;
  public int r12_renderers,entrances,storefronts,glass_showcases,awnings,fictional_signs,sign_asset_count,invalid_materials,missing_uv0;
  public bool artistic_gate_approved=false;
  public bool fps_measured=false;
 }
 static void Need(bool c,string s){if(!c)throw new InvalidOperationException("RESORT_R12_BLOCKED:"+s);}
 static string Sha(string p){using(var f=File.OpenRead(p))using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
 static void Folder(string p){string cur="Assets";foreach(string seg in p.Substring(7).Split('/')){string next=cur+"/"+seg;if(!AssetDatabase.IsValidFolder(next))AssetDatabase.CreateFolder(cur,seg);cur=next;}}
 static Material Create(string key,Color color,float metal,float smooth,Texture2D tex=null){
  string path=MatDir+"/R12_"+key+".mat";
  var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
  Shader shader=Shader.Find("Universal Render Pipeline/Lit");
  Need(shader!=null,"URP_LIT_NOT_FOUND");
  if(mat==null){mat=new Material(shader){name="R12_"+key};AssetDatabase.CreateAsset(mat,path);}
  mat.shader=shader;mat.SetColor("_BaseColor",color);mat.SetFloat("_Metallic",metal);mat.SetFloat("_Smoothness",smooth);
  mat.SetTexture("_BaseMap",tex);mat.enableInstancing=true;
  if(tex!=null){
   if(mat.HasProperty("_Cull"))mat.SetFloat("_Cull",0);
   mat.doubleSidedGI=true;
   mat.EnableKeyword("_EMISSION");
   mat.SetColor("_EmissionColor",new Color(.09f,.08f,.07f));
   mat.SetTexture("_EmissionMap",tex);
  }else{
   mat.SetTexture("_EmissionMap",null);mat.DisableKeyword("_EMISSION");
  }
  EditorUtility.SetDirty(mat);return mat;
 }
 static Texture2D GlassArt(string kind){
  string path="Assets/Textures/R12_Storefronts/r12_glass_"+kind+".png";
  var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
  Need(texture!=null&&texture.width==512&&texture.height==1024,"ORIGINAL_GLAZING_TEXTURE_MISSING:"+kind);
  return texture;
 }
 static string R11Scene(){
  var q=AssetDatabase.FindAssets("R11_Copacabana t:Scene",new[]{"Assets/Scenes"})
   .Select(AssetDatabase.GUIDToAssetPath).Where(p=>Path.GetFileName(p).StartsWith("R11_Copacabana_")).ToArray();
  Need(q.Length==1,"R11_VALIDATED_SCENE_MISSING");return q[0];
 }
 [MenuItem("Resort/R12/Integrar fachadas lojas vitrines e entradas")]
 public static void Build(){
  string source=R11Scene();
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FBX);
  Need(prefab!=null,"R12_NATIVE_FBX_MISSING");
  var disk=Path.Combine(Application.dataPath,FBX.Substring(7));
  var report=Path.Combine(Application.dataPath,QA.Substring(7));
  Need(File.Exists(disk)&&File.Exists(report),"R12_FBX_JSON_NOT_FOUND");
  var sourceQA=JsonUtility.FromJson<Manifest>(File.ReadAllText(report));
  Need(sourceQA!=null&&sourceQA.status=="R12_NATIVE_OSM_SHOPFRONT_FBX_GENERATED_UNITY_PENDING"
   &&sourceQA.coast_m==2000&&sourceQA.inland_m==1000&&sourceQA.osm_full_city==1468
   &&sourceQA.r8_source_buildings==1418&&sourceQA.mesh_parts>=19&&sourceQA.mesh_faces>100000
   &&sourceQA.doors>=1350&&sourceQA.storefronts>=300
   &&sourceQA.fictional_sign_panels==sourceQA.storefronts&&sourceQA.awnings==sourceQA.storefronts,
   "R12_NATIVE_GIS_ASSERTIONS_FAILED");
  var hash=Sha(disk);
  Need(hash==sourceQA.fbx_sha256,"R12_NATIVE_FBX_HASH_CHANGED");
  var scene=EditorSceneManager.OpenScene(source,OpenSceneMode.Single);
  var existing=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  var road=existing.SingleOrDefault(x=>x.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS"));
  Need(road!=null && road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"OSM_ROADS_CHANGED");
  int trees=existing.Count(r=>r.name.StartsWith("R9_TREE_")),r11=existing.Count(r=>r.name.StartsWith("R11_cop_"));
  Need(trees==48&&r11==210,"R11_R9_SOURCE_SCENE_CORRUPT");
  Folder(MatDir);
  var baseMats=new Dictionary<string,Material> {
   {"door_glass",Create("TintedEntryGlass",new Color(.83f,.89f,.92f),.18f,.89f,GlassArt("entrance"))},
   {"door_frame",Create("AnodizedAluminium",new Color(.30f,.33f,.36f),.72f,.64f)},
   {"stone_entrance",Create("WarmLimestone",new Color(.78f,.72f,.64f),.04f,.25f)},
   {"warm_interiors",Create("WarmShopInterior",new Color(.65f,.40f,.25f),.04f,.35f)},
   {"showcase_glass",Create("ShowcaseSlateGlass",new Color(.91f,.94f,.98f),.19f,.91f,GlassArt("showcase"))},
   {"canopy_dark",Create("CanopySlate",new Color(.30f,.30f,.29f),.12f,.28f)},
   {"awning_trim",Create("BrushedBrass",new Color(.76f,.60f,.37f),.75f,.67f)}
  };
  var signMats=new Dictionary<int,Material>();
  for(int i=0;i<12;i++){
   string path="Assets/Textures/R12_Storefronts/r12_sign_"+i.ToString("00")+".png";
   var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
   Need(tex!=null&&tex.width==1024&&tex.height==256,"SIGN_ART_12_MISSING:"+path);
   signMats[i]=Create("ShopSign_"+i.ToString("00"),Color.white,.04f,.51f,tex);
  }
  var root=PrefabUtility.InstantiatePrefab(prefab) as GameObject;
  Need(root!=null,"PREFAB_INSTANCE_FAILED");
  root.name="R12_ORIGINAL_OSM_STREET_LEVEL_LOBBY_STORES";
  int count=0,uvmissing=0,bad=0,signed=0;
  var used=new HashSet<int>();
  foreach(var mr in root.GetComponentsInChildren<MeshRenderer>(true)){
   string name=mr.name;
   var match=Regex.Match(name,@"^R12_sign_(\d\d)(?:\.\d+)*$");
   Material mat=null;
   if(match.Success){
    int key=int.Parse(match.Groups[1].Value);
    Need(signMats.TryGetValue(key,out mat),"UNMAPPED_FICTIONAL_SIGN");
    used.Add(key);signed++;mr.shadowCastingMode=ShadowCastingMode.Off;
   }else{
    string suffix=name.StartsWith("R12_")?name.Substring(4):name;
    if(suffix.Contains("."))suffix=suffix.Substring(0,suffix.IndexOf('.'));
    Need(baseMats.TryGetValue(suffix,out mat),"UNKNOWN_R12_MATERIAL_SLOT:"+name);
    mr.shadowCastingMode=ShadowCastingMode.On;
   }
   var mesh=mr.GetComponent<MeshFilter>();
   if(mesh==null||mesh.sharedMesh==null||!mesh.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0))uvmissing++;
   if(mat==null||mat.shader==null||mat.shader.name!="Universal Render Pipeline/Lit")bad++;
   Need(mr.sharedMaterials.Length==1,"UNEXPECTED_BLENDER_MATERIAL_SLOTS:"+name);
   mr.sharedMaterials=new[]{mat};mr.receiveShadows=true;count++;
  }
  Need(count==sourceQA.mesh_parts&&signed>=9&&used.Count>=9&&uvmissing==0&&bad==0,
   "R12_VISUAL_MATERIAL_GATE:"+count+"/"+signed+"/"+uvmissing+"/"+bad);
  Need(EditorSceneManager.SaveScene(scene,Output,false),"R12_DERIVED_SCENE_SAVE_FAILED");
  AssetDatabase.SaveAssets();
  string folder=Path.GetFullPath(Path.Combine(Application.dataPath,"..","..","build","R12_StreetQA"));
  Directory.CreateDirectory(folder);
  var result=new Report{
   status="R12_URP_STREETLEVEL_TECHNICAL_PASS_ART_VISUAL_PENDING",
   unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
   renderer=SystemInfo.graphicsDeviceType.ToString(),
   source_scene=source,output_scene=Output,fbx_sha256=hash,
   map_coast_m=2000,map_inland_m=1000,total_buildings=1468,road_triangles=3731,
   trees=trees,r11_renderers=r11,r12_renderers=count,entrances=sourceQA.doors,
   storefronts=sourceQA.storefronts,glass_showcases=sourceQA.showcase_windows,
   awnings=sourceQA.awnings,fictional_signs=sourceQA.fictional_sign_panels,
   sign_asset_count=signMats.Count,invalid_materials=bad,missing_uv0=uvmissing
  };
  File.WriteAllText(Path.Combine(folder,"R12_UnityStreetQA.json"),JsonUtility.ToJson(result,true)+"\n",Encoding.UTF8);
  Debug.Log("RESORT_R12_STREET_PASS doors="+sourceQA.doors+" shops="+sourceQA.storefronts+
   " showcase="+sourceQA.showcase_windows+" signs="+sourceQA.fictional_sign_panels+
   " renderers="+count+" artAssets=12 missingUV=0 shaderErrors=0");
 }
}
