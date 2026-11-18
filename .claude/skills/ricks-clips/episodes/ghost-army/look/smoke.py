"""LookDev prototype, job 001: rebuild one place from the lock (from_lock) and render one plan frame, Cycles GPU or EEVEE, timed.
    blender -b --python smoke.py -- <place> <preset> <frame> <engine CYCLES|EEVEE> <out.png> [samples]"""
import bpy, sys, os, time, json
a = sys.argv[sys.argv.index("--") + 1:]; place, preset, frame, engine, out = a[0], a[1], int(a[2]), a[3], a[4]; samples = int(a[5]) if len(a) > 5 else 64
SK = os.environ["SKILL"]; sys.path.insert(0, os.path.join(SK, "templates")); from blender_look import from_lock as FL
t0 = time.time(); K = FL.build(bpy.context.scene, os.environ["EP"], place=place, preset=preset, samples=samples, res=37.5, motion_blur=False); tb = time.time() - t0
sc = bpy.context.scene
if engine == "CYCLES":
    p = bpy.context.preferences.addons["cycles"].preferences; p.compute_device_type = "OPTIX"; p.get_devices()
    for d in p.devices: d.use = d.type in ("OPTIX", "CUDA")
    sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.samples = samples; sc.cycles.use_denoising = True
sc.frame_set(frame); sc.render.filepath = out; t1 = time.time(); bpy.ops.render.render(write_still=True); tr = time.time() - t1
print("SMOKE", json.dumps(dict(place=place, frame=frame, engine=engine, samples=samples, build_s=round(tb, 1), render_s=round(tr, 1), res=[sc.render.resolution_x * sc.render.resolution_percentage // 100, sc.render.resolution_y * sc.render.resolution_percentage // 100], set_objects=len(K["set"]))))
