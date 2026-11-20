"""cart_army: reproduction of "How One Cart Stopped an Entire Army" shot by shot (reference: references/cart_army, breakdown in shots/*.md).
    blender -b --factory-startup --python shots/film.py -- <shot id> <out.blend> [--res 405x720] [--samples 32] [--still f:png ...] [--anim dir]"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
from kit import beach as fort, cast, col, key, move, ink, label, box, cyl, blob, fx
BK = os.path.join(fort.SKILL, "library", "blenderkit")

def bk(c, name, size, tex_max=1024):
    """a real BlenderKit model appended under a root empty at the origin, its largest side scaled to `size` metres"""
    with bpy.data.libraries.load(os.path.join(BK, name, name + ".blend"), link=False) as (src, dst): dst.objects = list(src.objects)
    objs = [o for o in dst.objects if o is not None]; root = bpy.data.objects.new("bk_" + name, None); c.objects.link(root)
    for o in objs:
        c.objects.link(o)
        if o.name.startswith("wdg"): o.hide_render = True
        if o.parent is None or o.parent not in objs: o.parent = root
    bpy.context.view_layer.update(); ms = [o for o in objs if o.type == "MESH" and not o.hide_render]; pts = [o.matrix_world @ Vector(v) for o in ms for v in o.bound_box]
    ext = max(max(p[k] for p in pts) - min(p[k] for p in pts) for k in range(3)); s = size / ext; root.scale = (s, s, s)
    for im in {n.image for o in ms for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image}:
        if max(im.size) > tex_max: k = tex_max / max(im.size); im.scale(max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k)))
    return root, {o.name: o for o in objs}

SF = os.path.join(fort.SKILL, "library", "assets", "sketchfab")
BRACE_ID = "d6a4c41ff34f4f638aeb8aec72a2f6ef"                                          # "Brace" (carpenter's brace), Sketchfab, CC-BY: the reference's tool

def brace(c, length=.62):
    """the carpenter's brace of the reference (a real model): black crank, wooden knob and handle; root at the tip of its bit, pointing +X"""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(SF, BRACE_ID, "gltf", "scene.gltf")); new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new("brace", None); c.objects.link(root); spin = bpy.data.objects.new("brace_spin", None); c.objects.link(spin); spin.parent = root
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = spin
    bpy.context.view_layer.update(); ms = [o for o in new if o.type == "MESH"]; pts = [o.matrix_world @ Vector(v) for o in ms for v in o.bound_box]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts); s = length / (x1 - x0); spin.scale = (s, s, s); spin.location = (-(x1 * s) - .13, 0, 0)
    for o in ms:
        for m in o.data.materials:
            b = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
            if b and m.name.startswith("Light"): b.inputs["Base Color"].default_value = (.025, .025, .03, 1); b.inputs["Metallic"].default_value = .7; b.inputs["Roughness"].default_value = .38   # blackened iron
    cyl("brace_bit", .009, .14, (-.065, 0, 0), ink("bit_steel", (.55, .55, .58), 0, .25), c, rot=(0, math.radians(90), 0), seg=10, parent=root)
    return root, spin

def wood(name, hexcol, tile=1.0):
    return fort.tex(name, "brown_planks_05", tile=tile, recolor=hexcol, value=1.0, normal=.6, spec=.25, macro=.1)

