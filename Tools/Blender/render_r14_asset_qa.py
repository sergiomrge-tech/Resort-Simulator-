"""Actual Blender asset QA: GIS road + R14 connectors/coastal kit, no Unity claim."""
from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tools/geo'),str(ROOT/'Tools/Blender')]
from r14_geometry import load_domains, nearest_points, Point
from generate_r14_urban_connectors import material,sha
from generate_r9_urban_environment import make,GEO_ROT
from generate_r14_coastal_art import coast_at_x
def main():
    audit,roads,lots,rows,prom,domains,ramps=load_domains()
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    mats={k:material(k) for k in ('asphalt','sidewalk','curbstone','gutter','stonetile','timber','granite','foliage')}
    vs=[v for t in audit['road_triangles'] for v in t];fs=[(i,i+1,i+2) for i in range(0,len(vs),3)]
    make('R14_QA_ORIGINAL_GIS_ROAD_REFERENCE',vs,fs,mats['asphalt'])
    for filename in ('R14_GIS_Urban_Connectors.fbx','R14_Coastal_Art_Seven_Sectors.fbx'):
        bpy.ops.import_scene.fbx(filepath=str(ROOT/'UnityProject/Assets/Architecture/R14_Urban'/filename))
    for ob in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('R14_S')]:
        if '_LOD' in ob.name:ob.hide_render=True;continue
        key=ob.name[8:].replace('art_','');ob.data.materials.clear();ob.data.materials.append(mats[key])
        if key=='foliage':
            # Blender uses genuine leaf mesh; no artificial generated backdrop.
            pass
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.world.use_nodes=True
    background=scene.world.node_tree.nodes.get('Background');background.inputs['Color'].default_value=(.55,.64,.80,1);background.inputs['Strength'].default_value=.65
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.7
    bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-30));sun.data.energy=2.5;sun.data.angle=.12
    bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.lens=32;cam.data.clip_end=4000;scene.camera=cam
    shots=[];out=ROOT/'ArtSource/Previews'
    for s in (1,5,8):
        x=-900+s*200;shore=coast_at_x(audit['coast_samples'],x)
        edge=nearest_points(Point(x,shore+38),roads.boundary)[1]
        local=Vector((edge.x-6,edge.y-3,1.75));target=Vector((edge.x+9,edge.y+2,.18))
        cam.location=GEO_ROT@local;world_target=GEO_ROT@target;cam.rotation_euler=(world_target-cam.location).to_track_quat('-Z','Y').to_euler()
        path=out/f'R14_S{s:02d}_Connectors_RealBlender_AssetQA.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        shots.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'camera_local':list(local),'target_local':list(target),'renderer':'Blender Cycles','scope':'asset inspection; GIS streets + R14; no city or gameplay','resolution':[1600,900]})
    q={'status':'R14_REAL_BLENDER_ASSET_QA_ART_PENDING','blender_version':bpy.app.version_string,'renderer':'Cycles','shots':shots,'connector_fbx_sha256':sha(ROOT/'UnityProject/Assets/Architecture/R14_Urban/R14_GIS_Urban_Connectors.fbx'),'art_fbx_sha256':sha(ROOT/'UnityProject/Assets/Architecture/R14_Urban/R14_Coastal_Art_Seven_Sectors.fbx'),'unity_screenshot':False,'artistic_gate_approved':False}
    (out/'R14_BlenderAssetVisualQA.json').write_text(json.dumps(q,indent=2)+'\n')
    print('R14_REAL_BLENDER_ASSET_QA_PASS',len(shots),flush=True)
if __name__=='__main__':main()
