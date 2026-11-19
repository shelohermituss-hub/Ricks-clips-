"""crash_instinct shot 1 (0.0-3.2 s, frames 0-95): "If you plant a tree beside an empty road, cars will steer right into it."
Analysis: references/crash_instinct/shots/s01.md; plan: plan/s01.json (PLAN PASS). One continuous take:
  0-8   the planter shows his acorn (proud)            8-17  squats and drops it into the hole (it follows his drawn hand, then falls)
  15-21 a full-grown oak FALLS FROM THE SKY roots first into the hole (enters through the top of the frame), 21 impact: dust ring,
        clods, camera shake, crown sways, leaves fall      19-24 he jumps in shock      22-36 the blast throws him back on an arc;
        he plops down sitting in the tall grass      24-45 the camera pulls back and slides down onto the road
  0-95  a white car drives down the empty road toward us; 78-95 it steers off toward the tree, bites the shoulder (dust)
    blender -b --factory-startup --python s01_plant.py -- <out.blend> [--res 270x480] [--samples 12] [--still f:out.png ...]"""
import bpy, math, os, random, sys, json
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "sets")); sys.path.insert(0, os.path.join(SKILL, "demos", "crashed_car", "sets")); sys.path.insert(0, os.path.join(SKILL, "blender"))
import roadside, street, oak as oakkit  # noqa: E402
from rc import render, vfx, characters, lookdev  # noqa: E402

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: A[A.index(k) + 1] if k in A else d
OUT = A[0] if A and not A[0].startswith("--") else "/tmp/s01_plant.blend"
F0, F1 = 0, 95; IMPACT = 21; RELEASE = 14
HERO = Vector((-0.75, -0.3, 0)); LAND = Vector((-1.85, -0.75, 0)); SIT_DROP = .30          # seated drawing sits on a 0.45 m seat: sunk 0.30 m into the tall grass
CAR_GLTF = os.path.join(SKILL, "library", "assets", "sketchfab", "5db696c6ed5d4bdc87905c1040fa072a", "gltf", "scene.gltf")   # MMC Generic Small SUV (MMC Works, CC-BY)
CAR_LIFT = .80; CAR_FRONT = 2.05                                                         # its origin is at mid-height; nose at local y = -2.05

EXPOSURE = -0.5; SATURATION = 1.05

def smooth(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)

def oak():
    """the hero tree: falls from the sky (keyed, accelerating like gravity) and lands upright in the hole; the crown sways twice after"""
    o = oakkit.oak(street.col("L_SET"), "oak", seed=7, height=9.0); o.location = (0, 0, 40); o.rotation_euler = (0, 0, .6)
    roadside.light_shafts(street.col("L_FX"), parent=o)                                   # sun shafts under its crown, attached to it
    z_top = 24.0
    for f in range(F0, IMPACT + 1):
        if f <= 13: z = 40.0                                                                  # far above the frame (its shadow falls ~40 m away, out of frame)
        else: t = (f - 13) / (IMPACT - 13); z = z_top * (1 - t * t)                          # free fall: z = h (1 - t^2)
        o.location.z = z; o.keyframe_insert("location", frame=f)
    for f in range(IMPACT, F1 + 1):                                                           # settle: a damped sway of the whole tree about its base
        t = f - IMPACT; a = math.radians(3.2) * math.exp(-t / 9) * math.sin(t * .55)
        o.rotation_euler = (a, a * .4, .6); o.keyframe_insert("rotation_euler", frame=f)
    o.keyframe_insert("rotation_euler", frame=IMPACT - 1)
    return o

