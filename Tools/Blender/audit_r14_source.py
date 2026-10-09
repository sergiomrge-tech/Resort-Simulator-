"""Read-only original GIS extraction. Never save the opened source blend."""
from pathlib import Path
import bpy, json, hashlib, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/Blender'))
from generate_r9_urban_environment import read_osm, coast_at_x

def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    protected=['ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend',
      'UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx',
      'geo/data/copacabana.osm.gz','geo/procedural/R4_SOURCE_FRAME.json',
      'geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json','geo/procedural/R9_VEGETATION_SELECTED.json',
      'ArtSource/Blender/R13_VisualPass2_Coastal_Sectors.blend',
      'UnityProject/Assets/Architecture/R13_Pass2/R13_VisualPass2_Coastal_Sectors.fbx']
    hashes={p:sha(p) for p in protected}
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/protected[0]))
    city=next(o for o in bpy.data.objects if o.type=='MESH' and len(o.data.polygons)==26764)
    roads=[]
    for p in city.data.polygons:
        if 'road' in city.data.materials[p.material_index].name.lower():
            roads.append([list(city.data.vertices[i].co) for i in p.vertices])
    assert len(roads)==3731 and all(len(p)==3 for p in roads)
    coast,_=read_osm()
    q={'status':'READ_ONLY_ORIGINAL_GIS_EXTRACTED','source_sha256':hashes,
       'road_triangles':roads,'road_z_range_m':[min(v[2] for p in roads for v in p),max(v[2] for p in roads for v in p)],
       'coast_samples':[[x,coast_at_x(coast,x)] for x in range(-1000,1001)],
       'frame_m':[2000,1000],'crs':'EPSG:32723','angle_degrees':46,
       'footprints':1468,'original_trees':48,'blender_version':bpy.app.version_string,
       'coordinate_basis':'original mesh vertices in frozen local frame, as R13 native road gate'}
    out=ROOT/'ArtSource/Previews/R14_SourceAudit.json'
    out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    assert all(sha(p)==h for p,h in hashes.items())
    print('R14_SOURCE_READ_ONLY_PASS',len(roads),q['road_z_range_m'],flush=True)
if __name__=='__main__':main()
