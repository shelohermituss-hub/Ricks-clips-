"""Race-track sets of shot 2 (references/crashed_car/shots/s02.md), built for the camera, every object in a layer collection:
  L_SKY (clouds; the world is the sky), L_SET (ground, walls, fence, stands + crowd, roof, gantry, mechanics), L_OBJECTS (cars, props, debris),
  L_FX (confetti, dust). Characters go to L_SET (rule: render in layers).
    pit(scene)     pit lane: concrete with tyre marks, red/white edge stripe, pit wall with sponsor boards, 3 mechanics, chain-link fence,
                   packed grandstand under a flat roof, gantry beam + hanging air hose, red jack box
    corner(scene)  the corner after the crash: asphalt with curved skid marks, gravel + red debris, red/white kerb, gravel trap, low red/white
                   barrier with a blue tyre, grass, tall fence
Layout (metres): the car stands at the origin, nose towards -X; the camera looks from -Y; the pit wall runs along X at y=+6."""
import bpy, bmesh, math, random, os, sys
from mathutils import Vector, Matrix, noise
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import street  # noqa: E402  (mat, box, cyl, mesh_obj, srgb, cloud, sky helpers)

def lcol(name):
    return street.col(name)

def text_decal(name, c, txt, size, loc, rot, color="#ffffff", bg=None, extrude=.004):
    """flat 3D text (sponsor boards, decals): Blender text object converted to mesh"""
    cu = bpy.data.curves.new(name, "FONT"); cu.body = txt; cu.size = size; cu.extrude = extrude; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new(name, cu); c.objects.link(o); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(street.mat("txt_" + color, color, .5)); return o

def chainlink_mat():
    """chain-link fence: diamond wire pattern cut by alpha (procedural), grey metal"""
    if "chainlink" in bpy.data.materials: return bpy.data.materials["chainlink"]
    m = bpy.data.materials.new("chainlink"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*street.srgb("#8c9096"), 1); b.inputs["Metallic"].default_value = .7; b.inputs["Roughness"].default_value = .4
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, math.radians(45), 0); mp.inputs["Scale"].default_value = (14, 14, 14)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Mortar Size"].default_value = .06; br.inputs["Scale"].default_value = 1.0
    br.offset = 0.0; br.squash = 1.0; nt.links.new(mp.outputs["Vector"], br.inputs["Vector"])
    nt.links.new(br.outputs["Fac"], b.inputs["Alpha"]); m.blend_method = "HASHED" if hasattr(m, "blend_method") else None
    return m

def crowd(c, x0, x1, rows, z0, y0, dz, dy, seed=0):
    """packed grandstand: rows of tiny stick-figure spectators (head ball + coloured body capsule), instanced from 6 variants"""
    rr = random.Random(seed); cols = ("#e2453c", "#2f6fd6", "#f2c230", "#3fb35a", "#f4f1ea", "#7a4fc9")
    vc = bpy.data.collections.get("crowd_variants") or bpy.data.collections.new("crowd_variants")
    variants = []
    for k, hc in enumerate(cols):
        if ("fan_%d" % k) in bpy.data.objects: variants.append(bpy.data.objects["fan_%d" % k]); continue
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.13); bmesh.ops.translate(bm, vec=(0, 0, .62), verts=bm.verts)
        b2 = bmesh.new(); bmesh.ops.create_cone(b2, cap_ends=True, segments=6, radius1=.16, radius2=.12, depth=.42); bmesh.ops.translate(b2, vec=(0, 0, .3), verts=b2.verts)
        vm = {v: bm.verts.new(v.co) for v in b2.verts}
        for f in b2.faces: bm.faces.new([vm[v] for v in f.verts])
        b2.free(); me = bpy.data.meshes.new("fan_%d" % k); bm.to_mesh(me); bm.free()
        me.materials.append(street.mat("fan_head", "#f4f1ea", .6)); me.materials.append(street.mat("fan_body_" + hc, hc, .7))
        for p in me.polygons: p.material_index = 0 if p.center.z > .52 else 1
        o = bpy.data.objects.new("fan_%d" % k, me); vc.objects.link(o); variants.append(o)
    pts = []
    for r in range(rows):
        x = x0
        while x < x1:
            pts.append((x + rr.uniform(-.05, .05), y0 + r * dy, z0 + r * dz, rr.randrange(len(variants)))); x += rr.uniform(.36, .5)
    for k, v in enumerate(variants):                                 # one point cloud per variant, instanced by geometry nodes
        P = [(x, y, z) for x, y, z, i in pts if i == k]
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "blender"))
        from rc import geo
        src = bpy.data.collections.get("fanv_%d" % k) or bpy.data.collections.new("fanv_%d" % k)
        if v.name not in src.objects: src.objects.link(v)
        geo.instancer("crowd_%d" % k, P, src, c, [(0, 0, rr.uniform(-.3, .3)) for _ in P], [rr.uniform(.9, 1.1) for _ in P])
    return len(pts)

