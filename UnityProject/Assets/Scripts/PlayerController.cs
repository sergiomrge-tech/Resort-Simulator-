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
            click = Input.GetMouseButtonDown(0);
            mouseDelta = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y")) * 10f;
#endif

            if (escape) SetPointerLocked(false);
            else if (click && !pointerLocked) SetPointerLocked(true);

            if (pointerLocked && viewPivot != null)
            {
                transform.Rotate(0f, mouseDelta.x * mouseSensitivity, 0f);
                pitch = Mathf.Clamp(pitch - mouseDelta.y * mouseSensitivity, -85f, 85f);
                viewPivot.localRotation = Quaternion.Euler(pitch, 0f, 0f);
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

        private void SetPointerLocked(bool locked)
        {
            pointerLocked = locked;
            Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !locked;
        }

        private void OnGUI()
        {
            GUI.Box(new Rect(14, 14, 525, 88),
                "COPACABANA — MAPA REAL (BLOCO GEOGRAFICO)\n" +
                "WASD: andar  |  Shift: correr  |  Espaco: pular  |  Mouse: olhar\n" +
                "Esc: soltar cursor  |  Clique: capturar cursor\n" +
                "© OpenStreetMap contributors — ODbL 1.0. Predios ainda sem fachadas.");
        }
    }
}