def turned_earth():
    """lasting consequence of the landing: a ring of turned earth and clods around the trunk (they fly out at the impact, then stay)"""
    c = street.col("L_FX"); mud = bpy.data.materials.get("hole_mud") or street.pbr("hole_mud", "brown_mud_02", tile=.8, value=.8)
    import bmesh
    R = random.Random(11); g = 9.81 / 900.0; out = []
    for k in range(22):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=R.uniform(.05, .13))
        for v in bm.verts: v.co *= 1 + .25 * math.sin(v.co.x * 40 + k)
        o = street.mesh_obj("clod%d" % k, bm, mud, c, smooth=True); a = R.uniform(0, 6.28); r0 = .5
        p = Vector((math.cos(a) * r0, math.sin(a) * r0, .1)); vel = Vector((math.cos(a), math.sin(a), 0)) * R.uniform(.05, .11) + Vector((0, 0, R.uniform(.08, .16)))
        o.location = p; o.hide_render = True; o.keyframe_insert("hide_render", frame=IMPACT - 1)
        for f in range(IMPACT, F1 + 1):                                                       # the clods are thrown OUT of the hole (born inside it, under the trunk)
            if f > IMPACT: vel.z -= g; p = p + vel
            if p.z < .04 and vel.z < 0: p.z = .04; vel = Vector((vel.x * .3, vel.y * .3, 0))
            o.location = p; o.keyframe_insert("location", frame=f)
        o.hide_render = False; o.keyframe_insert("hide_render", frame=IMPACT); out.append(o)
    return out

def leaves():
    """leaves shaken off the crown by the impact: they flutter down for ~2 s and stay on the grass"""
    import bmesh
    c = street.col("L_FX"); m = street.mat("leaf_fall", "#5f9e2e", .7); R = random.Random(21); out = []
    for k in range(46):
        bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((-.045, 0, 0), (0, .07, 0), (.045, 0, 0), (0, -.05, 0))]; bm.faces.new(vs)
        o = street.mesh_obj("leaf%d" % k, bm, m, c); o.visible_shadow = False
        a = R.uniform(0, 6.28); r = R.uniform(1.0, 5.0); p0 = Vector((math.cos(a) * r, math.sin(a) * r, R.uniform(4.5, 8.0))); drop = R.uniform(.045, .08)
        sw, ph = R.uniform(.25, .6), R.uniform(0, 6.28); delay = R.randint(0, 8)            # drawn ONCE per leaf (a draw per frame made it jump: TELEPORT)
        t_land = (p0.z - .03) / drop; rest = None
        for f in range(F0, F1 + 1):
            t = min(max(0, f - IMPACT - delay), t_land)                                     # landed: it stays where it fell (lasting consequence)
            o.location = p0 + Vector((sw * math.sin(t * .2 + ph), sw * .6 * math.cos(t * .17 + ph), 0)); o.location.z = max(.03, p0.z - drop * t)
            o.rotation_euler = (t * .23 + ph, t * .31, t * .11) if t < t_land else (0, 0, ph)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
        out.append(o)
    return out

def acorn():
    import bmesh
    c = street.col("L_OBJECTS"); nut = street.mat("acorn_nut", "#9a5a22", .35); cap = street.mat("acorn_cap", "#5e3d1e", .85, bump=("noise", 60, .5))
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=.04)
    for v in bm.verts: v.co.z *= 1.35
    o = street.mesh_obj("acorn", bm, nut, c, smooth=True)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=.044)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < .005], context="VERTS")
    k = street.mesh_obj("acorn_cap", bm, cap, c, smooth=True); k.parent = o; k.location = (0, 0, .03)
    return o

