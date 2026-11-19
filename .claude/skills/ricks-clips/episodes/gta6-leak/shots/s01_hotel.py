"""gta6-leak S01 (0.00 - 5.48 s, local frames 0-165): "He leaked the biggest video game on Earth from a hotel room, using nothing but a TV
stick and a phone."  Plan: episodes/gta6-leak/plan/plan.json shot S01.
Actions (all through an action, nothing pops): his right hand brings the TV stick to the TV port (the stick follows the hand measured on
the drawing, then slides into the port) -> the TV wakes (static burst, blue boot light that spreads over the room and his face) -> sly grin
-> the phone on the dresser lights up (hotspot) -> his fist pump knocks the energy drink off the dresser: it falls, bounces, rolls and
fizzes, a wet stain stays on the carpet. Camera: frontal insert on the port -> rise to his lit face -> crane back to the room -> whip to
the door (S02). Layers: L_SKY / L_SET / L_OBJECTS / L_FX.
    blender -b --factory-startup --python s01_hotel.py -- <out.blend> [--res 270x480] [--samples 12]"""
import bpy, math, os, sys, json, random, bmesh
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.abspath(os.path.join(HERE, "..")); SKILL = os.path.abspath(os.path.join(EP, "..", ".."))
sys.path.insert(0, os.path.join(EP, "sets")); sys.path.insert(0, os.path.join(SKILL, "blender"))
import hotel  # noqa: E402
from hotel import street  # noqa: E402
from rc import render, characters  # noqa: E402
A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: A[A.index(k) + 1] if k in A else d
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/gta_s01.blend"
F0, F1 = 0, 165
KID = Vector((-.98, 1.42, 0)); PORT = Vector((-.79, 1.995, 1.02))
PLUG, TV_ON, KNOCK = 14, 17, 126            # HOOK: the stick is in and the TV wakes inside the first 0.6 s (7 refs: the action at once)

def key_val(node, value, f):
    node.outputs[0].default_value = value; node.outputs[0].keyframe_insert("default_value", frame=f)

def camera():
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); street.col("CAM").objects.link(cam); bpy.context.scene.camera = cam; cam.data.sensor_fit = "VERTICAL"
    # fov = VERTICAL angle in degrees (sensor fit vertical): 9:16 -> the horizontal angle is ~0.56x. Wide = 65-70, close = 40-45 (lesson 2026-11-19)
    keys = [(0, (-1.55, .35, 1.15), (-.85, 1.75, 1.0), 38), (40, (-1.45, .45, 1.2), (-.8, 1.8, 1.05), 36),        # insert: hand + stick + TV edge, slow push
            (52, (-1.25, .25, 1.55), (-.98, 1.42, 1.45), 42), (100, (-1.3, .15, 1.58), (-.98, 1.42, 1.45), 42),    # rise to his face lit by the TV
            (118, (-.15, -1.15, 1.6), (-.55, 1.35, 1.0), 62), (156, (-.25, -1.35, 1.66), (-.55, 1.3, .95), 64),     # crane back: kid, TV, painting, suitcase, pizza (all in the 9:16 width)
            (165, (-1.75, -1.7, 1.78), (-2.1, -.6, 1.1), 70)]                                                     # whip to the door (-> S02)
    for f, p, a, fov in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    street.handheld(cam, F0, F1, amp=.006, rot_deg=.18, seed=11)
    return cam

