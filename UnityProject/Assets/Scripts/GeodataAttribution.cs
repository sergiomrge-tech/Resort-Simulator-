using UnityEngine;

namespace ResortSimulator
{
    public sealed class GeodataAttribution : MonoBehaviour
    {
        [TextArea] public string source = "© OpenStreetMap contributors — ODbL 1.0";
        public string sourceUrl = "https://www.openstreetmap.org/copyright";
        [TextArea] public string accuracyNotice =
            "Real OSM footprints and roads. Unknown building heights are approximated for geometric preview. " +
            "No DEM, PBR architecture, detailed shore or production-ready resort is included yet.";
    }
}
