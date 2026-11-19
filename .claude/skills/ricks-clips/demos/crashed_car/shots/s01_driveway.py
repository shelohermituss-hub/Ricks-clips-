"""Shot 1 (0.0-4.07 s, frames 0-121): "He crashed his car right into his own invention, on purpose!"
Wide high view over the lawn, the blue sedan rolls up the driveway, camera cranes down to grass level, the car smashes the wooden barrels
(sacks and staves fly, dust), stops; he gets out (2D card, added by the character pass).
    blender -b --factory-startup --python s01_driveway.py -- <out.blend> [--frames a-b] [--still f out.png] [--res 270x480] [--samples 16]"""
import bpy, math, os, sys, random
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "sets")); sys.path.insert(0, os.path.join(SKILL, "blender"))
import street  # noqa: E402
from rc import library, bl_library, render, vfx, lookdev, characters  # noqa: E402

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: A[A.index(k) + 1] if k in A else d
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s01.blend"
F0, F1 = 0, 121; IMPACT = 42                                       # crash at 1.4 s (narration "right into", measured on the reference)
CAR_GLTF = os.path.join(SKILL, "library", "assets", "sketchfab", "58c33766470d46e7b2aed542650494e5", "gltf", "scene.gltf")

def car(scene):
    """the blue sedan (Sketchfab 'Generic Sedan Car', MMC Works, CC-BY): imported once, paint set to the reference blue, parented to an empty"""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=CAR_GLTF); new = [o for o in bpy.data.objects if o not in before]
    c = street.col("CAR"); rig = bpy.data.objects.new("car_rig", None); c.objects.link(rig)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = rig
    paint = bpy.data.materials.get("Car_Paint_-_All_Colors")
    if paint and paint.use_nodes:
        b = paint.node_tree.nodes.get("Principled BSDF")
        if b:
            for l in list(b.inputs["Base Color"].links): paint.node_tree.links.remove(l)
            b.inputs["Base Color"].default_value = (*street.srgb("#1d4fd1"), 1); b.inputs["Roughness"].default_value = .3; b.inputs["Metallic"].default_value = .15
            b.inputs["Coat Weight"].default_value = .35; b.inputs["Coat Roughness"].default_value = .1
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(cn) for o in new if o.type == "MESH" for cn in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    rig.rotation_euler = (0, 0, math.pi)                            # the model faces -Y: turned round so it drives +Y (towards the garage)
    return rig, (lo, hi)

def barrels(scene):
    """wooden barrels + burlap sacks stacked in front of the garage door (the first prototype)"""
    blend, _ = library.resolve("wine_barrel_01", log=lambda *a: None); holder = bpy.data.collections.new("lib"); src = bl_library.link_asset(blend, "wine_barrel_01", holder)
    c = street.col("BARRELS"); out = []; R = random.Random(3)
    spots = [(-1.6, 3.4), (-.6, 3.5), (.4, 3.4), (1.4, 3.5), (-1.1, 4.3), (.0, 4.35), (1.0, 4.3), (-.5, 3.9), (.6, 3.9)]
    for k, (x, y) in enumerate(spots):
        inst = bpy.data.objects.new("barrel%d" % k, None); inst.instance_type = "COLLECTION"; inst.instance_collection = src; c.objects.link(inst)
        inst.location = (x, y, 0 if k < 7 else .95); inst.rotation_euler = (0, 0, R.uniform(0, 6.28)); inst.scale = (1, 1, 1); out.append(inst)
    sack = street.mat("burlap", "#c9a46a", .95, bump=("noise", 40, .4))
    for k in range(6):
        import bmesh
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=.38)
        for v in bm.verts: v.co.z *= .62; v.co.x *= 1.15
        o = street.mesh_obj("sack%d" % k, bm, sack, c, smooth=True); o.location = (R.uniform(-1.8, 1.8), R.uniform(3.2, 4.4), 1.1 + R.uniform(0, .5)); out.append(o)
    return out

def crash(objs, car_front_y):
    """the barrels and sacks fly from the impact (keyed ballistic arcs, spin, one bounce, then rest): deterministic, frame-only"""
    R = random.Random(9); g = 9.81 / 900.0                                   # per frame^2 at 30 fps
    for o in objs:                                                           # rest height: barrel origin at its base, sack origin at its centre
        p0 = o.location.copy(); r0 = o.rotation_euler.copy(); d = Vector((p0.x * .9 + R.uniform(-.4, .4), 1.0, 0)).normalized()
        v = d * R.uniform(.10, .20) + Vector((0, 0, R.uniform(.10, .22))); w = Vector((R.uniform(-.25, .25), R.uniform(-.25, .25), R.uniform(-.15, .15)))
        p = p0.copy(); vel = v.copy(); rest = 0.0 if o.name.startswith("barrel") else .24; rot = r0.copy()
        o.keyframe_insert("location", frame=IMPACT - 1); o.keyframe_insert("rotation_euler", frame=IMPACT - 1)
        for f in range(IMPACT, F1 + 1):
            vel.z -= g; p += vel
            if p.z < rest and vel.z < 0: p.z = rest; vel.z *= -.3; vel.x *= .6; vel.y *= .6; w *= .5
            rot.x += w.x; rot.y += w.y; rot.z += w.z; o.location = p; o.rotation_euler = rot
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)

