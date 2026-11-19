"""Shot 2, part 2C (frames 200-248): the corner after the crash (references/crashed_car/shots/s02.md §3). The red car hangs UPSIDE DOWN in the
air behind him, turning very slowly (frozen dramatic instant), debris and gravel in the air; he is shocked (200-221), then raises his hand
to vow (222-248). Low camera, very slow push-in + slight tilt down. Layers: L_SKY / L_SET / L_OBJECTS / L_FX.
    blender -b --factory-startup --python s02_corner.py -- <out.blend> [--still f:out.png ...] [--res 270x480] [--samples 12]"""
import bpy, math, os, sys, random, bmesh
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s02_pit as P  # noqa: E402  (race_car, street, racetrack, characters, render)
A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: A[A.index(k) + 1] if k in A else d
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s02_corner.blend"
F0, F1 = 199, 248

def flipped(rig, box):
    """upside down, nose down 22 deg, above the gravel trap behind him; turns 6 deg and drifts 0.3 m over the whole part"""
    for f, rx, ry, rz, loc in ((F0, 180, 22, 25, (-0.5, 3.8, 2.45)), (F1, 186, 26, 31, (-0.25, 3.7, 2.3))):
        rig.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz)); rig.location = loc
        rig.keyframe_insert("rotation_euler", frame=f); rig.keyframe_insert("location", frame=f)
    R = random.Random(4); fx = P.street.col("L_FX"); red = P.street.mat("debris_red", "#c9141c", .45); grey = P.street.mat("stone_beige", "#a89474", .9)
    for k in range(26):                                                # pieces and gravel hanging around the car, slow drift
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=R.uniform(.03, .09)); o = P.street.mesh_obj("airbit", bm, red if k % 3 == 0 else grey, fx, smooth=k % 3 != 0)
        p0 = Vector((-1.4 + R.uniform(-2.2, 2.2), 3.0 + R.uniform(-1.2, 1.0), R.uniform(.3, 3.2))); d = Vector((R.uniform(-.2, .2), R.uniform(-.1, .1), R.uniform(-.35, -.05)))
        for f, pp in ((F0, p0), (F1, p0 + d)): o.location = pp; o.rotation_euler = (f * .05 * k, f * .03, 0); o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)

def camera():
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); P.street.col("CAM").objects.link(cam); bpy.context.scene.camera = cam; cam.data.sensor_fit = "VERTICAL"
    for f, p, a, fov in ((F0, (0.5, -6.6, 2.3), (-0.4, 2.0, 1.2), 54), (F1, (0.45, -5.9, 2.15), (-0.35, 2.0, 1.05), 52)):
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    return cam

def hero(cam):
    cd = os.path.join(HERE, "..", "build", "cards_s02")
    P.characters.place_cards(bpy.context.scene, cd, ["old"], cam, .55, ground=bpy.data.objects.get("track"))
    setc = P.street.col("L_SET")
    for o in [o for o in bpy.data.objects if o.name.lower() in ("card_old", "contact_old")]:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        setc.objects.link(o)
        for f in range(F0 - 1, F1 + 2):
            for dp in ("hide_render", "hide_viewport", "location"):
                try: o.keyframe_delete(dp, frame=f)
                except RuntimeError: pass
    c = bpy.data.objects["Card_old"]; c.hide_render = c.hide_viewport = False; c.location = (0.1, -0.6, 0); c.keyframe_insert("location", frame=F0)
    h = P.helmet3d(); h.scale = (1.55,) * 3; h.location = (0.42, -0.75, .9)                 # the helmet still under his arm

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    P.racetrack.corner(sc); rig, box = P.race_car(); flipped(rig, box); cam = camera(); hero(cam)
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    w, h = map(int, opt("--res", "270x480").split("x")); P.render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "12")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    if "--still" in A:
        for tok in A[A.index("--still") + 1:]:
            if tok.startswith("--"): break
            f, png = tok.split(":"); sc.frame_set(int(f)); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)

main()
