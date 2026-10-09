"""Original, fictional generic Portuguese storefront panels for R12 URP.
No product names, no copied logos and no font files distributed.
Rasterizes locally from system fonts; signed final PNG pixels are committed to GitHub.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hashlib,json,math,random
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"UnityProject/Assets/Textures/R12_Storefronts"
LABELS=[
 ("CAFE","CAFE E CONFEITARIA",("24343C","F6DFAD","BB8C4E")),
 ("BOUTIQUE","MODA & ESTILO",("292B34","F5ECE1","B69F84")),
 ("MERCADO","MERCEARIA DE BAIRRO",("23423B","F1EEE3","9EC19A")),
 ("PADARIA","PAES E DOCES",("53382E","F8E2B4","E7B16A")),
 ("GALERIA","ARTE & DESIGN",("2B3D4F","F0EEE6","8EB6C2")),
 ("FARMACIA","SAUDE & BEM ESTAR",("23554D","F0F3E9","9DD6C3")),
 ("HOTEL","HOSPEDAGEM",("283542","F0E1B6","BAA378")),
 ("RESTAURANTE","COZINHA CARIOCA",("382D31","F8ECE1","C18F85")),
 ("SERVICOS","SERVICOS & ESCRITORIOS",("2B4050","EDF0F0","85A4B5")),
 ("CLINICA","ATENDIMENTO ESPECIALIZADO",("2C4850","EFF4F1","89C7C1")),
 ("FLORICULTURA","FLORES & PRESENTES",("354535","F2E8E0","B9B487")),
 ("ATELIE","OFICINA CRIATIVA",("463C48","EFE1ED","B49EC2")),
]
def systemfont(sz,bold=False):
 candidates=[
  Path("C:/Windows/Fonts")/("segoeuib.ttf" if bold else "segoeui.ttf"),
  Path("/usr/share/fonts/truetype/dejavu")/("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
 ]
 for fp in candidates:
  if fp.exists():return ImageFont.truetype(str(fp),sz)
 return ImageFont.load_default()
def rgb(hexcode):
 return tuple(int(hexcode[i:i+2],16) for i in (0,2,4))
def fit_label(draw,label,font_size,maxwidth,bold=True):
 size=font_size
 while size>14:
  f=systemfont(size,bold)
  if draw.textbbox((0,0),label,font=f)[2]<=maxwidth:return f
  size-=1
 return systemfont(14,False)
def image_sign(key,name,desc,colors):
 bg,fg,accent=(rgb(x) for x in colors)
 w,h=1024,256
 im=Image.new("RGB",(w,h))
 pix=im.load()
 r=random.Random(key*11791+113)
 for y in range(h):
  for x in range(w):
   v=r.randint(-5,5)+int(math.sin(x*.021+y*.045)*2)
   pix[x,y]=tuple(min(255,max(0,int(c+v))) for c in bg)
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((8,8,w-9,h-9),radius=12,outline=accent,width=5)
 d.line((25,208,w-25,208),fill=accent,width=3)
 # brass ornament / understated boutique sign embellishment
 for x in (38,w-38):
  d.ellipse((x-7,107,x+7,121),fill=accent)
  d.line((x,82,x,99),fill=accent,width=3)
  d.line((x,129,x,147),fill=accent,width=3)
 f=fit_label(d,name,83,875)
 bbox=d.textbbox((0,0),name,font=f)
 d.text(((w-(bbox[2]-bbox[0]))/2,27-bbox[1]),name,font=f,fill=fg,stroke_width=1,stroke_fill=accent)
 f2=fit_label(d,desc,27,884,False)
 box=d.textbbox((0,0),desc,font=f2)
 d.text(((w-(box[2]-box[0]))/2,159-box[1]),desc,font=f2,fill=accent)
 d.line((70,226,954,226),fill=tuple(int(a*.55+b*.45) for a,b in zip(bg,accent)),width=2)
 path=OUT/f"r12_sign_{key:02d}.png"
 im.save(path,optimize=True)
 return {"name":name,"subtitle":desc,"path":str(path.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 data=[image_sign(i,*item) for i,item in enumerate(LABELS)]
 manifest={"status":"R12_ORIGINAL_SIGN_GRAPHICS_GENERATED",
  "count":len(data),"pixel_size":[1024,256],
  "copyright":"Original generic Portuguese categories; no copied brands or logos.",
  "signs":data}
 p=ROOT/"ArtSource/Previews/R12_SignArt_QA.json"
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("R12_SIGNS_RASTER_PASS",json.dumps({"count":len(data),"total_png_bytes":sum(i["bytes"] for i in data)}))
if __name__=="__main__":main()
