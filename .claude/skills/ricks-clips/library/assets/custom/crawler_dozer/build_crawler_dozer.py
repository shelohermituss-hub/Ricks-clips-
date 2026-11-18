"""THE GHOST ARMY — 1940s crawler bulldozer (engineer camp), custom Blender model (V3, user request 2026-11-18).
A generic period crawler tractor with a cable-lift blade, no brand: worn olive paint, real track chains (shoes with grousers wrapped
round sprocket and idler), rollers, louvred engine hood, radiator grille, exhaust stack with rain cap, air pre-cleaner, open seat and
steering levers, fuel tank, fenders, front A-frame with sheaves and lift cables, curved moldboard with cutting edge and ribs, push arms,
and at the back the toothed beam the 603rd dragged to draw fake tank tracks.

    blender -b --python build_crawler_dozer.py -- <out_dir>
Writes <out_dir>/crawler_dozer.glb. Axes (Blender): X = forward (blade at +X), Y = width, Z = up, ground at Z = 0.
Material names (read by sets/ghost.js): paint, paint_worn, steel_dark, track, rubber, exhaust, rust, glass.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["."]
OUT = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
srgb = lambda h: tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))
def mat(name, col, rough, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(col), 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal; return m
M = dict(paint=mat("paint", "#7d7440", .55, .25), paint_worn=mat("paint_worn", "#6a6236", .7, .3), steel_dark=mat("steel_dark", "#3a3a36", .5, .8),
         track=mat("track", "#2c2b28", .75, .7), rubber=mat("rubber", "#1c1a18", .85), exhaust=mat("exhaust", "#22201e", .6, .5),
         rust=mat("rust", "#6a3e24", .9, .2), glass=mat("glass", "#9aa8a8", .15))
ROOT = bpy.data.objects.new("crawler_dozer", None); SC.collection.objects.link(ROOT)
GROUPS = {}
def bm_for(material):
    """one bmesh per material and part family keeps draw calls low"""
    return GROUPS.setdefault(material, bmesh.new())
def merge(dst, src):
    vm = {v: dst.verts.new(v.co) for v in src.verts}
    for f in src.faces: dst.faces.new([vm[v] for v in f.verts])
    src.free()
def obj(name, bm, material, smooth=True, bevel=None, sub=0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    me.materials.append(M[material]); ob = bpy.data.objects.new(name, me); SC.collection.objects.link(ob); ob.parent = ROOT
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"; b.angle_limit = math.radians(35); b.harden_normals = False
    if sub:
        s = ob.modifiers.new("s", "SUBSURF"); s.levels = sub
    if bevel or sub:
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me2 = bpy.data.meshes.new_from_object(ev); ob.modifiers.clear(); old = ob.data; ob.data = me2; bpy.data.meshes.remove(old)
        for p in ob.data.polygons: p.use_smooth = smooth
    return ob
def box(bm, c, s, rot=None):
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0); bmesh.ops.scale(t, vec=s, verts=t.verts)
    if rot: bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=rot, verts=t.verts)
    bmesh.ops.translate(t, vec=c, verts=t.verts); merge(bm, t)
def cyl(bm, c, axis, r, h, seg=20, r2=None):
    t = bmesh.new(); bmesh.ops.create_cone(t, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    z = Vector(axis).normalized(); q = Vector((0, 0, 1)).rotation_difference(z); bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=q.to_matrix(), verts=t.verts)
    bmesh.ops.translate(t, vec=c, verts=t.verts); merge(bm, t)
def prism(bm, prof_xz, y0, y1):
    t = bmesh.new(); a = [t.verts.new((x, y0, z)) for x, z in prof_xz]; b = [t.verts.new((x, y1, z)) for x, z in prof_xz]; n = len(a)
    t.faces.new(list(reversed(a))); t.faces.new(b)
    for i in range(n): t.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces); merge(bm, t)
def tube_path(bm, pts, r, seg=8):
    rings = []
    for i, p in enumerate(pts):
        q = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]; t = q.normalized(); n = t.orthogonal().normalized(); b = t.cross(n)
        rings.append([bm.verts.new(p + (n * math.cos(a) + b * math.sin(a)) * r) for a in (2 * math.pi * k / seg for k in range(seg))])
    for A, B in zip(rings, rings[1:]):
        for k in range(seg): bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))

# ------------------------------------------------ tracks: an oval chain of shoes with grousers, rollers, idler, sprocket, track frame
L, R0, ZC = 2.9, .34, .36                       # track length between wheel centres, wheel radius, centre height
def oval(u):                                    # point and tangent angle on the track path, u in [0,1)
    straight = L; arc = math.pi * R0; tot = 2 * straight + 2 * arc; s = u * tot
    if s < straight: return Vector((-L / 2 + s, 0, ZC + R0)), 0.0                                  # top run, rearward to forward
    s -= straight
    if s < arc: a = math.pi / 2 - s / R0; return Vector((L / 2 + R0 * math.cos(a), 0, ZC + R0 * math.sin(a))), a - math.pi / 2
    s -= arc
    if s < straight: return Vector((L / 2 - s, 0, ZC - R0)), math.pi
    s -= straight; a = -math.pi / 2 - s / R0; return Vector((-L / 2 + R0 * math.cos(a), 0, ZC + R0 * math.sin(a))), a - math.pi / 2
NS = 46
for side in (-1, 1):
    yc = side * 1.0; tb = bm_for("track")
    for i in range(NS):
        p, ang = oval(i / NS); rot = Matrix.Rotation(-ang, 3, "Y")
        box(tb, p + Vector((0, yc, 0)) + rot @ Vector((0, 0, .025)), (.19, .5, .035), rot)        # the shoe plate
        box(tb, p + Vector((0, yc, 0)) + rot @ Vector((0, 0, .06)), (.035, .48, .05), rot)        # the grouser bar
        box(tb, p + Vector((0, yc, 0)) + rot @ Vector((0, 0, -.03)), (.16, .14, .05), rot)        # the link under the shoe
    sd = bm_for("steel_dark")
    cyl(sd, (L / 2, yc, ZC), (0, 1, 0), R0 - .05, .34, 28)                                         # front idler
    cyl(sd, (-L / 2, yc, ZC), (0, 1, 0), R0 - .03, .3, 11)                                         # rear sprocket hub
    for k in range(11):                                                                            # sprocket teeth
        a = 2 * math.pi * k / 11; box(sd, (-L / 2 + (R0 - .03) * math.cos(a), yc, ZC + (R0 - .03) * math.sin(a)), (.07, .1, .07), Matrix.Rotation(-a, 3, "Y"))
    for k in range(5): cyl(sd, (-1.1 + k * .55, yc, .17), (0, 1, 0), .13, .28, 18)                # track rollers
    for k in range(2): cyl(sd, (-.6 + k * 1.2, yc, .76), (0, 1, 0), .08, .2, 14)                  # carrier rollers
    pt = bm_for("paint_worn"); box(pt, (0, yc, .43), (2.7, .2, .32))                              # track frame
    for k in range(9): cyl(sd, (-1.2 + k * .3, yc + side * .105, .5), (0, side, 0), .022, .02, 8)  # frame bolts
    # fender over the track, bent down at the front
    fp = bm_for("paint"); prism(fp, [(-1.75, .86), (1.25, .86), (1.62, .7), (1.66, .74), (1.28, .92), (-1.75, .92)], yc - .3, yc + .3)
# ------------------------------------------------ engine hood with louvres, radiator, frame
P = bm_for("paint")
box(P, (.35, 0, 1.25), (1.6, 1.15, .78))                                                           # engine hood
box(P, (-.75, 0, 1.0), (.75, 1.6, .26))                                                            # operator deck
box(P, (-1.0, 0, 1.45), (.5, 1.1, .55))                                                            # fuel tank behind the seat
D = bm_for("steel_dark")
for s in (-1, 1):
    for k in range(7): box(D, (.0 + k * .14, s * .58, 1.32), (.08, .02, .32))                     # side louvres (slots)
box(D, (1.19, 0, 1.2), (.06, 1.05, .74))                                                           # radiator grille frame
G = bm_for("track")
for k in range(13): box(G, (1.23, -.48 + k * .08, 1.2), (.03, .025, .66))                         # grille bars
box(P, (1.2, 0, 1.6), (.12, 1.15, .08))                                                            # top tank of the radiator
cyl(D, (1.0, 0, 1.69), (0, 0, 1), .07, .1, 14)                                                      # radiator cap
for s in (-.42, .42): cyl(D, (1.2, s, 1.72), (1, 0, 0), .09, .14, 18); cyl(bm_for('glass'), (1.275, s, 1.72), (1, 0, 0), .075, .02, 18)   # headlights
for s in (-1, 1):
    for k in range(4): box(D, (.35, s * .578, .95 + k * .19), (1.5, .012, .012))                  # hood panel seams
# exhaust stack with a rain flap, air pre-cleaner bowl
E = bm_for("exhaust")
cyl(E, (.7, .3, 2.115), (0, 0, 1), .06, .95, 16); cyl(E, (.7, .3, 1.69), (0, 0, 1), .085, .1, 16)
box(E, (.7, .3, 2.6), (.14, .14, .01), Matrix.Rotation(-.35, 3, "Y"))                             # the rain flap
cyl(D, (.35, -.32, 1.815), (0, 0, 1), .05, .35, 14); cyl(P, (.35, -.32, 2.09), (0, 0, 1), .12, .2, 20); cyl(D, (.35, -.32, 2.205), (0, 0, 1), .13, .03, 20)
# open operator station: seat, backrest, steering clutch levers with knobs, brake pedals, a canopy on four posts
Rb = bm_for("rubber")
box(Rb, (-.75, 0, 1.25), (.42, .5, .1)); box(Rb, (-.98, 0, 1.52), (.08, .5, .42))
for s in (-.22, -.08, .08, .22):
    tube_path(D, [Vector((-.3, s, 1.12)), Vector((-.38, s, 1.4)), Vector((-.46, s, 1.62))], .015, 8); cyl(Rb, (-.46, s, 1.62), (0, 0, 1), .03, .06, 10)
for s in (-.3, .3): box(D, (-.2, s, 1.16), (.16, .08, .03), Matrix.Rotation(.5, 3, "Y"))
for x in (-1.2, -.25):
    for s in (-.75, .75): cyl(D, (x, s, 1.875), (0, 0, 1), .03, 1.5, 10)
box(P, (-.72, 0, 2.64), (1.15, 1.7, .05))                                                          # canopy
# front A-frame with sheaves and lift cables down to the blade (cable control, 1940s)
for s in (-.45, .45): tube_path(D, [Vector((1.0, s, 1.62)), Vector((1.55, s * .25, 2.35))], .035, 10)
cyl(D, (1.58, 0, 2.38), (0, 1, 0), .12, .1, 22); cyl(D, (1.92, 0, 1.25), (0, 1, 0), .1, .1, 20)
Ca = bm_for("track")
for dy in (-.03, .03): tube_path(Ca, [Vector((1.62, dy, 2.27)), Vector((1.78, dy, 1.85)), Vector((1.92, dy, 1.35))], .009, 6)
tube_path(Ca, [Vector((1.5, 0, 2.38)), Vector((.9, 0, 2.15)), Vector((-.9, 0, 1.9)), Vector((-1.6, 0, 1.15))], .009, 6)   # back to the winch
cyl(D, (-1.62, 0, 1.0), (0, 1, 0), .16, .5, 20)                                                    # rear cable winch drum
# blade: curved moldboard, cutting edge, end bits, ribs on the back, push arms
prof = [(1.95 + .18 * math.sin(math.pi * t) - .05 * t, .05 + 1.05 * t) for t in [k / 14 for k in range(15)]]
BL = bm_for("paint_worn")
outer = [(x, z) for x, z in prof]; inner = [(x - .06, z) for x, z in reversed(prof)]
prism(BL, outer + inner, -1.45, 1.45)
box(D, (2.0, 0, .06), (.08, 2.92, .1))                                                             # cutting edge
for s in (-1, 1): box(D, (1.98, s * 1.47, .35), (.1, .06, .65))                                    # end bits
for k in range(6): box(BL, (1.78, -1.2 + k * .48, .55), (.08, .05, .9))                            # ribs
for s in (-1, 1): tube_path(BL, [Vector((1.8, s * 1.05, .45)), Vector((.4, s * 1.05, .43)), Vector((-.3, s * 1.03, .42))], .07, 10); cyl(D, (-.3, s * 1.0, .42), (0, 1, 0), .09, .22, 16)
# toothed beam dragged behind (the story's fake-track tool) with chains
Bm = bm_for("rust")
box(Bm, (-2.05, 0, .18), (.22, 2.4, .18))
for k in range(8): box(Bm, (-2.05, -1.05 + k * .3, .05), (.07, .12, .2))
for s in (-.8, .8): tube_path(D, [Vector((-1.6, s * .5, .5)), Vector((-1.85, s * .7, .3)), Vector((-2.0, s, .26))], .02, 6)
box(D, (-1.55, 0, .5), (.25, .3, .12))                                                             # drawbar hitch
for name, bm in list(GROUPS.items()):
    obj("dozer_" + name, bm, name, smooth=name in ("rubber",), bevel=.03 if name in ("paint", "paint_worn", "rust") else (.008 if name in ("steel_dark",) else None))
# UVs + export
for ob in [o for o in SC.objects if o.type == "MESH"]:
    bpy.context.view_layer.objects.active = ob
    for o in SC.objects: o.select_set(o == ob)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.01); bpy.ops.object.mode_set(mode="OBJECT")
tris = sum(len(p.vertices) - 2 for o in SC.objects if o.type == "MESH" for p in o.data.polygons)
os.makedirs(OUT, exist_ok=True); fn = os.path.join(OUT, "crawler_dozer.glb")
for o in SC.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=fn, export_format="GLB", export_yup=True, export_apply=True)
print("EXPORTED", fn, "meshes", len([o for o in SC.objects if o.type == "MESH"]), "tris", tris, os.path.getsize(fn))
