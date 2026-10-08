using UnityEngine;

namespace ResortSimulator
{
    // Temporary geography inspection camera; replace with final player later.
    public sealed class CameraFlyController : MonoBehaviour
    {
        [SerializeField] private float speed = 45f;
        [SerializeField] private float boost = 5f;
        [SerializeField] private float sensitivity = 0.16f;
        private float yaw;
        private float pitch;

        private void Awake()
        {
            yaw = transform.eulerAngles.y;
            pitch = transform.eulerAngles.x;
        }

        private void Update()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetMouseButton(1))
            {
                Cursor.lockState = CursorLockMode.Locked;
                Cursor.visible = false;
                yaw += Input.GetAxisRaw("Mouse X") * sensitivity * 10f;
                pitch -= Input.GetAxisRaw("Mouse Y") * sensitivity * 10f;
                pitch = Mathf.Clamp(pitch, -85f, 85f);
                transform.rotation = Quaternion.Euler(pitch, yaw, 0f);
            }
            else
            {
                Cursor.lockState = CursorLockMode.None;
                Cursor.visible = true;
            }

            Vector3 move = Vector3.zero;
            if (Input.GetKey(KeyCode.W)) move += transform.forward;
            if (Input.GetKey(KeyCode.S)) move -= transform.forward;
            if (Input.GetKey(KeyCode.D)) move += transform.right;
            if (Input.GetKey(KeyCode.A)) move -= transform.right;
            if (Input.GetKey(KeyCode.E)) move += Vector3.up;
            if (Input.GetKey(KeyCode.Q)) move -= Vector3.up;
            float rate = speed * (Input.GetKey(KeyCode.LeftShift) ? boost : 1f);
            transform.position += move.normalized * rate * Time.deltaTime;
#endif
        }

        private void OnGUI()
        {
            GUI.Box(new Rect(12, 12, 490, 100),
                "COSTA CARIOCA — BASE GEOGRÁFICA OSM\n" +
                "WASD mover | Mouse direito olhar | Q/E altitude | Shift acelerar\n" +
                "Prédios: footprints reais; alturas incompletas estimadas\n" +
                "© OpenStreetMap contributors (ODbL 1.0)");
        }
    }
}
