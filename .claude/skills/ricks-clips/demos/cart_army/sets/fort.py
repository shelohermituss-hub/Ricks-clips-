"""cart_army ("How One Cart Stopped an Entire Army", reproduction of the reference, CB 2026-11-20): THE FORT COURTYARD CORNER of shot 1.
Layout (metres): the engineer stands at the origin facing +X, his board on its stand at x = 1; the curtain wall runs along X at y = 6
(an arched gate at x = -7, the blue tiger banner at x = -1); a tower block stands forward on the right (x 3..11, y 1.5..9); a dirt path
runs along the foot of the wall; everything else is dense bright grass up to the lens.
Reference facts (references/cart_army/shots/s01_hi.jpg): walls are INDIVIDUAL bevelled ashlar blocks, beige-grey, tint varies block by
block; grass is long, dense, vivid yellow-green; soft high sun, pale blue sky with clouds.
    import fort; Mo = fort.build(scene)"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "blender")); sys.path.insert(0, os.path.join(SKILL, "demos", "crashed_car", "sets"))
from rc import look, geo  # noqa: E402
from rc.look import tex, col, mesh_obj, srgb  # noqa: E402
import street  # noqa: E402

MOOD = dict(az=-152, el=46, energy=8.5, hdri="kloofendal_48d_partly_cloudy_puresky", light=.55, glow=.3, exposure=-.3, sat=1.12, contrast="Medium Contrast")

def height(x, y): return 0.0

def stone():
    """ashlar: a smooth scanned stone surface, recoloured beige-grey, each block with its own tint (vertex colour), dark recessed joints"""
    m = tex("fort_stone", "grey_plaster_02", tile=2.5, recolor="#c9bea8", value=1.0, normal=.5, spec=.12, macro=.25)   # smooth dressed stone (the first scan was speckled like terrazzo)
    nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]; src = b.inputs["Base Color"].links[0].from_socket
    vc = N.new("ShaderNodeVertexColor"); vc.layer_name = "tint"; mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0
    L.new(src, mx.inputs[6]); L.new(vc.outputs["Color"], mx.inputs[7]); L.new(mx.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .85
    return m

def blocks(name, c, origin, u, n, length, hgt, mat, seed=1, row=.56, holes=()):
    """one wall FACE built block by block: origin (corner at the ground), u (unit vector along the wall), n (outward normal), every block a
    bevelled box standing 6-10 cm proud of a dark backing; holes = [(u0, u1, z0, z1, arch)] openings (arch: round top)"""
    R = random.Random(seed); bm = bmesh.new(); colr = bm.loops.layers.color.new("tint"); u, n = Vector(u), Vector(n); o = Vector(origin); z = 0.0; r = 0
    def is_open(a, bb, z0, z1):
        for h0, h1, k0, k1, arch in holes:
            if bb <= h0 or a >= h1 or z1 <= k0: continue
            top = k1 if not arch else k1 + math.sqrt(max(0.0, ((h1 - h0) / 2) ** 2 - (min(max((a + bb) / 2, h0), h1) - (h0 + h1) / 2) ** 2))
            if z0 < top - .1: return True
        return False
    while z < hgt - .01:
        x = -R.uniform(0, .7) if r % 2 else 0.0
        while x < length:
            w = R.uniform(.85, 1.55); a, bb = max(0.0, x), min(length, x + w); x += w
            if bb - a < .12 or is_open(a, bb, z, z + row): continue
            d = R.uniform(.06, .11); t = R.uniform(.70, 1.0); tw = R.uniform(-.05, .05)
            g = bmesh.ops.create_cube(bm, size=1.0); vs = g["verts"]
            for v in vs:
                lu, ld, lz = (v.co.x + .5) * (bb - a - .016) + a + .008, (v.co.y + .5) * (d + .3) - .3, (v.co.z + .5) * (row - .016) + z + .008
                v.co = o + u * lu + n * ld + Vector((0, 0, lz))
            fs = list({f for v in vs for f in v.link_faces})
            bmesh.ops.bevel(bm, geom=list({e for f in fs for e in f.edges}), offset=.018, segments=2, affect="EDGES")
            for f in [f for f in bm.faces if not f.tag]:
                f.tag = True
                for lp in f.loops: lp[colr] = (t + tw, t, t - tw, 1)
        z += row; r += 1
    w = mesh_obj(name, bm, mat, c, smooth=True)
    try: w.data.set_sharp_from_angle(angle=.7)
    except Exception: pass
    bk = bmesh.new(); q = [o - n * .02, o + u * length - n * .02, o + u * length - n * .02 + Vector((0, 0, hgt)), o - n * .02 + Vector((0, 0, hgt))]   # dark joints behind
    bk.faces.new([bk.verts.new(p) for p in q]); m2 = bpy.data.materials.get("fort_joint") or bpy.data.materials.new("fort_joint"); m2.use_nodes = True
    m2.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.06, .055, .05, 1); m2.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    if not holes: mesh_obj(name + "_joints", bk, m2, c)
    return w

def banner(c, at, w=1.25, h=3.6):
    """the blue banner: white tiger, gold chevron, gold border and fringe, hung on an iron bracket (drawn as a texture, real cloth folds)"""
    p = os.path.join(SKILL, "demos", "cart_army", "build", "banner_tiger.png")
    if not os.path.exists(p): __import__("subprocess").run(["python3", os.path.join(HERE, "banner_art.py"), p], check=True)       # drawn outside Blender (its Python has no PIL)
    bm = bmesh.new(); uv = bm.loops.layers.uv.new(); nx, nz = 10, 28; V = [[bm.verts.new((at[0] - w / 2 + w * i / nx, at[1] - .12 - .035 * math.sin(i * 1.3) * (j / nz), at[2] - h * j / nz)) for i in range(nx + 1)] for j in range(nz + 1)]
    for j in range(nz):
        for i in range(nx):
            f = bm.faces.new((V[j][i], V[j + 1][i], V[j + 1][i + 1], V[j][i + 1]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))): lp[uv].uv = (a / nx, 1 - b / nz)
    m = bpy.data.materials.new("banner_cloth"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(p)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9; b.inputs["Sheen Weight"].default_value = .4
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 180; bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .12; nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])   # the weave
    o = mesh_obj("banner", bm, m, c, smooth=True); sd = o.modifiers.new("thick", "SOLIDIFY"); sd.thickness = .012
    iron = bpy.data.materials.new("iron"); iron.use_nodes = True; ib = iron.node_tree.nodes["Principled BSDF"]; ib.inputs["Base Color"].default_value = (.03, .03, .035, 1); ib.inputs["Metallic"].default_value = .8; ib.inputs["Roughness"].default_value = .5
    bmr = bmesh.new(); bmesh.ops.create_cone(bmr, cap_ends=True, segments=10, radius1=.022, radius2=.022, depth=w + .3); r = mesh_obj("banner_rod", bmr, iron, c, smooth=True); r.rotation_euler = (0, math.radians(90), 0); r.location = (at[0], at[1] - .12, at[2] + .02)
    for k in range(26):                                                                            # the fringe
        bf = bmesh.new(); bmesh.ops.create_cube(bf, size=1.0); fo = mesh_obj("fringe", bf, bpy.data.materials.get("fringe_gold") or _flat("fringe_gold", (.75, .55, .1)), c); fo.scale = (.012, .006, .16); fo.location = (at[0] - w / 2 + w * (k + .5) / 26, at[1] - .12, at[2] - h - .08)
    return o

def _tint(bm, t=.9):
    """the stone material multiplies by the per-block tint attribute: a mesh without it renders black"""
    lay = bm.loops.layers.color.get("tint") or bm.loops.layers.color.new("tint")
    for f in bm.faces:
        for lp in f.loops: lp[lay] = (t, t, t, 1)

def _flat(name, rgb, rough=.7):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; return m

def ground(c):
    """grass field (dense blades, as in the demo that matched its reference) with a worn dirt path along the foot of the wall"""
    bm = bmesh.new(); bm.faces.new([bm.verts.new(p) for p in ((-60, -40, 0), (60, -40, 0), (60, 30, 0), (-60, 30, 0))])
    mesh_obj("fort_ground", bm, tex("fort_soil", "brown_mud_02", tile=3.0, recolor="#5d7a35", value=1.0, normal=1.0, spec=.1, macro=.2), c)
    bp = bmesh.new(); bp.faces.new([bp.verts.new(p) for p in ((-40, 2.6, .012), (1.5, 2.6, .012), (1.5, 6.0, .012), (-40, 6.0, .012))])
    mesh_obj("fort_path", bp, tex("fort_path", "brown_mud_02", tile=2.0, recolor="#8a6a48", value=1.0, normal=1.4, spec=.12, macro=.2), c)
    src = street.blade_clump(); m = bpy.data.materials.get("grass_blades")
    if m and not m.get("rc_recoloured"):
        cr = [n_ for n_ in m.node_tree.nodes if n_.type == "VALTORGB"][0].color_ramp; cr.elements[0].color = (*srgb("#4a8426"), 1); cr.elements[1].color = (*srgb("#c6e060"), 1); m["rc_recoloured"] = 1   # the reference's vivid yellow-green
        nt = m.node_tree; b = nt.nodes["Principled BSDF"]; out = nt.nodes["Material Output"]; tl = nt.nodes.new("ShaderNodeBsdfTranslucent"); mixs = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(b.inputs["Base Color"].links[0].from_socket, tl.inputs["Color"]); mixs.inputs[0].default_value = .45; nt.links.new(b.outputs[0], mixs.inputs[1]); nt.links.new(tl.outputs[0], mixs.inputs[2]); nt.links.new(mixs.outputs[0], out.inputs["Surface"])
    for k, (zone, n, sd, sc) in enumerate(((  [[-2.2, -6.6], [3.4, -6.6], [3.4, -3.2], [-2.2, -3.2]], 9000, 9, (1.5, 2.9)), (  [[-6, -6.5], [7, -6.5], [7, 2.4], [-6, 2.4]], 30000, 1, (.5, 2.3)), ([[-30, -22], [30, -22], [30, -6.5], [-30, -6.5]], 16000, 2, (1.0, 2.0)),
                                             ([[-36, -6.5], [-6, -6.5], [-6, 2.7], [-36, 2.7]], 22000, 3, (.9, 1.9)), ([[7, -6.5], [36, -6.5], [36, 3.4], [7, 3.4]], 16000, 4, (.9, 1.9)))):
        P, Rt, Sc = geo.scatter_points({"polygon": zone}, n, sd, exclude=[{"center": [.55, 0], "radius": .38}], scale_range=sc); geo.instancer("grass_%d" % k, P, src, c, Rt, Sc, wind=.05)

def build(scene):
    c = col("L_SET"); Mo = dict(MOOD); look.SUN[0], look.SUN[1] = Mo["az"], Mo["el"]
    look.sky_hdri(scene, strength=1.0, hdri=Mo["hdri"], glow=Mo["glow"], light=Mo["light"]); look.sun(scene, energy=Mo["energy"]); look.bounce_fill(c, at=(-2.0, -9.0, 3.0), aim=(0, 0, 1.2), energy=700.0, size=8.0)
    st = stone(); ground(c)
    blocks("wall_A", c, (-34, 6, 0), (1, 0, 0), (0, -1, 0), 37.0, 9.6, st, seed=1, holes=[(29.2, 32.0, 0, 2.7, True)])           # the curtain wall with its arched gate (x -8.8 .. -5.2)
    blocks("tower_front", c, (1.5, 3.4, 0), (1, 0, 0), (0, -1, 0), 9.0, 12.0, st, seed=2); blocks("tower_side", c, (1.5, 6.0, 0), (0, -1, 0), (-1, 0, 0), 2.6, 12.0, st, seed=3)
    back = bmesh.new(); back.faces.new([back.verts.new(p) for p in ((-34, 6.05, 0), (3, 6.05, 0), (3, 6.05, 9.6), (-34, 6.05, 9.6))]); mesh_obj("wall_A_back", back, bpy.data.materials["fort_joint"] if bpy.data.materials.get("fort_joint") else _flat("fort_joint", (.06, .055, .05)), c)
    gate = bmesh.new(); gate.faces.new([gate.verts.new(p) for p in ((-4.9, 6.6, 0), (-1.9, 6.6, 0), (-1.9, 6.6, 4.6), (-4.9, 6.6, 4.6))]); mesh_obj("gate_dark", gate, _flat("gate_dark", (.02, .018, .016)), c)
    banner(c, (-.9, 6.0, 7.4), h=3.6)
    for i in range(11):                                                                            # the gate arch: a ring of dressed wedge stones (voussoirs), each its own block
        a = math.pi * (i + .5) / 11; r = 1.4 + .27; bmv = bmesh.new(); bmesh.ops.create_cube(bmv, size=1.0)
        for v in bmv.verts: v.co = Vector((v.co.x * .56, v.co.y * .3, v.co.z * .5))
        bmesh.ops.bevel(bmv, geom=bmv.edges[:], offset=.02, segments=2, affect="EDGES"); _tint(bmv, .92 - .12 * (i % 3) / 2); o = mesh_obj("voussoir%02d" % i, bmv, st, c, smooth=True)
        o.location = (-3.4 + r * math.cos(a), 5.9, 2.7 + r * math.sin(a)); o.rotation_euler = (0, -a, 0)
    for nm, x0, x1, y, z in (("A", -34.0, 1.5, 5.8, 9.6), ("T", 1.5, 10.5, 3.2, 12.0)):               # crenellations: one merlon every two metres
        x = x0 + .6
        while x < x1 - .4:
            bmm = bmesh.new(); bmesh.ops.create_cube(bmm, size=1.0)
            for v in bmm.verts: v.co = Vector((v.co.x * 1.05, v.co.y * .55, v.co.z * .95))
            bmesh.ops.bevel(bmm, geom=bmm.edges[:], offset=.03, segments=2, affect="EDGES"); _tint(bmm, .9); o = mesh_obj("merlon_" + nm, bmm, st, c, smooth=True); o.location = (x, y + .1, z + .47); x += 2.0
    nt = scene.world.node_tree; N, L = nt.nodes, nt.links                                           # the reference's sky is pale everywhere: the photo seen by the lens is lightened and less saturated (the light it gives does not change)
    pick = [n for n in N if n.type == "MIX" and n.inputs[0].links and n.inputs[0].links[0].from_node.type == "LIGHT_PATH" and n.data_type == "RGBA"]
    if pick:
        src = pick[0].inputs[7].links[0].from_socket; hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = .62; hs.inputs["Value"].default_value = 2.1; L.new(src, hs.inputs["Color"]); L.new(hs.outputs["Color"], pick[0].inputs[7])
    return Mo


def gltf(c, asset_id, size, at, yaw=0.0):
    """a real Sketchfab model (library/assets/sketchfab/<id>): stood on `at`, its largest horizontal side scaled to `size` metres"""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(SKILL, "library", "assets", "sketchfab", asset_id, "gltf", "scene.gltf")); new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new("sf_" + asset_id[:6], None); c.objects.link(root); fix = bpy.data.objects.new("sf_fix", None); c.objects.link(fix); fix.parent = root
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = fix
    bpy.context.view_layer.update(); ms = [o for o in new if o.type == "MESH"]; pts = [o.matrix_world @ Vector(v) for o in ms for v in o.bound_box]
    mn = Vector([min(p[k] for p in pts) for k in range(3)]); mx = Vector([max(p[k] for p in pts) for k in range(3)]); s = size / max(mx.x - mn.x, mx.y - mn.y); cen = (mn + mx) / 2
    fix.scale = (s, s, s); fix.location = (-cen.x * s, -cen.y * s, -mn.z * s); root.location = at; root.rotation_euler = (0, 0, yaw); return root
