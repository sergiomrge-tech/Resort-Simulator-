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

public static class ResortR13Pass2Finish {
 public const string Source="Assets/Scenes/R13_Copacabana_200m_Premium.unity";
 public const string Scene="Assets/Scenes/R13_VisualPass2.unity";
 const string Fbx="Assets/Architecture/R13_Pass2/R13_VisualPass2_Coastal_Sectors.fbx";
 const string Dir="Assets/Materials/R13_Pass2";
 [Serializable] public class Sector {public int sector;public string geometry,native_gate,visual_gate;public float[] local_x_m;}
 [Serializable] public class Manifest {public string status,fbx_sha256;public int meshes,faces,native_missing_uv0;public int[] frame_m,refined_sectors;public Sector[] sectors;}
 [Serializable] class Report {public string status,unity_version,gpu,renderer,fbx_sha256;public int meshes,road_triangles,trees,missing_uv0,shader_errors,tree_missing_uv0,texture2d_count,missing_material_slots;public string urp_version; public bool artistic_gate_approved=false,fps_measured=false;}
 public static void EnsurePipeline(){
  var pipeline=AssetDatabase.LoadAssetAtPath<UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset>("Assets/Settings/R7_QA_URP.asset");
  Need(pipeline!=null,"REBUILD_R7_URP_ASSET_FIRST");GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;
 }
 public static string Repo(){var d=new DirectoryInfo(Application.dataPath);while(d!=null){if(Directory.Exists(Path.Combine(d.FullName,"Tools/Blender")))return d.FullName;d=d.Parent;}throw new InvalidOperationException("REPO_ROOT_MISSING");}
 static void Need(bool ok,string why){if(!ok)throw new InvalidOperationException("R13_BLOCKED:"+why);}
 public static string Sha(string p){using(var f=File.OpenRead(p))using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
 static void Folder(string path){string p="Assets";foreach(string part in path.Substring(7).Split('/')){string next=p+"/"+part;if(!AssetDatabase.IsValidFolder(next))AssetDatabase.CreateFolder(p,part);p=next;}}
 static Texture2D Texture(string kind,string channel){
  string path="Assets/Textures/R13_Pass2/r13_"+kind+"_"+channel+".png";
  var importer=AssetImporter.GetAtPath(path) as TextureImporter;Need(importer!=null,"PBR_MAP_MISSING:"+path);
  bool normal=channel=="normal",srgb=channel=="base";
  if(importer.sRGBTexture!=srgb||importer.textureType!=(normal?TextureImporterType.NormalMap:TextureImporterType.Default)||!importer.mipmapEnabled||importer.wrapMode!=TextureWrapMode.Repeat){
   importer.sRGBTexture=srgb;importer.textureType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;
   importer.mipmapEnabled=true;importer.wrapMode=TextureWrapMode.Repeat;importer.anisoLevel=4;importer.maxTextureSize=2048;importer.SaveAndReimport();
  }
  var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(path);Need(tex!=null,"PBR_TEXTURE_IMPORT_FAILED:"+path+" importer="+importer.textureType);return tex;
 }
 static Material Mat(string key){
  if(key=="sand"||key=="wet_sand"||key=="sand_service"){
   string asset=Dir+"/R13_Pass2Sand.mat";var sand=AssetDatabase.LoadAssetAtPath<Material>(asset);
   var sh=Shader.Find("Resort/R13/Pass2Sand");Need(sh!=null&&sh.isSupported&&!ShaderUtil.ShaderHasError(sh),"SAND_SHADER_FAILED");
   if(sand==null){sand=new Material(sh);AssetDatabase.CreateAsset(sand,asset);}sand.shader=sh;
   sand.SetTexture("_BaseMap",Texture("sand","base"));sand.SetTexture("_WetMap",Texture("wet_sand","base"));sand.SetTexture("_BumpMap",Texture("sand","normal"));EditorUtility.SetDirty(sand);return sand;
  }
  if(key.StartsWith("ocean")){
   string oceanPath=Dir+"/R13_ShoreOcean.mat";var water=AssetDatabase.LoadAssetAtPath<Material>(oceanPath);
   var ocean=Shader.Find("Resort/R13/ShoreOcean");Need(ocean!=null&&ocean.isSupported&&!ShaderUtil.ShaderHasError(ocean),"R13_OCEAN_SHADER_FAILED");
   if(water==null){water=new Material(ocean);AssetDatabase.CreateAsset(water,oceanPath);}water.shader=ocean;water.enableInstancing=true;return water;
  }
  Need(new[]{"mosaic","sand","wet_sand","sand_service","limestone","timber","asphalt","pavement","metal","leaves","soil","baseline","baseline_dark"}.Contains(key),"UNKNOWN_MATERIAL_SEMANTIC:"+key);
  string path=Dir+"/R13_"+key+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
  var shader=Shader.Find("Universal Render Pipeline/Lit");Need(shader!=null&&shader.isSupported,"URP_LIT_UNSUPPORTED");
  if(m==null){m=new Material(shader){name="R13_"+key};AssetDatabase.CreateAsset(m,path);}m.shader=shader;m.enableInstancing=true;
  string map=key=="sand_service"?"sand":key;
  bool textured=new[]{"mosaic","sand","wet_sand","sand_service","limestone","timber","asphalt","pavement"}.Contains(key);
  m.SetColor("_BaseColor",key=="wet_sand"?Color.white:key=="metal"?new Color(.12f,.16f,.17f):key=="leaves"?new Color(.13f,.29f,.10f):key=="soil"?new Color(.12f,.085f,.045f):key=="baseline"?new Color(.72f,.70f,.66f):key=="baseline_dark"?new Color(.20f,.22f,.23f):Color.white);
  m.SetFloat("_Metallic",key=="metal"?.8f:0);m.SetFloat("_Smoothness",key=="metal"?.64f:key=="wet_sand"?.48f:.2f);
  if(textured){m.SetTexture("_BaseMap",Texture(map,"base"));m.SetTexture("_BumpMap",Texture(map,"normal"));m.SetFloat("_BumpScale",.65f);m.EnableKeyword("_NORMALMAP");
   {m.SetTexture("_MetallicGlossMap",Texture(map,"mask"));m.SetFloat("_Smoothness",1);m.EnableKeyword("_METALLICSPECGLOSSMAP");}}
  m.SetFloat("_Cull",key=="leaves"?0:2);EditorUtility.SetDirty(m);return m;
 }
 [MenuItem("Resort/R13 Pass2/Build derived continuous coast")]
 public static void Build(){
  EnsurePipeline();
  string repo=Repo();
  int textureCount=0;
  foreach(string kind in new[]{"mosaic","sand","wet_sand","limestone","timber","asphalt","pavement"})foreach(string channel in new[]{"base","normal","mask"}){Texture(kind,channel);textureCount++;}
  var q=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(repo,"UnityProject/Assets/Architecture/R13_Pass2/R13_Pass2_NATIVE.json")));
  Need(q.status=="R13_NATIVE_FBX_REIMPORT_CONTINUITY_UV_PASS_ART_PENDING"&&q.frame_m.SequenceEqual(new[]{2000,1000})&&q.native_missing_uv0==0,"NATIVE_QA_REQUIRED");
  Need(q.sectors.Length==10&&q.sectors.All(s=>s.native_gate=="PASS_REIMPORT_CONTINUITY_UV"),"COAST_SEAMS_UNTESTED");
  Need(Sha(Path.Combine(repo,"UnityProject/"+Fbx))==q.fbx_sha256,"FBX_HASH_CHANGED");
  Need(AssetDatabase.LoadAssetAtPath<SceneAsset>(Source)!=null,"R12_SCENE_MISSING_REBUILD_R7_TO_R12_FIRST");
  var scene=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);
  var old=scene.GetRootGameObjects().Single(o=>o.name=="R13_OSM_COAST_SECTORS");old.SetActive(false);
  var all=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  var road=all.Single(r=>r.name.StartsWith("GIS_OSM_REAL_MAP_MINUS_50_REPLACED_WAYS"));
  Need(road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"OSM_ROADS_CHANGED");
  Need(all.Count(r=>r.name.StartsWith("R9_TREE_"))==48,"OSM_TREE_POSITIONS_LOST");
  // Replace the earlier continuous surfaces in THIS derived scene only.
  foreach(var r in all.Where(r=>r.name.StartsWith("R10_MOSAIC_")||r.name.StartsWith("R10_PROMENADE_")||r.name.StartsWith("R10_WATER_BREAKING_")||r.name.StartsWith("R9_SAND_REAL_OSM_COAST")||r.name.StartsWith("R9_OCEAN_REAL_OSM_COAST")))r.enabled=false;
  var importer=AssetImporter.GetAtPath(Fbx) as ModelImporter;Need(importer!=null,"NATIVE_FBX_NOT_IMPORTED");
  if(!importer.isReadable){importer.isReadable=true;importer.SaveAndReimport();}
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Fbx);Need(prefab!=null,"FBX_PREFAB_MISSING");
  var root=(GameObject)PrefabUtility.InstantiatePrefab(prefab);root.name="R13_PASS2_OSM_COAST_SECTORS";Folder(Dir);
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
   var furniture=root.GetComponentsInChildren<MeshRenderer>().Where(r=>r.name.StartsWith(prefix)&&new[]{"limestone","timber","asphalt","pavement","metal","leaves","soil"}.Any(k=>r.name==prefix+k||r.name.StartsWith(prefix+k+"_LOD"))).ToArray();
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
  // Derived meshes get UV0 without modifying R9 imports or OSM positions.
  Folder("Assets/Architecture/R13_Pass2/Derived");
  foreach(var r in all.Where(r=>r.name.StartsWith("R9_TREE_")||r.name.StartsWith("R9_URBAN_PAVEMENT_")||r==road)){
   var f=r.GetComponent<MeshFilter>();Need(f!=null&&f.sharedMesh!=null,"DERIVED_MESH_MISSING");
   var mesh=UnityEngine.Object.Instantiate(f.sharedMesh);mesh.name=r.name+"_Pass2UV";
   // FBX node transforms may retain axis conversion; UVs must use world metres.
   var coords=new List<Vector2>();
   foreach(var v in mesh.vertices){var w=f.transform.TransformPoint(v);coords.Add(new Vector2(Vector3.Dot(w,new Vector3(.694658f,0,-.719340f))/2,Vector3.Dot(w,new Vector3(-.719340f,0,-.694658f))/2));}
   mesh.SetUVs(0,coords);
   if(r==road||r.name.StartsWith("R9_URBAN_PAVEMENT_"))Need(coords.Max(v=>v.x)-coords.Min(v=>v.x)>100&&coords.Max(v=>v.y)-coords.Min(v=>v.y)>100,"WORLD_METRIC_PAVEMENT_UV_COLLAPSED");
   string asset="Assets/Architecture/R13_Pass2/Derived/"+mesh.name+".asset";
   if(AssetDatabase.LoadAssetAtPath<Mesh>(asset)!=null)AssetDatabase.DeleteAsset(asset);
   AssetDatabase.CreateAsset(mesh,asset);f.sharedMesh=mesh;
   if(r==road)r.sharedMaterial=Mat("asphalt");
   if(r.name.StartsWith("R9_URBAN_PAVEMENT_")){r.sharedMaterial=Mat("pavement");r.receiveShadows=true;}
  }
  Need(all.Where(r=>r.name.StartsWith("R9_TREE_")).All(r=>r.GetComponent<MeshFilter>().sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0)),"TREE_UV0_FAILED");
  Need(road.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3==3731,"DERIVED_ROADS_CHANGED");
  int treeMissing=all.Count(r=>r.name.StartsWith("R9_TREE_")&&!r.GetComponent<MeshFilter>().sharedMesh.HasVertexAttribute(VertexAttribute.TexCoord0));
  int missingSlots=all.Where(r=>r.enabled&&r.gameObject.activeInHierarchy).Concat(root.GetComponentsInChildren<MeshRenderer>()).SelectMany(r=>r.sharedMaterials).Count(m=>m==null);
  Need(treeMissing==0&&missingSlots==0,"ALL_VISIBLE_MATERIAL_OR_TREE_UV_GATE_FAILED");
  Need(EditorSceneManager.SaveScene(scene,Scene,false),"DERIVED_SCENE_SAVE_FAILED");AssetDatabase.SaveAssets();
  string outdir=Path.Combine(repo,"build/R13_Pass2_QA");Directory.CreateDirectory(outdir);
  File.WriteAllText(Path.Combine(outdir,"R13_Pass2_UnityTechnicalQA.json"),JsonUtility.ToJson(new Report{status="R13_UNITY_TECHNICAL_PASS_ART_PENDING",unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,renderer=SystemInfo.graphicsDeviceType.ToString(),fbx_sha256=q.fbx_sha256,meshes=count,road_triangles=3731,trees=48,missing_uv0=uv,shader_errors=bad,tree_missing_uv0=treeMissing,texture2d_count=textureCount,missing_material_slots=missingSlots,urp_version=UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset).Assembly).version},true));
  Debug.Log("R13_UNITY_NATIVE_PASS meshes="+count+" roads=3731 trees=48 missingUV=0 shaderErrors=0");
 }

}

