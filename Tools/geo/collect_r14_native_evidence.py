"""Publish only scoped R14 scene/capture evidence from isolated native work.
Raw Unity logs remain ignored (may contain machine/licensing information).
"""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'build/R14_NativeWorkspace'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    qdir=WORK/'build/R14_QA';out=ROOT/'ArtSource/Previews'
    for p in qdir.glob('R14_*'):
        if p.suffix in ('.json','.png'):shutil.copy2(p,out/p.name)
    for p in (WORK/'UnityProject/Assets/Scenes').glob('R14_Copacabana_*'):
        shutil.copy2(p,ROOT/'UnityProject/Assets/Scenes'/p.name)
    mats=WORK/'UnityProject/Assets/Materials/R14_Urban'
    shutil.copytree(mats,ROOT/'UnityProject/Assets/Materials/R14_Urban',dirs_exist_ok=True)
    shutil.copy2(mats.with_suffix('.meta'),ROOT/'UnityProject/Assets/Materials/R14_Urban.meta')
    # Unity emits trailing spaces in blank YAML values. Normalize whitespace
    # only, preserving IDs/references/values; retain raw scene hash separately.
    formatted=list((ROOT/'UnityProject/Assets/Materials/R14_Urban').glob('*'))
    formatted+=list((ROOT/'UnityProject/Assets/Scenes').glob('R14_Copacabana_*'))
    formatted.append(ROOT/'UnityProject/Assets/Materials/R14_Urban.meta')
    for p in formatted:
        if p.is_file():p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8-sig').splitlines())+'\n',encoding='utf-8',newline='\n')
    files=[]
    for directory in ('Tools/Blender','Tools/geo','Tools/tests','UnityProject/Assets/Editor','UnityProject/Assets/Architecture/R14_Urban','UnityProject/Assets/Textures/R14_Urban','UnityProject/Assets/Materials/R14_Urban','UnityProject/Assets/Scenes'):
        files.extend(p for p in (ROOT/directory).glob('*') if p.is_file() and ('r14' in p.name.lower()) and p.suffix in ('.py','.cs','.json','.fbx','.png','.unity','.mat','.meta'))
    gates=[]
    for name in ('source-audit.log','connectors-reimport-slots.log','art-reimport-slots-final.log','blender-render-distances.log','unity-final-Build.log','unity-curb-reviewed-Assemble.log'):
        p=ROOT/'build/R14_QA'/name
        if not p.exists():continue
        raw=p.read_bytes();encoding='utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
        for line in raw.decode(encoding,errors='replace').splitlines():
            if line.startswith(('R14_NATIVE_REIMPORT_PASS','R14_ART_NATIVE_PASS','R14_UNITY_NATIVE_PASS','R14_REAL_GPU_CAPTURE','R14_REAL_BLENDER_ASSET_QA_PASS','R14_SOURCE_READ_ONLY_PASS')):
                gates.append({'log':p.relative_to(ROOT).as_posix(),'gate':line})
    q={'status':'R14_NATIVE_BLENDER_UNITY_EXECUTED_ART_PENDING','machine_scope':'isolated Resort workspace copy; no gameplay checkout',
       'files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(files))},
       'gates':gates,'raw_logs_published':False,'fps_measured':False,'gameplay_integrated':False,
       'scene_native_unformatted_sha256':sha(WORK/'UnityProject/Assets/Scenes/R14_Copacabana_Urban_Connectors.unity'),
       'scene_committed_sha256':sha(ROOT/'UnityProject/Assets/Scenes/R14_Copacabana_Urban_Connectors.unity'),
       'scene_note':'Native R14 scene depends on generated R7-R13 assets; reconstruct with full chain before opening in clean checkout.'}
    (out/'R14_NativeExecution.json').write_text(json.dumps(q,indent=2)+'\n')
    print('R14_SANITIZED_NATIVE_EVIDENCE',len(q['files_sha256']),len(gates))
if __name__=='__main__':main()