def board(c, at=(1.0, 0.0), holes=82):
    """THE HERO: the plank with its 82 drilled holes, held upright in a stand (ochre uprights with black iron clamps, pale wooden feet).
    The plank faces the engineer (-X). Returns (root, list of hole centres in world space)."""
    root = bpy.data.objects.new("board", None); c.objects.link(root); root.location = (at[0], at[1], 0); T, W, Hh, Z0 = .06, 1.05, 1.0, .42
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * T, v.co.y * W, v.co.z * Hh + Z0 + Hh / 2))
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=.006, segments=2, affect="EDGES")
    pl = fort.mesh_obj("plank", bm, wood("plank_wood", "#e6c690", .5), c, smooth=True); pl.parent = root
    cut = bmesh.new(); pts = []; nx, nz = 9, 10; k = 0
    for j in range(nz):
        for i in range(nx):
            if k >= holes: break
            y = -W / 2 + .1 + (W - .2) * i / (nx - 1) + (.03 if j % 2 else 0); z = Z0 + .09 + (Hh - .18) * j / (nz - 1); k += 1
            g = bmesh.ops.create_cone(cut, cap_ends=True, segments=14, radius1=.024, radius2=.024, depth=T * 3)
            bmesh.ops.rotate(cut, verts=g["verts"], cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.radians(90), 3, "Y")); bmesh.ops.translate(cut, verts=g["verts"], vec=(0, y, z)); pts.append((at[0], at[1] + y, z))
    co = fort.mesh_obj("plank_holes", cut, ink("hole_dark", (.05, .03, .02), 0, .9), c); co.parent = root; co.hide_render = True; co.display_type = "WIRE"
    md = pl.modifiers.new("holes", "BOOLEAN"); md.object = co; md.operation = "DIFFERENCE"; md.solver = "EXACT"
    och = wood("stand_ochre", "#e0a021", .9); pale = wood("stand_pale", "#e2cba0", .8); iron = ink("clamp_iron", (.03, .03, .035), 0, .45)
    for s in (-1, 1):
        box("stand_post", (.17, .17, 1.3), (0, s * (W / 2 + .1), .78), och, c, bevel=.012, parent=root); box("stand_foot", (.5, .24, .16), (0, s * (W / 2 + .1), .08), pale, c, bevel=.02, parent=root)
        box("stand_brace", (.1, .1, .5), (-.2, s * (W / 2 + .1), .3), pale, c, rot=(0, math.radians(-35), 0), bevel=.01, parent=root)
        for z in (1.32, .82): box("stand_clamp", (.19, .19, .16), (0, s * (W / 2 + .1), z), iron, c, bevel=.01, parent=root); cyl("clamp_knob", .035, .05, (-.11, s * (W / 2 + .1), z), wood("knob", "#7a4a22"), c, rot=(0, math.radians(90), 0), seg=12, parent=root)
    return root, pts

def chips(c, at, f0, f1, n=26, seed=3):
    """wood chips thrown by the bit: small pale curls that fly off and fall in the grass (they stay there)"""
    R = random.Random(seed); m = ink("chip_wood", (.86, .70, .45), 0, .8)
    for i in range(n):
        o = box("chip%02d" % i, (R.uniform(.012, .03), R.uniform(.008, .016), .003), (0, 0, -5), m, c, bevel=0); t0 = f0 + int((f1 - f0) * i / n); vx, vy, vz = R.uniform(-1.1, -.2), R.uniform(-.7, .7), R.uniform(.3, 1.6)
        for f in range(t0, t0 + 16):
            t = (f - t0) / 30; z = max(.02, at[2] + vz * t - 4.9 * t * t); o.location = (at[0] + vx * t, at[1] + vy * t, z); key(o, "location", f); key(o, "rotation_euler", f, (t * 19, t * 13, t * 7))

