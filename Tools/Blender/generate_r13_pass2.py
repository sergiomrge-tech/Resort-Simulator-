"""Pass2 derived layer: metric PBR surfaces across 2km and S04/S05/S06 details.
Fork of the frozen R13 checkpoint; writes only R13_Pass2 outputs.
--sectors controls detail batches; all ten surface sectors are always generated.
"""
from pathlib import Path
import sys, json, math, argparse, hashlib
import bpy
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/Blender'))
from generate_r9_urban_environment import read_osm, coast_at_x, make, GEO_ROT, FRAME
from generate_r11_architectural_detail import append_prism, area, stable_id
from generate_r10_coastal_details import band
OUT = ROOT/'UnityProject/Assets/Architecture/R13_Pass2'
TEXTURES = ROOT/'UnityProject/Assets/Textures/R13_Pass2'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def material(key, rgb, texture=None, rough=.7, metal=0):
    m=bpy.data.materials.new('R13_'+key); m.use_nodes=True; m.diffuse_color=(*rgb,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if texture:
        image=m.node_tree.nodes.new('ShaderNodeTexImage'); image.image=bpy.data.images.load(str(TEXTURES/f'r13_{texture}_base.png'))
        m.node_tree.links.new(image.outputs['Color'],bs.inputs['Base Color'])
        image=m.node_tree.nodes.new('ShaderNodeTexImage'); image.image=bpy.data.images.load(str(TEXTURES/f'r13_{texture}_normal.png'))
        image.image.colorspace_settings.name='Non-Color'
        normal=m.node_tree.nodes.new('ShaderNodeNormalMap')
        m.node_tree.links.new(image.outputs['Color'],normal.inputs['Color']); m.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    return m

def strip(name, coast, lo, hi, a, b, z, mat, uvmeters, subdivisions=1):
    vs=[]; fs=[]; uvs=[]
    for i in range((hi-lo)+1):
        x=lo+i; y=coast_at_x(coast,x)
        for j in range(subdivisions+1):
            low=(-1150-y) if 'ocean_far' in name else a
            offset=low+(b-low)*j/subdivisions
            # Dry sand gently rises inland; no displacement at shared boundaries.
            zz=z + (.008*math.sin(x*.063)*math.sin(math.pi*(offset-a)/(b-a)) if 'sand' in name else 0)
            vs.append((x,y+offset,zz)); uvs.append((x/uvmeters[0], (offset-25.5 if 'mosaic' in name else offset)/uvmeters[1]))
        if i:
            n=i*(subdivisions+1)
            for j in range(subdivisions): fs.append((n-subdivisions-1+j,n+j,n+j+1,n-subdivisions+j))
    ob=make(name,vs,fs,mat)
    for loop in ob.data.loops: ob.data.uv_layers.active.data[loop.index].uv=uvs[loop.vertex_index]
    return ob

def detail_mesh(name, buffer, mat):
    ob=make(name,buffer['v'],buffer['f'],mat)
    # Face projection in metres; no stretched UVs on vertical furniture/facades.
    for face in ob.data.polygons:
        normal=face.normal; axis=Vector((1,0,0)) if abs(normal.z)>.8 else Vector((-normal.y,normal.x,0)).normalized()
        across=normal.cross(axis)
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            ob.data.uv_layers.active.data[li].uv=(v.dot(axis)/2,v.dot(across)/2)
    return ob

def main():
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser=argparse.ArgumentParser(); parser.add_argument('--sectors',default='4,5,6')
    refined={int(s) for s in parser.parse_args(argv).sectors.split(',')}
    assert refined and refined <= set(range(10))
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    assert FRAME['along_coast_length_m']==2000 and FRAME['inland_width_m']==1000
    coast,_=read_osm()
    mats={k:material(k,c,t,r,m) for k,c,t,r,m in [
        ('mosaic',(.72,.70,.66),'mosaic',.78,0),('sand',(.55,.48,.35),'sand',.96,0),
        ('wet_sand',(.40,.35,.26),'wet_sand',.84,0),('limestone',(.64,.61,.53),'limestone',.78,0),
        ('timber',(.39,.26,.14),'timber',.70,0),('metal',(.12,.16,.17),None,.36,.8),
        ('leaves',(.12,.27,.09),None,.84,0),('baseline',(.72,.70,.66),None,.85,0),
        ('baseline_dark',(.20,.22,.23),None,.85,0),('ocean',(.04,.24,.30),None,.25,0),('soil',(.12,.085,.045),None,.96,0)]}
    rows=json.loads((ROOT/'geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json').read_text(encoding='utf-8'))['buildings']
    coverage=[]; placements=[]; facade_ids=[]
    for s in range(10):
        lo=-1000+s*200; hi=lo+200; premium=True; detailed=s in refined
        prefix=f'R13_S{s:02d}_'
        # UV0 carries along-coast metres and signed shoreline distance to URP.
        strip(prefix+'ocean_near',coast,lo,hi,-60,0,-.098,mats['ocean'],(1,1),15)
        strip(prefix+'ocean_far',coast,lo,hi,-600,-60,-.098,mats['ocean'],(1,1),1)
        parts=[('wet_sand',0,6,-.078,(4,4)),('sand',6,25.5,-.078,(4,4)),
               ('mosaic',25.5,38,-.032,(12,12.5)),('sand_service',38,42,-.066,(4,4))]
        for key,a,b,z,scale in parts:
            mk='sand' if key=='sand_service' else key
            strip(prefix+key,coast,lo,hi,a,b,z,mats[mk if premium else ('sand' if 'sand' in key else 'baseline')],scale,8 if 'sand' in key else 1)
        if not premium:
            # Preserve the visible R10 language outside the pilot; no blank fallback.
            samples=[(x,coast_at_x(coast,x)) for x in range(lo,hi+1,5)]
            for i,center in enumerate((28.0,31.8,35.5)):
                def w(x,c=center,j=i):return c+.74*math.sin(x*.043+j*.67)+.24*math.sin(x*.127-j*.36)
                band(prefix+f'baseline_dark_{i}',samples,lambda x:w(x)-.70,lambda x:w(x)+.70,-.022,mats['baseline_dark'])
            for i,(a,b) in enumerate(((25.13,25.43),(38.02,38.24))):
                band(prefix+f'baseline_edge_{i}',samples,lambda x,a=a:a,lambda x,b=b:b,-.021,mats['limestone'])
        if detailed:
            buffers={k:{'v':[],'f':[]} for k in ('limestone','timber','metal','leaves','soil')}
            def box(k,a,t,n,u0,u1,v0,v1,z0,z1): append_prism(buffers[k],a,t,n,u0,u1,v0,v1,z0,z1)
            for i,x in enumerate(range(lo+12,hi-10,24)):
                y=coast_at_x(coast,x); slope=(coast_at_x(coast,x+.5)-coast_at_x(coast,x-.5))
                length=math.hypot(1,slope); t=(1/length,slope/length); n=(-t[1],t[0])
                a=(x,y+27.1); width=1.8+((stable_id(f'{s}:{i}')%3))*.15
                # Slatted bench, metal feet and inclined support, realistic seat 45cm.
                for u in (-width/2+.16,width/2-.26): box('metal',a,t,n,u,u+.10,-.23,.23,-.025,.42)
                for j in range(5): box('timber',a,t,n,-width/2,width/2,-.24+j*.10,-.16+j*.10,.42,.47)
                for j in range(4): box('timber',a,t,n,-width/2,width/2,.27,.32,.56+j*.105,.64+j*.105)
                for u in (-width/2+.08,width/2-.14): box('metal',a,t,n,u,u+.06,.24,.30,.4,1.01)
                # Planting contained on seaward margin, leaves are curved blades, not spheres.
                p=(x+5,coast_at_x(coast,x+5)+27.0)
                # Open planter, stone walls and recessed real soil surface.
                for u0,u1 in ((-.9,-.80),(.80,.9)):box('limestone',p,t,n,u0,u1,-.48,.48,-.03,.42)
                for v0,v1 in ((-.48,-.38),(.38,.48)):box('limestone',p,t,n,-.80,.80,v0,v1,-.03,.42)
                box('soil',p,t,n,-.80,.80,-.38,.38,.34,.37)
                for blade in range(80):
                    theta=blade*2.39996; radius=.34*math.sqrt((blade+.5)/80)
                    center=(p[0]+math.cos(theta)*radius,p[1]+math.sin(theta)*radius)
                    height=.32+(stable_id(f'{s}:{i}:{blade}')%100)/250
                    buf=buffers['leaves']; start=len(buf['v'])
                    for step in range(7):
                        f=step/6; reach=.32*f*f; w=.026*(1-f)+.003
                        xx=center[0]+math.cos(theta)*reach; yy=center[1]+math.sin(theta)*reach
                        for sign in (-1,1): buf['v'].append((xx-sign*math.sin(theta)*w,yy+sign*math.cos(theta)*w,.46+height*f))
                        if step: buf['f'].extend([(start+2*step-2,start+2*step,start+2*step+1,start+2*step-1),
                                                (start+2*step-1,start+2*step+1,start+2*step,start+2*step-2)])
                # Bins, three-loop cycle stand and utility bollard, grouped by material.
                q=(x+8,coast_at_x(coast,x+8)+27.2)
                box('metal',q,t,n,-.25,.25,-.25,.25,-.03,.8)
                box('timber',q,t,n,-.29,.29,-.29,-.255,.10,.70)
                for j in range(3):
                    u=j*.6
                    for v in (-.40,.40): box('metal',q,t,n,1+u,1.04+u,v,v+.04,-.03,.70)
                    box('metal',q,t,n,1+u,1.04+u,-.40,.44,.70,.74)
                # 3.4m pedestrian lantern, kept on planting margin.
                lamp=(x-3,coast_at_x(coast,x-3)+26.8)
                box('metal',lamp,t,n,-.065,.065,-.065,.065,-.03,3.25)
                box('metal',lamp,t,n,-.28,.28,-.28,.28,3.2,3.27)
                box('limestone',lamp,t,n,-.17,.17,-.17,.17,3.27,3.50)
                box('metal',lamp,t,n,-.30,.30,-.30,.30,3.50,3.55)
                placements.append({'sector':s,'kind':'bench_planter_bin_cycle_stand','local_xy':[x,y+27.1],
                                   'fictional_planting':True,'clear_pedestrian_corridor_offset_m':[29,36]})
            # Detail near-coast buildings using their real edges and persistent OSM ID.
            for row in rows:
                cx,cy=row['centroid_local_xy_m']
                if not lo<=cx<hi or not 42<cy-coast_at_x(coast,cx)<135: continue
                pts=[tuple(p) for p in row['footprint_ring_local_xy_m']]
                if pts[0]==pts[-1]:pts.pop()
                sign=1 if area(pts)>0 else -1
                for a,b in zip(pts,pts[1:]+pts[:1]):
                    length=math.dist(a,b)
                    if length<5:continue
                    t=((b[0]-a[0])/length,(b[1]-a[1])/length); n=(sign*t[1],-sign*t[0])
                    if n[1]>-.3:continue
                    # Limestone dado, narrow reveals and upper weatherline: overlays, no boolean doors.
                    box('limestone',a,t,n,.08,length-.08,.012,.035,.15,.58)
                    for u in (.12,length-.24):box('limestone',a,t,n,u,u+.12,.01,.08,.6,2.8)
                    box('metal',a,t,n,.08,length-.08,.025,.065,2.91,2.95)
                    # Persistently varied stone piers / timber shades by OSM ID.
                    style=stable_id(str(row['building_id']))%3
                    for u in range(1,int(length)-1,3):
                        if style==0:
                            box('limestone',a,t,n,u,u+.16,.02,.09,.60,2.8)
                        elif style==1:
                            for h in range(4):box('timber',a,t,n,u,u+1.35,.10,.22,2.45+h*.10,2.49+h*.10)
                        else:
                            box('metal',a,t,n,u,u+.06,.02,.12,.65,2.8)
                    facade_ids.append(row['building_id']); break
            for k,buf in buffers.items():
                if buf['f']:
                    ob=detail_mesh(prefix+k,buf,mats[k])
                    if k in ('limestone','timber','metal'):
                        bpy.context.view_layer.objects.active=ob
                        bevel=ob.modifiers.new('R13_manufactured_edge_radius','BEVEL')
                        bevel.width={'limestone':.014,'timber':.007,'metal':.003}[k]
                        bevel.segments=3;bevel.limit_method='ANGLE'
                        bpy.ops.object.modifier_apply(modifier=bevel.name)
                    # Export real reduced geometry, not a promised runtime LOD.
                    for level,ratio in ((1,.55),(2,.22)):
                        lod=ob.copy();lod.data=ob.data.copy();lod.name=prefix+k+f'_LOD{level}'
                        bpy.context.collection.objects.link(lod)
                        bpy.context.view_layer.objects.active=lod
                        modifier=lod.modifiers.new('R13_distance_reduction','DECIMATE');modifier.ratio=ratio
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
        coverage.append({'sector':s,'longitudinal_m':[s*200,(s+1)*200],'local_x_m':[lo,hi],
            'coast_endpoints_local_xy':[[lo,coast_at_x(coast,lo)],[hi,coast_at_x(coast,hi)]],
            'geometry':'GENERATED_DETAILS' if detailed else 'GENERATED_SURFACES',
            'native_gate':'PENDING_REIMPORT','visual_gate':'PENDING','source_coast':'way/70574890',
            'promenade_offsets_m':[25.5,38],'width_is_surveyed':False})
        mid=(lo+hi)/2; shore=coast_at_x(coast,mid)
        coverage[-1]['camera_matrix_local_m']=[
            {'focus':'promenade','position':[mid-35,shore+32,1.65],'target':[mid+30,shore+32,1.3]},
            {'focus':'shore','position':[mid,shore+5,1.65],'target':[mid,shore-70,.1]},
            {'focus':'city','position':[mid,shore-15,35],'target':[mid,shore+75,8]}]
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    assert len(meshes)<=250
    # Freeze explicit triangles: decimation can produce n-gons which FBX
    # tessellates differently. Native census must match the exported geometry.
    for ob in meshes:
        bpy.context.view_layer.objects.active=ob
        modifier=ob.modifiers.new('R13_export_triangles','TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        # Decimation can collapse thin trim faces to collinear triangles. FBX
        # discards them; remove them here explicitly, preserving each UV loop.
        old=ob.data;keep=[];seen=set()
        for p in old.polygons:
            key=tuple(sorted(tuple(round(float(c),6) for c in old.vertices[i].co) for i in p.vertices))
            if p.area>1e-7 and key not in seen:keep.append(p);seen.add(key)
        if len(keep)!=len(old.polygons):
            mesh=bpy.data.meshes.new(ob.name+'_Clean')
            mesh.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in keep]);mesh.update()
            for m in old.materials:mesh.materials.append(m)
            uv=mesh.uv_layers.new(name='UVMap')
            for new,previous in zip(mesh.polygons,keep):
                for dst,src in zip(new.loop_indices,previous.loop_indices):uv.data[dst].uv=old.uv_layers.active.data[src].uv
            ob.data=mesh
    OUT.mkdir(parents=True,exist_ok=True)
    fbx=OUT/'R13_VisualPass2_Coastal_Sectors.fbx'
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',
        apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,path_mode='RELATIVE')
    for image in bpy.data.images:
        if image.source=='FILE' and 'R13_Pass2' in image.filepath:
            image.filepath='//../../UnityProject/Assets/Textures/R13_Pass2/'+Path(image.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'ArtSource/Blender/R13_VisualPass2_Coastal_Sectors.blend'))
    protected=['ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend','UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx',
               'geo/data/copacabana.osm.gz','geo/procedural/R4_SOURCE_FRAME.json','geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json','geo/procedural/R9_VEGETATION_SELECTED.json']
    report={'status':'R13_GENERATED_NATIVE_REIMPORT_PENDING','frame_m':[2000,1000],'refined_sectors':sorted(refined), 'surface_sectors':list(range(10)), 'generator':'Tools/Blender/generate_r13_pass2.py',
        'fbx_sha256':sha(fbx),'meshes':len(meshes),'faces':sum(len(o.data.polygons) for o in meshes),
        'mesh_faces':{o.name:len(o.data.polygons) for o in meshes},
        'source_sha256':{p:sha(ROOT/p) for p in protected},'sectors':coverage,'placements':placements,
        'facade_osm_ids':sorted(set(facade_ids)),'artistic_gate_approved':False,'fps_measured':False}
    (OUT/'R13_Pass2_NATIVE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('R13_NATIVE_GENERATION_PASS',len(meshes),report['faces'],report['facade_osm_ids'],flush=True)

if __name__=='__main__': main()
