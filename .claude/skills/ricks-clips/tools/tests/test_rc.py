"""Mission 1 foundation tests (rc package + card cache), 2026-11-18. Runs Blender headless; no network, no pod.
    python3 tools/tests/test_rc.py            -> N/N PASS   (about 2-4 min on 4 CPU cores; the card test is fast once the card cache is warm)
Each test states what it proves; NOT_RUN is never counted as PASS."""
import json, os, subprocess, sys, tempfile, shutil, time

SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "blender"))
BL = os.environ.get("RICKCLIPS_BLENDER", shutil.which("blender") or "blender")
CLI = os.path.join(SKILL, "blender", "rc", "cli.py"); FIX = os.path.join(SKILL, "blender", "tests", "fixtures", "test_place.json")
RES = []

def t(name, ok, info=""): RES.append((name, ok)); print("%s  %s  %s" % ("PASS" if ok else "FAIL", name, info), flush=True)
def blender(*a, timeout=900):
    r = subprocess.run([BL, "-b", "--factory-startup", "--python-exit-code", "3", "--python", CLI, "--", *a], capture_output=True, text=True, timeout=timeout)
    res = [l[10:] for l in r.stdout.splitlines() if l.startswith("RC_RESULT ")]
    return r.returncode, (json.loads(res[-1]) if res else None), r.stdout + r.stderr

def test_cache():
    from rc import cache
    tmp = tempfile.mkdtemp(); old = cache.ROOT; cache.ROOT = tmp; calls = []
    try:
        def b(out): calls.append(1); open(os.path.join(out, "x.txt"), "w").write("hello")
        d1 = cache.get_or_build("t", {"a": 1}, b, log=lambda *a: None); d2 = cache.get_or_build("t", {"a": 1}, b, log=lambda *a: None)
        t("cache: same inputs build once", len(calls) == 1 and d1 == d2)
        cache.get_or_build("t", {"a": 2}, b, log=lambda *a: None); t("cache: changed inputs rebuild", len(calls) == 2)
        open(os.path.join(d1, "x.txt"), "w").write("tampered"); ok, probs = cache.verify(d1); t("cache: verify detects a changed file", not ok and probs == ["changed x.txt"])
        def bad(out): open(os.path.join(out, "half"), "w").write("."); raise RuntimeError("boom")
        try: cache.get_or_build("t", {"a": 3}, bad, log=lambda *a: None)
        except RuntimeError: pass
        k, _ = cache.key("t", {"a": 3}); t("cache: a failed build leaves no entry", cache.lookup("t", k) is None)
    finally: cache.ROOT = old; shutil.rmtree(tmp, ignore_errors=True)

def test_library():
    from rc import library
    A = library.index(); bad = {i: library.validate(a) for i, a in A.items() if library.validate(a)}
    t("library: every asset.json valid", len(A) >= 10 and not bad, "%d assets %s" % (len(A), bad or ""))
    library.resolve("crawler_dozer", log=lambda *a: None); logs = []
    t0 = time.time(); p, s = library.resolve("crawler_dozer", log=logs.append)
    t("library: resolve of an unchanged asset is a cache hit", all("HIT" in l for l in logs) and os.path.exists(p), "%.2f s" % (time.time() - t0))
    t("library: ingest measures the asset (dims, tris)", s["tris"] > 10000 and 3 < s["dims_m"][0] < 6, json.dumps({"tris": s["tris"], "dims_m": s["dims_m"]}))

def test_blender_scene(tmp):
    rc, res, log = blender("assemble", FIX, os.path.join(tmp, "p.blend"))
    ok = rc == 0 and res is not None
    t("assemble: place.json -> .blend", ok, "" if ok else log[-800:])
    if not ok: return None
    st = res["stats"]
    t("assemble: repeats are instances (few objects, many drawn)", st["objects"] <= 20 and st["instances_drawn"] >= 2000, "objects %d, instances %d" % (st["objects"], st["instances_drawn"]))
    t("assemble: scatter counts follow the place file", res["scatter"] == {"decoys": 30, "bikes_stress": 2000}, json.dumps(res["scatter"]))
    return os.path.join(tmp, "p.blend")

