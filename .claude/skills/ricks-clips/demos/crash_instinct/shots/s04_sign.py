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

F0, F1 = 282, 362; SWAP = 284; HIT = 313; FLIP = 339; FLAT = 349   # HIT measured on the reference (rear already lifted at 318)
SIGN_AT = (0.5, -1.75); TYRE_AT = Vector((1.3, -1.6, 0)); CAR_X = .35; CAR_STOP = .5 + 1.73; SPEED = 1.3     # m per frame = 140 km/h (measured: 5 frames across 6.5 m)
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

KEI_GLTF = os.path.join(S1.SKILL, "library", "assets", "sketchfab", "6689ab2bf0f244808efcbe6baf31b7de", "gltf", "scene.gltf")   # "Generic Kei car", ahadika, CC-BY 4.0, no real brand
KEI_FRONT = 1.73; KEI_AXLE = 1.16; KEI_WHEEL_R = .29; KEI_SEAT = Vector((.36, -.15, .12))

def blue_car():
    """THE REFERENCE'S CAR, analysed on frames 312-327 (references/crash_instinct/shots/s04.md §3): a small boxy tall van, bright plain blue
    (#3e7ecf measured), glossy clear coat without flakes, black window frames, BIG CLEAR windows through which the light seats, the
    steering wheel and the sky behind are seen, silver multi-spoke wheels, red tail lights. Model: "Generic Kei car" (ahadika, CC-BY).
    Its origin is on the ground; it faces -Y."""
    before_o = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=KEI_GLTF); new = [o for o in bpy.data.objects if o not in before_o]
    c = street.col("L_OBJECTS"); rig = bpy.data.objects.new("blue_rig", None); c.objects.link(rig)
    body = bpy.data.objects.new("blue_body", None); c.objects.link(body); body.parent = rig
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = body
    mine = {sl.material.name.split(".")[0]: sl.material for o in new if o.type == "MESH" for sl in o.material_slots if sl.material}   # THIS import's materials
    def bsdf(name):                                                                             # (the white SUV also has a "body": never look a material up by its bare name)
        m = mine.get(name); return (m, m.node_tree.nodes.get("Principled BSDF")) if m and m.use_nodes else (None, None)
    def unlink(m, b, names):
        for inp in names:
            for l in list(b.inputs[inp].links): m.node_tree.links.remove(l)
    m, b = bsdf("body")
    if b:                                                                                       # plain bright blue, smooth clear coat (no texture, no flakes)
        unlink(m, b, ("Base Color", "Metallic", "Roughness", "Normal"))
        b.inputs["Base Color"].default_value = (*street.srgb("#2f74d8"), 1); b.inputs["Metallic"].default_value = 0.0; b.inputs["Roughness"].default_value = .32
        b.inputs["Coat Weight"].default_value = .8; b.inputs["Coat Roughness"].default_value = .05; b.inputs["Specular IOR Level"].default_value = .5
    m, b = bsdf("glass")
    if b:                                                                                       # CLEAR glass: the inside is seen from the outside (CB)
        unlink(m, b, ("Base Color", "Alpha", "Roughness", "Metallic", "Normal"))
        b.inputs["Base Color"].default_value = (1, 1, 1, 1); b.inputs["Alpha"].default_value = 1.0; b.inputs["Metallic"].default_value = 0.0
        b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["Roughness"].default_value = .0; b.inputs["IOR"].default_value = 1.05
    m, b = bsdf("interior")
    if b:                                                                                       # light grey seats and trim, as in the reference (#adbfc8 seen through the glass)
        src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
        if src:
            hv = m.node_tree.nodes.new("ShaderNodeHueSaturation"); hv.inputs["Saturation"].default_value = .25; hv.inputs["Value"].default_value = 3.2
            m.node_tree.links.new(src, hv.inputs["Color"]); m.node_tree.links.new(hv.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = .8
    m, b = bsdf("WHEEL")
    if b: b.inputs["Metallic"].default_value = .9; b.inputs["Roughness"].default_value = .28
    for o in [rig, body] + new:
        if o.type in ("MESH", "EMPTY"): key_vis(o, visible_from=SWAP)
    for f in range(S1.F0, F1 + 1, 1):                                                           # constant speed down the verge, brakes over 3 frames, stopped by the trunk, rebound
        if f <= HIT - 3: y = CAR_STOP + SPEED * (HIT - 3 - max(f, SWAP - 2)) + 2.6
        elif f <= HIT: y = CAR_STOP + (2.6, 1.3, .45, 0.0)[f - (HIT - 3)]
        else: t = f - HIT; y = CAR_STOP + .2 * (1 - math.exp(-t / 2.5))
        if f < SWAP - 2 and f % 40: continue
        rig.location = (CAR_X, y, 0); rig.keyframe_insert("location", frame=f)
    for f in range(HIT - 4, F1 + 1):                                                            # the rear lifts ABOUT the front axle and drops back with a bounce
        t = f - HIT
        if t < -3: p = 0.0
        elif t < 0: p = 3.0 * (t + 3) / 3
        else: p = 3.0 * math.exp(-t / 2) + 25.0 * math.sin(min(math.pi, t * math.pi / 13)) * (1 if t <= 13 else 0) + (2.5 * math.exp(-(t - 13) / 3) * math.sin((t - 13) * 1.2) if t > 13 else 0)
        pr = math.radians(p); rig.rotation_euler = (pr, 0, 0); rig.delta_location = (0, -KEI_AXLE * (1 - math.cos(pr)), KEI_AXLE * math.sin(pr))
        rig.keyframe_insert("rotation_euler", frame=f); rig.keyframe_insert("delta_location", frame=f)
    return rig, body, new

def crush(rig, parts):
    from rc import physics
    sc = bpy.context.scene; sc.frame_set(HIT); bpy.context.view_layer.update(); n = 0
    front = rig.matrix_world @ Vector((0, -KEI_FRONT, .6))
    for o in parts:
        if o.type != "MESH" or not o.data.materials or o.data.materials[0].name.split(".")[0] not in ("body", "grille", "frontgrille", "headlamp"): continue
        r = physics.deform(sc, {"object": o.name, "name": "crash_dent", "point": list(front + Vector((0, -.1, 0))), "direction": [0, 1, -.2],
                                "radius": .85, "depth": .34, "at_frame": HIT, "ease": 3}, None, None)
        n += r["deformed_vertices"]
    return n

def wheel_off(parts):
    """ONE OF THE CAR'S OWN WHEELS breaks off and rolls (CB 2026-11-20). The model keeps its four wheels in two meshes (tyres, rims): the
    front wheel on the camera's side (x > 0, y < 0) is CUT OUT of them into its own object, origin at the wheel centre (PI-021). It rides
    with the car to the hit, is thrown up, lands on the shoulder in front of the grass, rolls to the sign, wobbles and falls flat ON the old tyre."""
    import bmesh
    sc = bpy.context.scene; c = street.col("L_OBJECTS"); body = bpy.data.objects["blue_body"]
    wm = bpy.data.meshes.new("blue_wheel"); wb = bmesh.new(); mats = []
    for o in parts:
        if o.type != "MESH" or not o.data.materials or o.data.materials[0].name.split(".")[0] not in ("tire", "WHEEL"): continue
        M = body.matrix_world.inverted() @ o.matrix_world; bm = bmesh.new(); bm.from_mesh(o.data)
        mine = [v for v in bm.verts if (M @ v.co).x > .3 and (M @ v.co).y < -.5]
        if not mine: bm.free(); continue
        keep = bmesh.new(); keep.from_mesh(o.data); keep.verts.ensure_lookup_table()
        idx = set(v.index for v in mine)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in idx], context="VERTS")               # bm = the wheel only
        bmesh.ops.delete(keep, geom=[v for v in keep.verts if v.index in idx], context="VERTS")               # keep = the three other wheels
        keep.to_mesh(o.data); keep.free()
        tmp = bpy.data.meshes.new("tmp"); bm.to_mesh(tmp); bm.free(); tmp.transform(M)
        k = len(mats); mats.append(o.data.materials[0]); off = len(wb.verts); wb.from_mesh(tmp); wb.faces.ensure_lookup_table()
        for f_ in wb.faces:
            if all(v.index >= off for v in f_.verts): f_.material_index = k
        bpy.data.meshes.remove(tmp)
    if not wb.verts: return None
    cen = sum((v.co for v in wb.verts), Vector()) / len(wb.verts); bmesh.ops.translate(wb, vec=-cen, verts=wb.verts)
    wb.to_mesh(wm); wb.free()
    for m_ in mats: wm.materials.append(m_)
    w = bpy.data.objects.new("blue_wheel", wm); c.objects.link(w); w.rotation_mode = "QUATERNION"; C = Matrix.Translation(cen); local = {}
    for f in [SWAP - 2, SWAP - 1] + list(range(SWAP, HIT + 1)):
        sc.frame_set(f); local[f] = (body.matrix_world @ C).copy()
    def put(M, f):
        loc, rot, scl = M.decompose(); w.location = loc; w.rotation_quaternion = rot; w.scale = scl
        w.keyframe_insert("location", frame=f); w.keyframe_insert("rotation_quaternion", frame=f); w.keyframe_insert("scale", frame=f)
    prev_y = None; spin = 0.0
    for f, M in local.items():                                                                  # on the car it turns with the distance driven
        y = M.translation.y; spin += 0 if prev_y is None else (prev_y - y) / KEI_WHEEL_R; prev_y = y
        put(M @ Matrix.Rotation(-spin, 4, "X"), f)
    key_vis(w, visible_from=SWAP)
    loc0 = local[HIT].translation; start = Vector((loc0.x, loc0.y, 0)); mid = Vector((1.75, -.2, 0)); stop = TYRE_AT.copy()   # out in front of the trunk, along the shoulder, to the sign
    top = bpy.data.objects["old_tyre"].get("top", .22); T = FLAT - 5 - HIT
    def pos(e): return (1 - e) ** 2 * start + 2 * e * (1 - e) * mid + e ** 2 * stop          # one smooth curve
    dist = 0.0; last = start
    for f in range(HIT + 1, F1 + 1):
        t = min(1.0, (f - HIT) / T); e = 1 - (1 - t) ** 2; p = pos(e); step = p - last; dist += step.length; d = step.normalized() if step.length > 1e-4 else (stop - mid).normalized(); last = p
        yaw = math.atan2(d.y, d.x)
        fall = (math.pi / 2) * min(1.0, max(0.0, (f - (FLAT - 6)) / 6.0)) ** 2
        wob = math.radians(9) * math.sin((f - HIT) * .9) * max(0.0, t - .55) * 2.2 if f <= FLAT - 6 else 0.0
        hop = .55 * math.sin(min(math.pi, (f - HIT) * math.pi / 8)) if f - HIT <= 8 else (.12 * math.sin(min(math.pi, (f - HIT - 8) * math.pi / 5)) if f - HIT <= 13 else 0.0)   # thrown up, lands, one small bounce
        R = Matrix.Rotation(fall + wob, 4, d) @ Matrix.Rotation(yaw + math.pi / 2, 4, "Z") @ Matrix.Rotation(-spin - dist / KEI_WHEEL_R, 4, "X")
        h = KEI_WHEEL_R * math.cos(fall) + (top + .1) * math.sin(fall) + hop
        put(Matrix.Translation(p + Vector((0, 0, h))) @ R, f)
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
    """the blue car's driver: ONE still drawing of the seated driver (first drawing of the driver card) on its own card, standing on the
    blue car's seat and facing the road side (this shot's camera is always east of the tree); thrown forward at the hit (seat belt)"""
    src = bpy.data.objects.get("Card_driver"); png = os.path.join(HERE, "..", "build", "cards_s01", "cards", "driver", "s0001.png")
    if src is None or not os.path.exists(png): return None
    m = bpy.data.materials.new("card_driver_blue"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(png, check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"]); nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = .45; b.inputs["Roughness"].default_value = .9; b.inputs["Specular IOR Level"].default_value = 0.0
    me = src.data.copy(); me.materials.clear(); me.materials.append(m)
    card = bpy.data.objects.new("Card_driver_blue", me); street.col("L_OBJECTS").objects.link(card); card.scale = src.scale * .88; sc = bpy.context.scene
    card.rotation_euler = (0, 0, math.radians(90))
    for f in [SWAP - 2] + list(range(SWAP - 1, F1 + 1)):
        sc.frame_set(f); off = KEI_SEAT.copy()
        if f >= HIT: t_ = f - HIT; off.y -= .22 * math.exp(-t_ / 3.0) * math.sin(min(math.pi, t_ * .7) + .01)
        card.location = body.matrix_world @ off; card.keyframe_insert("location", frame=f)
    key_vis(card, visible_from=SWAP)
    return card

def week_later_light(sc):
    """THE REFERENCE'S LIGHT for this view, analysed on frames 300-357 (s04.md §10): the sun is on the CAMERA's side, high on the left
    (the sign's shadow falls behind it to the right, 1 sign-height long -> about 45 deg; trunk and crown lit from the front-left, branch
    shadows on the trunk), deep blue sky with small clouds and NO glow, open bright shadows. A week has passed inside the whip, so the
    time of day changes there, off-frame: sun from the south-east at 45 deg, sky photo turned with it, no sun glow, stronger sky fill."""
    from rc.look import relight, bounce_fill
    relight(sc, SWAP, azimuth=160.0, elevation=54.0, energy=11.5, glow=0.0, light=.55, sky=1.4)
    l = bounce_fill(street.col("LIGHT"), at=(12.0, 4.0, 3.0), aim=(0, 0, 3.0), energy=0.0, size=10.0, name="bounce_fill_east")   # opens the trunk's shadow side
    l.data.energy = 0.0; l.data.keyframe_insert("energy", frame=SWAP - 1); l.data.energy = 500.0; l.data.keyframe_insert("energy", frame=SWAP)
    return l


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
    aim2 = (SIGN_AT[0], SIGN_AT[1] + .45, 1.5)
    keys = [(283, (4.2, -15.0, 1.6), (2.5, -6.0, 15.0), 24), (284, (4.5, -2.4, 1.62), (SIGN_AT[0], SIGN_AT[1], 7.5), 32),
            (284.8, (4.6, -2.05, 1.6), tuple(sg), 35),                                        # the whip ENDS before frame 285's shutter opens: 285 is sharp
            (285, (4.61, -2.05, 1.6), tuple(sg), 35), (288, (4.9, -2.0, 1.58), tuple(sg), 35),
            (309, (11.6, -.6, .6), (0.0, 0.3, 4.8), 22), (330, (11.4, -.75, .64), (0.0, 0.25, 4.75), 22),
            (348, (6.6, -1.3, 1.35), aim2, 30), (F1, (6.3, -1.35, 1.38), aim2, 30)]
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
    for o in bpy.data.objects:                                                                  # a week later the clods of the planting are gone too
        if o.name.startswith("clod"): key_vis(o, hidden_from=SWAP)
    S1.roadside.verge_grass(street.col("L_SET"), [[10.55, -3.2], [10.95, -3.2], [10.95, 2.0], [10.55, 2.0]], 260, 21, scale=(2.0, 3.3))   # tall blades in front of the wide shot's lens (reference)
    sg = signkit.build(street.col("L_OBJECTS"), SIGN_AT)
    for o in tree_and_children(sg): key_vis(o, visible_from=SWAP)
    signkit.shake(sg, HIT); signkit.flip(sg, FLIP)
    old_tyre(); brig, body, parts = blue_car(); nd = crush(brig, parts); driver2(body, cam); w = wheel_off(parts)
    oak_shake(); leaves_third(); camera_sign(cam); week_later_light(sc)
    print("SHOT4 gone", n, "dent verts", nd, "wheel", w.name if w else None)
    vfx.apply(sc, [
        {"type": "dust_burst", "name": "blue_brake", "at": [CAR_X + .6, 3.6, .1], "frame": HIT - 3, "count": 8, "radius": 1.2, "height": .8, "seed": 41, "life": 30, "color": [.72, .64, .5]},
        {"type": "dust_burst", "name": "blue_hit", "at": [.6, .6, .3], "frame": HIT, "count": 18, "radius": 2.2, "height": 1.8, "seed": 42, "life": 45, "color": [.75, .7, .6]},
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
