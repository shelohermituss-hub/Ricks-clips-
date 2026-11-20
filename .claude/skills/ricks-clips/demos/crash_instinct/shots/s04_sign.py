"""crash_instinct shot 4 (9.4-12.07 s, frames 282-362): "somehow, somebody hits it every week."
NO CUT (references/crash_instinct/shots/s04.md, plan/s04.json PLAN PASS before the build): the same take as shots 1-3, so this script
builds shot 3's take up to frame 281 and adds:
  282-285  WHIP through the foliage onto the DAYS SINCE LAST CRASH sign. Inside the whip (frame 284, everything off-frame) a week passes:
           the white wreck, its wheel, its driver and the planter leave; the sign, an old tyre and (far up the road) a blue car come in
  285-309  the sign close ("7"), then a fast pull back across the road to the far verge: the whole tree
  309-315  a blue car comes fast along the verge from the right       315  IMPACT: front crushed, the rear lifts and drops back, dust,
           the oak shakes and loses leaves, the sign rocks, the front wheel breaks off and rolls to the sign
  330-348  push in to the sign; 339-343 the split-flap digit flips 7 -> 0; 349 the wheel falls flat on the old tyre (a stack of tyres)
  348-362  slow drift on the sign
    blender -b --factory-startup --python s04_sign.py -- <out.blend> [--res 270x480] [--samples 12] [--still f:out.png ...]"""
import bpy, math, os, random, sys
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s01_plant as S1, s02_crash as S2, s03_aerial as S3  # noqa: E402
from s01_plant import street, vfx, smooth  # noqa: E402
import sign as signkit  # noqa: E402  (sets/ is on the path through s01_plant)

F0, F1 = 282, 362; SWAP = 284; HIT = 315; FLIP = 339; FLAT = 349
SIGN_AT = (0.4, -3.0); TYRE_AT = Vector((1.25, -2.85, 0)); CAR_X = .35; CAR_STOP = .55 + S1.CAR_FRONT; SPEED = 1.3     # m per frame = 140 km/h (measured: 5 frames across 6.5 m)
A = S1.A
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s04_sign.blend"

def key_vis(o, visible_from=None, hidden_from=None):
    """a visibility change INSIDE the whip (SWAP: nothing of it is on screen on the frame before or after; continuity.py checks it)"""
    f = visible_from if visible_from is not None else hidden_from
    o.hide_render = o.hide_viewport = visible_from is not None; o.keyframe_insert("hide_render", frame=f - 1); o.keyframe_insert("hide_viewport", frame=f - 1)
    o.hide_render = o.hide_viewport = visible_from is None; o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)

def tree_and_children(o):
    out = [o]
    for ch in o.children: out += tree_and_children(ch)
    return out

def a_week_later():
    """the white wreck, its wheel, its driver and the planter are gone when the camera comes down from the foliage"""
    gone = tree_and_children(bpy.data.objects["car_rig"])
    for n in ("tire-low-fr_tire-low_0", "Card_driver", "Card_planter", "Contact_planter", "acorn", "seed"):
        if n in bpy.data.objects: gone.append(bpy.data.objects[n])
    for o in gone:
        if o.type in ("MESH", "EMPTY"): key_vis(o, hidden_from=SWAP)
    return len(gone)

