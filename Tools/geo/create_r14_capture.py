"""Create a scoped R14 capture from frozen R13 capturer, preserving GPU routine."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    source=(ROOT/'UnityProject/Assets/Editor/ResortR13Pass2Capture.cs').read_text(encoding='utf-8')
    s=source.replace('ResortR13Pass2Capture','ResortR14UrbanCapture').replace('ResortR13Pass2Finish','ResortR14UrbanFinish')
    s=s.replace('R13_Pass2_','R14_').replace('build/R13_Pass2_QA','build/R14_QA')
    s=s.replace('R13_CAPTURE_','R14_CAPTURE_').replace('R13_REAL_','R14_REAL_').replace('R13_GPU_','R14_GPU_')
    s=s.replace('Resort/R13 Pass2/','Resort/R14/').replace('Capture R12 before','Capture R13 before').replace('Capture R13 after','Capture R14 after')
    start=s.index('  // Always obtain the same')
    end=s.index('  var renderers=',start)
    s=s[:start]+'''  // One scene per Editor process: avoid stale SRP ColorLut state.
  string source=version=="before"?ResortR14UrbanFinish.Source:ResortR14UrbanFinish.Scene;
  var r13=EditorSceneManager.OpenScene(source,OpenSceneMode.Single);
'''+s[end:]
    s=s.replace('new[]{4,5,6}.ToDictionary','new[]{1,4,5,6,8}.ToDictionary')
    s=s.replace('foreach(int sector in new[]{4,5,6})','foreach(int sector in new[]{1,5,8})')
    s=s.replace('  var views=new[]{','''  // Obtain the nearest REAL imported curb vertex for each sector. The
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
  var views=new[]{''')
    s=s.replace('  }\n  }\n  Need(shots.Count==30', '''   var curb=curbAnchors[sector];
   var towardsPromenade=new Vector3(anchor.x-curb.x,0,anchor.z-curb.z).normalized;
   shots.Add(Capture(cam,curb+towardsPromenade*3+Vector3.up*1.65f,curb+Vector3.up*.10f,
     Path.Combine(dir,"R14_S"+sector.ToString("00")+"_"+version+"_"+time+"_curb_RealUnity.png"),source,time));
  }
  }
  Need(shots.Count==36''')
    s=s.replace('captures.Length==30','captures.Length==36').replace('for(int i=0;i<30;i++)','for(int i=0;i<36;i++)').replace('paired_views=30','paired_views=36')
    s=s.replace('NEED_6_BEFORE_AND_6_AFTER_GPU_PNGS','NEED_36_BEFORE_AND_36_AFTER_GPU_PNGS')
    s=s.replace('  string source=version=="before"?ResortR14UrbanFinish.Source:ResortR14UrbanFinish.Scene;\n  var scene=EditorSceneManager.OpenScene(source,OpenSceneMode.Single);\n','')
    s=s.replace('public string status,unity_version,gpu,renderer,urp_version;', 'public string status,unity_version,gpu,renderer,urp_version,connector_fbx_sha256,art_fbx_sha256;')
    s=s.replace('unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,',
       'connector_fbx_sha256=ResortR14UrbanFinish.Sha(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/R14_GIS_Urban_Connectors.fbx")),art_fbx_sha256=ResortR14UrbanFinish.Sha(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/R14_Coastal_Art_Seven_Sectors.fbx")),unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,')
    s=s.replace('status="R14_REAL_UNITY_CAPTURED_ART_PENDING",unity_version=after.unity_version,',
       'status="R14_REAL_UNITY_CAPTURED_ART_PENDING",connector_fbx_sha256=after.connector_fbx_sha256,art_fbx_sha256=after.art_fbx_sha256,unity_version=after.unity_version,')
    s=s.replace('"BEFORE_AFTER_DEVICE_MISMATCH");','"BEFORE_AFTER_DEVICE_MISMATCH");\n  Need(before.connector_fbx_sha256==after.connector_fbx_sha256&&before.art_fbx_sha256==after.art_fbx_sha256,"ASSET_HASH_CHANGED_BETWEEN_CAPTURES");')
    (ROOT/'UnityProject/Assets/Editor/ResortR14UrbanCapture.cs').write_text(s,encoding='utf-8',newline='\n')
if __name__=='__main__':main()
