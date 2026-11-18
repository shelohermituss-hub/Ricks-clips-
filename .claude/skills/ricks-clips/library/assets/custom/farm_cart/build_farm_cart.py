"""Normandy two-wheel farm cart (Mission 2 prototype, 2026-11-18): the DESTRUCTIBLE test asset.
Every structural piece is its own named object so rc.physics can fracture, detach and simulate it:
  cart_plank_00..07 (bed floor), cart_side_L/R_0..1 (side boards), cart_end_F/B, cart_rail_L/R (frame), cart_cross_0..3,
  cart_shaft_L/R (long tapered shafts), cart_axle, cart_wheel_L/R (rim of 12 felloes + iron tyre + hub + 12 spokes, one object each),
  cart_stake_* (side stakes). Materials: wood (planks), wood_dark (frame, shafts), iron (tyres, hub bands, straps).
Real size: bed 2.4 x 1.3 m at 0.95 m, wheels 1.3 m diameter. X forward (shafts toward +X), Z up, ground at 0.
    blender -b --python build_farm_cart.py -- <out dir>"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _blender_kit import reset, mat, box, cyl, torus, MATS  # noqa: E402

OUT = sys.argv[sys.argv.index("--") + 1]
reset(); sc = bpy.context.scene
mat("wood", "#8a6a44", .78); mat("wood_dark", "#5a4330", .7); mat("iron", "#2e2c2a", .45, .6)
root = bpy.data.objects.new("farm_cart", None); sc.collection.objects.link(root)

def part(name, material, build, bevel=.0):
    bm = bmesh.new(); build(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(MATS[material])
    if isinstance(material, str) and material == "iron":
        for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); ob.parent = root
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"; b.angle_limit = math.radians(40)
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me2 = bpy.data.meshes.new_from_object(ev); ob.modifiers.clear(); ob.data = me2
    return ob

Z, L, W = .95, 2.4, 1.3                      # bed height, length, width
for i in range(8):                            # floor planks along X, slightly uneven
    y = -W / 2 + W / 8 * (i + .5); part("cart_plank_%02d" % i, "wood", lambda bm, y=y, i=i: box(bm, (0, y, Z + .02), (L, W / 8 - .012, .04 + .004 * (i % 3))), bevel=.006)
for s, side in ((-1, "R"), (1, "L")):
    for k in range(2): part("cart_side_%s_%d" % (side, k), "wood", lambda bm, s=s, k=k: box(bm, (0, s * (W / 2 + .02), Z + .14 + k * .2), (L, .035, .17)), bevel=.006)
    part("cart_rail_" + side, "wood_dark", lambda bm, s=s: box(bm, (.1, s * (W / 2 - .08), Z - .06), (L + .3, .11, .1)), bevel=.008)
    part("cart_shaft_" + side, "wood_dark", lambda bm, s=s: cyl(bm, (L / 2 + 1.25, s * .42, Z - .15), (1, -s * .14, -.12), .05, 2.6, seg=10, r2=.035))
    for k in range(4): part("cart_stake_%s_%d" % (side, k), "wood_dark", lambda bm, s=s, k=k: box(bm, (-L / 2 + .2 + k * .66, s * (W / 2 + .045), Z + .25), (.06, .05, .52)), bevel=.004)
for e, x in (("F", L / 2 + .02), ("B", -L / 2 - .02)): part("cart_end_" + e, "wood", lambda bm, x=x: box(bm, (x, 0, Z + .2), (.035, W + .06, .36)), bevel=.006)
for k in range(4): part("cart_cross_%d" % k, "wood_dark", lambda bm, k=k: box(bm, (-L / 2 + .25 + k * .63, 0, Z - .07), (.09, W - .1, .08)), bevel=.006)
R = .65                                       # wheel radius; wheels at the bed's mid length
part("cart_axle", "iron", lambda bm: cyl(bm, (0, 0, R), (0, 1, 0), .045, W + .5, seg=14))
def wheel(bm, y):
    torus(bm, (0, y, R), (0, 1, 0), R - .04, .045, seg=36, rs=8)                       # wooden rim (felloes)
    torus(bm, (0, y, R), (0, 1, 0), R + .005, .02, seg=48, rs=6)                       # iron tyre
    cyl(bm, (0, y, R), (0, 1, 0), .11, .2, seg=16)                                       # hub
    for k in range(12):                                                                  # spokes
        a = 2 * math.pi * k / 12; d = Vector((math.cos(a), 0, math.sin(a)))
        c = Vector((0, y, R)) + d * (R / 2 + .02); cyl(bm, c, d, .025, R - .16, seg=8, r2=.02)
for s, side in ((-1, "R"), (1, "L")): part("cart_wheel_" + side, "wood", lambda bm, s=s: wheel(bm, s * (W / 2 + .2)))
for o in sc.objects:
    if o.type == "MESH":
        for p in o.data.polygons: p.use_smooth = o.name.startswith(("cart_wheel", "cart_shaft", "cart_axle"))
os.makedirs(OUT, exist_ok=True)
for ob in [o for o in sc.objects if o.type == "MESH"]:
    bpy.context.view_layer.objects.active = ob
    for o in sc.objects: o.select_set(o == ob)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.01); bpy.ops.object.mode_set(mode="OBJECT")
tris = sum(len(p.vertices) - 2 for o in sc.objects if o.type == "MESH" for p in o.data.polygons)
for o in sc.objects: o.select_set(True)
fn = os.path.join(OUT, "farm_cart.glb"); bpy.ops.export_scene.gltf(filepath=fn, export_format="GLB", export_yup=True, export_apply=True)
print("EXPORTED", fn, "parts", len([o for o in sc.objects if o.type == "MESH"]), "tris", tris)
