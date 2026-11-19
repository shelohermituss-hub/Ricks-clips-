"""gta6-leak — the budget hotel room at night (plan.json place "hotel"), built for the camera.
Layout (metres): floor centre at the origin, the TV dresser against the back wall (y = +1.8), the bed in front of it (foot at y = +0.3),
the window with curtains on the right wall (x = +2.1, the city outside), the door on the left wall. Layer collections L_SKY / L_SET /
L_OBJECTS / L_FX / L_LIGHTS (rule: render in layers). Real surfaces only (CC0 Poly Haven scans)."""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "demos", "crashed_car", "sets"))
import street, racetrack  # noqa: E402  (shared kit: box, cyl, mat, pbr, handheld, text_decal)

def lcol(n): return street.col(n)

def night_world(scene, strength=.06):
    """dark blue night world (very low: the practical lights make the picture) + interior HDRI for reflections only"""
    w = bpy.data.worlds.new("night"); scene.world = w; w.use_nodes = True; bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*street.srgb("#0b1430"), 1); bg.inputs["Strength"].default_value = strength
    street.hdri_reflections(scene, "hotel_room", strength=.35)

def tv_screen_mat(name="tv_screen"):
    """screen: glossy black when off; emission driven by the 'rc_on' value node (0 off, 1 on) and a noise for the static burst"""
    m = bpy.data.materials.new(name); m.use_nodes = True; N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (.005, .006, .01, 1); b.inputs["Roughness"].default_value = .06
    em = N.new("ShaderNodeEmission"); add = N.new("ShaderNodeAddShader"); out = N["Material Output"]
    on = N.new("ShaderNodeValue"); on.name = "rc_on"; on.outputs[0].default_value = 0
    stat = N.new("ShaderNodeValue"); stat.name = "rc_static"; stat.outputs[0].default_value = 0
    nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = 180; nz.name = "rc_noise"
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; L.new(stat.outputs[0], mix.inputs[0]); mix.inputs[6].default_value = (*street.srgb("#3a7bff"), 1)
    L.new(nz.outputs["Fac"], mix.inputs[7])
    tc = N.new("ShaderNodeTexCoord"); gr = N.new("ShaderNodeTexGradient"); L.new(tc.outputs["Generated"], gr.inputs[0])   # boot screen: soft vertical gradient
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = .35; L.new(mix.outputs[2], mul.inputs[6]); L.new(gr.outputs[0], mul.inputs[7])
    L.new(mul.outputs[2], em.inputs["Color"]); st = N.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = 6.0; L.new(on.outputs[0], st.inputs[0]); L.new(st.outputs[0], em.inputs["Strength"])
    L.new(b.outputs[0], add.inputs[0]); L.new(em.outputs[0], add.inputs[1]); L.new(add.outputs[0], out.inputs["Surface"]); return m

