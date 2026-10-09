"""Project Resort R4: actual procedural 3D facades from frozen OSM footprints.

Blender 4.x headless:
  blender -b --factory-startup --python Tools/Blender/generate_r4_buildings.py -- --mode pilot
  blender -b --factory-startup --python Tools/Blender/generate_r4_buildings.py -- --mode gallery
  blender -b --factory-startup --python Tools/Blender/generate_r4_buildings.py -- --mode city --start 0 --count 50 --no-render

pilot: 10 building IDs (one per architectural family), actual source OSM footprints
gallery: all 50 unique style recipes instantiated on representative OSM footprints
city: batch over full 1,468-building frozen style assignment (chunk size bounded)

The original Copacabana GIS .blend/.fbx and R3 hero buildings are never altered.
Generated FBX meshes are centered on their original OSM centroid, with placement
recorded separately in local EPSG:32723/R3 frame. NO Unity scene is modified.
All mesh and previews are truly rendered by Blender; no image mockups.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"ArtSource/ProceduralBuildings/Resort50Styles.json"
ASSIGNMENTS=ROOT/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
OUT=ROOT/"UnityProject/Assets/Architecture/R4_Procedural"
IMAGES=ROOT/"ArtSource/Previews"
HELD_BACK={"way/1048277518","way/1048277521"}  # R3 hero placements
VERSION="R4_PROCEDURAL_GEOMETRY_V1"
MATERIAL_KEYS=("wall","stone","trim","glass","metal","wood","roof","plants","shadow")
COLORS={
 "residencial_orla":(.83,.78,.68),"residencial_anos70":(.75,.75,.71),
 "art_deco_carioca":(.86,.77,.62),"hotel_classico":(.87,.83,.72),
 "hotel_contemporaneo":(.72,.74,.72),"misto_loja_terrea":(.81,.72,.63),
 "residencial_compacto":(.78,.78,.73),"predio_historico":(.88,.74,.60),
 "escritorio_clinica":(.73,.75,.75),"equipamento_especial":(.82,.76,.65)
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def clamp(x,low,high):
    return max(low,min(high,x))

def mat(name,rgb,metal=0.0,rough=.6,glass=False,noise=False):
    obj=bpy.data.materials.get(name)
    if obj:return obj
    obj=bpy.data.materials.new(name)
    obj.diffuse_color=(*rgb,1.0)
    obj.use_nodes=True
    tree=obj.node_tree
    bs=tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1.0)
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    if glass:
        bs.inputs["Transmission Weight"].default_value=.14
        bs.inputs["Coat Weight"].default_value=.52
        bs.inputs["Coat Roughness"].default_value=.1
    if noise:
        tex=tree.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=26
        tex.inputs["Detail"].default_value=2
        tex.inputs["Roughness"].default_value=.65
        bump=tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.18
        bump.inputs["Distance"].default_value=.014
        tree.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return obj

def palette(style):
    family=style["family"]
    base=COLORS[family]
    variant=style["variant"]
    # Non-identical warm architectural materials, not random rainbow buildings.
    offset=(variant-3)*.021
    wall=tuple(clamp(x+offset,.18,.96) for x in base)
    accent=tuple(clamp(x*.73+.035,.05,.92) for x in wall)
    prefix="R4_"+style["id"]+"_"
    return {
        "wall":mat(prefix+"01_plaster",wall,.01,.76,noise=True),
        "stone":mat(prefix+"02_stone",tuple(clamp(x*.81+.065,0,1) for x in base),0,.73,noise=True),
        "trim":mat(prefix+"03_facade_trim",accent,.08,.45),
        "glass":mat(prefix+"04_glass_blue",(0.115+variant*.008,.235+variant*.005,.27+variant*.013),.16,.11,glass=True),
        "metal":mat(prefix+"05_steel_or_bronze",(.27,.26,.24) if variant%2 else (.19,.24,.27),.75,.28),
        "wood":mat(prefix+"06_wood",(.31,.19,.105),0,.46,noise=True),
        "roof":mat(prefix+"07_roof_stone",tuple(clamp(x*.6,0,1) for x in base),.04,.69),
        "plants":mat(prefix+"08_plant_green",(.15,.29,.17),0,.8),
        "shadow":mat(prefix+"09_recess_shadow",(.07,.075,.077),0,.91),
    }

class Geometry:
    """Batched Blender geometry: one combined mesh per material, not per window."""
    def __init__(self):
        self.data={key:{"v":[],"f":[]} for key in MATERIAL_KEYS}
        self.boxes=0
        self.windows=0
        self.balconies=0
        self.roof_features=0

    def face(self,category,points):
        if len(points)<3:return
        o=self.data[category]
        idx=len(o["v"])
        o["v"].extend(tuple(p) for p in points)
        o["f"].append(tuple(idx+i for i in range(len(points))))

    def box(self,key,c,tangent,normal,length,depth,height):
        if min(length,depth,height)<.009:return
        t=Vector((tangent[0],tangent[1],0))
        n=Vector((normal[0],normal[1],0))
        mid=Vector(c)
        corners=[]
        for z in (-height/2,height/2):
            for a,b in ((-1,-1),(1,-1),(1,1),(-1,1)):
                q=mid+t*a*length/2+n*b*depth/2+Vector((0,0,z))
                corners.append(tuple(q))
        for face in ((3,2,1,0),(4,5,6,7),(0,1,5,4),
                     (1,2,6,5),(2,3,7,6),(3,0,4,7)):
            self.face(key,[corners[i] for i in face])
        self.boxes+=1

    def add_edge_box(self,key,a,t,n,u,depth_center,z,length,thickness,height):
        c=(a[0]+t[0]*u+n[0]*depth_center,
           a[1]+t[1]*u+n[1]*depth_center,z)
        self.box(key,c,t,n,length,thickness,height)

    def emit(self,collection,materials,ident):
        objects=[]
        for key,spec in self.data.items():
            if not spec["f"]:continue
            mesh=bpy.data.meshes.new(ident+"_"+key+"_mesh")
            mesh.from_pydata(spec["v"],[],spec["f"])
            mesh.update(calc_edges=True)
            obj=bpy.data.objects.new(ident+"_"+key,mesh)
            collection.objects.link(obj)
            mesh.materials.append(materials[key])
            # Avoid costly full mesh bevels; detailed fascia geometry is explicit.
            objects.append(obj)
        return objects


def ring_stats(coords):
    pts=[tuple(float(x) for x in p) for p in coords]
    if len(pts)>=2 and pts[0]==pts[-1]:pts=pts[:-1]
    if len(pts)<3:
        raise ValueError("OSM polygon has fewer than 3 vertices")
    signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))/2
    if abs(signed)<2:
        raise ValueError("Degenerate footprint")
    return pts,signed

def choose_buildings(data,mode,start,count):
    all_items=data["buildings"]
    compatible=[x for x in all_items if
       110<=x["area_footprint_m2"]<=1600
       and 4<=len(x["footprint_ring_local_xy_m"])<=15
       and 9<=x["height_for_visualization_m"]<=40
       and x["building_id"] not in HELD_BACK]
    if mode=="pilot":
        families={}
        for item in compatible:
            family=item["visual_family"]
            if family in families:continue
            families[family]=item
        if len(families)!=10:raise RuntimeError("Cannot find pilot for all 10 architectural families")
        return list(families.values())
    if mode=="gallery":
        samples={}
        styles={s["id"] for s in json.loads(CATALOG.read_text())["styles"]}
        for item in compatible:
            samples.setdefault(item["style_id"],item)
        # some style IDs may occur only on impractical footprints; use a
        # representative compatible real footprint from same family instead.
        by_family={}
        for item in compatible:by_family.setdefault(item["visual_family"],item)
        for style in json.loads(CATALOG.read_text())["styles"]:
            sid=style["id"]
            if sid not in samples:
                original=by_family.get(style["family"])
                if original is None:
                    raise RuntimeError("No measured OSM example for style "+sid)
                modified=dict(original)
                modified["style_id"]=sid
                modified["building_id"]=original["building_id"]+"__style_"+str(style["variant"])
                samples[sid]=modified
        if set(samples)!=styles:raise RuntimeError("Not all 50 catalog entries have geometric examples")
        return [samples[sid] for sid in sorted(styles)]
    if mode=="city":
        if start<0 or count<1 or count>100:
            raise ValueError("City mode accepts chunks of 1–100 buildings, with --start and --count")
        # ALL city buildings, excluding 2 hero locations, even small ones;
        # quality/safety gates still run per footprint.
        return [x for x in all_items if x["building_id"] not in HELD_BACK][start:start+count]
    raise ValueError("Unrecognized mode "+mode)


def building_geometry(item,style):
    """Make physically metric roof/walls + true mesh modules, not flat texture boxes."""
    coords=item["footprint_ring_local_xy_m"]
    pts,area=ring_stats(coords)
    ox,oy=item["centroid_local_xy_m"]
    # local coordinate origin in each generated FBX; placement recorded in JSON.
    pts=[(x-ox,y-oy) for x,y in pts]
    h=clamp(float(item["height_for_visualization_m"]),3.5,80.0)
    floor_h=style["floor_height_m"]
    floors=int(clamp(round(h/floor_h),2,25))
    visual_height=float(h)
    sign=1 if area>0 else -1
    G=Geometry()
    source_seed=item["seed"]
    rng=random.Random(int(source_seed))
    winmode=style["window_pattern"]
    variant=style["variant"]
    window_w={"vertical_recessed":.89,"horizontal_ribbon":1.45,
              "large_tripartite":1.35,"alternating_bays":1.07,
              "full_height_inset":1.12}[winmode]
    n_edges=len(pts)
    walls=[((pts[i]),pts[(i+1)%n_edges]) for i in range(n_edges)]
    lengths=[math.dist(a,b) for a,b in walls]
    front_index=max(range(n_edges),key=lambda i:lengths[i])
    # Actual perimeter walls of unmodified mapped OSM polygon.
    for ei,(a,b) in enumerate(walls):
        delta=(b[0]-a[0],b[1]-a[1])
        length=math.hypot(*delta)
        if length<.3:continue
        t=(delta[0]/length,delta[1]/length)
        # For CCW ring outward is to the RIGHT of travel.
        n=(sign*t[1],-sign*t[0])
        G.face("wall",[(a[0],a[1],0),(b[0],b[1],0),
                       (b[0],b[1],visual_height),(a[0],a[1],visual_height)])
        # Structural plinth, upper cornice and roof parapet rails sit slightly
        # within footprint. Do not add fake sidewalks or road geometry.
        G.add_edge_box("stone",a,t,n,length/2,-.12,.37,length-.04,.24,.75)
        G.add_edge_box("trim",a,t,n,length/2,-.11,visual_height-.24,
                       length-.04,.23,.33)
        G.add_edge_box("roof",a,t,n,length/2,-.15,visual_height+.34,
                       length-.03,.31,.68)
        if length<3.1:continue
        bay_count=int(clamp(round(length/2.9),1,12))
        bay_step=length/bay_count
        entry_bay=bay_count//2
        for floor in range(floors):
            ground=floor==0
            center_z=(floor+.46)*visual_height/floors
            frame_h=clamp(visual_height/floors*(.60 if ground else .59),1.15,2.17)
            win_height=frame_h if ground else min(frame_h,2.08)
            win_width=min(window_w,bay_step*.68)
            for bi in range(bay_count):
                u=(bi+.5)*bay_step
                if ground and ei==front_index and bi==entry_bay:
                    # Door with recessed frame and canopy later.
                    G.add_edge_box("shadow",a,t,n,u,-.038,center_z,
                                   min(bay_step*.76,2.35),.07,frame_h*1.3)
                    G.add_edge_box("glass",a,t,n,u,-.018,center_z,
                                   min(bay_step*.65,2.10),.04,frame_h*1.20)
                    G.add_edge_box("metal",a,t,n,u,-.032,center_z,
                                   .07,.085,frame_h*1.18)
                    continue
                if floor>0 and winmode=="alternating_bays" and bi%2:
                    win_width*=.94
                # Shadow recess, inner pane, four trim members and sill.
                # The actual mesh has thickness, frames and multiple materials.
                G.add_edge_box("shadow",a,t,n,u,-.015,center_z,
                               win_width+.23,.065,win_height+.2)
                G.add_edge_box("glass",a,t,n,u,-.005,center_z,
                               win_width,.045,win_height)
                edge=.085 if style["family"]=="art_deco_carioca" else .06
                for xx in (-win_width/2,win_width/2):
                    G.add_edge_box("trim",a,t,n,u+xx,.02,center_z,
                                   edge,.085,win_height+.22)
                for zz in (-win_height/2,win_height/2):
                    G.add_edge_box("trim",a,t,n,u,.02,center_z+zz,
                                   win_width+.21,.085,edge)
                if winmode in ("large_tripartite","horizontal_ribbon"):
                    for xx in (-win_width/6,win_width/6):
                        G.add_edge_box("metal",a,t,n,u+xx,.018,center_z,
                                       .028,.055,win_height)
                else:
                    G.add_edge_box("metal",a,t,n,u,.015,center_z,
                                   .028,.06,win_height)
                G.add_edge_box("stone",a,t,n,u,-.035,center_z-win_height/2-.09,
                               win_width+.34,.26,.13)
                G.windows+=1

                eligible=not ground and style["balcony_type"]!="none"
                balcony_pattern=style["balcony_type"]
                if "alternating" in balcony_pattern:eligible &= ((floor+bi+ei)%2==0)
                elif "vertical_bay" in balcony_pattern:eligible &= (bi%3==0)
                elif "staggered" in balcony_pattern:eligible &= ((floor//2+bi)%2==0)
                elif "recessed" in balcony_pattern:eligible &= ((floor+bi)%3!=1)
                if eligible and bay_step>2.0:
                    # Limit balcony to mapped polygon interior: recess along
                    # -normal, not street. Thin rim may protrude <= 0.16 m.
                    bal_d=min(.92,style["balcony_depth_m"])
                    bal_len=min(bay_step*.78,win_width+.65)
                    floor_z=center_z-win_height/2-.15
                    G.add_edge_box("stone",a,t,n,u,-bal_d*.44,floor_z,
                                   bal_len,bal_d,.16)
                    # Glass/metal/concrete railing along inward-most edge.
                    railmat="glass" if "glass" in balcony_pattern else "stone" if "concrete" in balcony_pattern else "metal"
                    G.add_edge_box(railmat,a,t,n,u,-bal_d*.28,
                                   floor_z+.47,bal_len-.12,.065,.91)
                    for xoff in (-bal_len/2+.12,bal_len/2-.12):
                        G.add_edge_box("metal",a,t,n,u+xoff,-bal_d*.28,
                                       floor_z+.50,.045,.07,1.0)
                    G.balconies+=1
        if ei==front_index:
            middle=length/2
            # A substantial architectural entry/canopy visible at street level.
            G.add_edge_box("roof",a,t,n,middle,-.10,visual_height/floors*.94,
                           min(5.4,length*.44),.72,.19)
            for off in (-1.27,1.27):
                G.add_edge_box("stone",a,t,n,middle+off,-.08,
                               visual_height/floors*.48,.20,.26,
                               visual_height/floors*.92)
        if style["accent_element"]=="vertical_fins":
            for fi in range(1,5):
                G.add_edge_box("trim",a,t,n,length*fi/5,-.06,
                               visual_height*.57,.09,.17,visual_height*.72)
        if style["parapet_type"] in ("stepped_cornice","deep_ledge"):
            G.add_edge_box("stone",a,t,n,length/2,-.14,
                           visual_height+.10,length-.01,.30,.20)
    # Triangulate the exact source polygon without inventing a rectangle.
    tess=tessellate_polygon([[Vector((x,y,visual_height)) for x,y in pts]])
    for tri in tess:
        G.face("roof",[(v.x,v.y,v.z) for v in tri])
    # Roof equipment models (water tanks, louvers, pergola) interior only;
    # limit their footprint to a small region around the polygon centroid.
    from mathutils.geometry import intersect_point_tri_2d
    cx=sum(x for x,y in pts)/len(pts)
    cy=sum(y for x,y in pts)/len(pts)
    if style["roof_detail"] in ("water_tank_screen","service_screen"):
        G.box("roof",(cx,cy,visual_height+.57),(1,0),(0,1),1.25,1.15,1.1)
        G.roof_features+=1
    elif style["roof_detail"]=="pergola":
        for shift in (-.65,0,.65):
            G.box("wood",(cx+shift,cy,visual_height+.70),(1,0),(0,1),.12,2.3,.12)
            G.roof_features+=1
    elif style["roof_detail"]=="terrace_planters":
        G.box("stone",(cx,cy,visual_height+.24),(1,0),(0,1),1.25,1.1,.4)
        G.box("plants",(cx,cy,visual_height+.50),(1,0),(0,1),1.02,.88,.24)
        G.roof_features+=1
    else:
        G.box("roof",(cx,cy,visual_height+.06),(1,0),(0,1),1.4,1.2,.14)
        G.roof_features+=1
    return G,{"floor_count_visual":floors,"height_visual_m":visual_height,
              "source_footprint_area_m2":item["area_footprint_m2"],
              "source_footprint_vertices":len(pts),
              "windows":G.windows,"balconies":G.balconies,
              "roof_features":G.roof_features,"solid_boxes":G.boxes}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def empty_group(tag):
    coll=bpy.data.collections.new(tag)
    bpy.context.scene.collection.children.link(coll)
    return coll


def source_style(style_id,catalog):
    s=catalog.get(style_id)
    if s is None:raise RuntimeError("R4 assignment uses unknown 50 style ID: "+style_id)
    return s


def named_guid(key):
    return hashlib.sha256(("ResortR4FBX:"+key).encode()).hexdigest()[:32]


def generate_item(item,style,outputs,write_fbx=True):
    display_name=re.sub(r"[^A-Za-z0-9_-]+","_",item["building_id"])
    token=item["style_id"]+"__"+display_name
    group=empty_group("R4_"+token)
    geo,detail=building_geometry(item,style)
    objects=geo.emit(group,palette(style),token)
    if len(objects)<5 or detail["windows"]<3 or detail["solid_boxes"]<12:
        raise RuntimeError("Procedural building too shallow/no meaningful facade: "+token)
    polys=sum(len(o.data.polygons) for o in objects)
    verts=sum(len(o.data.vertices) for o in objects)
    if polys<80 or verts<300:
        raise RuntimeError("Insufficient actual polygons for architectural facade: "+token)
    fbxpath=OUT/"FBX"/(token+".fbx")
    if write_fbx:
        fbxpath.parent.mkdir(parents=True,exist_ok=True)
        bpy.ops.object.select_all(action="DESELECT")
        for ob in objects:ob.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.export_scene.fbx(filepath=str(fbxpath),use_selection=True,
            object_types={"MESH"},axis_forward="-Z",axis_up="Y",global_scale=1.0,
            apply_unit_scale=True,bake_space_transform=False,
            use_mesh_modifiers=True,add_leaf_bones=False)
        if fbxpath.stat().st_size<20000 or not fbxpath.read_bytes().startswith(b"Kaydara FBX Binary"):
            raise RuntimeError("Generated R4 FBX invalid: "+token)
        if bpy.context.scene.render.engine!="BLENDER_EEVEE_NEXT":
            pass
        metapath=fbxpath.with_suffix(fbxpath.suffix+".meta")
        metapath.write_text("fileFormatVersion: 2\nguid: "+named_guid(token)+
                            "\nModelImporter:\n  serializedVersion: 22200\n  externalObjects: {}\n")
    row={
        "building_id":item["building_id"],"style_id":style["id"],
        "family":style["family"],"seed":item["seed"],
        "source_osm":item["source_osm_way"],
        "local_osm_centroid_xy_m":item["centroid_local_xy_m"],
        "height_provenance":item["height_provenance"],
        "measured_height_m":None,
        "visual_only_not_surveyed":True,
        "mesh_object_count":len(objects),
        "vertices_generated":verts,"polygons_generated":polys,
        "materials_generated":len(objects),
        "fbx":str(fbxpath.relative_to(ROOT)) if write_fbx else None,
        "fbx_bytes":fbxpath.stat().st_size if write_fbx else None,
        "fbx_sha256":digest(fbxpath) if write_fbx else None,
        "unity_asset_guid":named_guid(token) if write_fbx else None,
        "source_ring_local_xy_m":item["footprint_ring_local_xy_m"],
        "placement_frame":"R4_SOURCE_FRAME.json: EPSG:32723 rotated local XY metres; FBX is centered and Z-up in Blender; Y-up in Unity",
        **detail
    }
    outputs.append(row)
    return objects


def shift_for_preview(objects,idx):
    col=idx%5
    row=(idx//5)%2
    # Original FBX is already exported BEFORE display transform is applied.
    # Normalize only in preview; show different architectural masses coherently.
    low=[min((o.matrix_world@Vector(c))[axis] for o in objects for c in o.bound_box) for axis in range(3)]
    high=[max((o.matrix_world@Vector(c))[axis] for o in objects for c in o.bound_box) for axis in range(3)]
    dims=[max(.1,high[k]-low[k]) for k in range(3)]
    scale=min(8.2/dims[0],7.4/dims[1],11.2/dims[2],1.4)
    x=(col-2)*11.8
    y=(row-.5)*13.4
    for obj in objects:
        # Generated origin close to building mapped centroid already; set a
        # shared transform via real mesh vertex data, display-only.
        for v in obj.data.vertices:
            v.co.x=(v.co.x-(low[0]+high[0])*.5)*scale+x
            v.co.y=(v.co.y-(low[1]+high[1])*.5)*scale+y
            v.co.z=(v.co.z-low[2])*scale+.25
    return x,y


def studio_square(cx,cy,name,color):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,cy,-.1))
    ob=bpy.context.object
    ob.name=name
    ob.dimensions=(10.9,11.4,.18)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(color)


def camera_and_lighting():
    backdrop=mat("R4_STUDIO_BASE",(0.19,.23,.26),0,.75)
    dark=mat("R4_STUDIO_PEDESTAL",(0.27,.29,.30),.02,.75)
    studio_square(0,0,"R4_Studio_Underlay",backdrop)
    ground=bpy.context.object
    ground.dimensions=(62,29,.16)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    key_light=bpy.data.lights.new("R4_Sun_Daylight","SUN")
    key_light.energy=1.9
    sun=bpy.data.objects.new("R4_Sun_Daylight",key_light)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler=(math.radians(42),math.radians(-24),math.radians(-22))
    for name,location,power,size in (
         ("R4_Softbox",(-18,-24,24),3500,18),
         ("R4_Fill",(23,14,17),1900,16)):
        light=bpy.data.lights.new(name,"AREA")
        light.energy=power
        light.shape="DISK"
        light.size=size
        obj=bpy.data.objects.new(name,light)
        bpy.context.collection.objects.link(obj)
        obj.location=location
        obj.rotation_euler=(-obj.location).to_track_quat("-Z","Y").to_euler()
    w=bpy.data.worlds.new("R4_Cloud_Studio")
    bpy.context.scene.world=w
    w.use_nodes=True
    bg=w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(.56,.67,.78,1)
    bg.inputs["Strength"].default_value=.6
    cam_data=bpy.data.cameras.new("R4_Architecture_Studio_Camera")
    cam=bpy.data.objects.new("R4_Architecture_Studio_Camera",cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location=(28,-34,32)
    cam.rotation_euler=(Vector((0,0,2))-cam.location).to_track_quat("-Z","Y").to_euler()
    cam_data.type="ORTHO"
    cam_data.ortho_scale=63
    cam_data.clip_end=400
    bpy.context.scene.camera=cam
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE_NEXT" if hasattr(bpy.app,"version") and bpy.app.version>=(4,2) else "BLENDER_EEVEE"
    scene.render.resolution_x=1800
    scene.render.resolution_y=1080
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX" if bpy.app.version>=(4,0) else "Standard"
    return dark


def add_label(name,x,y,mat_label):
    curve=bpy.data.curves.new("R4_ID","FONT")
    curve.body=name[:35].replace("cop_","")
    curve.size=.32
    curve.extrude=.002
    label=bpy.data.objects.new("R4_STUDIO_LABEL_NOT_EXPORTED",curve)
    bpy.context.collection.objects.link(label)
    label.location=(x-4.8,y-5.3,.1)
    label.rotation_euler=(0,0,0)
    curve.materials.append(mat_label)


def render_sheet(index,objects_by_sheet,labels,mode):
    # Delete previously displayed meshes ONLY AFTER they were exported and
    # inspected, so 1,468-building full-city batches remain RAM-bounded.
    studio_mat=camera_and_lighting()
    ivory=mat("R4_STUDIO_TEXT",(0.91,.86,.76))
    for i,(objects,name) in enumerate(zip(objects_by_sheet,labels)):
        px,py=shift_for_preview(objects,i)
        studio_square(px,py,"R4_STUDIO_Pedestal",studio_mat)
        add_label(name,px,py,ivory)
    path=IMAGES/("R4_Procedural_"+mode+"_Sheet_"+str(index+1).zfill(2)+"_Blender.png")
    path.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if not path.exists() or path.stat().st_size<45000:
        raise RuntimeError("Blender did not render real procedural buildings")
    return {"path":str(path.relative_to(ROOT)),"sha256":digest(path),
            "bytes":path.stat().st_size,"engine":bpy.context.scene.render.engine,
            "size":[1800,1080],"building_count":len(objects_by_sheet)}


def run():
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("pilot","gallery","city"),default="pilot")
    parser.add_argument("--start",type=int,default=0)
    parser.add_argument("--count",type=int,default=30)
    parser.add_argument("--no-render",action="store_true")
    parser.add_argument("--max-preview-sheets",type=int,default=5)
    args=parser.parse_args(argv)
    if args.mode=="gallery" and args.max_preview_sheets<5 and not args.no_render:
        raise RuntimeError("Cannot silently skip gallery proof of all 50 styles")
    catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
    assignments=json.loads(ASSIGNMENTS.read_text(encoding="utf-8"))
    if assignments["num_buildings_assigned"]!=1468:
        raise RuntimeError("Original complete OSM footprint assignment missing")
    if catalog["status"]!="FIFTY_PROCEDURAL_RECIPES_ONLY_NOT_FBX_OR_UNITY_PREFABS":
        raise RuntimeError("Original authored fifty recipes missing")
    styles={s["id"]:s for s in catalog["styles"]}
    items=choose_buildings(assignments,args.mode,args.start,args.count)
    if not items:
        raise RuntimeError("No OSM source buildings in requested slice")
    reset()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"FBX").mkdir(parents=True,exist_ok=True)
    # Keep Unity importer GUIDs stable when moving generated models between PCs.
    for folder in (OUT, OUT/"FBX"):
        meta=Path(str(folder)+".meta")
        if not meta.is_file():
            meta.write_text("fileFormatVersion: 2\nguid: "+
                named_guid("folder:"+folder.relative_to(ROOT).as_posix())+
                "\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n")
    output=[]
    skipped=[]
    previews=[]
    for batch_i in range(0,len(items),10):
        sheet_items=items[batch_i:batch_i+10]
        scene_objects=[]
        labels=[]
        # Render clean studio sheets with bounded memory usage.
        for item in sheet_items:
            style=source_style(item["style_id"],styles)
            try:
                objs=generate_item(item,style,output,write_fbx=True)
            except (RuntimeError,ValueError) as err:
                if args.mode!="city":
                    raise
                # OSM contains narrow/degenerate outlines that cannot support
                # an honest windowed multi-storey facade. Never fabricate a
                # larger parcel or place geometry on a neighboring street.
                skipped.append({"building_id":item["building_id"],
                                "reason":str(err),"requires_manual_review":True})
                print("R4_REQUIRES_MANUAL_REVIEW",item["building_id"],str(err),flush=True)
                continue
            scene_objects.append(objs)
            labels.append(style["id"])
            print("R4_GEOMETRY_GENERATED",item["building_id"],style["id"],
                  "vertices",output[-1]["vertices_generated"],
                  "windows",output[-1]["windows"],
                  "balconies",output[-1]["balconies"],flush=True)
        if not args.no_render and scene_objects and (batch_i//10)<args.max_preview_sheets:
            previews.append(render_sheet(batch_i//10,scene_objects,labels,args.mode))
        # Each batch owns all its objects/materials and can be garbage
        # collected without corrupting previously written FBXs.
        if batch_i+10<len(items):
            reset()
    result={
        "status":"ACTUAL_PROCEDURAL_BLENDER_FBX_GENERATED_NOT_UNITY_VALIDATED",
        "version":VERSION,"mode":args.mode,"start":args.start,
        "count":len(output),"skipped_count":len(skipped),
        "skipped_source_ids":skipped,
        "total_source_buildings":1468,
        "catalog_sha256":digest(CATALOG),
        "assignments_sha256":digest(ASSIGNMENTS),
        "source_geo_unchanged":True,
        "source_map_sha256":digest(ROOT/"ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend"),
        "source_city_fbx_sha256":digest(ROOT/"UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx"),
        "excluded_R3_hero_ids":sorted(HELD_BACK),
        "meshes":output,"real_blender_previews":previews,
        "geometry_is_not_surveyed":True,
        "limits":"A physically generated FBX collection, not a Unity-built/imported map; prefab placement requires GIS duplication/removal gate and manual visual approval. PBR shader parameters in Blender may not reproduce identically in URP.",
        "geodata_licence":"© OpenStreetMap contributors, ODbL 1.0"
    }
    report=OUT/("R4_"+args.mode.upper()+"_GENERATION_REPORT.json")
    report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("R4_GENERATOR_COMPLETE",json.dumps({
        "mode":args.mode,"count":len(output),"skipped":len(skipped),
        "styles":len({m["style_id"] for m in output}),
        "polygons":sum(m["polygons_generated"] for m in output),
        "fbx_size_bytes":sum(m["fbx_bytes"] for m in output),
        "previews":len(previews),"report":str(report.relative_to(ROOT))},ensure_ascii=False),flush=True)


if __name__=="__main__":
    run()
