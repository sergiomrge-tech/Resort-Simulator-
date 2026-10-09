"""Pure R7 FBX contracts shared by generators and native re-import QA."""
import math
import re
from numbers import Integral

SEMANTICS = ("wall", "stone", "trim", "glass", "metal", "wood", "roof", "plants", "shadow")
SUFFIX = re.compile(r"(?:\.\d+)+$")
OBJECT_NAME = re.compile(
    r"^R7B_(?P<way>\d+(?:_part[1-9]\d*)?)__(?P<style>cop_[a-z0-9_]+_0[1-5])__"
    r"(?P<semantic>wall|stone|trim|glass|metal|wood|roof|plants|shadow)$")


def semantic_part(name):
    """Blender duplicates material datablocks on each FBX import (.001 etc.)."""
    name = SUFFIX.sub("", name)
    part = name.rsplit("_", 1)[-1]
    if not name.startswith("R7_") or part not in SEMANTICS:
        raise ValueError("R7 material semantic missing: " + name)
    return part


def object_id(building_id, style_id, semantic):
    if not re.fullmatch(r"way/\d+(?:#part[1-9]\d*)?", building_id):
        raise ValueError("Not an original OSM identifier: " + building_id)
    name = "R7B_" + building_id[4:].replace("#part", "_part") + "__" + style_id + "__" + semantic
    if len(name.encode("ascii")) > 63 or not OBJECT_NAME.fullmatch(name):
        raise ValueError("R7 FBX name invalid/truncated: " + name)
    return name


def triangle_points(triangle, vertices):
    """Accept both Blender Vector triangles and index triangles, without guessing version."""
    return [tuple(vertices[int(p)]) if isinstance(p, Integral) else tuple(p) for p in triangle]


def metric_uv(co, normal, repeat_m=2.0):
    """Orthonormal planar projection; rotated facades retain metres per repeat."""
    nx, ny, nz = normal
    horizontal = math.hypot(nx, ny)
    if horizontal < 1e-6:
        return co[0] / repeat_m, co[1] / repeat_m
    # Tangent lies in the plane. Second tangent is normal cross first tangent.
    tx, ty = -ny / horizontal, nx / horizontal
    bx, by, bz = -nz * ty, nz * tx, horizontal
    return (co[0] * tx + co[1] * ty) / repeat_m, (co[0] * bx + co[1] * by + co[2] * bz) / repeat_m


def wall_rectangles(length, height, openings):
    """Partition a planar wall around non-overlapping rectangular holes in metres."""
    if any(not (0 <= a < b <= length and 0 <= z0 < z1 <= height)
           for a,b,z0,z1 in openings):
        raise ValueError("Out-of-bounds facade opening")
    xs = sorted({0.0, length} | {v for hole in openings for v in hole[:2]})
    for x0, x1 in zip(xs, xs[1:]):
        cuts = sorted((z0, z1) for a, b, z0, z1 in openings if a <= (x0+x1)/2 <= b)
        z = 0.0
        for z0, z1 in cuts:
            if z0 < z - 1e-6 or not (0 <= z0 < z1 <= height):
                raise ValueError("Overlapping/out-of-bounds facade opening")
            if z0 > z:
                yield x0, x1, z, z0
            z = z1
        if z < height:
            yield x0, x1, z, height


def project_uv(mesh):
    uv = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = metric_uv(co, poly.normal)
    return uv


def verify_planar_quad_retriangulation(original, rebuilt, allowed_material="Road"):
    """Accept ONLY exact planar quad diagonal flips between equivalent GIS meshes.

    Fingerprints are Counters of (material, sorted 3 rounded world vertices).
    Two source triangles must share one diagonal, and the rebuild must contain
    the two alternative triangles of the SAME 4 vertices/material. This cannot
    hide moved vertices, removed roads, non-planar roof changes, or altered ways.
    Returns the number of verified quad diagonal flips (zero is also valid).
    """
    from collections import Counter

    original=Counter(original)
    rebuilt=Counter(rebuilt)
    if original == rebuilt:
        return 0
    missing=original-rebuilt
    extra=rebuilt-original
    if sum(missing.values())!=sum(extra.values()):
        raise ValueError("GIS_TRIANGLE_COUNT_DRIFT")
    if any(mat!=allowed_material for mat,triangle in list(missing)+list(extra)):
        raise ValueError("GIS_NON_ROAD_TRIANGLE_DRIFT")

    def cross(a,b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

    def area(tri):
        a,b,c=tri
        u=tuple(b[i]-a[i] for i in range(3))
        v=tuple(c[i]-a[i] for i in range(3))
        n=cross(u,v)
        return .5*math.sqrt(sum(x*x for x in n))

    def planar(vertices):
        a,b,c,d=vertices
        n=cross(tuple(b[i]-a[i] for i in range(3)),
                tuple(c[i]-a[i] for i in range(3)))
        magnitude=math.sqrt(sum(x*x for x in n))
        if magnitude<1.e-8:
            return False
        distance=abs(sum(n[i]*(d[i]-a[i]) for i in range(3)))/magnitude
        return distance<=.002

    def exterior(triangles):
        sides=Counter()
        for tri in triangles:
            a,b,c=tri
            for u,v in ((a,b),(b,c),(c,a)):
                sides[tuple(sorted((u,v)))]+=1
        return {edge for edge,count in sides.items() if count==1}

    flips=0
    while missing:
        first=sorted(missing)[0]
        material,tri=first
        valid=None
        for second in sorted(missing):
            if second==first or second[0]!=material:
                continue
            t2=second[1]
            common=set(tri)&set(t2)
            unique=set(tri)^set(t2)
            if len(common)!=2 or len(unique)!=2:
                continue
            unique=sorted(unique)
            common=sorted(common)
            quad=sorted(set(tri)|set(t2))
            if len(quad)!=4 or not planar(quad):
                continue
            alternate=((material,tuple(sorted((unique[0],unique[1],common[0])))),
                       (material,tuple(sorted((unique[0],unique[1],common[1])))))
            if not all(extra.get(t,0)>0 for t in alternate):
                continue
            if exterior((tri,t2))!=exterior((alternate[0][1],alternate[1][1])):
                continue
            before=area(tri)+area(t2)
            after=area(alternate[0][1])+area(alternate[1][1])
            if abs(before-after)>max(.005,before*1e-5):
                continue
            valid=second,alternate
            break
        if valid is None:
            raise ValueError("GIS_UNEXPLAINED_TRIANGULATION_DRIFT: "+repr(first))
        second,alternate=valid
        for entry in (first,second):
            missing[entry]-=1
            if missing[entry]==0:del missing[entry]
        for entry in alternate:
            extra[entry]-=1
            if extra[entry]==0:del extra[entry]
        flips+=1
    if extra:
        raise ValueError("GIS_ADDED_UNKNOWN_TRIANGLES: "+repr(list(extra.items())[:2]))
    return flips
