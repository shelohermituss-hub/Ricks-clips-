"""Shot 2, parts 2A + 2B (frames 122-199): pit lane. See references/crashed_car/shots/s02.md.
2A 122-142 young driver standing in the cockpit (arms out), low close camera sliding left, confetti; 139-145 fast whip pan;
2B 146-199 wide side view, he stands by the car; 158 the helmet lifts off (old face revealed), goes under his arm by 172; slow push-in.
Objects are sorted into the layer collections L_SKY / L_SET / L_OBJECTS / L_FX (rule: render in layers).
    blender -b --factory-startup --python s02_pit.py -- <out.blend> [--still f out.png] [--res 270x480] [--samples 12]"""
import bpy, math, os, sys, random, bmesh
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "sets")); sys.path.insert(0, os.path.join(SKILL, "blender"))
import street, racetrack  # noqa: E402
from rc import render, characters  # noqa: E402

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: A[A.index(k) + 1] if k in A else d
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s02_pit.blend"
F0, F1 = 122, 205
F1_GLTF = os.path.join(SKILL, "library", "assets", "sketchfab", "ca91852b29bb435d8d0278d9131aa775", "gltf", "scene.gltf")

def race_car():
    """the red formula car (Sketchfab 'Formula 1 Car Midpoly', LWDream, CC-BY): half scale (5.45 m), its single livery texture recoloured:
    dark parts (tyres, carbon) kept, everything else -> race red; real-brand logos disappear in the red"""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=F1_GLTF); new = [o for o in bpy.data.objects if o not in before]
    c = street.col("L_OBJECTS"); rig = bpy.data.objects.new("f1_rig", None); c.objects.link(rig)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = rig
    rig.scale = (.5, .5, .5)
    for m in {s.material for o in new if o.type == "MESH" for s in o.material_slots if s.material}:
        nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
        if not b or not b.inputs["Base Color"].links: continue
        src = b.inputs["Base Color"].links[0].from_socket; N, L = nt.nodes, nt.links
        hsv = N.new("ShaderNodeSeparateColor"); hsv.mode = "HSV"; L.new(src, hsv.inputs[0])          # keep greys/blacks (tyres, carbon); recolour any SATURATED
        ms = N.new("ShaderNodeMapRange"); ms.inputs["From Min"].default_value = .18; ms.inputs["From Max"].default_value = .32   # colour (the navy livery is dark but saturated)
        L.new(hsv.outputs[1], ms.inputs["Value"]); mv = N.new("ShaderNodeMapRange"); mv.inputs["From Min"].default_value = .22; mv.inputs["From Max"].default_value = .3
        L.new(hsv.outputs[2], mv.inputs["Value"]); mxm = N.new("ShaderNodeMath"); mxm.operation = "MAXIMUM"; L.new(ms.outputs[0], mxm.inputs[0]); L.new(mv.outputs[0], mxm.inputs[1])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; L.new(mxm.outputs[0], mx.inputs[0]); L.new(src, mx.inputs[6])
        mx.inputs[7].default_value = (*street.srgb("#cc101a"), 1); L.new(mx.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .32
        b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = .03; b.inputs["Coat IOR"].default_value = 1.5   # PAINT WITH DEPTH (CB 2026-11-19):
        b.inputs["Specular IOR Level"].default_value = .6                                       # base + glossy clear coat, reflecting the real sky HDRI
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(cn) for o in new if o.type == "MESH" for cn in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    rig.location = (-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z)       # centred on the origin, wheels on the floor
    return rig, (lo - Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)), hi - Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)))

def decals(box):
    """our own livery: BIG BARREL on both sidepods, the number 7 on the nose side"""
    c = street.col("L_OBJECTS"); lo, hi = box; L = hi.x - lo.x
    for s in (-1, 1):
        y = (hi.y if s > 0 else lo.y) * .5
        racetrack.text_decal("decal_bigbarrel", c, "BIG BARREL", .11, (lo.x + L * .52, y + s * .01, .55), (math.pi / 2, 0, 0 if s < 0 else math.pi), "#f4f1ea")
        racetrack.text_decal("decal_7", c, "7", .22, (lo.x + L * .25, y * .55 + s * .01, .5), (math.pi / 2, 0, 0 if s < 0 else math.pi), "#f4f1ea")

