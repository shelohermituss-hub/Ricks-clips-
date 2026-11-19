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
            b.inputs["Base Color"].default_value = (*street.srgb("#1d4fd1"), 1); b.inputs["Roughness"].default_value = .42; b.inputs["Metallic"].default_value = 0.0
            b.inputs["Coat Weight"].default_value = .25; b.inputs["Coat Roughness"].default_value = .18
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
    wood = street.mat("stave_wood", "#7a5532", .8, bump=("noise", 30, .35)); hoop = street.mat("hoop_iron", "#3a3634", .45, .6)
    broken = []
    for b in [o for o in out if o.name in ("barrel0", "barrel1", "barrel2", "barrel3")]: broken += staves(b, c, R, wood, hoop)
    out = [o for o in out if o.name not in ("barrel0", "barrel1", "barrel2", "barrel3")] + broken
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

def car_impact(rig):
    """the car takes the hit: nose dive and rebound (pitch + suspension), dented front (shape key on the front body panels)"""
    from rc import physics
    for f, rx, dz in ((IMPACT - 1, 0, 0), (IMPACT + 2, 4.5, -.05), (IMPACT + 7, -1.8, .035), (IMPACT + 13, .7, -.01), (IMPACT + 19, 0, 0)):
        rig.rotation_euler = (math.radians(rx), 0, math.pi); rig.keyframe_insert("rotation_euler", frame=f)
        rig.delta_location = (0, 0, dz); rig.keyframe_insert("delta_location", frame=f)
    sc = bpy.context.scene; sc.frame_set(IMPACT + 20); bpy.context.view_layer.update(); n = 0
    front = max((o.matrix_world @ Vector(c)).y for o in bpy.data.collections["CAR"].all_objects if o.type == "MESH" for c in o.bound_box)
    for o in bpy.data.collections["CAR"].all_objects:
        if o.type != "MESH" or not o.data.materials or "Paint" not in o.data.materials[0].name and "Plastic" not in o.data.materials[0].name: continue
        if max((o.matrix_world @ Vector(c)).y for c in o.bound_box) < front - .4: continue
        r = physics.deform(sc, {"object": o.name, "name": "crash_dent", "point": [0, front + .05, .62], "direction": [0, -1, -.25], "radius": .75, "depth": .16, "at_frame": IMPACT, "ease": 3}, None, None)
        n += r["deformed_vertices"]
    return front, n

def staves(barrel, c, R, mat_wood, mat_hoop):
    """a barrel that bursts: 10 staves + 2 hoops thrown out from its centre at the impact (the intact barrel is hidden from then on)"""
    import bmesh
    p0 = barrel.location.copy(); out = []
    for k in range(10):
        a = 2 * math.pi * k / 10; bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(.15, .035, .82), verts=bm.verts)
        o = street.mesh_obj("%s_stave%d" % (barrel.name, k), bm, mat_wood, c, bevel=.008); o.location = p0 + Vector((math.cos(a) * .27, math.sin(a) * .27, .42)); o.rotation_euler = (0, 0, a + math.pi / 2)
        out.append(o)
    for k in range(2):
        bpy.ops.mesh.primitive_torus_add(major_radius=.3, minor_radius=.015, location=p0 + Vector((0, 0, .2 + k * .45))); t = bpy.context.object; t.name = "%s_hoop%d" % (barrel.name, k)
        for uc in list(t.users_collection): uc.objects.unlink(t)
        c.objects.link(t); t.data.materials.append(mat_hoop); out.append(t)
    for o in out:
        o.hide_render = True; o.keyframe_insert("hide_render", frame=IMPACT - 1); o.hide_render = False; o.keyframe_insert("hide_render", frame=IMPACT)
    barrel.hide_render = False; barrel.keyframe_insert("hide_render", frame=IMPACT - 1); barrel.hide_render = True; barrel.keyframe_insert("hide_render", frame=IMPACT)
    return out

def shake(cam, f0, n=12, amp=.035):
    R = random.Random(2)
    for f in range(f0 - 1, f0 + n + 2):
        k = max(0.0, 1 - (f - f0) / n) if f >= f0 else 0.0; cam.data.shift_x = R.uniform(-1, 1) * amp * k; cam.data.shift_y = R.uniform(-1, 1) * amp * k
        cam.data.keyframe_insert("shift_x", frame=f); cam.data.keyframe_insert("shift_y", frame=f)

