"""THE GHOST ARMY — signals and photo-interpretation props, custom Blender models (V3, 2026-11-18).
  field_radio.glb  : a 1940s field transmitter-receiver (generic, no brand): steel cabinet with rounded edges, front panel with two
                     round meters under glass, a big tuning window with a scale, eight bakelite knobs, toggle switches, jack sockets,
                     side carrying handles, louvred side vents, cable connectors and a coiled cord, a nameplate.
  morse_key.glb    : a straight Morse key: wooden base, brass trunnion frame, lever arm on its pivot ('key_lever', animated by
                     sets/ghost.js), black knob, contact points, tension spring, binding posts.
  light_table.glb  : a photo-interpretation light table: wooden frame and legs with braces, a frosted top ('table_glass',
                     glows), a lamp box under the top, two drawers with pulls, a pocket stereoscope, a pencil tray.
    blender -b --python build_signals_props.py -- <out_dir>
Axes: X forward (towards the viewer of the front panel = +X), Y width, Z up, each prop standing on Z = 0 at its own origin."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _blender_kit import *
import bpy
OUT = sys.argv[sys.argv.index("--") + 1]

def materials():
    for n, c, r, m in (("case", "#4d5634", .55, .4), ("panel", "#2c2e2a", .5, .3), ("bakelite", "#1a1614", .35, 0), ("chrome", "#c8c8c0", .25, 1),
                       ("glass", "#d8e4e8", .08, 0), ("dial", "#e8e0c8", .7, 0), ("brass", "#c8a24a", .3, 1), ("wood", "#5a3a26", .6, 0),
                       ("wood_light", "#8a6a44", .65, 0), ("table_glass", "#e8eef4", .5, 0), ("metal_dark", "#3a3a36", .5, .8), ("rubber", "#151515", .8, 0)):
        mat(n, c, r, m)

# ------------------------------------------------ field radio: 0.9 (y) x 0.5 (x, depth) x 0.6 (z)
reset(); materials(); R = root("field_radio")
C, PN, BK, CH = bm_for("case"), bm_for("panel"), bm_for("bakelite"), bm_for("chrome")
box(C, (0, 0, .3), (.5, .9, .6))
box(PN, (.252, 0, .3), (.01, .84, .54))                                                       # front panel
for y in (-.25, .25):                                                                          # two meters under glass
    cyl(CH, (.26, y, .45), (1, 0, 0), .085, .02, 32); cyl(bm_for("dial"), (.268, y, .45), (1, 0, 0), .072, .004, 32); cyl(bm_for("glass"), (.272, y, .45), (1, 0, 0), .074, .004, 32)
    box(BK, (.271, y + .02, .46), (.002, .004, .06), Matrix.Rotation(.6, 3, "X"))             # needle
box(CH, (.26, 0, .3), (.012, .36, .1)); box(bm_for("dial"), (.266, 0, .3), (.004, .33, .075))  # tuning window + scale
for k in range(15): box(BK, (.27, -.15 + k * .0214, .32 if k % 2 else .315), (.002, .002, .02 if k % 2 else .03))
for i, (y, z) in enumerate([(-.33, .18), (-.2, .15), (-.07, .15), (.07, .15), (.2, .15), (.33, .18), (-.36, .33), (.36, .33)]):   # knobs
    cyl(BK, (.29, y, z), (1, 0, 0), .03 if i < 6 else .025, .04, 20); cyl(CH, (.311, y, z), (1, 0, 0), .012, .004, 12)
for k in range(4): box(CH, (.27, -.12 + k * .08, .07), (.02, .012, .012)); box(CH, (.28, -.12 + k * .08, .078), (.01, .008, .03), Matrix.Rotation(.4, 3, "Y"))   # toggles
for y in (.26, .32): cyl(BK, (.262, y, .07), (1, 0, 0), .018, .02, 14)                         # jacks
box(bm_for("brass"), (.258, -.3, .07), (.004, .14, .04))                                       # nameplate
for s in (-1, 1):
    tube_path(CH, [(-.12, s * .45, .45), (-.12, s * .5, .48), (.12, s * .5, .48), (.12, s * .45, .45)], .012, 8)   # carrying handles
    for k in range(6): box(PN, (-.1 + k * .04, s * .452, .25), (.02, .004, .2))               # side vents
for k in range(4): cyl(CH, (-.252, -.3 + k * .2, .2), (1, 0, 0), .025, .03, 14)              # rear connectors
tube_path(bm_for("rubber"), [(-.26, .3, .2), (-.35, .32, .12), (-.3, .45, .03), (-.1, .55, .02), (.1, .6, .02)], .012, 8)  # cord to the key
finish(R, bevel_mats=("case",), bevel=.02, smooth_mats=("chrome", "bakelite", "rubber")); export(os.path.join(OUT, "field_radio.glb"))

# ------------------------------------------------ morse key: base 0.3 x 0.16
reset(); materials(); R = root("morse_key")
W, BR = bm_for("wood"), bm_for("brass")
box(W, (0, 0, .015), (.3, .16, .03))
for y in (-.04, .04): box(BR, (0, y, .055), (.03, .012, .05))                                 # trunnion frame
for x in (.11, -.11): cyl(BR, (x, .05, .04), (0, 0, 1), .012, .02, 12); cyl(bm_for("bakelite"), (x, .05, .055), (0, 0, 1), .014, .014, 12)   # binding posts
cyl(BR, (.08, 0, .035), (0, 0, 1), .008, .012, 10)                                             # contact
tube_path(bm_for("metal_dark"), [(-.08, 0, .033 + .004 * math.sin(k)) if False else (-.08, 0, .033 + k * .006) for k in range(6)], .006, 8)  # spring
finish(R, bevel_mats=("wood",), bevel=.004, smooth_mats=("bakelite",))
LV = bpy.data.objects.new("key_lever", None); bpy.context.scene.collection.objects.link(LV); LV.parent = R; LV.location = (0, 0, .07)
lb, kb = bm_for("brass"), bm_for("bakelite")
box(lb, (.0, 0, 0), (.24, .018, .012)); cyl(lb, (0, 0, 0), (0, 1, 0), .009, .1, 12)          # lever and pivot pin
cyl(kb, (.11, 0, .022), (0, 0, 1), .022, .02, 24); cyl(kb, (.11, 0, .036), (0, 0, 1), .017, .012, 24)   # knob
finish(LV, smooth_mats=("bakelite",)); export(os.path.join(OUT, "morse_key.glb"))

# ------------------------------------------------ light table: 2.2 (x) x 1.3 (y) x 0.9 (z)
reset(); materials(); R = root("light_table")
WL, MD = bm_for("wood_light"), bm_for("metal_dark")
box(WL, (0, 0, .86), (2.2, 1.3, .07))                                                          # frame rail around the glass
for x in (-1.0, 1.0):
    for y in (-.55, .55): box(WL, (x, y, .41), (.08, .08, .82))                                # legs
for y in (-.55, .55): box(WL, (0, y, .16), (2.0, .05, .05))                                    # low braces
box(WL, (0, 0, .16), (.05, 1.1, .05))
box(MD, (0, 0, .7), (1.95, 1.05, .22))                                                         # lamp box under the top
for k in range(8): box(MD, (-.8 + k * .23, .53, .65), (.12, .01, .03))                         # lamp-box vents
for x in (-.55, .55):
    box(WL, (x, -.66, .62), (.8, .03, .16)); cyl(bm_for("brass"), (x, -.69, .62), (0, 1, 0), .02, .03, 12)   # drawers + pulls
box(bm_for("table_glass"), (0, 0, .9), (2.0, 1.1, .02))                                        # frosted top (glows in the set)
# pocket stereoscope: two lenses in a bridge on folding legs
ST = bm_for("metal_dark")
box(ST, (.45, .25, 1.02), (.06, .22, .02))
for y in (.17, .33): cyl(bm_for("glass"), (.45, y, 1.03), (0, 0, 1), .035, .012, 20); torus(ST, (.45, y, 1.035), (0, 0, 1), .036, .006, 20, 6)
for y in (.15, .35): tube_path(ST, [(.45, y, 1.02), (.5, y, .97), (.55, y, .915)], .005, 6)
box(WL, (-.85, .4, .915), (.3, .1, .02)); [cyl(bm_for("case" if k % 2 else "brass"), (-.85, .37 + k * .02, .93), (1, 0, 0), .004, .26, 8) for k in range(3)]   # pencil tray
finish(R, bevel_mats=("wood_light",), bevel=.01, smooth_mats=("glass",)); export(os.path.join(OUT, "light_table.glb"))