def blue_car():
    """the same small SUV model (Sketchfab, MMC Works, CC-BY), its own copy with a bright clear-coated BLUE paint (the reference's car is blue)"""
    before_o = set(bpy.data.objects); before_m = set(bpy.data.materials)
    bpy.ops.import_scene.gltf(filepath=S1.CAR_GLTF); new = [o for o in bpy.data.objects if o not in before_o]
    c = street.col("L_OBJECTS"); rig = bpy.data.objects.new("blue_rig", None); c.objects.link(rig)
    body = bpy.data.objects.new("blue_body", None); c.objects.link(body); body.parent = rig; body.location = (0, 0, S1.CAR_LIFT)
    blue = None
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = body
        if o.type != "MESH": continue
        for sl in o.material_slots:
            m = sl.material
            if m and m.name.split(".")[0] == "body":
                if blue is None:
                    blue = m.copy(); blue.name = "body_blue"; b = blue.node_tree.nodes.get("Principled BSDF")
                    for inp in ("Base Color", "Metallic", "Roughness", "Normal"):
                        for l in list(b.inputs[inp].links): blue.node_tree.links.remove(l)
                    b.inputs["Base Color"].default_value = (*street.srgb("#2f5fd6"), 1); b.inputs["Metallic"].default_value = .3; b.inputs["Roughness"].default_value = .3
                    b.inputs["Coat Weight"].default_value = .6; b.inputs["Coat Roughness"].default_value = .06
                sl.material = blue
    for o in [rig, body] + new:
        if o.type in ("MESH", "EMPTY"): key_vis(o, visible_from=SWAP)
    # constant speed down the verge, braking over the last 3 frames, stopped by the trunk; then the rebound
    for f in range(S1.F0, F1 + 1, 1):
        if f <= HIT - 3: y = CAR_STOP + SPEED * (HIT - 3 - max(f, SWAP - 2)) + 2.6
        elif f <= HIT: y = CAR_STOP + (2.6, 1.3, .45, 0.0)[f - (HIT - 3)]
        else: t = f - HIT; y = CAR_STOP + .2 * (1 - math.exp(-t / 2.5))
        if f < SWAP - 2 and f % 40: continue
        rig.location = (CAR_X, y, 0); rig.keyframe_insert("location", frame=f)
    FA = 1.35                                                                                # front axle ahead of the rig origin: the rear lifts ABOUT it
    for f in range(HIT - 4, F1 + 1):
        t = f - HIT
        if t < -3: p = 0.0
        elif t < 0: p = 3.0 * (t + 3) / 3                                                     # nose dips under braking
        else: p = 3.0 * math.exp(-t / 2) + 23.0 * math.sin(min(math.pi, t * math.pi / 13)) * (1 if t <= 13 else 0) + (2.5 * math.exp(-(t - 13) / 3) * math.sin((t - 13) * 1.2) if t > 13 else 0)
        pr = math.radians(p); rig.rotation_euler = (pr, 0, 0); rig.delta_location = (0, -FA * (1 - math.cos(pr)), FA * math.sin(pr) * .92)
        rig.keyframe_insert("rotation_euler", frame=f); rig.keyframe_insert("delta_location", frame=f)
    return rig, body, new

def crush(rig, parts):
    from rc import physics
    sc = bpy.context.scene; sc.frame_set(HIT); bpy.context.view_layer.update(); n = 0
    front = rig.matrix_world @ Vector((0, -S1.CAR_FRONT, S1.CAR_LIFT - .1))
    for o in parts:
        if o.type != "MESH" or not o.data.materials or not o.data.materials[0].name.startswith(("body", "black-plastic", "headligth", "glass-headlight", "Headlight")): continue
        if min((o.matrix_world @ Vector(c) - front).length for c in o.bound_box) > 1.3: continue
        if o.data.users > 1: o.data = o.data.copy()
        r = physics.deform(sc, {"object": o.name, "name": "crash_dent", "point": list(front + Vector((0, -.1, 0))), "direction": [0, 1, -.2],
                                "radius": .9, "depth": .36, "at_frame": HIT, "ease": 3}, None, None)
        n += r["deformed_vertices"]
    return n

def wheel_off(parts):
    """the blue car's own front wheel (tyre + rim joined, origin moved to the wheel centre, PI-021): follows the car to the hit, then rolls
    along the shoulder to the sign, wobbles and falls flat ON the old tyre"""
    sc = bpy.context.scene
    w = next((o for o in parts if o.name.startswith("tire-low-fr_tire-low_0")), None); rim = next((o for o in parts if o.name.startswith("wheel-fr_wheels-brakes_0")), None)
    if w is None: return None
    if rim:
        for o in bpy.context.selected_objects: o.select_set(False)
        rim.hide_viewport = w.hide_viewport = False; rim.select_set(True); w.select_set(True); bpy.context.view_layer.objects.active = w; bpy.ops.object.join()
    c = sum((Vector(v) for v in w.bound_box), Vector()) / 8.0
    if w.data.users > 1: w.data = w.data.copy()
    w.data.transform(Matrix.Translation(-c)); C = Matrix.Translation(c); local = {}
    for f in [SWAP - 2, SWAP - 1] + list(range(SWAP, HIT + 1)):
        sc.frame_set(f); local[f] = (w.matrix_world @ C).copy()
    w.parent = None; w.animation_data_clear(); w.rotation_mode = "QUATERNION"
    def put(M, f):
        loc, rot, scl = M.decompose(); w.location = loc; w.rotation_quaternion = rot; w.scale = scl
        w.keyframe_insert("location", frame=f); w.keyframe_insert("rotation_quaternion", frame=f); w.keyframe_insert("scale", frame=f)
    for f, M in local.items(): put(M, f)
    key_vis(w, visible_from=SWAP)
    loc0, rot0, scl0 = local[HIT].decompose(); radius = .35; S = Matrix.Diagonal(scl0.to_4d())
    start = Vector((loc0.x, loc0.y, 0)); stop = TYRE_AT.copy(); d = (stop - start).normalized(); dist = (stop - start).length; yaw = math.atan2(d.y, d.x)
    top = bpy.data.objects["old_tyre"].get("top", .22)
    for f in range(HIT + 1, F1 + 1):
        t = min(1.0, (f - HIT) / (FLAT - 5 - HIT)); e = 1 - (1 - t) ** 2
        p = start + d * dist * e
        fall = (math.pi / 2) * min(1.0, max(0.0, (f - (FLAT - 6)) / 6.0)) ** 2
        wob = math.radians(9) * math.sin((f - HIT) * .9) * max(0.0, t - .55) * 2.2 if f <= FLAT - 6 else 0.0
        hop = .45 * math.sin(min(math.pi, (f - HIT) * math.pi / 9)) if f - HIT <= 9 else 0.0   # thrown up by the hit, lands and rolls
        R = Matrix.Rotation(fall + wob, 4, d) @ Matrix.Rotation(yaw + math.pi / 2, 4, "Z") @ Matrix.Rotation(-dist * e / radius, 4, "X")
        h = radius * math.cos(fall) + (top + .11) * math.sin(fall) + hop
        put(Matrix.Translation(p + Vector((0, 0, h))) @ R @ S, f)
    return w