def lights(screen):
    LT = street.col("L_LIGHTS")
    def light(name, kind, energy, color, loc, rot=(0, 0, 0), size=None):
        d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = street.srgb(color)
        if size and kind == "AREA": d.size, d.size_y, d.shape = size[0], size[1], "RECTANGLE"
        o = bpy.data.objects.new(name, d); LT.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
    lamp = light("bedside_lamp", "POINT", 70, "#ffb56b", (-1.25, -1.75, .98)); lamp.data.shadow_soft_size = .12
    tv = light("tv_light", "AREA", 0, "#5b8cff", (-.2, 1.96, 1.12), (math.radians(90), 0, 0), (1.0, .58))
    for f, e in ((0, 0), (TV_ON - 1, 0), (TV_ON, 90), (TV_ON + 2, 25), (TV_ON + 4, 110), (TV_ON + 7, 60), (TV_ON + 14, 70)):  # static burst flicker, then boot
        tv.data.energy = e; tv.data.keyframe_insert("energy", frame=f)
    for f in range(TV_ON + 14, F1 + 1, 6): tv.data.energy = 70 + 8 * math.sin(f * .7); tv.data.keyframe_insert("energy", frame=f)   # screen content flicker
    neon = light("neon_outside", "AREA", 20, "#ff3fa4", (2.4, .4, 1.5), (0, math.radians(-90), 0), (1.2, 1.2))
    for f in range(F0, F1 + 1, 10): neon.data.energy = 18 + 9 * math.sin(f * .21); neon.data.keyframe_insert("energy", frame=f)
    sp = bpy.data.lights.new("neon_on_port", "SPOT"); sp.energy = 35; sp.color = street.srgb("#ff4fb0"); sp.spot_size = math.radians(35); sp.shadow_soft_size = .05
    so = bpy.data.objects.new("neon_on_port", sp); LT.objects.link(so); so.location = (.9, 1.0, 1.5); so.rotation_euler = (PORT - so.location).to_track_quat("-Z", "Y").to_euler()   # the window neon grazing the TV side
    fill = light("room_fill", "AREA", 18, "#8fa4d6", (0, -1.5, 2.6), (0, 0, 0), (2.5, 2.5))     # very low ceiling bounce so shadows stay readable
    rim = light("tv_spill_on_kid", "AREA", 0, "#5b8cff", (-.55, 1.85, 1.45), (math.radians(70), 0, math.radians(-60)), (.5, .5))   # the TV glow reaches his face
    for f, e in ((0, 0), (TV_ON - 1, 0), (TV_ON, 30), (TV_ON + 2, 8), (TV_ON + 4, 35), (TV_ON + 14, 28)): rim.data.energy = e; rim.data.keyframe_insert("energy", frame=f)
    O = street.col("L_OBJECTS"); txt = hotel.racetrack.text_decal("tv_loading", O, "LOADING . . .", .06, (-.2, 1.99, 1.12), (math.pi / 2, 0, 0), "#ffffff")
    tb = txt.data.materials[0]; tb = bpy.data.materials.new("tv_text_glow"); tb.use_nodes = True; txt.data.materials[0] = tb; pb = tb.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (1, 1, 1, 1); pb.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    for f, e in ((0, 0), (TV_ON + 14, 0), (TV_ON + 20, 5), (F1, 5)): pb.inputs["Emission Strength"].default_value = e; pb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)   # the display shows its text (fades in, no pop)
    nt = screen.data.materials[0].node_tree.nodes
    for f, on, st in ((0, 0, 0), (TV_ON - 1, 0, 0), (TV_ON, 1, 1), (TV_ON + 10, 1, 1), (TV_ON + 16, 1, 0)):
        key_val(nt["rc_on"], on, f); key_val(nt["rc_static"], st, f)
    nz = nt["rc_noise"]; nz.inputs["W"].default_value = 0; nz.inputs["W"].keyframe_insert("default_value", frame=TV_ON); nz.inputs["W"].default_value = 30; nz.inputs["W"].keyframe_insert("default_value", frame=TV_ON + 16)
    return tv

def cards(cam):
    cd = os.path.join(EP, "build", "cards_s01"); AN = json.load(open(os.path.join(cd, "cards", "kid", "anchors.json")))
    characters.place_cards(bpy.context.scene, cd, ["kid"], cam, .55, ground=bpy.data.objects.get("floor"))
    setc = street.col("L_SET")
    for o in [o for o in bpy.data.objects if o.name.lower() in ("card_kid", "contact_kid")]:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        setc.objects.link(o)
        for f in range(F0 - 1, F1 + 2):
            for dp in ("hide_render", "hide_viewport", "location"):
                try: o.keyframe_delete(dp, frame=f)
                except RuntimeError: pass
        o.hide_render = o.hide_viewport = False
    card = bpy.data.objects["Card_kid"]; card.location = KID; card.keyframe_insert("location", frame=F0)
    return card, AN

