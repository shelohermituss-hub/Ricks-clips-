"""Card anchors (CB rule 2026-11-19 "everything happens through an action"): where the HEAD and the FEET of a drawn character are on every
frame, measured on the drawings themselves, so a 3D prop can sit exactly on the drawn head (a helmet) and a jump can keep its path.
    python3 tools/card_anchors.py <cards/<who> folder> [--head-window 0.12]
Writes <folder>/anchors.json: {"<frame>": {"head_top": z, "head_x": x, "feet": z, "hands": [[x, z], [x, z]]}} in the card's local metres
(x from the card centre, z up from the card's ground line), the same space as index.json "hands".
head_top = highest inked row inside a narrow window around the head column (hands raised wide stay outside the window);
feet = lowest inked row (0 when standing, > 0 when the drawing itself is in the air).
It also lists POSE POPS: on a change of move (pose id) a hand that jumps > 0.9 m (faster than the motion library's own fastest swing,
0.83 m/frame in jump/joy) or the feet > 0.2 m in ONE frame = the new move did not
ease in (the move-to-move blend only works when both moves are drawn in the SAME view: puppets.mjs moveOf). continuity.py fails on them."""
import json, os, sys
import numpy as np
from PIL import Image

def anchors(folder, win=.12):
    I = json.load(open(os.path.join(folder, "index.json"))); k = I["metres_per_px"]; w, h = I["px"]; g = I["ground_px"]; cx = I.get("centre_px", w / 2)
    cache, out = {}, {}
    for r in I["runs"]:
        fn = I["images"][r["img"] - 1]["file"]
        if fn not in cache:
            a = np.asarray(Image.open(os.path.join(folder, fn)).getchannel("A")) > 128
            rows = np.where(a.any(1))[0]; feet = (g - rows.max()) * k if rows.size else 0.
            x0, x1 = int(cx - win / k), int(cx + win / k); band = a[:, max(0, x0):x1]; br = np.where(band.any(1))[0]
            top = int(br.min()) if br.size else int(rows.min()); cols = np.where(a[top + int(.04 / k)])[0] if br.size else np.array([cx])
            cols = cols[(cols > x0 - .1 / k) & (cols < x1 + .1 / k)] if cols.size else cols
            cache[fn] = {"head_top": round((g - top) * k, 4), "head_x": round(((cols.min() + cols.max()) / 2 - cx) * k, 4) if cols.size else 0., "feet": round(feet, 4)}
        pose = (I["images"][r["img"] - 1].get("keys") or ["|||"])[0].split("|")[3]
        for f in range(r["f0"], r["f1"] + 1): out[str(f)] = cache[fn] | {"hands": r.get("hands"), "pose": pose}
    pops = []
    for f in sorted(int(x) for x in out)[1:]:
        a, b = out.get(str(f - 1)), out[str(f)]
        if not a or a["pose"] == b["pose"] or not a["hands"] or not b["hands"]: continue
        hs = max(((h0[0] - h1[0]) ** 2 + (h0[1] - h1[1]) ** 2) ** .5 for h0, h1 in zip(a["hands"], b["hands"]))
        if hs > .9 or abs(a["feet"] - b["feet"]) > .2: pops.append({"frame": f, "from": a["pose"], "to": b["pose"], "hand_step_m": round(hs, 3), "feet_step_m": round(float(abs(a["feet"] - b["feet"])), 3)})
    out["_pose_pops"] = pops
    json.dump(out, open(os.path.join(folder, "anchors.json"), "w"), indent=0); return out

if __name__ == "__main__":
    a = sys.argv[1:]; A = anchors(a[0], float(a[a.index("--head-window") + 1]) if "--head-window" in a else .12)
    print("anchors", len(A) - 1, "frames ->", os.path.join(a[0], "anchors.json"), "| pose pops:", A["_pose_pops"])