def city_window_mat():
    """the city through the window: rows of lit / dark windows (brick texture as a window grid), a few warm, mostly cool"""
    m = bpy.data.materials.new("city_windows"); m.use_nodes = True; N, L = m.node_tree.nodes, m.node_tree.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); tc = N.new("ShaderNodeTexCoord")
    br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 9; br.inputs["Mortar Size"].default_value = .035; br.offset = 0
    br.inputs["Color1"].default_value = (*street.srgb("#ffd27a"), 1); br.inputs["Color2"].default_value = (*street.srgb("#0d1326"), 1); br.inputs["Mortar"].default_value = (*street.srgb("#070a14"), 1)
    L.new(tc.outputs["Object"], br.inputs["Vector"]); L.new(br.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = 1.6; L.new(em.outputs[0], out.inputs["Surface"]); return m

def duvet(c, size, loc, seed=3):
    """crumpled duvet: subdivided slab with a noise displacement (folds), white cotton"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = street.mesh_obj("duvet", bm, street.mat("cotton_white", "#e9e6df", .85, bump=("noise", 30, .25)), c, smooth=True); o.location = loc
    s = o.modifiers.new("sub", "SUBSURF"); s.levels = s.render_levels = 3
    t = bpy.data.textures.new("folds", "CLOUDS"); t.noise_scale = .35; d = o.modifiers.new("folds", "DISPLACE"); d.texture = t; d.strength = .07; d.texture_coords = "GLOBAL"
    return o

def build(scene):
    S, O, F, LT = lcol("L_SET"), lcol("L_OBJECTS"), lcol("L_FX"), lcol("L_LIGHTS"); lcol("L_SKY")
    carpet = street.pbr("hotel_carpet", "acg:Carpet012", tile=1.0, tint="#8a3a4c", tint_k=.75, value=1.25)   # continuous pile (the woven pattern read as tiles)
    wall = street.pbr("hotel_wall", "beige_wall_001", tile=1.4, value=1.05); wood = street.pbr("dresser_wood", "wood_table_001", tile=.8, value=.9)
    leather = street.pbr("headboard", "fabric_leather_02", tile=.6, tint="#3b2b2a", tint_k=.5)
    street.box("floor", S, (4.4, 4.2, .05), (0, 0, -.025), carpet, bevel=0)
    street.box("wall_back", S, (4.4, .1, 2.7), (0, 2.1, 1.35), wall, bevel=0)
    street.box("wall_left", S, (.1, 4.2, 2.7), (-2.2, 0, 1.35), wall, bevel=0)
    street.box("wall_front", S, (4.4, .1, 2.7), (0, -2.1, 1.35), wall, bevel=0)
    street.box("ceiling", S, (4.4, 4.2, .05), (0, 0, 2.7), street.mat("ceiling", "#d8d2c6", .9), bevel=0)
    for z0, z1 in ((0, .55), (2.25, 2.7)): street.box("wall_right", S, (.1, 4.2, z1 - z0), (2.2, 0, (z0 + z1) / 2), wall, bevel=0)   # right wall around the window
    for y0, y1 in ((-2.1, -.5), (1.3, 2.1)): street.box("wall_right", S, (.1, y1 - y0, 1.7), (2.2, (y0 + y1) / 2, 1.4), wall, bevel=0)
    street.box("window_frame", S, (.08, 1.85, .06), (2.18, .4, .55), street.mat("frame_white", "#eeeae2", .4), bevel=.01)
    street.box("window_frame", S, (.08, 1.85, .06), (2.18, .4, 2.25), street.mat("frame_white", "#eeeae2", .4), bevel=.01)
    city = street.box("city_outside", lcol("L_SKY"), (.02, 9, 5), (5.5, .4, 1.6), city_window_mat(), bevel=0)
    for k, y in enumerate((-.35, 1.15)):                                    # curtains half drawn: folded fabric planes
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=24, y_segments=2, size=.5)
        for v in bm.verts: v.co.z, v.co.x = v.co.y * 2.0, .05 * math.sin(v.co.x * 28)
        cu = street.mesh_obj("curtain", bm, street.pbr("curtain_fabric", "fabric_pattern_05", tile=.5, tint="#5b2f6b", tint_k=.7, value=.8), S, smooth=True)
        cu.rotation_euler = (0, 0, math.pi / 2); cu.location = (2.05, y, 1.4); cu.scale = (.65, 1, 1.15)
    # dresser + TV + props
    street.box("dresser", S, (1.9, .5, .72), (0, 1.8, .36), wood, bevel=.015)
    for x in (-.5, .5): street.box("drawer_handle", S, (.18, .02, .02), (x, 1.54, .5), street.mat("brass", "#b08d4a", .3, .9), bevel=.005)
    street.box("tv_bezel", O, (1.12, .05, .66), (-.2, 2.03, 1.15), street.mat("tv_black", "#0d0e10", .2), bevel=.012)     # wall-mounted, ports on its left side
    scr = street.box("tv_screen", O, (1.06, .012, .6), (-.2, 2.003, 1.15), tv_screen_mat(), bevel=0)
    street.box("tv_wall_mount", O, (.3, .04, .2), (-.2, 2.07, 1.15), street.mat("tv_black", "#0d0e10", .2), bevel=.005)
    street.box("tv_port", O, (.012, .03, .02), (-.765, 2.0, 1.02), street.mat("port_dark", "#050505", .4), bevel=0)
    # bed
    street.box("bed_base", S, (1.65, 2.1, .32), (-.15, -.85, .16), street.mat("bed_base", "#3a2a24", .7), bevel=.02)
    street.box("mattress", S, (1.6, 2.05, .22), (-.15, -.85, .43), street.mat("mattress", "#f1eee7", .85), bevel=.05)
    duvet(S, (1.66, 1.5, .1), (-.15, -.55, .58))
    for x in (-.55, .25): pl = street.box("pillow", S, (.6, .38, .14), (x, -1.62, .62), street.mat("cotton_white", "#e9e6df", .85), bevel=.06); pl.rotation_euler.x = math.radians(-18)
    street.box("headboard", S, (1.85, .08, .9), (-.15, -1.98, .85), leather, bevel=.03)
    # bedside table + lamp (warm practical)
    street.box("bedside", S, (.45, .4, .55), (-1.25, -1.75, .275), wood, bevel=.015)
    street.cyl("lamp_base", S, .07, .3, (-1.25, -1.75, .7), street.mat("brass", "#b08d4a", .3, .9), seg=16)
    shade = street.cyl("lamp_shade", S, .16, .22, (-1.25, -1.75, .95), street.mat("lampshade", "#f3e2c0", .9), seg=20)
    shade.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*street.srgb("#ffc27a"), 1)
    shade.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.2
    # door on the left wall with the DO NOT DISTURB hanger
    street.box("door", S, (.06, .95, 2.1), (-2.16, -.6, 1.05), wood, bevel=.01)
    street.cyl("door_handle", S, .02, .12, (-2.11, -.2, 1.0), street.mat("brass", "#b08d4a", .3, .9), seg=10, rot=(0, math.pi / 2, 0))
    hg = street.box("dnd_hanger", O, (.01, .1, .24), (-2.1, -.2, .86), street.mat("dnd_red", "#c8202a", .5), bevel=.004)
    racetrack.text_decal("dnd_text", O, "DO NOT\nDISTURB", .028, (-2.094, -.2, .86), (math.pi / 2, 0, -math.pi / 2), "#f4f1ea")
    # room-service tray (left of the TV), key card sleeve with the 18 sticker (fact), energy drinks (one will be knocked over)
    street.box("tray", O, (.5, .34, .02), (-.7, 1.75, .73), street.mat("tray_steel", "#b9bcc2", .25, .9), bevel=.006)
    street.cyl("plate", O, .12, .015, (-.75, 1.75, .745), street.mat("plate", "#f6f4ee", .3), seg=24)
    street.cyl("cloche", O, .1, .09, (-.55, 1.78, .78), street.mat("tray_steel", "#b9bcc2", .25, .9), seg=24)
    kc = street.box("keycard_sleeve", O, (.09, .06, .004), (.75, 1.62, .725), street.mat("keycard", "#1f3a8a", .4), bevel=.002); kc.rotation_euler.z = .3
    racetrack.text_decal("keycard_18", O, "18", .03, (.75, 1.62, .728), (0, 0, .3), "#ffd23a")
    dress(S, O, wood)
    return {"screen": scr, "tv_center": Vector((-.2, 2.003, 1.15))}

def dress(S, O, wood):
    """what makes it read as a HOTEL ROOM in the wide shot: painting above the TV, two wall sconces, open suitcase with clothes,
    stacked pizza boxes, a chair with his hoodie, a laundry bag"""
    street.box("painting_frame", S, (.9, .03, .55), (-.2, 2.04, 2.05), street.mat("frame_gold", "#a5803f", .35, .8), bevel=.01)
    art = street.box("painting", S, (.82, .01, .47), (-.2, 2.022, 2.05), street.mat("canvas_blue", "#3f6e9e", .8, bump=("noise", 6, .4)), bevel=0)
    for x in (-1.05, .65):
        street.cyl("sconce", S, .07, .16, (x, 2.03, 1.75), street.mat("sconce_glass", "#ffe2b0", .5), seg=16)
        m = bpy.data.materials["sconce_glass"].node_tree.nodes["Principled BSDF"]; m.inputs["Emission Color"].default_value = (*street.srgb("#ffc27a"), 1); m.inputs["Emission Strength"].default_value = 3
        d = bpy.data.lights.new("sconce_light", "POINT"); d.energy = 12; d.color = street.srgb("#ffb56b"); d.shadow_soft_size = .08; l = bpy.data.objects.new("sconce_light", d); street.col("L_LIGHTS").objects.link(l); l.location = (x, 1.95, 1.75)
    case = street.box("suitcase", O, (.7, .45, .2), (.3, .95, .1), street.mat("suitcase_blue", "#22406e", .4), bevel=.03)
    lid = street.box("suitcase_lid", O, (.7, .06, .45), (.3, 1.2, .33), street.mat("suitcase_blue", "#22406e", .4), bevel=.03); lid.rotation_euler.x = math.radians(-15)
    rr = random.Random(9)
    for k, c in enumerate(("#c94b3b", "#f0eadc", "#2e7d4f", "#d9b23a", "#1f1f26")):     # clothes spilling out of the suitcase
        cl = street.box("clothes", O, (.32, .26, .05), (.15 + rr.uniform(-.1, .25), .9 + rr.uniform(-.12, .1), .22 + k * .025), street.mat("cloth_" + c, c, .9, bump=("noise", 25, .3)), bevel=.02)
        cl.rotation_euler.z = rr.uniform(-.6, .6)
    sock = street.box("sock", O, (.22, .07, .03), (-.1, .7, .015), street.mat("cloth_#f0eadc", "#f0eadc", .9), bevel=.015); sock.rotation_euler.z = .7
    for k in range(3):                                                         # pizza boxes on the floor by the bed
        b = street.box("pizza_box", O, (.42, .42, .045), (-.35 + k * .015, .3 - k * .02, .025 + k * .047), street.mat("cardboard", "#b88a55", .85, bump=("noise", 40, .2)), bevel=.004); b.rotation_euler.z = .2 * k - .2
    racetrack.text_decal("pizza_txt", O, "PIZZA", .07, (-.32, .26, .17), (0, 0, -.2), "#c8202a")
    street.box("chair_seat", S, (.48, .48, .05), (-1.75, .9, .46), wood, bevel=.01)
    for dx in (-.2, .2):
        for dy in (-.2, .2): street.box("chair_leg", S, (.04, .04, .45), (-1.75 + dx, .9 + dy, .22), wood, bevel=.005)
    street.box("chair_back", S, (.48, .05, .5), (-1.75, 1.12, .75), wood, bevel=.01)
    hood = street.box("hoodie_on_chair", O, (.46, .28, .1), (-1.75, 1.05, .82), street.mat("hoodie_grey", "#4a4f5a", .95, bump=("noise", 30, .3)), bevel=.05); hood.rotation_euler.x = math.radians(70)

def energy_can(name, loc, color="#d01f2f"):
    c = lcol("L_OBJECTS"); o = street.cyl(name, c, .033, .12, loc, street.mat("can_" + color, color, .25, .8), seg=20)
    racetrack.text_decal(name + "_txt", c, "VOLT", .02, (loc[0], loc[1] - .034, loc[2]), (math.pi / 2, 0, 0), "#f4f1ea").parent = o
    o.children[0].location = (0, -.034, 0); return o
