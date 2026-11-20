"""exploding-whale shot 01 (0.0-4.37 s, frames 0-131): "They packed half a ton of dynamite under a dead whale, and the engineer pushed the
button." Plan: plan/plan.json shot 01 (PLAN PASS before the build). One take:
  0-45    two workers shove the last two DYNAMITE crates along the whale's flank toward us (the wall of crates is already there)
  45-100  the firing wire runs from the crates across the sand and up the dune; the camera rides along it, low and fast
  100-131 the engineer, proud; his finger rises, holds, and pushes the plunger down on the word "button" (118); 5-frame push on the plunger
    blender -b --factory-startup --python s01_button.py -- <out.blend> [--res 270x480] [--samples 16] [--still f:out.png ...]"""
import bpy, json, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.abspath(os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(EP, "sets"))
import beach, props
from rc import render, lookdev, characters, vfx
sys.path.insert(0, os.path.join(beach.SKILL, "demos", "crashed_car", "sets")); import street

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: A[A.index(k) + 1] if k in A else d
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s01_button.blend"
F0, F1 = 0, 131; PRESS = 117
ENG = Vector((22.0, -30.0, 0)); CARDS = os.path.join(EP, "build", "cards_s01")

def smooth(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)

def crates():
    c = beach.col("L_OBJECTS"); R = random.Random(2); out = []
    for i in range(18):                                                                     # the wall already packed along the flank, two high
        k, lvl = i % 9, i // 9; o = props.crate("crate%02d" % i, c)
        x = -4.2 + k * .98 + R.uniform(-.04, .04); y = -2.55 + R.uniform(-.06, .06) - .12 * lvl
        o.location = (x, y, beach.height(x, y) - .03 + lvl * .5); o.rotation_euler = (0, 0, R.uniform(-.08, .08)); out.append(o)
    mov = []
    for j, (y, x0, x1, f1) in enumerate(((-2.6, 2.6, 4.75, 38), (-3.55, 1.7, 4.3, 45))):   # the last two slide into place, pushed toward the camera
        o = props.crate("crate_push%d" % j, c)
        for f in range(F0, F1 + 1):
            t = min(1.0, f / f1); e = t - .12 * math.sin(t * math.pi * 3) * (1 - t)          # shoved in surges
            x = x0 + (x1 - x0) * max(0, min(1, e)); o.location = (x, y, beach.height(x, y) - .02); o.keyframe_insert("location", frame=f)
        mov.append((o, y, x0, x1, f1))
    return out, mov

def cards(cam, mov):
    sc = bpy.context.scene; who = ["engineer", "worker_a", "worker_b"]
    characters.place_cards(sc, CARDS, who, cam, .55, ground=None)
    for n in who:
        card = bpy.data.objects["Card_" + n]; disc = bpy.data.objects.get("Contact_" + n)
        for o in (card, disc):
            if o is None: continue
            for uc in list(o.users_collection): uc.objects.unlink(o)
            beach.col("L_OBJECTS").objects.link(o)
            for f in range(F0 - 1, 200):
                for dp in ("hide_render", "hide_viewport", "location"):
                    try: o.keyframe_delete(dp, frame=f)
                    except RuntimeError: pass
            o.hide_render = o.hide_viewport = False
        card["rc_anchors"] = os.path.join(CARDS, "cards", n, "anchors.json")
    e = bpy.data.objects["Card_engineer"]; e.location = (ENG.x, ENG.y, beach.height(ENG.x, ENG.y))
    for (o, y, x0, x1, f1), n in zip(mov, ("worker_a", "worker_b")):                         # each worker stays behind his crate
        card = bpy.data.objects["Card_" + n]
        for f in range(F0, F1 + 1):
            sc.frame_set(f); x = o.location.x - .78; card.location = (x, y, beach.height(x, y)); card.keyframe_insert("location", frame=f)
    return e

