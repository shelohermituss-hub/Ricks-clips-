"""THE GHOST ARMY — inflatable decoy tank, custom Blender model (V3 step 1, 2026-11-18).
A FICTIONAL, NON-FUNCTIONAL film prop: a rubberised-canvas balloon shaped like a tank, as the 1944 deception units used.
Nothing here models a working vehicle: no interior, no mechanism; only inflated bladders, seams, valves, patches and straps.

    blender -b --python build_inflatable_tank.py -- <out_dir> [--lod]

Writes <out_dir>/inflatable_tank.glb (hero, close-up detail) or inflatable_tank_lod.glb (--lod: background decoys).
Axes (Blender): X = length (front +X), Y = width, Z = up; ground at Z = 0. glTF export turns it Y-up for three.js.
Node names are read by episodes/ghost-army/sets/ghost.js: root 'inflatable_tank', 'turret' (pivot at the ring), 'gun_pivot'
(pivot at the mantlet), 'valve_main'. Material names: rubber_body, rubber_dark, rubber_track, seam, brass, webbing, patch, thread.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["."]
OUT = argv[0]; LOD = "--lod" in argv
SUB = 1 if LOD else 2                       # subdivision levels of the bladders
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
DG = lambda: bpy.context.evaluated_depsgraph_get()

# ---------------------------------------------------------------- materials (base values; ghost.js swaps in its textured rubber)
def mat(name, col, rough, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m
srgb = lambda h: tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))
M = dict(rubber_body=mat("rubber_body", srgb("#5d6538"), .55), rubber_dark=mat("rubber_dark", srgb("#454a2c"), .62),
         rubber_track=mat("rubber_track", srgb("#34352e"), .8), seam=mat("seam", srgb("#3e4228"), .7),
         brass=mat("brass", srgb("#c8a24a"), .32, 1.0), webbing=mat("webbing", srgb("#8a7f5c"), .9),
         patch=mat("patch", srgb("#6c7444"), .6), thread=mat("thread", srgb("#d8d2b8"), .9))

ROOT = bpy.data.objects.new("inflatable_tank", None); SC.collection.objects.link(ROOT)
def link(ob, parent=ROOT):
    SC.collection.objects.link(ob); ob.parent = parent; return ob
def mesh_obj(name, bm, material, parent=ROOT, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(M[material]); return link(bpy.data.objects.new(name, me), parent)
def bake(ob):
    """apply every modifier (evaluated mesh becomes the object's mesh)"""
    ev = ob.evaluated_get(DG()); me = bpy.data.meshes.new_from_object(ev); old = ob.data; ob.modifiers.clear(); ob.data = me
    bpy.data.meshes.remove(old); return ob
def mod_bevel_sub(ob, width, segs=3, sub=SUB, angle=None):
    b = ob.modifiers.new("bevel", "BEVEL"); b.width = width; b.segments = segs; b.limit_method = "NONE" if angle is None else "ANGLE"
    if angle is not None: b.angle_limit = angle
    s = ob.modifiers.new("sub", "SUBSURF"); s.levels = sub; s.render_levels = sub; return bake(ob)
def inflate(ob, centre, half, amount, keep=()):
    """push every vertex along its normal by a pillow profile: 0 at the panel edges, `amount` at the panel centre.
    The panel is chosen by the dominant normal axis; the profile uses the two other axes (an inflated cushion)."""
    me = ob.data; me.calc_loop_triangles() if hasattr(me, "calc_loop_triangles") else None
    for v in me.vertices:
        n = v.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        if ax in keep: continue
        f = 1.0
        for i in range(3):
            if i == ax: continue
            t = (v.co[i] - centre[i]) / half[i]; f *= max(0.0, 1 - t * t)
        v.co += n * amount * f
def wrinkle(ob, zb, zh, amp, freq):
    """slack folds near the bottom of the side panels (the canvas is not pulled tight there)"""
    for v in ob.data.vertices:
        if abs(v.normal.y) < .6: continue
        k = 1 - (v.co.z - zb) / zh
        if 0 < k <= 1: v.co += v.normal * amp * k * k * math.sin(v.co.x * freq + 2.3 * math.sin(v.co.x * 1.7))
def bvh(ob):
    me = ob.data; return BVHTree.FromPolygons([ob.matrix_world @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
def project(tree, pts, off):
    out = []
    for p in pts:
        loc, nor, _, _ = tree.find_nearest(Vector(p))
        if loc is None: continue
        out.append((loc + nor * off, nor.normalized()))
    return out
def resample(poly, step, closed=False):
    step *= 2.2 if LOD else 1.0
    pts = list(poly) + ([poly[0]] if closed else []); out = []
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b); n = max(1, int((b - a).length / step))
        out += [a.lerp(b, i / n) for i in range(n)]
    if not closed: out.append(Vector(pts[-1]))
    return out
def tube(bm, frames, r, seg=8, closed=False):
    """a round tube through surface points (loc, normal): the seam piping and rope"""
    seg = 4 if LOD else seg
    rings = []
    for i, (p, n) in enumerate(frames):
        q = frames[min(i + 1, len(frames) - 1)][0] - frames[max(i - 1, 0)][0]
        t = q.normalized() if q.length > 1e-6 else Vector((1, 0, 0)); b = t.cross(n).normalized(); nn = b.cross(t)
        rings.append([bm.verts.new(p + (nn * math.cos(a) + b * math.sin(a)) * r) for a in (2 * math.pi * k / seg for k in range(seg))])
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for A, B in pairs:
        for k in range(seg): bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
def ribbon(bm, frames, w, th):
    """a flat strap lying on the surface (webbing)"""
    prev = None
    for i, (p, n) in enumerate(frames):
        q = frames[min(i + 1, len(frames) - 1)][0] - frames[max(i - 1, 0)][0]; t = q.normalized(); s = t.cross(n).normalized() * w / 2
        quad = [bm.verts.new(p - s), bm.verts.new(p + s), bm.verts.new(p + s + n * th), bm.verts.new(p - s + n * th)]
        if prev:
            for k in range(4): bm.faces.new((prev[k], prev[(k + 1) % 4], quad[(k + 1) % 4], quad[k]))
        prev = quad
def cyl(bm, at, axis, r, h, seg=16, r2=None):
    """a cylinder (valve parts, rings) placed at `at`, along `axis`"""
    z = Vector(axis).normalized(); x = z.orthogonal().normalized(); y = z.cross(x); r2 = r if r2 is None else r2
    lo = [bm.verts.new(Vector(at) + (x * math.cos(a) + y * math.sin(a)) * r) for a in (2 * math.pi * k / seg for k in range(seg))]
    hi = [bm.verts.new(Vector(at) + z * h + (x * math.cos(a) + y * math.sin(a)) * r2) for a in (2 * math.pi * k / seg for k in range(seg))]
    for k in range(seg): bm.faces.new((lo[k], lo[(k + 1) % seg], hi[(k + 1) % seg], hi[k]))
    bm.faces.new(list(reversed(lo))); bm.faces.new(hi)
def torus(bm, at, axis, R, r, seg=20, rs=8):
    z = Vector(axis).normalized(); x = z.orthogonal().normalized(); y = z.cross(x); rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; c = x * math.cos(a) + y * math.sin(a)
        rings.append([bm.verts.new(Vector(at) + c * (R + r * math.cos(b)) + z * r * math.sin(b)) for b in (2 * math.pi * k / rs for k in range(rs))])
    for i in range(seg):
        A, B = rings[i], rings[(i + 1) % seg]
        for k in range(rs): bm.faces.new((A[k], A[(k + 1) % rs], B[(k + 1) % rs], B[k]))
def merge(dst, src):
    vm = {v: dst.verts.new(v.co) for v in src.verts}
    for f in src.faces: dst.faces.new([vm[v] for v in f.verts])
    src.free()
def child(ob, parent):
    bpy.context.view_layer.update(); ob.parent = parent; ob.matrix_parent_inverse = parent.matrix_world.inverted(); return ob
def prism(profile_xz, y0, y1):
    """closed prism: a side profile (X,Z) extruded across Y"""
    bm = bmesh.new(); a = [bm.verts.new((x, y0, z)) for x, z in profile_xz]; b = [bm.verts.new((x, y1, z)) for x, z in profile_xz]; n = len(a)
    bm.faces.new(list(reversed(a))); bm.faces.new(b)
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm
def blob(name, profile, y0, y1, material, bevel, bulge, parent=ROOT, keep=()):
    ob = mesh_obj(name, prism(profile, y0, y1), material, parent); mod_bevel_sub(ob, bevel)
    xs = [p[0] for p in profile]; zs = [p[1] for p in profile]
    c = Vector(((max(xs) + min(xs)) / 2, (y0 + y1) / 2, (max(zs) + min(zs)) / 2)); h = Vector(((max(xs) - min(xs)) / 2, (y1 - y0) / 2, (max(zs) - min(zs)) / 2))
    inflate(ob, c, h, bulge, keep); ob.data.update(); return ob

# ---------------------------------------------------------------- hull bladder (the sloped glacis keeps the tank silhouette)
HULL = [(-2.75, .86), (2.2, .86), (2.92, 1.36), (1.72, 2.02), (-2.62, 2.02), (-2.84, 1.56)]
hull = blob("hull_bladder", HULL, -1.12, 1.12, "rubber_body", .2, .07)
wrinkle(hull, .86, .42, .022, 9.0); hull.data.update()
bpy.context.view_layer.update(); HT = bvh(hull)
seams = bmesh.new()
for s in (-1.12, 1.12):                                   # the two side outlines (piping round each side panel)
    tube(seams, project(HT, resample([(x, s, z) for x, z in HULL], .06, True), .012), .02, 6, True)
for x, z in HULL:                                         # transverse seams at every fold of the profile
    tube(seams, project(HT, resample([(x, -1.12, z), (x, 1.12, z)], .05), .012), .02, 6)
for x in (-1.45, -.2, 1.05):                              # panel joins on the deck and down the sides
    tube(seams, project(HT, resample([(x, -1.25, .9), (x, -1.25, 2.1), (x, 1.25, 2.1), (x, 1.25, .9)], .04), .01), .014, 6)
# ---------------------------------------------------------------- track bladders + wheel cushions + fenders (each side)
TRK = [(-2.85, .06), (2.62, .06), (2.98, .5), (2.62, .98), (-2.85, .98), (-3.1, .5)]
tracks = []
for s in (-1, 1):
    y0, y1 = (s * .98, s * 1.42) if s > 0 else (s * 1.42, s * .98)   # V3 fix: the footprint of the staged lifters (PI-006)
    t = blob("track_bladder_%s" % ("L" if s < 0 else "R"), TRK, y0, y1, "rubber_track", .24, .05); tracks.append(t)
    TT = bvh(t)
    for i in range(14):                                   # tread ribs: tie seams round the bladder every 0.42 m
        x = -2.7 + i * .41
        ring = [(x, y0 - .02, .0), (x, y0 - .02, 1.05), (x, y1 + .02, 1.05), (x, y1 + .02, .0)]
        tube(seams, project(TT, resample(ring, .07, True), .008), .016, 6, True)
    wheels = bmesh.new()
    for i in range(5):                                    # five road-wheel cushions, a painted-hub disc and a cap each
        x = -2.05 + i * 1.02; yo = s * 1.48
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=.36)
        bmesh.ops.scale(bm, vec=(1, .3, 1), verts=bm.verts); bmesh.ops.translate(bm, vec=(x, yo, .46), verts=bm.verts); merge(wheels, bm)
        torus(seams, (x, yo + s * .1, .46), (0, 1, 0), .3, .016, 32, 6)          # the seam round each cushion
        cyl(wheels, (x, yo + s * .09, .46), (0, s, 0), .11, .04, 18)              # hub
    for x in (2.55, -2.72):                               # front sprocket and rear idler cushions
        torus(wheels, (x, s * 1.42, .52), (0, 1, 0), .27, .1, 24, 10)
    w = mesh_obj("wheel_cushions_%s" % ("L" if s < 0 else "R"), wheels, "rubber_dark")
# ---------------------------------------------------------------- turret (own node: ghost.js turns and squashes it)
TUR = bpy.data.objects.new("turret", None); link(TUR); TUR.location = (-.35, 0, 2.02)
def round_blob(name, r1, r2, h, at, material, bevel, bulge, parent, seg=14, sx=1.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=h)
    bmesh.ops.scale(bm, vec=(sx, 1, 1), verts=bm.verts); bmesh.ops.translate(bm, vec=Vector(at) + Vector((0, 0, h / 2)), verts=bm.verts)
    ob = mesh_obj(name, bm, material, parent); mod_bevel_sub(ob, bevel, 4, SUB, math.radians(40))
    inflate(ob, Vector(at) + Vector((0, 0, h / 2)), Vector((r1 * sx, r1, h / 2)), bulge); ob.data.update(); return ob
tur = round_blob("turret_bladder", 1.0, .84, .7, (-.05, 0, 0), "rubber_body", .2, .035, TUR, 24, 1.06)
cup = blob("cupola_bladder", [(-.3, .64), (.3, .64), (.24, .9), (-.24, .9)], -.66, -.14, "rubber_dark", .1, .03, parent=TUR)
hatch = bmesh.new(); cyl(hatch, (.3, .35, .66), (0, 0, 1), .28, .06, 24); torus(hatch, (.3, .35, .72), (0, 0, 1), .27, .022, 28, 6)
mesh_obj("hatch_cushion", hatch, "rubber_dark", TUR)
bpy.context.view_layer.update(); TT = bvh(tur)
tseam = bmesh.new()
tube(tseam, project(TT, [Vector((-.35 + .98 * math.cos(a), .98 * math.sin(a), 2.06)) for a in (2 * math.pi * k / 72 for k in range(72))], .01), .024, 6, True)
tube(tseam, project(TT, [Vector((-.35 + .86 * math.cos(a), .86 * math.sin(a), 2.62)) for a in (2 * math.pi * k / 72 for k in range(72))], .01), .018, 6, True)
for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2):     # four gores joining at the top (a sewn dome)
    tube(tseam, project(TT, [Vector((-.35 + r * math.cos(a), r * math.sin(a), 2.06 + (1 - r) * .65)) for r in [1 - i / 20 for i in range(19)]], .01), .014, 6)
