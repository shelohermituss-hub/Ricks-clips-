"""crash_instinct shot 2 (3.2-5.0 s, frames 96-149, + the crane to the aerial 150-176): "...it. You see, the road runs"
NO CUT with shot 1 (references/crash_instinct/shots/s02.md): the same take, so this script builds shot 1's take (s01_plant.build_take)
up to frame 176 and adds on top:
  96-106  the white car brakes across the shoulder into the trunk          106  IMPACT: front crushed (shape key), rebound, dust,
          the oak shakes and loses leaves, smoke from the wreck            106  the front-left wheel breaks off where it is, rolls to the
          planter, wobbles and falls flat at his feet (134)                136-145 he stands up (the sit move played backwards, card rises)
  camera: drift (96-101), fast swoop down to grass level (102-120), drift (120-149), crane up to the aerial (150-176)
    blender -b --factory-startup --python s02_crash.py -- <out.blend> [--res 270x480] [--samples 12] [--still f:out.png ...]"""
import bpy, math, os, random, sys
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s01_plant as S1  # noqa: E402
from s01_plant import street, vfx, smooth  # noqa: E402

F0, F1 = 96, 176; HIT = 106; FLAT = 134; UP0, UP1 = 136, 145
A, opt = S1.A, S1.opt
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s02_crash.blend"

def car_crash(rig):
    """brake across the shoulder into the trunk (front stops 0.7 m from the trunk axis), crush + rebound, then it stays"""
    head = Vector((-.375, -.927, 0)); p95 = Vector((1.9, 4.6, 0)); hit = p95 + head * (4.98 - S1.CAR_FRONT - .6)   # nose stops at the bark
    keys = [(99, p95 + head * (hit - p95).length * .48), (103, p95 + head * (hit - p95).length * .83), (HIT, hit), (HIT + 3, hit + head * .22), (HIT + 8, hit + head * .1), (F1, hit + head * .1)]
    for f, p in keys:
        rig.location = p; rig.keyframe_insert("location", frame=f)
    for f, pitch in ((HIT - 1, 0), (HIT + 2, 5.0), (HIT + 6, -2.0), (HIT + 11, .6), (HIT + 16, 0), (F1, 0)):   # nose dive and rebound
        rig.rotation_euler = (math.radians(pitch), math.radians(1.2 if f < HIT else 0), math.radians(-22)); rig.keyframe_insert("rotation_euler", frame=f)
    from rc import physics
    sc = bpy.context.scene; sc.frame_set(HIT + 10); bpy.context.view_layer.update(); n = 0
    body = [o for o in bpy.data.collections["L_OBJECTS"].all_objects if o.type == "MESH" and o.data.materials and o.data.materials[0].name.startswith(("body", "black-plastic", "headligth", "glass-headlight", "Headlight"))]
    front_w = rig.matrix_world @ Vector((0, -S1.CAR_FRONT, S1.CAR_LIFT - .1))
    for o in body:
        if min((o.matrix_world @ Vector(c) - front_w).length for c in o.bound_box) > 1.3: continue
        r = physics.deform(sc, {"object": o.name, "name": "crash_dent", "point": list(front_w + head * .1), "direction": list(-head + Vector((0, 0, -.2))),
                                "radius": .8, "depth": .28, "at_frame": HIT, "ease": 3}, None, None)
        n += r["deformed_vertices"]
    return hit, n

def wheel_off(rig):
    """the REAL front wheel of the SUV (tyre tire-low-fr + rim wheel-fr, joined) follows the car until the hit, then rolls on its own,
    wobbles and tips over flat. Its mesh origin is moved to the wheel centre first (the glTF puts it at the car origin)."""
    w = bpy.data.objects.get("tire-low-fr_tire-low_0"); rim = bpy.data.objects.get("wheel-fr_wheels-brakes_0")
    if w is None: return None
    sc = bpy.context.scene
    if rim:                                                                                     # tyre + rim are one wheel: join them
        for o in bpy.context.selected_objects: o.select_set(False)
        rim.select_set(True); w.select_set(True); bpy.context.view_layer.objects.active = w; bpy.ops.object.join()
    c = sum((Vector(v) for v in w.bound_box), Vector()) / 8.0                                   # wheel centre in the object's own space
    if w.data.users > 1: w.data = w.data.copy()
    w.data.transform(Matrix.Translation(-c)); C = Matrix.Translation(c)
    local = []
    for f in range(S1.F0, HIT + 1):
        sc.frame_set(f); local.append(w.matrix_world @ C)                                       # world matrix of the wheel CENTRE
    w.parent = None; w.animation_data_clear(); w.rotation_mode = "QUATERNION"
    def put(M, f):
        loc, rot, scl = M.decompose(); w.location = loc; w.rotation_quaternion = rot; w.scale = scl
        w.keyframe_insert("location", frame=f); w.keyframe_insert("rotation_quaternion", frame=f); w.keyframe_insert("scale", frame=f)
    for f, M in zip(range(S1.F0, HIT + 1), local): put(M, f)
    loc0, rot0, scl0 = local[-1].decompose(); radius = .35
    stop = Vector((-1.25, -1.55, 0)); start = Vector((loc0.x, loc0.y, 0)); d = (stop - start).normalized(); dist = (stop - start).length
    yaw = math.atan2(d.y, d.x); S = Matrix.Diagonal(scl0.to_4d())
    for f in range(HIT + 1, F1 + 1):
        t = min(1.0, (f - HIT) / (FLAT - 4 - HIT)); e = 1 - (1 - t) ** 2                       # thrown out, slows down as it rolls
        p = start + d * dist * e
        fall = (math.pi / 2) * min(1.0, max(0.0, (f - (FLAT - 6)) / 6.0)) ** 2                  # tips over flat at the end
        wob = math.radians(9) * math.sin((f - HIT) * .9) * max(0.0, t - .55) * 2.2 if f <= FLAT - 6 else 0.0
        R = Matrix.Rotation(fall + wob, 4, d) @ Matrix.Rotation(yaw + math.pi / 2, 4, "Z") @ Matrix.Rotation(-dist * e / radius, 4, "X")   # spin about the axle, then tip about the path
        h = radius * math.cos(fall) + .11 * math.sin(fall)
        put(Matrix.Translation(p + Vector((0, 0, h))) @ R @ S, f)
    return w

