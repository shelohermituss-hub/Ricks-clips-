"""Small shared toolkit for the custom Blender prop scripts in library/assets/custom/ (V3, 2026-11-18).
Import from a prop script:  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from _blender_kit import *
Conventions: Blender X = forward, Y = width, Z = up, ground at Z = 0; glTF export turns it Y-up for three.js.
Parts are merged per material (one mesh per material keeps draw calls low); material names are what the set module re-maps."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
srgb = lambda h: tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))
MATS, GROUPS = {}, {}
def mat(name, col, rough, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(col), 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    MATS[name] = m; return m
def root(name):
    r = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(r); return r
def bm_for(material):
    return GROUPS.setdefault(material, bmesh.new())
def merge(dst, src):
    vm = {v: dst.verts.new(v.co) for v in src.verts}
    for f in src.faces: dst.faces.new([vm[v] for v in f.verts])
    src.free()
def box(bm, c, s, rot=None):
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0); bmesh.ops.scale(t, vec=s, verts=t.verts)
    if rot: bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=rot, verts=t.verts)
    bmesh.ops.translate(t, vec=c, verts=t.verts); merge(bm, t)
def cyl(bm, c, axis, r, h, seg=20, r2=None):
    """a cylinder CENTRED on c along axis"""
    t = bmesh.new(); bmesh.ops.create_cone(t, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    q = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()); bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=q.to_matrix(), verts=t.verts)
    bmesh.ops.translate(t, vec=c, verts=t.verts); merge(bm, t)
def torus(bm, c, axis, R, r, seg=24, rs=8):
    z = Vector(axis).normalized(); x = z.orthogonal().normalized(); y = z.cross(x); rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; d = x * math.cos(a) + y * math.sin(a)
        rings.append([bm.verts.new(Vector(c) + d * (R + r * math.cos(b)) + z * r * math.sin(b)) for b in (2 * math.pi * k / rs for k in range(rs))])
    for i in range(seg):
        A, B = rings[i], rings[(i + 1) % seg]
        for k in range(rs): bm.faces.new((A[k], A[(k + 1) % rs], B[(k + 1) % rs], B[k]))
def prism(bm, prof_xz, y0, y1):
    t = bmesh.new(); a = [t.verts.new((x, y0, z)) for x, z in prof_xz]; b = [t.verts.new((x, y1, z)) for x, z in prof_xz]; n = len(a)
    t.faces.new(list(reversed(a))); t.faces.new(b)
    for i in range(n): t.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces); merge(bm, t)
def prism_yz(bm, prof_yz, x0, x1):
    """a profile drawn in the Y-Z plane (front view), extruded along X"""
    t = bmesh.new(); a = [t.verts.new((x0, y, z)) for y, z in prof_yz]; b = [t.verts.new((x1, y, z)) for y, z in prof_yz]; n = len(a)
    t.faces.new(list(reversed(a))); t.faces.new(b)
    for i in range(n): t.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces); merge(bm, t)
def tube_path(bm, pts, r, seg=8):
    pts = [Vector(p) for p in pts]; rings = []
    for i, p in enumerate(pts):
        q = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]; t = q.normalized(); n = t.orthogonal().normalized(); b = t.cross(n)
        rings.append([bm.verts.new(p + (n * math.cos(a) + b * math.sin(a)) * r) for a in (2 * math.pi * k / seg for k in range(seg))])
    for A, B in zip(rings, rings[1:]):
        for k in range(seg): bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
def finish(parent, bevel_mats=(), bevel=.02, smooth_mats=()):
    """turn every material group into one mesh object (optional angle-limited bevel), parented to `parent`"""
    sc = bpy.context.scene; out = []
    for name, bm in list(GROUPS.items()):
        me = bpy.data.meshes.new(parent.name + "_" + name); bm.to_mesh(me); bm.free()
        me.materials.append(MATS[name]); ob = bpy.data.objects.new(parent.name + "_" + name, me); sc.collection.objects.link(ob); ob.parent = parent
        if name in bevel_mats:
            b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"; b.angle_limit = math.radians(35)
            ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me2 = bpy.data.meshes.new_from_object(ev); ob.modifiers.clear(); ob.data = me2
        for p in ob.data.polygons: p.use_smooth = name in smooth_mats
        out.append(ob)
    GROUPS.clear(); return out
def export(path):
    sc = bpy.context.scene
    for ob in [o for o in sc.objects if o.type == "MESH"]:
        bpy.context.view_layer.objects.active = ob
        for o in sc.objects: o.select_set(o == ob)
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.01); bpy.ops.object.mode_set(mode="OBJECT")
    tris = sum(len(p.vertices) - 2 for o in sc.objects if o.type == "MESH" for p in o.data.polygons)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    for o in sc.objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_apply=True)
    print("EXPORTED", path, "meshes", len([o for o in sc.objects if o.type == "MESH"]), "tris", tris, os.path.getsize(path))
