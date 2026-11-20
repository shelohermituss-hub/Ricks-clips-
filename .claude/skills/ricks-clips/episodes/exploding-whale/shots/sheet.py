"""contact sheet of a shot's key frames: python3 shots/sheet.py <shot id>  ->  build/k/sheet_sNN.jpg (+ colour measures)"""
import sys, glob, os
import numpy as np
from PIL import Image, ImageDraw
EP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sid = sys.argv[1]
fs = sorted(glob.glob(os.path.join(EP, "build", "k", "s%s_*.png" % sid))); ims = []
for f in fs:
    im = Image.open(f).convert("RGB").resize((270, 480)); a = np.asarray(im).astype(float) / 255; lum = (a * [.2126, .7152, .0722]).sum(2); mx, mn = a.max(2), a.min(2)
    print("%s luma %.2f sat %.2f contrast %.2f" % (os.path.basename(f), lum.mean(), np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean(), lum.std()))
    ImageDraw.Draw(im).text((6, 4), os.path.basename(f)[4:7], fill=(255, 255, 0)); ims.append(im)
W = Image.new("RGB", (270 * len(ims), 480)); [W.paste(im, (270 * i, 0)) for i, im in enumerate(ims)]; W.save(os.path.join(EP, "build", "k", "sheet_s%s.jpg" % sid), quality=88)
