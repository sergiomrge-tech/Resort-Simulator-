"""Additive GIS-derived solid curb/sidewalk/gutter, grouped per 200m sector.
Run source audit and PBR first. Requires Shapely 2.1, GEOS constrained triangulation.
No original source scene or R7-R13 output is written by this module.
"""
from pathlib import Path
import sys, json, math, hashlib
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tools/geo'),str(ROOT/'Tools/Blender')]
from r14_geometry import load_domains, polygons, triangles, box, Point, segmentize
from generate_r9_urban_environment import make, GEO_ROT
OUT=ROOT/'UnityProject/Assets/Architecture/R14_Urban'
TEX=ROOT/'UnityProject/Assets/Textures/R14_Urban'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def material(key):
    m=bpy.data.materials.new('R14_'+key);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
    for channel in ('base','normal','mask'):
        n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(TEX/f'r14_{key}_{channel}.png'))
        if channel!='base':n.image.colorspace_settings.name='Non-Color'
        if channel=='base':m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
        elif channel=='normal':
            normal=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(n.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
        else:
            inv=m.node_tree.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1
            m.node_tree.links.new(n.outputs['Alpha'],inv.inputs[1]);m.node_tree.links.new(inv.outputs[0],bs.inputs['Roughness'])
    return m

def solid(name,g,mat,key,roads,ramps,lo,hi):
    vs=[];fs=[];index={}
    def height(x,y):
        if key=='gutter':return .065
        if key=='stonetile':return -.012
        rise=.14
        for r in ramps:
            d=math.hypot(x-r['xy'][0],y-r['xy'][1])
            if d<3:
                edge=Point(x,y).distance(roads)
                flare=max(0,min(1,(d-1.3)/1.7))
                cut=.02+.12*min(1,edge/1.8)
                rise=min(rise,cut+(.14-cut)*flare)
        return .06+rise
    def vertex(x,y,z):
        k=(round(x,7),round(y,7),round(z,7))
        if k not in index:index[k]=len(vs);vs.append(k)
        return index[k]
    for tri in triangles(g):
        fs.append(tuple(vertex(x,y,height(x,y)) for x,y in tri))
        fs.append(tuple(vertex(x,y,-.025) for x,y in reversed(tri)))
    for p in polygons(g):
        from shapely.geometry.polygon import orient
        p=segmentize(orient(p,sign=1),1)
        for ring in [p.exterior,*p.interiors]:
            for a,b in zip(ring.coords,list(ring.coords)[1:]):
                # Adjacent sectors share the boundary, never duplicate end caps.
                if abs(a[0]-b[0])<1e-7 and (abs(a[0]-lo)<1e-6 or abs(a[0]-hi)<1e-6):continue
                fs.append((vertex(*a,-.025),vertex(*b,-.025),vertex(*b,height(*b)),vertex(*a,height(*a))))
    ob=make(name,vs,fs,mat)
    # Planar dominant-axis metric UV for top and vertical faces.
    for p in ob.data.polygons:
        normal=p.normal;axis=Vector((1,0,0)) if abs(normal.z)>.5 else Vector((-normal.y,normal.x,0)).normalized()
        across=normal.cross(axis)
        for li in p.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            ob.data.uv_layers.active.data[li].uv=(v.dot(axis)/2,v.dot(across)/2)
    return ob

def main():
    audit,roads,lots,rows,prom,domains,ramps=load_domains()
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    mats={key:material(key) for key in domains}
    coverage=[]
    for s in range(10):
        lo=-1000+s*200;hi=lo+200;clip=box(lo,-500,hi,500);parts={};bounds={}
        for key,g in domains.items():
            g=g.intersection(clip);parts[key]={'area_m2':g.area,'polygon_count':len(polygons(g)),
              'minimum_lot_distance_m':g.distance(lots) if not g.is_empty else None}
            if g.is_empty or g.area<1e-6:continue
            ob=solid(f'R14_S{s:02d}_{key}',g,mats[key],key,roads,ramps,lo,hi)
            parts[key]['mesh']=ob.name
            bounds[key]=[list(g.bounds[:2]),list(g.bounds[2:])]
            assert (g.intersection(lots).area)<1e-6
            if key!='gutter':assert g.intersection(roads).area<1e-6
        samples=audit['coast_samples'][s*200:(s+1)*200+1:10]
        gaps=[Point(x,y+38).distance(roads) for x,y in samples]
        coverage.append({'sector':f'S{s:02d}','local_x_m':[lo,hi],'parts':parts,'bounds_xy_m':bounds,
            'promenade_landward_edge_to_road_sample_distance_m':{'minimum':min(gaps),'maximum':max(gaps),'sample_step_m':10},
            'ramps':[r for r in ramps if lo<=r['xy'][0]<hi],
            'native_gate':'PENDING_REIMPORT','unity_gate':'PENDING','visual_gate':'PENDING'})
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    discarded_area=0;discarded_faces=0
    for o in meshes:
        bpy.context.view_layer.objects.active=o
        m=o.modifiers.new('R14_export_triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
        # Sub-millimetre needles in Boolean boundaries can invert after FBX's
        # float32 geographic transform. Remove numerical slivers, never move
        # a source coordinate. Area removed is recorded, not concealed.
        old=o.data;keep=[]
        for p in old.polygons:
            pts=[old.vertices[i].co for i in p.vertices]
            if p.area>1e-4 and min((pts[i]-pts[(i+1)%3]).length for i in range(3))>.002:
                keep.append(p)
            else:discarded_area+=p.area;discarded_faces+=1
        if len(keep)!=len(old.polygons):
            mesh=bpy.data.meshes.new(o.name+'_numeric_clean');mesh.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in keep]);mesh.update()
            for mat in old.materials:mesh.materials.append(mat)
            uv=mesh.uv_layers.new(name='UVMap')
            for new,prior in zip(mesh.polygons,keep):
                for dst,src in zip(new.loop_indices,prior.loop_indices):uv.data[dst].uv=old.uv_layers.active.data[src].uv
            o.data=mesh
    OUT.mkdir(parents=True,exist_ok=True);fbx=OUT/'R14_GIS_Urban_Connectors.fbx'
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False,path_mode='RELATIVE')
    for image in bpy.data.images:
        if image.source=='FILE':image.filepath='//../../UnityProject/Assets/Textures/R14_Urban/'+Path(image.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'ArtSource/Blender/R14_GIS_Urban_Connectors.blend'))
    q={'status':'R14_GENERATED_REIMPORT_PENDING','frame_m':[2000,1000],'angle_degrees':46,
       'source_sha256':audit['source_sha256'],'source_road_triangles':3731,'fbx_sha256':sha(fbx),
       'meshes':len(meshes),'faces':sum(len(o.data.polygons) for o in meshes),
       'mesh_faces':{o.name:len(o.data.polygons) for o in meshes},'sectors':coverage,
       'road_z_m':.06,'curb_rise_m':.14,'gutter_top_m':.065,'sidewalk_top_m':.20,
       'widths_m':{'curbstone':.18,'gutter':.28,'sidewalk':2.32},
       'numeric_sliver_faces_removed':discarded_faces,'numeric_sliver_total_area_removed_m2':discarded_area,
       'ramp_locations_inferred':True,'artistic_gate_approved':False,'fps_measured':False,
       'limitations':['GIS is clipped to y +/-500; curved R13 shoreline extends outside it at map ends. No invented road across missing substrate.',
       'No surveyed entrances, curb heights or crossing geometry. No gameplay collision approval.',
       '8m connection search intentionally leaves wider promenade-road gaps pending.']}
    (OUT/'R14_CONNECTORS_NATIVE.json').write_text(json.dumps(q,indent=2)+'\n')
    print('R14_CONNECTORS_GENERATED',q['meshes'],q['faces'],flush=True)
if __name__=='__main__':main()
