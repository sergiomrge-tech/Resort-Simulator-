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

public static class ResortR13Pass2Capture {
 [Serializable] class Shot {public string filename,sha256,source_scene,lighting;public Vector3 position,target;public int warmup_frames=5,width=1600,height=900;public float field_of_view=53,near_clip=.15f,far_clip=4000,sun_intensity,sun_shadow_strength;public Vector3 sun_euler;}
 [Serializable] class Report {public string status,unity_version,gpu,renderer,urp_version;public Shot[] captures;public bool artistic_gate_approved=false,fps_measured=false,playmode_water_animation_tested=false;}
 static void Need(bool ok,string why){if(!ok)throw new InvalidOperationException("R13_CAPTURE_BLOCKED:"+why);}
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
   Debug.Log("R13_GPU_FRAME_DIAGNOSTIC file="+Path.GetFileName(path)+" rgbRange="+(maxRgb-minRgb)+" bytes="+new FileInfo(path).Length+" camera="+pos+" target="+target);
   Need(maxRgb-minRgb>60,"EMPTY_FRAME_DIAGNOSTIC_SAVED:"+Path.GetFileName(path));
   Need(new FileInfo(path).Length>50000,"EMPTY_IMAGE");
   return new Shot{filename=Path.GetFileName(path),sha256=ResortR13Pass2Finish.Sha(path),source_scene=scene,lighting=light,position=pos,target=target,sun_intensity=RenderSettings.sun.intensity,sun_shadow_strength=RenderSettings.sun.shadowStrength,sun_euler=RenderSettings.sun.transform.eulerAngles};
  }finally{camera.targetTexture=saved;RenderTexture.active=active;rt.Release();UnityEngine.Object.DestroyImmediate(rt);if(pixels!=null)UnityEngine.Object.DestroyImmediate(pixels);}
 }
 [MenuItem("Resort/R13 Pass2/Capture R12 before, separate batch")]
 public static void RunBefore(){RunVersion("before");}
 [MenuItem("Resort/R13 Pass2/Capture R13 after, separate batch")]
 public static void RunAfter(){RunVersion("after");}
 static void RunVersion(string version){
  ResortR13Pass2Finish.EnsurePipeline();
  Need(version=="before"||version=="after","INVALID_CAPTURE_VERSION");
  // Always obtain the same geographically anchored 200m focus from the
  // R13 scene, but render each scene in an independent Editor process.
  // Reopening two URP scenes in a single process can retain stale Volume
  // settings and cause SetupColorLut assertion / all-black frames.
  var r13=EditorSceneManager.OpenScene(ResortR13Pass2Finish.Scene,OpenSceneMode.Single);
  var renderers=r13.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<MeshRenderer>(true));
  var promenade=renderers.Single(r=>r.name=="R13_S05_mosaic"&&r.gameObject.activeInHierarchy);
  var p=promenade.bounds.center;
  var anchors=new[]{4,5,6}.ToDictionary(s=>s,s=>renderers.Single(r=>r.name=="R13_S"+s.ToString("00")+"_mosaic"&&r.gameObject.activeInHierarchy).bounds.center);
  Need(p.magnitude<2000f,"COASTAL_FBX_IMPORT_SCALE_REGRESSION_100X:"+p);
  Vector3 along=new Vector3(.694658f,0,-.719340f);
  Vector3 sea=new Vector3(.719340f,0,.694658f);
  var views=new[]{
   new {id="walk",pos=p-along*42+Vector3.up*1.65f,target=p+along*28+Vector3.up*1.3f},
   new {id="coast",pos=p+sea*48+Vector3.up*36,target=p+Vector3.up*1.0f},
   new {id="shore",pos=p+sea*24+Vector3.up*1.65f,target=p+sea*90+Vector3.up*.1f}
  };
  string source=version=="before"?ResortR13Pass2Finish.Source:ResortR13Pass2Finish.Scene;
  var scene=EditorSceneManager.OpenScene(source,OpenSceneMode.Single);
  var cam=Camera.main;
  Need(cam!=null&&GraphicsSettings.currentRenderPipeline!=null,"CAMERA_OR_URP_MISSING");
  string repo=ResortR13Pass2Finish.Repo(),dir=Path.Combine(repo,"build/R13_Pass2_QA");
  Directory.CreateDirectory(dir);
  var shots=new List<Shot>();
  foreach(int sector in new[]{4,5,6}){
  var anchor=anchors[sector];var shift=anchor-p;
  foreach(string time in new[]{"day","late"}){
   Need(RenderSettings.sun!=null,"SUN_MISSING");
   RenderSettings.sun.transform.rotation=Quaternion.Euler(time=="day"?50:20,time=="day"?-30:-65,0);
   RenderSettings.sun.shadows=LightShadows.Soft;
   RenderSettings.sun.shadowStrength=.45f;
   RenderSettings.sun.intensity=time=="day"?1.1f:.8f;
   foreach(var v in views)
    shots.Add(Capture(cam,v.pos+shift,v.target+shift,
      Path.Combine(dir,"R13_Pass2_S"+sector.ToString("00")+"_"+version+"_"+time+"_"+v.id+"_RealUnity.png"),source,time));
  }
  }
  Need(shots.Count==18,"PARTIAL_CAPTURES_MISSING");
  File.WriteAllText(Path.Combine(dir,"R13_Pass2_VisualNativeQA_"+version+".json"),
    JsonUtility.ToJson(new Report{
     status="R13_REAL_UNITY_CAPTURE_"+version.ToUpper()+"_ART_PENDING",
     unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
     renderer=SystemInfo.graphicsDeviceType.ToString(),urp_version=UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UniversalRenderPipelineAsset).Assembly).version,captures=shots.ToArray()
    },true));
  Debug.Log("R13_REAL_GPU_CAPTURE_"+version.ToUpper()+"_PASS count="+shots.Count);
 }
 [MenuItem("Resort/R13 Pass2/Assemble verifiable before-after native captures")]
 public static void Assemble(){
  string repo=ResortR13Pass2Finish.Repo(),dir=Path.Combine(repo,"build/R13_Pass2_QA");
  var before=JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(dir,"R13_Pass2_VisualNativeQA_before.json")));
  var after=JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(dir,"R13_Pass2_VisualNativeQA_after.json")));
  Need(before!=null&&after!=null&&before.captures.Length==18&&after.captures.Length==18,
   "NEED_6_BEFORE_AND_6_AFTER_GPU_PNGS");
  Need(before.unity_version==after.unity_version&&before.renderer==after.renderer&&before.gpu==after.gpu&&before.urp_version==after.urp_version,
   "BEFORE_AFTER_DEVICE_MISMATCH");
  foreach(var row in before.captures.Concat(after.captures)){
   string path=Path.Combine(dir,row.filename);
   Need(File.Exists(path)&&ResortR13Pass2Finish.Sha(path)==row.sha256,
    "GPU_PNG_PROVENANCE_MISMATCH:"+row.filename);
  }
  for(int i=0;i<18;i++){
   var a=before.captures[i];var b=after.captures[i];
   Need(a.lighting==b.lighting&&Vector3.Distance(a.position,b.position)<.001f&&
    Vector3.Distance(a.target,b.target)<.001f&&Vector3.Distance(a.sun_euler,b.sun_euler)<.001f&&a.sun_intensity==b.sun_intensity,"CAMERA_LIGHTING_NOT_COMPARABLE:"+i);
  }
  var merged=before.captures.Concat(after.captures).ToArray();
  File.WriteAllText(Path.Combine(dir,"R13_Pass2_VisualNativeQA.json"),
   JsonUtility.ToJson(new Report{
    status="R13_REAL_UNITY_CAPTURED_ART_PENDING",unity_version=after.unity_version,
    gpu=after.gpu,renderer=after.renderer,urp_version=after.urp_version,captures=merged
   },true));
  Debug.Log("R13_REAL_GPU_CAPTURE_PASS count="+merged.Length+" paired_views=18");
 }
}
