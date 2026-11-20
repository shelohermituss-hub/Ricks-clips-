"""cart_army shot 2: THE VALLEY below the fort (reference: references/cart_army/shots/s02_hi.jpg).
Layout (metres): the fort wall runs along X at y = 0 on its hill (z = 7), gate at x = 0; a dirt road goes down the slope and across the plain
along -Y; the army marches up it (its head near y = -120). The plain is a patchwork of small fields (greens, straw yellow, olive) with
hedges, a river, tree clumps; rolling green hills behind, grey rocky peaks far away; a deep blue sky with streaks of white cloud.
    import valley; Mo = valley.build(scene)"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
import fort
from fort import look, geo, tex, col, mesh_obj, srgb, street, SKILL, _flat, _tint

MOOD = dict(az=-150, el=48, energy=8.5, hdri="kloofendal_48d_partly_cloudy_puresky", light=.55, glow=.3, exposure=-.3, sat=1.18, contrast="Medium Contrast")
HEAD = (0.0, -80.0)                                                                     # where the general's palanquin is at frame 0 of the close view

def height(x, y):
    t = min(1.0, max(0.0, (y + 75.0) / 60.0)); t = t * t * (3 - 2 * t); return 7.0 * t + .25 * math.sin(x * .05) * (1 - t)

def ground(c):
    bm = bmesh.new(); nx, ny = 120, 360; V = [[bm.verts.new((-600 + 1200 * i / nx, -1400 + 1440 * j / ny, height(-600 + 1200 * i / nx, -1400 + 1440 * j / ny))) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx): bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    mesh_obj("valley_ground", bm, tex("valley_grass", "brown_mud_02", tile=6.0, recolor="#5f9a2c", value=1.0, normal=.8, spec=.1, macro=.25), c, smooth=True)
    rd = bmesh.new(); pv = None
    for k in range(120):                                                                 # the dirt road, following the ground
        y = 2 - 420 * k / 119; x = 3.5 * math.sin(y * .012) * min(1.0, max(0.0, (-y - 150) / 100)); a, b = rd.verts.new((x - 2.8, y, height(x, y) + .16)), rd.verts.new((x + 2.8, y, height(x, y) + .16))
        if pv: rd.faces.new((pv[0], pv[1], b, a))
        pv = (a, b)
    mesh_obj("valley_road", rd, tex("valley_road", "brown_mud_02", tile=2.0, recolor="#8a6540", value=1.0, normal=1.4, spec=.12, macro=.2), c, smooth=True)

def fields(c, seed=7):
    """the patchwork: hundreds of small plots, each one colour, with a darker hedge line between them (seen from the air and from the road)"""
    R = random.Random(seed); cols = ["#6fae2e", "#8cc23a", "#4f9a2a", "#d6c84a", "#ead867", "#9fbf3e", "#3f8a2c", "#c9b540", "#7fb83a", "#e2d060"]; bm = bmesh.new(); lay = bm.loops.layers.color.new("tint"); hed = bmesh.new(); y = -112.0
    while y > -900:
        h = R.uniform(14, 30); x = -520.0 + R.uniform(0, 30)
        while x < 520:
            w = R.uniform(18, 46)
            if abs(x + w / 2) > 9 + w / 2:
                cc = srgb(R.choice(cols)); k = R.uniform(.85, 1.1); q = [(x + 1, y - h + 1), (x + w - 1, y - h + 1), (x + w - 1, y - 1), (x + 1, y - 1)]
                f = bm.faces.new([bm.verts.new((px, py, height(px, py) + .05)) for px, py in q])
                for lp in f.loops: lp[lay] = (cc[0] * k, cc[1] * k, cc[2] * k, 1)
                if R.random() < .5:
                    g = bmesh.ops.create_cube(hed, size=1.0)
                    for v in g["verts"]: v.co = Vector((v.co.x * w + x + w / 2, v.co.y * 1.6 + y, v.co.z * 1.6 + .8))
            x += w
        y -= h
    m = bpy.data.materials.new("field_paint"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "tint"
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .6; mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = .35
    nt.links.new(vc.outputs["Color"], mx.inputs[6]); nt.links.new(nz.outputs["Color"], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .95
    mesh_obj("valley_fields", bm, m, c); mesh_obj("valley_hedges", hed, _flat("hedge_green", (.05, .16, .04), .95), c)
    rv = bmesh.new(); pv = None
    for k in range(80):                                                                  # a river crossing the plain
        x = -560 + 1120 * k / 79; yy = -330 + 40 * math.sin(x * .011) + 18 * math.sin(x * .03); a, b2 = rv.verts.new((x, yy - 7, .12)), rv.verts.new((x, yy + 7, .12))
        if pv: rv.faces.new((pv[0], pv[1], b2, a))
        pv = (a, b2)
    wm = _flat("river_blue", (.10, .32, .62), .08); mesh_obj("valley_river", rv, wm, c)

def relief(c, seed=3):
    """rolling green hills behind the plain, then grey rocky peaks (three planes of depth)"""
    R = random.Random(seed); gm = _flat("hill_green", (.10, .34, .07), .95); nt = gm.node_tree; nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 6; rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = .4; rp.color_ramp.elements[0].color = (.03, .16, .03, 1); rp.color_ramp.elements[1].position = .62; rp.color_ramp.elements[1].color = (.20, .50, .10, 1); nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); rk = _flat("peak_grey", (.42, .44, .46), .9); tm = _flat("tree_green", (.04, .2, .05), .95)
    for i in range(46):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0); a, b = R.uniform(2, 5), R.uniform(2, 5)
        for v in bm.verts: v.co *= 1 + .16 * math.sin(v.co.x * a + i) * math.cos(v.co.y * b)
        far = i >= 30; o = mesh_obj("peak%02d" % i if far else "hill%02d" % i, bm, rk if far else gm, c, smooth=True)
        if far: o.location = (R.uniform(-1500, 1500), R.uniform(-2600, -1900), -20); o.scale = (R.uniform(160, 300), R.uniform(140, 220), R.uniform(260, 420))
        else: o.location = (R.uniform(-1200, 1200), R.uniform(-1700, -950), -30); o.scale = (R.uniform(180, 380), R.uniform(160, 300), R.uniform(90, 200))
    for i in range(160):                                                                 # tree clumps in the plain
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0); x, y = R.uniform(-520, 520), R.uniform(-900, -160)
        if abs(x) < 14: continue
        o = mesh_obj("clump%03d" % i, bm, tm, c, smooth=True); s = R.uniform(4, 9); o.location = (x, y, height(x, y) + s * .5); o.scale = (s * R.uniform(1, 1.8), s * R.uniform(1, 1.6), s * .8)

def fort_outside(c):
    """the fort seen from the road: a long crenellated curtain wall, round towers, the gate with its roofed gatehouse"""
    st = fort.stone(); z = 7.0
    for nm, x0, L in (("L", -90.0, 86.5), ("R", 3.5, 86.5)): fort.blocks("out_wall_" + nm, c, (x0, 0, z), (1, 0, 0), (0, -1, 0), L, 9.0, st, seed=11 if nm == "L" else 12, row=.7)
    fort.blocks("out_lintel", c, (-3.5, 0, z + 5.2), (1, 0, 0), (0, -1, 0), 7.0, 3.8, st, seed=13, row=.7)
    for x in range(-88, 90, 3):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts: v.co = Vector((v.co.x * 1.5, v.co.y * .7, v.co.z * 1.2))
        _tint(bm, .9); o = mesh_obj("out_merlon", bm, st, c); o.location = (x, .1, z + 9.6)
    for x in (-46, -16, 16, 46):                                                         # round towers
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=4.6, radius2=4.2, depth=13.0); _tint(bm, .86); o = mesh_obj("out_tower", bm, st, c, smooth=True); o.location = (x, -1.5, z + 6.5)
        try: o.data.set_sharp_from_angle(angle=.9)
        except Exception: pass
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=5.0, radius2=5.0, depth=1.4); _tint(bm, .8); mesh_obj("out_tower_top", bm, st, c, smooth=True).location = (x, -1.5, z + 13.5)
    roof = _flat("roof_tile", (.10, .11, .13), .5); red = _flat("lacquer_red", (.55, .05, .04), .4)
    for sx in (-2.6, 2.6):
        for sy in (-.6, 1.8): bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=.22, radius2=.22, depth=3.4); mesh_obj("gate_col", bm, red, c, smooth=True).location = (sx, sy, z + 10.7)
    for k, (w, zz) in enumerate(((9.5, 12.6), (7.0, 13.5), (3.6, 14.3))):                   # the curved tiled roof in three courses
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * (w * .62), v.co.z * .5 + .35 * abs(v.co.x) ** 1 * (1 if v.co.z < 0 else 0)))
        mesh_obj("gate_roof%d" % k, bm, roof, c).location = (0, .6, z + zz)
    gd = bmesh.new(); gd.faces.new([gd.verts.new(p) for p in ((-3.5, .4, z), (3.5, .4, z), (3.5, .4, z + 5.2), (-3.5, .4, z + 5.2))]); mesh_obj("out_gate_dark", gd, _flat("gate_dark2", (.02, .018, .016)), c)

def grass(c, at, r=14.0, n=26000, seed=5):
    src = street.blade_clump(); m = bpy.data.materials.get("grass_blades")
    if m and not m.get("rc_recoloured"):
        cr = [n_ for n_ in m.node_tree.nodes if n_.type == "VALTORGB"][0].color_ramp; cr.elements[0].color = (*srgb("#4a8426"), 1); cr.elements[1].color = (*srgb("#c6e060"), 1); m["rc_recoloured"] = 1
    for k, (x0, x1) in enumerate(((at[0] - r, at[0] - 3.0), (at[0] + 3.0, at[0] + r))):
        P, Rt, Sc = geo.scatter_points({"polygon": [[x0, at[1] - r], [x1, at[1] - r], [x1, at[1] + r * 1.4], [x0, at[1] + r * 1.4]]}, n // 2, seed + k, scale_range=(.9, 2.4))
        P = [(p[0], p[1], height(p[0], p[1])) for p in P]; geo.instancer("vgrass_%d" % k, P, src, c, Rt, Sc, wind=.05)

def build(scene):
    c = col("L_SET"); Mo = dict(MOOD); look.SUN[0], look.SUN[1] = Mo["az"], Mo["el"]
    look.sky_hdri(scene, strength=1.0, hdri=Mo["hdri"], glow=Mo["glow"], light=Mo["light"]); look.sun(scene, energy=Mo["energy"])
    nt = scene.world.node_tree; N, L = nt.nodes, nt.links                                # this reference's sky is a DEEP saturated blue with white streaks
    pick = [n for n in N if n.type == "MIX" and n.inputs[0].links and n.inputs[0].links[0].from_node.type == "LIGHT_PATH" and n.data_type == "RGBA"]
    if pick:
        src = pick[0].inputs[7].links[0].from_socket; hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 1.35; hs.inputs["Value"].default_value = 1.5; L.new(src, hs.inputs["Color"]); L.new(hs.outputs["Color"], pick[0].inputs[7])
    ground(c); fields(c); relief(c); fort_outside(c); grass(c, HEAD); return Mo
