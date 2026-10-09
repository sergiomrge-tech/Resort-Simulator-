"""Real Blender render of exported R13 assets only; NEVER a Unity screenshot.
The city is deliberately absent in this asset-inspection render.
"""
from pathlib import Path
import sys,json,math,hashlib
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/Blender'))
from generate_r9_urban_environment import GEO_ROT,read_osm,coast_at_x
OUT=ROOT/'ArtSource/Previews'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/Blender/R13_VisualPass2_Coastal_Sectors.blend'))
for ob in list(bpy.data.objects):
    if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True)
    else:ob.hide_render=not ob.name.startswith('R13_S05_') or '_LOD' in ob.name
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.color=(.25,.25,.25)
sun=bpy.data.lights.new('R13_QA_Daylight','SUN');sun.energy=2.1;sun.angle=.035
obj=bpy.data.objects.new('R13_QA_Daylight',sun);scene.collection.objects.link(obj);obj.rotation_euler=(.5,-.6,-.5)
cam_data=bpy.data.cameras.new('R13_Asset_QA');cam=bpy.data.objects.new('R13_Asset_QA',cam_data);scene.collection.objects.link(cam);scene.camera=cam
cam.data.lens=30
coast,_=read_osm();y=coast_at_x(coast,12)
shots=[]
for name,pos,target in [('Furniture',(1,y+34,2.0),(18,y+27.1,.5)),('Mosaic',(16,y+35,4.8),(14,y+30,0))]:
    cam.location=GEO_ROT@Vector(pos);point=GEO_ROT@Vector(target)
    cam.rotation_euler=(point-cam.location).to_track_quat('-Z','Y').to_euler()
    path=OUT/f'R13_Pass2_{name}_RealBlender_AssetQA.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    shots.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'local_position':pos,'local_target':target})
(OUT/'R13_Pass2_BlenderAssetVisualQA.json').write_text(json.dumps({'renderer':'Blender Cycles','blender_version':bpy.app.version_string,'asset_only':True,'unity_capture':False,'art_approved':False,'captures':shots},indent=2)+'\n',encoding='utf-8')
