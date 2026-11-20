"""Look test of the beach set: key frames from the cameras of shots 01, 02 and 07 (no characters yet).
blender -b --factory-startup --python episodes/exploding-whale/shots/key_look.py -- <outdir> [mood]"""
import bpy, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "sets"))
import beach
from rc import render, lookdev
A = sys.argv[sys.argv.index("--") + 1:]; OUT = A[0]; mood = A[1] if len(A) > 1 else "grey"; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
c, w, Mo = beach.build(sc, mood)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); beach.col("CAM").objects.link(cam); sc.camera = cam; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24; cam.data.clip_end = 4000
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium Contrast"; sc.view_settings.exposure = Mo["exposure"]; lookdev.grade(sc, {"saturation": Mo["sat"]})
render.setup(sc, "CYCLES", (270, 480), 16, 0)
V = {"aerial": ((0, -40, 18), (0, 2, 0), 22), "whale_side": ((-9, -14, 2.0), (1, 0, 1.2), 28), "low_macro": ((3.0, -4.2, .55), (1.0, -1.2, .5), 24), "dune_view": ((18, -45, 7.2), (0, 0, 1), 28)}
for name, (p, a, lens) in V.items():
    cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (mood, name)); bpy.ops.render.render(write_still=True); print("STILL", name)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "look_%s.blend" % mood))
