using System;
using System.IO;
using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace ResortSimulator
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class PlayerController : MonoBehaviour
    {
        [Header("Primeira pessoa")]
        [SerializeField] private Transform viewPivot;
        [SerializeField, Range(0.1f, 10f)] private float walkSpeed = 4.2f;
        [SerializeField, Range(1f, 4f)] private float sprintMultiplier = 1.8f;
        [SerializeField] private float jumpHeight = 1.15f;
        [SerializeField] private float gravity = -21.0f;
        [SerializeField] private float mouseSensitivity = 0.12f;

        private CharacterController character;
        private float verticalVelocity;
        private float pitch;
        private bool pointerLocked;
        private bool freeFly;

        [Header("QA do mapa geográfico (temporário)")]
        [SerializeField, Min(2f)] private float inspectionFlySpeed = 45f;
        [SerializeField, Min(1f)] private float inspectionSprintMultiplier = 4f;

        public void SetCameraPivot(Transform pivot) { viewPivot = pivot; }

        private void Awake()
        {
            character = GetComponent<CharacterController>();
            if (viewPivot == null)
            {
                var camera = GetComponentInChildren<Camera>();
                if (camera != null)
                    viewPivot = camera.transform.parent;
            }
        }

        private void OnEnable() { SetPointerLocked(true); }
        private void OnDisable() { SetPointerLocked(false); }

        private void Update()
        {
            bool escape = false;
            bool click = false;
            bool run = false;
            bool jump = false;
            bool switchFly = false;
            bool takeScreenshot = false;
            float flyUp = 0f;
            float horizontal = 0f, forward = 0f;
            Vector2 mouseDelta = Vector2.zero;

#if ENABLE_INPUT_SYSTEM
            var keys = Keyboard.current;
            var mouse = Mouse.current;
            if (keys != null)
            {
                horizontal = (keys.dKey.isPressed ? 1f : 0f) - (keys.aKey.isPressed ? 1f : 0f);
                forward = (keys.wKey.isPressed ? 1f : 0f) - (keys.sKey.isPressed ? 1f : 0f);
                run = keys.leftShiftKey.isPressed || keys.rightShiftKey.isPressed;
                jump = keys.spaceKey.wasPressedThisFrame;
                escape = keys.escapeKey.wasPressedThisFrame;
                switchFly = keys.fKey.wasPressedThisFrame;
                takeScreenshot = keys.f12Key.wasPressedThisFrame;
                flyUp = (keys.eKey.isPressed ? 1f : 0f) - (keys.qKey.isPressed ? 1f : 0f);
            }
            if (mouse != null)
            {
                click = mouse.leftButton.wasPressedThisFrame;
                mouseDelta = mouse.delta.ReadValue();
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            horizontal = Input.GetAxisRaw("Horizontal");
            forward = Input.GetAxisRaw("Vertical");
            run = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
            jump = Input.GetKeyDown(KeyCode.Space);
            escape = Input.GetKeyDown(KeyCode.Escape);
            switchFly = Input.GetKeyDown(KeyCode.F);
            takeScreenshot = Input.GetKeyDown(KeyCode.F12);
            flyUp = (Input.GetKey(KeyCode.E) ? 1f : 0f) - (Input.GetKey(KeyCode.Q) ? 1f : 0f);
            click = Input.GetMouseButtonDown(0);
            mouseDelta = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y")) * 10f;
#endif

            if (escape) SetPointerLocked(false);
            else if (click && !pointerLocked) SetPointerLocked(true);

            if (switchFly)
            {
                freeFly = !freeFly;
                character.enabled = !freeFly;
                verticalVelocity = 0f;
            }
            if (takeScreenshot)
                CaptureRealScreenshot();

            if (pointerLocked && viewPivot != null)
            {
                transform.Rotate(0f, mouseDelta.x * mouseSensitivity, 0f);
                pitch = Mathf.Clamp(pitch - mouseDelta.y * mouseSensitivity, -85f, 85f);
                viewPivot.localRotation = Quaternion.Euler(pitch, 0f, 0f);
            }

            if (freeFly)
            {
                // A camera flies through the actual imported city for R1 inspection.
                // No geometry is replaced and CharacterController is disabled only in QA fly mode.
                Vector3 lookDirection = viewPivot != null ? viewPivot.forward : transform.forward;
                Vector3 flyDirection = transform.right * horizontal + lookDirection * forward + Vector3.up * flyUp;
                float speed = inspectionFlySpeed * (run ? inspectionSprintMultiplier : 1f);
                transform.position += Vector3.ClampMagnitude(flyDirection, 1f) * speed * Time.deltaTime;
                return;
            }

            Vector3 direction = transform.right * horizontal + transform.forward * forward;
            direction = Vector3.ClampMagnitude(direction, 1f);
            float targetSpeed = walkSpeed * (run ? sprintMultiplier : 1f);

            if (character.isGrounded && verticalVelocity < 0f)
                verticalVelocity = -2f;
            if (jump && character.isGrounded)
                verticalVelocity = Mathf.Sqrt(jumpHeight * -2f * gravity);
            verticalVelocity += gravity * Time.deltaTime;

            character.Move((direction * targetSpeed + Vector3.up * verticalVelocity) * Time.deltaTime);
        }

        private void CaptureRealScreenshot()
        {
            // Saves pixels captured by a REAL running Unity player. No synthetic previews.
            var folder = Path.Combine(Application.persistentDataPath, "Captures");
            Directory.CreateDirectory(folder);
            string file = Path.Combine(folder, "Copacabana_Unity_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + ".png");
            ScreenCapture.CaptureScreenshot(file);
            Debug.Log("REAL UNITY SCREENSHOT REQUESTED: " + file);
        }

        private void SetPointerLocked(bool locked)
        {
            pointerLocked = locked;
            Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !locked;
        }

        private void OnGUI()
        {
            GUI.Box(new Rect(14, 14, 610, 128),
                "COPACABANA — MALHA GEOGRAFICA REAL (ARTE TEMPORARIA)\n" +
                "Modo: " + (freeFly ? "SOBREVOO QA (sem colisao)" : "CAMINHADA (com colisao)") + " | F: alternar modo\n" +
                "WASD mover | Mouse olhar | Shift acelerar | F12: screenshot real\n" +
                (freeFly ? "Q/E: descer/subir | atravesse o mapa para inspecionar ruas e edificios\n"
                         : "Espaco: pular | Esc: soltar cursor; clique: capturar\n") +
                "© OpenStreetMap contributors — ODbL 1.0. Fachadas finais pendentes.");
        }
    }
}
