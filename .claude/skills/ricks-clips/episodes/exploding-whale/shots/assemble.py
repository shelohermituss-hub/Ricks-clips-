"""Assemble the preview film from the per-shot preview frames (build/frames/sNN/f####.png, local frame numbers, any frame step):
every film frame takes the nearest rendered frame at or before it. Then captions + voice (shots/finish_clip.py).
    python3 shots/assemble.py [out.mp4]        prints which shots are missing or incomplete"""
import json, os, shutil, subprocess, sys, glob
H = os.path.dirname(os.path.abspath(__file__)); EP = os.path.abspath(os.path.join(H, "..")); P = json.load(open(os.path.join(EP, "plan", "plan.json")))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(EP, "build", "review", "film_preview.mp4"); film = os.path.join(EP, "build", "film"); shutil.rmtree(film, ignore_errors=True); os.makedirs(film)
B = [round(s["t0"] * 30) for s in P["shots"]] + [round(P["shots"][-1]["t1"] * 30)]; last = None; report = []
for s, f0, f1 in zip(P["shots"], B, B[1:]):
    d = os.path.join(EP, "build", "frames", "s" + s["id"]); have = sorted(int(os.path.basename(p)[1:5]) for p in glob.glob(os.path.join(d, "f????.png"))); n = f1 - f0
    report.append("s%s %d/%d" % (s["id"], len(have), n)); 
    for f in range(f0, f1):
        k = [h for h in have if h <= f - f0]; src = os.path.join(d, "f%04d.png" % k[-1]) if k else (os.path.join(d, "f%04d.png" % have[0]) if have else last)
        if src is None: raise SystemExit("no frame at all for shot " + s["id"])
        os.symlink(src, os.path.join(film, "f%04d.png" % f)); last = src
print("FRAMES", " | ".join(report))
subprocess.run([sys.executable, os.path.join(H, "finish_clip.py"), film, "0", str(B[-1] - 1), out], check=True)
