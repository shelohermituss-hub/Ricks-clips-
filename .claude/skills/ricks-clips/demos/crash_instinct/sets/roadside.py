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

HDRI = "kloofendal_48d_partly_cloudy_puresky"; HDRI_SUN_DEG = -34.2          # its sun: atan2(y, x) of the brightest pixel (measured), elevation 47.8
SUN_AZ, SUN_EL = 30.5, 45.0                                                     # CB 2026-11-19: backlit like the reference (sun behind the tree, right)

def sky_hdri(scene, strength=1.0):
    """CINEMATIC SKY (CB 2026-11-19): a real cloudy sky photo (Poly Haven CC0) seen by the camera AND lighting the scene (soft fill, so the
    trunk is never black in daylight); rotated so its sun sits where the sun lamp is"""
    from rc import fetch
    w = bpy.data.worlds.new("sky_hdri"); scene.world = w; w.use_nodes = True; nt = w.node_tree; N, L = nt.nodes, nt.links; bg = N["Background"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); env = N.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(fetch.polyhaven_hdri(HDRI, "1k", log=lambda *a: None), check_existing=True)
    want = math.degrees(math.atan2(math.cos(math.radians(SUN_AZ)), math.sin(math.radians(SUN_AZ))))     # direction the light comes from, as atan2(y, x)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(HDRI_SUN_DEG - want))
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], env.inputs["Vector"]); L.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength

def god_rays(c, center=(0, 0, 0), size=(34, 34, 16), density=.003, anisotropy=.75):
    """SUN RAYS (CB 2026-11-19): a light haze volume around the tree; the sun lamp shining through the crown draws the shafts"""
    m = bpy.data.materials.get("god_ray_haze") or bpy.data.materials.new("god_ray_haze"); m.use_nodes = True; nt = m.node_tree
    for n_ in list(nt.nodes):
        if n_.type != "OUTPUT_MATERIAL": nt.nodes.remove(n_)
    v = nt.nodes.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = density; v.inputs["Anisotropy"].default_value = anisotropy
    v.inputs["Color"].default_value = (1, .97, .9, 1); nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    o = box("god_rays", c, size, (center[0], center[1], size[2] / 2 - .05), m, bevel=0); o.visible_shadow = False
    return o

def light_shafts(c, n=12, seed=3, under=(0, 0, 4.6), spread=3.0, length=7.0, strength=.2, parent=None):
    """SUN RAYS you can SEE (CB 2026-11-19): soft tapered shafts falling from gaps under the crown along the sun direction, additive light
    (transparent + emission, fading along the shaft and at its edges); the reference shows them under the tree in daylight"""
    import random as _r
    R = _r.Random(seed); el, az = math.radians(SUN_EL), math.radians(SUN_AZ)
    d = -Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))      # the way the light travels
    m = bpy.data.materials.get("light_shaft")
    if not m:
        m = bpy.data.materials.new("light_shaft"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
        for n_ in list(N):
            if n_.type != "OUTPUT_MATERIAL": N.remove(n_)
        tc = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sx.inputs[0])
        along = N.new("ShaderNodeMath"); along.operation = "SUBTRACT"; along.inputs[0].default_value = 1.0; L.new(sx.outputs["Y"], along.inputs[1])
        edge = N.new("ShaderNodeMath"); edge.operation = "SINE"; m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.inputs[1].default_value = math.pi
        L.new(sx.outputs["X"], m2.inputs[0]); L.new(m2.outputs[0], edge.inputs[0])
        k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; L.new(along.outputs[0], k.inputs[0]); L.new(edge.outputs[0], k.inputs[1])
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1, .95, .82, 1)
        st = N.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength; L.new(k.outputs[0], st.inputs[0]); L.new(st.outputs[0], em.inputs["Strength"])
        tr = N.new("ShaderNodeBsdfTransparent"); add = N.new("ShaderNodeAddShader"); L.new(tr.outputs[0], add.inputs[0]); L.new(em.outputs[0], add.inputs[1])
        L.new(add.outputs[0], N["Material Output"].inputs["Surface"])
    side = d.cross(Vector((0, 0, 1))).normalized(); out = []
    for i in range(n):
        p0 = Vector(under) + Vector((R.uniform(-spread, spread), R.uniform(-spread, spread), R.uniform(-.4, .6))); w0, w1 = R.uniform(.06, .16), R.uniform(.18, .38)
        p1 = p0 + d * (length * R.uniform(.8, 1.1))
        bm = bmesh.new(); uv = bm.loops.layers.uv.new()
        vs = [bm.verts.new(v) for v in (p0 - side * w0, p0 + side * w0, p1 + side * w1, p1 - side * w1)]; f = bm.faces.new(vs)
        for lp, (u_, v_) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uv].uv = (u_, v_)
        o = mesh_obj("light_shaft%d" % i, bm, m, c); o.visible_shadow = False; o.visible_glossy = False; out.append(o)
        if parent: o.parent = parent                                                        # they belong to the tree (fall with it)
    return out

def bounce_fill(c, at=(-3.0, -9.0, 2.2), aim=(0, 0, 2.0), energy=900.0, size=7.0):
    """CINEMATIC FILL (CB 2026-11-19: "le tronc est tout sombre en plein jour"): a big soft area light on the camera side, like a bounce board;
    invisible to the camera and in reflections, it opens the shadow side of the trunk and the characters under the crown"""
    l = bpy.data.lights.new("bounce_fill", "AREA"); l.energy = energy; l.size = size; l.color = srgb("#fff6ea")
    o = bpy.data.objects.new("bounce_fill", l); col("LIGHT").objects.link(o); o.location = at
    o.rotation_euler = (Vector(aim) - Vector(at)).to_track_quat("-Z", "Y").to_euler()
    o.visible_camera = False; o.visible_glossy = False
    return o

def sun(scene, elevation=SUN_EL, azimuth=SUN_AZ, energy=4.2, angle=2.0):
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

def cross_fence(c, y=10.0, x0=FENCE_X, x1=1.3):
    """a field fence perpendicular to the road, behind the tree (seen behind the planter at grass level, shot 2)"""
    wood = bpy.data.materials.get("fence_post"); wire = bpy.data.materials.get("barbed_wire")
    for k in range(int((x1 - x0) / 3) + 1):
        x = x0 + 3 * k; o = cyl("xpost%d" % k, c, .062, 1.25, (x, y, .62), wood, seg=8)
    for z in (.55, .85, 1.15):
        o = cyl("xwire_%d" % int(z * 100), c, .006, x1 - x0, ((x0 + x1) / 2, y + .07, z), wire, seg=4, rot=(0, math.pi / 2, 0), smooth=False); o.visible_shadow = False

def verge_grass(c, zone, n, seed, scale=(1.0, 1.8), exclude=()):
    """roadside grass from street's blade tufts, recoloured to the reference's soft yellow-green (saturation 0.29 measured)"""
    from rc import geo
    src = street.blade_clump(); m = bpy.data.materials.get("grass_blades")
    if m and not m.get("rc_recoloured"):
        cr = [n_ for n_ in m.node_tree.nodes if n_.type == "VALTORGB"][0].color_ramp
        cr.elements[0].color = (*srgb("#4e8a2e"), 1); cr.elements[1].color = (*srgb("#a4d866"), 1)   # CB 2026-11-19: brighter, more saturated   # measured on the reference: #44662e (shade) .. #65932d (sun); m["rc_recoloured"] = 1
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
    god_rays(col("L_FX")); bounce_fill(c)          # light_shafts() is called by the shot once the oak exists
    return c