def aim_insert(cam, card, AN):
    """the insert (0-40) is OBJECT-ONLY: the TV port in close-up, the stick slides in from the edge of the frame (the hand that holds it is
    just outside the frame). Lesson 2026-11-19: a drawn character always faces the lens, so a close-up on its hand shows its torso;
    an insert on a held object is framed on the object, with the card out of frame."""
    for f, p, fov in ((0, (-.42, 1.58, 1.08), 40), (40, (-.3, 1.38, 1.18), 48)):     # tighter on the port, pulls back as the TV light floods in
        tgt = PORT + Vector((0, -.06, 0)); p = Vector(p)
        cam.location = p; cam.rotation_euler = (tgt - p).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)

def hand_world(card, AN, f, i):
    bpy.context.scene.frame_set(f); h = AN[str(f)]["hands"][i]; return card.matrix_world @ Vector((h[0], 0, h[1]))

def stick(card, AN):
    """the TV stick: in his right hand (follows the drawn hand), pushed into the port at PLUG, LED on with the TV; never pops"""
    O = street.col("L_OBJECTS"); s = street.box("tv_stick", O, (.03, .095, .014), (0, 0, 0), street.mat("stick_black", "#121214", .35), bevel=.004)
    led = street.box("stick_led", O, (.006, .006, .004), (0, -.03, .008), street.mat("led_off", "#1a1a1a", .3), bevel=0); led.parent = s
    m = led.data.materials[0].node_tree.nodes["Principled BSDF"]; m.inputs["Emission Color"].default_value = (*street.srgb("#3cff6a"), 1)
    prev = None
    for f in range(F0, F1 + 1):
        if f <= 6: tgt = hand_world(card, AN, f, 1) + Vector((0, .02, .015))
        elif f <= PLUG: t = (f - 6) / (PLUG - 6); tgt = hand_world(card, AN, 6, 1).lerp(PORT, t * t * (3 - 2 * t))   # slow approach: seen entering the insert
        else: tgt = PORT.copy()
        p = tgt if prev is None else prev + ((tgt - prev) if (tgt - prev).length <= .12 else (tgt - prev).normalized() * .12)
        prev = p.copy(); s.location = p; s.keyframe_insert("location", frame=f)
    s.rotation_euler = (0, 0, 0); s.keyframe_insert("rotation_euler", frame=F0)
    for f in range(F0, TV_ON, 4):                                   # red standby blink while held, green once the TV answers
        m.inputs["Emission Color"].default_value = (*street.srgb("#ff2a2a"), 1); m.inputs["Emission Color"].keyframe_insert("default_value", frame=f)
        m.inputs["Emission Strength"].default_value = 6 if (f // 4) % 2 == 0 else 1.5; m.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    for f, e in ((TV_ON, 6), (TV_ON + 3, 1), (TV_ON + 6, 6)):
        m.inputs["Emission Color"].default_value = (*street.srgb("#3cff6a"), 1); m.inputs["Emission Color"].keyframe_insert("default_value", frame=f)
        m.inputs["Emission Strength"].default_value = e; m.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    return s

def phone():
    O = street.col("L_OBJECTS"); p = street.box("phone", O, (.075, .15, .009), (.35, 1.72, .727), street.mat("phone_body", "#202226", .3, .6), bevel=.008); p.rotation_euler.z = -.4
    sc = street.box("phone_screen", O, (.068, .14, .001), (0, 0, .005), street.mat("phone_glass", "#05070a", .05), bevel=0); sc.parent = p
    b = sc.data.materials[0].node_tree.nodes["Principled BSDF"]; b.inputs["Emission Color"].default_value = (*street.srgb("#7fb2ff"), 1)
    for f, e, z in ((F0, 0, .727), (107, 0, .727), (108, 6, .727), (109, 2, .73), (110, 7, .727), (113, 7, .729), (116, 7, .727), (165, 7, .727)):   # lights up + buzz on the wood
        b.inputs["Emission Strength"].default_value = e; b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f); p.location.z = z; p.keyframe_insert("location", frame=f)
    return p

