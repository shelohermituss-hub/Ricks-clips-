"""THE GHOST ARMY — the sonic deception half-track (body only), custom Blender model (V3, 2026-11-18).
A generic 1940s half-track carrying a loudspeaker rig. NO weapon, no mount: it is a sound truck. The giant horn, the turntable,
the disc and the cable stay in sets/ghost.js (they are animated and drive the sound-wave rings).
Front wheels with treaded tyres, armoured radiator shutters, hood with side panels, bumper and winch, headlights in brush guards,
curved front fenders, an open cab with armoured sides, windshield armour with vision slits and glass, steering wheel, seats;
rear bed with armoured sides, stowage racks, jerry cans, rear door; rubber band tracks with chevron cleats on two bogies,
front sprocket and rear idler, mud guards.
    blender -b --python build_sound_halftrack.py -- <out_dir>      ->  <out_dir>/sound_halftrack.glb
Axes: X forward (bumper at +2.6), Y width, Z up. Footprint and heights match the old box version, so the horn rig sits where it did."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _blender_kit import *
OUT = sys.argv[sys.argv.index("--") + 1]
reset()
for n, c, r, m in (("paint", "#4d5634", .62, .3), ("paint_dark", "#3e452a", .7, .3), ("steel_dark", "#2e302a", .5, .8), ("rubber", "#1c1c1c", .9, 0),
                   ("glass", "#8fa2b0", .12, 0), ("chrome", "#c8c8c0", .25, 1), ("canvas", "#6e6a4c", .9, 0), ("wood", "#7a6444", .8, 0)):
    mat(n, c, r, m)
R = root("sound_halftrack")
P, PD, D, RB = bm_for("paint"), bm_for("paint_dark"), bm_for("steel_dark"), bm_for("rubber")
# chassis rails and cross members
for s in (-.45, .45): box(D, (0, s, .62), (5.0, .12, .18))
for x in (-2.0, -.6, .8, 2.0): box(D, (x, 0, .62), (.12, 1.0, .12))
# front axle, wheels with treaded tyres and hubs
box(D, (1.7, 0, .48), (.14, 1.8, .14))
for s in (-1, 1):
    y = s * .95; cyl(RB, (1.7, y, .48), (0, 1, 0), .48, .3, 32)
    for k in range(22):
        a = 2 * math.pi * k / 22; box(RB, (1.7 + .48 * math.cos(a), y, .48 + .48 * math.sin(a)), (.07, .3, .05), Matrix.Rotation(-a, 3, "Y"))   # tread blocks
    cyl(D, (1.7, y + s * .155, .48), (0, 1, 0), .28, .03, 24); cyl(D, (1.7, y + s * .175, .48), (0, 1, 0), .1, .05, 16)
    for k in range(8): cyl(D, (1.7 + .19 * math.cos(k * math.pi / 4), y + s * .18, .48 + .19 * math.sin(k * math.pi / 4)), (0, 1, 0), .02, .03, 6)
    # curved front fender
    prism(P, [(1.05, .98), (1.3, 1.12), (1.75, 1.18), (2.2, 1.1), (2.42, .92), (2.36, .9), (2.16, 1.06), (1.75, 1.13), (1.32, 1.07), (1.1, .94)], y - .28, y + .28)
# hood with side panels and hinges, radiator armour with shutters, bumper, winch
prism(P, [(.9, .95), (2.3, .95), (2.3, 1.48), (.95, 1.62)], -.78, .78)
for s in (-1, 1):
    for k in range(5): box(PD, (1.2 + k * .22, s * .785, 1.22), (.12, .01, .38))                                      # side panels (louvres)
    box(D, (1.6, s * .79, 1.55), (1.3, .02, .03))                                                                     # hinge line
box(PD, (2.33, 0, 1.2), (.06, 1.5, .55))
for k in range(9): box(D, (2.37, -.64 + k * .16, 1.2), (.03, .1, .5), Matrix.Rotation(.35, 3, "Z"))                   # armoured shutters
box(D, (2.62, 0, .82), (.18, 2.2, .22))                                                                                # bumper
cyl(D, (2.55, 0, .98), (0, 1, 0), .16, 1.2, 20); cyl(bm_for("steel_dark"), (2.55, 0, .98), (0, 1, 0), .17, .1, 20)   # winch drum
for s in (-1, 1):                                                                                                       # headlights in brush guards
    cyl(bm_for("chrome"), (2.12, s * .92, 1.3), (1, 0, 0), .11, .16, 18); cyl(bm_for("glass"), (2.21, s * .92, 1.3), (1, 0, 0), .095, .02, 18)   # on the fenders
    for dz in (-.1, .1): tube_path(D, [(2.04, s * .8, 1.3 + dz), (2.3, s * .92, 1.3 + dz), (2.04, s * 1.04, 1.3 + dz)], .012, 6)              # brush guard hoops
# open cab: armoured sides with door cut, windshield armour with vision slits and glass, steering wheel, seats
for s in (-1, 1):
    prism(P, [(-.05, .95), (.95, .95), (.95, 1.55), (.6, 1.55), (.6, 1.3), (.15, 1.3), (.15, 1.75), (-.05, 1.75)], s * 1.0 - .025, s * 1.0 + .025)
box(P, (.95, 0, 1.95), (.04, 1.95, .55))                                                                               # windshield armour (raised)
for s in (-.45, .45): box(bm_for("glass"), (.97, s, 1.98), (.01, .7, .3)); box(D, (.98, s, 2.12), (.02, .4, .04))   # glass + vision slit
cyl(D, (.55, .38, 1.65), (.6, 0, .8), .2, .03, 24); tube_path(D, [(.55, .38, 1.65), (.85, .38, 1.25)], .025, 8)        # steering wheel + column
for s in (-.38, .38): box(bm_for("canvas"), (.25, s, 1.25), (.45, .45, .1)); box(bm_for("canvas"), (.05, s, 1.5), (.08, .45, .45))
# rear bed: floor, armoured sides with stowage racks and jerry cans, rear door, track mud guards
box(P, (-1.0, 0, 1.0), (3.2, 2.0, .1))
for s in (-1, 1):
    box(P, (-1.0, s * 1.05, 1.5), (3.2, .05, 1.0))
    for k in range(4): box(D, (-2.3 + k * .85, s * 1.1, 1.75), (.05, .05, .5))                                         # rack uprights
    box(D, (-1.0, s * 1.1, 1.98), (2.6, .04, .04))
    for k in range(3): box(PD, (-2.1 + k * .5, s * 1.18, 1.45), (.35, .14, .5)); box(D, (-2.1 + k * .5, s * 1.18, 1.73), (.06, .1, .06))   # jerry cans + handles
    prism(PD, [(-2.6, 1.0), (.55, 1.0), (.7, .9), (.62, .86), (.5, .94), (-2.55, .94)], s * .9 - .3, s * .9 + .3)       # mud guard over the track
box(P, (-2.62, 0, 1.45), (.05, 1.4, .9)); box(D, (-2.65, 0, 1.45), (.02, .05, .7))                                     # rear door + hinge
for s in (-.5, .5): cyl(D, (-2.66, s, 1.6), (1, 0, 0), .04, .04, 10)
# rubber band tracks with chevron cleats on two bogies, sprocket front, idler rear
L, r0, zc = 2.3, .3, .42
def band(u):
    st = L; arc = math.pi * r0; tot = 2 * st + 2 * arc; s = u * tot
    if s < st: return Vector((-1.0 - L / 2 + s, 0, zc + r0)), 0.0
    s -= st
    if s < arc: a = math.pi / 2 - s / r0; return Vector((-1.0 + L / 2 + r0 * math.cos(a), 0, zc + r0 * math.sin(a))), a - math.pi / 2
    s -= arc
    if s < st: return Vector((-1.0 + L / 2 - s, 0, zc - r0)), math.pi
    s -= st; a = -math.pi / 2 - s / r0; return Vector((-1.0 - L / 2 + r0 * math.cos(a), 0, zc + r0 * math.sin(a))), a - math.pi / 2
for s in (-1, 1):
    y = s * .9
    for i in range(48):
        p, ang = band(i / 48); rot = Matrix.Rotation(-ang, 3, "Y")
        box(RB, p + Vector((0, y, 0)) + rot @ Vector((0, 0, .015)), (.16, .36, .03), rot)
        for side in (-1, 1): box(RB, p + Vector((0, y + side * .08, 0)) + rot @ Vector((0, 0, .045)), (.03, .14, .03), rot @ Matrix.Rotation(side * .5, 3, "Z"))   # chevron cleat
    cyl(D, (-1.0 + L / 2, y, zc), (0, 1, 0), r0 - .04, .3, 12)                                                         # drive sprocket
    for k in range(12): a = 2 * math.pi * k / 12; box(D, (-1.0 + L / 2 + (r0 - .04) * math.cos(a), y, zc + (r0 - .04) * math.sin(a)), (.05, .08, .06), Matrix.Rotation(-a, 3, "Y"))
    cyl(D, (-1.0 - L / 2, y, zc), (0, 1, 0), r0 - .03, .3, 24)                                                         # rear idler
    for k in range(4): cyl(D, (-1.75 + k * .5, y, .2), (0, 1, 0), .18, .26, 20)                                        # road wheels
    for b in (-1.5, -.5): box(PD, (b, y, .32), (.85, .12, .18)); cyl(D, (b, y, .35), (0, 1, 0), .06, .3, 10)          # two bogies and their pivots
finish(R, bevel_mats=("paint", "paint_dark"), bevel=.025, smooth_mats=("rubber", "chrome"))
export(os.path.join(OUT, "sound_halftrack.glb"))