def stick_mechanic(name, c, loc):
    """a pit mechanic seen behind the wall: white helmet ball, white overalls body (simple, far away)"""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=.17); o = street.mesh_obj(name + "_head", bm, street.mat("mech_white", "#f2f2ee", .5), c, smooth=True); o.location = (loc[0], loc[1], loc[2] + .62)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.17, radius2=.13, depth=.45); b = street.mesh_obj(name + "_body", bm, street.mat("mech_white", "#f2f2ee", .5), c, smooth=True); b.location = (loc[0], loc[1], loc[2] + .25)

def pit(scene):
    SET, OBJ, SKY = lcol("L_SET"), lcol("L_OBJECTS"), lcol("L_SKY")
    conc = street.mat("pit_concrete", "#999b9f", .85, bump=("noise", 22, .15)); street.stains(conc, "#6e7074", 1.6, .55)
    street.box("pit_floor", SET, (80, 30, .1), (0, 0, -.05), conc, bevel=0)
    for k in range(7):                                               # dark tyre marks on the pit floor
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(6, .22, .004), verts=bm.verts)
        o = street.mesh_obj("tyre_mark", bm, street.mat("tyre_mark", "#3d3f43", .9), SET); o.location = (-12 + k * 4.5, -1.5 + (k % 3) * 1.1, .002); o.rotation_euler = (0, 0, math.radians(-8 + k * 3))
    street.box("pit_stripe_red", SET, (80, 1.4, .01), (0, -4.6, .004), street.mat("stripe_red", "#e0202a", .55), bevel=0)
    street.box("pit_stripe_white", SET, (80, .22, .012), (0, -3.8, .005), street.mat("stripe_white", "#f2f0ea", .55), bevel=0)
    wall = street.mat("pit_wall", "#c8cacc", .7, bump=("noise", 18, .1)); street.box("pit_wall", SET, (80, .5, 1.1), (0, 6, .55), wall, bevel=.04)
    for k in range(-5, 6):                                            # sponsor boards on the pit wall
        x = k * 4.2; green = k % 2 == 0
        street.box("board", SET, (3.4, .04, .55), (x, 5.72, .6), street.mat("board_green" if green else "board_black", "#1f6b3a" if green else "#1b1c20", .5), bevel=.01)
        text_decal("board_txt", SET, "BIG BARREL" if green else "ZOOM", .32, (x, 5.69, .6), (math.pi / 2, 0, 0), "#f4f1ea" if green else "#ff8a1f")
    for k, x in enumerate((7.5, 8.1, 8.7)): stick_mechanic("mech%d" % k, SET, (x, 6.2, 1.1))
    fence = chainlink_mat()
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5); fo = street.mesh_obj("fence_mesh", bm, fence, SET)
    fo.scale = (80, 4.2, 1); fo.rotation_euler = (math.pi / 2, 0, 0); fo.location = (0, 6.6, 3.2)
    for k in range(-10, 11): street.cyl("fence_post", SET, .05, 4.4, (k * 4.0, 6.6, 2.2), street.mat("post_grey", "#7d8187", .4, .7), seg=8)
    # grandstand: stepped rows + crowd + flat roof
    stand = street.mat("stand_concrete", "#6d7178", .8)
    for r in range(10): street.box("stand_step", SET, (80, .9, .45), (0, 9 + r * .9, 1.2 + r * .45 - .22), stand, bevel=0)
    n = crowd(SET, -38, 38, 10, 1.2, 9.0, .45, .9, seed=4)
    street.box("stand_roof", SET, (82, 12, .4), (0, 13.5, 7.6), street.mat("roof_dark", "#3a3d44", .7), bevel=0)
    for k in range(-8, 9): street.box("roof_beam", SET, (.25, 12, .5), (k * 5, 13.5, 7.3), street.mat("beam_grey", "#575b63", .6), bevel=0)
    # pit gantry above the car + hanging air hose + red jack box
    steel = street.mat("gantry_steel", "#4b4f57", .45, .6)
    street.box("gantry_beam", OBJ, (14, .35, .35), (0, -1.5, 5.4), steel, bevel=.02)
    pts = [Vector((1.8, -1.5, 5.2)), Vector((1.9, -1.2, 3.6)), Vector((2.0, -.6, 1.6)), Vector((2.3, -.2, .1))]
    cu = bpy.data.curves.new("hose", "CURVE"); cu.dimensions = "3D"; sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
    cu.bevel_depth = .03; ho = bpy.data.objects.new("air_hose", cu); OBJ.objects.link(ho); ho.data.materials.append(street.mat("hose_black", "#151517", .5))
    street.box("jack_box", OBJ, (.45, .35, .3), (2.6, -.3, .15), street.mat("jack_red", "#d61f26", .4), bevel=.03)
    for k, (x, y, z, s) in enumerate(((-25, 60, 26, 14), (20, 70, 30, 16), (60, 80, 24, 12))): o = street.cloud("cloud%d" % k, SKY, (x, y, z), s, seed=k + 3)
    street.sky(scene, "day")
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 5.5; sun.angle = math.radians(3); sun.color = street.srgb("#fff3dc")
    so = bpy.data.objects.new("sun", sun); lcol("L_LIGHTS").objects.link(so); so.rotation_euler = (math.radians(42), 0, math.radians(25))   # front-right sun: lit faces, like the reference
    return n