def helmet3d():
    """the white racing helmet as a real object (it lifts off at 158 and goes under his arm): shell, two blue stripes, dark visor"""
    c = street.col("L_OBJECTS"); root = bpy.data.objects.new("helmet3d", None); c.objects.link(root)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=.16)
    for v in bm.verts: v.co.z *= 1.08
    sh = street.mesh_obj("helmet_shell", bm, street.mat("helmet_white", "#f4f4f2", .3), c, smooth=True); sh.parent = root
    for x in (-.03, .03):
        st = street.box("helmet_stripe", c, (.03, .33, .02), (x, 0, .155), street.mat("helmet_blue", "#2f5fbf", .35), bevel=.005); st.parent = root
    v = street.box("helmet_visor", c, (.22, .06, .07), (0, -.145, .01), street.mat("visor_smoke", "#1d2633", .1, .3), bevel=.02); v.parent = root
    return root

def confetti(n=320, seed=5):
    """falling confetti: small coloured cards spinning down through the view, LINEAR keys (start, end) = cheap and deterministic"""
    c = street.col("L_FX"); rr = random.Random(seed); cols = ("#e2453c", "#2f6fd6", "#3fb35a", "#f4f1ea", "#f2c230")
    for k in range(n):
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.022); o = street.mesh_obj("confetti", bm, street.mat("conf_" + cols[k % 5], cols[k % 5], .5), c)
        x, y, z = rr.uniform(-6, 6), rr.uniform(-6, 3), rr.uniform(1.5, 7.5); dz = rr.uniform(2.5, 4.5); dx = rr.uniform(-.8, .8)
        o.location = (x, y, z); o.rotation_euler = (rr.uniform(0, 6.3), rr.uniform(0, 6.3), rr.uniform(0, 6.3)); o.keyframe_insert("location", frame=F0); o.keyframe_insert("rotation_euler", frame=F0)
        o.location = (x + dx, y, z - dz); o.rotation_euler = (o.rotation_euler.x + rr.uniform(6, 14), o.rotation_euler.y + rr.uniform(6, 14), o.rotation_euler.z); o.keyframe_insert("location", frame=F1); o.keyframe_insert("rotation_euler", frame=F1)
        ad = o.animation_data
        if ad and ad.action and hasattr(ad.action, "fcurves"):
            for fc in ad.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

def camera(box):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); street.col("CAM").objects.link(cam); bpy.context.scene.camera = cam
    cam.data.sensor_fit = "VERTICAL"; lo, hi = box; ck = Vector((lo.x + (hi.x - lo.x) * .45, 0, 1.25))     # cockpit
    # THE CAMERA NEVER STOPS (CB 2026-11-19): slide on the cockpit, whip to the wide while he jumps out (follows him), then a push-in
    # that keeps going to the last frame; handheld() adds a soft drift on every frame on top
    keys = [(122, ck + Vector((-1.5, -2.5, .95)), ck + Vector((.15, 0, .15)), 58), (134, ck + Vector((-1.05, -2.75, .92)), ck + Vector((.2, 0, .3)), 57),
            (142, Vector((-1.35, -7.6, 1.55)), Vector((-.6, -.6, 1.05)), 52), (152, Vector((-1.1, -7.25, 1.52)), Vector((-.5, -.4, 1.0)), 50),
            (175, Vector((-.85, -6.9, 1.5)), Vector((-.35, -.2, .98)), 49), (205, Vector((-.45, -6.35, 1.45)), Vector((-.25, 0, .95)), 47)]
    for f, p, a, fov in keys:
        cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    street.handheld(cam, F0, F1, seed=2)
    return cam, ck