child(mesh_obj("turret_seams", tseam, "seam"), TUR)
# ---------------------------------------------------------------- gun: a mantlet cushion + four sausage segments tied with bands
GUN = bpy.data.objects.new("gun_pivot", None); link(GUN); GUN.location = (.55, 0, 2.3)
blob("mantlet_cushion", [(-.25, -.28), (.32, -.28), (.32, .28), (-.25, .28)], -.42, .42, "rubber_dark", .12, .04, parent=GUN)
gb = bmesh.new(); bands = bmesh.new()
for i in range(4):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
    L = .76; bmesh.ops.scale(bm, vec=(L / 2, .135 - i * .006, .135 - i * .006), verts=bm.verts); bmesh.ops.translate(bm, vec=(.4 + L / 2 + i * .72, 0, 0), verts=bm.verts)
    merge(gb, bm)
    torus(bands, (.4 + i * .72 + .02, 0, 0), (1, 0, 0), .095, .022, 20, 6)
torus(bands, (.4 + 4 * .72, 0, 0), (1, 0, 0), .1, .03, 20, 6)             # muzzle cuff
gun = mesh_obj("gun_segments", gb, "rubber_body", GUN); s = gun.modifiers.new("s", "SUBSURF"); s.levels = SUB - 1 if SUB > 1 else 1; bake(gun)
mesh_obj("gun_bands", bands, "webbing", GUN)
# ---------------------------------------------------------------- valves (brass), reinforcement discs, patches with stitches, straps, lift loops
def valve(name, at, nor, parent=ROOT, big=False):
    bm = bmesh.new(); n = Vector(nor).normalized(); p = Vector(at); k = 1.4 if big else 1.0
    cyl(bm, p, n, .085 * k, .018, 20); cyl(bm, p + n * .018, n, .045 * k, .1 * k, 16); cyl(bm, p + n * (.018 + .1 * k), n, .058 * k, .035, 24)
    torus(bm, p + n * (.1 * k), n, .05 * k, .01, 16, 6); cyl(bm, p + n * (.15 * k), n, .012, .05, 8)
    ob = mesh_obj(name, bm, "brass", parent, smooth=False)
    pad = bmesh.new(); cyl(pad, p - n * .006, n, .17 * k, .008, 28); mesh_obj(name + "_pad", pad, "rubber_dark", parent)
    return ob
