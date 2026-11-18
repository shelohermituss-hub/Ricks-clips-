"""Farmyard props (restructuring deliverables, 2026-11-18). One script, several GLBs (like signals_props):
  rail_fence.glb      4 m split-rail section: 2 hewn posts (tapered, notched tops), 3 rails with knots/irregular section
  hay_bale.glb        1.2 x 0.5 x 0.4 m square bale: displaced straw body (noise), two twine bands, loose straw tufts
  stone_well.glb      round well: 28 stacked stones per course x 5 courses, wooden roof frame, crank axle, rope, bucket
  water_trough.glb    stone trough on two blocks, with water surface (material "water")
  washing_posts.glb   two T posts with a sagging line (the cloth is simulated by rc.animate cloth, not here)
  garden_shed.glb     plank shed: walls of vertical boards, roof planks, SEPARATE door object (shed_door, hinge on its left edge,
                      origin ON the hinge) and SEPARATE window panes (shed_glass_0/1) for rc.physics glass_shatter
Materials: wood, wood_dark, straw, twine, stone, iron, rope, glass, water.
    blender -b --python build_farm_props.py -- <out dir>"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Matrix, noise
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _blender_kit import reset, mat, root, bm_for, box, cyl, torus, tube_path, finish, export, MATS  # noqa: E402

OUT = sys.argv[sys.argv.index("--") + 1]; R = random.Random(7)
def mats():
    mat("wood", "#8a6a44", .8); mat("wood_dark", "#5a4330", .75); mat("straw", "#c8a85e", .9); mat("twine", "#7a6038", .9)
    mat("stone", "#9a958a", .92); mat("iron", "#2e2c2a", .5, .6); mat("rope", "#9a8a62", .9); mat("glass", "#9fb4c0", .05); mat("water", "#3a5a62", .05)

def displace(bm, amp, scale, seed=0):
    for v in bm.verts:
        n = noise.noise(v.co * scale + Vector((seed, seed * 2, seed * 3))); v.co += v.normal * amp * n

def post(bm, x, y, h=1.3, r=.075):
    t = bmesh.new(); bmesh.ops.create_cone(t, cap_ends=True, segments=7, radius1=r, radius2=r * .82, depth=h)
    for v in t.verts: v.co.x += R.uniform(-.008, .008); v.co.y += R.uniform(-.008, .008)
    bmesh.ops.translate(t, vec=(x, y, h / 2), verts=t.verts)
    from _blender_kit import merge; merge(bm, t)

# ---- rail fence
reset(); mats(); H = root("rail_fence"); W = bm_for("wood_dark")
for x in (-2.0, 2.0): post(W, x, 0)
WL = bm_for("wood")
for k, z in enumerate((.35, .7, 1.05)):
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1); bmesh.ops.scale(t, vec=(4.3, .07, .1), verts=t.verts)
    bmesh.ops.subdivide_edges(t, edges=t.edges, cuts=6); displace(t, .012, 3.0, k)
    bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=Matrix.Rotation(R.uniform(-.02, .02), 3, "Y"), verts=t.verts); bmesh.ops.translate(t, vec=(0, .09, z), verts=t.verts)
    from _blender_kit import merge; merge(WL, t)
finish(H, bevel_mats=(), smooth_mats=()); export(os.path.join(OUT, "rail_fence.glb"))

# ---- hay bale
reset(); mats(); H = root("hay_bale"); S = bm_for("straw")
t = bmesh.new(); bmesh.ops.create_cube(t, size=1); bmesh.ops.scale(t, vec=(1.2, .5, .4), verts=t.verts); bmesh.ops.subdivide_edges(t, edges=t.edges, cuts=10)
displace(t, .018, 9.0, 1); bmesh.ops.translate(t, vec=(0, 0, .2), verts=t.verts)
from _blender_kit import merge; merge(S, t)
for i in range(60):                                                  # loose straw tufts sticking out
    p = Vector((R.uniform(-.6, .6), R.choice((-.25, .25)) + R.uniform(-.01, .01), R.uniform(.05, .38))); d = Vector((R.uniform(-.3, .3), (1 if p.y > 0 else -1) * R.uniform(.2, .6), R.uniform(-.2, .3))).normalized()
    tube_path(S, [p, p + d * R.uniform(.04, .1)], .003, seg=3)
TW = bm_for("twine")
for x in (-.3, .3): torus(TW, (x, 0, .2), (1, 0, 0), .0, .0, seg=4, rs=3) if False else box(TW, (x, 0, .2), (.012, .51, .41))
finish(H, smooth_mats=("straw",)); export(os.path.join(OUT, "hay_bale.glb"))

# ---- stone well
reset(); mats(); H = root("stone_well"); ST = bm_for("stone")
for c in range(5):
    n = 28; r0 = .85
    for k in range(n):
        a = 2 * math.pi * (k + (.5 if c % 2 else 0)) / n; t = bmesh.new(); bmesh.ops.create_cube(t, size=1)
        bmesh.ops.scale(t, vec=(.18, .26, .17), verts=t.verts); bmesh.ops.subdivide_edges(t, edges=t.edges, cuts=2); displace(t, .012, 6.0, c * 50 + k)
        bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "Z"), verts=t.verts); bmesh.ops.translate(t, vec=(math.cos(a) * r0, math.sin(a) * r0, .09 + c * .175), verts=t.verts)
        merge(ST, t)
WD = bm_for("wood_dark")
for s in (-1, 1): box(WD, (0, s * .9, 1.55), (.12, .12, 2.1))
for s in (-1, 1):
    for k in range(8): box(WD, (s * (.22 + k * .0), 0, 0), (.01, .01, .01))
roof = bm_for("wood")
for s in (-1, 1):
    for k in range(9): box(roof, (s * .42, -1.0 + k * .25, 2.72 + .0), (.95, .24, .03), rot=Matrix.Rotation(s * .62, 3, "Y"))
cyl(WD, (0, 0, 2.15), (0, 1, 0), .06, 1.9, seg=12); box(bm_for("iron"), (0, 1.0, 2.0), (.03, .03, .3))
tube_path(bm_for("rope"), [(0, 0, 2.1), (0, 0, 1.2)], .012, seg=6)
B = bm_for("wood"); cyl(B, (0, 0, 1.1), (0, 0, 1), .14, .22, seg=16, r2=.17)
finish(H, smooth_mats=("rope",)); export(os.path.join(OUT, "stone_well.glb"))

# ---- water trough
reset(); mats(); H = root("water_trough"); ST = bm_for("stone")
for x in (-.65, .65):
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1); bmesh.ops.scale(t, vec=(.3, .55, .35), verts=t.verts); bmesh.ops.subdivide_edges(t, edges=t.edges, cuts=2); displace(t, .01, 5, x * 10)
    bmesh.ops.translate(t, vec=(x, 0, .175), verts=t.verts); merge(ST, t)
for (c, s) in [((0, 0, .38), (1.9, .65, .08)), ((0, .29, .58), (1.9, .07, .4)), ((0, -.29, .58), (1.9, .07, .4)), ((.92, 0, .58), (.07, .58, .4)), ((-.92, 0, .58), (.07, .58, .4))]:
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1); bmesh.ops.scale(t, vec=s, verts=t.verts); bmesh.ops.subdivide_edges(t, edges=t.edges, cuts=3); displace(t, .006, 6, c[0] + c[1]); bmesh.ops.translate(t, vec=c, verts=t.verts); merge(ST, t)
box(bm_for("water"), (0, 0, .7), (1.75, .5, .01))
finish(H); export(os.path.join(OUT, "water_trough.glb"))

# ---- washing line posts
reset(); mats(); H = root("washing_posts"); WD = bm_for("wood_dark")
for x in (-2.5, 2.5): post(WD, x, 0, h=2.1, r=.06); box(WD, (x, 0, 1.95), (.08, .7, .06))
for y in (-.3, .3): tube_path(bm_for("rope"), [(-2.5 + 5 * k / 16, y, 1.97 - .18 * 4 * (k / 16) * (1 - k / 16)) for k in range(17)], .006, seg=5)
finish(H, smooth_mats=("rope",)); export(os.path.join(OUT, "washing_posts.glb"))

# ---- garden shed with a separate hinged door and separate glass panes
reset(); mats(); sc = bpy.context.scene; H = root("garden_shed")
def obj(name, material, build, parent=H, origin=(0, 0, 0)):
    bm = bmesh.new(); build(bm); bmesh.ops.translate(bm, vec=Vector(origin) * -1, verts=bm.verts); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(MATS[material])
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.parent = parent; o.location = origin; return o
SW, SD, SH = 2.4, 1.8, 2.1
def walls(bm):
    for side, (ax, n, L, c) in {"back": ("x", 12, SW, (0, SD / 2)), "left": ("y", 9, SD, (-SW / 2, 0)), "right": ("y", 9, SD, (SW / 2, 0))}.items():
        for k in range(n):
            off = -L / 2 + L / n * (k + .5)
            if ax == "x": box(bm, (off, c[1], SH / 2), (L / n - .008, .03, SH))
            else: box(bm, (c[0], off, SH / 2), (.03, L / n - .008, SH))
    for k in range(12):                                                                  # front boards, with the door gap and a window gap
        off = -SW / 2 + SW / 12 * (k + .5)
        if -.15 < off < .75: continue
        if .75 < off < 1.15: box(bm, (off, -SD / 2, .45), (SW / 12 - .008, .03, .9)); box(bm, (off, -SD / 2, 1.9), (SW / 12 - .008, .03, .4)); continue
        box(bm, (off, -SD / 2, SH / 2), (SW / 12 - .008, .03, SH))
    for k in range(10): box(bm, (0, -SD / 2 - .05 + (SD + .1) / 10 * (k + .5), SH + .08 - .0), (SW + .2, (SD + .1) / 10 - .006, .03), rot=Matrix.Rotation(.08, 3, "X"))
obj("shed_walls", "wood", walls)
def frame(bm):
    for x in (-.15, .75): box(bm, (x, -SD / 2 - .02, 1.0), (.06, .05, 2.0))
    box(bm, (.3, -SD / 2 - .02, 2.0), (1.0, .05, .06))
    for z in (.9, 1.7): box(bm, (.95, -SD / 2 - .02, z), (.46, .05, .05))
    box(bm, (.95, -SD / 2 - .02, 1.3), (.04, .05, .8))
obj("shed_frames", "wood_dark", frame)
def door(bm):
    for k in range(5): box(bm, (-.12 + .85 / 5 * (k + .5), -SD / 2 - .03, .99), (.85 / 5 - .006, .035, 1.94))
    for z in (.3, 1.6): box(bm, (.3, -SD / 2 - .055, z), (.8, .02, .1))
    box(bm, (.3, -SD / 2 - .055, .95), (.95, .02, .09), rot=Matrix.Rotation(1.0, 3, "Y"))
obj("shed_door", "wood_dark", door, origin=(-.12, -SD / 2 - .03, 0))                     # origin ON the hinge line: rotate about Z to open
def pane(bm, x):                                                                         # a subdivided pane (6 x 10): real geometry for the shatter cuts
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1); bmesh.ops.scale(t, vec=(.18, .006, .76), verts=t.verts); bmesh.ops.subdivide_edges(t, edges=[e for e in t.edges if abs((e.verts[0].co - e.verts[1].co).y) < 1e-6], cuts=6)
    bmesh.ops.translate(t, vec=(x, -SD / 2 - .01, 1.3), verts=t.verts); from _blender_kit import merge; merge(bm, t)
for i, x in enumerate((.85, 1.05)): obj("shed_glass_%d" % i, "glass", lambda bm, x=x: pane(bm, x))
for ob in [o for o in sc.objects if o.type == "MESH"]:
    bpy.context.view_layer.objects.active = ob
    for o in sc.objects: o.select_set(o == ob)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.01); bpy.ops.object.mode_set(mode="OBJECT")
for o in sc.objects: o.select_set(True)
os.makedirs(OUT, exist_ok=True); fn = os.path.join(OUT, "garden_shed.glb"); bpy.ops.export_scene.gltf(filepath=fn, export_format="GLB", export_yup=True, export_apply=True)
print("EXPORTED", fn, "parts", len([o for o in sc.objects if o.type == "MESH"]))