def test_determinism(blend, tmp):
    a = blender("render", blend, os.path.join(tmp, "seq"), "0,15", "--res", "135x240", "--samples", "4", "--no-denoise")
    b = blender("render", blend, os.path.join(tmp, "one"), "15", "--res", "135x240", "--samples", "4", "--no-denoise")
    if a[0] or b[0]: t("determinism: renders ran", False, (a[2] + b[2])[-600:]); return
    h = lambda d: {r["f"]: r["sha256"] for r in json.load(open(os.path.join(tmp, d, "render.json")))["frames"]}
    t("determinism: frame 15 alone == frame 15 after frame 0 (bit-identical, no denoise)", h("seq")[15] == h("one")[15])

def test_gpu_required(blend, tmp):
    rc, res, log = blender("render", blend, os.path.join(tmp, "gpu"), "0", "--res", "64x64", "--samples", "1", "--gpu")
    has_gpu = "GPU REQUIRED" not in log and rc == 0
    if has_gpu: t("gpu: a GPU is present and was selected", res and res.get("device") == "GPU", json.dumps(res.get("devices") if res else None))
    else: t("gpu: --gpu without a GPU fails explicitly (no silent CPU)", rc != 0 and "GPU REQUIRED" in log)

def test_scene_gates(blend, tmp):
    rc, res, log = blender("stats", blend, os.path.join(tmp, "stats.json"))
    r = subprocess.run([sys.executable, os.path.join(SKILL, "tools", "production_controller.py"), "scene-gates", os.path.join(tmp, "stats.json")], capture_output=True, text=True)
    t("gates: scene gates read measured stats (instanced untextured assets must FAIL materials_textured)", "FAIL     materials_textured" in r.stdout and "PASS     repeats_instanced" in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-300:])

def test_physics(tmp):
    place = os.path.join(SKILL, "episodes", "ghost-army", "places", "field_crash_test", "place.json")
    rc, res, log = blender("assemble", place, os.path.join(tmp, "crash.blend"))
    ph = (res or {}).get("physics", [{}])[0]
    t("physics: prepared destruction (fracture + breakable joints) bakes to keys", rc == 0 and ph.get("pieces", 0) >= 40 and ph.get("joints", 0) >= 100, json.dumps({k: ph.get(k) for k in ("pieces", "joints", "pieces_moved_after_release")}))
    tr = ph.get("track", {}); mv = [v["moved_m"] for v in tr.values()]
    t("physics: the cart is pushed by the striker, no piece thrown absurdly far (< 8 m)", bool(mv) and min(mv) > 1.0 and max(mv) < 8.0, json.dumps({k: v["moved_m"] for k, v in tr.items()}))

def test_card_cache(tmp):
    ep = os.path.join(SKILL, "episodes", "ghost-army"); node = shutil.which("node")
    if not node: t("cards: cache", False, "node missing"); return
    cmd = lambda d: subprocess.run([node, "../../templates/threejs_film/render_gpu.mjs", "film.json", "--export-lock", "--cards-only", "--who", "radio_op", "--lock-dir", d, "--cache", os.path.join(tmp, "pc")], cwd=ep, capture_output=True, text=True, timeout=1800)
    cmd(os.path.join(tmp, "l1")); r = cmd(os.path.join(tmp, "l2"))
    line = [l for l in r.stdout.splitlines() if l.startswith("cards radio_op: cache")]
    t("cards: a second lock re-draws nothing (content cache)", bool(line) and "/ 0 drawn" in line[0], line[0] if line else r.stdout[-400:])
    same = all(open(os.path.join(tmp, "l1", "cards", "radio_op", f), "rb").read() == open(os.path.join(tmp, "l2", "cards", "radio_op", f), "rb").read() for f in os.listdir(os.path.join(tmp, "l1", "cards", "radio_op")) if f.endswith(".png"))
    t("cards: cached drawings are byte-identical to fresh ones", same)

if __name__ == "__main__":
    tmp = tempfile.mkdtemp(prefix="rc_test_")
    try:
        test_cache(); test_library(); b = test_blender_scene(tmp)
        if b: test_determinism(b, tmp); test_gpu_required(b, tmp); test_scene_gates(b, tmp)
        test_physics(tmp)
        if "--no-cards" not in sys.argv: test_card_cache(tmp)
    finally: shutil.rmtree(tmp, ignore_errors=True)
    n = sum(ok for _, ok in RES); print("%d/%d PASS" % (n, len(RES))); sys.exit(0 if n == len(RES) else 1)