v_main = valve("valve_main", *project(HT, [(-2.25, .45, 2.1)], 0)[0], big=True)
valve("valve_side_L", *project(HT, [(-2.0, -1.2, 1.3)], 0)[0]); valve("valve_side_R", *project(HT, [(-2.0, 1.2, 1.3)], 0)[0])
for t in tracks:
    TT = bvh(t); s = 1 if t.name.endswith("R") else -1; valve("valve_track_" + t.name[-1], *project(TT, [(-2.7, s * 1.2, 1.0)], 0)[0])
tv = valve("valve_turret", *project(TT, [(-1.3, -.3, 2.4)], 0)[0]); child(tv, TUR); child(bpy.data.objects["valve_turret_pad"], TUR)
def patch(name, cx, cz, side, w, h):
    y = side * 1.3; grid = []
    bm = bmesh.new(); st = bmesh.new(); rows = 6; cols = max(4, int(w / .05))
    pts = [[project(HT, [(cx - w / 2 + w * i / cols, y, cz - h / 2 + h * j / rows)], .006)[0] for i in range(cols + 1)] for j in range(rows + 1)]
    vv = [[bm.verts.new(p) for p, _ in row] for row in pts]
    for j in range(rows):
        for i in range(cols): bm.faces.new((vv[j][i], vv[j][i + 1], vv[j + 1][i + 1], vv[j + 1][i]))
    edge = resample([(cx - w / 2 + .03, y, cz - h / 2 + .03), (cx + w / 2 - .03, y, cz - h / 2 + .03), (cx + w / 2 - .03, y, cz + h / 2 - .03), (cx - w / 2 + .03, y, cz + h / 2 - .03)], .035, True)
    for p, n in ([] if LOD else project(HT, edge, .009)):  # running stitches round the patch (hero only)
        cyl(st, p - n * .002, n, .006, .006, 5)
    mesh_obj(name, bm, "patch"); mesh_obj(name + "_stitches", st, "thread", smooth=False)
