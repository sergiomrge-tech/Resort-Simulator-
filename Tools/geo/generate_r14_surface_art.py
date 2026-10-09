"""Original periodic two-metre PBR maps, seed 14061, no external images."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'UnityProject/Assets/Textures/R14_Urban'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(14061);files=[];size=1024
    y,x=np.mgrid[0:size,0:size]/size
    for key in ('asphalt','sidewalk','curbstone','gutter','stonetile','timber','foliage','granite'):
        grain=rng.normal(0,1,(size,size))
        coarse=np.sin(2*np.pi*x)*np.sin(4*np.pi*y)*.008
        base={'asphalt':.18,'sidewalk':.43,'curbstone':.53,'gutter':.31,
              'stonetile':.49,'timber':.29,'foliage':.22,'granite':.34}[key]
        joint=np.zeros_like(x,dtype=bool)
        if key in ('sidewalk','stonetile'):
            joint=(np.mod(x*4+(np.floor(y*4)%2)*.5,1)<.008)|(np.mod(y*4,1)<.008)
        elif key in ('gutter','curbstone'):
            joint=np.mod(x*2,1)<.006
        height=grain*.000045-joint*.0012
        value=base+grain*(.018 if key=='granite' else .009)+coarse-joint*.08
        if key=='timber':
            value+=.035*np.sin(y*2*np.pi*48+.8*np.sin(x*2*np.pi));height+=.0002*np.sin(y*2*np.pi*48)
        tint=(1.05,1,.91) if key not in ('timber','foliage') else ((1.32,.94,.60) if key=='timber' else (.53,1.28,.43))
        rgb=np.stack([value*c for c in tint],-1)
        dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(4/size)
        dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(4/size)
        normal=np.stack((-dx,-dy,np.ones_like(x)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
        mask=np.zeros((size,size,4));mask[:,:,1]=1
        mask[:,:,3]= {'asphalt':.08,'sidewalk':.13,'curbstone':.16,'gutter':.10,'stonetile':.19,'timber':.25,'foliage':.12,'granite':.27}[key]
        for channel,data in [('base',rgb),('normal',normal*.5+.5),('mask',mask)]:
            p=OUT/f'r14_{key}_{channel}.png'
            Image.fromarray((np.clip(data,0,1)*255).astype('uint8')).save(p)
            files.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[size,size],'meters_per_repeat':[2,2],'kind':channel})
    (OUT/'R14_SURFACE_ART.json').write_text(json.dumps({'author':'Project Resort original procedural artwork','seed':14061,'external_assets':False,'textures':files},indent=2)+'\n')
    print('R14_PBR_GENERATED',len(files))
if __name__=='__main__':main()
