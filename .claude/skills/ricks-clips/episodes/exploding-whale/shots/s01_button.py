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

HAND = (-.60, .97)                                                                       # the drawn hands of the pushing workers (card_anchors: local x, height)
PUSH = (("worker_a", -2.6, 4.6, 2.25, 40), ("worker_b", -3.6, 5.3, 2.9, 46))               # who, row y, crate x at frame 0, x at the end, last frame of the shove

def furrow(c, y, x0, x1, f1, name):
    """THE SAND GIVES WAY (CB 2026-11-20): two ridges of pushed sand along the crate's path, growing with it, and a mound that rides in front"""
    sand = bpy.data.materials["beach_sand"]; out = []
    for side in (-1, 1):
        cu = bpy.data.curves.new(name + "_ridge%d" % side, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = .05; cu.bevel_resolution = 3
        sp = cu.splines.new("POLY"); n = 24; sp.points.add(n - 1)
        for k, q in enumerate(sp.points):
            x = x0 + (x1 - x0) * k / (n - 1); yy = y + side * .36 + .02 * math.sin(k * 1.3 + side)
            q.co = (x, yy, beach.height(x, yy) + .01 + .012 * math.sin(k * 2.1), 1)
        o = bpy.data.objects.new(cu.name, cu); c.objects.link(o); cu.materials.append(sand); o.scale = (1, 1, .3); o.location.z = -.004   # a low flat ridge of pushed sand, not a tube
        for f, v in ((0, 0.0), (f1, 1.0)): cu.bevel_factor_end = v; cu.keyframe_insert("bevel_factor_end", frame=f)
        out.append(o)
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    for v in bm.verts: v.co *= 1 + .18 * math.sin(v.co.x * 5 + v.co.y * 3)
    m = beach.mesh_obj(name + "_mound", bm, sand, c, smooth=True); m.scale = (.24, .44, .09); out.append(m)
    return out

def crates():
    c = beach.col("L_OBJECTS"); R = random.Random(2); out = []
    for i in range(16):                                                                     # the wall already packed along the flank, two high (x -5.6 .. 1.3)
        k, lvl = i % 8, i // 8; o = props.crate("crate%02d" % i, c)
        x = -5.6 + k * .98 + R.uniform(-.04, .04); y = -2.6 + R.uniform(-.06, .06) - .1 * lvl
        o.location = (x, y, beach.height(x, y) - .03 + lvl * .5); o.rotation_euler = (0, 0, R.uniform(-.08, .08)); out.append(o)
    mov = []
    for j, (who, y, x0, x1, f1) in enumerate(PUSH):                                         # the last two STACKS are shoved along the flank, by hand, each in its own row
        o = props.crate("crate_push%d" % j, c); top = props.crate("crate_push%d_top" % j, c); top.parent = o; top.location = (.03, -.02, .5); top.rotation_euler = (0, 0, .06)
        fur = furrow(beach.col("L_SET"), y, x0 - .45, x1 - .45, f1, "furrow%d" % j)
        for f in range(F0, F1 + 1):
            t = min(1.0, f / f1); e = max(0, min(1, t - .10 * math.sin(t * math.pi * 3) * (1 - t)))   # shoved in surges
            x = x0 + (x1 - x0) * e; o.location = (x, y, beach.height(x, y) - .03); o.keyframe_insert("location", frame=f)
            fur[2].location = (x - .5, y, beach.height(x, y) + .02 + .03 * math.sin(e * 9)); fur[2].keyframe_insert("location", frame=f)
        mov.append((o, who, y))
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
    for o, n, y in mov:                                                                     # HANDS ON THE CRATE: the card stands so its drawn hands touch the stack's back face
        card = bpy.data.objects["Card_" + n]
        for f in range(F0, F1 + 1):
            sc.frame_set(f); x = o.location.x + .45 - HAND[0] + .02; card.location = (x, y - .05, beach.height(x, y)); card.keyframe_insert("location", frame=f)
    return e

def camera():
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); beach.col("CAM").objects.link(cam); bpy.context.scene.camera = cam
    cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24; cam.data.clip_end = 4000.0
    hz = beach.height(ENG.x, ENG.y)
    keys = [(0, (5.3, -9.8, 1.25), (4.9, -2.3, 1.05), 24), (40, (4.3, -7.2, 1.0), (3.6, -3.0, .95), 26),   # CLOSE: the men and the whale fill the frame (references: big subjects, centred)          # the whale, the wall of crates, two men shoving the last stacks
            (52, (6.2, -9.5, .75), (9.5, -12.0, .7), 24), (62, (9.5, -12.5, .8), (14.0, -18.5, 1.0), 24),          # whip round onto the wire, then ride it
            (84, (15.5, -20.5, 1.6), (21.0, -28.5, hz + 1.2), 26),
            (102, (19.0, -25.6, hz + 1.25), (ENG.x + .1, ENG.y, hz + 1.12), 30), (124, (19.3, -26.0, hz + 1.22), (ENG.x + .12, ENG.y, hz + 1.1), 31),
            (F1, (20.2, -27.9, hz + 1.05), (ENG.x - .33, ENG.y + .03, hz + .78), 45)]
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    street.handheld(cam, F0, F1, amp=.008, rot_deg=.18, seed=3)
    return cam

