"""THE GHOST ARMY: the final grade (last picture step, CB_RULES 11c). One look per light kind, the same for every frame of a place.
  .venv/bin/python episodes/ghost-army/grade/grade.py calibrate <stills_dir>          one rendered frame per place -> grade/grade.json (exposure per place)
  .venv/bin/python episodes/ghost-army/grade/grade.py apply <in_dir> <out_dir> [--jobs N]  grades every f_#####.png
  .venv/bin/python episodes/ghost-army/grade/grade.py measure <dir>                   mean, saturation, crushed / clipped share per frame
Order per pixel: white balance gains -> exposure on luminance (gamma that brings the place to its target mean, chroma kept)
-> gentle S contrast -> saturation -> black floor (never crushed) and a soft highlight roll-off -> light vignette.
Targets (v1 notes 7): day bright and natural, night readable (mean >= .28) but still blue and dark, interiors warm not orange,
the photo room cold, the attic golden; no frame with more than 1 % of pixels crushed to black or burned to white."""
import json, os, sys, glob
import numpy as np
from PIL import Image
EP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(EP, "grade", "grade.json")
#            target mean, saturation, contrast, gains (r, g, b), vignette
LOOK = {
    "field":   dict(mean=.44, sat=.92, con=.10, gain=(1.04, 1.00, .94), vig=.10),   # dawn: a touch warm
    "camp":    dict(mean=.45, sat=.86, con=.08, gain=(1.00, 1.00, .98), vig=.10),   # overcast day: neutral
    "road":    dict(mean=.27, sat=.80, con=.06, gain=(.92, 1.00, 1.10), vig=.16),   # moonlit night: blue, readable
    "radio":   dict(mean=.40, sat=.70, con=.10, gain=(1.00, .98, .94), vig=.14),   # warm lamp, not orange
    "cafe":    dict(mean=.44, sat=.72, con=.08, gain=(1.00, .98, .95), vig=.12),
    "photo":   dict(mean=.34, sat=.80, con=.10, gain=(.94, 1.00, 1.08), vig=.14),   # the enemy's cold room
    "river":   dict(mean=.28, sat=.70, con=.06, gain=(.94, 1.00, 1.08), vig=.14),
    "bedroom": dict(mean=.32, sat=.90, con=.06, gain=(.96, .98, 1.06), vig=.14),
    "attic":   dict(mean=.36, sat=.62, con=.08, gain=(1.00, .98, .95), vig=.12),   # golden afternoon, today
}
LUMA = np.array([.2126, .7152, .0722], np.float32)

def frame_places():
    cam = json.load(open(os.path.join(EP, "out", "plan", "camera_baked.json")))
    cam = cam.get("frames", cam) if isinstance(cam, dict) else cam
    return {c["f"]: c["place"] for c in cam}

def grade(x, lk, gam):
    x = x * np.array(lk["gain"], np.float32)
    L = np.clip(x @ LUMA, 1e-4, None); L2 = L ** gam; x = x * (L2 / L)[..., None]
    c = lk["con"]; x = x + c * (x - .5) * 4 * np.clip(x, 0, 1) * (1 - np.clip(x, 0, 1))
    L = (x @ LUMA)[..., None]; x = L + (x - L) * lk["sat"]
    x = .018 + .982 * np.clip(x, 0, None)                                  # black floor: dark detail stays readable
    x = np.where(x > .85, .85 + .15 * np.tanh((x - .85) / .15), x)           # soft highlight roll-off
    h, w = x.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]; r2 = ((xx / w - .5) ** 2 + (yy / h - .5) ** 2) / .5
    return np.clip(x * (1 - lk["vig"] * r2)[..., None], 0, 1)

def measure(a):
    L = a @ LUMA; hsv_s = (a.max(-1) - a.min(-1)) / np.clip(a.max(-1), 1e-4, None)
    return dict(mean=round(float(L.mean()), 3), sat=round(float(hsv_s.mean()), 3), crushed=round(float((L < .02).mean()), 4), burned=round(float((L > .985).mean()), 4))

