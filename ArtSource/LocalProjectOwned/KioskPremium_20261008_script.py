import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
root=Path('D:/sergi/Documents/Simulador-predial/FacilityOps')
lib=Path('D:/ProjectResort_AssetLibrary/ProjectOwned/KioskPremium_20261008');lib.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for name in ['Kiosk_Wood','Kiosk_Plaster','Kiosk_Stone','Kiosk_Metal','Kiosk_Steel','Kiosk_Roof','Kiosk_Ceramic']:
 m=bpy.data.materials.new(name);m.diffuse_color=(.7,.65,.55,1);materials[name]=m
# Author in Unity metres; FBX + existing stage root invert X/Z.
def pos(p):return (-p[0],-p[2],p[1])
def finish(o,name,mat,bevel=.008):
 o.name=name;o.data.materials.append(materials[mat]);bpy.context.view_layer.objects.active=o
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Manufactured edges','BEVEL');mod.width=bevel;mod.segments=3
  bpy.ops.object.modifier_apply(modifier=mod.name)
 # World metres on each face, no stretched normalized UVs.
 uv=o.data.uv_layers.new(name='Metres')
 for face in o.data.polygons:
  n=face.normal
  for li in face.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=(v.x,v.y) if abs(n.z)>.5 else ((v.y,v.z) if abs(n.x)>.5 else (v.x,v.z))
 return o
def box(n,p,s,m,bev=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos(p));o=bpy.context.object;o.scale=(s[0],s[2],s[1]);return finish(o,n,m,bev)
def cyl(n,p,r,h,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=h,location=pos(p));return finish(bpy.context.object,n,m,.003)
# Solid substrate and individual teak planks: surface remains at existing 0.14m.
box('Kiosk_DeckFoundation',(0,.035,-3.05),(19,.07,12.9),'Kiosk_Metal')
for i in range(95):box('Kiosk_DeckPlank_%03d'%i,(-9.4+i*.2,.105,-3.05),(.195,.07,12.9),'Kiosk_Wood',.003)
# Contemporary flat roof with deep fascia, timber soffit and expressed beams.
for x in [-4.35,4.35]:
 for z in [1.85,-5.65]:box('Kiosk_Column',(x,1.81,z),(.18,3.34,.18),'Kiosk_Wood')
box('Kiosk_RoofWeatherSkin',(0,3.68,-1.9),(10.2,.12,8.8),'Kiosk_Roof')
for x in [-5.02,5.02]:box('Kiosk_RoofFascia',(x,3.54,-1.9),(.16,.34,8.8),'Kiosk_Metal')
for z in [2.43,-6.23]:box('Kiosk_RoofFascia',(0,3.54,z),(10.2,.34,.16),'Kiosk_Metal')
for z in [1.85,-1.9,-5.65]:box('Kiosk_RoofBeam',(0,3.36,z),(9,.22,.16),'Kiosk_Wood')
for i in range(45):box('Kiosk_SoffitSlat_%02d'%i,(-4.85+i*.22,3.48,-1.9),(.16,.08,8.5),'Kiosk_Wood',.003)
# Continuous service counter; kitchen appliances match the retained gameplay stations.
box('Kiosk_CounterBase',(0,.63,1.2),(8.8,.98,.7),'Kiosk_Plaster')
box('Kiosk_CounterStone',(0,1.15,1.2),(9.2,.06,.85),'Kiosk_Stone')
for i in range(72):box('Kiosk_CounterFlute_%02d'%i,(-4.3+i*.12,.62,1.565),(.065,.9,.045),'Kiosk_Wood',.004)
box('Kiosk_GrillCabinet',(-1.5,.56,-1),(1.2,.84,.7),'Kiosk_Steel')
box('Kiosk_GrillCooktop',(-1.5,1,-1),(1.23,.04,.74),'Kiosk_Metal')
for i in range(12):box('Kiosk_GrillBar',(-2.02+i*.095,1.025,-1),(.028,.015,.53),'Kiosk_Steel',.002)
for x in [-1.82,-1.5,-1.18]:cyl('Kiosk_GrillControl',(x,.87,-.64),.035,.055,'Kiosk_Metal').rotation_euler[0]=math.pi/2
box('Kiosk_Hood',(-1.5,2.62,-1),(1.5,.38,.9),'Kiosk_Steel')
box('Kiosk_HoodFlue',(-1.5,3.13,-1),(.35,.64,.35),'Kiosk_Steel')
box('Kiosk_Freezer',(1.4,.55,-1.2),(1.1,.82,.6),'Kiosk_Plaster')
box('Kiosk_FreezerLid',(1.4,.99,-1.2),(1.15,.065,.65),'Kiosk_Steel')
box('Kiosk_FreezerHandle',(1.4,.94,-.86),(.4,.04,.04),'Kiosk_Metal')
# Back bar with a real aisle, shelves, enclosed storage, sink and tiled backsplash.
box('Kiosk_BackWall',(0,1.52,-5.55),(8.6,2.76,.16),'Kiosk_Plaster')
box('Kiosk_BackCabinets',(0,.57,-5.02),(8.3,.86,.82),'Kiosk_Wood')
box('Kiosk_BackWorktop',(0,1.035,-4.97),(8.4,.06,.94),'Kiosk_Stone')
for x in [-3.6,-2.4,-1.2,0,1.2,2.4,3.6]:
 box('Kiosk_StorageDoor',(x,.58,-4.6),(1.12,.73,.028),'Kiosk_Wood')
 box('Kiosk_StoragePull',(x+.4,.81,-4.56),(.16,.02,.025),'Kiosk_Metal')
