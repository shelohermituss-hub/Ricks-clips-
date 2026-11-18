"""J. Render Manager (deliverable 10, 2026-11-18): slices, resume, frame cache, GPU proof, benchmark, encode, manifest — around rc/render.py.
    python3 tools/render_manager.py render <scene.blend> <outdir> --frames 0-449 [--slice 30] [--engine CYCLES] [--res 540x960] [--samples 64] [--gpu]
    python3 tools/render_manager.py bench  <scene.blend> <outdir> --frames 60,200,380 [--res 540x960] [--samples 64] [--gpu]
    python3 tools/render_manager.py encode <framesdir> <out.mp4> [--fps 30]
    python3 tools/render_manager.py verify <outdir>
RENDER: frames are cut into slices (one Blender process each). A slice whose frames are all present with the sha256 recorded in the
  manifest is SKIPPED (resume after a stop or a crash); inside Blender the frame cache (scene key + frame) skips unchanged frames too.
  Every slice writes slices/<a>-<b>.json (device, GPU names, seconds per frame, sha256); RENDER_MANIFEST.json is the union.
  --gpu makes the GPU mandatory: no OPTIX/CUDA device -> the slice fails, nothing is rendered on the CPU silently.
  While rendering, nvidia-smi (when present) samples utilisation and memory every 2 s into gpu_usage.csv (proof of GPU use).
BENCH: the same frames with Cycles and EEVEE: seconds per frame, peak GPU memory (nvidia-smi), and the EEVEE picture's mean difference
  from Cycles (quality cost of the faster engine), so the engine choice is measured, not assumed.
Frames are deterministic (fixed seed, baked keys): a frame rendered alone equals the same frame inside a slice (tested in test_rc.py)."""
import glob, hashlib, json, os, shutil, subprocess, sys, time

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = os.environ.get("RICKCLIPS_BLENDER", shutil.which("blender") or "blender")
CLI = os.path.join(SKILL, "blender", "rc", "cli.py")

def _frames(s):
    out = []
    for x in s.split(","):
        a, _, b = x.partition("-"); out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out

def _sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def bl_render(blend, outdir, frames, engine, res, samples, gpu, timeout=86400):
    a = [BL, "-b", "--factory-startup", "--python-exit-code", "3", "--python", CLI, "--", "render", blend, outdir, ",".join(map(str, frames)),
         "--engine", engine, "--res", res, "--samples", str(samples)] + (["--gpu"] if gpu else [])
    r = subprocess.run(a, capture_output=True, text=True, timeout=timeout); res_ = [l[10:] for l in r.stdout.splitlines() if l.startswith("RC_RESULT ")]
    if r.returncode != 0 or not res_: raise RuntimeError("render failed (rc %s): %s" % (r.returncode, (r.stdout + r.stderr)[-2500:]))
    return json.loads(res_[-1])

class GpuSampler:
    """nvidia-smi every 2 s into a CSV while a block runs; peak() = highest memory.used (MiB) and utilisation (%) seen"""
    def __init__(self, path): self.path, self.p = path, None
    def __enter__(self):
        if shutil.which("nvidia-smi"):
            self.f = open(self.path, "a"); self.p = subprocess.Popen(["nvidia-smi", "--query-gpu=timestamp,utilization.gpu,memory.used,power.draw", "--format=csv,noheader,nounits", "-l", "2"], stdout=self.f, stderr=subprocess.DEVNULL)
        return self
    def __exit__(self, *e):
        if self.p: self.p.terminate(); self.p.wait(); self.f.close()
    def peak(self, since=0):
        if not os.path.exists(self.path): return None
        rows = [l.split(",") for l in open(self.path).read().splitlines()[since:] if l.count(",") >= 3]
        try: return {"samples": len(rows), "max_util_pct": max(float(r[1]) for r in rows), "max_mem_mib": max(float(r[2]) for r in rows), "mean_util_pct": round(sum(float(r[1]) for r in rows) / len(rows), 1)} if rows else None
        except ValueError: return None

