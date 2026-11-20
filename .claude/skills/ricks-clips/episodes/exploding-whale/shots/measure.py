"""Colour check of our frames against the DAYLIGHT range measured on the reference videos (references/style_analysis/data/*/per_second.json,
seconds with luma > .38 of V02, V04, V05): luma .40-.58, saturation .26-.48, contrast .16-.25 (10th-90th percentile).
    python3 episodes/exploding-whale/shots/measure.py <png> [<png> ...]      exit 1 when a frame is outside the range"""
import sys, numpy as np
from PIL import Image
R = {"luma": (.40, .58), "sat": (.26, .48), "contrast": (.16, .25)}; ok = True
for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert("RGB").resize((90, 160))).astype(float) / 255; lum = (a * [.2126, .7152, .0722]).sum(2); mx, mn = a.max(2), a.min(2)
    v = {"luma": lum.mean(), "sat": np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean(), "contrast": lum.std()}
    bad = [k for k in R if not R[k][0] <= v[k] <= R[k][1]]; ok &= not bad
    print("%s %s luma %.2f sat %.2f contrast %.2f %s" % ("FAIL" if bad else "PASS", f.split("/")[-1], v["luma"], v["sat"], v["contrast"], "out: " + ", ".join(bad) if bad else ""))
print("COLOUR", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