def open_door(rig, f0=80, f1=94, angle=-68):
    """driver door (front left after the 180 turn): every car part inside the door volume swings on a hinge at its front edge"""
    bpy.context.scene.frame_set(F1); bpy.context.view_layer.update(); parts = []
    for o in bpy.data.collections["CAR"].all_objects:
        if o.type != "MESH": continue
        P = [o.matrix_world @ Vector(c) for c in o.bound_box]; lo = Vector([min(p[i] for p in P) for i in range(3)]); hi = Vector([max(p[i] for p in P) for i in range(3)])
        if hi.x < -.55 and lo.y > rig.location.y - .3 and hi.y < rig.location.y + 1.3 and lo.z > .2 and (hi.y - lo.y) > .15: parts.append((o, lo, hi))
    if not parts: return 0
    hy = max(h.y for _, _, h in parts); hx = min(l.x for _, l, _ in parts)
    hinge = bpy.data.objects.new("door_hinge", None); street.col("CAR").objects.link(hinge); hinge.location = (hx + .05, hy - .05, .7)
    bpy.context.view_layer.update()                                    # the hinge matrix must exist before children are attached (door was displaced)
    hinge.parent = rig; hinge.matrix_parent_inverse = rig.matrix_world.inverted(); bpy.context.view_layer.update()
    for o, _, _ in parts:
        mw = o.matrix_world.copy(); o.parent = hinge; o.matrix_parent_inverse = hinge.matrix_world.inverted() @ mw @ o.matrix_basis.inverted()
    for f, a in ((f0, 0.0), (f1, angle)): hinge.rotation_euler = (0, 0, math.radians(a)); hinge.keyframe_insert("rotation_euler", frame=f)
    return len(parts)

def camera(scene):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); street.col("CAM").objects.link(cam); scene.camera = cam
    cam.data.lens_unit = "FOV"; cam.data.sensor_fit = "VERTICAL"
    keys = [(0, (2.5, -30.0, 3.4), (-4.0, 5.0, 0.8), 40), (22, (-5.0, -12.0, 1.6), (0.0, 0.0, 0.8), 46), (32, (-11.0, -1.5, 1.1), (1.0, 1.0, 0.75), 40),
            (58, (-10.4, -0.6, 1.15), (0.8, 1.8, 0.8), 40), (88, (-5.6, -3.0, 1.35), (0.4, 0.9, 1.0), 46), (121, (-4.2, -2.8, 1.45), (0.2, 0.9, 1.15), 42)]
    for f, p, a, fov in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    return cam

def drive(rig, box):
    """car up the driveway (+Y) into the barrels, stops dead at the impact (pure keys; no simulation needed for the car)"""
    length = box[1].y - box[0].y; y_stop = 3.4 - length / 2 - .1
    for f, y in ((0, -11.0), (IMPACT, y_stop), (IMPACT + 5, y_stop + .25), (F1, y_stop + .25)):
        rig.location = (0, y, 0); rig.keyframe_insert("location", frame=f)
    for fc in rig.animation_data.action.fcurves if rig.animation_data and getattr(rig.animation_data.action, "fcurves", None) else []:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    street.build(sc, "day", lane=True); rig, box = car(sc); drive(rig, box); objs = barrels(sc); crash(objs, 0); cam = camera(sc); print("DOOR parts", open_door(rig))
    cards = os.path.join(HERE, "..", "build", "cards_s01")
    if os.path.isdir(os.path.join(cards, "cards")):                 # the hero card (2D drawings from tracks_s01.json), out of the car from f86
        placed = characters.place_cards(sc, cards, ["hero"], cam, .55, ground=bpy.data.objects.get("ground"))
        for o in [o for o in bpy.data.objects if o.name.lower() in ("card_hero", "contact_hero")]:
            for f in range(F0, F1 + 1):                             # the card loader keys its own visibility: replace it
                for dp in ("hide_render", "hide_viewport"):
                    try: o.keyframe_delete(dp, frame=f)
                    except RuntimeError: pass
            for f, h in ((0, True), (85, True), (86, False)): o.hide_render = h; o.hide_viewport = h; o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
    vfx.apply(sc, [{"type": "dust_burst", "name": "crash_dust", "at": [0, 3.2, 0], "frame": IMPACT, "count": 16, "radius": 2.2, "height": 1.2, "seed": 4, "life": 50, "color": [.78, .7, .56]}])
    lookdev.apply({"island_tree_02_leaves": {"tint": "#3d8a24", "amount": .7, "mean": .2}})   # saturated cartoon greens
    sc.render.film_transparent = False; sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    w, h = map(int, opt("--res", "270x480").split("x")); info = render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "16")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    if "--still" in A:
        f = int(opt("--still", "0")); png = A[A.index("--still") + 2]; sc.frame_set(f); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)

main()