def car():
    """the white SUV of the reference (Sketchfab 'MMC Generic Small SUV Car', MMC Works, CC-BY; no real brand). CB 2026-11-19: MATTE white
    paint (the model's metallic/roughness texture and normal map made it sparkle: removed; then CB asked for a smooth METALLIC white), CLEAR (untinted) windows, a driver inside.
    It faces -Y = toward us; lifted so the tyres sit on the road."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=CAR_GLTF); new = [o for o in bpy.data.objects if o not in before]
    c = street.col("L_OBJECTS"); rig = bpy.data.objects.new("car_rig", None); c.objects.link(rig)
    body = bpy.data.objects.new("car_body", None); c.objects.link(body); body.parent = rig; body.location = (0, 0, CAR_LIFT)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = body
    paint = bpy.data.materials.get("body")
    if paint and paint.use_nodes:
        b = paint.node_tree.nodes.get("Principled BSDF")
        for inp in ("Base Color", "Metallic", "Roughness", "Normal"):
            for l in list(b.inputs[inp].links): paint.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (*street.srgb("#f1f1ee"), 1); b.inputs["Metallic"].default_value = .55; b.inputs["Roughness"].default_value = .28   # CB 2026-11-19:
        b.inputs["Coat Weight"].default_value = .6; b.inputs["Coat Roughness"].default_value = .06; b.inputs["Specular IOR Level"].default_value = .5     # METALLIC white, smooth (no flake texture)
    for name in ("Glass_ext-tinted", "glass-windshield"):
        m = bpy.data.materials.get(name)
        if m and m.use_nodes and m.node_tree.nodes.get("Principled BSDF"):
            b = m.node_tree.nodes["Principled BSDF"]
            for inp in ("Base Color", "Alpha"):
                for l in list(b.inputs[inp].links): m.node_tree.links.remove(l)
            b.inputs["Base Color"].default_value = (1, 1, 1, 1); b.inputs["Alpha"].default_value = 1.0
            b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["Roughness"].default_value = .02; b.inputs["IOR"].default_value = 1.1
    keys = [(0, (4.2, 56.4), 0.0), (78, (4.2, 13.5), 0.0), (86, (3.4, 9.0), -11.0), (95, (1.9, 4.6), -22.0)]   # 60 km/h = 0.55 m/frame, then steers at the tree
    for f, (x, y), yaw in keys:
        rig.location = (x, y, 0); rig.rotation_euler = (0, math.radians(1.2) if f >= 86 else 0, math.radians(yaw))   # body roll in the turn
        rig.keyframe_insert("location", frame=f); rig.keyframe_insert("rotation_euler", frame=f)
    for f in range(F0, F1 + 1, 2):                                                             # suspension bob on the road surface
        rig.delta_location = (0, 0, .012 * math.sin(f * .9) + (.02 * math.sin(f * 1.7) if f >= 82 else 0)); rig.keyframe_insert("delta_location", frame=f)
    return rig

def camera():
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); street.col("CAM").objects.link(cam); bpy.context.scene.camera = cam
    cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24
    keys = [(0, (-0.45, -6.0, 1.75), (-0.35, 0.6, .45), 24), (24, (-0.4, -5.7, 1.78), (-0.3, 0.7, .6), 24), (32, (0.6, -7.0, 1.5), (0.1, 0.3, 2.4), 21),
            (40, (3.3, -12.4, 1.05), (0.3, 0.5, 4.5), 20), (95, (3.6, -11.8, 1.1), (0.35, 0.6, 4.4), 20)]
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
    street.handheld(cam, F0, F1, amp=.01, rot_deg=.2, seed=1)
    R = random.Random(2)                                                                        # impact shake (sensor shift, decays over 10 frames)
    for f in range(IMPACT - 1, IMPACT + 12):
        k = max(0.0, 1 - (f - IMPACT) / 10) if f >= IMPACT else 0.0
        cam.data.shift_x = R.uniform(-1, 1) * .03 * k; cam.data.shift_y = R.uniform(-1, 1) * .03 * k
        cam.data.keyframe_insert("shift_x", frame=f); cam.data.keyframe_insert("shift_y", frame=f)
    return cam

def planter(cam, seed):
    """ONE card all through (front view only, PI-016). 22-36: thrown back on an arc by the blast and sunk into the tall grass as the drawing
    plops down onto its (hidden) seat. The acorn follows the drawn right hand (card_anchors.py) until RELEASE, then falls into the hole."""
    cd = os.path.join(HERE, "..", "build", "cards_s01"); folder = os.path.join(cd, "cards", "planter")
    AN = json.load(open(os.path.join(folder, "anchors.json"))); sc = bpy.context.scene
    characters.place_cards(sc, cd, ["planter"], cam, .55, ground=None)
    setc = street.col("L_SET")
    for o in [o for o in bpy.data.objects if o.name.lower() in ("card_planter", "contact_planter")]:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        setc.objects.link(o)
        for f in range(F0 - 1, F1 + 2):
            for dp in ("hide_render", "hide_viewport", "location"):
                try: o.keyframe_delete(dp, frame=f)
                except RuntimeError: pass
        o.hide_render = o.hide_viewport = False
    card = bpy.data.objects["Card_planter"]; disc = bpy.data.objects.get("Contact_planter")
    if disc:
        for cn in disc.constraints:
            if cn.type == "COPY_LOCATION": cn.use_z = False
    for f in range(F0, F1 + 1):
        if f < 22: p = HERO.copy()
        elif f <= 36:
            t = (f - 22) / 14; e = smooth(t); p = HERO.lerp(LAND, e); p.z = 4 * .38 * t * (1 - t) - SIT_DROP * smooth((f - 30) / 6)
        else: p = LAND.copy(); p.z = -SIT_DROP
        card.location = p; card.keyframe_insert("location", frame=f)
    prev = None; hole = Vector((0, 0, .05))
    for f in range(F0, F1 + 1):
        sc.frame_set(f); M = card.matrix_world; a = AN[str(f)]; rh = max(a["hands"], key=lambda q: q[0])
        tocam = cam.matrix_world.translation - M.translation; tocam.z = 0; tocam.normalize()
        if f <= RELEASE: p = M @ Vector((rh[0], 0, rh[1] + .02)) + tocam * .04
        else:
            t = min(1., (f - RELEASE) / 4); p = prev.lerp(Vector((hole.x, hole.y, prev.z)), t); p.z = max(-.25, prev.z - .05 - .06 * (f - RELEASE))   # sinks under the earth disc: hidden by the hole itself, no visibility switch
        if prev is not None and f <= RELEASE:
            d = p - prev; p = prev + (d if d.length <= .12 else d.normalized() * .12)       # a held thing never jumps: 12 cm per frame at most
        seed.location = p; seed.keyframe_insert("location", frame=f); prev = p.copy()
    return card

DRIVER_SEAT = Vector((.37, -.02, -.66))                                                # card origin (its feet) in the SUV body's space: hips on the front-left seat

def driver(rig, cam, hit=None):
    """the SUV driver (cast:driver, front view, frozen seated drawing): his card follows the driver's seat on every frame (seen through the
    clear windscreen); at the hit he is thrown forward and back (seat belt). Called after the car's last keys are set."""
    cd = os.path.join(HERE, "..", "build", "cards_s01"); sc = bpy.context.scene
    if "Card_driver" not in bpy.data.objects: characters.place_cards(sc, cd, ["driver"], cam, .55, contact=False, ground=None)
    card = bpy.data.objects["Card_driver"]
    for uc in list(card.users_collection): uc.objects.unlink(card)
    street.col("L_OBJECTS").objects.link(card)
    for f in range(F0 - 1, F1 + 2):
        for dp in ("hide_render", "hide_viewport", "location"):
            try: card.keyframe_delete(dp, frame=f)
            except RuntimeError: pass
    card.hide_render = card.hide_viewport = False; body = bpy.data.objects["car_body"]
    for f in range(F0, F1 + 1):
        sc.frame_set(f); off = DRIVER_SEAT.copy()
        if hit is not None and f >= hit:
            t = f - hit; off.y -= .22 * math.exp(-t / 3.0) * math.sin(min(math.pi, t * .7) + .01)      # thrown toward the dashboard, back into the seat
        card.location = body.matrix_world @ off; card.keyframe_insert("location", frame=f)
    return card