def oak_shake():
    o = bpy.data.objects["oak"]
    for f in range(HIT, F1 + 1):
        t = f - HIT; a = math.radians(1.6) * math.exp(-t / 8) * math.sin(t * .7)
        o.rotation_euler = (a * .5, -a, .6); o.keyframe_insert("rotation_euler", frame=f)

def leaves_again():
    """second leaf fall: these leaves sit IN the crown from frame 0 (no visibility switch) and are shaken loose by the car hitting the trunk"""
    import bmesh
    c = street.col("L_FX"); m = bpy.data.materials["leaf_fall"]; R = random.Random(77)
    for k in range(40):
        bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((-.045, 0, 0), (0, .07, 0), (.045, 0, 0), (0, -.05, 0))]; bm.faces.new(vs)
        o = street.mesh_obj("leafB%d" % k, bm, m, c); o.visible_shadow = False
        a = R.uniform(0, 6.28); r = R.uniform(.8, 4.5); p0 = Vector((math.cos(a) * r, math.sin(a) * r, R.uniform(4.5, 8.5))); drop = R.uniform(.05, .085)
        sw, ph = R.uniform(.25, .6), R.uniform(0, 6.28); delay = R.randint(0, 6); t_land = (p0.z - .03) / drop
        for f in range(S1.F0, F1 + 1):
            t = min(max(0, f - HIT - delay), t_land)
            o.location = p0 + Vector((sw * math.sin(t * .2 + ph), sw * .6 * math.cos(t * .17 + ph), 0)); o.location.z = max(.03, p0.z - drop * t)
            o.rotation_euler = (t * .23 + ph, t * .31, t * .11) if t < t_land else (0, 0, ph)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)

def camera_more(cam):
    keys = [(101, (3.5, -11.4, 1.1), (0.35, 0.65, 4.2), 20), (106, (1.6, -10.6, .95), (0.1, 0.6, 3.0), 22), (120, (-2.6, -7.4, 1.35), (-.9, 0.0, .95), 26),
            (149, (-2.45, -7.0, 1.38), (-.85, 0.1, 1.0), 26), (162, (1.2, -16.0, 6.0), (2.5, 10.0, 2.0), 22), (F1, (5.0, -24.0, 15.0), (6.2, 70.0, 0.0), 22)]
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    R = random.Random(4)
    for f in range(HIT - 1, HIT + 12):
        k = max(0.0, 1 - (f - HIT) / 10) if f >= HIT else 0.0
        cam.data.shift_x = R.uniform(-1, 1) * .025 * k; cam.data.shift_y = R.uniform(-1, 1) * .025 * k
        cam.data.keyframe_insert("shift_x", frame=f); cam.data.keyframe_insert("shift_y", frame=f)

def stand_up():
    card = bpy.data.objects["Card_planter"]
    for f in range(UP0, F1 + 1):
        p = S1.LAND.copy(); p.z = -S1.SIT_DROP * (1 - smooth((f - UP0) / (UP1 - UP0))); card.location = p; card.keyframe_insert("location", frame=f)

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
    S1.F1 = F1; sc.frame_start, sc.frame_end = S1.F0, F1
    rig, cam = S1.build_take(sc)
    hit, nd = car_crash(rig); S1.driver(rig, cam, HIT); w = wheel_off(rig); oak_shake(); leaves_again(); camera_more(cam); stand_up()
    print("CRASH dent verts", nd, "wheel", w.name if w else None)
    front = rig.matrix_world @ Vector((0, -2.0, 1.0))
    vfx.apply(sc, [
        {"type": "dust_burst", "name": "car_brake", "at": [1.5, 3.7, .1], "frame": 100, "count": 8, "radius": 1.2, "height": .8, "seed": 31, "life": 30, "color": [.72, .64, .5]},
        {"type": "dust_burst", "name": "car_hit", "at": [.6, 1.2, .3], "frame": HIT, "count": 16, "radius": 2.0, "height": 1.6, "seed": 32, "life": 45, "color": [.75, .7, .6]},
        {"type": "smoke", "name": "wreck_smoke", "at": [.9, 1.9, 1.0], "frames": [HIT + 4, F1], "every": 6, "per_burst": 2, "rise": 1.8, "size": .35, "density": .45,
         "color": [.88, .88, .88], "life": 50, "seed": 33, "drift": [-.3, 0]},
        {"type": "dust_burst", "name": "wheel_flat", "at": [-1.25, -1.55, .05], "frame": FLAT, "count": 6, "radius": .5, "height": .3, "seed": 34, "life": 24, "color": [.6, .52, .4]}])
    S1.fx_to_layer(("car_brake", "car_hit", "wreck_smoke", "wheel_flat"))
    sc.frame_start = F0
    S1.finish(sc, OUT)

if __name__ == "__main__": main()
