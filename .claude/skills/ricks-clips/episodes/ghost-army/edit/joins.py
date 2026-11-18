"""THE GHOST ARMY: the joins between takes (V3 step 8, 2026-11-18). Reads film.json "joins" (one per incoming take) and the baked camera
(out/plan/camera_baked.json, the first frame of every take) and writes a frame folder where every 'dissolve' join is a short blend:
the last frame of the outgoing take (held, it is at the end of a push or a slow rest) melts into the first n frames of the incoming take.
'cut' joins are left as they are (each one carries its reason in film.json). Nothing is shortened: the film keeps every frame and its length.
    .venv/bin/python episodes/ghost-army/edit/joins.py <in_frames> <out_frames>      (f_#####.png in both)
Writes edit/joins_log.json {joins applied, frames blended}."""
import json, os, sys, glob, shutil
import numpy as np
from PIL import Image
EP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def main(src, dst):
    film = json.load(open(os.path.join(EP, "film.json"))); cam = json.load(open(os.path.join(EP, "out", "plan", "camera_baked.json")))["frames"]
    first = {}
    for c in cam: first.setdefault(c["take"], c["f"])
    os.makedirs(dst, exist_ok=True); files = sorted(glob.glob(os.path.join(src, "f_*.png")))
    for p in files:
        q = os.path.join(dst, os.path.basename(p))
        if not os.path.exists(q): shutil.copyfile(p, q)
    log = []
    for j in film.get("joins", []):
        c = first.get(j["take"]); n = int(j.get("frames", 0))
        if c is None or c == 0: continue
        if j["kind"] != "dissolve" or n <= 0: log.append(dict(take=j["take"], at=c, kind=j["kind"], why=j.get("why"))); continue
        A = np.asarray(Image.open(os.path.join(src, "f_%05d.png" % (c - 1))).convert("RGB"), np.float32)
        for i in range(n):
            f = c + i; w = (i + 1) / (n + 1.0); w = w * w * (3 - 2 * w)
            B = np.asarray(Image.open(os.path.join(src, "f_%05d.png" % f)).convert("RGB"), np.float32)
            Image.fromarray(np.clip((1 - w) * A + w * B + .5, 0, 255).astype(np.uint8)).save(os.path.join(dst, "f_%05d.png" % f))
        log.append(dict(take=j["take"], at=c, kind="dissolve", frames=n, why=j.get("why")))
    json.dump(dict(src=os.path.abspath(src), dst=os.path.abspath(dst), joins=log), open(os.path.join(EP, "edit", "joins_log.json"), "w"), indent=1)
    print("joins:", ", ".join("%s@%d %s%s" % (x["take"], x["at"], x["kind"], (" %d f" % x["frames"]) if x.get("frames") else "") for x in log))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
