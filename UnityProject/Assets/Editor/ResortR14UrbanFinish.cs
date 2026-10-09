// Additive R14 scene only. Frozen R13 remains the source and before reference.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class ResortR14UrbanFinish {
 public const string Source="Assets/Scenes/R13_VisualPass2.unity";
 public const string Scene="Assets/Scenes/R14_Copacabana_Urban_Connectors.unity";
 const string Dir="Assets/Materials/R14_Urban";
 public static string Repo(){return ResortR13Pass2Finish.Repo();}
 public static string Sha(string path){return ResortR13Pass2Finish.Sha(path);}
 public static void EnsurePipeline(){ResortR13Pass2Finish.EnsurePipeline();}
 [Serializable] class Manifest {public string status,fbx_sha256;public int meshes,native_missing_uv0;public int[] frame_m;}
 [Serializable] class Report {public string status,unity_version,urp_version,renderer,gpu,connector_fbx_sha256,art_fbx_sha256;public int connector_meshes,art_meshes,missing_uv0,shader_errors,missing_material_slots,default_materials,texture2d_count,road_triangles,original_trees;public bool artistic_gate_approved=false,fps_measured=false,playmode_water_animation_tested=false;}
 static void Need(bool ok,string why){if(!ok)throw new InvalidOperationException("R14_BLOCKED:"+why);}
 static void Folder(string path){string p="Assets";foreach(string part in path.Substring(7).Split('/')){string next=p+"/"+part;if(!AssetDatabase.IsValidFolder(next))AssetDatabase.CreateFolder(p,part);p=next;}}
 static Texture2D Texture(string key,string channel){
  string path="Assets/Textures/R14_Urban/r14_"+key+"_"+channel+".png";
  var imp=AssetImporter.GetAtPath(path) as TextureImporter;
  Need(imp!=null&&imp.textureShape==TextureImporterShape.Texture2D,"TEXTURE_NOT_2D:"+path);
  Need(imp.sRGBTexture==(channel=="base")&&imp.textureType==(channel=="normal"?TextureImporterType.NormalMap:TextureImporterType.Default),"TEXTURE_CHANNEL:"+path);
  Need(imp.mipmapEnabled,"MIPS_REQUIRED:"+path);
  var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(path);Need(tex!=null,"TEXTURE_MISSING:"+path);return tex;
 }
 static Material Material(string key){
  string asset=Dir+"/R14_"+key+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(asset);
  var sh=Shader.Find("Universal Render Pipeline/Lit");Need(sh!=null&&sh.isSupported&&!ShaderUtil.ShaderHasError(sh),"URP_LIT_FAILED");
  if(m==null){m=new Material(sh);AssetDatabase.CreateAsset(m,asset);}m.shader=sh;m.name="R14_"+key;m.enableInstancing=true;
  m.SetColor("_BaseColor",Color.white);m.SetTexture("_BaseMap",Texture(key,"base"));m.SetTexture("_BumpMap",Texture(key,"normal"));m.SetTexture("_MetallicGlossMap",Texture(key,"mask"));
  m.SetFloat("_Metallic",0);m.SetFloat("_Smoothness",1);m.SetFloat("_BumpScale",.7f);m.EnableKeyword("_NORMALMAP");m.EnableKeyword("_METALLICSPECGLOSSMAP");m.SetFloat("_Cull",key=="foliage"?0:2);EditorUtility.SetDirty(m);return m;
 }
 static GameObject Import(string file,string manifest,string expected,out Manifest q){
  string repo=ResortR13Pass2Finish.Repo();q=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/"+manifest)));
  Need(q.status==expected&&q.native_missing_uv0==0&&q.frame_m.SequenceEqual(new[]{2000,1000}),"NATIVE_REIMPORT_REQUIRED:"+manifest);
  string path="Assets/Architecture/R14_Urban/"+file;
  Need(ResortR13Pass2Finish.Sha(Path.Combine(repo,"UnityProject/"+path))==q.fbx_sha256,"FBX_HASH_CHANGED");
  var imp=AssetImporter.GetAtPath(path) as ModelImporter;Need(imp!=null&&Mathf.Abs(imp.globalScale-1)<.0001f&&imp.useFileUnits,"MODEL_SCALE_100X_REGRESSION");
  if(!imp.isReadable){imp.isReadable=true;imp.SaveAndReimport();}
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);Need(prefab!=null,"FBX_PREFAB_MISSING");
  var root=(GameObject)PrefabUtility.InstantiatePrefab(prefab);Need(root!=null,"FBX_INSTANCE_FAILED");return root;
 }
 // Call this only in the isolated R14_NativeWorkspace when source scenes are
 // absent. Never regenerate prior scenes in a user's existing project.
 public static void BuildIsolatedFoundation(){
  Need(ResortR13Pass2Finish.Repo().Replace('\\','/').EndsWith("/build/R14_NativeWorkspace"),"ISOLATED_FOUNDATION_ONLY");
  ResortR7FacadeFinish.Build();ResortR8FullCityFinish.Build();ResortR9UrbanFinish.Build();ResortR10CoastalFinish.Build();ResortR11ArchitectureFinish.Build();ResortR12StreetFinish.Build();ResortR13CoastalFinish.Build();ResortR13Pass2Finish.Build();Build();
 }
 [MenuItem("Resort/R14/Build derived urban connectors and seven-sector art")]
 public static void Build(){
  ResortR13Pass2Finish.EnsurePipeline();
  Need(AssetDatabase.LoadAssetAtPath<SceneAsset>(Source)!=null,"R13_SOURCE_SCENE_MISSING");
  var scene=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);Folder(Dir);
  var sourceRenderers=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  var roads=sourceRenderers.Single(r=>r.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS"));
  Need(roads.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"GIS_ROADS_CHANGED");
  Need(sourceRenderers.Count(r=>r.name.StartsWith("R9_TREE_"))==48,"OSM_TREE_POSITIONS_LOST");
  Manifest connectors,art;var cr=Import("R14_GIS_Urban_Connectors.fbx","R14_CONNECTORS_NATIVE.json","R14_NATIVE_FBX_REIMPORT_PASS_ART_PENDING",out connectors);cr.name="R14_GIS_CONNECTORS";
  var ar=Import("R14_Coastal_Art_Seven_Sectors.fbx","R14_ART_NATIVE.json","R14_ART_NATIVE_FBX_REIMPORT_PASS_ART_PENDING",out art);ar.name="R14_SEVEN_BASE_SECTORS_ART";
  var all=cr.GetComponentsInChildren<MeshRenderer>().Concat(ar.GetComponentsInChildren<MeshRenderer>()).ToArray();
  var mats=new Dictionary<string,Material>();int missingUV=0,bad=0;
  foreach(var r in all){
   string key=r.name.Substring(8).Replace("art_","").Replace("_LOD1","").Replace("_LOD2","");
   if(!mats.ContainsKey(key))mats[key]=Material(key);r.sharedMaterial=mats[key];r.receiveShadows=true;
   var mesh=r.GetComponent<MeshFilter>().sharedMesh;
   if(!mesh.HasVertexAttribute(VertexAttribute.TexCoord0)||mesh.uv.Length!=mesh.vertexCount)missingUV++;
   if(ShaderUtil.ShaderHasError(r.sharedMaterial.shader))bad++;
   Need(r.bounds.center.magnitude<2000&&r.bounds.size.magnitude<1800,"FBX_100X_OR_OFFSET:"+r.name);
   // Connectors are true pedestrian/curb solids; collision is generated here,
   // gameplay movement and regulatory accessibility remain a runtime gate.
   if(r.transform.IsChildOf(cr.transform)&&!r.name.EndsWith("gutter")){
    var collider=r.gameObject.AddComponent<MeshCollider>();collider.sharedMesh=mesh;
   }
  }
  foreach(int s in new[]{0,1,2,3,7,8,9}){
   var renderers=ar.GetComponentsInChildren<MeshRenderer>().Where(r=>r.name.StartsWith("R14_S"+s.ToString("00")+"_")).ToArray();
   if(renderers.Length==0)continue;
   var group=new GameObject("R14_S"+s.ToString("00")+"_ArtLOD");group.transform.SetParent(ar.transform,false);
   foreach(var r in renderers)r.transform.SetParent(group.transform,true);
   var lod=group.AddComponent<LODGroup>();lod.SetLODs(new[]{new LOD(.22f,renderers.Where(r=>!r.name.Contains("_LOD")).Cast<Renderer>().ToArray()),new LOD(.08f,renderers.Where(r=>r.name.EndsWith("_LOD1")).Cast<Renderer>().ToArray()),new LOD(.025f,renderers.Where(r=>r.name.EndsWith("_LOD2")).Cast<Renderer>().ToArray())});lod.RecalculateBounds();
  }
  int slots=all.SelectMany(r=>r.sharedMaterials).Count(m=>m==null);
  int defaults=all.SelectMany(r=>r.sharedMaterials).Count(m=>m!=null&&(m.name=="Default-Material"||m.name=="DefaultMaterial"));
  Need(all.Length==connectors.meshes+art.meshes&&missingUV==0&&bad==0&&slots==0&&defaults==0,"R14_UV_MATERIAL_NATIVE_GATE_FAILED");
  // Apply R14 asphalt PBR to the road material, keeping its copied mesh untouched.
  roads.sharedMaterial=Material("asphalt");
  Need(EditorSceneManager.SaveScene(scene,Scene,false),"R14_SCENE_SAVE_FAILED");AssetDatabase.SaveAssets();
  string dir=Path.Combine(ResortR13Pass2Finish.Repo(),"build/R14_QA");Directory.CreateDirectory(dir);
  File.WriteAllText(Path.Combine(dir,"R14_UnityTechnicalQA.json"),JsonUtility.ToJson(new Report{status="R14_UNITY_NATIVE_PASS_ART_PENDING",unity_version=Application.unityVersion,urp_version=UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset).Assembly).version,renderer=SystemInfo.graphicsDeviceType.ToString(),gpu=SystemInfo.graphicsDeviceName,connector_fbx_sha256=connectors.fbx_sha256,art_fbx_sha256=art.fbx_sha256,connector_meshes=connectors.meshes,art_meshes=art.meshes,missing_uv0=missingUV,shader_errors=bad,missing_material_slots=slots,default_materials=defaults,texture2d_count=24,road_triangles=3731,original_trees=48},true));
  Debug.Log("R14_UNITY_NATIVE_PASS connectors="+connectors.meshes+" art="+art.meshes+" roads=3731 trees=48 missingUV=0 shaderErrors=0");
 }
}
