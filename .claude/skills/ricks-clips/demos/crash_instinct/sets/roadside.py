"""crash_instinct: the empty country road and its one tree (shots 1-10, 14-15, 17-19, 25), built for the frame.
Layout (metres): the tree trunk at the origin; the road runs along +Y, dead straight to the horizon, between x = 2.2 and x = 9.8
(white edge lines, a double solid yellow centre line at x = 6); a gravel shoulder 1.6-2.2; roadside grass on the tree side; a wooden
barbed-wire fence at x = -6.5; flat fields in alternating dry-beige / ploughed-brown bands to the horizon on both sides.
Analysis: references/crash_instinct/ANALYSE_FR.md §4 and shots/s01.md. Helpers (mat, pbr, grass tufts, clouds, handheld) come
from demos/crashed_car/sets/street.py."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "crashed_car", "sets")); sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "blender"))
import street  # noqa: E402
from street import srgb, col, mat, pbr, box, cyl, mesh_obj, cloud, lib_instance  # noqa: E402

ROAD = (2.2, 9.8); FENCE_X = -6.5; FENCE_XR = 18.5; Y0, Y1 = -220.0, 2500.0                       # to the horizon (aerial view, shot 3)

def plane(name, c, x0, x1, y0, y1, m, z=0.0):
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))]; bm.faces.new(vs)
    return mesh_obj(name, bm, m, c)

def sky(scene):
    """pale country sky of the reference: white-blue haze at the horizon, soft blue at the top (saturation 0.29 measured)"""
    w = bpy.data.worlds.new("sky_pale"); scene.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(sep.outputs["Z"], cr.inputs[0])
    cr.color_ramp.elements[0].position = .5; cr.color_ramp.elements[0].color = (*srgb("#e4ecf0"), 1)
    cr.color_ramp.elements[1].position = .62; cr.color_ramp.elements[1].color = (*srgb("#6fa6de"), 1)
    nt.links.new(cr.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = .9

# the cinematic kit (sky, sun, fill, shafts, haze, scanned textures, road wear) lives in blender/rc/look.py since 2026-11-19 (CB: every
# correction becomes the default for every new scene); the sun of this film: back-left, 30 deg (look.SUN)
from rc.look import HDRI, SUN, sky_hdri, god_rays, light_shafts, bounce_fill, sun, tex, road_wear  # noqa: E402
SUN_AZ, SUN_EL = SUN

def road(c):
    # scanned worn asphalt, DARK BLUE-GREY as measured on the reference aerial (#3b3a4b), + wheel paths + tar snakes + repair patches
    asphalt = road_wear(tex("road_asphalt", "asphalt_02", tile=4.0, value=2.3, tint="#9aa0c0", tint_k=.85, normal=1.6, rough_mul=.9, spec=.4, macro=.22))
    plane("road", c, ROAD[0], ROAD[1], Y0, Y1, asphalt, .02)
    gravel = tex("shoulder_gravel", "asphalt_track", tile=1.2, value=1.7, tint="#b8a890", tint_k=.6, macro=.25, spec=.3)
    plane("shoulder_L", c, 1.5, ROAD[0], Y0, Y1, gravel, .012); plane("shoulder_R", c, ROAD[1], ROAD[1] + .7, Y0, Y1, gravel, .012)
    white = mat("paint_white", "#f2f2ec", .45); yellow = mat("paint_yellow", "#f7cf4a", .5)
    plane("edge_L", c, ROAD[0] + .2, ROAD[0] + .35, Y0, Y1, white, .026); plane("edge_R", c, ROAD[1] - .35, ROAD[1] - .2, Y0, Y1, white, .026)
    plane("centre_L", c, 5.86, 5.98, Y0, Y1, yellow, .026); plane("centre_R", c, 6.02, 6.14, Y0, Y1, yellow, .026)   # double solid yellow (seen from the air, shot 3)

def ground(c):
    grass = tex("verge_grass", "leafy_grass", tile=2.0, value=1.0, recolor="#4f8a2a", macro=.3)   # same green as the tufts seen from far, mottled (never one flat green from the air)
    plane("verge", c, FENCE_X - .5, 1.5, Y0, Y1, grass, 0.0); plane("verge_R", c, ROAD[1] + .7, FENCE_XR + .5, Y0, Y1, grass, 0.0)   # 8 m of green on BOTH sides (CB)
    fields(c)

def fields(c):
    """PREPARED FARMLAND (CB 2026-11-19: "la terre ... a des traces comme si un tracteur était passé"): scanned furrows (Poly Haven farm_furrows,
    CC0) running along the road, strong relief; bands of golden stubble-on-furrows and bare brown tilled soil, to the horizon on both sides"""
    # colours MEASURED on the reference aerial (frame 180): light gold #b99d57, ochre #9d8e63, pale straw #cebc5b; fine regular rows
    F = [tex("field_gold", "farm_furrows", tile=1.6, recolor="#b79c5c", value=1.0, rot=90, normal=1.6, stripes=(1.5, .30)),
         tex("field_ochre", "farm_furrows", tile=1.6, recolor="#9c8a5c", value=1.0, rot=90, normal=1.6, stripes=(1.2, .34)),
         tex("field_straw", "farm_furrows", tile=1.6, recolor="#c9b666", value=1.0, rot=90, normal=1.6, stripes=(1.8, .26))]
    order = (0, 1, 0, 2, 1, 0, 1, 2)
    for side, x0, x1 in (("L", -400.0, FENCE_X - .5), ("R", FENCE_XR + .5, 400.0)):
        x = x1 if side == "L" else x0; k = 0
        while (x > x0 if side == "L" else x < x1):
            w = 9.0 + (k % 3) * 4
            a, b = (x - w, x) if side == "L" else (x, x + w)
            plane("field_%s%d" % (side, k), c, a, b, Y0, Y1, F[order[(k + (3 if side == "R" else 0)) % len(order)]], -.01)
            x = a if side == "L" else b; k += 1
            if k > 40: break

def fence(c, x=FENCE_X, name="fence", seed=0):
    """REAL FENCE (CB 2026-11-19: "la clôture manque de réalisme et n'émet pas d'ombre"): rough split posts (Poly Haven rough_wood, CC0), each a
    little different (height, lean, twist), three barbed wires that sag between posts; posts AND wires cast shadows"""
    from rc import geo
    wood = tex("fence_post", "rough_wood", tile=.5, value=1.05, normal=1.8)
    if "post_src" not in bpy.data.collections:
        pc = bpy.data.collections.new("post_src")
        for v in range(3):
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=.085, radius2=.07, depth=1.35)
            for vt in bm.verts: vt.co.x += .012 * math.sin(vt.co.z * 9 + v); vt.co.y += .01 * math.cos(vt.co.z * 7 + v * 2)
            top = [vt for vt in bm.verts if vt.co.z > .6]
            for vt in top: vt.co.z += .05 * (vt.co.x * 6 + v * .3)                         # cut at a slant
            bmesh.ops.translate(bm, vec=(0, 0, .6), verts=bm.verts)
            me = bpy.data.meshes.new("post%d" % v); bm.to_mesh(me); bm.free(); me.materials.append(wood); pc.objects.link(bpy.data.objects.new("post%d" % v, me))
    pc = bpy.data.collections["post_src"]; R = random.Random(seed)
    ys = [Y0 + 3 * k + R.uniform(-.15, .15) for k in range(int((min(Y1, 600) - Y0) / 3))]
    P = [(x, y, -.05 - R.uniform(0, .12)) for y in ys]
    geo.instancer(name + "_posts", P, pc, c, [(R.uniform(-.05, .05), R.uniform(-.05, .05), R.uniform(0, 6.28)) for _ in P], [(1, 1, R.uniform(.92, 1.06)) for _ in P], pick=True, seed=seed)
    wire = mat("barbed_wire", "#6a6a6c", .35, .85)
    for z in (.55, .85, 1.12):                                                              # one sagging wire mesh per height (catenary-like dip between posts)
        bm = bmesh.new(); prev = None
        for i in range(len(ys) - 1):
            for t in (0, .25, .5, .75):
                yy = ys[i] + (ys[i + 1] - ys[i]) * t; zz = z - .045 * math.sin(math.pi * t)
                v = bm.verts.new((x + .09, yy, zz))
                if prev: bm.edges.new((prev, v))
                prev = v
        me = bpy.data.meshes.new("%s_wire_%d" % (name, int(z * 100))); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(me.name, me); c.objects.link(o)
        sk = o.modifiers.new("skin", "SKIN")
        for vd in me.skin_vertices[0].data: vd.radius = (.0045, .0045)
        me.materials.append(wire); o.visible_shadow = True

def cross_fence(c, y=10.0, x0=FENCE_X, x1=1.3):
    """a field fence perpendicular to the road, behind the tree (seen behind the planter at grass level, shot 2)"""
    wood = bpy.data.materials.get("fence_post"); wire = bpy.data.materials.get("barbed_wire")
    for k in range(int((x1 - x0) / 3) + 1):
        x = x0 + 3 * k; o = cyl("xpost%d" % k, c, .062, 1.25, (x, y, .62), wood, seg=8)
    for z in (.55, .85, 1.15):
        o = cyl("xwire_%d" % int(z * 100), c, .0045, x1 - x0, ((x0 + x1) / 2, y + .07, z), wire, seg=4, rot=(0, math.pi / 2, 0), smooth=False)

def verge_grass(c, zone, n, seed, scale=(1.0, 1.8), exclude=()):
    """roadside grass from street's blade tufts, recoloured to the reference's soft yellow-green (saturation 0.29 measured)"""
    from rc import geo
    src = street.blade_clump(); m = bpy.data.materials.get("grass_blades")
    if m and not m.get("rc_recoloured"):
        cr = [n_ for n_ in m.node_tree.nodes if n_.type == "VALTORGB"][0].color_ramp
        cr.elements[0].color = (*srgb("#4e8a2e"), 1); cr.elements[1].color = (*srgb("#a4d866"), 1); m["rc_recoloured"] = 1   # CB 2026-11-19: brighter, more saturated
        # BACKLIT GRASS (low sun behind, 2026-11-19): real blades let the light through; without it the camera sees only their shadow side
        # and the sky fill has to light them (flat green, no tree shadow on the grass). Half the light passes through the blade.
        nt = m.node_tree; b = nt.nodes["Principled BSDF"]; out = nt.nodes["Material Output"]; tl = nt.nodes.new("ShaderNodeBsdfTranslucent"); mixs = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(b.inputs["Base Color"].links[0].from_socket, tl.inputs["Color"]); mixs.inputs[0].default_value = .45; nt.links.new(b.outputs[0], mixs.inputs[1]); nt.links.new(tl.outputs[0], mixs.inputs[2])
        nt.links.new(mixs.outputs[0], out.inputs["Surface"])
    P, Rt, Sc = geo.scatter_points({"polygon": zone}, n, seed, exclude=exclude, scale_range=scale)
    return geo.instancer("grass_%d" % seed, P, src, c, Rt, Sc, wind=.05)

def hole(c, at=(0.0, 0.0)):
    """the planting hole: dark earth disc + raised rim + a little heap of dug earth"""
    mud = pbr("hole_mud", "brown_mud_02", tile=.8, value=.95, tint="#6a4428", tint_k=.4)
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=28, radius=.34); o = mesh_obj("hole", bm, mud, c); o.location = (at[0], at[1], .015)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=.24)
    for v in bm.verts: v.co.z *= .45; v.co += v.normal * .03 * math.sin(v.co.x * 31 + v.co.y * 17)
    h = mesh_obj("dirt_heap", bm, mud, c, smooth=True); h.location = (at[0] + .5, at[1] + .15, 0)
    return o, h

def dirt_patch(c, at=(0.0, 0.0), radius=.95):
    """dug ground around the planting hole: loose brown earth, irregular edge, a little raised (reference shot 1)"""
    soil = pbr("dug_soil", "brown_mud_02", tile=1.0, value=1.6, tint="#a87c52", tint_k=.3)
    bm = bmesh.new(); R = random.Random(9); n = 36
    vs = [bm.verts.new((at[0] + radius * (1 + .14 * math.sin(k * 2.3) + R.uniform(-.06, .06)) * math.cos(2 * math.pi * k / n),
                        at[1] + radius * (1 + .14 * math.cos(k * 1.7) + R.uniform(-.06, .06)) * math.sin(2 * math.pi * k / n), .008)) for k in range(n)]
    bm.faces.new(vs); return mesh_obj("dirt_patch", bm, soil, c)

def clouds(c):
    """big flat soft cloud banks of the reference (top-left and along the horizon), not cotton balls"""
    for k, (x, y, z, sz) in enumerate(((-70, 150, 55, 130), (-10, 240, 80, 150), (70, 230, 85, 110), (-140, 110, 45, 100), (110, 330, 60, 140))):
        o = cloud("cloud%d" % k, c, (x, y, z), sz, seed=30 + k); o.scale = (1.0, .75, .55)
    m = bpy.data.materials["cloud"]; b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Emission Strength"].default_value = .5; b.inputs["Subsurface Weight"].default_value = .0; b.inputs["Base Color"].default_value = (*srgb("#f4f4f6"), 1)

def build(scene):
    c = col("L_SET"); sky_hdri(scene); sun(scene); road(c); ground(c); fence(c); cross_fence(c)   # the HDRI carries the clouds (no mesh clouds)
    fence(c, FENCE_XR, "fence_R", seed=5); god_rays(col("L_FX")); bounce_fill(c)          # light_shafts() is called by the shot once the oak exists
    return c