def grass_and_flowers():
    """CB 2026-11-19: grass shorter and half as dense as before (closer to the reference, faster to render); tall only right under shot 1's lens,
    short where shot 2 looks across at grass level; far zones thinned (LOD)"""
    c = street.col("L_SET"); clear = ({"center": [0, 0], "radius": 1.0},)
    roadside.verge_grass(c, [[-6.3, -2.4], [1.45, -2.4], [1.45, 14], [-6.3, 14]], 15000, 1, scale=(.45, .8), exclude=clear)
    roadside.verge_grass(c, [[-1.6, -6.5], [1.45, -6.5], [1.45, -2.4], [-1.6, -2.4]], 3200, 4, scale=(1.0, 1.6))
    roadside.verge_grass(c, [[-6.3, -16], [1.45, -16], [1.45, -6.5], [-6.3, -6.5]], 7000, 5, scale=(.5, .9))
    roadside.verge_grass(c, [[-6.3, -6.5], [-1.6, -6.5], [-1.6, -2.4], [-6.3, -2.4]], 3200, 6, scale=(.5, .9))
    roadside.verge_grass(c, [[-6.3, 14], [1.45, 14], [1.45, 140], [-6.3, 140]], 6000, 2, scale=(.9, 1.5))
    roadside.verge_grass(c, [[10.6, -16], [14.7, -16], [14.7, 80], [10.6, 80]], 2500, 3, scale=(.9, 1.5))
    for k, (x, y) in enumerate(((-2.8, -3.2), (-3.4, -2.1), (-1.6, -2.6), (-4.2, -1.0), (.6, -2.4), (-2.2, -4.0))):
        street.lib_instance("dandelion%d" % k, "dandelion_01", c, (x, y, 0), rot=k * 1.3, scale=1.0)

