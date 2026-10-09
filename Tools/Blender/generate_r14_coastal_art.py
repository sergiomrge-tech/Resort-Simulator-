"""R14 original coastal kit for seven previously BASE sectors.
Fictional decor, road/lot guarded envelopes, metric UV, material batches and LOD.
R8 window lattice and frozen building IDs govern additive facade trims.
"""
from pathlib import Path
import sys,json,math,random
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tools/Blender'),str(ROOT/'Tools/geo')]
from r14_geometry import load_domains, Polygon, Point
from generate_r14_urban_connectors import material,sha,OUT
from generate_r13_pass2 import detail_mesh
from generate_r11_architectural_detail import append_prism,area,stable_id
from generate_r7_buildings import choose_buildings
def coast_at_x(coast,x):
    i=max(0,min(len(coast)-2,int(math.floor(x+1000))))
    a,b=coast[i],coast[i+1]
    return a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])
SECTORS=(0,1,2,3,7,8,9)

def tube(buf,a,b,radius,segments=12):
    a=Vector(a);b=Vector(b);axis=(b-a).normalized()
    side=axis.cross(Vector((0,1,0))).normalized();other=axis.cross(side)
    start=len(buf['v'])
    for center in (a,b):
        for i in range(segments):buf['v'].append(tuple(center+radius*(side*math.cos(i*math.tau/segments)+other*math.sin(i*math.tau/segments))))
    buf['f'].append(tuple(start+i for i in reversed(range(segments))))
    buf['f'].append(tuple(start+segments+i for i in range(segments)))
    for i in range(segments):buf['f'].append((start+i,start+(i+1)%segments,start+(i+1)%segments+segments,start+i+segments))

def leaf(buf,center,theta,length,width,up):
    start=len(buf['v'])
    for step in range(9):
        f=step/8;reach=length*f
        w=width*math.sin(math.pi*f)+.001
        z=center[2]+up*f-.35*length*f*f
        for sign in (-1,1):
            buf['v'].append((center[0]+math.cos(theta)*reach-sign*math.sin(theta)*w,
                             center[1]+math.sin(theta)*reach+sign*math.cos(theta)*w,z))
        if step:buf['f'].append((start+2*step-2,start+2*step,start+2*step+1,start+2*step-1))

