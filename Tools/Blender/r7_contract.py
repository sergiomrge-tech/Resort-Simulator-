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
