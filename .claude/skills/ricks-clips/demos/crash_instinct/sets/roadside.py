"""crash_instinct: the empty country road and its one tree (shots 1-10, 14-15, 17-19, 25), built for the frame.
Layout (metres): the tree trunk at the origin; the road runs along +Y, dead straight to the horizon, between x = 2.2 and x = 9.8
(white edge lines, a yellow dashed centre line at x = 6); a gravel shoulder 1.6-2.2; roadside grass on the tree side; a wooden
barbed-wire fence at x = -6.5; flat fields in alternating dry-beige / ploughed-brown bands to the horizon on both sides.
Analysis: references/crash_instinct/ANALYSE_FR.md §4 and shots/s01.md. Helpers (mat, pbr, grass tufts, clouds, handheld) come
from demos/crashed_car/sets/street.py."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "crashed_car", "sets")); sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "blender"))
import street  # noqa: E402
from street import srgb, col, mat, pbr, box, cyl, mesh_obj, cloud, lib_instance  # noqa: E402

ROAD = (2.2, 9.8); FENCE_X = -6.5; Y0, Y1 = -40.0, 700.0

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

def sun(scene, elevation=45, azimuth=-120, energy=5.2, angle=2.0):
    s = bpy.data.lights.new("sun", "SUN"); s.energy = energy; s.angle = math.radians(angle); s.color = srgb("#fff3e2")
    o = bpy.data.objects.new("sun", s); col("LIGHT").objects.link(o)
    el, az = math.radians(elevation), math.radians(azimuth)                       # azimuth: direction the light COMES FROM, 0 = +Y, -90 = -X
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    o.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); return o

def road(c):
    asphalt = pbr("road_asphalt", "asphalt_track", tile=3.0, value=1.6, rough_mul=1.1)
    plane("road", c, ROAD[0], ROAD[1], Y0, Y1, asphalt, .02)
    gravel = pbr("shoulder_gravel", "asphalt_track", tile=1.2, value=1.15, tint="#b8a888", tint_k=.5)
    plane("shoulder_L", c, 1.5, ROAD[0], Y0, Y1, gravel, .012); plane("shoulder_R", c, ROAD[1], ROAD[1] + .7, Y0, Y1, gravel, .012)
    white = mat("paint_white", "#f2f2ec", .45); yellow = mat("paint_yellow", "#f7cf4a", .5)
    plane("edge_L", c, ROAD[0] + .2, ROAD[0] + .35, Y0, Y1, white, .026); plane("edge_R", c, ROAD[1] - .35, ROAD[1] - .2, Y0, Y1, white, .026)
    bm = bmesh.new(); y = Y0                                                       # yellow centre: dashed 3 m every 12 m, one mesh
    while y < Y1:
        vs = [bm.verts.new(v) for v in ((5.9, y, .026), (6.1, y, .026), (6.1, y + 3, .026), (5.9, y + 3, .026))]; bm.faces.new(vs); y += 12
    mesh_obj("centre_line", bm, yellow, c)

def ground(c):
    grass = pbr("verge_grass", "leafy_grass", tile=2.0, value=1.1)
    plane("verge", c, FENCE_X - .5, 1.5, Y0, Y1, grass, 0.0); plane("verge_R", c, ROAD[1] + .7, ROAD[1] + 5, Y0, Y1, grass, 0.0)
    fields(c)

def fields(c):
    """flat farmland in bands parallel to the road: dry beige stubble / ploughed brown, to the horizon on both sides"""
    dry = pbr("field_dry", "leafy_grass", tile=4.0, tint="#c9b27a", tint_k=.85, value=1.25)
    plough = pbr("field_plough", "brown_mud_02", tile=3.0, value=1.05)
    for side, x0, x1 in (("L", -400.0, FENCE_X - .5), ("R", ROAD[1] + 5, 400.0)):
        x = x1 if side == "L" else x0; k = 0
        while (x > x0 if side == "L" else x < x1):
            w = 9.0 + (k % 3) * 4
            a, b = (x - w, x) if side == "L" else (x, x + w)
            plane("field_%s%d" % (side, k), c, a, b, Y0, Y1, dry if k % 2 == 0 else plough, -.01)
            x = a if side == "L" else b; k += 1
            if k > 40: break

def fence(c):
    """grey wooden posts every 3 m with three barbed wires, along x = FENCE_X to the horizon (posts: one mesh, instanced)"""
    wood = pbr("fence_post", "brown_planks_05", tile=.6, tint="#9a958c", tint_k=.6, value=1.1)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.065, radius2=.055, depth=1.25); bmesh.ops.translate(bm, vec=(0, 0, .62), verts=bm.verts)
    me = bpy.data.meshes.new("post"); bm.to_mesh(me); bm.free(); me.materials.append(wood)
    pc = bpy.data.collections.new("post_src"); po = bpy.data.objects.new("post", me); pc.objects.link(po)
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "blender")); from rc import geo
    P = [(FENCE_X, y, 0) for y in [Y0 + 3 * k for k in range(int((Y1 - Y0) / 3))]]
    geo.instancer("fence_posts", P, pc, c, [(0, 0, (k * 1.7) % .4) for k in range(len(P))], [(1, 1, 1)] * len(P))
    wire = mat("barbed_wire", "#5a5a5c", .4, .8)
    for z in (.55, .85, 1.15):
        o = cyl("wire_%d" % int(z * 100), c, .006, Y1 - Y0, (FENCE_X + .07, (Y0 + Y1) / 2, z), wire, seg=4, rot=(math.pi / 2, 0, 0), smooth=False); o.visible_shadow = False

def verge_grass(c, zone, n, seed, scale=(1.0, 1.8), exclude=()):
    """roadside grass from street's blade tufts, recoloured to the reference's soft yellow-green (saturation 0.29 measured)"""
    from rc import geo
    src = street.blade_clump(); m = bpy.data.materials.get("grass_blades")
    if m and not m.get("rc_recoloured"):
        cr = [n_ for n_ in m.node_tree.nodes if n_.type == "VALTORGB"][0].color_ramp
        cr.elements[0].color = (*srgb("#4a7a26"), 1); cr.elements[1].color = (*srgb("#b6cf6c"), 1); m["rc_recoloured"] = 1
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
    c = col("L_SET"); sky(scene); sun(scene); road(c); ground(c); fence(c); clouds(col("L_SKY"))
    street.hdri_reflections(scene, strength=1.0)
    return c
