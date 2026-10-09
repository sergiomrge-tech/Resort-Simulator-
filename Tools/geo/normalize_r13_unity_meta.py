"""Upgrade R13 authored PBR PNG Unity .meta without changing their GUIDs.

Unity 6000 interprets the old two-line pseudo-meta as a Cubemap (not Texture2D),
so no material can bind it. Reuse the fully versioned TextureImporter already
versioned in R12 and keep the R13 stable per-asset GUID.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"UnityProject/Assets/Textures/R12_Storefronts/r12_sign_00.png.meta"
R13=ROOT/"UnityProject/Assets/Textures/R13_Coastal"
def main():
    original=TEMPLATE.read_text(encoding="utf-8-sig")
    assert "TextureImporter:" in original
    assert "serializedVersion: 13" in original
    assert "textureShape: 1" in original
    assert "textureType: 0" in original
    items=sorted(R13.glob("r13_*.png.meta"))
    assert len(items)==12,(len(items),R13)
    guids=set()
    for file in items:
        old=file.read_text(encoding="utf-8-sig")
        match=re.search(r"(?m)^guid: ([a-f0-9]{32})\s*$",old)
        assert match,(file,old)
        guid=match.group(1)
        assert guid not in guids
        guids.add(guid)
        text=re.sub(r"(?m)^guid: [a-f0-9]{32}$","guid: "+guid,original,count=1)
        # Use RGB PNG authored normal map as an explicitly typed normal map;
        # do not process the data as sRGB or accidentally generate a cubemap.
        is_normal=file.name.endswith("_normal.png.meta")
        is_mask=file.name.endswith("_mask.png.meta")
        if is_normal:
            text=text.replace("    sRGBTexture: 1","    sRGBTexture: 0",1)
            text=text.replace("  textureType: 0","  textureType: 1",1)
        elif is_mask:
            text=text.replace("    sRGBTexture: 1","    sRGBTexture: 0",1)
        file.write_text(text,encoding="utf-8",newline="\n")
        assert file.read_text(encoding="utf-8").count("TextureImporter:")==1
        assert re.search(r"(?m)^guid: "+guid+r"$",file.read_text(encoding="utf-8"))
    # Critical: two-line FBX .meta is imported at Unity's inferred FBX scale,
    # placing the R13 slice tens of kilometres from the existing R12 scene.
    # Freeze the exact metre-scale R12 model importer configuration, preserving
    # only the already assigned R13 stable GUID.
    model_template=ROOT/"UnityProject/Assets/Architecture/R12_Storefronts/R12_StreetLevel_1418_Entrances_Storefronts.fbx.meta"
    model_meta=ROOT/"UnityProject/Assets/Architecture/R13_Coastal/R13_OSM_Coastal_Sectors.fbx.meta"
    original_model=model_meta.read_text(encoding="utf-8-sig")
    model_guid=re.search(r"(?m)^guid: ([a-f0-9]{32})\s*$",original_model)
    assert model_guid
    src=model_template.read_text(encoding="utf-8-sig")
    assert "ModelImporter:" in src and "globalScale: 1" in src and "useFileUnits: 1" in src
    src=re.sub(r"(?m)^guid: [a-f0-9]{32}$","guid: "+model_guid.group(1),src,count=1)
    model_meta.write_text(src,encoding="utf-8",newline="\n")
    print("R13_UNITY_FULL_IMPORTER_META_PASS",len(items),"png",1,"fbx; stable_guids",len(guids)+1,flush=True)
if __name__=="__main__":main()
