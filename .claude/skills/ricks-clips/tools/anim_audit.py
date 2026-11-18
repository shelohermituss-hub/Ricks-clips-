"""Animation audit (generic, Production Intelligence gate D): classifies every character act in film.json by the method
that animates it, and measures moves. Promoted from the Ghost Army audit (2026-11-18, lessons PI-001, PI-003).
  .venv/bin/python tools/anim_audit.py episodes/<name>/film.json [--json out.json]
  exit 0 = no STATIC / WALK2F / GLIDE / OVERLAP; exit 1 = at least one (the table says which)
Method classes (CB_RULES section 5 + 'NEVER A STATIC KIT POSE'):
  LIBRARY   pose is a registered motion-library move m:<id> (plays through time; breath/blink/follow-through layered on)
  STATIC    a plain kit pose (stand, knock, hold_up ...): a frozen drawing, blocking stand-in only
  WALK2F    position move with walk=True: the planner's 2-frame step toggle (forbidden stand-in walk)
  GLIDE     position move with no walking legs (slides over the ground)
  POP       position change in <= 2 frames inside a shot (teleport) unless hidden by a cut or a place change"""
import json, os, sys, re, math
if len(sys.argv) < 2: print(__doc__); sys.exit(2)
FILM = os.path.abspath(sys.argv[1]); EP = os.path.dirname(FILM); ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = json.load(open(FILM))
words = json.load(open(os.path.join(EP, "voice", "words.json"))); fps = F["fps"]
def wt(at):
    if isinstance(at, (int, float)): return at / fps
    w, n = at[0], at[1]; off = at[2] if len(at) > 2 else 0; k = 0
    for x in words:
        if re.sub(r"[^a-z\-é']", "", x["w"].lower()) == w.lower():
            k += 1
            if k == n: return x["s"] + off / fps
    return None
import subprocess
lib = set(json.loads(subprocess.run(["node", "-e", "import('./library.mjs').then(m=>console.log(JSON.stringify(m.LIB.map(e=>e.id))))"], cwd=os.path.join(ROOT, "templates", "motion_styles"), capture_output=True, text=True).stdout))
last = {}; rows = []; curpose = {}
for a in sorted(F["acts"], key=lambda a: wt(a["at"]) or 0):
    t = wt(a["at"]); who = a["who"]; pose = a.get("pose") or None; cls = []
    if pose: curpose[who] = pose
    eff = curpose.get(who, "")
    if pose:
        if pose.startswith("m:"):
            mid = re.match(r"m:([^@+]+)", pose).group(1); cls.append("LIBRARY" if mid in lib else "LIBRARY?missing")
            if "@=" in pose: cls.append("FROZEN-MOVE")
        else: cls.append("STATIC")
    if "pos" in a and who in last:
        p0 = last[who]; d = math.dist(p0[:2], a["pos"][:2]); ms = a.get("move_s", .5)
        if d > .05:
            if a.get("place") and a.get("place") != (last.get(who + "_place")): cls.append("PLACE-CHANGE(hidden)")
            elif ms <= 2 / fps: cls.append("POP")
            elif a.get("walk"): cls.append("WALK2F %.1fm" % d)
            elif not re.match(r"m:(walk|run|bike)", eff): cls.append("GLIDE %.1fm in %.2fs" % (d, ms))
    if "pos" in a: last[who] = a["pos"]
    if a.get("place"): last[who + "_place"] = a["place"]
    rows.append(dict(t=round(t, 2) if t is not None else None, who=who, at=a["at"], pose=pose, face=a.get("face"), cls=cls))
for r in rows: print("%6s  %-15s %-28s %-22s %s" % (r["t"], r["who"], (r["pose"] or "")[:28], (r["face"] or "")[:22], " ".join(r["cls"])))
from collections import Counter
c = Counter(x.split()[0] for r in rows for x in r["cls"]); print("\nTOTALS", dict(c), "acts", len(rows), "| film.tween:", F.get("tween"), "| motion_polish:", F.get("motion_polish"))
OUTJ = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
# OVERLAP: a move (walk/run/position change) still travelling when the same character's next posed beat starts
acts = sorted(F["acts"], key=lambda a: wt(a["at"]) or 0); bad = []
for i, a in enumerate(acts):
    if "pos" not in a or a.get("move_s", .5) <= .05: continue
    t0 = wt(a["at"]); t1 = t0 + a.get("move_s", .5)
    for b in acts[i + 1:]:
        if b["who"] == a["who"] and (b.get("pose") or "pos" in b):
            tb = wt(b["at"])
            if tb < t1 - 1 / fps and not (b.get("pose", "").startswith(("m:idle", "m:lift/C", "m:push", "m:board", "m:sweep", "m:bike")) and abs(tb - t1) < 2 / fps): bad.append("%s: move %.2f-%.2fs overlaps the beat at %.2fs (%s)" % (a["who"], t0, t1, tb, b.get("pose")))
            break
print("\nOVERLAPS", len(bad)); [print("  " + x) for x in bad]

verdict = {k: c.get(k, 0) for k in ("STATIC", "WALK2F", "GLIDE", "POP", "LIBRARY")}; verdict["OVERLAP"] = len(bad); verdict["acts"] = len(rows)
verdict["status"] = "FAIL" if (verdict["STATIC"] or verdict["WALK2F"] or verdict["GLIDE"] or verdict["OVERLAP"]) else ("WARN" if verdict["POP"] else "PASS")
print("VERDICT", json.dumps(verdict))
if OUTJ: json.dump(dict(verdict=verdict, acts=rows, overlaps=bad), open(OUTJ, "w"), indent=1)
sys.exit(1 if verdict["status"] == "FAIL" else 0)
