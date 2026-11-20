"""render a saved shot as a preview sequence: blender -b build/sNN.blend --python shots/anim.py -- <frames dir> [step] [samples]
CPU preview only (CB rule): 270x480, every `step`-th frame; the assembly repeats frames to keep 30 fps."""
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]; sc = bpy.context.scene; step = int(a[1]) if len(a) > 1 else 2; sc.cycles.samples = int(a[2]) if len(a) > 2 else 12
sc.render.resolution_x, sc.render.resolution_y = 270, 480; sc.render.image_settings.file_format = "PNG"; os.makedirs(a[0], exist_ok=True)
for f in range(sc.frame_start, sc.frame_end + 1, step):
    p = os.path.join(a[0], "f%04d.png" % f)
    if os.path.exists(p): continue
    sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
print("ANIM DONE", a[0])
