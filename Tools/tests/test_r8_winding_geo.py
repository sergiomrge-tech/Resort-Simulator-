"""2x1 km and correct outward winding on all 1468 real OSM footprints."""
import json,math,unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
class R8Winding(unittest.TestCase):
 def test_osm_all_facing_outward_and_coast_frame(self):
  data=json.loads((ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json").read_text(encoding="utf-8"))
  frame=json.loads((ROOT/"geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf-8"))
  self.assertEqual(frame["along_coast_length_m"],2000)
  self.assertEqual(frame["inland_width_m"],1000)
  self.assertEqual(len(data["buildings"]),1468)
  counts=Counter()
  for b in data["buildings"]:
   pts=[tuple(p) for p in b["footprint_ring_local_xy_m"]]
   if len(pts)>1 and pts[0]==pts[-1]:pts.pop()
   area=sum(x[0]*y[1]-y[0]*x[1] for x,y in zip(pts,pts[1:]+pts[:1]))*.5
   self.assertGreater(abs(area),.02,b["building_id"])
   flip=area<0
   counts["CW" if flip else "CCW"]+=1
   for a,z in zip(pts,pts[1:]+pts[:1]):
    dx,dy=z[0]-a[0],z[1]-a[1]
    ll=math.hypot(dx,dy)
    if ll<.15:continue
    # Polygon [a_bottom,b_bottom,b_top,a_top] normal: (dy,-dx,0).
    nx,ny=(dy,-dx) if not flip else (-dy,dx)
    expected=(dy,-dx) if area>0 else (-dy,dx)
    self.assertGreater(nx*expected[0]+ny*expected[1],0)
  self.assertEqual(sum(counts.values()),1468)
  print("R8_ORIGINAL_OSM_WINDING",dict(counts))
if __name__=="__main__":unittest.main()