for y in [1.65,2.2]:box('Kiosk_BackShelf',(0,y,-5.22),(7.9,.05,.48),'Kiosk_Wood')
# Recessed sink rim plus basin, faucet with spout.
box('Kiosk_SinkBasin',(2.65,1.072,-4.97),(.58,.035,.46),'Kiosk_Metal')
for x in [2.32,2.98]:box('Kiosk_SinkRim',(x,1.095,-4.97),(.035,.026,.53),'Kiosk_Steel')
for z in [-5.23,-4.71]:box('Kiosk_SinkRim',(2.65,1.095,z),(.7,.026,.035),'Kiosk_Steel')
cyl('Kiosk_Faucet',(2.65,1.25,-5.26),.018,.33,'Kiosk_Steel');box('Kiosk_FaucetSpout',(2.65,1.41,-5.15),(.035,.035,.24),'Kiosk_Steel')
# Accessible washroom with doorway instead of a solid decorative cube.
for x in [-9.12,-5.68]:box('Kiosk_WashroomSide',(x,1.53,-7.62),(.16,2.78,3.6),'Kiosk_Plaster')
box('Kiosk_WashroomBack',(-7.4,1.53,-9.34),(3.6,2.78,.16),'Kiosk_Plaster')
for x,w in [(-8.72,.8),(-6.58,1.8)]:box('Kiosk_WashroomFront',(x,1.53,-5.9),(w,2.78,.16),'Kiosk_Plaster')
box('Kiosk_WashroomLintel',(-7.92,2.69,-5.9),(1.34,.46,.16),'Kiosk_Plaster')
box('Kiosk_WashroomRoof',(-7.4,2.99,-7.62),(3.8,.14,3.8),'Kiosk_Metal')
# Ceramic toilet bowl, lid and cistern, washbasin at human scale.
cyl('Kiosk_WCBase',(-8.5,.36,-8.6),.18,.44,'Kiosk_Ceramic')
bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=pos((-8.5,.56,-8.6)));o=bpy.context.object;o.scale=(.23,.33,.16);finish(o,'Kiosk_WCBowl','Kiosk_Ceramic')
box('Kiosk_WCCistern',(-8.5,.88,-9),(.43,.64,.18),'Kiosk_Ceramic',.035)
box('Kiosk_WashBasin',(-6.22,.94,-8.5),(.58,.16,.46),'Kiosk_Ceramic',.06)
cyl('Kiosk_WashFaucet',(-6.22,1.09,-8.65),.018,.19,'Kiosk_Steel')
# Low-rise bevelled thresholds on side accesses, never across NPC aisles.
for x in [-8.4,8.4]:
 box('Kiosk_AccessStep',(x,.045,3.72),(1.8,.09,.65),'Kiosk_Stone')
# Modern exterior bin with recessed lid, away from doors and tables.
for x in [-5.55,5.55]:
 cyl('Kiosk_Bin',(x,.57,2.5),.23,.86,'Kiosk_Metal');cyl('Kiosk_BinRim',(x,1.01,2.5),.245,.045,'Kiosk_Steel')
# Flush downlight housings; emitters are connected to the runtime light pool.
for x in [-3,0,3]:
 for z in [1,-4.2]:cyl('Kiosk_DownlightHousing',(x,3.30,z),.12,.055,'Kiosk_Metal')
# Consolidate static components by material, preserving source objects in the .blend.
bpy.ops.wm.save_as_mainfile(filepath=str(lib/'KioskPremium.blend'))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];count=len(parts)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='KioskShellF02'
# FBX importer preserves metres and authored material names; keep existing GUID/meta.
bpy.ops.export_scene.fbx(filepath=str(root/'Assets/_Game/Resources/Art/Resort/Props/KioskShellF02.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,mesh_smooth_type='FACE',add_leaf_bones=False)
manifest={'license':'Project-owned original geometry','source':'KioskPremium.blend + build_kiosk_premium.py','components':count,'polygons':len(o.data.polygons),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'scale':'1 unit = 1 metre','visual_status':'CANDIDATE_REVIEW until actual Unity capture inspection','preserved':'GUID; seats; station coordinates; stage ranges; source FBX in session backup'}
(lib/'SOURCE.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');print(json.dumps(manifest))
