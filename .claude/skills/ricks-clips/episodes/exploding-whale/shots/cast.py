"""Card characters of every shot (local frames, 0 = first frame of the shot). Pure data + the bake:
    python3 shots/cast.py [02 05 ...]     bakes build/cards_sNN with tools/card_service.py (skipped when the tracks did not change)
Each act: (who, at, pose, face, view, dir). The cards are drawn standing at the origin; the shot script moves them in the 3D set."""
import json, os, subprocess, sys, hashlib
EP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); SKILL = os.path.abspath(os.path.join(EP, "..", ".."))
P = lambda puppet, h=1.75: {"puppet": "cast:" + puppet, "height": h}
SHOTS = {   # id: (length in frames, cast, acts)
 "02": (214, {"surveyor": P("construction", 1.78), "jogger": P("aerobics", 1.72)},
        [("surveyor", 0, "m:walk/A", "k:concentrate", "side", 1), ("surveyor", 112, "m:inspect/A", "k:surprised", "side", 1),
         ("jogger", 0, "m:run/A", "k:happy", "side", -1), ("jogger", 176, "m:fall/A", "k:shocked", "side", -1)]),
 "03": (176, {"clerk_a": P("clerk", 1.7), "clerk_b": P("business", 1.76), "clerk_c": P("clerk", 1.74)},
        [("clerk_a", 0, "m:phone/A", "k:nervous", "front", 1), ("clerk_a", 30, "m:shrug/A", "k:smug", "front", 1),
         ("clerk_b", 0, "m:desk/A", "k:standard", "front", 1), ("clerk_b", 36, "m:phone/A", "k:nervous", "front", 1), ("clerk_b", 70, "m:shrug/A", "k:smug", "front", 1),
         ("clerk_c", 0, "m:desk/A", "k:standard", "front", 1), ("clerk_c", 84, "m:phone/A", "k:confused", "front", 1), ("clerk_c", 132, "m:shrug/A", "k:confused", "front", 1)]),
 "04": (125, {"engineer": P("engineer", 1.78)}, [("engineer", 0, "m:board/A", "k:proud", "side", 1), ("engineer", 84, "m:thumbs/A", "k:proud", "front", 1)]),
 "05": (72, {"veteran": P("veteran", 1.74), "farmer": P("farmer", 1.76), "teacher": P("teacher", 1.68), "bbqdad": P("bbqdad", 1.8)},
        [("veteran", 0, "m:idle/A", "k:standard", "34", 1), ("veteran", 26, "m:react/idea", "k:standard", "34", 1),
         ("farmer", 0, "m:idle/A", "k:standard", "34", 1), ("farmer", 40, "m:idle/A", "k:surprised", "34", -1),
         ("teacher", 0, "m:idle/B", "k:nervous", "front", 1), ("teacher", 44, "m:idle/A", "k:surprised", "34", -1), ("bbqdad", 0, "m:idle/B", "k:annoyed", "front", 1)]),
 "06": (57, {"veteran": P("veteran", 1.74), "engineer": P("engineer", 1.78)},
        [("veteran", 0, "m:idle/B", "k:standard", "front", 1), ("engineer", 0, "m:idle/B", "k:smug", "front", 1), ("engineer", 28, "m:laugh/A", "k:laugh", "front", 1)]),
 "07": (109, {"worker": P("worker", 1.76), "farmer": P("farmer", 1.76), "teacher": P("teacher", 1.68), "bbqdad": P("bbqdad", 1.8), "soccermom": P("soccermom", 1.7)},
        [("worker", 0, "m:wave/A", "k:concentrate", "side", 1)] + [(w, 0, "m:idle/B", "k:nervous", "front", 1) for w in ("farmer", "teacher", "bbqdad", "soccermom")]
        + [(w, 52 + 3 * i, "m:walk/A", "k:nervous", "side", 1) for i, w in enumerate(("farmer", "teacher", "bbqdad", "soccermom"))]),
 "08": (116, {"reporter": P("reporter", 1.78), "cameraman": P("cameraman", 1.74), "farmer": P("farmer", 1.76), "teacher": P("teacher", 1.68)},
        [("reporter", 0, "m:idle/B", "k:proud", "front", 1), ("reporter", 54, "m:react/backaway", "k:shocked", "side", 1), ("reporter", 80, "m:cheer/A", "k:happy", "front", 1),
         ("cameraman", 0, "m:inspect/A", "k:concentrate", "side", -1),
         ("farmer", 0, "m:idle/B", "k:nervous", "front", 1), ("farmer", 66, "m:cheer/A", "k:happy", "front", 1), ("teacher", 0, "m:idle/B", "k:nervous", "front", 1), ("teacher", 70, "m:cheer/B", "k:happy", "front", 1)]),
 "10": (143, {"farmer": P("farmer", 1.76), "teacher": P("teacher", 1.68), "soccermom": P("soccermom", 1.7), "bbqdad": P("bbqdad", 1.8)},
        [("farmer", 0, "m:run/A", "k:shocked", "side", 1), ("teacher", 0, "m:run/B", "k:shocked", "side", -1), ("soccermom", 0, "m:run/A", "k:shocked", "side", 1),
         ("bbqdad", 0, "m:idle/B", "k:shocked", "front", 1), ("bbqdad", 30, "m:fall/A", "k:shocked", "side", 1)]),
 "11": (42, {"veteran": P("veteran", 1.74)}, [("veteran", 0, "m:idle/B", "k:annoyed", "front", 1)]),
 "12": (85, {"veteran": P("veteran", 1.74)}, [("veteran", 0, "m:idle/B", "k:annoyed", "front", 1), ("veteran", 50, "m:facepalm/A", "k:annoyed", "front", 1)]),
 "14": (94, {"engineer": P("engineer", 1.78), "worker": P("worker", 1.76)},
        [("engineer", 0, "m:idle/B", "k:confused", "front", 1), ("engineer", 22, "m:shrug/A", "k:confused", "front", 1), ("worker", 0, "m:drive/A", "k:annoyed", "side", 1)]),
 "15": (71, {"ranger": P("scout", 1.76)}, [("ranger", 0, "m:hammer/A", "k:concentrate", "side", 1)]),
 "16": (126, {"engineer": P("engineer", 1.78)}, [("engineer", 0, "m:idle/B", "k:proud", "front", 1), ("engineer", 78, "m:thumbs/A", "k:proud", "front", 1)]),
}

def tracks(sid):
    n, cast, acts = SHOTS[sid]
    return {"title": "exploding-whale shot " + sid, "fps": 30, "end": n + 8, "cast": cast,
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
