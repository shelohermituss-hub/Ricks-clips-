"""exploding-whale props built for the frame (real scanned materials, story lettering): dynamite crates, plunger box, fuse wire."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import beach
from rc.look import tex, col, mesh_obj, mat, srgb

def _ink(name, rgb, strength=1.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = mat(name, "#000000", .7); b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Specular IOR Level"].default_value = .1; return m

def _label(name, body, size, parent, loc, rot, m):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.extrude = .0015
    o = bpy.data.objects.new(name, cu); col("L_OBJECTS").objects.link(o); cu.materials.append(m); o.parent = parent; o.location = loc; o.rotation_euler = rot; return o

def crate(name, c, size=(.9, .6, .5)):
    """a rough wooden dynamite crate: scanned planks, plank gaps, corner battens, rope handles, red stencil DYNAMITE on the long sides"""
    wood = tex("crate_wood", "weathered_planks", tile=.9, recolor="#b08a5a", value=1.0, normal=1.8, spec=.15, macro=.15, untile=False)
    dark = tex("crate_batten", "weathered_planks", tile=.7, recolor="#7a5a38", value=1.0, normal=1.8, spec=.15, macro=.1, untile=False)
    sx, sy, sz = size; bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0, sz / 2), verts=bm.verts)
    o = mesh_obj(name, bm, wood, c)
    for i, (dx, dy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        b2 = bmesh.new(); bmesh.ops.create_cube(b2, size=1); bmesh.ops.scale(b2, vec=(.07, .07, sz + .02), verts=b2.verts)
        bmesh.ops.translate(b2, vec=(dx * (sx / 2 - .02), dy * (sy / 2 - .02), sz / 2), verts=b2.verts); p = mesh_obj("%s_b%d" % (name, i), b2, dark, c); p.parent = o
    for k, z in enumerate((.02, sz - .02)):
        b2 = bmesh.new(); bmesh.ops.create_cube(b2, size=1); bmesh.ops.scale(b2, vec=(sx + .03, sy + .03, .035), verts=b2.verts); bmesh.ops.translate(b2, vec=(0, 0, z), verts=b2.verts)
        p = mesh_obj("%s_r%d" % (name, k), b2, dark, c); p.parent = o
    red = _ink("stencil_red", srgb("#b3261e"))
    for s_ in (-1, 1):
        _label(name + "_t%d" % s_, "DYNAMITE", .125, o, (0, s_ * (sy / 2 + .004), sz * .52), (math.radians(90), 0, 0 if s_ < 0 else math.pi), red)
    return o

def plunger(c, at):
    """the blasting machine: a wooden box with brass corners and a T-handle that goes DOWN when pushed; returns (box, handle)"""
    wood = tex("plunger_wood", "wood_planks_grey", tile=.6, recolor="#8a5a34", value=1.0, normal=1.5, spec=.25, macro=.1, untile=False)
    metal = mat("plunger_metal", "#b9a26a", .35, .9); steel = mat("plunger_steel", "#8d9096", .4, .9)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(.3, .3, .5), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0, .25), verts=bm.verts)
    box = mesh_obj("plunger_box", bm, wood, c); box.location = at
    for i, (dx, dy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        b2 = bmesh.new(); bmesh.ops.create_cube(b2, size=1); bmesh.ops.scale(b2, vec=(.05, .05, .52), verts=b2.verts); bmesh.ops.translate(b2, vec=(dx * .14, dy * .14, .25), verts=b2.verts)
        p = mesh_obj("plunger_c%d" % i, b2, metal, c); p.parent = box
    h = bpy.data.objects.new("plunger_handle", None); c.objects.link(h); h.parent = box; h.location = (0, 0, .5)
    b2 = bmesh.new(); bmesh.ops.create_cone(b2, cap_ends=True, segments=12, radius1=.018, radius2=.018, depth=.42); bmesh.ops.translate(b2, vec=(0, 0, .21), verts=b2.verts); r = mesh_obj("plunger_rod", b2, steel, c, smooth=True); r.parent = h
    b2 = bmesh.new(); bmesh.ops.create_cone(b2, cap_ends=True, segments=12, radius1=.028, radius2=.028, depth=.34); g = mesh_obj("plunger_grip", b2, wood, c, smooth=True); g.parent = h; g.rotation_euler = (0, math.radians(90), 0); g.location = (0, 0, .43)
    _label("plunger_txt", "BLAST", .07, box, (0, -.152, .3), (math.radians(90), 0, 0), _ink("stencil_red", srgb("#b3261e")))
    return box, h

def fuse_wire(c, pts, radius=.012):
    """the firing wire lying on the sand from the crates to the plunger: follows the ground, with slack curves; grows with bevel_factor_end"""
    cu = bpy.data.curves.new("fuse_wire", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = radius; cu.bevel_resolution = 2
    sp = cu.splines.new("POLY"); P = []
    for i in range(len(pts) - 1):
        a, b = Vector(pts[i]), Vector(pts[i + 1]); n = max(2, int((b - a).length / .5)); side = Vector((-(b - a).y, (b - a).x)).normalized()
        for k in range(n):
            t = k / n; p = a.lerp(b, t) + side * .22 * math.sin((i * 7 + k) * .55)
            P.append((p.x, p.y, beach.height(p.x, p.y) + radius + .004))
    P.append((pts[-1][0], pts[-1][1], beach.height(*pts[-1]) + .02))
    sp.points.add(len(P) - 1)
    for q, p in zip(sp.points, P): q.co = (*p, 1)
    o = bpy.data.objects.new("fuse_wire", cu); c.objects.link(o); cu.materials.append(mat("wire_black", "#141416", .5)); return o