def glass_clear():
    for m in bpy.data.materials:
        if m.name.startswith("Glass") and m.use_nodes and m.node_tree.nodes.get("Principled BSDF"):
            b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["Roughness"].default_value = .02; b.inputs["IOR"].default_value = 1.2
            if "tinted" in m.name: b.inputs["Base Color"].default_value = (.55, .62, .7, 1)

def camera(scene):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); street.col("CAM").objects.link(cam); scene.camera = cam
    cam.data.lens_unit = "FOV"; cam.data.sensor_fit = "VERTICAL"
    keys = [(0, (-7.0, -31.0, 5.0), (4.0, -7.0, 0.0), 64), (22, (-5.0, -12.0, 1.6), (0.0, 0.0, 0.8), 46), (32, (-11.0, -0.8, 1.1), (1.0, 2.2, 0.75), 40),
            (58, (-10.4, 0.0, 1.15), (0.8, 2.6, 0.8), 40), (88, (-5.0, -2.2, 1.1), (-0.6, 0.9, 1.0), 48), (121, (-4.9, -1.2, 1.3), (-1.6, 0.85, 1.05), 42)]
    for f, p, a, fov in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    return cam

def drive(rig, box):
    """car up the driveway (+Y) into the barrels, stops dead at the impact (pure keys; no simulation needed for the car)"""
    length = box[1].y - box[0].y; y_stop = 3.4 - length / 2 - .1
    for f, y in ((0, -22.0), (IMPACT, y_stop), (IMPACT + 5, y_stop + .25), (F1, y_stop + .25)):
        rig.location = (0, y, 0); rig.keyframe_insert("location", frame=f)
    for fc in rig.animation_data.action.fcurves if rig.animation_data and getattr(rig.animation_data.action, "fcurves", None) else []:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    street.build(sc, "day", lane=True); rig, box = car(sc); drive(rig, box); objs = barrels(sc); crash(objs, 0); cam = camera(sc); print("DOOR parts", open_door(rig)); front, nd = car_impact(rig); print("DENT verts", nd)
    shake(cam, IMPACT); glass_clear()
    sacks = [o for o in objs if o.name.startswith("sack")]
    fx = [{"type": "smoke", "name": "hood_steam", "at": [0, front - .7, 1.05], "frames": [IMPACT + 4, F1], "every": 7, "per_burst": 2, "rise": 1.6, "size": .32, "density": .5,
           "color": [.86, .86, .86], "life": 55, "seed": 12, "drift": [0.4, 0]}]
    fx += [{"type": "dust_burst", "name": "sack_dust%d" % k, "at": [o.location.x, o.location.y, .2], "frame": IMPACT + 2, "count": 7, "radius": 1.0, "height": .9, "seed": 20 + k, "life": 40, "color": [.82, .72, .52]} for k, o in enumerate(sacks)]
    vfx.apply(sc, fx)
    cards = os.path.join(HERE, "..", "build", "cards_s01")
    if os.path.isdir(os.path.join(cards, "cards")):                 # the hero card: SEATED in the car while it drives (seen through the glass),
        characters.place_cards(sc, cards, ["hero"], cam, .55, ground=bpy.data.objects.get("ground"))   # then he climbs out through the open door
        card = bpy.data.objects["Card_hero"]
        for f in range(F0, F1 + 1):
            for dp in ("hide_render", "hide_viewport", "location"):
                try: card.keyframe_delete(dp, frame=f)
                except RuntimeError: pass
        card.hide_render = card.hide_viewport = False
        for f in range(F0, F1 + 1):
            sc.frame_set(f); ry = rig.matrix_world.translation.y; seat = Vector((-.42, ry + .2, -.47))
            if f <= 88: p = seat
            elif f <= 102: k = (f - 88) / 14; k = k * k * (3 - 2 * k); p = seat.lerp(Vector((-1.55, ry + .3, 0.0)), k)       # stands up and steps out
            else: k = min(1.0, (f - 102) / 12); k = k * k * (3 - 2 * k); p = Vector((-1.55, ry + .3, 0)).lerp(Vector((-1.8, ry - .25, 0)), k)
            card.location = p; card.keyframe_insert("location", frame=f)
    sc.render.film_transparent = False; sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    w, h = map(int, opt("--res", "270x480").split("x")); info = render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "16")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    if "--still" in A:
        f = int(opt("--still", "0")); png = A[A.index("--still") + 2]; sc.frame_set(f); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)

main()