def build_take(sc):
    """everything of the take on the roadside set up to frame F1 (shot 2 sets F1 further and adds its own actions on top)"""
    roadside.build(sc); roadside.hole(street.col("L_SET")); roadside.dirt_patch(street.col("L_SET")); grass_and_flowers()
    oak(); turned_earth(); leaves(); rig = car(); cam = camera(); seed = acorn(); planter(cam, seed)
    vfx.apply(sc, [
        {"type": "dust_burst", "name": "seed_earth", "at": [0, 0, .05], "frame": RELEASE + 3, "count": 5, "radius": .35, "height": .25, "seed": 3, "life": 18, "color": [.45, .33, .22]},
        {"type": "dust_burst", "name": "tree_impact", "at": [0, 0, .1], "frame": IMPACT, "count": 22, "radius": 2.6, "height": 1.6, "seed": 5, "life": 50, "color": [.62, .52, .38]},
        {"type": "dust_burst", "name": "planter_landing", "at": [LAND.x, LAND.y, .1], "frame": 34, "count": 6, "radius": .6, "height": .4, "seed": 8, "life": 26, "color": [.6, .52, .4]},
        {"type": "dust_burst", "name": "car_shoulder_1", "at": [2.6, 7.4, .1], "frame": 86, "count": 8, "radius": 1.2, "height": .8, "seed": 13, "life": 30, "color": [.72, .64, .5]},
        {"type": "dust_burst", "name": "car_shoulder_2", "at": [2.0, 5.6, .1], "frame": 92, "count": 8, "radius": 1.4, "height": 1.0, "seed": 14, "life": 30, "color": [.72, .64, .5]}])
    fx_to_layer()
    return rig, cam

def fx_to_layer(prefixes=("seed_earth", "tree_impact", "planter_landing", "car_shoulder")):
    for o in list(bpy.data.objects):                                                           # every effect object goes to the FX layer
        if o.users_collection and o.users_collection[0].name in ("RC_FX", "FX") or o.name.startswith(tuple(prefixes)):
            for uc in list(o.users_collection): uc.objects.unlink(o)
            street.col("L_FX").objects.link(o)

def finish(sc, out):
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium Contrast"; sc.view_settings.exposure = EXPOSURE   # grade matched on the reference:
    lookdev.grade(sc, {"saturation": SATURATION})          # 5 transforms measured on frames 46 and 126 (luma, saturation, contrast): this one is closest
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .3
    w, h = map(int, opt("--res", "270x480").split("x")); render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "12")), 0)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    if "--still" in A:
        for tok in A[A.index("--still") + 1:]:
            if tok.startswith("--"): break
            f, png = tok.split(":"); sc.frame_set(int(f)); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = F0, F1
    rig, cam = build_take(sc); driver(rig, cam); finish(sc, OUT)

if __name__ == "__main__": main()