patch("patch_L1", -1.0, 1.35, -1, .42, .3); patch("patch_R1", .7, 1.5, 1, .34, .26); patch("patch_R2", -2.1, 1.1, 1, .26, .22)
straps = bmesh.new(); rings = bmesh.new()
for x in (-1.9, .45):                                     # two webbing straps over the deck, D-rings near the ground
    path = resample([(x, -1.3, .95), (x, -1.3, 2.15), (x, 1.3, 2.15), (x, 1.3, .95)], .04)
    ribbon(straps, project(HT, path, .016), .075, .012)
    for s in (-1, 1): torus(rings, project(HT, [(x, s * 1.3, .92)], .03)[0][0], (1, 0, 0), .05, .012, 16, 6)
for i in range(4):                                        # lift loops along the base: the GIs carry it by these
    for s in (-1, 1):
        p, n = project(HT, [(-2.1 + i * 1.35, s * 1.3, 1.0)], .045)[0]; torus(rings, p, (1, 0, 0), .07, .016, 16, 6)
mesh_obj("straps", straps, "webbing"); mesh_obj("d_rings_lift_loops", rings, "rubber_dark")
mesh_obj("hull_seams", seams, "seam")
# ---------------------------------------------------------------- UVs, normals, export
for ob in [o for o in SC.objects if o.type == "MESH" and not o.data.polygons]: bpy.data.objects.remove(ob)
for ob in [o for o in SC.objects if o.type == "MESH"]:
    bpy.context.view_layer.objects.active = ob
    for o in SC.objects: o.select_set(o == ob)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=.01); bpy.ops.object.mode_set(mode="OBJECT")
tris = sum(len(p.vertices) - 2 for o in SC.objects if o.type == "MESH" for p in o.data.polygons)
meshes = [o.name for o in SC.objects if o.type == "MESH"]
os.makedirs(OUT, exist_ok=True); fn = os.path.join(OUT, "inflatable_tank_lod.glb" if LOD else "inflatable_tank.glb")
for o in SC.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=fn, export_format="GLB", export_yup=True, export_apply=True, use_selection=False)
print("EXPORTED", fn, "meshes", len(meshes), "tris", tris, os.path.getsize(fn))