def old_tyre():
    """a worn tyre lying in the grass at the foot of the sign (Poly Haven old_tyre, CC0): last week's crash. Laid flat whatever its file axis."""
    o = street.lib_instance("old_tyre", "old_tyre", street.col("L_OBJECTS"), tuple(TYRE_AT))
    pts = [ob.matrix_world @ Vector(c) for ob in o.instance_collection.all_objects if ob.type == "MESH" for c in ob.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))); sz = mx - mn
    ax = min(range(3), key=lambda i: sz[i]); cen = (mn + mx) / 2
    if ax == 0: o.rotation_euler = (0, math.radians(90), 0)
    elif ax == 1: o.rotation_euler = (math.radians(90), 0, 0)
    s = .72 / max(sz); o.scale = (s,) * 3; thick = sz[ax] * s
    bpy.context.view_layer.update(); off = o.matrix_world.to_3x3() @ cen
    o.location = (TYRE_AT.x - off.x, TYRE_AT.y - off.y, thick / 2 - off.z - .02); o["top"] = thick - .02
    key_vis(o, visible_from=SWAP)
    for f, sc_ in ((FLAT - 1, 1.0), (FLAT + 1, .9), (FLAT + 5, 1.0)):                          # it squashes a little under the wheel
        o.delta_scale = (1, 1, sc_) if ax == 2 else ((sc_, 1, 1) if ax == 0 else (1, sc_, 1)); o.keyframe_insert("delta_scale", frame=f)
    return o

def driver2(body, cam):
    """the blue car's driver: a copy of the drawn driver card on the blue car's seat, thrown forward at the hit (seat belt)"""
    src = bpy.data.objects.get("Card_driver")
    if src is None: return None
    card = src.copy(); card.name = "Card_driver_blue"; card.animation_data_clear(); street.col("L_OBJECTS").objects.link(card); sc = bpy.context.scene
    card.hide_render = card.hide_viewport = False
    for f in [SWAP - 2] + list(range(SWAP - 1, F1 + 1)):
        sc.frame_set(f); off = S1.DRIVER_SEAT.copy()
        if f >= HIT: t = f - HIT; off.y -= .22 * math.exp(-t / 3.0) * math.sin(min(math.pi, t * .7) + .01)
        card.location = body.matrix_world @ off; card.keyframe_insert("location", frame=f)
    key_vis(card, visible_from=SWAP)
    return card

def oak_shake():
    o = bpy.data.objects["oak"]
    for f in range(HIT - 1, F1 + 1):
        t = f - HIT; a = math.radians(1.8) * math.exp(-t / 8) * math.sin(t * .7) if t >= 0 else 0.0
        o.rotation_euler = (a, a * .5, .6); o.keyframe_insert("rotation_euler", frame=f)

def leaves_third():
    """leaves shaken loose by the blue car: they sit in the crown from the start (no visibility switch), fall after HIT, stay on the ground"""
    import bmesh
    c = street.col("L_FX"); m = bpy.data.materials["leaf_fall"]; R = random.Random(91)
    for k in range(36):
        bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((-.045, 0, 0), (0, .07, 0), (.045, 0, 0), (0, -.05, 0))]; bm.faces.new(vs)
        o = street.mesh_obj("leafC%d" % k, bm, m, c); o.visible_shadow = False
        a = R.uniform(0, 6.28); r = R.uniform(.8, 4.5); p0 = Vector((math.cos(a) * r, math.sin(a) * r, R.uniform(4.5, 8.5))); drop = R.uniform(.12, .2)
        sw, ph = R.uniform(.25, .6), R.uniform(0, 6.28); delay = R.randint(0, 6); t_land = (p0.z - .03) / drop
        o.location = p0; o.keyframe_insert("location", frame=S1.F0)
        for f in range(HIT - 1, F1 + 1):
            t = min(max(0, f - HIT - delay), t_land)
            o.location = p0 + Vector((sw * math.sin(t * .2 + ph) - sw * math.sin(ph), sw * .6 * (math.cos(t * .17 + ph) - math.cos(ph)), 0)); o.location.z = max(.03, p0.z - drop * t)
            o.rotation_euler = (t * .23 + ph, t * .31, t * .11) if t < t_land else (0, 0, ph)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)