def render(blend, out, frames, slice_n=30, engine="CYCLES", res="540x960", samples=64, gpu=False, log=print):
    os.makedirs(os.path.join(out, "slices"), exist_ok=True); mp = os.path.join(out, "RENDER_MANIFEST.json")
    M = json.load(open(mp)) if os.path.exists(mp) else {"frames": {}, "slices": []}; settings = {"engine": engine, "res": res, "samples": samples, "gpu": gpu, "blend_sha256": _sha(blend)}
    if M.get("settings") and M["settings"] != settings: log("settings changed since the last run: previous frames are not reused"); M = {"frames": {}, "slices": []}
    M["settings"] = settings; t0 = time.time()
    with GpuSampler(os.path.join(out, "gpu_usage.csv")) as G:
        for i in range(0, len(frames), slice_n):
            sl = frames[i:i + slice_n]; name = "%05d-%05d" % (sl[0], sl[-1])
            done = all(str(f) in M["frames"] and os.path.exists(os.path.join(out, "f%05d.png" % f)) and _sha(os.path.join(out, "f%05d.png" % f)) == M["frames"][str(f)]["sha256"] for f in sl)
            if done: log("slice %s: already rendered and verified, skipped (resume)" % name); continue
            tmp = os.path.join(out, "slices", name + ".tmp"); t = time.time(); r = bl_render(blend, tmp, sl, engine, res, samples, gpu)
            rows = json.load(open(os.path.join(tmp, "render.json")))
            for row in rows["frames"]:
                src = os.path.join(tmp, "f%05d.png" % row["f"]); os.replace(src, os.path.join(out, "f%05d.png" % row["f"]))
                M["frames"][str(row["f"])] = {"sha256": row["sha256"], "seconds": row["seconds"], "cached": row.get("cached", False)}
            info = {"slice": name, "device": rows.get("device"), "devices": rows.get("devices"), "seconds": round(time.time() - t, 1), "cached_frames": rows.get("cached_frames")}
            json.dump(info | {"render": {k: rows[k] for k in rows if k != "frames"}}, open(os.path.join(out, "slices", name + ".json"), "w"), indent=1); shutil.rmtree(tmp, ignore_errors=True)
            M["slices"] = [s for s in M["slices"] if s["slice"] != name] + [info]; json.dump(M, open(mp, "w"), indent=1)
            log("slice %s: %d frames in %.1f s on %s" % (name, len(sl), info["seconds"], info["device"]))
        M["gpu_usage"] = G.peak()
    sec = [v["seconds"] for v in M["frames"].values() if not v["cached"]]
    M["summary"] = {"frames": len(M["frames"]), "wall_seconds_this_run": round(time.time() - t0, 1), "mean_seconds_per_rendered_frame": round(sum(sec) / len(sec), 2) if sec else None,
                    "devices": sorted({str(s.get("devices")) for s in M["slices"]})}
    json.dump(M, open(mp, "w"), indent=1); return M

def verify(out):
    M = json.load(open(os.path.join(out, "RENDER_MANIFEST.json"))); bad = [f for f, v in M["frames"].items() if not os.path.exists(os.path.join(out, "f%05d.png" % int(f))) or _sha(os.path.join(out, "f%05d.png" % int(f))) != v["sha256"]]
    return {"frames": len(M["frames"]), "bad": bad, "ok": not bad}

def bench(blend, out, frames, res="540x960", samples=64, gpu=False):
    import numpy as np
    from PIL import Image
    os.makedirs(out, exist_ok=True); R = {}; csv = os.path.join(out, "bench_gpu_usage.csv")
    for eng in ("CYCLES", "EEVEE"):
        d = os.path.join(out, eng.lower()); n0 = len(open(csv).read().splitlines()) if os.path.exists(csv) else 0
        with GpuSampler(csv) as G:
            t = time.time()
            try: r = bl_render(blend, d, frames, eng, res, samples if eng == "CYCLES" else max(16, samples // 2), gpu and eng == "CYCLES")
            except RuntimeError as e: R[eng] = {"error": str(e)[-600:]}; continue
        sec = r["sec"]; warm = sorted(sec[1:]) or sec                      # the 1st frame of a process pays the GPU kernel compile / scene load
        R[eng] = {"seconds_per_frame": round(warm[len(warm) // 2], 2), "first_frame_s": round(sec[0], 2), "per_frame_s": sec, "wall_s": round(time.time() - t, 1), "device": r.get("device"), "gpu": G.peak(n0)}   # median after warm-up (measured 2026-11-18: 121 s then 4.5 s)
    if "error" not in R.get("CYCLES", {"error": 1}) and "error" not in R.get("EEVEE", {"error": 1}):
        diffs = []
        for f in frames:
            a = np.asarray(Image.open(os.path.join(out, "cycles", "f%05d.png" % f)).convert("RGB"), float); b = np.asarray(Image.open(os.path.join(out, "eevee", "f%05d.png" % f)).convert("RGB"), float)
            diffs.append(float(np.abs(a - b).mean()))
        R["EEVEE"]["mean_abs_diff_vs_cycles_0_255"] = round(sum(diffs) / len(diffs), 2)
    R["frames"], R["res"], R["samples"] = frames, res, samples; json.dump(R, open(os.path.join(out, "BENCH.json"), "w"), indent=1); return R

def encode(fdir, mp4, fps=30):
    fl = sorted(glob.glob(os.path.join(fdir, "f*.png"))); start = int(os.path.basename(fl[0])[1:6])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-start_number", str(start), "-i", os.path.join(fdir, "f%05d.png"), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", mp4], check=True)
    return {"mp4": mp4, "frames": len(fl), "sha256": _sha(mp4)}

def main(a):
    if len(a) < 2: print(__doc__); return 2
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    if a[0] == "render": r = render(a[1], a[2], _frames(opt("--frames", "0-0")), int(opt("--slice", "30")), opt("--engine", "CYCLES"), opt("--res", "540x960"), int(opt("--samples", "64")), "--gpu" in a); print(json.dumps(r["summary"] | {"gpu_usage": r.get("gpu_usage")}))
    elif a[0] == "bench": print(json.dumps(bench(a[1], a[2], _frames(opt("--frames", "0")), opt("--res", "540x960"), int(opt("--samples", "64")), "--gpu" in a), indent=1))
    elif a[0] == "encode": print(json.dumps(encode(a[1], a[2], int(opt("--fps", "30")))))
    elif a[0] == "verify": r = verify(a[1]); print(json.dumps(r)); return 0 if r["ok"] else 1
    else: print(__doc__); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
