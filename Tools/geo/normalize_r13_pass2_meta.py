"""Deterministic complete Unity importers for Pass2, preserving existing GUIDs."""
from pathlib import Path
import hashlib,re
ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'UnityProject/Assets'
def write(p,template):
 meta=Path(str(p)+'.meta')
 old=meta.read_text(encoding='utf-8-sig') if meta.exists() else ''
 match=re.search(r'^guid: ([a-f0-9]{32})$',old,re.M)
 guid=match.group(1) if match else hashlib.md5(p.relative_to(ROOT).as_posix().encode()).hexdigest()
 s=re.sub(r'^guid: [a-f0-9]{32}$','guid: '+guid,template,count=1,flags=re.M)
 meta.write_text(s,encoding='utf-8',newline='\n')
def main():
 tex=(ASSETS/'Textures/R12_Storefronts/r12_sign_00.png.meta').read_text(encoding='utf-8-sig')
 model=(ASSETS/'Architecture/R13_Coastal/R13_OSM_Coastal_Sectors.fbx.meta').read_text(encoding='utf-8-sig')
 generic='fileFormatVersion: 2\nguid: '+'0'*32+'\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n'
 folder=generic.replace('DefaultImporter:','folderAsset: yes\nDefaultImporter:')
 for directory in [ASSETS/'Textures/R13_Pass2',ASSETS/'Architecture/R13_Pass2']:
  write(directory,folder)
  for p in sorted(directory.glob('*')):
   if p.name.endswith('.meta'):continue
   if p.suffix=='.png':
    s=tex
    if not p.stem.endswith('_base'):s=s.replace('    sRGBTexture: 1','    sRGBTexture: 0',1)
    if p.stem.endswith('_normal'):s=s.replace('  textureType: 0','  textureType: 1',1)
    write(p,s)
   elif p.suffix=='.fbx':write(p,model)
   elif p.is_file():write(p,generic)
 print('R13_PASS2_COMPLETE_IMPORTERS_PASS')
if __name__=='__main__':main()
