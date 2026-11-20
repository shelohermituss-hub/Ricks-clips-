"""Proof sheet for blender/rc/signs.py: one card character (crash_instinct planter, cards_s01), each emotion sign in its own time window,
rendered with Cycles at preview size. blender -b --factory-startup --python demos/signs_test/signs_test.py -- <outdir>"""
import bpy, os, sys, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); SK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(SK, "blender")); from rc import characters, signs, render
OUT = sys.argv[sys.argv.index("--") + 1]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, 80
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (.55, .7, .9, 1)
bpy.ops.mesh.primitive_plane_add(size=40); g = bpy.context.object; m = bpy.data.materials.new("g"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.25, .4, .15, 1); g.data.materials.append(m)
s = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); s.data.energy = 3; s.rotation_euler = (math.radians(50), 0, math.radians(30)); sc.collection.objects.link(s)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 35
cam.location = (0, -4.6, 1.2); cam.rotation_euler = (Vector((0, 0, 1.05)) - cam.location).to_track_quat("-Z", "Y").to_euler()
lock = os.path.join(SK, "demos", "crash_instinct", "build", "cards_s01")
c = characters.place_cards(sc, lock, ["planter"], cam, contact=False)["planter"]; card = c["object"]
card["rc_anchors"] = os.path.join(lock, "cards", "planter", "anchors.json")
for dp in ("location", "hide_render", "hide_viewport"):
    for f in range(-2, 300):
        try: card.keyframe_delete(dp, frame=f)
        except RuntimeError: pass
card.location = (0, 0, 0); card.hide_render = card.hide_viewport = False
print("ANCHORS", signs.anchors(card))
W = {"lightning": (2, 10), "shock_ring": (6, 10), "glow_eyes": (14, 20), "spiral_eyes": (24, 30), "dollar_eyes": (34, 40), "sweat_drop": (44, 50), "aura": (54, 60), "scribble": (64, 70)}
signs.lightning(card, 2, 10); signs.shock_ring(card, 6); signs.glow_eyes(card, 14, 20); signs.spiral_eyes(card, 24, 30); signs.dollar_eyes(card, 34, 40)
signs.sweat_drop(card, 44, 50); signs.aura(card, 54, 60); signs.scribble(card, 64, 70); signs.impact_lines((0, 0, 0), 74)
render.setup(sc, "CYCLES", (270, 480), 16, 0)
for name, f in (("lightning", 4), ("shock_ring", 8), ("glow_eyes", 15), ("spiral_eyes", 27), ("dollar_eyes", 35), ("sweat_drop", 46), ("aura", 56), ("scribble", 65), ("impact_lines", 77)):
    sc.frame_set(f); sc.render.filepath = os.path.join(OUT, "%02d_%s.png" % (f, name)); bpy.ops.render.render(write_still=True); print("STILL", name, f)
