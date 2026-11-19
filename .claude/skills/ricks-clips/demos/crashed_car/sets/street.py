"""Street set (crashed_car, 2026-11-19): the suburban street of shots 1, 5-9, 11, 13, built FOR THE CAMERA (light: a few hundred objects).
Look target (references/crashed_car/ANALYSE_FR.md §4): stylised TV-feature 3D, soft rounded shapes, saturated colours, cloud-ball trees,
mint house with a red/white target painted on the garage door, deep-blue sky with big white clouds, hard sun with soft-edged shadows.
Layout (metres): road along X at y=-10 (7 m wide), sidewalk y=-6.5..-5, hero driveway x in [-3, 3] from the sidewalk to the garage door
(y = 5), hero house behind (garage front at y=5), lawns both sides, wooden fence behind (y=17), neighbour houses at x=-17 and x=+17.
    from street import build; build(scene, tod="day"|"dusk")"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

R = random.Random(11)
def srgb(h): return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))

def col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def mat(name, hexcol, rough=.6, metal=0.0, bump=None):
    """principled material; bump = (kind, scale, strength): 'siding' horizontal lap boards, 'noise' fine grain, 'panel' garage panels"""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if bump:
        kind, sc, st = bump; tc = nt.nodes.new("ShaderNodeTexCoord"); bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = st
        if kind in ("siding", "panel"):
            w = nt.nodes.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"; w.wave_profile = "SAW"; w.inputs["Scale"].default_value = sc
            nt.links.new(tc.outputs["Object"], w.inputs["Vector"]); nt.links.new(w.outputs["Fac"], bp.inputs["Height"])
        else:
            n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = sc; n.inputs["Detail"].default_value = 6
            nt.links.new(tc.outputs["Object"], n.inputs["Vector"]); nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
            mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = .18
            nt.links.new(n.outputs["Fac"], mix.inputs[7]); mix.inputs[6].default_value = (*srgb(hexcol), 1); nt.links.new(mix.outputs[2], b.inputs["Base Color"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def stains(m, hexcol, scale, amount):
    """large-scale blotches (oil stains on concrete, patches on asphalt, sun-bleached patches on the lawn): a second noise mixed into the colour"""
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
    tc = nt.nodes.new("ShaderNodeTexCoord"); n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"]); cr = nt.nodes.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = .55; cr.inputs["From Max"].default_value = .75
    nt.links.new(n.outputs["Fac"], cr.inputs["Value"]); mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = amount; nt.links.new(cr.outputs[0], k.inputs[0]); nt.links.new(k.outputs[0], mx.inputs[0])
    if src: nt.links.new(src, mx.inputs[6])
    else: mx.inputs[6].default_value = b.inputs["Base Color"].default_value[:]
    mx.inputs[7].default_value = (*srgb(hexcol), 1); nt.links.new(mx.outputs[2], b.inputs["Base Color"])

def flowers(c, x0, x1, y, depth=.7, seed=0):
    """a flower bed: dark soil strip, low bushes and bright blossoms (instanced icospheres in 4 colours)"""
    rr = random.Random(seed); soil = mat("soil", "#4a3424", .95, bump=("noise", 20, .3)); box("bed_soil", c, (x1 - x0, depth, .08), ((x0 + x1) / 2, y, .03), soil, bevel=.02)
    box("bed_edge", c, (x1 - x0, .06, .12), ((x0 + x1) / 2, y - depth / 2, .05), mat("edging", "#d9d2c5", .6), bevel=.01)
    leafm = mat("bush_leaf", "#2f7d22", .8, bump=("noise", 12, .5)); cols = ("#e83b5a", "#ffd23a", "#ff8fc0", "#f4f1ea")
    for k in range(int((x1 - x0) * 2.2)):
        x = rr.uniform(x0 + .2, x1 - .2); yy = y + rr.uniform(-depth * .3, depth * .3); r = rr.uniform(.18, .32)
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        for v in bm.verts: v.co += v.normal * r * .25 * noise.noise(v.co * 6 + Vector((k, seed, 0)))
        o = mesh_obj("bed_bush", bm, leafm, c, smooth=True); o.location = (x, yy, r * .7); o.scale = (1, 1, .8)
        fm = mat("blossom_" + cols[k % 4], cols[k % 4], .5)
        for j in range(4):
            bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.05); f_ = mesh_obj("blossom", bm, fm, c, smooth=True)
            a = rr.uniform(0, 6.28); f_.location = (x + math.cos(a) * r * .7, yy + math.sin(a) * r * .7, r * 1.15 + rr.uniform(-.05, .08))

def target_mat():
    """red/white concentric rings painted on the garage door (object coords, centre at origin of the door object)"""
    if "target_paint" in bpy.data.materials: return bpy.data.materials["target_paint"]
    m = bpy.data.materials.new("target_paint"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = .55
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = "LENGTH"; cm = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], cm.inputs["X"]); nt.links.new(sep.outputs["Z"], cm.inputs["Y"]); nt.links.new(cm.outputs[0], vm.inputs[0])
    ring = nt.nodes.new("ShaderNodeMath"); ring.operation = "MULTIPLY"; ring.inputs[1].default_value = 1 / .18; nt.links.new(vm.outputs["Value"], ring.inputs[0])
    fl = nt.nodes.new("ShaderNodeMath"); fl.operation = "FLOOR"; nt.links.new(ring.outputs[0], fl.inputs[0])
    md = nt.nodes.new("ShaderNodeMath"); md.operation = "MODULO"; md.inputs[1].default_value = 2.0; nt.links.new(fl.outputs[0], md.inputs[0])
    out = nt.nodes.new("ShaderNodeMath"); out.operation = "LESS_THAN"; out.inputs[1].default_value = 5 * .18; nt.links.new(vm.outputs["Value"], out.inputs[0])   # rings only inside r < 0.9 m
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; nt.links.new(md.outputs[0], k.inputs[0]); nt.links.new(out.outputs[0], k.inputs[1])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; nt.links.new(k.outputs[0], inv.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; nt.links.new(inv.outputs[0], mx.inputs[0])
    mx.inputs[6].default_value = (*srgb("#d8262f"), 1); mx.inputs[7].default_value = (*srgb("#f4f1ea"), 1); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m

def mesh_obj(name, bm, material, c, smooth=False, bevel=0.0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); c.objects.link(o); me.materials.append(material)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if bevel:
        mo = o.modifiers.new("bevel", "BEVEL"); mo.width = bevel; mo.segments = 2; mo.limit_method = "ANGLE"
    return o

def box(name, c, size, loc, material, bevel=.03, rot=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = mesh_obj(name, bm, material, c, bevel=bevel); o.location = loc; o.rotation_euler = (0, 0, rot); return o

def cyl(name, c, r, h, loc, material, seg=24, r2=None, rot=(0, 0, 0), smooth=True):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = mesh_obj(name, bm, material, c, smooth=smooth); o.location = loc; o.rotation_euler = rot; return o

def gable_house(name, c, w, d, h, roof_h, loc, wall_m, roof_m, trim_m, rot=0.0, windows=(), door=None):
    """box walls + gable roof with overhang (ridge along X), windows as framed dark quads on the front (-Y) face"""
    root = bpy.data.objects.new(name, None); c.objects.link(root); root.location = loc; root.rotation_euler = (0, 0, rot)
    walls = box(name + "_walls", c, (w, d, h), (0, 0, h / 2), wall_m, bevel=.04); walls.parent = root
    bm = bmesh.new(); o = .45; hw, hd = w / 2 + o, d / 2 + o
    vs = [bm.verts.new(p) for p in ((-hw, -hd, h - .05), (hw, -hd, h - .05), (hw, 0, h + roof_h), (-hw, 0, h + roof_h), (-hw, hd, h - .05), (hw, hd, h - .05))]
    bm.faces.new((vs[0], vs[1], vs[2], vs[3])); bm.faces.new((vs[3], vs[2], vs[5], vs[4]))
    roof = mesh_obj(name + "_roof", bm, roof_m, c); roof.parent = root; sm = roof.modifiers.new("t", "SOLIDIFY"); sm.thickness = .16
    bm = bmesh.new(); g = [bm.verts.new(p) for p in ((-w / 2, -d / 2, h), (w / 2, -d / 2, h), (0, -d / 2, h + roof_h - .05))]   # front and back gables
    bm.faces.new(g); g2 = [bm.verts.new(p) for p in ((-w / 2, d / 2, h), (0, d / 2, h + roof_h - .05), (w / 2, d / 2, h))]; bm.faces.new(g2)
    gab = mesh_obj(name + "_gable", bm, wall_m, c); gab.parent = root
    win_m = mat("window_glass", "#2c4a6e", .15)
    for (x, z, ww, wh) in windows:
        f = box(name + "_wframe", c, (ww + .16, .08, wh + .16), (x, -d / 2 - .04, z), trim_m, bevel=.02); f.parent = root
        g_ = box(name + "_wglass", c, (ww, .06, wh), (x, -d / 2 - .07, z), win_m, bevel=0); g_.parent = root
        for s in (-1, 1):
            sh = box(name + "_shutter", c, (ww * .42, .06, wh + .1), (x + s * (ww / 2 + ww * .26), -d / 2 - .06, z), mat("shutter", "#3d6b4f", .55), bevel=.015); sh.parent = root
    if door:
        x, dw, dh, dm = door; f = box(name + "_door", c, (dw, .1, dh), (x, -d / 2 - .05, dh / 2), dm, bevel=.02); f.parent = root
    return root

def blob_tree(name, c, loc, height=5.5, crown=2.6, seed=0, leaf="#3f8f2e"):
    """cloud-ball tree: tapered trunk + 7-11 displaced balls in a rounded cluster (TV-cartoon look), one mesh per material"""
    rr = random.Random(seed); root = bpy.data.objects.new(name, None); c.objects.link(root); root.location = loc
    t = cyl(name + "_trunk", c, .28, height * .62, (0, 0, height * .31), mat("bark", "#6b4a32", .85, bump=("noise", 14, .25)), seg=10, r2=.18); t.parent = root
    bm = bmesh.new(); cz = height * .7
    for k in range(rr.randint(7, 11)):
        a = rr.uniform(0, 2 * math.pi); rad = rr.uniform(.3, 1.0) * crown * .55; z = cz + rr.uniform(-.35, .6) * crown * .6
        r = crown * rr.uniform(.42, .62) * (1.0 if k else 1.25); s = bmesh.new(); bmesh.ops.create_icosphere(s, subdivisions=3, radius=r)
        off = Vector((math.cos(a) * rad, math.sin(a) * rad, z)) if k else Vector((0, 0, cz + .2))
        for v in s.verts:
            v.co += v.normal * r * .16 * noise.noise(v.co * 1.7 + Vector((seed, k, 0))); v.co += off
        vm = {v: bm.verts.new(v.co) for v in s.verts}
        for f in s.faces: bm.faces.new([vm[v] for v in f.verts])
        s.free()
    leaves = mat("leaves_" + leaf, leaf, .75, bump=("noise", 6, .5)); o = mesh_obj(name + "_crown", bm, leaves, c, smooth=True); o.parent = root
    return root

def cloud(name, c, loc, size=6.0, seed=0):
    rr = random.Random(seed); bm = bmesh.new()
    for k in range(26):
        r = size * rr.uniform(.12, .26) * (1.3 if k < 6 else 1.0); s = bmesh.new(); bmesh.ops.create_icosphere(s, subdivisions=3, radius=r)
        off = Vector((rr.uniform(-.6, .6) * size, rr.uniform(-.2, .2) * size, (rr.uniform(0, .45) if k >= 6 else 0) * size))
        for v in s.verts: v.co += v.normal * r * .22 * noise.noise(v.co * (2.5 / r) + Vector((seed, k, 1))); v.co += off
        vm = {v: bm.verts.new(v.co) for v in s.verts}
        for f in s.faces: bm.faces.new([vm[v] for v in f.verts])
        s.free()
    m = bpy.data.materials.get("cloud") or bpy.data.materials.new("cloud")
    if not m.use_nodes:
        m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (1, 1, 1, 1); b.inputs["Roughness"].default_value = 1
        b.inputs["Subsurface Weight"].default_value = .6; b.inputs["Subsurface Radius"].default_value = (2, 2, 2); b.inputs["Emission Color"].default_value = (1, 1, 1, 1); b.inputs["Emission Strength"].default_value = .15
    o = mesh_obj(name, bm, m, c, smooth=True); o.location = loc; o.visible_shadow = False; return o

def blade_clump():
    """a 25 x 25 cm tuft of 18 curved blades (2 tris each, bent), vertex-coloured dark at the root -> light at the tip; built once"""
    if "grass_tuft" in bpy.data.collections: return bpy.data.collections["grass_tuft"]
    rr = random.Random(5); bm = bmesh.new(); cl = bm.loops.layers.color.new("Col")
    for k in range(18):
        x, y = rr.uniform(-.12, .12), rr.uniform(-.12, .12); h = rr.uniform(.08, .16); a = rr.uniform(0, 6.28); bend = rr.uniform(.02, .06); w = .012
        d = Vector((math.cos(a), math.sin(a), 0)); n = Vector((-d.y, d.x, 0))
        p0 = Vector((x, y, 0)) - n * w; p1 = Vector((x, y, 0)) + n * w; pm0 = Vector((x, y, h * .55)) + d * bend * .4 - n * w * .6; pm1 = pm0 + n * w * 1.2
        tip = Vector((x, y, h)) + d * bend
        vs = [bm.verts.new(p) for p in (p0, p1, pm1, pm0, tip)]
        f1 = bm.faces.new((vs[0], vs[1], vs[2], vs[3])); f2 = bm.faces.new((vs[3], vs[2], vs[4]))
        for f in (f1, f2):
            for lp in f.loops:
                t = lp.vert.co.z / h; lp[cl] = (.25 + .75 * t, .25 + .75 * t, .25 + .75 * t, 1)
    me = bpy.data.meshes.new("grass_tuft"); bm.to_mesh(me); bm.free()
    m = bpy.data.materials.new("grass_blades"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"; cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*srgb("#1f5e10"), 1); cr.color_ramp.elements[1].color = (*srgb("#7cd23a"), 1)
    nt.links.new(vc.outputs["Color"], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .55
    b.inputs["Subsurface Weight"].default_value = .15; me.materials.append(m)
    c = bpy.data.collections.new("grass_tuft"); o = bpy.data.objects.new("grass_tuft", me); c.objects.link(o); return c

def grass(c, lane):
    """dense lawn of own blade tufts on the lawns only (kept 0.15 m off every paved edge), denser near the lens"""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "blender"))
    from rc import geo
    src = blade_clump()
    zones = ([({"polygon": [[-16, -32], [-5.5, -32], [-5.5, 4.5], [-16, 4.5]]}, 26000, 1), ({"polygon": [[-3.7, -32], [-3.15, -32], [-3.15, 4.5], [-3.7, 4.5]]}, 2400, 2),
              ({"polygon": [[3.15, -32], [12, -32], [12, 4.0], [3.15, 4.0]]}, 18000, 3)] if lane else
             [({"polygon": [[-25, -4.5], [-3.3, -4.5], [-3.3, 14], [-25, 14]]}, 30000, 1), ({"polygon": [[3.3, -4.5], [25, -4.5], [25, 14], [3.3, 14]]}, 26000, 3)])
    for k, (z, n, sd) in enumerate(zones):
        P, Rt, Sc = geo.scatter_points(z, n, sd, scale_range=(.9, 1.6))
        geo.instancer("grass_%d" % k, P, src, c, Rt, Sc, wind=.04)

def sky(scene, tod):
    w = bpy.data.worlds.new("sky_" + tod); scene.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(sep.outputs["Z"], cr.inputs[0])
    top, hor = (("#0a3fc8", "#5ea4f5") if tod == "day" else ("#4b2bb8", "#ff9a6a"))
    cr.color_ramp.elements[0].position = .5; cr.color_ramp.elements[0].color = (*srgb(hor), 1); cr.color_ramp.elements[1].position = .6; cr.color_ramp.elements[1].color = (*srgb(top), 1)
    nt.links.new(cr.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = .75 if tod == "day" else .55

def lib_instance(name, aid, c, loc, rot=0.0, scale=1.0):
    """an instance of a library asset (rc.library: built once, cached)"""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "blender"))
    from rc import library, bl_library
    blend, _ = library.resolve(aid, log=lambda *a: None); holder = bpy.data.collections.get("LIB") or bpy.data.collections.new("LIB")
    src = bl_library.link_asset(blend, aid, holder); o = bpy.data.objects.new(name, None); o.instance_type = "COLLECTION"; o.instance_collection = src
    c.objects.link(o); o.location = loc; o.rotation_euler = (0, 0, rot); o.scale = (scale,) * 3; return o

def build(scene, tod="day", lane=False, lib_trees=True):
    """lane=True: shot-1 layout, the hero driveway is a 32 m asphalt lane straight to the garage, a concrete footpath on its left,
    the cross street far behind (y=-34); lib_trees: leafy library trees (island_tree_02) instead of the cloud-ball blobs"""
    S = col("SET_street")
    road = mat("asphalt", "#4d525b", .8, bump=("noise", 40, .15)); conc = mat("concrete", "#cfc9bf", .75, bump=("noise", 25, .12))
    lawn = mat("lawn", "#4fa22a", .9, bump=("noise", 30, .2)); curb = mat("curb", "#b9b4ab", .7)
    stains(conc, "#9c958a", 1.3, .55); stains(road, "#3a3e45", 2.0, .5); stains(lawn, "#6aa83a", .35, .6)
    box("ground", S, (220, 220, .1), (0, 0, -.06), lawn, bevel=0)
    ry = -34 if lane else -10
    box("road", S, (220, 7, .04), (0, ry, -.01), road, bevel=0)
    for y in (ry - 3.6, ry + 3.6): box("curb", S, (220, .3, .16), (0, y, .05), curb, bevel=.03)
    box("sidewalk", S, (220, 1.6, .05), (0, ry + 4.5, .0), conc, bevel=.01)
    if lane:
        box("lane", S, (5.5, 34, .05), (0, -12, .0), road, bevel=.01); box("apron", S, (6, 4, .052), (0, 3, .0), conc, bevel=.01)
        box("footpath", S, (1.5, 34, .05), (-4.6, -12, .0), conc, bevel=.01)
        for k in range(-20, 3): box("path_joint", S, (1.48, .04, .052), (-4.6, k * 1.5, .0), mat("joint", "#a8a39a", .9), bevel=0)
        for x in (-2.9, 2.9): box("lane_edge", S, (.18, 34, .1), (x, -12, .03), curb, bevel=.02)
    else:
        box("driveway", S, (6, 10.2, .05), (0, 0, .0), conc, bevel=.01)
    for x in (-17, 17): box("driveway_n", S, (5, 10, .05), (x, 0, 0), conc, bevel=.01)
    for k in range(-30, 31): box("walk_joint", S, (.04, 1.58, .052), (k * 1.6, ry + 4.5, .0), mat("joint", "#a8a39a", .9), bevel=0)
    # hero house: garage block in front (door faces -Y at y=5), house body behind and to the left
    mint = mat("siding_mint", "#93d7c4", .65, bump=("siding", 6.0, .35)); trim = mat("trim_white", "#f2efe8", .5); roofm = mat("roof_slate", "#5d6577", .8, bump=("siding", 9.0, .6))
    gable_house("garage", S, 7.0, 6.0, 3.0, 1.7, (0, 8, 0), mint, roofm, trim)
    door = box("garage_door", S, (5.2, .12, 2.5), (0, 4.94, 1.25), mat("door_white", "#f4f1ea", .45, bump=("panel", 2.2, .5)), bevel=.02)
    paint = box("garage_target", S, (2.2, .01, 2.2), (0, 4.87, 1.15), target_mat(), bevel=0)
    for k in range(4): box("door_window", S, (.75, .02, .32), (-1.8 + k * 1.2, 4.86, 2.15), mat("window_glass", "#2c4a6e", .15), bevel=0)
    vent = cyl("gable_vent", S, .42, .08, (0, 4.92, 3.95), trim, rot=(math.pi / 2, 0, 0)); [box("vent_slat", S, (.6, .03, .05), (0, 4.86, 3.72 + k * .12), mat("vent_slat", "#c9c3b5", .6), bevel=0) for k in range(5)]
    gable_house("house", S, 9.0, 9.0, 3.4, 2.4, (-8.5, 12, 0), mint, roofm, trim, windows=((-2.2, 1.9, 1.2, 1.3), (2.2, 1.9, 1.2, 1.3)), door=(0, 1.0, 2.1, mat("door_red", "#d9452e", .45)))
    gut = mat("gutter", "#e9e6df", .4)
    box("gutter_garage", S, (7.9, .14, .12), (0, 4.55, 2.98), gut, bevel=.02); box("gutter_house", S, (9.9, .14, .12), (-8.5, 7.05, 3.38), gut, bevel=.02)
    box("downpipe", S, (.09, .09, 2.95), (3.62, 4.62, 1.48), gut, bevel=.01)
    box("chimney", S, (.9, .9, 2.6), (-11.0, 13.0, 5.2), mat("brick", "#a8553f", .85, bump=("panel", 9.0, .4)), bevel=.03)
    box("porch_step", S, (2.6, 1.0, .18), (-8.5, 6.95, .09), mat("step", "#bdb6aa", .7), bevel=.03)
    flowers(S, -12.8, -9.6, 6.85, seed=1); flowers(S, -7.4, -4.4, 6.85, seed=2)
    flowers(S, -6.6, -3.6, 4.4, depth=.55, seed=3)
    for k, x in enumerate((4.2, 4.9)):                              # wheelie bins by the garage
        bm_ = mat("bin_green" if k == 0 else "bin_grey", "#2f6b3a" if k == 0 else "#5b6068", .5)
        box("bin", S, (.6, .7, 1.0), (x, 4.2, .5), bm_, bevel=.06); box("bin_lid", S, (.64, .76, .08), (x, 4.15, 1.04), bm_, bevel=.03)
    bpy.ops.mesh.primitive_torus_add(major_radius=.3, minor_radius=.07, location=(-3.9, 4.75, .45), rotation=(math.pi / 2, 0, 0)); hose = bpy.context.object; hose.name = "hose_reel"
    for c_ in list(hose.users_collection): c_.objects.unlink(hose)
    S.objects.link(hose); hose.data.materials.append(mat("hose_green", "#2e9c3a", .5))
    if lane:
        for k, y in enumerate(range(-30, 16, 3)): lib_instance("fence_shrub%d" % k, ("shrub_03", "shrub_04")[k % 2], S, (6.6, y + .7 * (k % 2), 0), rot=k * 1.3, scale=.55 + .1 * (k % 3))
    # basketball hoop at the right of the driveway
    pole = cyl("hoop_pole", S, .07, 3.6, (3.6, 4.0, 1.8), mat("pole", "#2f3a52", .4, .6), seg=12)
    box("backboard", S, (1.4, .05, .9), (3.6, 3.65, 3.5), trim, bevel=.02); box("board_square", S, (.5, .01, .38), (3.6, 3.62, 3.38), mat("board_red", "#d8262f", .5), bevel=0)
    bpy.ops.mesh.primitive_torus_add(major_radius=.23, minor_radius=.018, location=(3.6, 3.32, 3.1)); rim = bpy.context.object; rim.name = "rim"
    for c_ in list(rim.users_collection): c_.objects.unlink(rim)
    S.objects.link(rim); rim.data.materials.append(mat("rim_orange", "#ff5a1f", .4, .5))
    # mailbox, hydrant
    mx, my = (-6.0, -14.0) if lane else (-3.6, -4.4)
    cyl("mail_post", S, .05, 1.0, (mx, my, .5), mat("post_dark", "#3a2f2a", .6), seg=8); box("mailbox", S, (.25, .5, .28), (mx, my, 1.1), mat("mail_grey", "#6b7380", .35, .6), bevel=.08)
    hx, hy = (-7.2, -19.0) if lane else (-4.4, -6.2)
    h_ = mat("hydrant_red", "#d62a2a", .35); cyl("hydrant", S, .14, .55, (hx, hy, .28), h_, seg=16); cyl("hydrant_cap", S, .17, .12, (hx, hy, .6), h_, seg=16)
    cyl("hydrant_nozzle", S, .06, .32, (hx, hy, .4), h_, seg=10, rot=(0, math.pi / 2, 0))
    # wooden fence behind
    fence = mat("fence_wood", "#7b5a40", .85, bump=("noise", 18, .25))
    box("fence", S, (90, .1, 1.9), (0, 17, .95), mat("fence_planks", "#7b5a40", .85, bump=("panel", 3.5, .45)), bevel=0)
    # neighbour houses
    gable_house("neigh_L", S, 10, 9, 3.2, 2.2, (-18, 8, 0), mat("siding_pink", "#e8b4a6", .65, bump=("siding", 6.0, .3)), mat("roof_brown", "#7a5a52", .8), trim,
                windows=((-2.5, 1.8, 1.3, 1.2), (2.5, 1.8, 1.3, 1.2)), door=(0, 1.0, 2.1, mat("door_teal", "#2f8c8c", .45)))
    if lane:                                                         # shot-1 layout: a board fence closes the right side (the low shots look across it)
        box("fence_R", S, (.1, 40, 1.9), (7.5, -3, .95), mat("fence_planks", "#7b5a40", .85, bump=("panel", 3.5, .45)), bevel=0).rotation_euler = (0, 0, 0)
        for k, y in enumerate((-14, -6, 2, 10)): lib_instance("treeR%d" % k, "island_tree_02", S, (11 + (k % 2) * 3, y, 0), rot=k * 2.1, scale=1.15 + .1 * (k % 2))
    gable_house("neigh_R", S, 10, 9, 3.2, 2.2, (26 if lane else 18, 9, 0), mat("siding_lav", "#c9b9e0", .65, bump=("siding", 6.0, .3)), mat("roof_plum", "#6b4f72", .8), trim,
                windows=((-2.5, 1.8, 1.3, 1.2), (2.5, 1.8, 1.3, 1.2)), door=(0, 1.0, 2.1, mat("door_navy", "#2c3e6b", .45)))
    gable_house("far_house", S, 11, 8, 3.0, 2.0, (-34, 14, 0), mat("siding_cream", "#efe2b8", .65), mat("roof_grey", "#6a6f78", .8), trim, windows=((-3, 1.7, 1.2, 1.1), (3, 1.7, 1.2, 1.1)))
    # trees (cloud balls), along the fence and the street
    for k, (x, y, hgt, cr) in enumerate(((-4.5, 15.5, 7.5, 2.8), (6.5, 14.5, 8.0, 3.2), (11, 3, 6.5, 2.4), (-12, 2.5, 6.0, 2.2), (25, 15, 8.5, 3.4), (-27, 16, 8.0, 3.0), (-2, 22, 9, 3.8), (14, 21, 9.5, 4.0), (-14, 20, 9, 3.6), (4, 19, 8.5, 3.4), (5.5, 9.5, 8.0, 3.2), (-15.5, 9.0, 7.5, 3.0))):
        if lib_trees: lib_instance("tree%d" % k, "island_tree_02", S, (x, y, 0), rot=k * 1.7, scale=hgt / 7.5)
        else: blob_tree("tree%d" % k, S, (x, y, 0), hgt, cr, seed=k, leaf=("#3f8f2e", "#4a9a34", "#367f2a")[k % 3])
    for k, (x, y, z, s) in enumerate(((-28, 70, 26, 13), (30, 80, 30, 15), (-6, 110, 40, 18), (55, 95, 22, 12))): cloud("cloud%d" % k, S, (x, y, z), s, seed=k)
    grass(S, lane)
    sky(scene, tod)
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 6.0 if tod == "day" else 1.6; sun.angle = math.radians(3.5)
    sun.color = srgb("#fff3dc") if tod == "day" else srgb("#ffb07a")
    so = bpy.data.objects.new("sun", sun); col("SET_lights").objects.link(so); so.rotation_euler = (math.radians(58), 0, math.radians(-40 if tod == "day" else -80))
    return S

def pbr(name, ph_id, tile=2.0, tint=None, tint_k=0.0, rough_mul=1.0, normal=1.0, value=1.0):
    """REAL SURFACE (CB rule 2026-11-19): a CC0 Poly Haven PBR set (colour, roughness, normal, from rc.fetch's cache) tiled every `tile`
    metres in object space; tint (hex) mixed in by tint_k keeps the reference palette; value scales the brightness"""
    if name in bpy.data.materials: return bpy.data.materials[name]
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "blender"))
    from rc import fetch
    M = fetch.ambientcg_maps(ph_id[4:], "1K", log=lambda *a: None) if ph_id.startswith("acg:") else fetch.polyhaven_maps(ph_id, "1k", log=lambda *a: None)   # "acg:Carpet012" = ambientCG
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); L.new(tc.outputs["Object"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (1 / tile,) * 3
    def img(key, nc):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(M[key], check_existing=True)
        if nc: t.image.colorspace_settings.name = "Non-Color"
        t.projection = "BOX"; t.projection_blend = .2; L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    c = img("color", False); src = c.outputs["Color"]
    if tint and tint_k > 0:
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = tint_k; L.new(src, mx.inputs[6]); mx.inputs[7].default_value = (*srgb(tint), 1); src = mx.outputs[2]
    if value != 1.0:
        hv = N.new("ShaderNodeHueSaturation"); hv.inputs["Value"].default_value = value; L.new(src, hv.inputs["Color"]); src = hv.outputs["Color"]
    L.new(src, b.inputs["Base Color"])
    if "roughness" in M:
        r = img("roughness", True); rm = N.new("ShaderNodeMath"); rm.operation = "MULTIPLY"; rm.inputs[1].default_value = rough_mul; rm.use_clamp = True
        L.new(r.outputs["Color"], rm.inputs[0]); L.new(rm.outputs[0], b.inputs["Roughness"])
    if "normal" in M:
        n = img("normal", True); nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = normal; L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m

def hdri_reflections(scene, ph_hdri="kloofendal_48d_partly_cloudy_puresky", strength=1.0, sky_strength=None):
    """REAL REFLECTIONS (CB rule 2026-11-19): shiny surfaces (car paint, helmet, visor) reflect a real sky HDRI, but ONLY glossy rays see it;
    the camera keeps the painted sky gradient and the diffuse light stays the gradient, so the reference palette does not change.
    sky_strength: new strength of the gradient (lower = darker shadows next to the sun)"""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "blender"))
    from rc import fetch
    w = scene.world; nt = w.node_tree; N, L = nt.nodes, nt.links; out = N["World Output"]; bg = N["Background"]
    if sky_strength is not None: bg.inputs["Strength"].default_value = sky_strength
    env = N.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(fetch.polyhaven_hdri(ph_hdri, "1k", log=lambda *a: None), check_existing=True)
    b2 = N.new("ShaderNodeBackground"); b2.inputs["Strength"].default_value = strength; L.new(env.outputs["Color"], b2.inputs["Color"])
    lp = N.new("ShaderNodeLightPath"); mx = N.new("ShaderNodeMixShader"); L.new(lp.outputs["Is Glossy Ray"], mx.inputs[0])
    L.new(bg.outputs[0], mx.inputs[1]); L.new(b2.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])

def handheld(cam, f0, f1, amp=.012, rot_deg=.25, seed=0):
    """THE CAMERA NEVER STOPS (CB rule 2026-11-19): a soft deterministic hand-held drift on EVERY frame (delta transforms, on top of the
    keyed move): sums of slow sines, ~1 cm and ~0.25 deg, so no frame is ever a dead hold"""
    import math as _m
    for f in range(f0, f1 + 1):
        t = f + seed * 37.0
        cam.delta_location = (amp * (_m.sin(t * .21) + .5 * _m.sin(t * .53 + 1)), amp * .5 * _m.sin(t * .17 + 2), amp * (_m.sin(t * .27 + 4) + .4 * _m.sin(t * .61)))
        cam.delta_rotation_euler = (_m.radians(rot_deg) * _m.sin(t * .19 + 3), _m.radians(rot_deg) * .4 * _m.sin(t * .23 + 5), _m.radians(rot_deg) * _m.sin(t * .15 + 1))
        cam.keyframe_insert("delta_location", frame=f); cam.keyframe_insert("delta_rotation_euler", frame=f)