def camera_sign(cam):
    sg = Vector((SIGN_AT[0], SIGN_AT[1], 1.95))
    keys = [(283, (4.2, -16.0, 1.6), (2.5, -7.0, 15.0), 24), (284, (4.5, -8.5, 1.65), (1.2, -3.0, 10.0), 30), (285, (4.6, -3.3, 1.6), tuple(sg), 35), (288, (5.0, -3.25, 1.58), tuple(sg), 35),
            (309, (15.5, -1.0, 1.0), (0.0, 0.5, 4.0), 22), (330, (15.2, -1.2, 1.05), (0.0, 0.45, 3.9), 22),
            (348, (6.6, -2.7, 1.35), (SIGN_AT[0], SIGN_AT[1] + .1, 1.55), 30), (F1, (6.3, -2.75, 1.38), (SIGN_AT[0], SIGN_AT[1] + .1, 1.55), 30)]
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    act = cam.animation_data.action
    for fc in (act.fcurves if hasattr(act, "fcurves") else []):
        for k in fc.keyframe_points:
            if 281 <= k.co[0] <= 285: k.interpolation = "LINEAR"                              # the whip is one straight fast move
    street.handheld(cam, F0, F1, amp=.01, rot_deg=.2, seed=6)
    R = random.Random(8)
    for f in range(HIT - 1, HIT + 12):
        k = max(0.0, 1 - (f - HIT) / 10) if f >= HIT else 0.0
        cam.data.shift_x = R.uniform(-1, 1) * .02 * k; cam.data.shift_y = R.uniform(-1, 1) * .02 * k
        cam.data.keyframe_insert("shift_x", frame=f); cam.data.keyframe_insert("shift_y", frame=f)

def build_take4(sc):
    S2.SMOKE_END = 236                                                                        # last puffs of the white wreck fade before the whip
    S1.F1 = S3.F1; rig, cam = S2.build_take2(sc); S3.camera_aerial(cam)                       # shots 1-3, unchanged, up to frame 281
    sc.frame_end = F1
    n = a_week_later()
    sg = signkit.build(street.col("L_OBJECTS"), SIGN_AT)
    for o in tree_and_children(sg): key_vis(o, visible_from=SWAP)
    signkit.shake(sg, HIT); signkit.flip(sg, FLIP)
    old_tyre(); brig, body, parts = blue_car(); nd = crush(brig, parts); driver2(body, cam); w = wheel_off(parts)
    oak_shake(); leaves_third(); camera_sign(cam)
    print("SHOT4 gone", n, "dent verts", nd, "wheel", w.name if w else None)
    vfx.apply(sc, [
        {"type": "dust_burst", "name": "blue_brake", "at": [CAR_X + .6, 3.6, .1], "frame": HIT - 3, "count": 8, "radius": 1.2, "height": .8, "seed": 41, "life": 30, "color": [.72, .64, .5]},
        {"type": "dust_burst", "name": "blue_hit", "at": [.4, .7, .3], "frame": HIT, "count": 18, "radius": 2.2, "height": 1.8, "seed": 42, "life": 45, "color": [.75, .7, .6]},
        {"type": "smoke", "name": "blue_smoke", "at": [CAR_X, .9, 1.0], "frames": [HIT + 4, F1], "every": 6, "per_burst": 2, "rise": 1.8, "size": .35, "density": .45,
         "color": [.88, .88, .88], "life": 50, "seed": 43, "drift": [0, -.3]},
        {"type": "dust_burst", "name": "wheel_stack", "at": [TYRE_AT.x, TYRE_AT.y, .15], "frame": FLAT, "count": 6, "radius": .5, "height": .3, "seed": 44, "life": 24, "color": [.6, .52, .4]}])
    S1.fx_to_layer(("blue_brake", "blue_hit", "blue_smoke", "wheel_stack"))
    return cam

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
    sc.frame_start, sc.frame_end = S1.F0, F1
    build_take4(sc)
    sc.frame_start = F0
    S1.finish(sc, OUT)

if __name__ == "__main__": main()
