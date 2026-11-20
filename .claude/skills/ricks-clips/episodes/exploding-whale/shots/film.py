"""exploding-whale: shots 02-16, one function per shot (shot 01 is shots/s01_button.py). Plan: plan/plan.json (PLAN PASS before the build).
    blender -b --factory-startup --python shots/film.py -- <shot id> <out.blend> [--res 270x480] [--samples 16] [--still f:png ...] [--anim dir]"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit, toon
from kit import beach, props, cast, signs, col, key, move, ink, label, box, cyl, blob, show, fx
H = beach.height

# THE DRAWN WORLD on every beach shot (CB 2026-11-20: "exactement ce style, pour tous les prochains plans et vidéos"): sets/toon.py
DRESS_CLEAR = ((0, 0, 9.5), (-6.4, -8.0, 3.2), (-3.0, -8.2, 2.2), (-12.5, -4.6, 5.0))
_finish = kit.finish
def _drawn_finish(sc, Mo, expo=(), haze=.5):
    if "beach_sand" in bpy.data.materials:
        toon.stylize(sc, bpy.data.objects.get("whale"), sun=(Mo["az"], Mo["el"])); toon.dress(col("L_OBJECTS"), clear=DRESS_CLEAR); toon.ink_all()
        Mo.update(haze_color=(1.0, .80, .60, 1), bloom=.3, exposure=Mo["exposure"] - .5); haze = .2
    _finish(sc, Mo, expo, haze)
kit.finish = _drawn_finish
YELLOW, RED, WHITE, BLACK, GREEN = (.95, .72, .05), (.75, .04, .03), (.9, .9, .88), (.02, .02, .02), (.25, .75, .12)

def stink(c, at, f0, f1, n=5, seed=1):
    """green wavy stink lines rising from a point: a flat 2D sign, redrawn as it rises"""
    R = random.Random(seed); m = ink("stink_green", GREEN, 2.5); out = []
    for i in range(n):
        cu = bpy.data.curves.new("stink%d_%d" % (seed, i), "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = .035; sp = cu.splines.new("BEZIER"); sp.bezier_points.add(4)
        x0 = at[0] + R.uniform(-2.2, 2.2)
        for k, q in enumerate(sp.bezier_points): q.co = (x0 + .28 * math.sin(k * 1.9 + i), at[1], at[2] + k * .55); q.handle_left_type = q.handle_right_type = "AUTO"
        o = bpy.data.objects.new(cu.name, cu); c.objects.link(o); cu.materials.append(m); o.visible_shadow = False; s = f0 + i * 5
        for f, a, b in ((s, 0, 0), (s + 14, 0, .8), (s + 34, .5, 1), (f1, 1, 1)):
            cu.bevel_factor_start, cu.bevel_factor_end = a, b; cu.keyframe_insert("bevel_factor_start", frame=f); cu.keyframe_insert("bevel_factor_end", frame=f)
        key(o, "location", s, (0, 0, 0)); key(o, "location", f1, (0, 0, 1.2)); out.append(o)
    return out

# ---------------------------------------------------------------------------------------------------------------- 02
def s02(n):
    """131-345 "You see, in 1970, a whale washed up on a beach in Oregon. Forty five feet long, eight tons, and it stank for miles."
    0-70 aerial: a wave leaves the whale on the sand (washed 57) | 70-150 slide along it: the tape runs out, 45 FT (113), the 8 TONS tag drops (151)
    150-214 a jogger runs in, smells it and drops flat on "stank" (178); green stink lines rise"""
    sc = kit.begin(n); c, w, Mo = beach.build(sc, "grey", az=95, el=24); O = col("L_OBJECTS")
    y0, r0 = w.location.y, w.rotation_euler.z
    for f, y, rz in ((0, 9.0, .25), (44, 1.2, .06), (56, -.25, -.03), (70, 0, 0)):                 # carried in by the wave, slides, settles
        w.location.y = y0 + y; w.rotation_euler.z = r0 + rz; w.keyframe_insert("location", frame=f); w.keyframe_insert("rotation_euler", frame=f)
    foam = toon.wave(col("L_FX"))                                                                   # the wave that brings it, then pulls back: clear water with a foam lip
    move(foam, ((0, 0, 11.5, .05), (44, 0, 1.5, .16), (58, 0, .8, .10), (110, 0, 16.0, -.1)))
    tape = box("tape", (1, .06, .012), (0, 0, 0), ink("tape_yellow", YELLOW, .3, .4), bevel=0); x0, x1, ty = -7.0, 6.6, -3.0
    for f, t in ((62, .02), (112, 1.0)):                                                           # the tape unrolls behind the surveyor
        L = (x1 - x0) * t; tape.scale = (L, 1, 1); tape.location = (x0 + L / 2, ty, H(0, ty) + .03); key(tape, "scale", f); key(tape, "location", f)
    kit.linear(tape)
    t45 = label("t45", "45 FT", 1.0, (0, -2.6, 3.5), (math.radians(80), 0, 0), ink("sign_yellow", YELLOW, 1.2), extrude=.05)
    for f, s in ((108, 0), (113, 1.25), (118, 1.0)): key(t45, "scale", f, (s, s, s))               # pops on the word
    tag = box("tag8", (2.3, .08, 1.0), (2.5, -1.4, 40), ink("tag_card", (.93, .9, .8), 0, .7), bevel=.02); label("t8", "8 TONS", .5, (0, -.05, 0), (math.radians(90), 0, 0), ink("ink_red", RED), parent=tag, extrude=.01)
    move(tag, ((138, 2.5, -1.4, 40.0), (151, 2.5, -1.4, 2.5), (154, 2.5, -1.4, 2.72), (157, 2.5, -1.4, 2.55))); kit.linear(tag)
    cam = kit.camera([(0, (2.0, -34.0, 20.0), (0, 2.0, 0), 22), (50, (1.0, -24.0, 9.0), (0, 0, 1.0), 24), (70, (-11.0, -9.5, 1.4), (-6.0, -2.5, 1.2), 24),
                      (112, (2.0, -13.0, 1.5), (1.5, -2.0, 1.9), 22), (150, (3.0, -11.5, 1.5), (3.0, -1.5, 2.0), 24), (178, (9.5, -10.5, 1.2), (10.5, -4.4, 1.0), 26), (n - 1, (10.4, -9.4, .9), (11.0, -4.4, .6), 30)], n)
    C = kit.cards(sc, "02", cam, {"surveyor": [(0, -7.4, -3.5), (62, -7.0, -3.5), (112, 6.6, -3.5), (n, 6.6, -3.5)],
                                   "jogger": [(0, 36.0, -4.4), (150, 19.0, -4.4), (176, 11.6, -4.4), (n, 11.0, -4.4)]}, H)
    stink(col("L_FX"), (1.0, -2.2, 2.2), 150, n, 6, 1); stink(col("L_FX"), (8.6, -3.8, .6), 168, n, 3, 2)
    signs.spiral_eyes(C["jogger"], 186, n); fx(sc, [{"type": "dust_burst", "name": "faint", "at": [11.0, -4.4, .1], "frame": 190, "count": 8, "radius": .9, "height": .4, "seed": 4, "life": 24, "color": [.78, .7, .56]},
                                                   {"type": "dust_burst", "name": "beach_slide", "at": [0, -1.0, .2], "frame": 46, "count": 14, "radius": 5.0, "height": .7, "seed": 6, "life": 30, "color": [.8, .74, .6]}])
    d5 = bpy.data.objects.get("driftwood5"); d5.location.x += 9; d5.location.y += 1.5                # it lay across the jogger's close-up as a dark slab
    kit.finish(sc, Mo, ((0, -.1), (70, 0.0))); return sc

# ---------------------------------------------------------------------------------------------------------------- 03
def phone(c):
    b = box("phone", (.26, .2, .1), (0, 0, 0), ink("phone_black", (.02, .02, .02), 0, .25), c, bevel=.02)
    box("handset", (.3, .07, .06), (0, 0, .09), ink("phone_black", BLACK), c, bevel=.02, parent=b); return b

def s03(n):
    """345-521 "Nobody knew whose job that was, so it went to the highway department, because out there, the beach counts as a road."
    0-84 a ringing phone is thrown from desk to desk like a hot potato | 84 it lands on the highway desk (highway 82) | 150 red stamp ROADS | whip to the map (road 165)"""
    import office
    sc = kit.begin(n); Mo = office.build(sc); O = col("L_OBJECTS"); ph = phone(O); Z = .84; D = office.DESKS
    hops = ((0, D[0]), (30, D[0]), (38, D[1]), (70, D[1]), (84, D[2]), (n, D[2]))
    for (f0, x0), (f1, x1) in zip(hops, hops[1:]):
        steps = max(1, f1 - f0)
        for k in range(steps + 1):
            t = k / steps; x = x0 + (x1 - x0) * t; fly = x0 != x1; z = Z + (1.1 * math.sin(math.pi * t) if fly else .03 * abs(math.sin((f0 + k) * 1.9)))      # it rings: it hops on the desk
            ph.location = (x - .35, .55, z); ph.rotation_euler = (0, (t * 6.28 if fly else .12 * math.sin((f0 + k) * 2.3)), 0); key(ph, "location", f0 + k); key(ph, "rotation_euler", f0 + k)
    plq = box("plaque", (.7, .06, .16), (D[2] + .1, .28, .87), ink("brass", (.75, .55, .2), 0, .3), O); label("plq_t", "HIGHWAYS", .1, (0, -.035, 0), (math.radians(90), 0, 0), ink("ink_black", BLACK), parent=plq, extrude=.002)
    stamp = label("stamp", "ROADS", .2, (D[2] + .05, .2, 2.02), (math.radians(90), 0, math.radians(-8)), ink("ink_red_glow", RED, 1.5), extrude=.01)
    for f, v in ((146, 0), (150, 1.5), (154, 1.0)): key(stamp, "scale", f, (v, v, v))
    cam = kit.camera([(0, (-3.6, -3.4, 1.35), (-2.6, .9, 1.2), 30), (34, (-2.2, -3.4, 1.35), (-1.3, .9, 1.25), 30), (78, (.6, -3.3, 1.35), (1.3, .9, 1.25), 30),
                      (100, (2.1, -2.9, 1.4), (2.6, .9, 1.3), 34), (158, (2.2, -2.7, 1.45), (2.7, .9, 1.4), 36), (166, (2.6, -1.6, 1.5), (5.1, .6, 1.6), 30), (n - 1, (3.0, -1.0, 1.55), (5.1, .6, 1.6), 34)], n, amp=.006)
    C = kit.cards(sc, "03", cam, {"clerk_a": [(0, D[0], 1.45, 0)], "clerk_b": [(0, D[1], 1.45, 0)], "clerk_c": [(0, D[2], 1.45, 0)]})
    for f, x in ((38, D[1]), (84, D[2])): signs.impact_lines((x - .35, .5, Z + .02), f, frames=6, n=8, r0=.15, r1=.5)
    signs.sweat_drop(C["clerk_c"], 90, n); signs.scribble(C["clerk_c"], 100, 146)
    for i in range(10):                                                                           # papers fly up at each landing
        f0 = 38 if i < 5 else 84; x = (D[1] if i < 5 else D[2]) + random.Random(i).uniform(-.6, .6); p = box("fly_paper%d" % i, (.21, .3, .003), (x, .6, .8), ink("paper", (.9, .88, .8), 0, .8), O, bevel=0)
        move(p, ((f0, x, .6, .8), (f0 + 10, x + (i % 3 - 1) * .5, .3, 1.9 + .1 * i), (f0 + 40, x + (i % 3 - 1) * .9, -.2 - .1 * i, .02)))
        for f, r in ((f0, 0), (f0 + 40, 5 + i)): key(p, "rotation_euler", f, (r, r * .6, r * .3))
    kit.finish(sc, Mo, ((0, 0.0), (158, 0.0), (167, -1.5)), haze=0); return sc                              # the map wall takes the sun full on: exposure follows the view

# ---------------------------------------------------------------------------------------------------------------- 04
def chalk(name, body, size, at, f, c, pop=5):
    o = label(name, body, size, at, (math.radians(90), 0, 0), ink("chalk", (.92, .92, .88), 1.3), c, extrude=.002)
    for ff, v in ((f - 1, 0), (f + pop, 1.15), (f + pop + 4, 1.0)): key(o, "scale", ff, (v, v, v))
    return o

def s04(n):
    """521-646 "Their plan was simple. Blow it into tiny pieces, and let the seagulls eat the rest."
    the engineer draws on the blackboard: the whale (plan 8), BOOM (blow 38), tiny pieces (53-60), happy seagulls (90); the chalk seagull flies off the board"""
    import office
    sc = kit.begin(n); Mo = office.build(sc, board=True); O = col("L_OBJECTS"); y = 2.0; ch = ink("chalk", (.92, .92, .88), 1.3)
    cu = bpy.data.curves.new("chalk_whale", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = .012; sp = cu.splines.new("BEZIER"); pts = [(-1.15, 1.25), (-.9, 1.5), (-.3, 1.55), (.0, 1.4), (.25, 1.55), (.2, 1.2), (.0, 1.33), (-.4, 1.12), (-.95, 1.1), (-1.15, 1.25)]
    sp.bezier_points.add(len(pts) - 1)
    for q, (x, z) in zip(sp.bezier_points, pts): q.co = (x, y, z); q.handle_left_type = q.handle_right_type = "AUTO"
    wh = bpy.data.objects.new("chalk_whale", cu); O.objects.link(wh); cu.materials.append(ch)
    for f, v in ((2, 0.0), (30, 1.0)): cu.bevel_factor_end = v; cu.keyframe_insert("bevel_factor_end", frame=f)     # the outline appears under the chalk
    chalk("c_boom", "BOOM!", .34, (-.45, y, 1.95), 38, O); chalk("c_arrow", "→", .3, (.5, y, 1.35), 48, O)
    for i in range(9): chalk("c_bit%d" % i, "•", .12 + .03 * (i % 3), (.75 + .14 * (i % 3) + .03 * i, y, 1.15 + .12 * (i // 3) + .04 * (i % 2)), 53 + i, O, 3)
    for i, (x, z) in enumerate(((.75, 1.95), (1.1, 1.8))): chalk("c_gull%d" % i, "v", .3, (x, y, z), 88 + 4 * i, O)
    chalk("c_yum", "YUM", .13, (.95, y, 2.12), 104, O)
    bird = label("chalk_bird", "v", .34, (.4, y, 1.75), (math.radians(90), 0, 0), ch, O, extrude=.004)              # the chalk seagull leaves the board
    for f, v in ((87, 0), (93, 1.0)): key(bird, "scale", f, (v, v, v))
    move(bird, ((93, .4, y, 1.75), (106, .4, y, 1.75), (112, .5, 1.5, 1.9), (n - 1, 1.3, -1.2, 2.3))); 
    for f in range(106, n): key(bird, "scale", f, (1.0, 1.0, 1.0 if f % 6 < 3 else .45))                           # wing beats
    cam = kit.camera([(0, (-1.4, -4.4, 1.5), (-.4, 2.0, 1.5), 32), (50, (-.5, -4.0, 1.5), (-.1, 2.0, 1.55), 32), (86, (.5, -3.4, 1.55), (.4, 2.0, 1.6), 32), (106, (.7, -2.6, 1.65), (.6, 2.0, 1.75), 34), (n - 1, (.9, -3.2, 1.8), (1.2, -1.0, 2.2), 34)], n, amp=.006)
    C = kit.cards(sc, "04", cam, {"engineer": [(0, -1.25, 1.45, 0), (84, -1.25, 1.45, 0)]})
    fx(sc, [{"type": "dust_burst", "name": "chalk_dust", "at": [.4, 1.95, 1.75], "frame": 107, "count": 6, "radius": .35, "height": .3, "seed": 3, "life": 20, "color": [.9, .9, .88]}])
    kit.finish(sc, Mo, haze=0); return sc

# ---------------------------------------------------------------------------------------------------------------- props of the beach shots
ORANGE = (.9, .32, .03)
def truck(c, at, yaw=0.0):
    """the orange highway department dump truck: cab, hood, tilting bed, six wheels. Returns (root, bed); X = forward"""
    root = bpy.data.objects.new("truck", None); c.objects.link(root); root.location = at; root.rotation_euler = (0, 0, yaw)
    paint = ink("truck_orange", ORANGE, 0, .32); dark = ink("truck_dark", (.03, .03, .035), 0, .5); glass = ink("truck_glass", (.05, .09, .12), 0, .08); steel = ink("truck_steel", (.5, .5, .5), 0, .3)
    P = dict(c=c, parent=root)
    box("tr_frame", (6.2, 1.1, .25), (0, 0, .75), dark, **P); box("tr_cab", (1.7, 2.2, 1.7), (1.5, 0, 1.75), paint, bevel=.08, **P); box("tr_hood", (1.3, 2.0, 1.0), (2.9, 0, 1.35), paint, bevel=.08, **P)
    box("tr_wind", (.06, 1.9, .75), (2.36, 0, 2.15), glass, bevel=0, **P); box("tr_grille", (.08, 1.5, .6), (3.56, 0, 1.3), steel, bevel=.01, **P); box("tr_bumper", (.2, 2.3, .22), (3.65, 0, .78), steel, **P)
    for sy in (-1.11, 1.11): box("tr_door_%d" % sy, (1.2, .04, 1.1), (1.5, sy, 1.6), paint, bevel=.02, **P)
    label("tr_txt", "HIGHWAY DEPT", .2, (1.5, -1.14, 1.5), (math.radians(90), 0, 0), ink("ink_black", BLACK), c, parent=root, extrude=.002)
    for x in (2.7, -1.2, -2.3):
        for sy in (-1.05, 1.05):
            cyl("tr_wheel", .52, .42, (x, sy, .52), ink("tyre", (.025, .025, .025), 0, .8), rot=(math.radians(90), 0, 0), seg=28, **P); cyl("tr_hub", .24, .46, (x, sy, .52), steel, rot=(math.radians(90), 0, 0), **P)
    bed = bpy.data.objects.new("truck_bed", None); c.objects.link(bed); bed.parent = root; bed.location = (-2.9, 0, 1.0)            # pivot at the rear
    Q = dict(c=c, parent=bed)
    box("tr_bed_floor", (3.6, 2.3, .12), (1.8, 0, 0), paint, **Q); box("tr_bed_front", (.1, 2.3, 1.0), (3.55, 0, .5), paint, **Q)
    for sy in (-1.13, 1.13): box("tr_bed_side_%d" % sy, (3.6, .08, .8), (1.8, sy, .42), paint, **Q)
    return root, bed

def sticks(c, at, n=20):
    """a small bundle of twenty red sticks tied with string, with its fuse"""
    root = bpy.data.objects.new("bundle", None); c.objects.link(root); root.location = at; red = ink("stick_red", (.72, .05, .04), 0, .55); k = 0
    for ring, cnt, r in ((0, 1, 0), (1, 6, .032), (2, 13, .064)):
        for i in range(cnt):
            a = i / cnt * 6.283; cyl("stick%d" % k, .0155, .24, (r * math.cos(a), r * math.sin(a), 0), red, c, seg=10, parent=root); k += 1
    for z in (-.07, .07): cyl("string", .083, .012, (0, 0, z), ink("string", (.8, .72, .5), 0, .9), c, seg=24, parent=root)
    cyl("fuse", .004, .16, (0, 0, .19), ink("fuse", (.1, .1, .1), 0, .8), c, seg=6, parent=root, rot=(.25, 0, 0)); return root

def marker(c, at, text, yaw=0.0):
    root = bpy.data.objects.new("marker", None); c.objects.link(root); root.location = at; root.rotation_euler = (0, 0, yaw); wood = bpy.data.materials.get("crate_wood") or ink("post_wood", (.4, .28, .16), 0, .7)
    box("mk_post", (.1, .1, 1.5), (0, 0, .75), wood, c, parent=root); b = box("mk_board", (1.3, .05, .5), (0, -.03, 1.4), ink("mk_white", (.92, .9, .84), 0, .6), c, parent=root)
    label("mk_txt", text, .26, (0, -.03, 0), (math.radians(90), 0, 0), ink("ink_black", BLACK), c, parent=b, extrude=.003); return root

CROWD = {"farmer": (-8.2, -8.0), "teacher": (-7.1, -7.6), "bbqdad": (-5.9, -8.2), "veteran": (-4.5, -8.0)}

# ---------------------------------------------------------------------------------------------------------------- 05
def s05(n):
    """646-718 "One guy in the crowd actually knew explosives." slide along the crowd by the truck; a quiet man in an army cap raises one finger (26); heads turn (40-44)"""
    sc = kit.begin(n); c, w, Mo = beach.build(sc, "grey", az=95, el=24); O = col("L_OBJECTS"); truck(O, (-12.5, -4.6, H(-12.5, -4.6)), .3)
    cam = kit.camera([(0, (-9.6, -12.6, 1.55), (-7.6, -8.0, 1.25), 30), (34, (-6.6, -12.0, 1.55), (-5.4, -8.0, 1.3), 34), (n - 1, (-4.9, -10.9, 1.55), (-4.5, -8.0, 1.42), 46)], n)
    C = kit.cards(sc, "05", cam, {k: [(0, x, y)] for k, (x, y) in CROWD.items()}, H)
    kit.finish(sc, Mo); return sc

# ---------------------------------------------------------------------------------------------------------------- 06
def s06(n):
    """718-775 "He told them twenty sticks would do it." insert: his hand holds up a small bundle of twenty sticks (sticks 30); behind him the engineer laughs it away (28)"""
    sc = kit.begin(n); c, w, Mo = beach.build(sc, "grey", az=95, el=24); O = col("L_OBJECTS"); vx, vy = CROWD["veteran"]; z0 = H(vx, vy)
    b = sticks(O, (vx + .16, vy - .2, z0 + 1.12)); b.rotation_euler = (0, .2, 0)
    for f in range(0, n, 4): key(b, "rotation_euler", f, (.05 * math.sin(f * .7), .2 + .06 * math.sin(f * .5), .3 * math.sin(f * .21)))     # the bundle wobbles in his hand
    for f, z in ((0, .92), (10, 1.1), (14, 1.06)): key(b, "location", f, (vx + .16, vy - .2, z0 + z + .06))                                      # he lifts it into view
    tg = box("tag20", (.12, .004, .07), (.1, -.09, .0), ink("tag_card", (.93, .9, .8), 0, .7), O, bevel=0, parent=b); label("tag20_t", "x20", .05, (0, -.004, 0), (math.radians(90), 0, 0), ink("ink_red", RED), O, parent=tg, extrude=.001)
    cam = kit.camera([(0, (-4.7, -10.9, 1.35), (-4.35, -8.0, 1.22), 40), (30, (-4.55, -10.4, 1.3), (-4.35, -8.1, 1.2), 44), (n - 1, (-4.5, -10.2, 1.28), (-4.33, -8.1, 1.18), 46)], n, amp=.005)
    C = kit.cards(sc, "06", cam, {"veteran": [(0, vx, vy)], "engineer": [(0, vx + .95, vy + 1.1)]}, H)
    kit.finish(sc, Mo); return sc

# ---------------------------------------------------------------------------------------------------------------- 07
def s07(n):
    """775-884 "They used twenty cases. So everyone backed up a quarter mile." the orange truck tips its bed: crates slide off and pile up by the whale (cases 33);
    the crowd walks off up the beach past the 1/4 MILE marker (backed 68, mile 94); the camera pulls back and up, no cut"""
    sc = kit.begin(n); c, w, Mo = beach.build(sc, "noon", az=120, el=44); O = col("L_OBJECTS"); R = random.Random(7)
    tr, bed = truck(O, (5.6, -4.4, H(5.6, -4.4)), 0.0)
    for f, a in ((0, 0), (8, 0), (30, -.62), (70, -.62), (95, 0)): key(bed, "rotation_euler", f, (0, a, 0))
    for f in range(8, 34, 5): key(tr, "location", f, (5.6, -4.4, H(5.6, -4.4) + (.03 if (f // 5) % 2 else 0)))                           # the truck rocks on its springs
    land = []
    for i in range(12):                                                                            # the crates leave the bed one after the other and pile up
        o = props.crate("case%02d" % i, O); f0 = 12 + i * 3; x1 = 2.2 - (i % 4) * .95 + R.uniform(-.06, .06); y1 = -3.6 - (i // 4 % 2) * .7; z1 = .25 + (i // 8) * .5
        sx, sy = 4.6 - (i % 3) * .9, -4.4 + (i % 2 - .5) * .9
        for f, p, r in ((0, (sx, sy, 1.5 + .5 * (i // 6)), (0, 0, 0)), (f0, (sx - .6, sy, 1.5 + .5 * (i // 6)), (0, -.3, 0)), (f0 + 7, (x1 + .5, y1, z1 + .8), (0, -1.2, .4)),
                        (f0 + 11, (x1, y1, z1), (0, 0, R.uniform(-.3, .3))), (f0 + 13, (x1, y1, z1 + .07), (0, 0, 0)), (f0 + 15, (x1, y1, z1), (0, 0, 0))):
            o.location = (p[0], p[1], H(p[0], p[1]) + p[2]); key(o, "location", f); key(o, "rotation_euler", f, (r[0], r[1], r[2] if f < f0 + 11 else o.rotation_euler.z))
        land.append((x1, y1, f0 + 11))
    marker(O, (14.0, -24.5, H(14.0, -24.5)), "1/4 MILE", .3)
    cam = kit.camera([(0, (.6, -11.6, 1.3), (2.6, -4.2, 1.4), 24), (20, (.8, -11.4, 1.3), (2.4, -4.0, 1.3), 24), (50, (2.4, -13.0, 2.0), (3.0, -4.5, 1.1), 24),
                      (86, (11.5, -24.0, H(11.5, -24.0) + 2.6), (8.5, -9.0, 1.0), 24), (n - 1, (15.5, -29.0, H(15.5, -29.0) + 3.4), (10.5, -12.0, 1.2), 26)], n)
    for f, d in ((14, .02), (17, -.02), (26, .025), (29, -.02)): key(cam, "delta_location", f, (0, 0, d))                                   # the camera shakes at each crate
    W = ("farmer", "teacher", "bbqdad", "soccermom"); paths = {"worker": [(0, 7.4, -6.6)]}
    for i, k in enumerate(W): x, y = 6.5 + i * 1.1, -8.2 - (i % 2) * .8; paths[k] = [(0, x, y), (52 + 3 * i, x, y), (n, x + 6.5, y - 13.0)]
    C = kit.cards(sc, "07", cam, paths, H)
    fx(sc, [{"type": "dust_burst", "name": "case_puff%d" % i, "at": [x, y, .15], "frame": f, "count": 5, "radius": .5, "height": .35, "seed": 30 + i, "life": 20, "color": [.8, .74, .6]} for i, (x, y, f) in enumerate(land)])
    kit.finish(sc, Mo, ((0, 0.0), (50, 0.0), (90, -.2))); return sc

# ---------------------------------------------------------------------------------------------------------------- the dune top (shots 08-12)
DT = (19.0, -31.0); CAR = (25.5, -34.5); BLUB = (.2, .075, .08)
def dz(x, y, z=0.0): return H(x, y) + z
CLEAR = ((DT[0] + .5, DT[1] - 1.5, 6.5), (CAR[0] - 1.5, CAR[1] - 2.0, 8.0))

def tv_camera(c, at, yaw):
    root = bpy.data.objects.new("tv_camera", None); c.objects.link(root); root.location = at; root.rotation_euler = (0, 0, yaw); dark = ink("tv_dark", (.05, .05, .06), 0, .4); steel = ink("truck_steel", (.5, .5, .5), 0, .3)
    for a in (0, 2.094, 4.189): cyl("tv_leg", .02, 1.5, (.28 * math.cos(a), .28 * math.sin(a), .7), steel, c, rot=(.36 * math.sin(a), -.36 * math.cos(a), 0), seg=8, parent=root)
    box("tv_body", (.6, .28, .34), (0, 0, 1.55), dark, c, parent=root, bevel=.03); cyl("tv_lens", .085, .26, (.42, 0, 1.55), dark, c, rot=(0, math.radians(90), 0), parent=root); cyl("tv_reel1", .13, .06, (-.08, 0, 1.84), dark, c, rot=(math.radians(90), 0, 0), parent=root)
    cyl("tv_reel2", .13, .06, (.2, 0, 1.84), dark, c, rot=(math.radians(90), 0, 0), parent=root); rec = box("tv_rec", (.03, .03, .03), (-.3, -.15, 1.66), ink("rec_red", (1, .02, .02), 6.0), c, parent=root, bevel=0)
    for f in range(0, 60, 8): key(rec, "scale", f, (1, 1, 1) if (f // 8) % 2 == 0 else (.01, .01, .01))                                    # the REC light blinks
    return root

def car(c, at, yaw=0.0, length=4.7):
    """the brand new red car: 'Generic Sedan Car' (Sketchfab, see ASSET_MANIFEST), repainted red, on its wheels at `at`"""
    g = os.path.join(beach.SKILL, "library", "assets", "sketchfab", "58c33766470d46e7b2aed542650494e5", "gltf", "scene.gltf")
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=g); new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new("car", None); c.objects.link(root)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update(); P = [o.matrix_world @ Vector(b) for o in new if o.type == "MESH" for b in o.bound_box]
    lo = Vector([min(p[i] for p in P) for i in range(3)]); hi = Vector([max(p[i] for p in P) for i in range(3)]); d = hi - lo; k = length / max(d.x, d.y)
    inner = bpy.data.objects.new("car_fit", None); c.objects.link(inner); inner.parent = root
    for o in new:
        if o.parent == root: o.parent = inner
    inner.scale = (k, k, k); inner.location = (-(lo.x + hi.x) / 2 * k, -(lo.y + hi.y) / 2 * k, -lo.z * k)
    if d.y > d.x: fit = bpy.data.objects.new("car_turn", None); c.objects.link(fit); fit.parent = root; inner.parent = fit; fit.rotation_euler = (0, 0, math.radians(90))
    area = {}
    for o in new:                                                                                  # the paint is the material that covers the most surface (lesson PI-029: read it on the model)
        if o.type != "MESH": continue
        for p in o.data.polygons:
            m = o.data.materials[p.material_index] if o.data.materials else None
            if m: area[m.name] = area.get(m.name, 0) + p.area
    names = sorted(area, key=lambda n: -area[n]); print("CAR MATERIALS", [(n, round(area[n], 1)) for n in names[:6]])
    for n in names:
        b = bpy.data.materials[n].node_tree.nodes.get("Principled BSDF")
        if b is None or b.inputs["Transmission Weight"].default_value > .3 or b.inputs["Alpha"].default_value < .9: continue
        for l in list(b.inputs["Base Color"].links): bpy.data.materials[n].node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (.62, .015, .02, 1); b.inputs["Metallic"].default_value = 0; b.inputs["Roughness"].default_value = .22; b.inputs["Coat Weight"].default_value = 1.0; break
    root.location = at; root.rotation_euler = (0, 0, yaw); return root

def chunk(c, name, r, seed):
    return blob(name, r, (0, 0, -30), ink("blubber", BLUB, 0, .5), c, seed=seed, squash=(1, 1, .7))

def fall(o, f0, f1, top, land, squash=True):
    """ballistic fall then a SPLAT: it lands on frame f1, flattens in 2 frames and stays (the consequence persists)"""
    for f in range(f0, f1 + 1):
        t = (f - f0) / max(1, f1 - f0); o.location = (top[0] + (land[0] - top[0]) * t, top[1] + (land[1] - top[1]) * t, top[2] + (land[2] - top[2]) * t * t); key(o, "location", f)
    key(o, "rotation_euler", f0, (0, 0, 0)); key(o, "rotation_euler", f1, (3.0, 2.0, 1.0))
    if squash:
        for f, sv in ((f1, (1, 1, 1)), (f1 + 2, (1.5, 1.5, .35)), (f1 + 5, (1.35, 1.35, .45))): key(o, "scale", f, sv)

def dune(sc, mood, az, el, sid, whale_gone=False):
    c, w, Mo = beach.build(sc, mood, az=az, el=el, clear=CLEAR); return c, w, Mo, col("L_OBJECTS")

# ---------------------------------------------------------------------------------------------------------------- 08
def s08(n):
    """884-1000 "A news crew started filming, and boom. For one second, it was beautiful." behind the TV camera (REC blinks), the reporter fixes his tie; push over the tripod
    to the whale far away; BOOM on 52: flash, a column of sand 100 feet high, a mushroom; the crowd cheers (66-80); the camera tilts up with the debris"""
    sc = kit.begin(n); c, w, Mo, O = dune(sc, "noon", 120, 44, "08"); B = 52; x, y = DT
    tv_camera(O, (x + .6, y + .2, dz(x + .6, y + .2)), math.atan2(0 - y, 0 - x))
    sandm = ink("blast_sand", (.62, .52, .36), 0, .9); smoke = ink("blast_smoke", (.16, .14, .13), 0, .95); R = random.Random(8)
    for i in range(22):                                                                            # the column: a stem and a cap that keeps growing, then hangs there
        cap = i >= 10; hgt = (4 + i * 2.6) if not cap else R.uniform(27, 33); rr = R.uniform(2.2, 3.4) if not cap else R.uniform(4.5, 7.5); a = R.uniform(0, 6.283); off = 0 if not cap else R.uniform(2, 7)
        o = blob("col%02d" % i, 1.0, (0, 0, -20), sandm if i % 3 else smoke, col("L_FX"), seed=40 + i, squash=(1, 1, 1), sub=3)
        px, py = off * math.cos(a), off * math.sin(a); t0 = B + (i if not cap else 6 + (i - 10) // 2)
        for f, z, sv in ((t0 - 1, .2, .01), (t0 + 5, hgt * .8, rr * .8), (t0 + 14, hgt, rr), (n + 40, hgt + (5 if cap else 0), rr * (1.35 if cap else 1.05))):
            o.location = (px, py, z); key(o, "location", f); key(o, "scale", f, (sv, sv, sv))
    for i in range(14):                                                                            # pieces thrown high into the sky
        o = chunk(col("L_FX"), "up%02d" % i, R.uniform(.25, .6), 60 + i); a = R.uniform(0, 6.283); r1 = R.uniform(4, 16)
        for f, p in ((B, (0, 0, 1)), (B + 12, (r1 * .5 * math.cos(a), r1 * .5 * math.sin(a), R.uniform(28, 44))), (B + 60, (r1 * math.cos(a), r1 * math.sin(a), R.uniform(70, 120)))): o.location = p; key(o, "location", f)
        key(o, "rotation_euler", B, (0, 0, 0)); key(o, "rotation_euler", n, (9, 6, 3))
    ring = cyl("shock_ring", 1.0, .08, (0, 0, .25), ink("ring_dust", (.62, .54, .40), 0, .95), col("L_FX"), seg=48)                          # ground shock ring
    for f, sv, z in ((B - 1, .01, .01), (B + 1, 4, 1), (B + 8, 20, .5), (B + 14, 30, .05), (B + 16, .01, .01)): key(ring, "scale", f, (sv, sv, z))
    fx(sc, [{"type": "explosion_stylized", "name": "boom", "at": [0, 0, 1.5], "frame": B, "seed": 5, "scale": 6.0}])
    cam = kit.camera([(0, (x + 2.6, y - 3.6, dz(x, y, 1.6)), (x + .4, y + .2, dz(x, y, 1.35)), 30), (30, (x + 2.0, y - 2.9, dz(x, y, 1.65)), (x + .2, y + .4, dz(x, y, 1.4)), 32),
                      (46, (x + .9, y - .6, dz(x, y, 1.9)), (0, 0, 2.0), 55), (B + 6, (x + .9, y - .6, dz(x, y, 1.9)), (0, 0, 6.0), 50), (B + 22, (x + 2.4, y - 4.2, dz(x, y, 1.7)), (8.0, -14.0, 9.0), 26),
                      (98, (x + 2.6, y - 4.6, dz(x, y, 1.6)), (9.0, -16.0, 12.0), 24), (n - 1, (x + 2.6, y - 4.6, dz(x, y, 1.6)), (12.0, -22.0, 45.0), 22)], n)
    for f, d in ((B, 0), (B + 1, .06), (B + 2, -.05), (B + 3, .035), (B + 4, -.025), (B + 6, .012), (B + 8, 0)): key(cam, "delta_location", f, (d, 0, d * .6))   # the blast kicks the camera
    C = kit.cards(sc, "08", cam, {"reporter": [(0, x - .9, y + .3)], "cameraman": [(0, x + 1.45, y + .1)], "farmer": [(0, x - 2.4, y + .9)], "teacher": [(0, x - 3.3, y + .5)]}, H)
    signs.shock_ring(C["reporter"], B + 2)
    kit.finish(sc, Mo, ((0, -.25),)); kit.flash(sc, B, 4, 2.6); return sc

# ---------------------------------------------------------------------------------------------------------------- 09
def s09(n):
    """1000-1049 "Then the sky started falling." straight up: black dots in the blue sky grow fast (sky 12, falling 30); a seagull flees across; the first chunk passes the lens"""
    sc = kit.begin(n); c, w, Mo, O = dune(sc, "noon", 120, 44, "09"); x, y = DT; z = dz(x, y, 1.7); R = random.Random(9)
    for i in range(16):
        o = chunk(col("L_FX"), "dot%02d" % i, R.uniform(.9, 1.8), 80 + i); ox, oy = R.uniform(-7, 7), R.uniform(-9, 9); f0 = R.randint(0, 14)
        for f, p in ((f0, (x + ox * 2.2, y + oy * 2.2, z + R.uniform(90, 140))), (n + R.randint(2, 16), (x + ox, y + oy, z + 3))): o.location = p; key(o, "location", f)
        kit.linear(o); key(o, "rotation_euler", 0, (0, 0, 0)); key(o, "rotation_euler", n, (5, 3, 2))
    first = chunk(col("L_FX"), "first", 1.1, 99)                                                    # the one that wipes the frame
    for f, p in ((6, (x + 1.5, y + 2.0, z + 200)), (n - 6, (x + .3, y + .35, z + 14)), (n - 1, (x, y + .05, z + .5))): first.location = p; key(first, "location", f)
    gull = label("gull", "v", 2.2, (x - 16, y + 6, z + 38), (0, 0, 0), ink("gull_white", (.93, .93, .9), .4), col("L_FX"), extrude=.02)
    move(gull, ((0, x - 16, y + 6, z + 38), (n, x + 18, y - 3, z + 42)))
    for f in range(0, n): key(gull, "scale", f, (1.0, 1.0 if f % 6 < 3 else .4, 1.0))
    cam = kit.camera([(0, (x, y, z), (x + 2.0, y + 6.0, z + 12), 22), (10, (x, y, z), (x + .2, y + .9, z + 30), 20), (n - 1, (x, y, z - .08), (x, y + .4, z + 30), 20)], n, amp=.006)
    kit.finish(sc, Mo, ((0, -.25),)); return sc

# ---------------------------------------------------------------------------------------------------------------- 10
def s10(n):
    """1049-1192 "Chunks of whale three feet wide came down on the crowd, and one of them crushed a brand new car." people run in every direction, chunks slap down
    around them and stay; whip (72-84) to the shiny red car; on "crushed" (102) a three-foot chunk flattens the roof in 4 frames, the glass bursts, the car bounces"""
    sc = kit.begin(n); c, w, Mo, O = dune(sc, "noon", 120, 44, "10"); x, y = DT; R = random.Random(10); K = 102
    cr = car(O, (CAR[0], CAR[1], dz(*CAR)), .5); lands = []
    for i in range(11):
        o = chunk(O, "rain%02d" % i, R.uniform(.2, .34), 110 + i); lx, ly = x + R.uniform(-5, 4), y + R.uniform(-2.5, 3.5); f1 = 6 + i * 6
        fall(o, f1 - 16, f1, (lx + R.uniform(-3, 3), ly + 4, dz(lx, ly) + 60), (lx, ly, dz(lx, ly) + .14)); lands.append((lx, ly, f1))
    big = chunk(O, "big", .45, 150)                                                                 # three feet wide
    fall(big, K - 18, K, (CAR[0] + 2, CAR[1] + 6, dz(*CAR) + 70), (CAR[0], CAR[1], dz(*CAR) + 1.42), squash=False)
    for f, sv in ((K, (1, 1, 1)), (K + 3, (1.15, 1.15, .6)), (n, (1.15, 1.15, .6))): key(big, "scale", f, sv)
    for f, zz in ((K + 3, .78), (K + 6, .86), (K + 9, .8)): key(big, "location", f, (CAR[0], CAR[1], dz(*CAR) + zz))
    for f, sz, z in ((K, 1.0, 0), (K + 3, .52, -.02), (K + 6, .6, .05), (K + 9, .55, 0), (n, .55, 0)):                                       # roof flattened in 4 frames, suspension bounce, stays flat
        key(cr, "scale", f, (1.04 if sz < 1 else 1, 1.06 if sz < 1 else 1, sz)); key(cr, "location", f, (CAR[0], CAR[1], dz(*CAR) + z))
    cam = kit.camera([(0, (x - 4.5, y - 5.5, dz(x, y, 1.4)), (x - 1.0, y + .5, dz(x, y, 1.2)), 24), (40, (x - 1.5, y - 6.0, dz(x, y, 1.4)), (x + .5, y + .5, dz(x, y, 1.1)), 24),
                      (72, (x + 1.5, y - 6.2, dz(x, y, 1.4)), (x + 2.5, y + .2, dz(x, y, 1.1)), 24), (84, (CAR[0] - 3.6, CAR[1] - 4.6, dz(CAR[0] - 3.6, CAR[1] - 4.6) + 1.5), (CAR[0], CAR[1], dz(*CAR) + .8), 28),
                      (K - 2, (CAR[0] - 3.3, CAR[1] - 4.2, dz(CAR[0] - 3.3, CAR[1] - 4.2) + 1.4), (CAR[0], CAR[1], dz(*CAR) + .8), 28), (n - 1, (CAR[0] - 2.9, CAR[1] - 3.8, dz(CAR[0] - 2.9, CAR[1] - 3.8) + 1.2), (CAR[0], CAR[1], dz(*CAR) + .6), 30)], n, amp=.014, rot=.3)
    for f, d in ((K, 0), (K + 1, .07), (K + 2, -.05), (K + 3, .03), (K + 5, -.02), (K + 8, 0)): key(cam, "delta_location", f, (0, 0, d))
    C = kit.cards(sc, "10", cam, {"farmer": [(0, x - 6.5, y + .8), (80, x + 7.5, y - .6)], "teacher": [(0, x + 5.0, y + 1.8), (80, x - 8.0, y + 2.6)],
                                   "soccermom": [(0, x - 9.0, y - .8), (90, x + 6.0, y - 1.6)], "bbqdad": [(0, x - .6, y + 1.2)]}, H)
    signs.sweat_drop(C["farmer"], 4, 80); signs.spiral_eyes(C["bbqdad"], 34, 90); signs.impact_lines((CAR[0], CAR[1] - 1.2, dz(*CAR) + .05), K, frames=8, n=12, r0=.8, r1=2.4)
    fx(sc, [{"type": "dust_burst", "name": "splat%d" % i, "at": [lx, ly, dz(lx, ly) + .1], "frame": f, "count": 6, "radius": .7, "height": .4, "seed": 50 + i, "life": 22, "color": [.8, .74, .6]} for i, (lx, ly, f) in enumerate(lands)]
           + [{"type": "dust_burst", "name": "glass", "at": [CAR[0], CAR[1], dz(*CAR) + 1.0], "frame": K, "count": 16, "radius": 2.2, "height": 1.0, "seed": 77, "life": 26, "color": [.86, .9, .92]}])
    kit.finish(sc, Mo, ((0, -.2),)); return sc

# ---------------------------------------------------------------------------------------------------------------- 11
def wreck(O):
    cr = car(O, (CAR[0], CAR[1], dz(*CAR)), .5); cr.scale = (1.04, 1.06, .55); big = chunk(O, "big", .45, 150); big.location = (CAR[0], CAR[1], dz(*CAR) + .8); big.scale = (1.15, 1.15, .6)
    for i in range(5): o = chunk(O, "left%02d" % i, .2 + .03 * i, 110 + i); a = .3 + i * .6; o.location = (CAR[0] + 3.2 * math.cos(a), CAR[1] + 2.6 * math.sin(a), dz(CAR[0] + 3.2 * math.cos(a), CAR[1] + 2.6 * math.sin(a)) + .14); o.scale = (1.35, 1.35, .45)
    return cr
VET = (CAR[0] - 2.6, CAR[1] - 1.4)

def s11(n):
    """1192-1234 "Guess whose car it was." the keys slip from a hand and fall in the sand in front of the wreck (10), a puff; slow pan left and up: a pair of boots, then their owner"""
    sc = kit.begin(n); c, w, Mo, O = dune(sc, "noon", 120, 44, "11"); wreck(O); kx, ky = VET[0] + .35, VET[1] - .35; g = dz(kx, ky)
    keys = bpy.data.objects.new("keys", None); O.objects.link(keys); st = ink("truck_steel", (.5, .5, .5), 0, .3)
    cu = bpy.data.curves.new("key_ring", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = .004; sp = cu.splines.new("POLY"); sp.points.add(23); sp.use_cyclic_u = True
    for i, p in enumerate(sp.points): p.co = (.032 * math.cos(i * .2618), .032 * math.sin(i * .2618), 0, 1)
    kr = bpy.data.objects.new("key_ring", cu); O.objects.link(kr); kr.parent = keys; cu.materials.append(st)
    box("key_a", (.014, .075, .004), (.03, -.065, 0), st, O, bevel=0, parent=keys); box("key_a_teeth", (.012, .03, .004), (.04, -.085, 0), st, O, bevel=0, parent=keys); box("key_b", (.012, .06, .004), (.0, -.06, 0), st, O, bevel=0, parent=keys); box("key_fob", (.035, .05, .008), (-.035, -.055, 0), ink("fob_red", RED, 0, .4), O, bevel=.002, parent=keys); keys.scale = (2.6, 2.6, 2.6)   # drawn large: readable on a phone
    for f, zz, r in ((0, 1.0, 0), (9, .02, 5), (12, .09, 6), (15, .02, 6.6)): key(keys, "location", f, (kx, ky, g + zz)); key(keys, "rotation_euler", f, (r * .3, r * .2, r))
    cam = kit.camera([(0, (kx + .2, ky - 1.5, g + .6), (kx, ky, g + .3), 35), (16, (kx + .1, ky - 1.4, g + .5), (kx - .02, ky + .05, g + .08), 38),
                      (30, (VET[0] + .1, VET[1] - 2.4, g + .9), (VET[0], VET[1], g + .7), 38), (n - 1, (VET[0], VET[1] - 2.6, g + 1.45), (VET[0], VET[1], g + 1.42), 40)], n, amp=.005)
    kit.cards(sc, "11", cam, {"veteran": [(0, VET[0], VET[1])]}, H)
    fx(sc, [{"type": "dust_burst", "name": "keys_puff", "at": [kx, ky, g + .05], "frame": 9, "count": 4, "radius": .1, "height": .06, "seed": 3, "life": 10, "color": [.7, .62, .46]}])
    kit.finish(sc, Mo, ((0, -.2),)); return sc

# ---------------------------------------------------------------------------------------------------------------- 12
def s12(n):
    """1234-1319 "The guy who said twenty sticks. And the seagulls?" the veteran, deadpan, the bundle still under his arm; a bit of blubber slides off his cap (20-60);
    slow push on his face; whip pan to the ocean on the last frames"""
    sc = kit.begin(n); c, w, Mo, O = dune(sc, "noon", 120, 44, "12"); wreck(O); g = dz(*VET)
    cam = kit.camera([(0, (VET[0], VET[1] - 2.6, g + 1.45), (VET[0], VET[1], g + 1.42), 40), (60, (VET[0] + .1, VET[1] - 2.0, g + 1.47), (VET[0], VET[1], g + 1.45), 52),
                      (n - 5, (VET[0] + .1, VET[1] - 1.9, g + 1.47), (VET[0], VET[1], g + 1.46), 56), (n - 1, (VET[0] + .1, VET[1] - 1.9, g + 1.5), (VET[0] - 14, VET[1] + 30, g + 2), 40)], n, amp=.005)
    C = kit.cards(sc, "12", cam, {"veteran": [(0, VET[0], VET[1])]}, H)
    b = sticks(O, (VET[0] + .34, VET[1] - .15, g + .98)); b.rotation_euler = (0, 1.2, .3)
    bit = chunk(O, "cap_bit", .07, 3)
    for f, p in ((0, (-.1, -.06, 1.72)), (20, (-.1, -.06, 1.72)), (56, (-.26, -.07, 1.55)), (62, (-.3, -.08, 1.2)), (68, (-.32, -.1, .04))): key(bit, "location", f, (VET[0] + p[0], VET[1] + p[1], g + p[2]))
    key(bit, "scale", 67, (1, 1, .7)); key(bit, "scale", 69, (1.5, 1.5, .3)); signs.sweat_drop(C["veteran"], 30, n - 6, side=1)
    kit.finish(sc, Mo, ((0, -.2),)); return sc

# ---------------------------------------------------------------------------------------------------------------- after the blast (shots 13-16)
def crater(O, at=(0.6, -3.4), r=3.2):
    """what the blast left: a ring of thrown sand around a dark hollow, and pieces lying about (they stay until the end)"""
    sand = bpy.data.materials["beach_sand"]; R = random.Random(13)
    for i in range(16):
        a = i / 16 * 6.283; x, y = at[0] + r * math.cos(a), at[1] + r * .8 * math.sin(a); o = blob("rim%02d" % i, R.uniform(.7, 1.1), (x, y, H(x, y) - .05), sand, O, seed=200 + i, squash=(1, 1, .35), sub=2)
    blob("hollow", 1.0, (at[0], at[1], H(*at) + .02), ink("scorch", (.07, .06, .05), 0, .95), O, seed=5, squash=(r * .8, r * .62, .03), sub=3)
    for i in range(9):
        a = R.uniform(0, 6.283); d = R.uniform(4, 9); x, y = at[0] + d * math.cos(a), at[1] - abs(d * math.sin(a)) * .8; o = chunk(O, "lying%02d" % i, R.uniform(.25, .45), 300 + i); o.location = (x, y, H(x, y) + .12); o.scale = (1.35, 1.35, .45)

def sign(O, at, lines, yaw=0.0):
    """the state park sign; returns (root, [word objects])"""
    root = bpy.data.objects.new("rule_sign", None); O.objects.link(root); root.location = at; root.rotation_euler = (0, 0, yaw); wood = ink("sign_post", (.3, .2, .12), 0, .7)
    for sx in (-.75, .75): box("sg_post", (.1, .1, 2.1), (sx, 0, 1.05), wood, O, parent=root)
    box("sg_board", (1.9, .06, 1.15), (0, -.05, 1.6), ink("sign_brown", (.22, .12, .05), 0, .6), O, parent=root); box("sg_head", (1.9, .065, .26), (0, -.052, 2.04), ink("sign_yellow_p", (.9, .68, .08), 0, .5), O, parent=root, bevel=.005)
    label("sg_h", "OREGON STATE PARKS", .11, (0, -.09, 2.04), (math.radians(90), 0, 0), ink("ink_black", BLACK), O, parent=root, extrude=.002); words = []
    for li, line in enumerate(lines):
        ws = line.split(); wd = [len(wv) * .088 + .06 for wv in ws]; x = -sum(wd) / 2
        for wv, d in zip(ws, wd):
            m = bpy.data.materials.new("sg_word_%d" % len(words)); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (.93, .9, .8, 1); b.inputs["Emission Color"].default_value = (1, .86, .35, 1)
            o = label("sg_w%d" % len(words), wv, .135, (x + d / 2, -.09, 1.78 - li * .27), (math.radians(90), 0, 0), m, O, parent=root, extrude=.003); words.append((o, b)); x += d
    return root, words

def flock(n, f0, start, end, count=13, seed=3):
    """seagulls: flat white V shapes that beat their wings and fly away over the sea"""
    R = random.Random(seed); out = []; white = ink("gull_white", (.93, .93, .9), .25)
    for i in range(count):
        o = label("gull%02d" % i, "v", R.uniform(1.3, 2.0), (0, 0, 0), (math.radians(75), 0, 0), white, col("L_FX"), extrude=.01); dx, dz_, d0 = R.uniform(-6, 6), R.uniform(-1.5, 2.5), R.randint(0, 10)
        move(o, ((f0 + d0, start[0] + dx, start[1] + R.uniform(-2, 2), start[2] + dz_), (n + 10, end[0] + dx * 4, end[1], end[2] + dz_ * 3))); kit.linear(o)
        for f in range(f0, n): key(o, "scale", f, (1.0, 1.0 if (f + i * 2) % 6 < 3 else .35, 1.0))
        out.append(o)
    cs = box("suitcase", (.22, .08, .15), (0, 0, -.3), ink("case_brown", (.35, .2, .1), 0, .5), col("L_FX"), parent=out[-1]); return out

def after(sc, mood, az, el, clear=()):
    c, w, Mo = beach.build(sc, mood, az=az, el=el, clear=clear); O = col("L_OBJECTS"); crater(O); w.scale = tuple(v * .93 for v in w.scale); return c, w, Mo, O

def s13(n):
    """1319-1389 "The blast scared every single one away." the whole flock flies off over the sea (away 54); the last one carries a tiny suitcase; the camera follows, then drops to the beach"""
    sc = kit.begin(n); c, w, Mo, O = after(sc, "gold", -115, 14); flock(n, 0, (0, -2, 5.0), (4, 110, 22))
    cam = kit.camera([(0, (-1.0, -19.0, 2.6), (0, 6, 6.0), 36), (40, (-.6, -18.0, 2.5), (1.5, 40, 12.0), 40), (56, (-.4, -17.0, 2.4), (2.0, 60, 13.0), 40), (n - 1, (-3.0, -14.5, 2.1), (-1.0, -3.0, 1.2), 28)], n)
    for i in range(6):                                                                             # feathers drift down
        f = box("feather%d" % i, (.16, .04, .004), (0, 0, 0), ink("gull_white", (.93, .93, .9)), col("L_FX"), bevel=0); x = -2 + i * .9
        move(f, ((4 + i * 5, x, -6 - i, 7.0), (n + 20, x + 1.5, -9 - i, .1)))
        for ff in range(0, n, 6): key(f, "rotation_euler", ff, (math.sin(ff * .3 + i), ff * .12, math.cos(ff * .2 + i)))
    kit.finish(sc, Mo, ((0, -.35),)); return sc

def s14(n):
    """1389-1483 "Most of the whale was still lying there, so they buried it anyway." the smoke clears: a crater, and the whale exactly where it was (still 25); the engineer
    shrugs; a bulldozer pushes a wave of sand over it (buried 61); the sand thrown by the blade covers the lens"""
    sc = kit.begin(n); c, w, Mo, O = after(sc, "gold", -115, 14)
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(kit.EP, "build", "assets", "crawler_dozer.glb")); new = [o for o in bpy.data.objects if o not in before]
    dz_root = bpy.data.objects.new("dozer", None); O.objects.link(dz_root)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        O.objects.link(o)
        if o.parent is None: o.parent = dz_root
        for m in (o.data.materials if o.type == "MESH" else ()):
            b = m.node_tree.nodes.get("Principled BSDF") if m and m.node_tree else None
            if b and m.name.startswith("paint"): b.inputs["Base Color"].default_value = (.85, .55, .04, 1)          # highway yellow
    dy = -4.6
    for f, x in ((0, -19.0), (40, -15.5), (n - 1, -10.2)): key(dz_root, "location", f, (x, dy, H(x, dy)))
    kit.linear(dz_root); sand = bpy.data.materials["beach_sand"]
    for i in range(7):                                                                             # the sand rolls in front of the blade and grows
        m = blob("push%d" % i, 1.0, (0, 0, 0), sand, O, seed=400 + i, squash=(1, 1, .6), sub=2); oy = dy + (i - 3) * .55
        for f, x, sv in ((0, -16.9, .3), (40, -13.4, .7), (n - 1, -8.0, 1.25)): key(m, "location", f, (x, oy, H(x, oy) + .1)); key(m, "scale", f, (sv, sv, sv))
        kit.linear(m)
    wave = blob("sand_wave", 1.0, (0, 0, -20), sand, col("L_FX"), seed=9, squash=(1, 1, 1), sub=3)   # thrown sand that covers the lens: the wipe
    for f, p, sv in ((n - 12, (-9.2, dy, .6), .3), (n - 5, (-10.0, -6.6, 1.2), 1.0), (n - 1, (-10.2, -6.7, 1.2), 1.05)): key(wave, "location", f, p); key(wave, "scale", f, (sv, sv, sv))
    cam = kit.camera([(0, (-5.0, -13.5, 2.1), (.5, -2.5, 1.0), 26), (34, (-7.0, -12.0, 1.9), (-1.0, -2.5, 1.0), 26), (62, (-10.8, -8.6, 1.4), (-11.5, -4.6, 1.0), 28), (n - 1, (-10.5, -7.9, 1.25), (-9.5, -4.6, .9), 28)], n)
    C = kit.cards(sc, "14", cam, {"engineer": [(0, -3.6, -6.2)], "worker": [(0, -19.6, dy, H(-19.6, dy) + 1.0), (40, -16.1, dy, H(-16.1, dy) + 1.0), (n - 1, -10.8, dy, H(-10.8, dy) + 1.0)]}, H)
    fx(sc, [{"type": "smoke", "name": "after_smoke", "at": [.6, -3.4, .6], "frame": -20, "count": 9, "seed": 4, "life": 70, "color": [.2, .18, .17], "size": 1.6, "rise": 3.0, "spread": 2.2},
            {"type": "dust_burst", "name": "blade_dust", "at": [-12.0, dy, .3], "frame": 44, "count": 8, "radius": 1.2, "height": .6, "seed": 6, "life": 30, "color": [.8, .74, .6]}])
    signs.scribble(C["engineer"], 24, 60)
    kit.finish(sc, Mo, ((0, -.35),)); return sc

SIGN = (-3.0, -8.2); LINES = ("DEAD WHALES:", "BURY THEM", "WHERE THEY LAND")
def s15(n):
    """1483-1554 "Today, Oregon has one rule for dead whales." the same beach today, clean and empty; a ranger hammers a state park sign into the sand: it shivers at each blow"""
    sc = kit.begin(n); c, w, Mo = beach.build(sc, "today", az=120, el=40); O = col("L_OBJECTS"); w.location.z = -60                             # today: no whale
    root, words = sign(O, (SIGN[0], SIGN[1], H(*SIGN)), LINES)
    for f in range(0, n, 12):                                                                      # a hammer blow every 12 frames
        for ff, r, z in ((f + 5, 0, .12 - f * .0012), (f + 6, .035, .1 - f * .0012), (f + 8, -.02, .1 - f * .0012), (f + 10, 0, .1 - f * .0012)): key(root, "rotation_euler", ff, (0, r, 0)); key(root, "location", ff, (SIGN[0], SIGN[1], H(*SIGN) + z))
    cam = kit.camera([(0, (-5.8, -13.4, 1.6), (-3.4, -8.0, 1.4), 28), (n - 1, (-3.5, -12.4, 1.6), (-3.1, -8.2, 1.55), 34)], n)
    kit.cards(sc, "15", cam, {"ranger": [(0, SIGN[0] - 1.35, SIGN[1] - .1)]}, H)
    fx(sc, [{"type": "dust_burst", "name": "hammer_puff%d" % i, "at": [SIGN[0] - .75, SIGN[1], H(*SIGN) + .05], "frame": f + 6, "count": 4, "radius": .3, "height": .2, "seed": i, "life": 14, "color": [.8, .74, .6]} for i, f in enumerate(range(0, n - 8, 12))])
    kit.finish(sc, Mo); return sc

def s16(n):
    """1554-1680 "Bury them where they land. And the engineer? He said it went exactly right." the words of the sign light up as they are said (0-34); whip (50-56) back to 1970:
    the engineer by the crater, covered in blubber, still holding the plunger, gives a proud thumbs up (78; right 105); a chunk slides off his hard hat. Loops to the first image"""
    sc = kit.begin(n); c, w, Mo, O = after(sc, "gold", -115, 14); root, words = sign(O, (SIGN[0], SIGN[1], H(*SIGN)), LINES); EN = (5.2, -7.2); g = H(*EN)
    for (o, b), f in zip(words[2:], (0, 18, 23, 29, 34)):                                          # BURY THEM WHERE THEY LAND, one word per spoken word
        for ff, v in ((f - 1, 0.0), (f + 2, 6.0), (f + 10, 2.5)): b.inputs["Emission Strength"].default_value = v; b.inputs["Emission Strength"].keyframe_insert("default_value", frame=ff)
        for ff, sv in ((f - 1, 1), (f + 2, 1.25), (f + 6, 1)): key(o, "scale", ff, (sv, sv, sv))
    boxp, handle = props.plunger(O, (EN[0] + .3, EN[1] - .2, g))
    cam = kit.camera([(0, (-3.5, -12.4, 1.6), (-3.1, -8.2, 1.55), 34), (48, (-3.2, -11.6, 1.6), (-3.0, -8.2, 1.6), 38), (57, (4.6, -11.4, 1.45), (EN[0], EN[1], g + 1.2), 32),
                      (100, (4.9, -10.6, 1.4), (EN[0], EN[1], g + 1.25), 36), (n - 1, (5.3, -9.6, 1.2), (EN[0] + .3, EN[1] - .2, g + .55), 45)], n)
    C = kit.cards(sc, "16", cam, {"engineer": [(0, EN[0], EN[1])]}, H); e = C["engineer"]
    for i, (px, pz) in enumerate(((-.2, 1.72), (.24, 1.2), (-.3, .9), (.1, .5))):                    # covered in blubber: bits stuck on him (parented to the card)
        bt = chunk(O, "stuck%d" % i, .06 + .015 * i, 500 + i); bt.parent = e; bt.location = (px, -.06, pz); bt.scale = (1.3, .5, 1.0)
        if i == 0:
            for f, p in ((0, (px, -.06, pz)), (84, (px, -.06, pz)), (104, (px - .22, -.07, 1.5)), (112, (px - .3, -.08, .05))): key(bt, "location", f, p)
    signs.impact_lines((EN[0] + .35, EN[1] - .1, g + 1.3), 82, frames=8, n=8, r0=.15, r1=.45, color=(.95, .8, .1))
    kit.finish(sc, Mo, ((0, -.3),)); return sc

SHOTS = {"02": s02, "03": s03, "04": s04, "05": s05, "06": s06, "07": s07, "08": s08, "09": s09, "10": s10, "11": s11, "12": s12, "13": s13, "14": s14, "15": s15, "16": s16}
if "13" not in cast.SHOTS: cast.SHOTS.update({"09": (49, {}, []), "13": (70, {}, [])})




if __name__ == "__main__":
    sid = kit.A[0]; sc = SHOTS[sid](cast.SHOTS[sid][0]); kit.output(sc, kit.A[1])
