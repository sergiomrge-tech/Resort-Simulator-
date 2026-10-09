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
    s=s.replace('  string source=version=="before"?ResortR14UrbanFinish.Source:ResortR14UrbanFinish.Scene;\n  var scene=EditorSceneManager.OpenScene(source,OpenSceneMode.Single);\n','')
    s=s.replace('public string status,unity_version,gpu,renderer,urp_version;', 'public string status,unity_version,gpu,renderer,urp_version,connector_fbx_sha256,art_fbx_sha256;')
    s=s.replace('unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,',
       'connector_fbx_sha256=ResortR14UrbanFinish.Sha(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/R14_GIS_Urban_Connectors.fbx")),art_fbx_sha256=ResortR14UrbanFinish.Sha(Path.Combine(repo,"UnityProject/Assets/Architecture/R14_Urban/R14_Coastal_Art_Seven_Sectors.fbx")),unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,')
    s=s.replace('status="R14_REAL_UNITY_CAPTURED_ART_PENDING",unity_version=after.unity_version,',
       'status="R14_REAL_UNITY_CAPTURED_ART_PENDING",connector_fbx_sha256=after.connector_fbx_sha256,art_fbx_sha256=after.art_fbx_sha256,unity_version=after.unity_version,')
    s=s.replace('"BEFORE_AFTER_DEVICE_MISMATCH");','"BEFORE_AFTER_DEVICE_MISMATCH");\n  Need(before.connector_fbx_sha256==after.connector_fbx_sha256&&before.art_fbx_sha256==after.art_fbx_sha256,"ASSET_HASH_CHANGED_BETWEEN_CAPTURES");')
    (ROOT/'UnityProject/Assets/Editor/ResortR14UrbanCapture.cs').write_text(s,encoding='utf-8',newline='\n')
if __name__=='__main__':main()