def can_knock(card, AN):
    """KNOCK: his swinging hand hits the can: it tips over the dresser edge, falls, bounces twice, rolls; fizz spray; a wet stain stays"""
    can = hotel.energy_can("can_hit", (-.63, 1.62, .78)); hotel.energy_can("can_2", (-.48, 1.72, .78), "#2f9e44")
    seq = [(KNOCK - 1, (-.63, 1.62, .78), (0, 0, 0)), (KNOCK + 3, (-.63, 1.52, .8), (math.radians(-35), 0, .2)), (KNOCK + 7, (-.64, 1.38, .66), (math.radians(-95), 0, .5)),
           (KNOCK + 13, (-.66, 1.22, .035), (math.radians(-90), 0, 1.4)), (KNOCK + 17, (-.68, 1.12, .12), (math.radians(-90), 0, 2.2)), (KNOCK + 21, (-.7, 1.04, .035), (math.radians(-90), 0, 2.9)),
           (KNOCK + 24, (-.71, 1.0, .07), (math.radians(-90), 0, 3.3)), (KNOCK + 27, (-.72, .96, .035), (math.radians(-90), 0, 3.6)), (F1, (-.78, .82, .035), (math.radians(-90), 0, 5.4))]
    for f, p, r in [(F0, (-.63, 1.62, .78), (0, 0, 0))] + seq:
        can.location = p; can.rotation_euler = r; can.keyframe_insert("location", frame=f); can.keyframe_insert("rotation_euler", frame=f)
    FX = street.col("L_FX"); rr = random.Random(5); drop = street.mat("fizz", "#e9f0ff", .05)
    for k in range(40):                                                      # fizz droplets from the can mouth, ballistic, die on the floor
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.006); o = street.mesh_obj("fizz", bm, drop, FX, smooth=True)
        f0 = KNOCK + 13 + rr.randint(0, 14); vx, vy, vz = rr.uniform(-.8, .8), rr.uniform(-.9, -.1), rr.uniform(.6, 1.6)
        base = Vector((-.7, 1.05, .05)); o.scale = (0, 0, 0); o.location = base; o.keyframe_insert("scale", frame=f0 - 1); o.keyframe_insert("location", frame=f0 - 1)
        for i in range(0, 14, 2):
            t = i / 30; o.location = base + Vector((vx * t, vy * t, max(0, vz * t - 4.9 * t * t))); o.scale = (1, 1, 1) if i < 12 else (0, 0, 0)
            o.keyframe_insert("location", frame=f0 + i); o.keyframe_insert("scale", frame=f0 + i)
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=.16)                   # the wet stain spreads and STAYS
    st = street.mesh_obj("fizz_stain", bm, street.mat("wet_stain", "#2a1a1e", .08), street.col("L_OBJECTS")); st.location = (-.72, 1.0, .003); st.scale = (.01, .01, 1)
    st.keyframe_insert("scale", frame=KNOCK + 13); st.scale = (1, .7, 1); st.keyframe_insert("scale", frame=KNOCK + 34)
    return can

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    for n in ("L_SKY", "L_SET", "L_OBJECTS", "L_FX", "L_LIGHTS"): street.col(n)
    hotel.night_world(sc); H = hotel.build(sc); cam = camera(); lights(H["screen"]); card, AN = cards(cam)
    aim_insert(cam, card, AN); stick(card, AN); phone(); can_knock(card, AN)
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"; sc.view_settings.exposure = .6; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    w, h = map(int, opt("--res", "270x480").split("x")); render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "12")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=OUT); print("SAVED", OUT)

if __name__ == "__main__": main()
