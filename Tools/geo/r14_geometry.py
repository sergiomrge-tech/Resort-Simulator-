"""Shared deterministic GIS domains; no bpy, no coordinate adjustment."""
from pathlib import Path
import json, gzip, xml.etree.ElementTree as ET, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build/r14deps'))
sys.path.insert(0,str(ROOT/'Tools/geo'))
from shapely import constrained_delaunay_triangles, segmentize
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union, nearest_points
from generate_r6_vegetation import Frame

def polygons(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    if not hasattr(g,'geoms'):return []
    return [p for a in g.geoms for p in polygons(a)]

def load_domains():
    audit=json.loads((ROOT/'ArtSource/Previews/R14_SourceAudit.json').read_text())
    roads=unary_union([Polygon([(v[0],v[1]) for v in tri]) for tri in audit['road_triangles']])
    rows=json.loads((ROOT/'geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json').read_text())['buildings']
    lots=unary_union([Polygon(r['footprint_ring_local_xy_m']).buffer(0) for r in rows])
    coast=audit['coast_samples']
    # The frozen 46-degree frame crosses the curved coast outside y=-500 at
    # the ends. Follow R13's documented coastal layer; do not move GIS inward.
    corridor=Polygon([(x,y+38) for x,y in coast]+[(x,y+150) for x,y in reversed(coast)])
    promenade=Polygon([(x,y+25.5) for x,y in coast]+[(x,y+38) for x,y in reversed(coast)])
    safe=corridor.difference(lots.buffer(.25)).intersection(box(-1000,-500,1000,500))
    outer=roads.buffer(.18,join_style=2)
    domains={
       'gutter':roads.difference(roads.buffer(-.28,join_style=2)).intersection(safe),
       'curbstone':outer.difference(roads).intersection(safe),
       'sidewalk':roads.buffer(2.5,join_style=2).difference(outer).intersection(safe),
    }
    # Fill only the verified gap from promenade landward edge to the first
    # road edge within 8m. Larger gaps remain explicitly unconnected.
    domains['stonetile']=roads.buffer(8,join_style=2).intersection(
       Polygon([(x,y+38) for x,y in coast]+[(x,y+42) for x,y in reversed(coast)]))
    domains['stonetile']=domains['stonetile'].difference(roads.buffer(2.5)).difference(lots.buffer(.25)).intersection(safe)
    frame=Frame(json.loads((ROOT/'geo/procedural/R4_SOURCE_FRAME.json').read_text()))
    osm=ET.parse(gzip.open(ROOT/'geo/data/copacabana.osm.gz','rb')).getroot()
    ramps=[]
    for node in osm.findall('node'):
        tags={t.get('k'):t.get('v') for t in node.findall('tag')}
        if tags.get('highway')!='crossing':continue
        p=Point(frame.local(float(node.get('lon')),float(node.get('lat'))))
        if not safe.buffer(3).covers(p) or p.distance(roads.boundary)>8:continue
        edge=nearest_points(p,roads.boundary)[1]
        # Two nearest sides where the node actually sits on the road.
        ramps.append({'osm_id':'node/'+node.get('id'),'xy':[edge.x,edge.y],
                      'source_xy':[p.x,p.y],'kind':'inferred_curb_cut_at_tagged_crossing'})
    return audit,roads,lots,rows,promenade,domains,ramps

def triangles(g):
    for p in polygons(g):
        for tri in constrained_delaunay_triangles(segmentize(p,1.0)).geoms:
            if tri.area>1e-8:
                coords=list(tri.exterior.coords)[:3]
                a,b,c=coords
                if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:coords.reverse()
                yield coords
