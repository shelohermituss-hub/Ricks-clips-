"""Card characters of every shot (local frames, 0 = first frame of the shot). Pure data + the bake:
    python3 shots/cast.py [02 05 ...]     bakes build/cards_sNN with tools/card_service.py (skipped when the tracks did not change)
Each act: (who, at, pose, face, view, dir). The cards are drawn standing at the origin; the shot script moves them in the 3D set."""
import json, os, subprocess, sys, hashlib
EP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); SKILL = os.path.abspath(os.path.join(EP, "..", ".."))
P = lambda puppet, h=1.75: {"puppet": "cast:" + puppet, "height": h}
SHOTS = {   # id: (length in frames, cast, acts)
 "01": (68, {"engineer": P("fort_engineer", 2.25)}, [("engineer", 0, "m:push/A", "k:concentrate", "side", 1)]),
 "02": (112, {"general": P("enemy_general", 2.5), "bearer_a": P("enemy_soldier", 1.6), "bearer_b": P("enemy_soldier", 1.6), "bearer_c": P("enemy_soldier", 1.6), "crowd": P("enemy_soldier", 1.6)},
        [("general", 0, "m:idle/B", "k:annoyed", "front", 1), ("general", 78, "m:idle/B", "k:annoyed", "front", 1),
         ("bearer_a", 0, "m:walk/A", "k:annoyed", "front", 1), ("bearer_b", 0, "m:walk/A", "k:annoyed", "front", 1), ("bearer_c", 0, "m:walk/A", "k:annoyed", "front", 1),
         ("bearer_a", 78, "m:walk/A", "k:annoyed", "front", 1), ("bearer_b", 78, "m:walk/A", "k:annoyed", "front", 1), ("bearer_c", 78, "m:walk/A", "k:annoyed", "front", 1),
         ("crowd", 0, "m:walk/A", "k:annoyed", "front", 1)]),
}

def tracks(sid):
    n, cast, acts = SHOTS[sid]
    return {"title": "cart_army shot " + sid, "fps": 30, "end": n + 8, "cast": cast,
            "acts": [{"who": w, "at": at, "pos": [0, 0, 0], "view": v, "dir": d, "pose": pose, "face": face, "move_s": .01} for w, at, pose, face, v, d in acts]}

def bake(sid):
    out = os.path.join(EP, "build", "cards_s" + sid); T = tracks(sid); h = hashlib.md5(json.dumps(T, sort_keys=True).encode()).hexdigest(); stamp = os.path.join(out, "tracks.md5")
    if os.path.exists(stamp) and open(stamp).read() == h: print("CARDS", sid, "up to date"); return out
    os.makedirs(out, exist_ok=True); tj = os.path.join(EP, "build", "tracks_s%s.json" % sid); json.dump(T, open(tj, "w"), indent=1)
    r = subprocess.run([sys.executable, os.path.join(SKILL, "tools", "card_service.py"), tj, out], capture_output=True, text=True)
    if r.returncode != 0: print("CARDS", sid, "FAILED\n", (r.stdout + r.stderr)[-1500:]); return None
    open(stamp, "w").write(h); print("CARDS", sid, "ok", (r.stdout.strip().splitlines() or [""])[-1][:160]); return out

if __name__ == "__main__":
    for s in (sys.argv[1:] or sorted(SHOTS)): bake(s)