def build(sc):
    c, w, Mo = beach.build(sc, "grey", az=95, el=24, clear=((ENG.x, ENG.y - .6, 2.4),)); O = beach.col("L_OBJECTS")   # sun from the sea side: the whale and the faces are lit, the western sky keeps its clouds
    st, mov = crates(); cam = camera(); hz = beach.height(ENG.x, ENG.y)
    box, handle = props.plunger(O, (ENG.x + .23, ENG.y - .12, hz))   # under his drawn right hand (card anchors: x +0.23, 1.08 -> 0.91 m)
    for f, z in ((PRESS - 1, .63), (PRESS + 3, .45), (PRESS + 5, .47), (F1, .47)):            # down in 3 frames, a small rebound, stays down
        handle.location.z = z; handle.keyframe_insert("location", frame=f)
    wire = props.fuse_wire(O, [(1.6, -3.1), (4.5, -5.5), (8.0, -10.5), (12.0, -15.5), (17.0, -22.0), (ENG.x - .3, ENG.y + .1)], radius=.022)
    for f, v in ((44, 0.0), (100, 1.0)): wire.data.bevel_factor_end = v; wire.data.keyframe_insert("bevel_factor_end", frame=f)
    e = cards(cam, mov)
    sc.frame_set(PRESS); bpy.context.view_layer.update()                                    # the box goes IN FRONT of the card, under the drawn right hand
    box.location = e.matrix_world @ Vector((.25, -.22, 0)); box.rotation_euler = (0, 0, e.matrix_world.to_euler().z)
    vfx.apply(sc, [{"type": "dust_burst", "name": "crate_sand_%d" % k, "at": [x, y, .1], "frame": f, "count": 5, "radius": .5, "height": .3, "seed": 20 + k, "life": 22, "color": [.78, .7, .56]}
                   for k, (x, y, f) in enumerate(((5.2, -2.6, 6), (4.0, -2.6, 20), (6.2, -3.6, 12), (4.6, -3.6, 30), (2.25, -2.6, 40), (2.9, -3.6, 46)))])
    for o in list(bpy.data.objects):
        if o.name.startswith("crate_sand"):
            for uc in list(o.users_collection): uc.objects.unlink(o)
            beach.col("L_FX").objects.link(o)
    return cam, Mo

EXPO_KEYS = ((0, 0.0), (48, 0.0), (68, -.25), (90, -.17), (131, -.17))

def finish(sc, Mo, out):
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = Mo.get("contrast", "Medium Contrast"); sc.view_settings.exposure = Mo["exposure"]; 
    # CB 20/11: the dune part faces the bright side of the sky -> exposure follows the view (rule L3, light per view)
    for f, d in EXPO_KEYS:
        sc.view_settings.exposure = Mo["exposure"] + d; sc.view_settings.keyframe_insert("exposure", frame=f)
    lookdev.grade(sc, {"saturation": Mo["sat"]})
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
