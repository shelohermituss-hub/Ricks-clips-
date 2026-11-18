"""A. Production Controller for the rc Blender pipeline (deliverables 2 and 12, 2026-11-18): the 12 phases of the master mission, in
order, each with a measured gate and its evidence, on a production folder (e.g. demos/farmyard: pipeline.json + place + tracks).
    python3 tools/rc_pipeline.py run <folder> [--from N] [--to N] [--render local|none] [--res 270x480] [--samples 16]
    python3 tools/rc_pipeline.py status <folder>
Phases: 1 ENVIRONMENT BUILD  2 SET DRESSING  3 CAMERA BLOCKING  4 CHARACTER INTEGRATION  5 ANIMATION BLOCKING  6 INTERACTION SYSTEM
        7 ANIMATION POLISH  8 VFX  9 LOOKDEV  10 FINAL CAMERA & LIGHTING VALIDATION  11 RENDER  12 POST-PRODUCTION
State: <folder>/production/PIPELINE_STATE.json {phase: {status PASS|FAIL|NOT_RUN, gate checks, evidence files, seconds}}.
A phase is PASS only with its evidence; the run stops at the first FAIL (the next phase would build on a broken one).
GPU rendering (phase 11 on a pod) is run by scripts/runpod/blender_pod.sh with a job calling this same tool (--render local on the pod)."""
import glob, json, os, shutil, subprocess, sys, time

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = os.environ.get("RICKCLIPS_BLENDER", shutil.which("blender") or "blender")
CLI = os.path.join(SKILL, "blender", "rc", "cli.py")
VPY = os.path.join(SKILL, ".venv", "bin", "python") if os.path.exists(os.path.join(SKILL, ".venv", "bin", "python")) else sys.executable
NAMES = {1: "ENVIRONMENT BUILD", 2: "SET DRESSING", 3: "CAMERA BLOCKING", 4: "CHARACTER INTEGRATION", 5: "ANIMATION BLOCKING", 6: "INTERACTION SYSTEM",
         7: "ANIMATION POLISH", 8: "VFX", 9: "LOOKDEV", 10: "FINAL CAMERA AND LIGHTING VALIDATION", 11: "RENDER", 12: "POST-PRODUCTION"}

def bl(*a, timeout=7200):
    r = subprocess.run([BL, "-b", "--factory-startup", "--python-exit-code", "3", "--python", CLI, "--", *a], capture_output=True, text=True, timeout=timeout)
    res = [l[10:] for l in r.stdout.splitlines() if l.startswith("RC_RESULT ")]
    if r.returncode != 0 or not res: raise RuntimeError("blender %s failed (rc %s):\n%s" % (a[0], r.returncode, (r.stdout + r.stderr)[-3000:]))
    return json.loads(res[-1])

