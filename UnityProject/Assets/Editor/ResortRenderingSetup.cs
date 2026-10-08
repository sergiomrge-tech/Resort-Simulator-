using System;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace ResortSimulator.Editor
{
    /// <summary>
    /// Create and assign a persistent URP renderer/pipeline. Installing the URP
    /// package is not equivalent to enabling URP for the actual game.
    /// Called by the scene generator, never at runtime.
    /// </summary>
    public static class ResortRenderingSetup
    {
        public const string RendererPath = "Assets/Settings/Rendering/ResortForwardRenderer.asset";
        public const string PipelinePath = "Assets/Settings/Rendering/ResortURP.asset";

        [MenuItem("Resort Simulator/00 - Configurar URP Premium")]
        public static void EnsureConfigured()
        {
            EnsureFolder("Assets", "Settings");
            EnsureFolder("Assets/Settings", "Rendering");

            var renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
            if (renderer == null)
            {
                renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
                renderer.name = "ResortForwardRenderer";
                AssetDatabase.CreateAsset(renderer, RendererPath);
            }

            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
            if (pipeline == null)
            {
                pipeline = UniversalRenderPipelineAsset.Create(renderer);
                if (pipeline == null)
                    throw new InvalidOperationException("Unity URP refused to create the pipeline asset.");
                pipeline.name = "ResortURP";
                AssetDatabase.CreateAsset(pipeline, PipelinePath);
            }

            GraphicsSettings.defaultRenderPipeline = pipeline;
            // Do not leave a Built-in / different URP override at the current quality level.
            QualitySettings.renderPipeline = null;
            PlayerSettings.colorSpace = ColorSpace.Linear;
            AssetDatabase.SaveAssets();

            if (GraphicsSettings.currentRenderPipeline != pipeline)
                throw new InvalidOperationException(
                    "Resort URP pipeline was not activated. Inspect Graphics and Quality Settings.");

            Debug.Log("RESORT URP CONFIGURED: " + PipelinePath + " with " + RendererPath);
        }

        private static void EnsureFolder(string parent, string folder)
        {
            string path = parent + "/" + folder;
            if (!AssetDatabase.IsValidFolder(path))
                AssetDatabase.CreateFolder(parent, folder);
        }
    }
}
