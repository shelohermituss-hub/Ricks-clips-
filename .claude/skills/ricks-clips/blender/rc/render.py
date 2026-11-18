"""rc.render — J. Render Manager, Blender side. Mission 1, 2026-11-18.
  devices(require_gpu)            Cycles compute devices; with require_gpu=True raises if no OPTIX/CUDA/HIP/ONEAPI/METAL device is
                                  enabled (CB rule: never claim a GPU without proof; fail explicitly when the GPU is mandatory)
  setup(scene, engine, res, samples, seed, gpu)   EEVEE | CYCLES | WORKBENCH, fixed Cycles seed (frame-independent noise pattern)
  frames(scene, frames, outdir)   renders each frame from scratch state: frame_set(f) then render; writes f#####.png + render.json
                                  (engine, device, per-frame seconds, sha256 of each image)
Determinism contract: the scene holds only baked keys and seeded geometry, so frame f gives the same picture whatever was rendered
before it; `tools/tests/test_rc.py` checks it (frame alone vs inside a sequence)."""
import hashlib, json, os, time
import bpy

GPU_TYPES = ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL")

def devices(require_gpu=False):
    prefs = bpy.context.preferences.addons["cycles"].preferences; found = []
    for t in GPU_TYPES:
        try: prefs.compute_device_type = t; prefs.get_devices()
        except Exception: continue
        gpus = [d for d in prefs.devices if d.type == t]
        if gpus:
            for d in prefs.devices: d.use = d.type == t
            found = [(d.name, d.type) for d in gpus]; break
    if not found:
        prefs.compute_device_type = "NONE"
        if require_gpu: raise RuntimeError("GPU REQUIRED but Cycles sees no GPU device (types tried: %s)" % ", ".join(GPU_TYPES))
    return {"compute_device_type": prefs.compute_device_type, "gpus": found}

def setup(scene, engine="CYCLES", res=(540, 960), samples=64, seed=0, gpu=False, denoise=True):
    r = scene.render; r.resolution_x, r.resolution_y = res; r.resolution_percentage = 100; r.image_settings.file_format = "PNG"
    info = {"engine": engine, "res": list(res), "samples": samples}
    for k in [k for k in dir(r) if k.startswith("use_stamp")]: setattr(r, k, False)   # no date / render time written into the PNG: same picture = same bytes = same sha256
    if engine == "CYCLES":
        r.engine = "CYCLES"; c = scene.cycles; c.samples = samples; c.seed = seed; c.use_animated_seed = False; c.use_denoising = denoise
        d = devices(require_gpu=gpu); c.device = "GPU" if d["gpus"] else "CPU"; info.update(device=c.device, devices=d)
    elif engine == "EEVEE":
        r.engine = "BLENDER_EEVEE"; scene.eevee.taa_render_samples = samples; info["device"] = "OpenGL"
    else:
        r.engine = "BLENDER_WORKBENCH"; info["device"] = "OpenGL"
    return info

def strip_png_text(p):
    """remove tEXt/iTXt/zTXt chunks (Cycles writes its timing there: total_time, render_time) so equal pixels give equal bytes; pixels untouched"""
    import struct
    b = open(p, "rb").read(); out = [b[:8]]; o = 8
    while o < len(b):
        n = struct.unpack(">I", b[o:o + 4])[0]; t = b[o + 4:o + 8]
        if t not in (b"tEXt", b"iTXt", b"zTXt"): out.append(b[o:o + 12 + n])
        o += 12 + n
    open(p, "wb").write(b"".join(out))

def _sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()

def frames(scene, frame_list, outdir, info):
    os.makedirs(outdir, exist_ok=True); rows = []
    for f in frame_list:
        scene.frame_set(f); p = os.path.join(outdir, "f%05d.png" % f); scene.render.filepath = p; t = time.time()
        bpy.ops.render.render(write_still=True); strip_png_text(p); rows.append({"f": f, "seconds": round(time.time() - t, 3), "sha256": _sha(p)})
    rep = {**info, "frames": rows, "blend": bpy.data.filepath, "blender": bpy.app.version_string}
    json.dump(rep, open(os.path.join(outdir, "render.json"), "w"), indent=1); return rep