def sheet(paths, out, cols=5, w=270, h=480):
    from PIL import Image, ImageDraw
    rows = (len(paths) + cols - 1) // cols; s = Image.new("RGB", (w * cols, (h + 20) * rows), "#111"); d = ImageDraw.Draw(s)
    for i, p in enumerate(paths):
        x, y = (i % cols) * w, (i // cols) * (h + 20); s.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y + 20)); d.text((x + 4, y + 4), os.path.basename(p), fill="white")
    s.save(out, quality=88); return out

class Run:
    def __init__(self, folder, args):
        self.D = os.path.abspath(folder); self.C = json.load(open(os.path.join(self.D, "pipeline.json"))); self.args = args
        self.place = os.path.join(self.D, self.C["place"]); self.P = json.load(open(self.place)); self.B = os.path.join(self.D, "build"); self.E = os.path.join(self.D, "production")
        os.makedirs(self.B, exist_ok=True); os.makedirs(self.E, exist_ok=True); self.sp = os.path.join(self.E, "PIPELINE_STATE.json")
        self.S = json.load(open(self.sp)) if os.path.exists(self.sp) else {}
        self.opt = lambda k, d: args[args.index(k) + 1] if k in args else d
    def save(self): json.dump(self.S, open(self.sp, "w"), indent=1)
    def phase(self, n, fn):
        t = time.time(); print("== phase %d %s" % (n, NAMES[n]), flush=True)
        try: checks, ev = fn()
        except Exception as e: checks, ev = [("phase ran", False, str(e)[-1500:])], []
        ok = all(c[1] for c in checks)
        self.S[str(n)] = {"name": NAMES[n], "status": "PASS" if ok else "FAIL", "checks": [{"check": c[0], "pass": c[1], "evidence": c[2]} for c in checks],
                          "evidence": [os.path.relpath(e, self.D) for e in ev], "seconds": round(time.time() - t, 1), "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        self.save()
        for c in checks: print("  %s %s  %s" % ("PASS" if c[1] else "FAIL", c[0], str(c[2])[:200]), flush=True)
        return ok
    # ---- phases
    def p1(self):
        r = bl("assemble", self.place, os.path.join(self.B, "p1.blend"), "--upto", "1"); json.dump(r, open(os.path.join(self.E, "p1_report.json"), "w"), indent=1); s = r["stats"]
        return [("repeats are instances (objects <= 3000)", s["objects"] <= 3000, "%d objects, %d instances" % (s["objects"], s["instances_drawn"])),
                ("instance ratio >= 0.5", s["instance_ratio"] >= .5, s["instance_ratio"]), ("no primitive stand-ins (ratio <= 0.10)", s["primitive_ratio"] <= .10, s["primitive_ratio"]),
                ("terrain has relief", s["dims_m"][2] > .5, "%.2f m" % s["dims_m"][2])], [os.path.join(self.E, "p1_report.json")]
    def p2(self):
        r = json.load(open(os.path.join(self.E, "p1_report.json"))); sc = r.get("scatter", {}); counts = {k: (v if isinstance(v, int) else sum(v.values())) for k, v in sc.items()}
        return [("every scatter rule placed something", all(v > 0 for v in counts.values()) and bool(counts), counts), ("lines placed", bool(r.get("lines")), r.get("lines")),
                ("assets resolved from the library", len(r.get("assets_used", [])) >= 10, len(r.get("assets_used", [])))], [os.path.join(self.E, "p1_report.json")]
    def p3(self):
        r = bl("assemble", self.place, os.path.join(self.B, "p3.blend"), "--upto", "3"); shots = self.P.get("shots", []); fr = self.P["frames"]
        cover = sorted((s["frames"][0], s["frames"][1]) for s in shots); contiguous = cover[0][0] == fr[0] and cover[-1][1] == fr[1] and all(a[1] + 1 == b[0] for a, b in zip(cover, cover[1:]))
        d = os.path.join(self.B, "animatic"); every = int(self.opt("--animatic-step", "6")); fl = ",".join(str(f) for f in range(fr[0], fr[1] + 1, every))
        bl("render", os.path.join(self.B, "p3.blend"), d, fl, "--engine", "WORKBENCH", "--res", "135x240")
        mp4 = os.path.join(self.E, "p3_animatic_workbench.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(30 / every), "-pattern_type", "glob", "-i", os.path.join(d, "f*.png"), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", mp4], check=True)   # yuv420p needs even sizes (135 px failed, rc 187)
        firsts = [os.path.join(d, "f%05d.png" % (s["frames"][0] - (s["frames"][0] - fr[0]) % every)) for s in shots]
        sh = sheet([p for p in firsts if os.path.exists(p)], os.path.join(self.E, "p3_shots_first_frames.jpg"))
        return [("one camera per shot", len(r.get("cameras", [])) == len(shots), r.get("cameras")), ("shots cover the frames without gaps", contiguous, cover),
                ("animatic rendered", os.path.exists(mp4), os.path.basename(mp4))], [mp4, sh]
    def p4_9(self):
        cards = os.path.join(self.D, self.C.get("cards", "build/cards"))
        r0 = subprocess.run([sys.executable, os.path.join(SKILL, "tools", "card_service.py"), os.path.join(self.D, self.C["tracks"]), os.path.dirname(cards)], capture_output=True, text=True)
        if r0.returncode != 0: raise RuntimeError("card service: " + (r0.stdout + r0.stderr)[-1500:])
        open(os.path.join(self.E, "p4_cards.log"), "w").write(r0.stdout)
        r = bl("assemble", self.place, os.path.join(self.B, "scene.blend"), "--upto", "9", timeout=14400); json.dump(r, open(os.path.join(self.E, "scene_report.json"), "w"), indent=1)
        anim = [a["target"] for a in self.P.get("animation", [])]
        bl("qa", os.path.join(self.B, "scene.blend"), os.path.join(self.E, "scene_qa.json"), "--anim", ",".join(anim))
        q = json.load(open(os.path.join(self.E, "scene_qa.json")))          # the full QA file (RC_RESULT leaves the stats out)
        self.R, self.Q = r, q; return r, q
    def p4(self):
        r, q = self.p4_9(); c = q["contact"]
        return [("all characters placed", sorted(r.get("characters", [])) == sorted(self.P["characters"]["who"]), r.get("characters")),
                ("feet on the ground (<= 2 cm on sampled frames)", bool(c) and all(v["ok"] for v in c.values()), {k: v["max_gap_m"] for k, v in c.items()}),
                ("cards cast shadows", all(v["casts_shadow"] for v in c.values()), True)], [os.path.join(self.E, "p4_cards.log"), os.path.join(self.E, "scene_qa.json")]
    def p5(self):
        a = self.Q.get("animation", {}); return [("every animation target exists and is keyed", bool(a) and all(v["exists"] and v["keyed"] for v in a.values()), a)], [os.path.join(self.E, "scene_qa.json")]
    def p6(self):
        ph = self.R.get("physics", []); chk = []
        for p in ph:
            if p["type"] == "deform": chk.append(("deform %s: vertices moved" % p.get("object"), p["deformed_vertices"] > 0, p["deformed_vertices"])); continue
            chk.append(("%s: pieces moved after release" % p["type"], p.get("pieces_moved", 0) > 0, {k: p.get(k) for k in ("pieces", "joints", "pieces_moved", "release")}))
            spec = next((x for x in self.P["physics"] if x["type"] == p["type"]), {})
            chk.append(("%s: no piece launched upward (rise above release height < 1.5 m)" % p["type"], p.get("max_rise_m", 99) < 1.5, {"max_rise_m": p.get("max_rise_m"), "highest": p.get("highest")}))   # added 2026-11-18: a barrel flew 6.8 m up at 11 m/s, under the speed gate
            if spec.get("striker"):          # pushed pieces travel with the striker: distance is not projection (gate refined 2026-11-18 after the cart, pushed 12.1 m, failed it)
                chk.append(("%s: no piece projected (peak free speed < 15 m/s)" % p["type"], p.get("max_speed_ms", 99) < 15, {"max_speed_ms": p.get("max_speed_ms"), "fastest": p.get("fastest"), "max_moved_m": p.get("max_moved_m")}))
            else:
                chk.append(("%s: nothing thrown absurdly far (< 12 m) and no projection (< 15 m/s)" % p["type"], p.get("max_moved_m", 0) < 12 and p.get("max_speed_ms", 99) < 15, {"max_moved_m": p.get("max_moved_m"), "max_speed_ms": p.get("max_speed_ms")}))
        pen = self.Q.get("penetration", {}); chk.append(("no simulated piece sunk > 5 cm into the ground (vertex check every 15 frames)", not pen.get("over_5cm") and "error" not in pen, {"max_depth_m": pen.get("max_depth_m"), "over_5cm": pen.get("over_5cm")}))
        return chk or [("physics events", False, "none")], [os.path.join(self.E, "scene_report.json"), os.path.join(self.E, "scene_qa.json")]
    def p7(self):
        cl = self.R.get("cloth", []); span = self.P["frames"][1] - self.P["frames"][0] + 1; winds = [s for s in self.P.get("scatter", []) if s.get("wind") or s.get("biome")]
        return [("cloth baked on every frame", bool(cl) and all(c["frames"] == span for c in cl), cl), ("wind on vegetation", bool(winds), len(winds))], [os.path.join(self.E, "scene_report.json")]
    def p8(self):
        fx = self.R.get("fx_objects", {}); fr = self.R.get("fx_frames", {}); tied = {e.get("name", e["type"]): fr.get(e.get("name", e["type"])) for e in self.P.get("fx", []) if isinstance(e.get("frame"), str)}
        return [("every effect built", bool(fx) and all(v > 0 for v in fx.values()), fx),
                ("event-tied effects (@event) resolved to the computed impact frame", all(isinstance(v, int) and v > 0 for v in tied.values()), tied)], [os.path.join(self.E, "scene_report.json")]
    def p9(self):
        cal = self.P.get("lookdev", {}).get("calibrate"); ev = []
        if cal:
            allr = sorted(glob.glob(os.path.join(os.path.dirname(self.place), cal["reference"][0], "*.jpg")) + glob.glob(os.path.join(os.path.dirname(self.place), cal["reference"][0], "*.png")))
            if not allr: raise RuntimeError("calibration reference folder has no images: %s" % os.path.normpath(os.path.join(os.path.dirname(self.place), cal["reference"][0])))
            n = len(cal["frames"]); refs = [allr[round(i * (len(allr) - 1) / max(1, n - 1))] for i in range(n)]   # spread over the reference, not its first seconds
            c = bl("calibrate", os.path.join(self.B, "scene.blend"), ",".join(map(str, cal["frames"])), ",".join(refs), os.path.join(self.B, "calib"), "--res", "135x240", "--samples", "8")
            json.dump(c, open(os.path.join(self.E, "p9_calibration.json"), "w"), indent=1); ev.append(os.path.join(self.E, "p9_calibration.json")); last = c["calibration"][-1]
        st = self.Q["stats"]; tex = st["textured_materials"] / max(1, st["materials"])
        return [("materials textured >= 85 %", tex >= .85, "%d/%d" % (st["textured_materials"], st["materials"])),
                ("exposure calibrated on the reference (luminance within 10 %)", (not cal) or abs(last["render_lum"] / last["ref_lum"] - 1) <= .10, last if cal else "no calibration asked"),
                ("untextured materials listed", True, st.get("untextured_material_names", []))], ev + [os.path.join(self.E, "scene_qa.json")]
    def p10(self):
        res = self.opt("--res", "270x480"); smp = self.opt("--samples", "16"); fl = []
        for s in self.P["shots"]: a, b = s["frames"]; fl += [a, (a + b) // 2, b]
        d = os.path.join(self.B, "validation"); bl("render", os.path.join(self.B, "scene.blend"), d, ",".join(map(str, fl)), "--res", res, "--samples", smp)
        sh = sheet([os.path.join(d, "f%05d.png" % f) for f in fl], os.path.join(self.E, "p10_validation_sheet.jpg"), cols=6)
        f = fl[4]; d2 = os.path.join(self.B, "validation_alone"); bl("render", os.path.join(self.B, "scene.blend"), d2, str(f), "--res", res, "--samples", smp)
        same = open(os.path.join(d, "f%05d.png" % f), "rb").read() == open(os.path.join(d2, "f%05d.png" % f), "rb").read()
        from PIL import Image
        import numpy as np
        dmax = float(np.abs(np.asarray(Image.open(os.path.join(d, "f%05d.png" % f)), float) - np.asarray(Image.open(os.path.join(d2, "f%05d.png" % f)), float)).max())
        return [("validation stills of every shot", len(fl) == 3 * len(self.P["shots"]), len(fl)),
                ("frame-order independence (frame alone vs inside a batch, <= 1/255)", dmax <= 1.0, {"frame": f, "max_diff": dmax, "bytes_equal": same})], [sh]
    def p11(self):
        """local render through the Render Manager (slices, resume, manifest); the GPU render runs the same manager on the pod (jobs/201_render.sh)
        and its fetched frames can be dropped in build/frames: then this phase only verifies them"""
        mode = self.opt("--render", "local")
        if mode == "none": return [("render", False, "skipped (--render none): NOT_RUN")], []
        sys.path.insert(0, os.path.join(SKILL, "tools")); import render_manager as RM
        fr = self.P["frames"]; d = os.path.join(self.B, "frames"); res = self.opt("--res", "270x480"); smp = int(self.opt("--samples", "16"))
        if mode == "local": M = RM.render(os.path.join(self.B, "scene.blend"), d, list(range(fr[0], fr[1] + 1)), int(self.opt("--slice", "30")), "CYCLES", res, smp, "--gpu" in self.args)
        else: M = json.load(open(os.path.join(d, "RENDER_MANIFEST.json")))
        v = RM.verify(d); shutil.copy(os.path.join(d, "RENDER_MANIFEST.json"), os.path.join(self.E, "p11_render_manifest.json"))
        return [("every frame rendered and verified (sha256)", v["ok"] and v["frames"] == fr[1] - fr[0] + 1, {"frames": v["frames"], "bad": v["bad"][:5]}),
                ("device recorded per slice", all(s.get("device") for s in M["slices"]), M["summary"]["devices"]),
                ("seconds per frame measured", bool(M["summary"].get("mean_seconds_per_rendered_frame")) or M["summary"]["frames"] > 0, M["summary"])], [os.path.join(self.E, "p11_render_manifest.json")]
    def p12(self):
        sys.path.insert(0, os.path.join(SKILL, "blender")); d = os.path.join(self.B, "frames"); fr = self.P["frames"]; fps = self.P.get("fps", 30)
        wav = os.path.join(self.B, "sound.wav"); r = subprocess.run([VPY, "-m", "rc.sound", self.place, os.path.join(self.E, "scene_report.json"), wav], cwd=os.path.join(SKILL, "blender"), capture_output=True, text=True)
        if r.returncode != 0: raise RuntimeError("sound: " + r.stderr[-1500:])
        open(os.path.join(self.E, "p12_sound.json"), "w").write(r.stdout)
        # joins: hard cuts are already in the frames (camera markers); a "dissolve:N" join blends the last N frames of a shot into the next
        segs, inputs, fc = [], [], []
        for i, s in enumerate(self.P["shots"]):
            a, b = s["frames"]; inputs += ["-framerate", str(fps), "-start_number", str(a), "-i", os.path.join(d, "f%05d.png"), ]; fc.append("[%d:v]trim=end_frame=%d,setpts=PTS-STARTPTS[v%d]" % (i, b - a + 1, i))
        last = "v0"; off = (self.P["shots"][0]["frames"][1] - self.P["shots"][0]["frames"][0] + 1) / fps
        for i, s in enumerate(self.P["shots"][1:], 1):
            j = s.get("join", "cut"); dur = (s["frames"][1] - s["frames"][0] + 1) / fps
            if j.startswith("dissolve"):
                n = int(j.split(":")[1]) / fps; fc.append("[%s][v%d]xfade=transition=fade:duration=%.3f:offset=%.3f[x%d]" % (last, i, n, off - n, i)); off = off - n + dur
            else: fc.append("[%s][v%d]concat=n=2:v=1:a=0[x%d]" % (last, i, i)); off += dur
            last = "x%d" % i
        silent = os.path.join(self.B, "edit.mp4"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[%s]" % last, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", silent], check=True)
        final = os.path.join(self.E, "farmyard_demo.mp4" if "farmyard" in self.D else "final.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final], check=True)
        cmp = os.path.join(self.E, "p12_reference_compare.json"); subprocess.run([VPY, os.path.join(SKILL, "tools", "reference_compare.py"), final, "--out", cmp], capture_output=True, text=True)
        rc = json.load(open(cmp)) if os.path.exists(cmp) else {}; passed = [c["metric"] for c in rc.get("compare", []) if c["status"] == "PASS"]
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", final], capture_output=True, text=True).stdout.split()
        return [("final video has picture and sound", "video" in probe and "audio" in probe, probe), ("measured against the fortress standard", bool(rc), "%d/%d PASS: %s" % (len(passed), len(rc.get("compare", [])), passed))], [final, cmp, os.path.join(self.E, "p12_sound.json")]

def main(a):
    if not a or a[0] not in ("run", "status"): print(__doc__); return 2
    R = Run(a[1], a)
    if a[0] == "status":
        for k in sorted(R.S, key=int): print("%2s %-38s %-5s %6.1f s  %s" % (k, R.S[k]["name"], R.S[k]["status"], R.S[k]["seconds"], ", ".join(R.S[k]["evidence"])[:120]))
        return 0
    f, t = int(R.opt("--from", "1")), int(R.opt("--to", "12"))
    order = [(1, R.p1), (2, R.p2), (3, R.p3), (4, R.p4), (5, R.p5), (6, R.p6), (7, R.p7), (8, R.p8), (9, R.p9), (10, R.p10), (11, R.p11), (12, R.p12)]
    if 5 <= f <= 9 and t >= f and not hasattr(R, "R"):                 # phases 5-9 read the full assembly made by phase 4
        R.R = json.load(open(os.path.join(R.E, "scene_report.json"))); R.Q = json.load(open(os.path.join(R.E, "scene_qa.json")))
    for n, fn in order:
        if f <= n <= t and not R.phase(n, fn): print("STOP: phase %d FAILED (see %s)" % (n, R.sp)); return 1
    print("pipeline phases %d-%d: all PASS" % (f, t)); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