def camera():
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); beach.col("CAM").objects.link(cam); bpy.context.scene.camera = cam
    cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24; cam.data.clip_end = 4000.0
    hz = beach.height(ENG.x, ENG.y)
    keys = [(0, (10.4, -5.6, 1.0), (3.2, -1.7, 1.0), 22), (44, (9.4, -5.9, .85), (4.0, -2.4, .8), 23),            # macro glide on the crates being shoved in
            (62, (9.5, -9.0, .75), (14.0, -17.0, .9), 24), (84, (15.5, -20.5, 1.6), (21.0, -28.5, hz + 1.2), 26),   # rides along the wire, low and fast
            (102, (19.0, -25.6, hz + 1.25), (ENG.x + .1, ENG.y, hz + 1.12), 30), (124, (19.3, -26.0, hz + 1.22), (ENG.x + .12, ENG.y, hz + 1.1), 31),   # the plunger and his hand stay in frame
            (F1, (20.2, -27.9, hz + 1.05), (ENG.x - .33, ENG.y + .03, hz + .78), 45)]                                  # 5-frame push on the plunger
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    street.handheld(cam, F0, F1, amp=.008, rot_deg=.18, seed=3)
    return cam

def build(sc):
    c, w, Mo = beach.build(sc, "grey", az=35, el=24, clear=((ENG.x, ENG.y - .6, 2.4),)); O = beach.col("L_OBJECTS")   # sun from the sea side: the whale and the faces are lit, the western sky keeps its clouds
    st, mov = crates(); cam = camera(); hz = beach.height(ENG.x, ENG.y)
    box, handle = props.plunger(O, (ENG.x + .23, ENG.y - .12, hz))   # under his drawn right hand (card anchors: x +0.23, 1.08 -> 0.91 m)
    for f, z in ((PRESS - 1, .63), (PRESS + 3, .45), (PRESS + 5, .47), (F1, .47)):            # down in 3 frames, a small rebound, stays down
        handle.location.z = z; handle.keyframe_insert("location", frame=f)
    wire = props.fuse_wire(O, [(4.9, -3.2), (7.5, -7.0), (12.0, -14.5), (17.0, -22.0), (ENG.x + .3, ENG.y - .1)])
    for f, v in ((44, 0.0), (100, 1.0)): wire.data.bevel_factor_end = v; wire.data.keyframe_insert("bevel_factor_end", frame=f)
    e = cards(cam, mov)
    sc.frame_set(PRESS); bpy.context.view_layer.update()                                    # the box goes IN FRONT of the card, under the drawn right hand
    box.location = e.matrix_world @ Vector((.25, -.22, 0)); box.rotation_euler = (0, 0, e.matrix_world.to_euler().z)
    vfx.apply(sc, [{"type": "dust_burst", "name": "crate_sand_%d" % k, "at": [x, y, .1], "frame": f, "count": 5, "radius": .5, "height": .3, "seed": 20 + k, "life": 22, "color": [.78, .7, .56]}
                   for k, (x, y, f) in enumerate(((3.2, -2.6, 6), (4.0, -2.6, 20), (2.6, -3.55, 12), (3.6, -3.55, 30), (4.75, -2.6, 38), (4.3, -3.55, 45)))])
    for o in list(bpy.data.objects):
        if o.name.startswith("crate_sand"):
            for uc in list(o.users_collection): uc.objects.unlink(o)
            beach.col("L_FX").objects.link(o)
    return cam, Mo

def finish(sc, Mo, out):
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium Contrast"; sc.view_settings.exposure = Mo["exposure"]; lookdev.grade(sc, {"saturation": Mo["sat"]})
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .3
    w, h = map(int, opt("--res", "270x480").split("x")); render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "16")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    if "--still" in A:
        for tok in A[A.index("--still") + 1:]:
            if tok.startswith("--"): break
            f, png = tok.split(":"); sc.frame_set(int(f)); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    cam, Mo = build(sc); finish(sc, Mo, OUT)

if __name__ == "__main__": main()
