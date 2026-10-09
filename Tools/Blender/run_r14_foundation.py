"""Rebuild missing native R7-R12 in an isolated workspace copy, not old sources.
Windows local helper. It invokes the existing frozen generation/reimport scripts.
"""
from pathlib import Path
import shutil,subprocess,os,sys
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'build/R14_NativeWorkspace'
BLENDER=Path('C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
PYTHON=BLENDER.parent/'5.2/python/bin/python.exe'
def main():
    WORK.mkdir(parents=True,exist_ok=True)
    for name in ('Tools','geo','UnityProject','ArtSource'):
        shutil.copytree(ROOT/name,WORK/name,dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('Library','Temp','Logs','__pycache__','*.blend1','*.png') if name=='ArtSource' else shutil.ignore_patterns('Library','Temp','Logs','__pycache__'))
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'build/r14deps')
    logs=ROOT/'build/R14_QA/foundation';logs.mkdir(exist_ok=True)
    jobs=[('Tools/Blender/generate_r7_buildings.py',['--mode','gallery','--no-render']),
      ('Tools/geo/r7_mask_city_50.py',None),('Tools/Blender/assemble_r7_city_50.py',[]),
      ('Tools/tests/test_r7_exported_fbx_native.py',[]),
      ('Tools/Blender/generate_r8_full_city_facades.py',[]),('Tools/tests/test_r8_native_fbx.py',[]),
      ('Tools/Blender/generate_r9_urban_environment.py',[]),('Tools/tests/test_r9_environment_native.py',[]),
      ('Tools/Blender/generate_r10_coastal_details.py',[]),('Tools/tests/test_r10_coastal_native.py',[]),
      ('Tools/Blender/generate_r11_architectural_detail.py',[]),('Tools/tests/test_r11_architecture_native.py',[]),
      ('Tools/Blender/generate_r12_storefronts.py',[]),('Tools/tests/test_r12_storefront_native.py',[])]
    # Selected 48 true OSM trees and R13 FBX/PBR are copied frozen, not regenerated.
    for i,(script,args) in enumerate(jobs):
        print('R14_FOUNDATION_STAGE',i,script,flush=True)
        cmd=[str(PYTHON),script] if args is None else [str(BLENDER),'--background','--factory-startup','--python-exit-code','1','--python',script,'--',*args,'--no-render'] if 'assemble_r7' in script else [str(BLENDER),'--background','--factory-startup','--python-exit-code','1','--python',script,'--',*args]
        with (logs/(str(i)+'-'+Path(script).stem+'.log')).open('w',encoding='utf-8') as log:
            subprocess.run(cmd,cwd=WORK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('R14_FOUNDATION_READY_ISOLATED',WORK,flush=True)
if __name__=='__main__':main()
