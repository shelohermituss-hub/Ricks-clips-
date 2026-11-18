"""RicksClips PRODUCTION CONTROLLER (Production Intelligence v1.0, 2026-11-18).
The showrunner's tool: opens an episode's production memory, reads the validated global lessons, runs the quality gates A-G
with honest statuses (PASS / WARN / FAIL / NOT_RUN; NOT_RUN never counts as PASS), keeps the shot-review / QA log, and
manages the lessons registry (a fix only becomes a global lesson after it is tested and has evidence).

    .venv/bin/python tools/production_controller.py init    episodes/<name>              # phase 0: memory, lessons to read, skeleton files
    .venv/bin/python tools/production_controller.py gates   episodes/<name> [--phase plan|preview|final] [--video final.mp4]
    .venv/bin/python tools/production_controller.py review  episodes/<name> <stills_dir> [--every 6] [--clip a-b ...]
    .venv/bin/python tools/production_controller.py issue   episodes/<name> --tc 00:43 --shot t_cafe --sev high --cat animation --obs "..." [--cause ...] [--fix ...]
    .venv/bin/python tools/production_controller.py compare-reference episodes/<name> <video.mp4> [--night 27-35 ...]   # vs the fortress standard
    .venv/bin/python tools/production_controller.py lessons [--all]                       # list validated (or all) global lessons
    .venv/bin/python tools/production_controller.py lesson-add  <lesson.json>              # add as 'proposed' (schema-checked)
    .venv/bin/python tools/production_controller.py scene-gates <stats.json> [out.json]       # phase-1 gates on rc.qa stats (scene or asset ingest)
    .venv/bin/python tools/production_controller.py lesson-promote <id>                     # only with tests + evidence + regression check

Spec: production/spec_fr/*.md (the package as delivered), production/README.md (how it is wired), CB_RULES.md section 11g.
Configs: production/config/{production_profile,quality_gates,action_effect_matrix}.json. Global memory: memory/.
"""
import json, os, sys, re, subprocess, datetime, glob, shutil, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "production", "config")
MEM = os.path.join(ROOT, "memory")
PY = sys.executable
STAT = ("PASS", "WARN", "FAIL", "NOT_RUN")
today = lambda: datetime.date.today().isoformat()

def jload(p, default=None):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default
def jsave(p, d): os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
def profile(): return jload(os.path.join(CFG, "production_profile.json"), {})
def run(cmd, cwd=ROOT, timeout=1800):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout); return r.returncode, (r.stdout + r.stderr)
    except Exception as e: return None, str(e)

# ------------------------------------------------------------------ memory
def lessons(all_=False):
    L = jload(os.path.join(MEM, "lessons_learned.json"), {"lessons": []})["lessons"]
    return L if all_ else [x for x in L if x.get("status") == "validated"]

REQ_LESSON = ["id", "date", "problem", "root_cause", "fix", "verification", "status"]
def lesson_problems(x):
    p = [k for k in REQ_LESSON if not x.get(k)]
    if x.get("status") not in ("proposed", "tested", "validated", "rejected"): p.append("status must be proposed|tested|validated|rejected")
    if x.get("severity") and x["severity"] not in ("low", "medium", "high", "blocker"): p.append("severity")
    return p

