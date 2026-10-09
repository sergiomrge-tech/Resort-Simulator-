"""Complete serialized R14 importers, stable GUIDs; earlier metas read only."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/geo'))
from normalize_r13_pass2_meta import write,ASSETS
def main():
    tex=(ASSETS/'Textures/R13_Pass2/r13_asphalt_base.png.meta').read_text(encoding='utf-8-sig')
    model=(ASSETS/'Architecture/R13_Pass2/R13_VisualPass2_Coastal_Sectors.fbx.meta').read_text(encoding='utf-8-sig')
    generic='fileFormatVersion: 2\nguid: '+'0'*32+'\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n'
    folder=generic.replace('DefaultImporter:','folderAsset: yes\nDefaultImporter:')
    for directory in (ASSETS/'Textures/R14_Urban',ASSETS/'Architecture/R14_Urban'):
        write(directory,folder)
        for p in sorted(directory.iterdir()):
            if p.name.endswith('.meta'):continue
            if p.suffix=='.png':
                s=tex
                if not p.stem.endswith('_base'):s=s.replace('    sRGBTexture: 1','    sRGBTexture: 0',1)
                if p.stem.endswith('_normal'):s=s.replace('  textureType: 0','  textureType: 1',1)
                write(p,s)
            elif p.suffix=='.fbx':write(p,model)
            elif p.is_file():write(p,generic)
    for p in (ASSETS/'Editor').glob('ResortR14*.cs'):
        write(p,'fileFormatVersion: 2\nguid: '+'0'*32+'\nMonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
    print('R14_COMPLETE_STABLE_IMPORTERS_PASS')
if __name__=='__main__':main()
