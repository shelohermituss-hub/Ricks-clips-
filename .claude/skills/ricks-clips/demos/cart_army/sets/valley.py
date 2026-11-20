"""cart_army shot 2: THE VALLEY below the fort (reference: references/cart_army/shots/s02_hi.jpg). Rebuilt after CB's corrections of 2026-11-20:
  * the fort stands ON A HILL (16 m), the road comes down from its gate in an S and the army CLIMBS it: nothing is seen head-on
  * the ground is a grass TEXTURE; real grass tufts are added only near the lens
  * colours are the reference's own (sampled): grass #77b336/#68993f/#52a72f, road #947848, hills #376d3f-#4f823e, sky #919fc6-#96abde, sunlit stone #ebe2d3
  * the far country is real relief (ridges and folds from fractal noise: woods, meadows, grey rock high up), not smooth bumps
  * detail only where a camera of this shot looks
Layout (metres): fort wall along X at y = 0 on the hill top (gate at x = 0, facing -Y); road(s) = point of the road s metres below the gate.
    import valley; Mo = valley.build(scene)"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, noise
import fort
from fort import look, geo, tex, col, mesh_obj, srgb, street, SKILL, _flat, _tint

MOOD = dict(az=-100, el=56, energy=7.0, hdri="kloofendal_48d_partly_cloudy_puresky", light=.75, glow=.25, exposure=-.15, sat=1.12, contrast="Medium Contrast")
HILL = 16.0; HEAD_S = 72.0                                                               # the general is 72 m down the road at frame 0

def road(s):
    t = s / 200.0; return 26.0 * math.sin(t * math.tau * .95) * min(1.0, s / 25.0), -6.0 - s * .93

def road_dir(s):
    a, b = road(s - .5), road(s + .5); d = Vector((a[0] - b[0], a[1] - b[1])).normalized(); return d                      # unit vector pointing UP the road (toward the gate)

def height(x, y):
    d = math.hypot(x, y - 15.0); t = min(1.0, max(0.0, 1.0 - (d - 45.0) / 80.0)); t = t * t * (3 - 2 * t)
    return HILL * t + .5 * math.sin(x * .031 + 1.0) * math.sin(y * .027) * (1 - t)

def ground(c):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new(); nx, ny = 240, 170; X0, X1, Y0, Y1 = -620.0, 620.0, -760.0, 110.0
    V = [[bm.verts.new((X0 + (X1 - X0) * i / nx, Y0 + (Y1 - Y0) * j / ny, height(X0 + (X1 - X0) * i / nx, Y0 + (Y1 - Y0) * j / ny))) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            f = bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
            for lp in f.loops: lp[uv].uv = (lp.vert.co.x * .25, lp.vert.co.y * .25)
    mesh_obj("valley_ground", bm, tex("valley_grass", "leafy_grass", tile=3.0, recolor="#6aa838", value=1.0, normal=1.2, spec=.08, macro=.3), c, smooth=True)   # THE GRASS IS A TEXTURE
    rd = bmesh.new(); pv = None
    for k in range(0, 420):                                                              # the dirt road, an S down the hill and across the plain
        s = k * 1.0; x, y = road(s); d = road_dir(s); nx_, ny_ = -d.y, d.x; w = 2.9
        a, b = rd.verts.new((x - nx_ * w, y - ny_ * w, height(x - nx_ * w, y - ny_ * w) + .14)), rd.verts.new((x + nx_ * w, y + ny_ * w, height(x + nx_ * w, y + ny_ * w) + .14))
        if pv: rd.faces.new((pv[0], pv[1], b, a))
        pv = (a, b)
    mesh_obj("valley_road", rd, tex("valley_road", "brown_mud_02", tile=2.0, recolor="#9a7f50", value=1.0, normal=1.6, spec=.1, macro=.25), c, smooth=True)

def fields(c, seed=7):
    """the patchwork of the plain: small plots, each one colour of the reference (greens and straw yellows), dark hedge lines, a blue river"""
    R = random.Random(seed); cols = ["#52a72f", "#6aa838", "#77b336", "#c9c24e", "#dccf66", "#8fbd3c", "#3f8a2c", "#b9ae44", "#e3d874", "#5f9f34"]; bm = bmesh.new(); lay = bm.loops.layers.color.new("tint"); hed = bmesh.new(); y = -150.0
    while y > -470:
        h = R.uniform(9, 20); x = -400.0 + R.uniform(0, 12)
        while x < 400:
            w = R.uniform(10, 26); rx, ry = road(-(y + 6) / .93)
            if abs(x + w / 2 - rx) > 6 + w / 2 and not (-312 < y < -286):
                cc = srgb(R.choice(cols)); k = R.uniform(.9, 1.08); q = [(x + .5, y - h + .5), (x + w - .5, y - h + .5), (x + w - .5, y - .5), (x + .5, y - .5)]
                f = bm.faces.new([bm.verts.new((px, py, height(px, py) + .06)) for px, py in q])
                for lp in f.loops: lp[lay] = (cc[0] * k, cc[1] * k, cc[2] * k, 1)
                if R.random() < .35:
                    g = bmesh.ops.create_cube(hed, size=1.0)
                    for v in g["verts"]: v.co = Vector((v.co.x * w + x + w / 2, v.co.y * 1.2 + y, v.co.z * 1.4 + .7 + height(x, y)))
            x += w
        y -= h
    m = bpy.data.materials.new("field_paint"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "tint"
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 3.0; wv.inputs["Distortion"].default_value = 1.0; mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = .22   # furrows
    nt.links.new(vc.outputs["Color"], mx.inputs[6]); nt.links.new(wv.outputs["Color"], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .95
    mesh_obj("valley_fields", bm, m, c); mesh_obj("valley_hedges", hed, _flat("hedge_green", (.04, .15, .05), .95), c)
    rv = bmesh.new(); pv = None
    for k in range(120):
        x = -560 + 1120 * k / 119; yy = -299 + 5 * math.sin(x * .02); a, b2 = rv.verts.new((x, yy - 6, height(x, yy) + .1)), rv.verts.new((x, yy + 6, height(x, yy) + .1))
        if pv: rv.faces.new((pv[0], pv[1], b2, a))
        pv = (a, b2)
    mesh_obj("valley_river", rv, _flat("river_blue", (.16, .36, .66), .08), c)
    tm = _flat("tree_green", (.05, .22, .07), .95)
    for i in range(150):
        x, yy = R.uniform(-400, 400), R.uniform(-470, -150)
        if abs(x - road(-(yy + 6) / .93)[0]) < 12: continue
        bt = bmesh.new(); bmesh.ops.create_icosphere(bt, subdivisions=2, radius=1.0); o = mesh_obj("clump%03d" % i, bt, tm, c, smooth=True); s = R.uniform(2.5, 5.5); o.location = (x, yy, height(x, yy) + s * .6); o.scale = (s * R.uniform(1, 1.6), s * R.uniform(1, 1.5), s * .9)

def relief(c):
    """the far country: REAL relief from fractal noise (ridges, folds, valleys), wooded green low down (#376d3f-#4f823e), grey rock on the peaks"""
    bm = bmesh.new(); nx, ny = 200, 130; X0, X1, Y0, Y1 = -2800.0, 2800.0, -3600.0, -440.0; V = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x, y = X0 + (X1 - X0) * i / nx, Y0 + (Y1 - Y0) * j / ny; amp = min(1.0, max(0.0, (-y - 470) / 500.0)) ** 1.3; far = min(1.0, max(0.0, (-y - 1500) / 1200.0))
            n1 = noise.fractal(Vector((x * .0016, y * .0016, .3)), 1.0, 2.1, 6); rid = 1.0 - abs(noise.fractal(Vector((x * .0011 + 7, y * .0011, 1.7)), .9, 2.0, 5))
            row.append(bm.verts.new((x, y, amp * (70 + 90 * n1 + (130 + 520 * far) * rid ** 2.2 * (.35 + .65 * far)) - 6)))
        V.append(row)
    for j in range(ny):
        for i in range(nx): bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    m = bpy.data.materials.new("relief_paint"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = .95
    geo_ = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo_.outputs["Position"], sep.inputs[0]); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .012; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = .65; L.new(geo_.outputs["Position"], nz.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements; e[0].position = .38; e[0].color = (*srgb("#2c5f36"), 1); e[1].position = .62; e[1].color = (*srgb("#5a9440"), 1); L.new(nz.outputs["Fac"], rp.inputs["Fac"])       # woods / meadows
    nrm = N.new("ShaderNodeSeparateXYZ"); L.new(geo_.outputs["Normal"], nrm.inputs[0])
    hh = N.new("ShaderNodeMapRange"); hh.inputs["From Min"].default_value = 300; hh.inputs["From Max"].default_value = 470; L.new(sep.outputs["Z"], hh.inputs["Value"])
    sl = N.new("ShaderNodeMapRange"); sl.inputs["From Min"].default_value = .86; sl.inputs["From Max"].default_value = .62; L.new(nrm.outputs["Z"], sl.inputs["Value"])                                                    # steep = bare rock
    mxf = N.new("ShaderNodeMath"); mxf.operation = "MULTIPLY"; L.new(hh.outputs[0], mxf.inputs[0]); L.new(sl.outputs[0], mxf.inputs[1])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; L.new(mxf.outputs[0], mx.inputs[0]); L.new(rp.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = (*srgb("#9aa0a4"), 1); L.new(mx.outputs[2], b.inputs["Base Color"])
    mesh_obj("valley_relief", bm, m, c, smooth=True)

def stone_far():
    """the fort seen from the road: dressed blocks as a BRICK TEXTURE with a little relief (at 50 m a block is a few pixels: no geometry needed)"""
    m = bpy.data.materials.get("fort_stone_far")
    if m: return m
    m = bpy.data.materials.new("fort_stone_far"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = .85
    tc = N.new("ShaderNodeTexCoord"); br = N.new("ShaderNodeTexBrick"); br.inputs["Color1"].default_value = (*srgb("#d8cfbf"), 1); br.inputs["Color2"].default_value = (*srgb("#c3b9a6"), 1); br.inputs["Mortar"].default_value = (*srgb("#6f675c"), 1)
    br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = .012; br.inputs["Brick Width"].default_value = 1.15; br.inputs["Row Height"].default_value = .55; br.offset = .5
    mp = N.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (math.radians(90), 0, 0); L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], br.inputs["Vector"]); L.new(br.outputs["Color"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .5; bp.inputs["Distance"].default_value = .05; inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; L.new(br.outputs["Fac"], inv.inputs[1]); L.new(inv.outputs[0], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def fort_outside(c):
    """the fort on its hill: curtain wall with battlements, an arched gate between two round towers, the roofed pavilion over the gate
    (a real model: "Chinese pavilion", Sketchfab b0f6c1fb, CC-BY), two more towers along the wall, the tall blue banner"""
    st = stone_far(); z = HILL; P_ = dict(c=c)
    def bx(name, size, loc, mat=st):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        o = mesh_obj(name, bm, mat, c); o.location = loc; return o
    for sx in (-1, 1): bx("out_wall", (72.0, 2.2, 8.0), (sx * 39.0, 0, z + 4.0))
    bx("out_lintel", (6.0, 2.2, 3.0), (0, 0, z + 6.5)); bx("gate_dark", (6.0, .3, 5.2), (0, .9, z + 2.6), _flat("gate_dark2", (.02, .018, .016)))
    for i in range(9):                                                                   # the arch stones
        a = math.pi * (i + .5) / 9; o = bx("out_voussoir", (.75, 2.4, .7), (3.0 * math.cos(a) * .92, -.05, z + 2.6 + 2.75 * math.sin(a))); o.rotation_euler = (0, -a, 0)
    for sx in (-1, 1): bx("gate_jamb", (.7, 2.4, 2.8), (sx * 2.85, -.05, z + 1.4))
    x = -74.0
    while x < 75:
        if abs(x) > 3.5: bx("out_merlon", (1.2, .6, 1.0), (x, -.8, z + 8.5))
        x += 2.4
    for x, r, hgt in ((-7.5, 3.6, 11.5), (7.5, 3.6, 11.5), (-44, 4.2, 11.0), (44, 4.2, 11.0)):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=r, radius2=r * .93, depth=hgt); o = mesh_obj("out_tower", bm, st, c, smooth=True); o.location = (x, -1.6, z + hgt / 2)
        try: o.data.set_sharp_from_angle(angle=.9)
        except Exception: pass
        for k in range(10): a = k * math.tau / 10; bx("tower_merlon", (.9, .5, .9), (x + (r - .3) * math.cos(a), -1.6 + (r - .3) * math.sin(a), z + hgt + .45)).rotation_euler = (0, 0, a + math.pi / 2)
    pv = fort.gltf(c, "b0f6c1fb43e744ec876faecaba3d4925", 11.0, (0, .6, z + 8.0), 0.0)                                   # the pavilion over the gate
    bx("flag_pole", (.12, .12, 9.0), (-7.5, -1.6, z + 16.0), _flat("pole_dark", (.08, .06, .05))); fl = bx("flag_blue", (1.1, .05, 5.0), (-6.9, -1.6, z + 17.6), _flat("flag_blue", (.05, .2, .75), .8))

def tufts(c, zones, seed=5):
    """a FEW real grass tufts over the texture, only near the lens"""
    src = street.blade_clump(); m = bpy.data.materials.get("grass_blades")
    if m and not m.get("rc_recoloured"):
        cr = [n_ for n_ in m.node_tree.nodes if n_.type == "VALTORGB"][0].color_ramp; cr.elements[0].color = (*srgb("#4f8a2a"), 1); cr.elements[1].color = (*srgb("#9fd04a"), 1); m["rc_recoloured"] = 1
    for k, (poly, n) in enumerate(zones):
        P, Rt, Sc = geo.scatter_points({"polygon": poly}, n, seed + k, scale_range=(1.0, 2.6)); keep = [i for i, p in enumerate(P) if min(math.hypot(p[0] - road(s)[0], p[1] - road(s)[1]) for s in range(0, 200, 3)) > 3.3]
        geo.instancer("vgrass_%d" % k, [(P[i][0], P[i][1], height(P[i][0], P[i][1])) for i in keep], src, c, [Rt[i] for i in keep], [Sc[i] for i in keep], wind=.05)

def build(scene):
    c = col("L_SET"); Mo = dict(MOOD); look.SUN[0], look.SUN[1] = Mo["az"], Mo["el"]
    look.sky_hdri(scene, strength=1.0, hdri=Mo["hdri"], glow=Mo["glow"], light=Mo["light"]); look.sun(scene, energy=Mo["energy"])
    nt = scene.world.node_tree; N, L = nt.nodes, nt.links                                # the reference's sky: a soft periwinkle blue (#919fc6-#96abde) with white streaks, never navy
    pick = [n for n in N if n.type == "MIX" and n.inputs[0].links and n.inputs[0].links[0].from_node.type == "LIGHT_PATH" and n.data_type == "RGBA"]
    if pick:
        src = pick[0].inputs[7].links[0].from_socket; hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = .7; hs.inputs["Value"].default_value = 2.0; L.new(src, hs.inputs["Color"]); L.new(hs.outputs["Color"], pick[0].inputs[7])
    ground(c); fields(c); relief(c); fort_outside(c); return Mo
