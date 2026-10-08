using UnityEngine;

namespace ResortSimulator
{
    /// <summary>Time-of-day lighting only. No weather, economy or skybox dependencies.</summary>
    public sealed class DayNightCycle : MonoBehaviour
    {
        [SerializeField] private Light sun;
        [SerializeField, Range(0f, 24f)] private float hour = 10f;
        [SerializeField, Min(1f)] private float fullDayMinutes = 35f;
        [SerializeField] private bool advanceTime = true;
        [SerializeField] private float daytimeIntensity = 1.35f;
        [SerializeField] private Color daytimeAmbient = new Color(0.56f, 0.63f, 0.71f);
        [SerializeField] private Color nighttimeAmbient = new Color(0.05f, 0.075f, 0.12f);

        public float Hour { get { return hour; } }
        public void SetSun(Light directional) { sun = directional; }
        public void SetHour(float value) { hour = Mathf.Repeat(value, 24f); ApplyLighting(); }

        private void Start()
        {
            if (sun == null) sun = GetComponent<Light>();
            ApplyLighting();
        }

        private void Update()
        {
            if (advanceTime)
            {
                hour = Mathf.Repeat(hour + 24f / (fullDayMinutes * 60f) * Time.deltaTime, 24f);
                ApplyLighting();
            }
        }

        private void ApplyLighting()
        {
            if (sun == null) return;
            float solarElevation = Mathf.Sin((hour - 6f) / 24f * 2f * Mathf.PI);
            float daylight = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(solarElevation * 1.8f + 0.12f));
            sun.transform.rotation = Quaternion.Euler((hour - 6f) * 15f, -28f, 0f);
            sun.intensity = daytimeIntensity * daylight;
            sun.enabled = daylight > 0.005f;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = Color.Lerp(nighttimeAmbient, daytimeAmbient, daylight);
        }
    }
}