def load(p): return np.asarray(Image.open(p).convert("RGB"), np.float32) / 255.0

def camera_speed():
    """measured screen speed (px/f at 720x1280) per frame from the baked camera: drives the motion blur on fast moves only"""
    sys.path.insert(0, os.path.join(EP, "..", "..", "tools")); import film_plan as fp
    cam = json.load(open(os.path.join(EP, "out", "plan", "camera_baked.json"))); cam = cam.get("frames", cam) if isinstance(cam, dict) else cam
    sp = fp.screen_speed(cam); return {c["f"]: (0 if c.get("cut") else sp[i]) for i, c in enumerate(cam)}

BLUR_FROM, BLUR_FULL, BLUR_MAX = 18.0, 55.0, .45     # px/f: no blur on rests and slow drifts; a shutter-like smear on whips and the crane
GRAIN = .010                                        # luma grain sigma: present on a phone, never noisy

if __name__ == "__main__":
    cmd = sys.argv[1]; places = frame_places()
    if cmd == "calibrate":
        cal = {}
        for p in sorted(glob.glob(os.path.join(sys.argv[2], "f_*.png"))):
            f = int(os.path.basename(p)[2:7]); pl = places[f]; lk = LOOK[pl]; a = load(p)
            lo, hi = .35, 2.5                                              # find the gamma that lands the place on its target mean
            for _ in range(24):
                g = (lo + hi) / 2; m = float(grade(a, lk, g) @ LUMA).mean() if False else float((grade(a, lk, g) @ LUMA).mean())
                if m > lk["mean"]: lo = g
                else: hi = g
            cal[pl] = round((lo + hi) / 2, 4); print(pl, f, "gamma", cal[pl], measure(a), "->", measure(grade(a, lk, cal[pl])))
        json.dump(cal, open(G, "w"), indent=1)
    elif cmd == "apply":
        cal = json.load(open(G)); src, dst = sys.argv[2], sys.argv[3]; os.makedirs(dst, exist_ok=True)
        files = sorted(glob.glob(os.path.join(src, "f_*.png")))
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 1; k = int(os.environ.get("GRADE_K", 0))
        sp = camera_speed(); byf = {int(os.path.basename(p)[2:7]): p for p in files}; done = 0
        for i, p in enumerate(files):
            if i % jobs != k: continue
            f = int(os.path.basename(p)[2:7]); pl = places.get(f, "field"); a = load(p)
            w = BLUR_MAX * min(1.0, max(0.0, (sp.get(f, 0) - BLUR_FROM) / (BLUR_FULL - BLUR_FROM)))
            if w > 0 and f - 1 in byf and f + 1 in byf and places.get(f - 1) == pl and places.get(f + 1) == pl and sp.get(f - 1, 0) > 0 and sp.get(f + 1, 0) > 0:
                a = (1 - w) * a + w * .5 * (load(byf[f - 1]) + load(byf[f + 1]))      # motion blur from the neighbours (never across a cut)
            g = grade(a, LOOK[pl], cal[pl]); rng = np.random.default_rng(f)
            g = np.clip(g + rng.normal(0, GRAIN, g.shape[:2])[..., None].astype(np.float32), 0, 1)
            Image.fromarray((g * 255 + .5).astype(np.uint8)).save(os.path.join(dst, os.path.basename(p))); done += 1
        if jobs == 1:   # Production Intelligence gate G reads this: the grade really ran over every frame of the edit
            json.dump(dict(src=os.path.abspath(src), dst=os.path.abspath(dst), frames_graded=done, places=sorted(set(places.values())), calibration=cal), open(os.path.join(EP, "grade", "grade_log.json"), "w"), indent=1)
    elif cmd == "measure":
        for p in sorted(glob.glob(os.path.join(sys.argv[2], "f_*.png"))):
            f = int(os.path.basename(p)[2:7]); print(os.path.basename(p), places.get(f), measure(load(p)))
