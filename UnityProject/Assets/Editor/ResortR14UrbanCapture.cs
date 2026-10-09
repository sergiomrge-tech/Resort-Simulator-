// Actual URP GPU capture only. Both versions share camera and lighting settings.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ResortR14UrbanCapture {
 [Serializable] class Shot {public string filename,sha256,source_scene,lighting;public Vector3 position,target;public int warmup_frames=5,width=1600,height=900;public float field_of_view=53,near_clip=.15f,far_clip=4000,sun_intensity,sun_shadow_strength;public Vector3 sun_euler;}
 [Serializable] class Report {public string status,unity_version,gpu,renderer,urp_version,connector_fbx_sha256,art_fbx_sha256;public Shot[] captures;public bool artistic_gate_approved=false,fps_measured=false,playmode_water_animation_tested=false;}
 static void Need(bool ok,string why){if(!ok)throw new InvalidOperationException("R14_CAPTURE_BLOCKED:"+why);}
 static Shot Capture(Camera camera,Vector3 pos,Vector3 target,string path,string scene,string light){
  camera.transform.position=pos;camera.transform.LookAt(target);camera.fieldOfView=53;camera.nearClipPlane=.15f;camera.farClipPlane=4000;
  var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);var saved=camera.targetTexture;var active=RenderTexture.active;Texture2D pixels=null;
  try {rt.Create();camera.targetTexture=rt;var request=new UniversalRenderPipeline.SingleCameraRequest{destination=rt};
   Need(RenderPipeline.SupportsRenderRequest(camera,request),"URP_RENDER_REQUEST_UNSUPPORTED");
   for(int i=0;i<5;i++)RenderPipeline.SubmitRenderRequest(camera,request);
   RenderTexture.active=rt;pixels=new Texture2D(1600,900,TextureFormat.RGB24,false);pixels.ReadPixels(new Rect(0,0,1600,900),0,0);pixels.Apply(false);
   var colors=pixels.GetPixels32();
   int minRgb=colors.Min(p=>(int)p.r+p.g+p.b),maxRgb=colors.Max(p=>(int)p.r+p.g+p.b);
   File.WriteAllBytes(path,pixels.EncodeToPNG());
   Debug.Log("R14_GPU_FRAME_DIAGNOSTIC file="+Path.GetFileName(path)+" rgbRange="+(maxRgb-minRgb)+" bytes="+new FileInfo(path).Length+" camera="+pos+" target="+target);
   Need(maxRgb-minRgb>60,"EMPTY_FRAME_DIAGNOSTIC_SAVED:"+Path.GetFileName(path));
   Need(new FileInfo(path).Length>50000,"EMPTY_IMAGE");
   return new Shot{filename=Path.GetFileName(path),sha256=ResortR14UrbanFinish.Sha(path),source_scene=scene,lighting=light,position=pos,target=target,sun_intensity=RenderSettings.sun.intensity,sun_shadow_strength=RenderSettings.sun.shadowStrength,sun_euler=RenderSettings.sun.transform.eulerAngles};
  }finally{camera.targetTexture=saved;RenderTexture.active=active;rt.Release();UnityEngine.Object.DestroyImmediate(rt);if(pixels!=null)UnityEngine.Object.DestroyImmediate(pixels);}
 }
 [MenuItem("Resort/R14/Capture R13 before, separate batch")]
 public static void RunBefore(){RunVersion("before");}
 [MenuItem("Resort/R14/Capture R14 after, separate batch")]
 public static void RunAfter(){RunVersion("after");}
 static void RunVersion(string version){
  ResortR14UrbanFinish.EnsurePipeline();
  Need(version=="before"||version=="after","INVALID_CAPTURE_VERSION");
  // One scene per Editor process: avoid stale SRP ColorLut state.
  string source=version=="before"?ResortR14UrbanFinish.Source:ResortR14UrbanFinish.Scene;
  var r13=EditorSceneManager.OpenScene(source,OpenSceneMode.Single);
  var renderers=r13.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true));
  var promenade=renderers.Single(r=>r.name=="R13_S05_mosaic"&&r.gameObject.activeInHierarchy);
  var p=promenade.bounds.center;
  var anchors=new[]{1,4,5,6,8}.ToDictionary(s=>s,s=>renderers.Single(r=>r.name=="R13_S"+s.ToString("00")+"_mosaic"&&r.gameObject.activeInHierarchy).bounds.center);
  Need(p.magnitude<2000f,"COASTAL_FBX_IMPORT_SCALE_REGRESSION_100X:"+p);
  Vector3 along=new Vector3(.694658f,0,-.719340f);
  Vector3 sea=new Vector3(.719340f,0,.694658f);
  // Import handedness differs from Blender: obtain coastal tangent from real world anchors.
  Vector3 tangent=(anchors[6]-anchors[4]).normalized;
  Vector3 outward=Vector3.Cross(Vector3.up,tangent).normalized;
  // Obtain the nearest REAL imported curb vertex for each sector. The
  // temporary FBX instance is removed before either version is rendered.
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Architecture/R14_Urban/R14_GIS_Urban_Connectors.fbx");
  Need(prefab!=null,"CONNECTOR_CAMERA_FBX_MISSING");
  var temp=UnityEngine.Object.Instantiate(prefab);
  var curbAnchors=new Dictionary<int,Vector3>();
  foreach(int sector in new[]{1,5,8}){
   var filter=temp.GetComponentsInChildren<MeshFilter>().Single(f=>f.name=="R14_S"+sector.ToString("00")+"_curbstone");
   var anchor=anchors[sector];
   var candidates=filter.sharedMesh.vertices.Select(v=>filter.transform.TransformPoint(v)).Where(v=>v.y>.10f).ToArray();
   Need(candidates.Length>0,"CURB_TOP_VERTICES_MISSING");
   curbAnchors[sector]=candidates.OrderBy(v=>(new Vector2(v.x-anchor.x,v.z-anchor.z)).sqrMagnitude).First();
  }
  UnityEngine.Object.DestroyImmediate(temp);
  var views=new[]{
   new {id="walk",pos=p-along*42+Vector3.up*1.65f,target=p+along*28+Vector3.up*1.3f},
   new {id="coast",pos=p+sea*48+Vector3.up*36,target=p+Vector3.up*1.0f},
   new {id="shore",pos=p+sea*24+Vector3.up*1.65f,target=p+sea*90+Vector3.up*.1f},
   new {id="pedestrian",pos=p-tangent*42+Vector3.up*1.65f,target=p+tangent*28+Vector3.up*1.3f},
   new {id="city",pos=p-outward*25+Vector3.up*1.65f,target=p-outward*65+Vector3.up*2.0f}
  };
  var cam=Camera.main;
  Need(cam!=null&&GraphicsSettings.currentRenderPipeline!=null,"CAMERA_OR_URP_MISSING");
  string repo=ResortR14UrbanFinish.Repo(),dir=Path.Combine(repo,"build/R14_QA");
  Directory.CreateDirectory(dir);
  var shots=new List<Shot>();
  foreach(int sector in new[]{1,5,8}){
  var anchor=anchors[sector];var shift=anchor-p;
  foreach(string time in new[]{"day","late"}){
   Need(RenderSettings.sun!=null,"SUN_MISSING");
   RenderSettings.sun.transform.rotation=Quaternion.Euler(time=="day"?50:20,time=="day"?-30:-65,0);
   RenderSettings.sun.shadows=LightShadows.Soft;
   RenderSettings.sun.shadowStrength=.45f;
   RenderSettings.sun.intensity=time=="day"?1.1f:.8f;
   foreach(var v in views)
    shots.Add(Capture(cam,v.pos+shift,v.target+shift,
      Path.Combine(dir,"R14_S"+sector.ToString("00")+"_"+version+"_"+time+"_"+v.id+"_RealUnity.png"),source,time));
   var curb=curbAnchors[sector];
   var towardsPromenade=new Vector3(anchor.x-curb.x,0,anchor.z-curb.z).normalized;
   shots.Add(Capture(cam,curb+towardsPromenade*3+Vector3.up*1.65f,curb+Vector3.up*.10f,
     Path.Combine(dir,"R14_S"+sector.ToString("00")+"_"+version+"_"+time+"_curb_RealUnity.png"),source,time));
  }
  }
  Need(shots.Count==36,"PARTIAL_CAPTURES_MISSING");
  File.WriteAllText(Path.Combine(dir,"R14_VisualNativeQA_"+version+".json"),
    JsonUtility.ToJson(new Report{
     status="R14_REAL_UNITY_CAPTURE_"+version.ToUpper()+"_ART_PENDING",
     connector_fbx_sha256=ResortR14UrbanFinish.Sha(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/R14_GIS_Urban_Connectors.fbx")),art_fbx_sha256=ResortR14UrbanFinish.Sha(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/R14_Coastal_Art_Seven_Sectors.fbx")),unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
     renderer=SystemInfo.graphicsDeviceType.ToString(),urp_version=UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UniversalRenderPipelineAsset).Assembly).version,captures=shots.ToArray()
    },true));
  Debug.Log("R14_REAL_GPU_CAPTURE_"+version.ToUpper()+"_PASS count="+shots.Count);
 }
 [MenuItem("Resort/R14/Assemble verifiable before-after native captures")]
 public static void Assemble(){
  string repo=ResortR14UrbanFinish.Repo(),dir=Path.Combine(repo,"build/R14_QA");
  var before=JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(dir,"R14_VisualNativeQA_before.json")));
  var after=JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(dir,"R14_VisualNativeQA_after.json")));
  Need(before!=null&&after!=null&&before.captures.Length==36&&after.captures.Length==36,
   "NEED_36_BEFORE_AND_36_AFTER_GPU_PNGS");
  Need(before.unity_version==after.unity_version&&before.renderer==after.renderer&&before.gpu==after.gpu&&before.urp_version==after.urp_version,
   "BEFORE_AFTER_DEVICE_MISMATCH");
  Need(before.connector_fbx_sha256==after.connector_fbx_sha256&&before.art_fbx_sha256==after.art_fbx_sha256,"ASSET_HASH_CHANGED_BETWEEN_CAPTURES");
  foreach(var row in before.captures.Concat(after.captures)){
   string path=Path.Combine(dir,row.filename);
   Need(File.Exists(path)&&ResortR14UrbanFinish.Sha(path)==row.sha256,
    "GPU_PNG_PROVENANCE_MISMATCH:"+row.filename);
  }
  for(int i=0;i<36;i++){
   var a=before.captures[i];var b=after.captures[i];
   Need(a.lighting==b.lighting&&Vector3.Distance(a.position,b.position)<.001f&&
    Vector3.Distance(a.target,b.target)<.001f&&Vector3.Distance(a.sun_euler,b.sun_euler)<.001f&&a.sun_intensity==b.sun_intensity,"CAMERA_LIGHTING_NOT_COMPARABLE:"+i);
  }
  var merged=before.captures.Concat(after.captures).ToArray();
  File.WriteAllText(Path.Combine(dir,"R14_VisualNativeQA.json"),
   JsonUtility.ToJson(new Report{
    status="R14_REAL_UNITY_CAPTURED_ART_PENDING",connector_fbx_sha256=after.connector_fbx_sha256,art_fbx_sha256=after.art_fbx_sha256,unity_version=after.unity_version,
    gpu=after.gpu,renderer=after.renderer,urp_version=after.urp_version,captures=merged
   },true));
  Debug.Log("R14_REAL_GPU_CAPTURE_PASS count="+merged.Length+" paired_views=36");
 }
}
