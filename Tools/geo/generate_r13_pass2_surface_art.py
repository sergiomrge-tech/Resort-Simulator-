"""Original metric coastal PBR textures. No photographs or external assets.
BaseColor is sRGB; tangent normals and Unity metallic/smoothness are linear.
Run with ordinary Python + numpy/Pillow, before native Blender generation.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'UnityProject/Assets/Textures/R13_Pass2'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(13061)
    files = []
    for kind in ('mosaic', 'sand', 'wet_sand', 'limestone', 'timber', 'asphalt', 'pavement'):
        size = 2048 if kind == 'mosaic' else 1024
        y, x = np.mgrid[0:size, 0:size] / size
        grain = rng.normal(0, 1, (size, size))
        if kind == 'mosaic':
            # Approximately 7cm Portuguese stones, subtly staggered rows.
            row = np.floor(y * 180).astype(int)
            col = np.floor(x * 171 + (row % 2) * .5).astype(int)
            tone = rng.uniform(-.045, .045, (181, 172))[row, col]
            cx = (col + .5 - (row % 2) * .5) / 171
            cy = (row + .5) / 180
            wave = np.sin(2*np.pi*cx) * .075
            dark = np.mod(cy - wave, .305) < .11
            value = np.where(dark, .13, .56) + tone + grain*.004
            joint = (np.mod(x*171 + (row%2)*.5, 1) < .045) | (np.mod(y*180, 1) < .045)
            value = np.where(joint, .40, value)
            rgb = np.stack((value*1.015, value, value*.967), -1)
            height = np.where(joint, 0, .0014) + grain*.00008
            smooth = np.where(dark, .26, .19)
            meters = (12, 12.5)
        else:
            if kind in ('sand','wet_sand'):
                value = (.52 if kind=='sand' else .36) + grain*.010 + .012*np.sin(x*2*np.pi)*np.cos(y*4*np.pi)
                rgb = np.stack((value*1.08, value*.98, value*.81), -1)
                height = grain*.000045 + .00012*np.sin(x*2*np.pi)*np.cos(y*4*np.pi)
                smooth = np.full_like(x, .04 if kind=='sand' else .16)
            elif kind in ('asphalt','pavement'):
                joint=(np.mod(x*4,1)<.012)|(np.mod(y*4,1)<.012)
                macro=np.sin(x*2*np.pi)*np.cos(y*2*np.pi)
                value=(.20 if kind=='asphalt' else .46)+grain*.008+macro*.014
                if kind=='pavement':value=np.where(joint,value*.78,value)
                rgb=np.stack((value*1.02,value,value*.95),-1)
                height=grain*.000025-(joint*.0006 if kind=='pavement' else 0)
                smooth=np.full_like(x,.10 if kind=='asphalt' else .14)
            elif kind == 'limestone':
                value = .64 + grain*.013 + .02*np.sin(x*2*np.pi)*np.sin(y*2*np.pi)
                rgb = np.stack((value*1.05, value, value*.91), -1)
                height = grain*.00008
                smooth = np.full_like(x, .22)
            else:
                value = .32 + .045*np.sin(y*2*np.pi*64 + .8*np.sin(x*2*np.pi)) + grain*.009
                rgb = np.stack((value*1.35, value*.94, value*.60), -1)
                height = .00008*np.sin(y*2*np.pi*64) + grain*.00001
                smooth = np.full_like(x, .30)
            meters = (4, 4) if kind in ('sand','wet_sand') else (2, 2)
        # Periodic derivatives avoid normal seams at the repeated map boundary.
        dx = (np.roll(height,-1,1)-np.roll(height,1,1)) / (2*meters[0]/size)
        dy = (np.roll(height,-1,0)-np.roll(height,1,0)) / (2*meters[1]/size)
        norm = np.stack((-dx, -dy, np.ones_like(x)), -1)
        norm /= np.linalg.norm(norm, axis=-1, keepdims=True)
        packed = np.zeros((size,size,4)); packed[:,:,3] = smooth
        for suffix, data in [('base',rgb), ('normal',norm*.5+.5), ('mask',packed)]:
            path = OUT / f'r13_{kind}_{suffix}.png'
            Image.fromarray((np.clip(data,0,1)*255).astype(np.uint8)).save(path)
            files.append({'path':path.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                          'size':[size,size], 'meters_per_repeat':meters, 'kind':suffix})
    (OUT/'R13_Pass2_SURFACE_ART.json').write_text(json.dumps({'author':'Project Resort procedural original',
        'seed':13061,'external_assets':False,'textures':files}, indent=2)+'\n',encoding='utf-8')
    print('R13_ORIGINAL_PBR_MAPS_PASS',len(files))

if __name__ == '__main__': main()
