"""rc command line inside Blender (Mission 1, 2026-11-18):
  blender -b --factory-startup --python blender/rc/cli.py -- assemble <place.json> <out.blend>
  blender -b --factory-startup --python blender/rc/cli.py -- stats <scene.blend> [out.json]
  blender -b --python blender/rc/cli.py -- render <scene.blend> <outdir> <frames a,b,c|a-b> [--engine CYCLES|EEVEE|WORKBENCH] [--res 270x480] [--samples 16] [--seed 0] [--gpu] [--no-denoise]
Every command prints one line "RC_RESULT <json>" for the orchestrator; errors raise (python-exit-code makes Blender exit non-zero)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy  # noqa: E402

def _frames(s):
    out = []
    for x in s.split(","):
        a, _, b = x.partition("-"); out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out

def _tile(paths, out):
    """side-by-side tile of PNGs (same size) with Blender's image API: one picture whose mean colour is the mean of all frames"""
    import numpy as np
    ims = []
    for p in paths:
        im = bpy.data.images.load(p, check_existing=False); A = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(A); ims.append((im.size[0], im.size[1], A.reshape(im.size[1], im.size[0], 4))); bpy.data.images.remove(im)
    h = min(x[1] for x in ims); T = np.concatenate([x[2][:h] for x in ims], axis=1); o = bpy.data.images.new("tile", T.shape[1], T.shape[0], alpha=True)
    o.pixels.foreach_set(T.ravel()); o.filepath_raw = out; o.file_format = "PNG"; o.save(); bpy.data.images.remove(o); return out

def main(a):
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    if a[0] == "assemble":
        from rc import assemble, qa
        rep = assemble.build(a[1], a[2], upto=int(opt("--upto", "9"))); rep["stats"] = qa.scene_stats(); bpy.ops.wm.save_mainfile()
        print("RC_RESULT " + json.dumps(rep)); return
    if a[0] == "stats":
        from rc import qa
        bpy.ops.wm.open_mainfile(filepath=a[1]); s = qa.scene_stats()
        if len(a) > 2 and not a[2].startswith("--"): json.dump(s, open(a[2], "w"), indent=1)
        print("RC_RESULT " + json.dumps(s)); return
    if a[0] == "render":
        from rc import render
        bpy.ops.wm.open_mainfile(filepath=a[1]); sc = bpy.context.scene; w, h = map(int, opt("--res", "270x480").split("x"))
        info = render.setup(sc, opt("--engine", "CYCLES"), (w, h), int(opt("--samples", "16")), int(opt("--seed", "0")), gpu="--gpu" in a, denoise="--no-denoise" not in a)
        rep = render.frames(sc, _frames(a[3]), a[2], info); print("RC_RESULT " + json.dumps({k: rep[k] for k in rep if k != "frames"} | {"n": len(rep["frames"]), "sec": [r["seconds"] for r in rep["frames"]]})); return
    if a[0] == "calibrate":                                     # calibrate <blend> <frame> <reference.png> <outdir> [--res 135x240] [--samples 16]
        from rc import render, lookdev
        bpy.ops.wm.open_mainfile(filepath=a[1]); sc = bpy.context.scene; fl = [int(x) for x in a[2].split(",")]; refs = a[3].split(","); f = fl[0]; w, h = map(int, opt("--res", "135x240").split("x"))
        info = render.setup(sc, opt("--engine", "CYCLES"), (w, h), int(opt("--samples", "16")), 0)
        def rf(i):                                               # MULTI-FRAME calibration: the frames are tiled side by side into one measured picture
            d = os.path.join(a[4], "it%d" % i); render.frames(sc, fl, d, info, frame_cache=False)
            if len(fl) == 1: return os.path.join(d, "f%05d.png" % f)
            return _tile([os.path.join(d, "f%05d.png" % x) for x in fl], os.path.join(d, "tile.png"))
        if len(refs) > 1: a[3] = _tile(refs, os.path.join(a[4], "ref_tile.png"))
        wb = lookdev.calibrate_white(sc, a[3], lambda i: rf(10 + i)); log = lookdev.calibrate_exposure(sc, a[3], f, a[4], rf); bpy.ops.wm.save_mainfile()
        print("RC_RESULT " + json.dumps({"white_balance": wb, "calibration": log, "exposure": sc.view_settings.exposure, "temperature": sc.view_settings.white_balance_temperature})); return
    if a[0] == "qa":                                            # qa <blend> <out.json> [--anim name,name]: character contact + animation keys
        from rc import qa
        bpy.ops.wm.open_mainfile(filepath=a[1]); r = {"contact": qa.character_contact(), "stats": qa.scene_stats()}
        if "--anim" in a: r["animation"] = qa.animation_keys(opt("--anim", "").split(","))
        json.dump(r, open(a[2], "w"), indent=1); print("RC_RESULT " + json.dumps({k: r[k] for k in r if k != "stats"})); return
    raise SystemExit("unknown rc command: %s" % a[0])

main(sys.argv[sys.argv.index("--") + 1:])