def write_lessons_md():
    L = lessons(True); out = ["# Production lessons (generated from memory/lessons_learned.json — do not edit by hand)", "",
        "Read the VALIDATED lessons at the start of every film (`production_controller.py init` prints them). A lesson is promoted only with a",
        "demonstrated cause, a reproducible fix, tests, before/after evidence and a regression check (CB_RULES 11g).", ""]
    for x in L:
        out += ["## %s — %s [%s, %s]" % (x["id"], x["problem"][:90], x.get("status"), x.get("severity", "")), "",
                "- **Where:** %s %s" % (x.get("episode", ""), x.get("shot_timecode", "")), "- **Root cause:** " + x["root_cause"], "- **Fix:** " + x["fix"],
                "- **Files:** " + ", ".join(x.get("files_changed", [])), "- **Tests:** " + "; ".join(x.get("verification", {}).get("tests", [])),
                "- **Evidence:** " + "; ".join(x.get("verification", {}).get("before_after_evidence", [])),
                "- **Regression check:** " + x.get("verification", {}).get("regression_check", ""), ""]
        for h in x.get("history", []): out.append("  - history: %s" % h)
    open(os.path.join(MEM, "LESSONS.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")

def cmd_lessons(args):
    for x in lessons("--all" in args):
        print("[%s] %s (%s, %s): %s\n    FIX: %s" % (x["id"], x.get("status"), x.get("severity", ""), x.get("date"), x["problem"], x["fix"]))

def cmd_lesson_add(args):
    new = jload(args[0]); probs = lesson_problems(new)
    if probs: print("REFUSED: missing/invalid", probs); return 1
    D = jload(os.path.join(MEM, "lessons_learned.json")); ids = {x["id"] for x in D["lessons"]}
    if new["id"] in ids: print("REFUSED: id exists (supersede it with a new id; history is never rewritten)"); return 1
    if new["status"] == "validated": new["status"] = "tested"; print("note: added as 'tested'; use lesson-promote to validate")
    D["lessons"].append(new); jsave(os.path.join(MEM, "lessons_learned.json"), D); write_lessons_md(); print("added", new["id"], new["status"]); return 0

def cmd_lesson_promote(args):
    D = jload(os.path.join(MEM, "lessons_learned.json")); x = next((l for l in D["lessons"] if l["id"] == args[0]), None)
    if not x: print("no lesson", args[0]); return 1
    v = x.get("verification", {}); miss = [k for k in ("tests", "before_after_evidence") if not v.get(k)] + ([] if v.get("regression_check") else ["regression_check"])
    for e in v.get("before_after_evidence", []):
        if not e.startswith("http") and not os.path.exists(os.path.join(ROOT, e.split("#")[0].strip())): miss.append("evidence file missing: " + e)
    if miss: print("REFUSED (promotion needs proof):", miss); return 1
    x.setdefault("history", []).append("%s: %s -> validated" % (today(), x["status"])); x["status"] = "validated"; x["promote_global"] = True
    jsave(os.path.join(MEM, "lessons_learned.json"), D); write_lessons_md(); print("validated", x["id"]); return 0

# ------------------------------------------------------------------ episode memory
SKELETON = {
    "BRIEF.md": "# Brief — {ep}\n\n- Story / sources:\n- Duration, format: 1080x1920, 30 fps\n- Approved items (script, voice, music, cast): \n- Budget / paid items allowed: none without explicit approval\n",
    "DECISIONS.md": "# Decisions — {ep}\n\n| date | decision | why | who approved |\n|---|---|---|---|\n",
    "OPEN_ISSUES.md": "# Open issues — {ep}\n\nBlockers that need a user decision (paid asset, account access, licence, creative change, missing reference).\n\n",
    "STATE.md": "# Production state — {ep}\n\nPhase: 0 (bootstrap). Gates: run `production_controller.py gates`.\n",
}
def ep_paths(ep):
    P = os.path.join(ep, "production"); return P, {k: os.path.join(P, k) for k in ("ASSET_REGISTER.json", "ACTION_EFFECT_MATRIX.json", "QA_LOG.json", "ENV_SCORES.json", "GATES.json", "GATES.md", "REVIEW")}

def cmd_init(args):
    ep = args[0].rstrip("/"); name = os.path.basename(ep); P, F = ep_paths(ep); os.makedirs(P, exist_ok=True); made = []
    for k, t in SKELETON.items():
        p = os.path.join(P, k)
        if not os.path.exists(p): open(p, "w", encoding="utf-8").write(t.format(ep=name)); made.append(k)
    film = jload(os.path.join(ep, "film.json"), {}); places = list((film.get("places") or {}).keys())
    if not os.path.exists(F["ASSET_REGISTER.json"]): jsave(F["ASSET_REGISTER.json"], {"schema_version": "1.0", "episode": name, "assets": []}); made.append("ASSET_REGISTER.json")
    if not os.path.exists(F["ACTION_EFFECT_MATRIX.json"]):
        ev = [dict(action="(story action)", at=None, shot=None, anticipation=[], animation=[], interaction=[], vfx=[], aftermath=[], audio=[], evidence=[], status="NOT_RUN")]
        jsave(F["ACTION_EFFECT_MATRIX.json"], {"schema_version": "1.0", "episode": name, "template": "production/config/action_effect_matrix.json", "events": ev}); made.append("ACTION_EFFECT_MATRIX.json")
    if not os.path.exists(F["QA_LOG.json"]): jsave(F["QA_LOG.json"], {"episode": name, "issues": []}); made.append("QA_LOG.json")
    if not os.path.exists(F["ENV_SCORES.json"]):
        crit = ["geometry", "variety", "materials", "depth", "lighting", "atmosphere", "coherence", "env_motion"]
        jsave(F["ENV_SCORES.json"], {"scale": "0 absent, 1 blockout/primitive, 2 readable but poor, 3 detailed and coherent, 4 reference finish",
                                     "essential": ["geometry", "materials", "depth", "lighting", "coherence"], "evidence_required": True,
                                     "places": {p: {c: None for c in crit} | {"evidence": [], "scored_by": None, "date": None} for p in places}}); made.append("ENV_SCORES.json")
    look = [p for p in (os.path.join(ep, "REFERENCE_LOOK_BIBLE.md"), os.path.join(ROOT, "references", "REFERENCE_LOOK_BIBLE.md")) if os.path.exists(p)]
    print("PRODUCTION CONTROLLER — init %s" % name)
    print("created:", ", ".join(made) or "(nothing; memory already exists, never overwritten)")
    print("reference look bible:", look[0] if look else "MISSING (gate A will FAIL): references/REFERENCE_LOOK_BIBLE.md")
    V = lessons(); print("\nVALIDATED GLOBAL LESSONS TO APPLY (%d) — memory/LESSONS.md:" % len(V))
    for x in V: print("  [%s] %s\n      -> %s" % (x["id"], x["problem"][:110], x["fix"][:160]))
    idx = os.path.join(ROOT, "library", "INDEX.md")
    if os.path.exists(idx): print("\nAlso read library/INDEX.md (%d pitfall/solution notes)." % sum(1 for l in open(idx, encoding="utf-8") if l.startswith("- [")))
    return 0

# ------------------------------------------------------------------ gates
def gate_rows():
    return jload(os.path.join(CFG, "quality_gates.json"), {"gates": []})["gates"]

def check_all(ep, phase, video):
    name = os.path.basename(ep.rstrip("/")); P, F = ep_paths(ep); prof = profile(); R = []
    def add(g, c, st, ev): assert st in STAT; R.append(dict(gate=g, check=c, status=st, evidence=ev))
    film = jload(os.path.join(ep, "film.json")); reg = jload(F["ASSET_REGISTER.json"], {"assets": []}); aem = jload(F["ACTION_EFFECT_MATRIX.json"], {"events": []})
    qa = jload(F["QA_LOG.json"], {"issues": []}); envs = jload(F["ENV_SCORES.json"], {"places": {}})
    final = phase == "final"
    # ---- A preproduction
    script = [p for p in ("SCRIPT.md", "voice/script.txt") if os.path.exists(os.path.join(ep, p))]
    add("A_PREPRODUCTION", "script_locked", "PASS" if script else "FAIL", ", ".join(script) or "no SCRIPT.md / voice/script.txt")
    lb = [p for p in (os.path.join(ep, "REFERENCE_LOOK_BIBLE.md"), os.path.join(ROOT, "references", "REFERENCE_LOOK_BIBLE.md"), os.path.join(ep, "LOOK_BIBLE.md"), os.path.join(ep, "STORY_BIBLE.md")) if os.path.exists(p)]
    refok = os.path.exists(os.path.join(ROOT, "references", "REFERENCE_LOOK_BIBLE.md"))
    provisional = refok and "Status: OFFICIAL" not in open(os.path.join(ROOT, "references", "REFERENCE_LOOK_BIBLE.md"), encoding="utf-8").read()
    add("A_PREPRODUCTION", "look_bible_exists", ("WARN" if provisional else "PASS") if refok else ("WARN" if lb else "FAIL"),
        ("reference bible not marked OFFICIAL; " if provisional else "official fortress standard; ") + ", ".join(os.path.relpath(p, ROOT) for p in lb))
    add("A_PREPRODUCTION", "shot_list_exists", "PASS" if film and film.get("takes") else "FAIL", "film.json takes=%d" % len((film or {}).get("takes", [])))
    real_ev = [e for e in aem.get("events", []) if e.get("action") and not e["action"].startswith("(")]
    add("A_PREPRODUCTION", "action_effect_matrix_exists", "PASS" if real_ev else "FAIL", "%d story events in production/ACTION_EFFECT_MATRIX.json" % len(real_ev))
    # ---- B assets
    inv_p = os.path.join(ep, "out", "plan", "inventory.json"); inv = jload(inv_p)
    if not inv:
        code, out = run(["node", "templates/threejs_film/render_gpu.mjs", os.path.join(ep, "film.json"), "--inventory"], timeout=900); inv = jload(inv_p)
    heroes = [a for a in reg.get("assets", []) if a.get("category") == "hero"]
    add("B_ASSETS", "hero_asset_inventory_complete", "PASS" if heroes else "FAIL", "%d hero assets registered" % len(heroes))
    th = prof.get("hero_detail", {"min_parts": 20, "min_tris": 12000, "max_primitive_share": 0.6})
    bad, weak, notes = [], [], []
    for a in heroes:
        if a.get("render_kind") == "flat_2d_prop": (bad if final else weak).append("%s: flat 2D library prop, not a 3D asset" % a["name"]); continue
        rows = [r for p in (inv or {}).values() if p for r in p["rows"] if r["name"].split("_0")[0] == a.get("scene_name") or r["name"] == a.get("scene_name")]
        if not rows: (bad if final else weak).append("%s: not found in renderer inventory (scene_name=%s)" % (a["name"], a.get("scene_name"))); continue
        r = max(rows, key=lambda r: r["tris"]); share = r["prim"] / max(1, r["meshes"])
        msg = "%s: %d parts, %d tris, %.0f%% primitive generators, %d textured mats" % (a["name"], r["meshes"], r["tris"], 100 * share, r["textured"])
        if a.get("source", "").startswith(("sketchfab", "blenderkit", "polyhaven", "fab", "blender_custom")) and a.get("validation_status") in ("render_tested", "approved"): notes.append(msg + " [modelled asset]")
        elif r["meshes"] < th["min_parts"] or r["tris"] < th["min_tris"] or share > th["max_primitive_share"]: (bad if final else weak).append(msg + " -> primitive assembly / below hero detail")
        else: notes.append(msg)
    add("B_ASSETS", "hero_assets_not_placeholder", "FAIL" if bad else ("WARN" if weak else ("PASS" if heroes else "NOT_RUN")), "; ".join(bad + weak + notes) or "no heroes")
    internal = lambda a: a.get("source", "") in ("procedural", "") or a.get("source", "").startswith(("motion-library", "blender_custom"))
    nolic = [a["name"] for a in reg.get("assets", []) if not internal(a) and not (a.get("license") and a.get("source_url"))]
    add("B_ASSETS", "license_and_provenance_recorded", "FAIL" if nolic else ("PASS" if reg.get("assets") else "NOT_RUN"), ("missing licence/source: " + ", ".join(nolic)) if nolic else "%d assets with provenance" % len(reg.get("assets", [])))
    ext = [a for a in reg.get("assets", []) if not internal(a)]
    tested = [a for a in ext if a.get("validation_status") in ("render_tested", "approved")]
    add("B_ASSETS", "renderer_import_test_passed", ("PASS" if len(tested) == len(ext) else ("FAIL" if final else "WARN")) if ext else "NOT_RUN",
        "%d/%d external assets render-tested" % (len(tested), len(ext)) if ext else "no external asset registered")
    texok = inv is not None and all((p is None) or True for p in inv.values())
    tex_rows = [(pl, sum(r["textured"] for r in p["rows"]), sum(r["mats"] for r in p["rows"])) for pl, p in (inv or {}).items() if p]
    add("B_ASSETS", "textures_verified", "PASS" if inv and all(t > 0 for _, t, _ in tex_rows) else ("NOT_RUN" if not inv else "WARN"),
        "; ".join("%s %d/%d textured materials" % x for x in tex_rows) if inv else "no inventory")
    # ---- C environments
    places = envs.get("places", {}); ess = envs.get("essential", ["geometry", "materials", "depth", "lighting", "coherence"])
    scored = {p: v for p, v in places.items() if all(isinstance(v.get(c), (int, float)) for c in ess)}
    low = ["%s.%s=%s" % (p, c, v[c]) for p, v in scored.items() for c in ess if v[c] < 3]
    unev = [p for p, v in scored.items() if not v.get("evidence")]
    if not scored: st = "NOT_RUN"
    elif low or len(scored) < len(places): st = "FAIL" if final else "WARN"
    else: st = "PASS"
    add("C_ENVIRONMENTS", "detail_score_minimum_3", st, ("below 3: " + ", ".join(low) + "; " if low else "") + "%d/%d places scored" % (len(scored), len(places)) + ("; no evidence for " + ", ".join(unev) if unev else ""))
    dp = [p for p, v in scored.items() if v.get("depth", 0) >= 3]
    add("C_ENVIRONMENTS", "three_depth_planes", "NOT_RUN" if not scored else ("PASS" if len(dp) == len(places) else "WARN"), "%d/%d places depth>=3" % (len(dp), len(places)))
    for c, k in (("materials_reviewed", "materials"), ("lighting_reviewed", "lighting"), ("environment_motion_reviewed", "env_motion")):
        ok = [p for p, v in scored.items() if isinstance(v.get(k), (int, float))]
        add("C_ENVIRONMENTS", c, "NOT_RUN" if not ok else ("PASS" if len(ok) == len(places) and all(scored[p][k] >= 3 for p in ok) else "WARN"), "%d/%d places reviewed" % (len(ok), len(places)))
    # ---- D animation
    code, out = run([PY, "tools/anim_audit.py", os.path.join(ep, "film.json"), "--json", os.path.join(P, "anim_audit.json")], timeout=600)
    v = (jload(os.path.join(P, "anim_audit.json")) or {}).get("verdict")
    add("D_ANIMATION", "actions_have_animation", v["status"] if v else "NOT_RUN", json.dumps(v) if v else out[-300:])
    fc = jload(os.path.join(ep, "out", "frame_checks.json"))
    if fc is None: add("D_ANIMATION", "contacts_checked", "NOT_RUN", "run node tools/frame_checks/check.mjs %s/film.json" % ep)
    else:
        rows = fc.get("rows", fc.get("results", [])) if isinstance(fc, dict) else fc
        fails = [r for r in rows if isinstance(r, dict) and r.get("result", r.get("status")) == "FAIL"]
        waived = {w["key"] for w in qa.get("waivers", [])}
        open_f = [r for r in fails if "%s|%s|%s" % (r.get("who"), r.get("rest"), r.get("check")) not in waived]
        add("D_ANIMATION", "contacts_checked", "FAIL" if open_f else ("WARN" if fails else "PASS"), "%d frame-check FAIL groups, %d waived with a reason (QA_LOG waivers)" % (len(fails), len(fails) - len(open_f)))
    add("D_ANIMATION", "transitions_checked", "PASS" if (film or {}).get("tween", {}).get("move_blend") else "WARN", "film.tween=%s" % (film or {}).get("tween"))
    mp = (film or {}).get("motion_polish", {})
    add("D_ANIMATION", "micro_animation_reviewed", "PASS" if mp.get("enabled") and mp.get("auto_blink") else "WARN", "motion_polish=%s" % mp)
    rev = glob.glob(os.path.join(P, "REVIEW", "*clip*.jpg"))
    add("D_ANIMATION", "continuity_reviewed", "PASS" if rev else "NOT_RUN", "%d continuous-motion strips in production/REVIEW" % len(rev))
    # ---- E vfx / audio
    evs = real_ev; withev = [e for e in evs if e.get("evidence") and all(os.path.exists(os.path.join(ep, x)) or os.path.exists(os.path.join(ROOT, x)) for x in e["evidence"])]
    add("E_VFX_AUDIO", "required_effects_rendered", "NOT_RUN" if not evs else ("PASS" if len(withev) == len(evs) else ("FAIL" if final else "WARN")), "%d/%d events with rendered evidence" % (len(withev), len(evs)))
    aft = [e for e in evs if e.get("aftermath")]
    add("E_VFX_AUDIO", "aftermath_checked", "NOT_RUN" if not evs else ("PASS" if all(e.get("status") == "PASS" for e in aft) and aft else "WARN"), "%d events with an aftermath, %d PASS" % (len(aft), sum(e.get("status") == "PASS" for e in aft)))
    snd = [e for e in evs if e.get("audio")]; mix = os.path.exists(os.path.join(ep, "sound", "mix_report.json"))
    add("E_VFX_AUDIO", "audio_visual_sync_checked", "NOT_RUN" if not (snd and mix) else ("PASS" if all(e.get("audio_sync") == "PASS" for e in snd) else "WARN"), "%d events with sound; mix_report=%s" % (len(snd), mix))
    lint = glob.glob(os.path.join(ep, "sets", "*.js"))
    if lint:
        code, out = run([PY, "tools/lint_set_modules.py"] + lint); add("E_VFX_AUDIO", "set_modules_no_swallowed_code", "PASS" if code == 0 else "FAIL", out.strip().splitlines()[-1] if out.strip() else "")
    # ---- F preview review
    sheets = glob.glob(os.path.join(P, "REVIEW", "*sheet*.jpg")); clips = glob.glob(os.path.join(P, "REVIEW", "*clip*.jpg"))
    add("F_PREVIEW_REVIEW", "contact_sheet_created", "PASS" if sheets else "NOT_RUN", "%d sheets" % len(sheets))
    add("F_PREVIEW_REVIEW", "continuous_clips_inspected", "PASS" if clips else "NOT_RUN", "%d strips" % len(clips))
    iss = qa.get("issues", []); openi = [i for i in iss if i.get("status") not in ("fixed", "waived", "closed")]
    add("F_PREVIEW_REVIEW", "timecoded_issues_logged", "PASS" if iss else "NOT_RUN", "%d issues, %d open" % (len(iss), len(openi)))
    rc = jload(os.path.join(P, "REFERENCE_COMPARE.json"))
    if not rc: add("F_PREVIEW_REVIEW", "reference_standard_compared", "NOT_RUN", "run compare-reference on the preview (fortress standard, references/REFERENCE_LOOK_BIBLE.md)")
    else:
        bad = [r["metric"] for r in rc["compare"] if r["status"] == "FAIL"]; wr = [r["metric"] for r in rc["compare"] if r["status"] == "WARN"]
        add("F_PREVIEW_REVIEW", "reference_standard_compared", "PASS" if not bad and not wr else ("FAIL" if bad and final else "WARN"),
            "%s (%s): FAIL %s; WARN %s" % (os.path.basename(rc.get("video", "?")), rc.get("date"), bad, wr))
    fx = [i for i in iss if i.get("status") == "fixed"]; fxe = [i for i in fx if i.get("after")]
    add("F_PREVIEW_REVIEW", "fixes_rerendered", "NOT_RUN" if not fx else ("PASS" if len(fxe) == len(fx) else "WARN"), "%d fixed, %d with after-render evidence" % (len(fx), len(fxe)))
    # ---- G final
    if phase != "final":
        for c in ("no_hero_placeholders", "grade_applied_to_all_shots", "native_resolution_render", "audio_and_subtitles_verified", "final_mp4_inspected", "lessons_saved"):
            add("G_FINAL_DELIVERY", c, "NOT_RUN", "final phase only")
    else:
        hb = next((r for r in R if r["check"] == "hero_assets_not_placeholder"), None)
        add("G_FINAL_DELIVERY", "no_hero_placeholders", "PASS" if hb and hb["status"] == "PASS" else "FAIL", hb["evidence"] if hb else "")
        glog = jload(os.path.join(ep, "grade", "grade_log.json"))
        add("G_FINAL_DELIVERY", "grade_applied_to_all_shots", "PASS" if glog and glog.get("frames_graded") == (film or {}).get("end") else "FAIL", "grade_log=%s" % (glog and {k: glog.get(k) for k in ("frames_graded", "src", "dst")}))
        if video and os.path.exists(video):
            code, out = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", video]); pr = json.loads(out) if code == 0 else {}
            vs = [s for s in pr.get("streams", []) if s.get("codec_type") == "video"]; au = [s for s in pr.get("streams", []) if s.get("codec_type") == "audio"]
            okres = vs and vs[0].get("width") == 1080 and vs[0].get("height") == 1920 and vs[0].get("r_frame_rate") in ("30/1", "30000/1000")
            dur = float(pr.get("format", {}).get("duration", 0)); want = (film or {}).get("end", 0) / 30.0
            add("G_FINAL_DELIVERY", "native_resolution_render", "PASS" if okres else "FAIL", "%s; native render log=%s" % (vs[0] if vs else "no video stream", os.path.exists(os.path.join(ep, "production", "native_render.json"))))
            add("G_FINAL_DELIVERY", "audio_and_subtitles_verified", "PASS" if au and abs(dur - want) < 0.2 else "FAIL", "audio streams=%d, duration %.2f s vs film %.2f s" % (len(au), dur, want))
            ins = glob.glob(os.path.join(P, "REVIEW", "final_*.jpg"))
            add("G_FINAL_DELIVERY", "final_mp4_inspected", "PASS" if ins else "NOT_RUN", "%d final inspection sheets" % len(ins))
        else:
            for c in ("native_resolution_render", "audio_and_subtitles_verified", "final_mp4_inspected"): add("G_FINAL_DELIVERY", c, "NOT_RUN", "no --video")
        add("G_FINAL_DELIVERY", "lessons_saved", "PASS" if any(x.get("episode") == name for x in lessons(True)) else "WARN", "lessons from this episode in memory/lessons_learned.json")
    return R

def cmd_gates(args):
    ep = args[0].rstrip("/"); phase = args[args.index("--phase") + 1] if "--phase" in args else "preview"; video = args[args.index("--video") + 1] if "--video" in args else None
    R = check_all(ep, phase, video); P, F = ep_paths(ep)
    jsave(F["GATES.json"], {"episode": os.path.basename(ep), "phase": phase, "date": today(), "results": R,
                            "policy": "NOT_RUN never counts as PASS; FAIL blocks the final; WARN needs a written reason and the user's acceptance"})
    lines = ["# Quality gates — %s (%s phase, %s)" % (os.path.basename(ep), phase, today()), "", "| gate | check | status | evidence |", "|---|---|---|---|"]
    for r in R: lines.append("| %s | %s | **%s** | %s |" % (r["gate"], r["check"], r["status"], r["evidence"].replace("|", "/")[:400]))
    tally = {s: sum(r["status"] == s for r in R) for s in STAT}; lines += ["", "Totals: " + ", ".join("%s %d" % kv for kv in tally.items())]
    open(F["GATES.md"], "w", encoding="utf-8").write("\n".join(lines) + "\n")
    for r in R: print("%-8s %-18s %-36s %s" % (r["status"], r["gate"], r["check"], r["evidence"][:150]))
    print("TOTALS", tally, "->", os.path.relpath(F["GATES.md"], ROOT))
    blocking = [r for r in R if r["status"] == "FAIL"]
    return 1 if blocking else 0

# ------------------------------------------------------------------ review sheets + QA log
def cmd_review(args):
    from PIL import Image, ImageDraw
    ep, src = args[0].rstrip("/"), args[1]; every = int(args[args.index("--every") + 1]) if "--every" in args else 6
    clips = [a for i, a in enumerate(args) if i > 0 and args[i - 1] == "--clip"]
    P, F = ep_paths(ep); os.makedirs(F["REVIEW"], exist_ok=True); fs = sorted(glob.glob(os.path.join(src, "f_*.png")))
    if not fs: print("no f_#####.png in", src); return 1
    def sheet(sel, out, W=180, H=320, cols=12):
        S = Image.new("RGB", (W * cols, H * ((len(sel) + cols - 1) // cols)), "black"); d = ImageDraw.Draw(S)
        for i, f in enumerate(sel): S.paste(Image.open(f).convert("RGB").resize((W, H)), ((i % cols) * W, (i // cols) * H)); d.text(((i % cols) * W + 3, (i // cols) * H + 3), os.path.basename(f)[2:7], fill="yellow")
        S.save(out, quality=82); return out
    made = [sheet(fs[::max(1, every // 3)][:240], os.path.join(F["REVIEW"], "sheet_overview.jpg"))]
    for c in clips:
        a, b = map(int, c.split("-")); sel = [f for f in fs if a <= int(os.path.basename(f)[2:7]) <= b]
        if sel: made.append(sheet(sel, os.path.join(F["REVIEW"], "clip_%05d_%05d.jpg" % (a, b)), cols=min(12, len(sel))))
    print("\n".join(os.path.relpath(m, ROOT) for m in made)); return 0

def cmd_compare_reference(args):
    sys.path.insert(0, os.path.join(ROOT, "tools")); import reference_compare as rcm
    ep, video = args[0].rstrip("/"), args[1]; P, F = ep_paths(ep)
    night = [tuple(map(float, args[i + 1].split("-"))) for i in range(len(args)) if args[i] == "--night"]
    m = rcm.measure(video); m["compare"] = rcm.compare(m, night); m["night"] = night; m["date"] = today()
    m["video"] = os.path.relpath(os.path.abspath(video), ROOT); jsave(os.path.join(P, "REFERENCE_COMPARE.json"), m)
    ref = jload(rcm.STD)["measured_reference"]
    L = ["# Reference comparison — %s vs the fortress standard (%s)" % (os.path.basename(ep), today()), "", "Video: `%s` (%s s). Standard: `production/config/reference_standard.json`, bible `references/REFERENCE_LOOK_BIBLE.md`." % (m["video"], m["seconds"]),
         "", "| metric | film | target | reference | status |", "|---|---|---|---|---|"]
    keymap = {"edge_detail": "edge_detail", "saturation": "saturation", "crushed": "crushed", "burned": "burned", "still_frames_pct": "still_frames_pct", "motion_median_x1000": "motion_median_x1000", "peaks_per_10s": "peaks_per_10s", "hard_cuts": "hard_cuts", "luma_day": "luma"}
    for r in m["compare"]: L.append("| %s | %s | %s | %s | **%s** |" % (r["metric"], r["value"], r["target"].replace("|", "/"), ref.get(keymap.get(r["metric"], ""), "-"), r["status"]))
    L += ["", "Hard cuts at (s): %s" % m["hard_cuts"], "", "Per second: see REFERENCE_COMPARE.json (luma, sat, crushed, burned, motion, edge)."]
    open(os.path.join(P, "REFERENCE_COMPARE.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    for r in m["compare"]: print("%-5s %-28s %-8s %s" % (r["status"], r["metric"], r["value"], r["target"]))
    print("->", os.path.relpath(os.path.join(P, "REFERENCE_COMPARE.md"), ROOT)); return 0

def cmd_issue(args):
    ep = args[0].rstrip("/"); P, F = ep_paths(ep); D = jload(F["QA_LOG.json"], {"issues": []})
    g = lambda k, d=None: args[args.index(k) + 1] if k in args else d
    it = dict(id="QA-%03d" % (len(D["issues"]) + 1), date=today(), timecode=g("--tc"), shot=g("--shot"), severity=g("--sev", "medium"), category=g("--cat", "general"),
              observation=g("--obs"), root_cause=g("--cause"), fix=g("--fix"), status=g("--status", "open"), before=g("--before"), after=g("--after"))
    D["issues"].append(it); jsave(F["QA_LOG.json"], D); print("logged", it["id"]); return 0

def cmd_scene_gates(args):
    """phase-1 gates on a Blender scene (or an asset ingest.json): honest PASS/WARN/FAIL from measured stats only (rc.qa)."""
    S = jload(args[0]); C = jload(os.path.join(CFG, "rc_gates.json")); out = []
    add = lambda k, st, ev: out.append((k, st, ev))
    if "instances_drawn" in S:                                   # a scene
        add("objects_bounded", "PASS" if S["objects"] <= C["max_objects"] else "FAIL", "%d objects (max %d)" % (S["objects"], C["max_objects"]))
        n, r = C["min_instance_ratio_if_over_objects"]; drawn = S["instances_drawn"] + S["mesh_objects"]
        add("repeats_instanced", "PASS" if drawn < n or S["instance_ratio"] >= r else "FAIL", "instance ratio %.3f of %d drawn" % (S["instance_ratio"], drawn))
        add("no_primitive_stand_ins", "PASS" if S["primitive_ratio"] <= C["max_primitive_ratio"] else "FAIL", "%d primitive-like of %d meshes (ratio %.3f)" % (S["primitive_like_objects"], S["mesh_objects"] - S.get("instancer_objects", 0), S["primitive_ratio"]))
        tr = S["textured_materials"] / max(1, S["materials"])
        add("materials_textured", "PASS" if tr >= C["min_textured_material_ratio"] else "FAIL", "%d/%d textured (min %.0f %%)" % (S["textured_materials"], S["materials"], 100 * C["min_textured_material_ratio"]))
    else:                                                        # an asset
        hero = S.get("tier") == "hero"
        add("asset_not_primitive", "PASS" if S["primitive_ratio"] <= (C["asset_hero_max_primitive_ratio"] if hero else C["max_primitive_ratio"]) else "FAIL", "primitive ratio %.3f (%s)" % (S["primitive_ratio"], S.get("tier")))
        if hero: add("hero_detail", "PASS" if S["tris"] >= C["asset_hero_min_tris"] else "FAIL", "%d tris (min %d)" % (S["tris"], C["asset_hero_min_tris"]))
        tr = S["textured_materials"] / max(1, S["materials"])
        add("asset_textured", "PASS" if tr >= C["asset_min_textured_ratio_warn"] else "WARN", "%d/%d textured materials" % (S["textured_materials"], S["materials"]))
    for k, st, ev in out: print("%-8s %-24s %s" % (st, k, ev))
    tot = {s: sum(1 for _, x, _ in out if x == s) for s in STAT}; print("TOTALS", tot)
    if len(args) > 1: jsave(args[1], {"stats_file": args[0], "gates": [dict(check=k, status=st, evidence=ev) for k, st, ev in out], "totals": tot})
    return 1 if tot["FAIL"] else 0

def main():
    if len(sys.argv) < 2: print(__doc__); return 2
    c, a = sys.argv[1], sys.argv[2:]
    fn = {"init": cmd_init, "gates": cmd_gates, "review": cmd_review, "issue": cmd_issue, "compare-reference": cmd_compare_reference, "lessons": cmd_lessons, "lesson-add": cmd_lesson_add, "lesson-promote": cmd_lesson_promote, "scene-gates": cmd_scene_gates}.get(c)
    if not fn: print(__doc__); return 2
    return fn(a) or 0

if __name__ == "__main__":
    sys.exit(main())
