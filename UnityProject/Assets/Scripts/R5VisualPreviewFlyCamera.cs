using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace ResortSimulator
{
    /// <summary>
    /// Camera control for the R5 Windows geography inspection preview only.
    /// Not the final first-person player or campaign character controller.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class R5VisualPreviewFlyCamera : MonoBehaviour
    {
        [SerializeField] private float moveSpeed = 26f;
        [SerializeField] private float sprintMultiplier = 4f;
        [SerializeField] private float mouseSensitivity = 0.14f;
        private float yaw;
        private float pitch;
        private float averageFps;

        private void Awake()
        {
            yaw=transform.eulerAngles.y;
            pitch=transform.eulerAngles.x;
            Application.targetFrameRate=60;
            Cursor.lockState=CursorLockMode.None;
            Cursor.visible=true;
        }

        private void Update()
        {
            bool orbit=false;
            Vector2 delta=Vector2.zero;
            Vector3 directional=Vector3.zero;
            bool sprint=false;
            bool exit=false;
            bool fullscreen=false;
#if ENABLE_LEGACY_INPUT_MANAGER
            orbit=Input.GetMouseButton(1);
            delta=new Vector2(Input.GetAxisRaw("Mouse X"),Input.GetAxisRaw("Mouse Y"))*11f;
            if (Input.GetKey(KeyCode.W)) directional.z+=1;
            if (Input.GetKey(KeyCode.S)) directional.z-=1;
            if (Input.GetKey(KeyCode.D)) directional.x+=1;
            if (Input.GetKey(KeyCode.A)) directional.x-=1;
            if (Input.GetKey(KeyCode.E)) directional.y+=1;
            if (Input.GetKey(KeyCode.Q)) directional.y-=1;
            sprint=Input.GetKey(KeyCode.LeftShift)||Input.GetKey(KeyCode.RightShift);
            exit=Input.GetKeyDown(KeyCode.Escape);
            fullscreen=Input.GetKeyDown(KeyCode.F11);
#elif ENABLE_INPUT_SYSTEM
            var k=Keyboard.current;
            var m=Mouse.current;
            if (m!=null)
            {
                orbit=m.rightButton.isPressed;
                delta=m.delta.ReadValue();
            }
            if(k!=null)
            {
                if(k.wKey.isPressed)directional.z+=1;
                if(k.sKey.isPressed)directional.z-=1;
                if(k.dKey.isPressed)directional.x+=1;
                if(k.aKey.isPressed)directional.x-=1;
                if(k.eKey.isPressed)directional.y+=1;
                if(k.qKey.isPressed)directional.y-=1;
                sprint=k.leftShiftKey.isPressed||k.rightShiftKey.isPressed;
                exit=k.escapeKey.wasPressedThisFrame;
                fullscreen=k.f11Key.wasPressedThisFrame;
            }
#endif
            if (exit) Application.Quit();
            if (fullscreen) Screen.fullScreen=!Screen.fullScreen;
            Cursor.lockState=orbit?CursorLockMode.Locked:CursorLockMode.None;
            Cursor.visible=!orbit;
            if (orbit)
            {
                yaw+=delta.x*mouseSensitivity;
                pitch=Mathf.Clamp(pitch-delta.y*mouseSensitivity,-84f,84f);
                transform.rotation=Quaternion.Euler(pitch,yaw,0);
            }
            if (directional.sqrMagnitude>0f)
            {
                var horizontal=transform.TransformDirection(new Vector3(directional.x,0,directional.z));
                horizontal.y=0;
                Vector3 move=(horizontal+Vector3.up*directional.y).normalized;
                transform.position+=move*moveSpeed*(sprint?sprintMultiplier:1f)*Time.unscaledDeltaTime;
            }
            float current=1f/Mathf.Max(.0001f,Time.unscaledDeltaTime);
            averageFps=Mathf.Lerp(averageFps,current,.04f);
        }

        private void OnGUI()
        {
            const int width=600;
            float x=14,y=12;
            GUI.Box(new Rect(x,y,width,110),
                "PROJECT RESORT — R5 | INSPEÇÃO VISUAL (NÃO É A VERSÃO FINAL)\n"+
                "50 prédios procedurais no mapa OSM; 1.418 volumes antigos ainda sem fachada premium\n"+
                "WASD mover | Botão direito + mouse olhar | Q/E altura | Shift acelerar | F11 tela cheia");
            GUI.Label(new Rect(x+12,y+84,300,22),"FPS instantâneo aproximado: "+
                      averageFps.ToString("0")+" (não equivale a benchmark)");
            if (GUI.Button(new Rect(Screen.width-136,14,122,40),"SAIR  (Esc)"))
                Application.Quit();
        }
    }
}
