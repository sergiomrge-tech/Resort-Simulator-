// Builds the already native-validated R5 Unity Editor scene into a
// standalone Windows 64-bit inspection preview, not the final Steam build.
// Run only on a legitimately licensed Unity Editor with Windows build support.
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.SceneManagement;
using ResortSimulator;

public static class ResortR5WindowsPreviewBuild
{
    private const string TechnicalScene =
        "Assets/Scenes/R5_Copacabana_50_Predios_EditorQA.unity";
    private const string RuntimeScene =
        "Assets/Scenes/R5_Copacabana_50_Predios_PreviewWindows.unity";

    public static void Build()
    {
        string projectRoot=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
        string repoRoot=Path.GetFullPath(Path.Combine(projectRoot,".."));
        string exe=Environment.GetEnvironmentVariable("RESORT_R5_WINDOWS_OUTPUT");
        if (string.IsNullOrWhiteSpace(exe))
            exe=Path.Combine(repoRoot,"build/R5_Windows_VisualPreview/Resort_R5_Visual_50_Predios.exe");
        exe=Path.GetFullPath(exe);
        Directory.CreateDirectory(Path.GetDirectoryName(exe));
        string derived=Path.Combine(Application.dataPath,
            "Architecture/R5_Pilot50/R5_Copacabana_50_Fachadas_Derivado.fbx");
        if (!File.Exists(derived))
            throw new InvalidOperationException("R5 50-building georeferenced FBX missing");
        var source=AssetDatabase.LoadAssetAtPath<SceneAsset>(TechnicalScene);
        if(source==null)
            throw new InvalidOperationException("Native-tested R5 QA scene not in project");
        var imported=AssetDatabase.LoadAssetAtPath<GameObject>(
            "Assets/Architecture/R5_Pilot50/R5_Copacabana_50_Fachadas_Derivado.fbx");
        if(imported==null || imported.GetComponentsInChildren<MeshFilter>(true).Length<250)
            throw new InvalidOperationException("R5 model never imported or too few meshes");
        Scene scene=EditorSceneManager.OpenScene(TechnicalScene,OpenSceneMode.Single);
        Camera mainCamera=Camera.main;
        if(mainCamera==null)
            throw new InvalidOperationException("Source R5 QA scene is missing camera");
        if(mainCamera.GetComponent<R5VisualPreviewFlyCamera>()==null)
            mainCamera.gameObject.AddComponent<R5VisualPreviewFlyCamera>();
        if(!AssetDatabase.IsValidFolder("Assets/Scenes"))
            AssetDatabase.CreateFolder("Assets","Scenes");
        if(!EditorSceneManager.SaveScene(scene,RuntimeScene,true))
            throw new InvalidOperationException("Could not save R5 runtime preview scene");
        AssetDatabase.Refresh();
        PlayerSettings.productName="Project Resort - Copacabana R5 Visual Preview";
        PlayerSettings.companyName="Project Resort";
        var build=new BuildPlayerOptions
        {
            scenes=new[]{RuntimeScene},
            locationPathName=exe,
            target=BuildTarget.StandaloneWindows64,
            options=BuildOptions.None
        };
        Debug.Log("RESORT_R5_WINDOWS_PREVIEW_BUILD_START="+exe);
        BuildReport report=BuildPipeline.BuildPlayer(build);
        if(report==null || report.summary.result!=BuildResult.Succeeded
           || !File.Exists(exe))
        {
            string details=report==null?"missing report":report.summary.result.ToString();
            throw new InvalidOperationException("R5 Windows preview build failed: "+details);
        }
        var file=new FileInfo(exe);
        if(file.Length<150000)
            throw new InvalidOperationException("R5 Unity Windows EXE unexpectedly small");
        Debug.Log("RESORT_R5_WINDOWS_PREVIEW_BUILD_PASS bytes="+file.Length+
                  " totalSize="+report.summary.totalSize+
                  " totalTime="+report.summary.totalTime+
                  " exe="+exe);
    }
}
