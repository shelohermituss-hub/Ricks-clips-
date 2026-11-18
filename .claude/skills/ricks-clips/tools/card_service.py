"""Character card service (deliverable 5, 2026-11-18): drawings of 2D cast characters for a Blender scene, WITHOUT a film.
    python3 tools/card_service.py <tracks.json> <out folder>
tracks.json:
  {"fps": 30, "end": 450,
   "cast": {"farmer": {"puppet": "cast:farmer", "height": 1.75}, ...},          # any of the 150-character cast (templates/vector2d_characters)
   "acts": [{"who": "farmer", "at": 0, "pos": [x, y, 0], "view": "side|34|front|back", "dir": 1|-1,
             "pose": "m:walk/A" (motion library id) | "stand", "face": "k:happy", "move_s": 1.0}, ...]}
What it does (reusing the proven tools, no new drawing code): writes <out>/plan/film.json (the generic kit set "platform", one static
station, no voice), bakes it with tools/film_plan.py (motion library moves, in-betweens, faces, mouths, blinks) and exports the drawings
with templates/threejs_film/render_gpu.mjs --export-lock --cards-only (content cache: unchanged drawings are copied, not redrawn).
Output: <out>/cards/<who>/s####.png + index.json (runs with position, visibility and HAND positions), read by rc.characters."""
import json, os, shutil, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(tracks, out):
    T = json.load(open(tracks)); plan = os.path.join(out, "plan"); os.makedirs(plan, exist_ok=True)
    acts = [dict(a, place="yard") for a in T["acts"]]
    F = {"title": T.get("title", "card service"), "fps": T.get("fps", 30), "size": [1080, 1920], "end": T["end"],
         "puppet_pkg": [os.path.relpath(os.path.join(SKILL, "templates", "vector2d_characters", "code"), plan)],
         "cast": T["cast"], "places": {"yard": {"set": "platform", "light": "day"}},
         "takes": [{"id": "t0", "place": "yard", "stations": [{"at": 0, "pos": [0, -12, 1.6], "aim": [0, 0, 1.0], "lens": 30, "framing": "W", "hold": 0.0}]}],
         "acts": acts, "tween": T.get("tween", {"ones": True, "move_blend": 6}), "motion_polish": T.get("motion_polish", {"enabled": True, "head_follow": .14, "hand_follow": .08, "breath": .55, "breath_rate": 2.15, "auto_blink": True})}
    json.dump(F, open(os.path.join(plan, "film.json"), "w"), indent=1)
    r = subprocess.run([sys.executable, os.path.join(SKILL, "tools", "film_plan.py"), "bake", os.path.join(plan, "film.json")], capture_output=True, text=True)
    if r.returncode != 0: raise SystemExit("film_plan bake failed:\n" + (r.stdout + r.stderr)[-2000:])
    lock = os.path.join(out, "lock"); who = ",".join(T["cast"])
    r = subprocess.run(["node", os.path.join(SKILL, "templates", "threejs_film", "render_gpu.mjs"), "film.json", "--export-lock", "--cards-only", "--who", who,
                        "--lock-dir", lock, "--cache", os.path.join(out, ".puppet_cache")], cwd=plan, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith("cards ")]
    if r.returncode != 0 or not lines: raise SystemExit("card export failed:\n" + (r.stdout + r.stderr)[-2000:])
    cards = os.path.join(out, "cards")
    if os.path.exists(cards): shutil.rmtree(cards)
    shutil.copytree(os.path.join(lock, "cards"), cards); shutil.rmtree(os.path.join(out, ".puppet_cache"), ignore_errors=True)
    print("\n".join(lines)); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