def cards(cam, ck):
    """ONE character all through (CB 2026-11-19: no swap, no teleport): the hero in his race suit with the 3D helmet ON his head (it hides
    the face in 2A); 131-150 he JUMPS out of the cockpit on an arc and lands on the track; 158-172 he springs, both hands swing up to the
    helmet and pull it up off his head by its lower rim (old face revealed); 173+ the hands come down and the helmet goes under his right arm.
    The helmet follows the drawing itself: tools/card_anchors.py measures the head and gives the hands on every frame."""
    import json
    cd = os.path.join(HERE, "..", "build", "cards_s02"); folder = os.path.join(cd, "cards", "old")
    AN = json.load(open(os.path.join(folder, "anchors.json")))
    characters.place_cards(bpy.context.scene, cd, ["old"], cam, .55, ground=bpy.data.objects.get("pit_floor"))
    setc = street.col("L_SET"); sc = bpy.context.scene
    for o in [o for o in bpy.data.objects if o.name.lower() in ("card_old", "contact_old")]:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        setc.objects.link(o)
        for f in range(F0 - 1, F1 + 2):
            for dp in ("hide_render", "hide_viewport", "location"):
                try: o.keyframe_delete(dp, frame=f)
                except RuntimeError: pass
        o.hide_render = o.hide_viewport = False
    card = bpy.data.objects["Card_old"]; disc = bpy.data.objects.get("Contact_old")
    if disc:
        for cn in disc.constraints:
            if cn.type == "COPY_LOCATION": cn.use_z = False                  # the contact shadow stays on the floor while he is in the air
    cock = Vector((ck.x, 0, .05)); stand = Vector((ck.x - .6, -1.45, 0)); T0, T1 = 137, 150
    feet = lambda f: max(0., AN[str(f)]["feet"])
    for f in range(F0, F1 + 1):
        if f <= T0: p = cock.copy()
        elif f < T1:
            t = (f - T0) / (T1 - T0); e = t * t * (3 - 2 * t); p = cock.lerp(stand, e); p.z = cock.z * (1 - t) + 4 * .35 * t * (1 - t)   # JUMP arc (+ the drawing's own spring)
        else: p = stand.copy()
        card.location = p; card.keyframe_insert("location", frame=f)
    h = helmet3d(); S = 2.0; h.scale = (S, S, S); R = .16 * 1.08 * S
    prev = None; LIFT0, DOWN0 = 163, 173
    for f in range(F0, F1 + 1):
        sc.frame_set(f); M = card.matrix_world; a = AN[str(f)]; cpos = cam.matrix_world.translation; tocam = (cpos - M.translation); tocam.z = 0; tocam.normalize()
        head = M @ Vector((a["head_x"], 0, a["head_top"] - .27)) + tocam * .03
        hs = a["hands"]; rh = max(hs, key=lambda q: q[0])
        if f < LIFT0: tgt, fast = head, True                                 # ON the head, exactly where the drawing's head is
        elif f < DOWN0:
            mz = (hs[0][1] + hs[1][1]) / 2 + .38; mx_ = (hs[0][0] + hs[1][0]) / 2      # the hands hold its lower rim
            tgt = head if mz < a["head_top"] - .27 else M @ Vector((mx_, 0, mz)) + tocam * .03; fast = False          # hands grip it and pull it UP
        else:
            k = min(1., max(0., (1.35 - rh[1]) / .35)); tgt = M @ Vector((rh[0] + .24, 0, rh[1] + .06)) + tocam * (.03 - .33 * k); fast = False   # down with the right hand, tucked behind the arm
        if prev is None or fast: p = tgt
        else:
            d = tgt - prev; p = prev + (d if d.length <= .12 else d.normalized() * .12)   # a held thing never jumps: at most 12 cm per frame
        prev = p.copy(); h.location = p
        q = (cpos - p).to_track_quat("-Y", "Z"); e = q.to_euler()
        if LIFT0 <= f < DOWN0 + 4: e.x += math.radians(18) * min(1, (f - LIFT0) / 4)          # tilts back as it is pulled off
        if f >= DOWN0: e.z += math.radians(70) * min(1, (f - DOWN0) / 8)                    # turns sideways under the arm
        h.rotation_euler = e; h.keyframe_insert("location", frame=f); h.keyframe_insert("rotation_euler", frame=f)
    h["rc_note"] = "on the drawn head until %d, pulled up by both hands %d-%d, then under the right arm" % (LIFT0, LIFT0, DOWN0)

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    n = racetrack.pit(sc); rig, box = race_car(); decals(box); cam, ck = camera(box); confetti(); cards(cam, ck)
    print("CROWD", n, "CAR box", [round(v, 2) for v in box[0]], [round(v, 2) for v in box[1]])
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    w, h = map(int, opt("--res", "270x480").split("x")); render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "12")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    if "--still" in A:
        for tok in A[A.index("--still") + 1:]:
            if tok.startswith("--"): break
            f, png = tok.split(":"); sc.frame_set(int(f)); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)

if __name__ == "__main__": main()
