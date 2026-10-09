"""R5 Windows preview source verification, without fabricating cloud-built EXE."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"UnityProject/Assets"
SCRIPT=ASSETS/"Scripts/R5VisualPreviewFlyCamera.cs"
META=Path(str(SCRIPT)+".meta")
SCENE=ASSETS/"Scenes/R5_Copacabana_50_Predios_PreviewWindows.unity"
BUILDER=ASSETS/"Editor/ResortR5WindowsPreviewBuild.cs"
README=ROOT/"docs/arte/R5_WINDOWS_PREVIEW_EXECUTAVEL.md"

class R5WindowsSourceTests(unittest.TestCase):
    def test_dedicated_preview_scene_references_real_runtime_controller_guid(self):
        text=META.read_text(encoding="utf-8")
        m=re.search(r"guid:\s*([a-f0-9]{32})",text)
        self.assertIsNotNone(m)
        scene=SCENE.read_text(encoding="utf-8")
        self.assertIn(m.group(1),scene)
        self.assertIn("R5 Native Unity Camera",scene)
        self.assertGreater(len(scene),40000)
        self.assertTrue(Path(str(SCENE)+".meta").exists())
    def test_camera_supports_wasd_vertical_and_exit_without_phase2(self):
        source=SCRIPT.read_text(encoding="utf-8")
        for phrase in ("KeyCode.W","KeyCode.A","KeyCode.S","KeyCode.D",
                       "KeyCode.Q","KeyCode.E","KeyCode.F11",
                       "Application.Quit","InputSystem","CursorLockMode"):
            self.assertIn(phrase,source)
        self.assertIn("NÃO É A VERSÃO FINAL",source)
    def test_build_targets_only_windows_and_preserves_original_qa_scene(self):
        source=BUILDER.read_text(encoding="utf-8")
        self.assertIn("BuildTarget.StandaloneWindows64",source)
        self.assertIn("EditorSceneManager.SaveScene(scene,RuntimeScene,true)",source)
        self.assertIn("BuildReport",source)
        self.assertIn("RESORT_R5_WINDOWS_PREVIEW_BUILD_PASS",source)
        self.assertIn("RESORT_R5_WINDOWS_OUTPUT",source)
        self.assertTrue((ASSETS/"Scenes/R5_Copacabana_50_Predios_EditorQA.unity").exists())
    def test_build_evidence_is_honest_about_player_gui_and_art_limitations(self):
        doc=README.read_text(encoding="utf-8")
        self.assertIn("af88b840e599661ac63fc10ae27ac77dd97cd46b44df8a7ce60eb0dcfacfc99e",doc)
        self.assertIn("headless",doc)
        self.assertIn("gate visual não foi aprovado",doc)
        self.assertIn("D:\\ProjectResort_Visual_Test_R5",doc)
        self.assertTrue((ASSETS/"Architecture/R5_Pilot50/R5_Copacabana_50_Fachadas_Derivado.fbx").exists())

if __name__=="__main__":
    unittest.main()
