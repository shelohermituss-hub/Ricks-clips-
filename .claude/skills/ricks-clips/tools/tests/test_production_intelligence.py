"""Regression tests for the Production Intelligence layer (2026-11-18). Each test reproduces a real defect from Ghost Army.
    .venv/bin/python tools/tests/test_production_intelligence.py        (prints PASS/FAIL per test, exit 1 on any FAIL)
Needs: node (motion library ids), ffprobe not required. Uses episodes/ghost-army and episodes/_pi_test (symlinked smoke episode)."""
import json, os, sys, subprocess, tempfile, shutil, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); os.chdir(ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
PY = sys.executable; GA = "episodes/ghost-army"; R = []
def t(name, fn):
    try: ok, why = fn()
    except Exception as e: ok, why = False, "exception: %r" % e
    R.append((name, ok)); print("%s  %s  %s" % ("PASS" if ok else "FAIL", name, why))
def run(*a): p = subprocess.run(list(a), capture_output=True, text=True); return p.returncode, p.stdout + p.stderr

# PI-002: an inline // comment swallowed code (shell bursts, river moonlight vanished) -> lint
def lint_fixture():
    c, o = run(PY, "tools/lint_set_modules.py", "tools/tests/fixtures/swallowed_comment.js")
    n = o.count("comment swallows code"); return c == 1 and n == 3, "fixture: exit %s, %d flagged (want 1, 3: the 2 clean lines must pass)" % (c, n)
def lint_current():
    c, o = run(PY, "tools/lint_set_modules.py", GA + "/sets/ghost.js"); return c == 0, o.strip().splitlines()[-1]

# PI-001: 40/64 static kit poses + glides in v1 -> anim_audit FAIL; current film PASS
def anim_v1_fails():
    c, o = run("git", "show", "c3937a0:.claude/skills/ricks-clips/episodes/ghost-army/film.json")
    if c != 0: return False, "git history not available: " + o[:120]
    p = "episodes/_pi_test/film_v1_for_test.json"; open(p, "w").write(o)
    try: c, out = run(PY, "tools/anim_audit.py", p, "--json", "/tmp/_v1audit.json")
    finally: os.remove(p)
    v = json.load(open("/tmp/_v1audit.json"))["verdict"]; return c == 1 and v["STATIC"] >= 30, "v1 verdict %s" % v
def anim_current_passes():
    c, o = run(PY, "tools/anim_audit.py", GA + "/film.json"); return c == 0 and '"status": "PASS"' in o, o.strip().splitlines()[-1][:200]

# PI-003: a figure entering a new place slid from its old coordinates for 0.5 s -> film_plan lands it at once
def place_entry_no_slide():
    from film_plan import load, bake_performance, perf_at
    F = json.load(open(GA + "/film.json"))
    for a in F["acts"]:
        if a.get("place") and "pos" in a: a.pop("move_s", None)          # the old default would slide 0.5 s
    tmp = GA + "/_film_entry_test.json"; json.dump(F, open(tmp, "w"))
    try:
        F2 = load(tmp); P = bake_performance(F2); worst = 0.0; where = None
        for who, runs in P.items():
            prev = None
            for f in range(F2["end"]):
                s = perf_at(runs, f)
                if prev and s.get("place") == prev.get("place") and s["visible"] and prev["visible"]:
                    d = math.dist(s["pos"][:2], prev["pos"][:2])
                    if 0.25 < d < 5 and not str(s["pose"]).startswith(("m:walk", "m:run", "m:bike")):   # a multi-frame slide step (not a 1-frame landing, not a walk)
                        if d > worst: worst, where = d, (who, f)
                prev = s
        return worst == 0.0, "largest non-walk per-frame slide inside a place: %.2f m at %s" % (worst, where)
    finally: os.remove(tmp)

# Controller: memory is never overwritten; statuses are honest; promotion needs proof
def controller_init_idempotent():
    p = GA + "/production/QA_LOG.json"; before = open(p).read(); c, o = run(PY, "tools/production_controller.py", "init", GA)
    return c == 0 and open(p).read() == before, "QA_LOG unchanged after re-init"
def controller_gates_honest():
    c, o = run(PY, "tools/production_controller.py", "gates", GA, "--phase", "final")
    G = json.load(open(GA + "/production/GATES.json"))["results"]; st = {r["status"] for r in G}
    hero = next(r for r in G if r["check"] == "hero_assets_not_placeholder")
    return st <= {"PASS", "WARN", "FAIL", "NOT_RUN"} and hero["status"] == "FAIL" and c == 1, "final phase: hero gate %s (the primitive-assembly tank must FAIL), exit %s" % (hero["status"], c)
def promote_refuses_without_proof():
    les = {"id": "PI-TEST-NOPROOF", "date": "2026-11-18", "problem": "test", "root_cause": "test", "fix": "test", "verification": {"tests": []}, "status": "proposed"}
    mem = "memory/lessons_learned.json"; keep = open(mem).read(); f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(les, f); f.close()
    try:
        run(PY, "tools/production_controller.py", "lesson-add", f.name); c, o = run(PY, "tools/production_controller.py", "lesson-promote", "PI-TEST-NOPROOF")
        return c == 1 and "REFUSED" in o, o.strip()[:160]
    finally: open(mem, "w").write(keep); run(PY, "-c", "import sys; sys.path.insert(0,'tools'); import production_controller as p; p.write_lessons_md()")

# Asset gate: the renderer inventory sees the hero and measures it
def inventory_measures_hero():
    inv = json.load(open(GA + "/out/plan/inventory.json")); rows = [r for r in inv["field"]["rows"] if r["name"] == "inflatable_sherman"]
    return bool(rows) and rows[0]["meshes"] > 50 and rows[0]["prim"] / rows[0]["meshes"] > .6, "inflatable_sherman %s" % rows[:1]

# Memory files follow the schemas' required fields
def memory_schema():
    req = json.load(open("production/schemas/lesson.schema.json"))["required"]; L = json.load(open("memory/lessons_learned.json"))["lessons"]
    bad = [x.get("id") for x in L if any(k not in x for k in req)]
    reqa = json.load(open("production/schemas/asset.schema.json"))["required"]; A = json.load(open(GA + "/production/ASSET_REGISTER.json"))["assets"]
    bada = [a.get("asset_id") for a in A if any(k not in a for k in reqa)]
    return not bad and not bada, "%d lessons, %d assets; bad: %s %s" % (len(L), len(A), bad, bada)

for n, fn in [("PI-002 lint catches swallowed code (fixture)", lint_fixture), ("PI-002 Ghost Army set module is clean", lint_current),
              ("PI-001 anim_audit FAILs the v1 film", anim_v1_fails), ("PI-001 anim_audit PASSes the current film", anim_current_passes),
              ("PI-003 entering a place never slides", place_entry_no_slide), ("controller init never overwrites memory", controller_init_idempotent),
              ("controller gates are honest (final: primitive hero FAILs)", controller_gates_honest), ("lesson promotion refuses without proof", promote_refuses_without_proof),
              ("renderer inventory measures the hero", inventory_measures_hero), ("memory files follow the schemas", memory_schema)]:
    t(n, fn)
fails = [n for n, ok in R if not ok]; print("\n%d/%d PASS" % (len(R) - len(fails), len(R))); sys.exit(1 if fails else 0)