# ---------------------------------------------------------------------------------------------------------------- 01
def s01(n):
    """0-66 "He drilled 82 holes into the wood" (drilled 6, 82 14, holes 28, into 45, wood 58): the engineer cranks his drill into the plank in the grass
    before the fort wall; snap push to the bit (30-36), extreme close-up of the turning bit and the chips (44-56), then the camera climbs the wall
    past the banner (58-66) on its way over the rampart (shot 2)"""
    sc = kit.begin(n); Mo = fort.build(sc); O = col("L_OBJECTS"); brd, holes = board(O); brd.rotation_euler = (0, 0, math.radians(24)); q = holes[64]                                              # turned a little toward the lens, as in the reference: its drilled face shows
    ca, sa = math.cos(math.radians(24)), math.sin(math.radians(24)); hy = (q[0] - 1.0) * sa + q[1] * ca; hz = q[2]; bx = 1.0 + (q[0] - 1.0) * ca - q[1] * sa
    dr, spin = brace(O); dr.location = (bx - .03, hy, hz)                                            # the tip of the bit in the hole
    for fr in range(0, n, 2): key(dr, "location", fr, (bx - .03 + (.012 if (fr // 2) % 2 else 0), hy, hz))                             # he leans on it
    for fr in (0, n): key(spin, "rotation_euler", fr, ((fr / 30) * math.tau * 2.2, 0, 0))                                            # the crank goes round
    kit.linear(spin)
    chips(col("L_FX"), (bx - .05, hy, hz), 4, 60)
    cam = kit.camera([(0, (bx - .3, hy - 5.7, 1.05), (bx - .62, hy, 1.12), 32), (26, (bx - .28, hy - 5.55, 1.05), (bx - .6, hy, 1.12), 32),   # portrait frame: at 32 mm the picture is only 0.42 x distance wide (36, (.2, -2.2, 1.0), (bx - .15, hy, hz - .05), 36),
                      (44, (bx - .75, hy - 1.15, hz - .12), (bx - .22, hy, hz + .02), 40), (56, (bx - .73, hy - 1.1, hz - .11), (bx - .22, hy, hz + .03), 40), (62, (.2, -3.2, 2.4), (-1.6, 6, 4.4), 26), (n - 1, (-.2, -2.0, 5.0), (-1.9, 6, 7.0), 24)], n, amp=.006)
    kit.cards(sc, "01", cam, {"engineer": [(0, bx - 1.2, hy + .02)]}, fort.height)
    kit.finish(sc, Mo, haze=.12); return sc

# ---------------------------------------------------------------------------------------------------------------- 02
def palanquin(c):
    """the general's litter: a red lacquered platform with a gold rim on two long carrying poles, and the great parasol planted on it
    (olive canopy, red and yellow scalloped rim, red tassels)"""
    root = bpy.data.objects.new("palanquin", None); c.objects.link(root); red = ink("laq_red", (.62, .05, .04), 0, .35); gold = ink("laq_gold", (.85, .62, .1), 0, .35); wd = wood("pole_wood", "#6a4426")
    box("pal_floor", (1.5, 1.9, .16), (0, 0, 1.0), red, c, bevel=.02, parent=root); box("pal_rim", (1.6, 2.0, .06), (0, 0, 1.1), gold, c, bevel=.01, parent=root)
    for s in (-1, 1):
        cyl("pal_pole", .05, 4.4, (s * .72, 0, .93), wd, c, rot=(math.radians(90), 0, 0), seg=10, parent=root); box("pal_rail", (.05, 1.7, .3), (s * .72, 0, 1.3), red, c, bevel=.01, parent=root)
    ol = ink("par_olive", (.42, .40, .12), 0, .7); cyl("par_pole", .035, 4.2, (.55, -.5, 3.15), wd, c, seg=10, parent=root)
    cyl("par_canopy", 1.6, .42, (.55, -.5, 5.3), ol, c, r2=.1, seg=18, parent=root); cyl("par_under", 1.56, .03, (.55, -.5, 5.08), ol, c, seg=18, parent=root)
    cyl("par_rim_y", 1.63, .07, (.55, -.5, 5.13), ink("par_yellow", (.95, .75, .08), 0, .6), c, seg=18, parent=root); cyl("par_rim_r", 1.65, .05, (.55, -.5, 5.07), red, c, seg=18, parent=root)
    for k in range(18): a = k * math.tau / 18; cyl("par_tassel", .03, .16, (.55 + 1.62 * math.cos(a), -.5 + 1.62 * math.sin(a), 4.96), red, c, seg=6, parent=root)
    for k in range(12): a = k * math.tau / 12; cyl("par_rib", .012, 1.55, (.55 + .78 * math.cos(a), -.5 + .78 * math.sin(a), 5.2), wd, c, rot=(0, math.radians(76), a), seg=6, parent=root)
    return root

def s02(n):
    """66-177 "because down(77) the hill(92) an army(109) is marching(125) straight(134) for his fort(158)": the camera clears the rampart, dives down the
    slope and along the road to the head of the army (the general on his palanquin under the parasol, the yellow column and its dust behind him), holds
    on him as they march (40-74), then swings round: the general in three-quarter view with the fort on its hill behind him (84-111)"""
    import valley
    sc = kit.begin(n); Mo = valley.build(sc); O = col("L_OBJECTS"); H = valley.height; hx, hy0 = valley.HEAD; v = 1.3 / 30                      # they march up the road (+Y) at 1.3 m/s
    pal = palanquin(O); move(pal, ((0, hx, hy0, H(hx, hy0)), (n, hx, hy0 + v * n, H(hx, hy0 + v * n)))); kit.linear(pal)
    army = bpy.data.objects.new("army", None); O.objects.link(army); move(army, ((0, 0, 0, 0), (n, 0, v * n, 0))); kit.linear(army)
    cam = kit.camera([(0, (0, 14, 26), (0, -90, 0), 22), (12, (1.5, -12, 20), (0, -150, 0), 22), (30, (2.5, hy0 + 34, 9), (hx, hy0, 2.6), 24), (40, (1.6, hy0 + 10.5, 3.3), (hx + .1, hy0, 2.7), 30),
                      (74, (1.5, hy0 + 10.8 + v * 34, 3.2), (hx + .1, hy0 + v * 34, 2.7), 30), (84, (-2.4, hy0 - 6.5 + v * 84, 1.5), (1.6, hy0 + 3 + v * 84, 3.4), 28), (n - 1, (-2.2, hy0 - 6.3 + v * n, 1.5), (1.6, hy0 + 3.2 + v * n, 3.4), 28)], n, amp=.006, clip=6000.0)
    P = lambda dx, dy, dz=0.0: [(0, hx + dx, hy0 + dy, H(hx + dx, hy0 + dy) + dz), (n, hx + dx, hy0 + dy + v * n, H(hx + dx, hy0 + dy + v * n) + dz)]
    C = kit.cards(sc, "02", cam, {"general": P(0, 0, 1.12), "bearer_a": P(-1.25, 1.5), "bearer_b": P(1.25, 1.7), "bearer_c": P(.15, 2.9), "crowd": P(-2.6, -3.0)}, None)
    src = bpy.data.objects["Card_crowd"]; R = random.Random(2)                                        # the column: hundreds of the same soldier, each a card of its own
    for i in range(260):
        o = src.copy(); O.objects.link(o); o.animation_data_clear(); row, k = divmod(i, 10); o.parent = army; x = -9 + k * 2.0 + R.uniform(-.4, .4); y = hy0 - 5.5 - row * 2.2 + R.uniform(-.4, .4); o.location = (x, y, H(x, y)); o.rotation_euler = src.rotation_euler
    fx(sc, [{"type": "dust_burst", "name": "march_dust_%d" % i, "at": [R.uniform(-14, 14), hy0 - 30 - i * 9, 1.0], "frame": -30 + i * 3, "count": 6, "radius": 9.0, "height": 5.0, "seed": 20 + i, "life": 200, "color": [.86, .82, .7]} for i in range(6)])
    kit.finish(sc, Mo, haze=.3); return sc

SHOTS = {"01": s01, "02": s02}
if __name__ == "__main__":
    sid = kit.A[0]; n = cast.SHOTS[sid][0] if sid in cast.SHOTS else 60; sc = SHOTS[sid](n); kit.output(sc, kit.A[1])
