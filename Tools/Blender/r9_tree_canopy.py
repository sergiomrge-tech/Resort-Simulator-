"""Add dense, two-sided tropical foliage to verified R6 tree meshes.
Retains authorial trunk and branch geometry. No billboard, low-poly sphere or
external asset. Deterministic per species. Intended for 48 OSM source trees.
"""
from __future__ import annotations
import random,math
import bpy
from mathutils import Vector

def enrich_tropical_canopy(source,species):
 rng=random.Random(7519 if species.endswith("_densa") else 6817)
 verts=[tuple(v.co) for v in source.vertices]
 faces=[tuple(p.vertices) for p in source.polygons]
 indices=[p.material_index for p in source.polygons]
 rich=species.endswith("_densa")
 count=490 if rich else 410
 spread=2.08 if rich else 1.80
 for i in range(count):
  # Ellipsoidal crown with randomized lateral clumping.
  z=rng.uniform(2.90,5.65 if rich else 5.48)
  norm=(z-4.18)/1.57
  reach=spread*math.sqrt(max(.05,1-norm*norm))
  radius=(.27+.73*math.sqrt(rng.random()))*reach
  bearing=rng.uniform(0,2*math.pi)
  center=Vector((math.cos(bearing)*radius, math.sin(bearing)*radius,z))
  heading=rng.uniform(0,2*math.pi)
  forward=Vector((math.cos(heading),math.sin(heading),rng.uniform(-.28,.36))).normalized()
  side=Vector((-forward.y,forward.x,rng.uniform(-.1,.1))).normalized()
  length=rng.uniform(.36,.76)
  width=rng.uniform(.15,.32)
  base=center-forward*length*.48
  tip=center+forward*length*.56+Vector((0,0,.04))
  left=center+side*width
  right=center-side*width
  ridge=center+Vector((0,0,rng.uniform(.07,.16)))
  start=len(verts)
  verts.extend(tuple(p) for p in (base,left,tip,right,ridge))
  a,b,c,d,e=[start+k for k in range(5)]
  triangles=((a,b,e),(b,c,e),(c,d,e),(d,a,e))
  pigment=1+(i%3)
  for face in triangles:
   faces.append(face);indices.append(pigment)
   faces.append(tuple(reversed(face)));indices.append(pigment)
 mesh=bpy.data.meshes.new("R9_Dense_Organic_Canopy_"+species)
 mesh.from_pydata(verts,[],faces)
 mesh.update()
 for material in source.materials:
  assert material is not None
  mesh.materials.append(material)
 assert len(mesh.materials)==4
 for poly,idx in zip(mesh.polygons,indices):
  poly.material_index=idx
  poly.use_smooth=idx==0
 return mesh
