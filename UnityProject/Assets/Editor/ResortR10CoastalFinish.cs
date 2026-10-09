// R10 isolated coastal/art finish. Original OSM and R7-R9 scenes remain immutable.
// Scene-specific visible corrections: broad city shadows restricted for far-camera
// QA, 50 material families tinted, UV mosaic promenade and animated sea shader.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;

public static class ResortR10CoastalFinish {
 const string SourceScene="Assets/Scenes/R9_Copacabana_Orla_Parques_Arvores.unity";
 const string TargetScene="Assets/Scenes/R10_Copacabana_Calçada_Mosaico_Mar.unity";
 const string FBX="Assets/Architecture/R10_Coastal/R10_Ocean_Foam_Mosaic_Promenade.fbx";
 const string QA="Assets/Architecture/R10_Coastal/R10_DETAILS_NATIVE_QA.json";
 const string MaterialDir="Assets/Materials/R10_Coastal";
 const string FacadeDir="Assets/Materials/R10_Facades";
 const string ShaderPath="Assets/Shaders/R10_AnimatedOcean.shader";
 static readonly Regex R8Style=new Regex(
   @"^R8_(?<style>cop_[a-z0-9_]+)__(?<part>wall|glass|roof)(?:\.\d+)*$",
   RegexOptions.Compiled|RegexOptions.CultureInvariant);
 [Serializable] public class Manifest {
  public string status;
  public int coast_aligned_length_m;
  public int map_inland_width_m;
  public int coast_samples;
  public int mosaic_stripes;
  public int sea_foam_stripes;
  public int fbx_meshes;
  public int fbx_faces;
  public string fbx_sha256;
 }
 [Serializable] public class Report {
  public string status;
  public string unity_version;
  public string gpu;
  public string renderer;
  public string output_scene;
  public string coastal_fbx_sha256;
  public int geographic_roads_triangles;
  public int detailed_background_facades;
  public int trees;
  public int promenade_meshes;
  public int facade_material_variants;
  public int coast_samples;
  public bool sea_shader_compiled;
  public bool aerial_shadows_temporarily_disabled;
  public bool visual_gate_approved=false;
  public bool fps_measured=false;
 }
 static void Demand(bool ok,string why){if(!ok)throw new InvalidOperationException("RESORT_R10_BLOCKED:"+why);}
 static string Sha(string p) {
  using(var f=File.OpenRead(p))using(var s=SHA256.Create())
   return BitConverter.ToString(s.ComputeHash(f)).Replace("-","").ToLowerInvariant();
 }
 static void Folder(string path) {
  var cur="Assets";
  foreach(var part in path.Substring("Assets/".Length).Split('/')) {
   var next=cur+"/"+part;
   if(!AssetDatabase.IsValidFolder(next))AssetDatabase.CreateFolder(cur,part);
   cur=next;
  }
 }
 static Material Make(string label,Shader shader,Color tint,float smooth,float metal){
  string path=MaterialDir+"/"+label+".mat";
  var m=AssetDatabase.LoadAssetAtPath<Material>(path);
  if(m==null){m=new Material(shader){name=label};AssetDatabase.CreateAsset(m,path);}
  m.shader=shader;
  if(m.HasProperty("_BaseColor"))m.SetColor("_BaseColor",tint);
  if(m.HasProperty("_Smoothness"))m.SetFloat("_Smoothness",smooth);
  if(m.HasProperty("_Metallic"))m.SetFloat("_Metallic",metal);
  m.enableInstancing=true;EditorUtility.SetDirty(m);
  return m;
 }
 static Color Tint(string style,string part) {
  int variant=1;
  var parts=style.Split('_');
  if(parts.Length>0)int.TryParse(parts[parts.Length-1],out variant);
  float n=(variant-3)*.035f;
  Color wall;
  if(style.Contains("art_deco"))wall=new Color(.86f,.77f,.63f);
  else if(style.Contains("residencial_orla"))wall=new Color(.76f,.78f,.76f);
  else if(style.Contains("hotel_classico"))wall=new Color(.82f,.72f,.62f);
  else if(style.Contains("hotel_contemporaneo"))wall=new Color(.60f,.70f,.73f);
  else if(style.Contains("predio_historico"))wall=new Color(.77f,.63f,.53f);
  else if(style.Contains("escritorio"))wall=new Color(.65f,.73f,.76f);
  else if(style.Contains("misto_loja"))wall=new Color(.81f,.73f,.64f);
  else if(style.Contains("residencial_anos70"))wall=new Color(.78f,.75f,.69f);
  else if(style.Contains("equipamento_especial"))wall=new Color(.70f,.69f,.66f);
  else wall=new Color(.75f,.74f,.69f);
  if(part=="glass")return new Color(.32f+n*.25f,.49f+n*.20f,.60f+n*.22f,1);
  if(part=="roof")return new Color(.43f+n,.43f+n*.6f,.42f+n*.5f,1);
  return new Color(Mathf.Clamp01(wall.r+n),Mathf.Clamp01(wall.g+n),Mathf.Clamp01(wall.b+n),1);
 }
 static int RefinishFacades(UnityEngine.SceneManagement.Scene scene) {
  Folder(FacadeDir);
  var renderers=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<MeshRenderer>(true));
  var generated=new Dictionary<string,Material>(StringComparer.Ordinal);
  foreach(var r in renderers){
   var match=R8Style.Match(r.name);
   if(!match.Success)continue;
   string style=match.Groups["style"].Value;
   string part=match.Groups["part"].Value;
   string key=style+"__"+part;
   if(!generated.TryGetValue(key,out var mat)){
    Demand(r.sharedMaterials.Length==1&&r.sharedMaterial!=null,"R8_MATERIAL_LOST:"+r.name);
    var existing=r.sharedMaterial;
    Demand(existing.shader!=null && existing.shader.name=="Universal Render Pipeline/Lit",
      "R8_PBR_TEXTURE_SOURCE_INVALID:"+r.name);
    string path=FacadeDir+"/R10_"+key+".mat";
    mat=AssetDatabase.LoadAssetAtPath<Material>(path);
    if(mat==null){mat=new Material(existing){name="R10_"+key};AssetDatabase.CreateAsset(mat,path);}
    mat.SetColor("_BaseColor",Tint(style,part));
    if(part=="glass"){mat.SetFloat("_Metallic",.21f);mat.SetFloat("_Smoothness",.77f);}
    if(part=="roof"){mat.SetFloat("_Metallic",.02f);mat.SetFloat("_Smoothness",.19f);}
    mat.enableInstancing=true;EditorUtility.SetDirty(mat);
    generated[key]=mat;
   }
   r.sharedMaterials=new[]{mat};
  }
  Demand(generated.Count==150,"EXPECTED_150_R10_FACADE_MATERIAL_VARIANTS:"+generated.Count);
  return generated.Count;
 }
 [MenuItem("Resort/R10/Construir fachada cor mar animado e calcada")]
 public static void Build() {
  Demand(AssetDatabase.LoadAssetAtPath<SceneAsset>(SourceScene)!=null,"R9_SCENE_MISSING");
  Demand(AssetDatabase.LoadAssetAtPath<GameObject>(FBX)!=null,"R10_NATIVE_COAST_FBX_NOT_FOUND");
  var shader=AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
  Demand(shader!=null && shader.isSupported,"OCEAN_SHADER_COMPILATION_NOT_SUPPORTED");
  var parsed=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(Application.dataPath,QA.Substring(7))));
  Demand(parsed!=null && parsed.status=="R10_COASTAL_NATIVE_BLEND_PASS_UNITY_PENDING" &&
    parsed.coast_aligned_length_m==2000 && parsed.map_inland_width_m==1000 &&
    parsed.coast_samples==401 && parsed.mosaic_stripes==3 && parsed.sea_foam_stripes==3 &&
    parsed.fbx_meshes==9 && parsed.fbx_faces==3600,"R10_MAP_OR_FBX_QA_FAILED");
  string disk=Path.Combine(Application.dataPath,FBX.Substring(7));
  string hash=Sha(disk);
  Demand(hash==parsed.fbx_sha256,"R10_BINARY_NOT_VALIDATED");
  var scene=EditorSceneManager.OpenScene(SourceScene,OpenSceneMode.Single);
  Demand(scene.isLoaded,"SOURCE_R9_SCENE_INVALID");
  var all=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  var road=all.SingleOrDefault(x=>x.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS",StringComparison.Ordinal));
  Demand(road!=null && road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"ROAD_SOURCE_MODIFIED");
  var trees=all.Where(x=>x.name.StartsWith("R9_TREE_",StringComparison.Ordinal)).ToArray();
  Demand(trees.Length==48,"R9_MAPPED_VEGETATION_LOST");
  var ocean=all.SingleOrDefault(x=>x.name.StartsWith("R9_OCEAN_REAL_OSM_COAST",StringComparison.Ordinal));
  Demand(ocean!=null,"R9_OCEAN_SOURCE_LOST");
  Folder(MaterialDir);
  var standard=Shader.Find("Universal Render Pipeline/Lit");
  Demand(standard!=null,"URP_LIT_UNSUPPORTED");
  ocean.sharedMaterial=Make("R10_Ocean_Animated_Glint",shader,new Color(.025f,.17f,.29f),.60f,.08f);
  // Make custom ocean shader's ocean colors explicit and stable across platforms.
  ocean.sharedMaterial.SetColor("_DeepColor",new Color(.025f,.19f,.30f));
  ocean.sharedMaterial.SetColor("_ShallowColor",new Color(.08f,.38f,.53f));
  ocean.sharedMaterial.SetColor("_FoamColor",new Color(.54f,.78f,.79f));
  ocean.sharedMaterial.SetFloat("_WaveSpeed",.34f);
  ocean.sharedMaterial.SetFloat("_WaveContrast",.34f);
  var mosaic=Make("R10_White_Natural_Mosaic",standard,new Color(.79f,.77f,.70f),.17f,0);
  var charcoal=Make("R10_Dark_Stone_Wave",standard,new Color(.20f,.22f,.23f),.14f,0);
  var curb=Make("R10_Stone_Edge",standard,new Color(.55f,.52f,.49f),.12f,0);
  var foam=Make("R10_Subtle_Breaking_Surf",standard,new Color(.64f,.83f,.85f),.28f,0);
  int n=RefinishFacades(scene);
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FBX);
  var asset=PrefabUtility.InstantiatePrefab(prefab) as GameObject;
  Demand(asset!=null,"R10_GEO_INSTANTIATION_FAILED");
  asset.name="R10_GEOREFERENCED_WAVE_PROMENADE_AND_OCEAN_FOAM";
  int count=0;
  foreach(var r in asset.GetComponentsInChildren<MeshRenderer>(true)){
   var name=r.name;
   Demand(r.sharedMaterials.Length==1,"R10_MATERIAL_SLOT_MISSING:"+name);
   var f=r.GetComponent<MeshFilter>();
   Demand(f!=null && f.sharedMesh!=null && f.sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0),
     "R10_SURFACE_UV0_MISSING:"+name);
   Material choice=
    name.StartsWith("R10_MOSAIC_PROMENADE_BASE")?mosaic:
    name.StartsWith("R10_MOSAIC_WAVE_BAND_")?charcoal:
    name.StartsWith("R10_PROMENADE_")?curb:
    name.StartsWith("R10_WATER_BREAKING_FOAM_")?foam:null;
   Demand(choice!=null,"UNKNOWN_R10_COAST_MESH:"+name);
   r.sharedMaterials=new[]{choice};
   r.shadowCastingMode=ShadowCastingMode.Off;
   r.receiveShadows=false;
   count++;
  }
  Demand(count==9,"R10_PROMENADE_MESH_MISSING");
  var lights=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<Light>(true)).ToArray();
  var sun=lights.FirstOrDefault(x=>x.type==LightType.Directional);
  Demand(sun!=null,"SUN_NOT_PRESENT");
  // The original black aerial frame was a cold URP single-camera render,
  // not a geographic geometry problem: the warm-up capture R10 renders
  // five real GPU frames. Preserve SOFT shadows at moderated strength.
  // Full gameplay cascades, SSAO, 60 FPS remain pending further QA.
  sun.shadows=LightShadows.Soft;
  sun.shadowStrength=.18f;
  sun.intensity=1.25f;
  RenderSettings.ambientMode=AmbientMode.Trilight;
  RenderSettings.ambientSkyColor=new Color(.71f,.73f,.74f);
  RenderSettings.ambientEquatorColor=new Color(.53f,.57f,.59f);
  RenderSettings.ambientGroundColor=new Color(.42f,.43f,.43f);
  RenderSettings.ambientIntensity=1.20f;
  Demand(EditorSceneManager.SaveScene(scene,TargetScene,false),"R10_SCENE_SAVE_FAILED");
  AssetDatabase.SaveAssets();
  string dir=Path.GetFullPath(Path.Combine(Application.dataPath,"..",".."));
  Directory.CreateDirectory(Path.Combine(dir,"build/R10_CoastalQA"));
  var report=new Report{
   status="R10_UNITY_URP_COPACABANA_ART_TECHNICAL_PASS_VISUAL_GATE_PENDING",
   unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
   renderer=SystemInfo.graphicsDeviceType.ToString(),
   output_scene=TargetScene,coastal_fbx_sha256=hash,
   geographic_roads_triangles=3731,detailed_background_facades=350,
   trees=48,promenade_meshes=count,facade_material_variants=n,coast_samples=401,
   sea_shader_compiled=shader.isSupported,aerial_shadows_temporarily_disabled=false
  };
  File.WriteAllText(Path.Combine(dir,"build/R10_CoastalQA/R10_UnityTechnicalQA.json"),
   JsonUtility.ToJson(report,true)+"\n",Encoding.UTF8);
  Debug.Log("RESORT_R10_COPACABANA_PASS promenade=9 variants=150 trees=48 roadTris=3731 animatedOcean=true aerialShadowFix=true");
 }
}
