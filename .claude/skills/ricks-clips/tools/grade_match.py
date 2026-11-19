"""GRADE MATCH (CB 2026-11-19: "le color grading que tu appliques à notre vidéo doit être similaire à celui de la référence").
Compares our key frames with the reference frames at the same time: luma, saturation, contrast (std of luma), for the whole frame.
Use it on every shot's key frames before a preview; adjust exposure / view transform / grade saturation until each value is within
the tolerance (default: luma 0.06, saturation 0.08, contrast 0.05).
    python3 tools/grade_match.py <reference.mp4> <frame>:<our.png> [<frame>:<our.png> ...] [--fps 30] [--sheet out.jpg]
Exit 1 when a frame is out of tolerance (it is a check, not a fix). Measured settings for crash_instinct: Standard + Medium Contrast,
exposure -0.3, grade saturation 1.0, HDRI sky visible, backlit sun, bounce fill (demos/crash_instinct/sets/roadside.py)."""
import subprocess, sys, tempfile, os
import numpy as np
from PIL import Image

TOL = {"luma": .06, "sat": .08, "contrast": .05}

def stats(img):
    a = np.asarray(img.convert("RGB")).astype(float) / 255; lum = (a * [.2126, .7152, .0722]).sum(2)
    mx, mn = a.max(2), a.min(2); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return {"luma": float(lum.mean()), "sat": float(sat.mean()), "contrast": float(lum.std())}

def ref_frame(video, f, fps, size):
    p = os.path.join(tempfile.mkdtemp(), "r.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.4f" % (f / fps + .001), "-i", video, "-frames:v", "1", "-vf", "scale=%d:%d" % size, p], check=True)
    return Image.open(p)

def main(argv):
    fps = float(argv[argv.index("--fps") + 1]) if "--fps" in argv else 30.0
    sheet = argv[argv.index("--sheet") + 1] if "--sheet" in argv else None
    pairs = [a for a in argv[1:] if ":" in a and not a.startswith("--")]
    video = argv[0]; ok = True; tiles = []
    for p in pairs:
        f, path = p.split(":", 1); f = int(f); ours = Image.open(path).convert("RGB"); ref = ref_frame(video, f, fps, ours.size)
        R, O = stats(ref), stats(ours); bad = [k for k in TOL if abs(O[k] - R[k]) > TOL[k]]; ok &= not bad
        print("%s frame %d  REF luma %.2f sat %.2f contrast %.2f | OURS luma %.2f sat %.2f contrast %.2f %s" % (
            "FAIL" if bad else "PASS", f, R["luma"], R["sat"], R["contrast"], O["luma"], O["sat"], O["contrast"], ("out: " + ", ".join(bad)) if bad else ""))
        tiles.append((ref, ours))
    if sheet and tiles:
        w, h = tiles[0][1].size; S = Image.new("RGB", (w * len(tiles), h * 2))
        for i, (r, o) in enumerate(tiles): S.paste(r.resize((w, h)), (i * w, 0)); S.paste(o, (i * w, h))
        S.save(sheet, quality=88); print("SHEET", sheet)
    print("GRADE MATCH", "PASS" if ok else "FAIL"); return 0 if ok else 1

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
