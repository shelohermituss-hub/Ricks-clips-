"""A pose change leaves 3-4 EMPTY drawings (the card would blink out: a POP). Each empty drawing is replaced by the last drawing before it.
    python3 shots/fix_cards.py [02 ...]"""
import json, os, shutil, sys, glob
import numpy as np
from PIL import Image
EP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for d in sorted(glob.glob(os.path.join(EP, "build", "cards_s*"))):
    if sys.argv[1:] and d[-2:] not in sys.argv[1:]: continue
    for w in sorted(os.listdir(os.path.join(d, "cards"))):
        f = os.path.join(d, "cards", w); ip = os.path.join(f, "index.json")
        if not os.path.exists(ip): continue
        I = json.load(open(ip)); last = None; n = 0
        for r in sorted(I["runs"], key=lambda r: r["f0"]):
            fn = os.path.join(f, I["images"][r["img"] - 1]["file"])
            if (np.asarray(Image.open(fn).getchannel("A")) > 128).any(): last = fn
            elif last: shutil.copyfile(last, fn); n += 1
        if n: print("FIXED", d[-2:], w, n, "empty drawings")
