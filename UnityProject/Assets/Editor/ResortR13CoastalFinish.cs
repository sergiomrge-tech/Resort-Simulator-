// R13 derives R12. Fail closed on missing native QA; never change older scenes.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class ResortR13CoastalFinish {
 public const string Source="Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity";
 public const string Scene="Assets/Scenes/R13_Copacabana_200m_Premium.unity";
 const string Fbx="Assets/Architecture/R13_Coastal/R13_OSM_Coastal_Sectors.fbx";
 const string Dir="Assets/Materials/R13_Coastal";
 [Serializable] public class Sector {public int sector;public string geometry,native_gate,visual_gate;public float[] local_x_m;}
 [Serializable] public class Manifest {public string status,fbx_sha256;public int meshes,faces,native_missing_uv0;public int[] frame_m,refined_sectors;public Sector[] sectors;}
 [Serializable] class Report {public string status,unity_version,gpu,renderer,fbx_sha256;public int meshes,road_triangles,trees,missing_uv0,shader_errors; public bool artistic_gate_approved=false,fps_measured=false;}
 static void Need(bool ok,string why){if(!ok)throw new InvalidOperationException("R13_BLOCKED:"+why);}
 public static string Sha(string p){using(var f=File.OpenRead(p))using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
 static void Folder(string path){string p="Assets";foreach(string part in path.Substring(7).Split('/')){string next=p+"/"+part;if(!AssetDatabase.IsValidFolder(next))AssetDatabase.CreateFolder(p,part);p=next;}}
 static Texture2D Texture(string kind,string channel){
  string path="Assets/Textures/R13_Coastal/r13_"+kind+"_"+channel+".png";
  var importer=AssetImporter.GetAtPath(path) as TextureImporter;Need(importer!=null,"PBR_MAP_MISSING:"+path);
  bool normal=channel=="normal",srgb=channel=="base";
  if(importer.sRGBTexture!=srgb||importer.textureType!=(normal?TextureImporterType.NormalMap:TextureImporterType.Default)||!importer.mipmapEnabled||importer.wrapMode!=TextureWrapMode.Repeat){
   importer.sRGBTexture=srgb;importer.textureType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;
   importer.mipmapEnabled=true;importer.wrapMode=TextureWrapMode.Repeat;importer.anisoLevel=4;importer.maxTextureSize=2048;importer.SaveAndReimport();
  }
  var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(path);Need(tex!=null,"PBR_TEXTURE_IMPORT_FAILED:"+path+" importer="+importer.textureType);return tex;
 }
 static Material Mat(string key){
  if(key.StartsWith("ocean")){
   string oceanPath=Dir+"/R13_ShoreOcean.mat";var water=AssetDatabase.LoadAssetAtPath<Material>(oceanPath);
   var ocean=Shader.Find("Resort/R13/ShoreOcean");Need(ocean!=null&&ocean.isSupported&&!ShaderUtil.ShaderHasError(ocean),"R13_OCEAN_SHADER_FAILED");
   if(water==null){water=new Material(ocean);AssetDatabase.CreateAsset(water,oceanPath);}water.shader=ocean;water.enableInstancing=true;return water;
  }
  Need(new[]{"mosaic","sand","wet_sand","sand_service","limestone","timber","metal","leaves","soil","baseline","baseline_dark"}.Contains(key),"UNKNOWN_MATERIAL_SEMANTIC:"+key);
  string path=Dir+"/R13_"+key+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
  var shader=Shader.Find("Universal Render Pipeline/Lit");Need(shader!=null&&shader.isSupported,"URP_LIT_UNSUPPORTED");
  if(m==null){m=new Material(shader){name="R13_"+key};AssetDatabase.CreateAsset(m,path);}m.shader=shader;m.enableInstancing=true;
  string map=key=="wet_sand"||key=="sand_service"?"sand":key;
  bool textured=new[]{"mosaic","sand","wet_sand","sand_service","limestone","timber"}.Contains(key);
  m.SetColor("_BaseColor",key=="wet_sand"?new Color(.62f,.60f,.55f):key=="metal"?new Color(.12f,.16f,.17f):key=="leaves"?new Color(.13f,.29f,.10f):key=="soil"?new Color(.12f,.085f,.045f):key=="baseline"?new Color(.72f,.70f,.66f):key=="baseline_dark"?new Color(.20f,.22f,.23f):Color.white);
  m.SetFloat("_Metallic",key=="metal"?.8f:0);m.SetFloat("_Smoothness",key=="metal"?.64f:key=="wet_sand"?.48f:.2f);
  if(textured){m.SetTexture("_BaseMap",Texture(map,"base"));m.SetTexture("_BumpMap",Texture(map,"normal"));m.SetFloat("_BumpScale",.65f);m.EnableKeyword("_NORMALMAP");
   if(key!="wet_sand"){m.SetTexture("_MetallicGlossMap",Texture(map,"mask"));m.SetFloat("_Smoothness",1);m.EnableKeyword("_METALLICSPECGLOSSMAP");}}
  m.SetFloat("_Cull",key=="leaves"?0:2);EditorUtility.SetDirty(m);return m;
 }
 [MenuItem("Resort/R13/Build native 200m coastal slice")]
 public static void Build(){
  string repo=Path.GetFullPath(Path.Combine(Application.dataPath,"../.."));
  var q=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(repo,"UnityProject/Assets/Architecture/R13_Coastal/R13_COVERAGE.json")));
  Need(q.status=="R13_NATIVE_FBX_REIMPORT_CONTINUITY_UV_PASS_ART_PENDING"&&q.frame_m.SequenceEqual(new[]{2000,1000})&&q.native_missing_uv0==0,"NATIVE_QA_REQUIRED");
  Need(q.sectors.Length==10&&q.sectors.All(s=>s.native_gate=="PASS_REIMPORT_CONTINUITY_UV"),"COAST_SEAMS_UNTESTED");
  Need(Sha(Path.Combine(repo,"UnityProject/"+Fbx))==q.fbx_sha256,"FBX_HASH_CHANGED");
  Need(AssetDatabase.LoadAssetAtPath<SceneAsset>(Source)!=null,"R12_SCENE_MISSING_REBUILD_R7_TO_R12_FIRST");
  var scene=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);
  var all=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  var road=all.Single(r=>r.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS"));
  Need(road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"OSM_ROADS_CHANGED");
  Need(all.Count(r=>r.name.StartsWith("R9_TREE_"))==48,"OSM_TREE_POSITIONS_LOST");
  // Replace the earlier continuous surfaces in THIS derived scene only.
  foreach(var r in all.Where(r=>r.name.StartsWith("R10_MOSAIC_")||r.name.StartsWith("R10_PROMENADE_")||r.name.StartsWith("R10_WATER_BREAKING_")||r.name.StartsWith("R9_SAND_REAL_OSM_COAST")||r.name.StartsWith("R9_OCEAN_REAL_OSM_COAST")))r.enabled=false;
  var importer=AssetImporter.GetAtPath(Fbx) as ModelImporter;Need(importer!=null,"NATIVE_FBX_NOT_IMPORTED");
  if(!importer.isReadable){importer.isReadable=true;importer.SaveAndReimport();}
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Fbx);Need(prefab!=null,"FBX_PREFAB_MISSING");
  var root=(GameObject)PrefabUtility.InstantiatePrefab(prefab);root.name="R13_OSM_COAST_SECTORS";Folder(Dir);
  var mats=new Dictionary<string,Material>();int count=0,uv=0,bad=0;
  foreach(var r in root.GetComponentsInChildren<MeshRenderer>()){
   // Surface refinement applies only to sectors actually generated as refined.
   int sector=int.Parse(r.name.Substring(5,2));string key=r.name.Substring(8).Replace("_LOD1","").Replace("_LOD2","");
   if(key.StartsWith("baseline_dark"))key="baseline_dark";
   if(key.StartsWith("baseline_edge"))key="limestone";
   if(!q.refined_sectors.Contains(sector)&&key=="mosaic")key="baseline";
   if(!mats.ContainsKey(key))mats[key]=Mat(key);r.sharedMaterial=mats[key];r.receiveShadows=true;
   r.shadowCastingMode=key.Contains("sand")||key.StartsWith("ocean")||key=="mosaic"||key=="baseline"?ShadowCastingMode.Off:ShadowCastingMode.On;
   var mesh=r.GetComponent<MeshFilter>().sharedMesh;if(!mesh.HasVertexAttribute(VertexAttribute.TexCoord0)||mesh.uv.Length!=mesh.vertexCount)uv++;
   if(ShaderUtil.ShaderHasError(r.sharedMaterial.shader))bad++;count++;
  }
  foreach(int sector in q.refined_sectors){
   string prefix="R13_S"+sector.ToString("00")+"_";
   var furniture=root.GetComponentsInChildren<MeshRenderer>().Where(r=>r.name.StartsWith(prefix)&&new[]{"limestone","timber","metal","leaves","soil"}.Any(k=>r.name==prefix+k||r.name.StartsWith(prefix+k+"_LOD"))).ToArray();
   var group=new GameObject(prefix+"Furniture_LOD");group.transform.SetParent(root.transform,false);
   foreach(var r in furniture)r.transform.SetParent(group.transform,true);
   var lod=group.AddComponent<LODGroup>();
   lod.SetLODs(new[]{new LOD(.20f,furniture.Where(r=>!r.name.Contains("_LOD")).Cast<Renderer>().ToArray()),new LOD(.07f,furniture.Where(r=>r.name.EndsWith("_LOD1")).Cast<Renderer>().ToArray()),new LOD(.02f,furniture.Where(r=>r.name.EndsWith("_LOD2")).Cast<Renderer>().ToArray())});lod.RecalculateBounds();
  }
  Need(count==q.meshes&&uv==0&&bad==0,"UV_MATERIAL_SHADER_GATE_FAILED");
  var check=root.GetComponentsInChildren<MeshRenderer>(true).Single(r=>r.name=="R13_S05_mosaic");
  Need(check.bounds.center.magnitude<1800f && check.bounds.extents.magnitude<1000f,
    "R13_FBX_IMPORTED_AT_100X_SCALE_OR_OUTSIDE_REAL_GEOGRAPHIC_FRAME:"+check.bounds.center);
  Debug.Log("R13_WORLD_METRE_SCALE_GATE_PASS center="+check.bounds.center+" extents="+check.bounds.extents);
  Need(EditorSceneManager.SaveScene(scene,Scene,false),"DERIVED_SCENE_SAVE_FAILED");AssetDatabase.SaveAssets();
  string outdir=Path.Combine(repo,"build/R13_QA");Directory.CreateDirectory(outdir);
  File.WriteAllText(Path.Combine(outdir,"R13_UnityTechnicalQA.json"),JsonUtility.ToJson(new Report{status="R13_UNITY_TECHNICAL_PASS_ART_PENDING",unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,renderer=SystemInfo.graphicsDeviceType.ToString(),fbx_sha256=q.fbx_sha256,meshes=count,road_triangles=3731,trees=48,missing_uv0=uv,shader_errors=bad},true));
  Debug.Log("R13_UNITY_NATIVE_PASS meshes="+count+" roads=3731 trees=48 missingUV=0 shaderErrors=0");
 }
 // Use only after native Blender has reconstructed R7-R12; never silently skip gates.
 public static void RebuildChain(){ResortR7FacadeFinish.Build();ResortR8FullCityFinish.Build();ResortR9UrbanFinish.Build();ResortR10CoastalFinish.Build();ResortR11ArchitectureFinish.Build();ResortR12StreetFinish.Build();Build();}
}