def corner(scene):
    SET, OBJ, SKY = lcol("L_SET"), lcol("L_OBJECTS"), lcol("L_SKY")
    asph = street.mat("track_asphalt", "#55585e", .85, bump=("noise", 35, .2)); street.stains(asph, "#3b3d42", 1.4, .5)
    street.box("track", SET, (60, 40, .1), (0, -10, -.05), asph, bevel=0)
    skid = street.mat("skid", "#222326", .9)
    for k in range(3):                                                # curved skid marks sweeping to the right
        cu = bpy.data.curves.new("skid%d" % k, "CURVE"); cu.dimensions = "2D"; sp = cu.splines.new("BEZIER"); sp.bezier_points.add(2)
        for bp, p in zip(sp.bezier_points, ((-1 + k * .6, -9, .003), (1.5 + k * .4, -4, .003), (5 + k * .5, 1.0, .003))): bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
        cu.fill_mode = "BOTH"
        o = bpy.data.objects.new("skid%d" % k, cu); SET.objects.link(o); o.data.materials.append(skid); o.data.extrude = .002; o.data.bevel_depth = .12
    gravel = street.mat("gravel", "#b9a27c", .95, bump=("noise", 60, .8)); street.box("gravel_trap", SET, (60, 3.2, .06), (0, 3.4, .0), gravel, bevel=0)
    for k in range(-14, 15):                                          # red/white kerb blocks
        street.box("kerb", SET, (1.0, .9, .08), (k * 1.0, 1.4, .03), street.mat("kerb_red" if k % 2 else "kerb_white", "#d9232c" if k % 2 else "#f2f0ea", .55), bevel=.02)
    for k in range(-12, 13): street.box("barrier", SET, (1.0, .25, .5), (k * 1.0, 5.2, .25), street.mat("barrier_red" if k % 2 else "barrier_white", "#d9232c" if k % 2 else "#f2f0ea", .55), bevel=.02)
    street.cyl("blue_tyre", SET, .38, .3, (2.3, 5.0, .55), street.mat("tyre_blue", "#2346a8", .6), seg=20, rot=(math.pi / 2, 0, 0))
    street.box("grass_strip", SET, (60, 5, .05), (0, 8.2, .0), street.mat("track_grass", "#4fa22a", .9, bump=("noise", 30, .2)), bevel=0)
    fence = chainlink_mat(); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5); fo = street.mesh_obj("fence_mesh", bm, fence, SET)
    fo.scale = (60, 6, 1); fo.rotation_euler = (math.pi / 2, 0, 0); fo.location = (0, 10.8, 3.0)
    for k in range(-7, 8): street.cyl("fence_post", SET, .06, 6.2, (k * 4.0, 10.8, 3.0), street.mat("post_grey", "#7d8187", .4, .7), seg=8)
    rr = random.Random(7); deb = street.mat("debris_red", "#c9141c", .45); stone = street.mat("stone_beige", "#a89474", .9)
    for k in range(140):                                              # gravel stones and red bodywork chips scattered on the asphalt
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rr.uniform(.03, .07))
        red = k % 6 == 0; o = street.mesh_obj("chip" if red else "stone", bm, deb if red else stone, OBJ, smooth=not red)
        o.location = (rr.uniform(-4, 5), rr.uniform(-6, 1.0), .02); o.scale = (1.6 if red else 1, .6 if red else 1, .3 if red else .7); o.rotation_euler = (0, 0, rr.uniform(0, 6.3))
    for k, (x, y, z, s) in enumerate(((-18, 60, 22, 13), (15, 70, 28, 15))): street.cloud("cloud%d" % k, SKY, (x, y, z), s, seed=k + 7)
    street.sky(scene, "day")
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 5.5; sun.angle = math.radians(3); sun.color = street.srgb("#fff3dc")
    so = bpy.data.objects.new("sun", sun); lcol("L_LIGHTS").objects.link(so); so.rotation_euler = (math.radians(48), 0, math.radians(20))
