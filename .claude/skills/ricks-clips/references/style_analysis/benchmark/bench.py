"""Benchmark EEVEE vs Cycles on the SAME built shot, same frames, same resolution (CPU of this cloud machine; EEVEE runs on Mesa llvmpipe software GL)."""
import bpy, time, sys, json
A = sys.argv[sys.argv.index("--") + 1:]; eng, out = A[0], A[1]; frames = [int(x) for x in A[2].split(",")]
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 270, 480, 100
sc.render.use_motion_blur = False; res = {}
if eng == "EEVEE":
    sc.render.engine = "BLENDER_EEVEE"; e = sc.eevee
    for k, v in (("taa_render_samples", 32), ("use_shadows", True), ("use_raytracing", True), ("use_volumetric_shadows", True)):
        try: setattr(e, k, v)
        except Exception: pass
else:
    sc.render.engine = "CYCLES"; sc.cycles.samples = 12; sc.cycles.device = "CPU"
for f in frames:
    sc.frame_set(f); sc.render.filepath = "%s/%s_%d.png" % (out, eng, f); t = time.time(); bpy.ops.render.render(write_still=True); res[f] = round(time.time() - t, 1)
    print("BENCH", eng, f, res[f], flush=True)
json.dump(res, open("%s/%s_times.json" % (out, eng), "w"))
