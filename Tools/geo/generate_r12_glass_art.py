"""Original tiled commercial glazing art: diffused interiors + daylight reflection.
Stylized light/reflection hints only, NOT actual ray-traced/window transparency.
No generated screenshot / no photographs; textures only.
"""
import math,random,json,hashlib
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"UnityProject/Assets/Textures/R12_Storefronts"
def make(kind,seed):
 rng=random.Random(seed)
 w,h=512,1024
 base=Image.new("RGB",(w,h));p=base.load()
 for y in range(h):
  v=y/h
  for x in range(w):
   u=x/w
   n=rng.randrange(-5,6)
   sheen=.5+.5*math.sin(u*8.7+v*3.6)
   sky=max(0,1-v*.82)
   color=(
     13+int(sky*38+sheen*7+n),
     29+int(sky*62+sheen*9+n),
     37+int(sky*71+sheen*10+n)
   ) if kind=="showcase" else (
     13+int(sky*32+sheen*6+n),
     24+int(sky*49+sheen*8+n),
     34+int(sky*57+sheen*8+n)
   )
   p[x,y]=tuple(max(0,min(255,c)) for c in color)
 d=ImageDraw.Draw(base,"RGBA")
 # Diffused interiors behind reflective glazing: horizontal recesses and
 # wood/stone retail shelving, no photoreal storefront claim.
 if kind=="showcase":
  for k in (340,525,700,845):
   d.rectangle((40,k,480,k+10),fill=(151,103,58,105))
   d.rectangle((43,k+12,480,k+18),fill=(27,20,21,155))
   for x in range(57,477,62):
    height=rng.randint(53,104)
    col=(134+rng.randrange(40),83+rng.randrange(35),51+rng.randrange(34),125)
    d.rounded_rectangle((x,k-height,x+38,k-4),radius=3,fill=col)
  # Recessed warm ceiling lights and vertical illuminated inner wall hints.
  for x in (94,255,423):
   d.ellipse((x-16,140,x+17,173),fill=(255,228,164,100))
   d.line((x,181,x+20,245),fill=(252,200,147,45),width=6)
 else:
  # Architectural reception desk, door vestibule and warm interior strips.
  d.rectangle((105,570,457,780),fill=(48,55,52,110))
  d.rectangle((102,570,464,589),fill=(200,156,104,100))
  d.rectangle((104,747,465,777),fill=(15,20,26,148))
  for x in (95,380):
   d.rectangle((x,155,x+16,640),fill=(164,154,130,49))
  for y in (210,325):
   d.line((55,y,445,y),fill=(168,201,193,55),width=4)
 # Ghost city/reflection layer: glass reflection dominates view from outside.
 reflection=Image.new("RGBA",(w,h),(0,0,0,0))
 r=ImageDraw.Draw(reflection,"RGBA")
 for xx,ww,opacity in ((-65,135,38),(132,57,26),(290,94,24),(446,124,31)):
  r.polygon([(xx,0),(xx+ww,0),(xx+ww-150,h),(xx-150,h)],fill=(225,239,236,opacity))
 for x in (25,176,404):
  r.line((x,0,x+110,h),fill=(209,232,238,18),width=18)
 reflection=reflection.filter(ImageFilter.GaussianBlur(17))
 base=Image.alpha_composite(base.convert("RGBA"),reflection).convert("RGB")
 name="r12_glass_"+kind+".png";path=OUT/name
 base.save(path,optimize=True)
 return {"path":str(path.relative_to(ROOT)).replace("\\","/"),
  "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 outputs=[make("showcase",9272),make("entrance",881)]
 qa={"status":"R12_ORIGINAL_GLASS_REFLECTION_ART_GENERATED",
  "size_px":[512,1024],"textures":outputs,
  "limitations":"Authored diffused facade reflection and interiors, not actual gameplay transparency or physical raytrace."}
 (ROOT/"ArtSource/Previews/R12_GlassArt_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("R12_GLASS_MAPS_PASS",json.dumps({"maps":len(outputs),"bytes":sum(x["bytes"] for x in outputs)}))
if __name__=="__main__":main()