def main():
    audit,roads,lots,rows,prom,domains,ramps=load_domains();coast=audit['coast_samples']
    assignment=json.loads((ROOT/'geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json').read_text())
    pilot_ids={r['building_id'] for r in choose_buildings(assignment,'gallery',0,50)}
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    keys=('timber','granite','foliage','curbstone','stonetile')
    mats={k:material(k) for k in keys};placements=[];facades=[];coverage=[]
    for s in SECTORS:
        lo=-1000+s*200;hi=lo+200;rng=random.Random(14061+s)
        buffers={k:{'v':[],'f':[]} for k in keys}
        def prism(k,a,t,n,u0,u1,v0,v1,z0,z1):append_prism(buffers[k],a,t,n,u0,u1,v0,v1,z0,z1)
        def valid(a,t,n,u,v):
            envelope=Polygon([(a[0]+t[0]*xx+n[0]*yy,a[1]+t[1]*xx+n[1]*yy) for xx,yy in ((-u,-v),(u,-v),(u,v),(-u,v))])
            return prom.covers(envelope) and not envelope.intersects(roads.buffer(.35)) and not envelope.intersects(lots.buffer(.5))
        for i in range(7):
            x=lo+13+i*26+rng.uniform(-3,3);y=coast_at_x(coast,x)
            slope=coast_at_x(coast,x+.5)-coast_at_x(coast,x-.5)
            length=math.hypot(1,slope);t=(1/length,slope/length);n=(-t[1],t[0]);a=(x,y+27.5)
            if not valid(a,t,n,5,1.1):continue
            # Variable benches: curved back rail with individually manufactured slats.
            width=rng.uniform(1.65,2.05)
            for u in (-width/2+.16,width/2-.24):prism('granite',a,t,n,u,u+.08,-.22,.22,-.03,.43)
            for j in range(5):prism('timber',a,t,n,-width/2,width/2,-.25+j*.10,-.17+j*.10,.43,.48)
            for j in range(4):prism('timber',a,t,n,-width/2,width/2,.26,.33,.59+j*.10,.65+j*.10)
            for u in (-width/2+.1,width/2-.17):prism('granite',a,t,n,u,u+.07,.24,.32,.4,1.02)
            # Open planter and low tropical foliage, held below sightline.
            p=(x+3*t[0],a[1]+3*t[1])
            for u0,u1 in ((-.70,-.60),(.60,.70)):prism('curbstone',p,t,n,u0,u1,-.5,.5,-.03,.44)
            for v0,v1 in ((-.5,-.4),(.4,.5)):prism('curbstone',p,t,n,-.60,.60,v0,v1,-.03,.44)
            prism('granite',p,t,n,-.6,.6,-.4,.4,.34,.37)
            for blade in range(48):
                theta=blade*2.39996;radius=.28*math.sqrt((blade+.5)/48)
                leaf(buffers['foliage'],(p[0]+math.cos(theta)*radius,p[1]+math.sin(theta)*radius,.40),theta,.30+rng.random()*.15,.025,.38+rng.random()*.30)
            q=(x-2.2*t[0],a[1]-2.2*t[1]);tube(buffers['granite'],(*q,-.03),(*q,.79),.22,20)
            for j in range(3):
                u=-3.3-j*.55
                for v in (-.30,.30):prism('granite',a,t,n,u,u+.035,v,v+.035,-.03,.75)
                prism('granite',a,t,n,u,u+.035,-.30,.335,.75,.785)
            lamp=(x-4.6*t[0],a[1]-4.6*t[1]);tube(buffers['granite'],(*lamp,-.03),(*lamp,3.15),.055)
            prism('curbstone',lamp,t,n,-.18,.18,-.18,.18,3.15,3.39)
            prism('granite',lamp,t,n,-.23,.23,-.23,.23,3.39,3.45)
            placements.append({'sector':f'S{s:02d}','kind':'urban_group','xy':list(a),'seed':14061+s,'envelope_uv_m':[5,1.1],'t':t,'n':n,'fictional':True})
        # Two palms per sector, organic swept trunk plus true pinnate leaf geometry.
        for i in range(2):
            x=lo+55+i*88+rng.uniform(-6,6);a=(x,coast_at_x(coast,x)+28.3)
            if not valid(a,(1,0),(0,1),2.0,2.0):continue
            height=5.4+rng.random()*1.2;trunk=[]
            for step in range(13):
                f=step/12;trunk.append((a[0]+.26*f*f,a[1]+.17*math.sin(f*2),-.03+height*f))
            for j in range(12):tube(buffers['timber'],trunk[j],trunk[j+1],.12*(1-j/28),16)
            for frond in range(12):
                theta=frond*math.tau/12+rng.random()*.12;end=trunk[-1];length=1.45+rng.random()*.45
                last=end
                for step in range(1,10):
                    f=step/9;reach=length*f;z=end[2]+.6*f-1.0*f*f
                    center=(end[0]+math.cos(theta)*reach,end[1]+math.sin(theta)*reach,z)
                    tube(buffers['timber'],last,center,.012*(1-f*.6),6);last=center
                    for side in (-1,1):leaf(buffers['foliage'],center,theta+side*1.1,.42*(math.sin(f*math.pi)*.7+.3),.025,-.06)
            placements.append({'sector':f'S{s:02d}','kind':'palm','xy':list(a),'height_m':height,'fictional':True,'envelope_uv_m':[2,2],'t':[1,0],'n':[0,1]})
        # One fictional kiosk: distinct pergola, pitched roof or radial pavilion.
        x=lo+105;sl=coast_at_x(coast,x+.5)-coast_at_x(coast,x-.5);length=math.hypot(1,sl)
        t=(1/length,sl/length);n=(-t[1],t[0]);a=(x,coast_at_x(coast,x)+27.8);style=s%3
        if valid(a,t,n,3.1,1.7):
            for u in (-2.4,2.4):
                for v in (-1.1,1.1):prism('timber',a,t,n,u-.07,u+.07,v-.07,v+.07,-.03,2.55)
            # Service counter opens towards pedestrian corridor, no real branding.
            prism('stonetile',a,t,n,-2.35,2.35,-.9,-.15,-.03,.97)
            prism('granite',a,t,n,-2.45,2.45,-1,-.05,.97,1.04)
            if style==0:
                prism('timber',a,t,n,-2.65,2.65,-1.42,1.42,2.45,2.54)
                for j in range(22):prism('curbstone',a,t,n,-2.75+j*.25,-2.67+j*.25,-1.55,1.55,2.54,2.62)
            elif style==1:
                # Two sloped slabs in real 3D, joined ridge rather than flat decal.
                for v0,v1 in ((-1.55,0),(0,1.55)):
                    b=buffers['stonetile'];start=len(b['v'])
                    for u,v,z in ((-2.8,v0,2.6+.45*(1-abs(v0)/1.55)),(2.8,v0,2.6+.45*(1-abs(v0)/1.55)),(2.8,v1,2.6+.45*(1-abs(v1)/1.55)),(-2.8,v1,2.6+.45*(1-abs(v1)/1.55))):b['v'].append((a[0]+u*t[0]+v*n[0],a[1]+u*t[1]+v*n[1],z))
                    b['f'].append(tuple(start+j for j in range(4)))
            else:
                b=buffers['timber'];start=len(b['v']);b['v'].append((*a,3.1))
                for j in range(24):
                    th=j*math.tau/24;b['v'].append((a[0]+t[0]*2.8*math.cos(th)+n[0]*1.5*math.sin(th),a[1]+t[1]*2.8*math.cos(th)+n[1]*1.5*math.sin(th),2.58))
                for j in range(24):b['f'].append((start,start+1+j,start+1+(j+1)%24))
            placements.append({'sector':f'S{s:02d}','kind':'kiosk','variant':style,'xy':list(a),'fictional':True,'envelope_uv_m':[3.1,1.7],'t':t,'n':n})
        # Coastal R8 backdrop only; use exactly R8 bay/floor/window expressions.
        for row in rows:
            # The R7 pilot has a different architectural lattice. Leave it
            # untouched rather than projecting R8 window trims onto it.
            if row['building_id'] in pilot_ids:continue
            cx,cy=row['centroid_local_xy_m']
            if not lo<=cx<hi or not 42<cy-coast_at_x(coast,cx)<150:continue
            pts=[tuple(p) for p in row['footprint_ring_local_xy_m']]
            if pts[0]==pts[-1]:pts.pop()
            sign=1 if area(pts)>0 else -1;h=max(3,min(100,float(row['height_for_visualization_m'])))
            floors=max(1,min(28,round(h/3.2)));step=h/floors;seed=stable_id(row['building_id']);windows=0
            for a,b in zip(pts,pts[1:]+pts[:1]):
                length=math.dist(a,b)
                if length<5.8:continue
                t=((b[0]-a[0])/length,(b[1]-a[1])/length);n=(sign*t[1],-sign*t[0])
                if n[1]>-.3:continue
                prism('granite',a,t,n,.12,length-.12,.055,.085,.1,.49)
                bays=min(12,max(1,int(length/3.10)));bay_step=length/bays
                is_coast='orla' in row['style_id'] or 'hotel' in row['style_id']
                ww=min(1.35 if is_coast else 1.12,bay_step*.63);wh=max(.62,min(1.75,step*.62))
                for floor in range(1,min(floors,6)):
                    z=max(.53,(floor+.49)*step-wh*.5)
                    if z+wh>h-.38:continue
                    for bay in range(bays):
                        u=(bay+.5)*bay_step
                        # Shallow stone jambs/lintel are within original wall layers;
                        # no protruding balcony duplication and no transparent panes.
                        k='curbstone' if seed%3==0 else 'granite' if seed%3==1 else 'timber'
                        for side in (-1,1):
                            xx=u+side*(ww/2+.15);prism(k,a,t,n,xx-.025,xx+.025,.06,.085,z,z+wh)
                        prism(k,a,t,n,u-ww/2-.16,u+ww/2+.16,.06,.105,z+wh+.015,z+wh+.09)
                        windows+=1
                facades.append({'sector':f'S{s:02d}','osm_id':row['building_id'],'style_id':row['style_id'],'windows':windows,'seed':seed,'lattice':'R8 3.10m bays and 3.2m floors; same window width/height'});break
        names=[]
        for key,buffer in buffers.items():
            if not buffer['f']:continue
            ob=detail_mesh(f'R14_S{s:02d}_art_{key}',buffer,mats[key]);names.append(ob.name)
            if key!='foliage':
                bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('manufactured_edge_radius','BEVEL');m.width=.004;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
            for level,ratio in ((1,.5),(2,.2)):
                lod=ob.copy();lod.data=ob.data.copy();lod.name=ob.name+f'_LOD{level}';bpy.context.collection.objects.link(lod)
                bpy.context.view_layer.objects.active=lod;m=lod.modifiers.new('distance_reduction','DECIMATE');m.ratio=ratio;bpy.ops.object.modifier_apply(modifier=m.name)
        coverage.append({'sector':f'S{s:02d}','material_batches_lod0':names})
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    for ob in meshes:
        bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('export_triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
        old=ob.data;keep=[];seen=set()
        for p in old.polygons:
            key=tuple(sorted(tuple(round(float(c),6) for c in old.vertices[i].co) for i in p.vertices))
            if p.area>1e-7 and key not in seen:keep.append(p);seen.add(key)
        if len(keep)!=len(old.polygons):
            mesh=bpy.data.meshes.new(ob.name+'_clean');mesh.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in keep]);mesh.update()
            for mat in old.materials:mesh.materials.append(mat)
            uv=mesh.uv_layers.new(name='UVMap')
            for new,prior in zip(mesh.polygons,keep):
                for dst,src in zip(new.loop_indices,prior.loop_indices):uv.data[dst].uv=old.uv_layers.active.data[src].uv
            ob.data=mesh
    OUT.mkdir(parents=True,exist_ok=True);fbx=OUT/'R14_Coastal_Art_Seven_Sectors.fbx'
    bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,path_mode='RELATIVE')
    for image in bpy.data.images:
        if image.source=='FILE':image.filepath='//../../UnityProject/Assets/Textures/R14_Urban/'+Path(image.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'ArtSource/Blender/R14_Coastal_Art_Seven_Sectors.blend'))
    q={'status':'R14_ART_GENERATED_NATIVE_PENDING','frame_m':[2000,1000],'source_sha256':audit['source_sha256'],'fbx_sha256':sha(fbx),'meshes':len(meshes),'faces':sum(len(o.data.polygons) for o in meshes),'mesh_faces':{o.name:len(o.data.polygons) for o in meshes},'sectors':coverage,'placements':placements,'facades':facades,'artistic_gate_approved':False,'fps_measured':False}
    (OUT/'R14_ART_NATIVE.json').write_text(json.dumps(q,indent=2)+'\n')
    print('R14_ART_GENERATED',q['meshes'],q['faces'],'groups',len(placements),'facades',len(facades),flush=True)
if __name__=='__main__':main()
