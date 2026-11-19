"""PLAN CHECK (CB 2026-11-19: "avant de commencer à construire tu fais un plan ultra détaillé et précis de tout ce dont tu as besoin").
A new video (with or without a reference video) is written as ONE plan file BEFORE anything is built:
    python3 tools/plan_check.py <plan.json> [--report out.json]
The plan format is templates/production_plan/plan_example.json (filled) and PLAN_TEMPLATE_FR.md (what each field means).
Exit 1 when anything blocks; the build must not start before PASS. What it checks:
  STYLE     style bible named, format / fps / duration, narration pace (3.2-4.0 words/s like the reference style)
  PLACES    every place: ground and big surfaces with a REAL texture (polyhaven:/ambientcg:/sketchfab:/file:), sky, sun (elevation,
            azimuth, energy, angle), fill strength, shadows described, props listed with their source
  OBJECTS   every object used by an action is declared with its source, material/texture and its breakable/wet/dirty states
  SHOTS     shots cover the whole duration without gaps; every shot has a place, a narration span, transition in/out
  CAMERA    >= 2 keys per shot, consecutive keys differ (the camera never stops), each move named, a hand-held drift on top
  ACTIONS   every action: who, frames, animation, >= 1 micro-animation, >= 1 REACTION, >= 1 lasting CONSEQUENCE, >= 1 SFX;
            matched against library/reactions/reactions.json: reactions the recipe lists and the plan forgot are reported
  STATE     every entry / exit / change of a character or object names the action that carries it (no pop, no teleport)
  RHYTHM    actions per 10 s (reference style: an event every ~0.9 s), FX and sound per shot (ambience + music)
  STORY     (7 reference videos, 2026-11-19) the hook action is SHOWN within the first second; every number / name of the narration is
            a TEXT IN THE SET (facts: sign, newspaper, label, display); >= 2 light moods; >= 1 emotion close-up and >= 1 insert shot;
            captions spec (1-3 words, white bold, black outline, ~70 % height); a loop back to the first image (WARN)
            -> FAIL for a full video (kind "video", the default), WARN for a fragment (kind "fragment", e.g. the shot-2 example)
  LOOK      (CB's corrections, docs/CORRECTIONS_CB_FR.md) every exterior place: a visible real sky (hdri:), where the sun comes from and the
            hero object's shadow, a fill light; a road declares its wear (wheel paths, cracks), fields a scanned furrow texture, a fence its
            shadow, roadside grass its height and that both sides match; a sun shaft plan under trees by day (WARN); the plan's grade is
            measured (tools/grade_match.py); a vehicle declares its paint (never the asset's texture) and clear glass
  LESSONS   prints every validated lesson of memory/lessons_learned.json that applies to the plan (they must be planned for)
Statuses per line: PASS / WARN / FAIL. Never NOT_RUN = PASS."""
import json, os, re, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_TEX = re.compile(r"^(polyhaven|ambientcg|sketchfab|blenderkit|fab|file|library):")

def check(P):
    out = []; add = lambda area, item, ok, msg="", warn=False: out.append({"area": area, "item": item, "status": "PASS" if ok else ("WARN" if warn else "FAIL"), "msg": msg})
    lib = json.load(open(os.path.join(SKILL, "library", "reactions", "reactions.json")))["recipes"]
    # STYLE
    add("STYLE", "style bible", bool(P.get("style")) and os.path.exists(os.path.join(SKILL, P.get("style", "-"))), P.get("style", "missing"))
    for k in ("format", "fps", "duration_s"): add("STYLE", k, k in P, str(P.get(k)))
    v = P.get("voice", {}); w = v.get("words", 0); d = P.get("duration_s", 1)
    add("STYLE", "narration pace", 3.2 <= w / max(d, 1) <= 4.0, "%.2f words/s (style 3.44)" % (w / max(d, 1)), warn=True)
    # PLACES
    places = {p["id"]: p for p in P.get("places", [])}; add("PLACES", "places listed", bool(places), "%d" % len(places))
    for pid, p in places.items():
        surf = [p.get("ground", {})] + p.get("surfaces", [])
        for s in surf:
            t = s.get("texture", ""); add("PLACES", "%s / %s texture" % (pid, s.get("name", "ground")), bool(REAL_TEX.match(t)), t or "no texture: a flat colour + noise is refused (rule REAL SURFACES)")
        L = p.get("light", {}); sun = L.get("sun", {})
        add("PLACES", pid + " sun", all(k in sun for k in ("elevation", "azimuth", "energy", "angle")), json.dumps(sun))
        add("PLACES", pid + " fill / sky strength", "fill" in L, str(L.get("fill")))
        add("PLACES", pid + " shadows", bool(p.get("shadows")), p.get("shadows", "describe which structures throw which shadows where"))
        add("PLACES", pid + " sky", bool(p.get("sky")), str(p.get("sky")))
        for pr in p.get("props", []): add("PLACES", "%s prop %s source" % (pid, pr.get("id")), bool(pr.get("source")), pr.get("source", "missing"))
        add("PLACES", pid + " dressing density", len(p.get("props", [])) >= 4, "%d props (a set is never empty)" % len(p.get("props", [])), warn=True)
    # LOOK (CB corrections 2026-11-19, docs/CORRECTIONS_CB_FR.md): never a flat, unlit, ungraded first version
    for pid, p in places.items():
        lk = p.get("look", {}); txt = json.dumps(p, ensure_ascii=False).lower()
        interior = bool(p.get("interior")); night = "night" in str(p.get("light", {}).get("mood", "")).lower() or "nuit" in txt
        if not interior:
            add("LOOK", pid + " visible real sky", str(lk.get("sky", "")).startswith(("hdri:", "polyhaven:")), lk.get("sky", "look.sky = hdri:<id> (a real sky photo seen by the camera, rotated to the sun)"))
            add("LOOK", pid + " sun direction + hero shadow", bool(lk.get("sun_from")) and bool(lk.get("hero_shadow")),
                "%s / %s" % (lk.get("sun_from", "look.sun_from: where the sun is, as in the reference"), lk.get("hero_shadow", "look.hero_shadow: which long shadow crosses the frame")))
        add("LOOK", pid + " fill light", bool(lk.get("fill")), lk.get("fill", "look.fill: camera-side soft bounce light (nothing black in daylight)"))
        if not interior and not night and any(w in txt for w in ("tree", "arbre", "oak", "chêne")):
            add("LOOK", pid + " sun shafts under the trees", bool(lk.get("shafts")), lk.get("shafts", "look.shafts: thin shafts under the crown toward the ground"), warn=True)
        for srf in [p.get("ground", {})] + p.get("surfaces", []):
            nm = str(srf.get("name", "")).lower()
            if re.search(r"\b(road|route|asphalt|chaussée)\b", nm) and "roadside" not in nm:
                add("LOOK", "%s / %s wear" % (pid, srf.get("name")), bool(srf.get("wear")), srf.get("wear", "wear: wheel paths, cracks / tar snakes, patches (never a uniform asphalt)"))
            if any(w in nm for w in ("field", "champ", "farm")):
                add("LOOK", "%s / %s furrows" % (pid, srf.get("name")), any(w in str(srf.get("texture", "")) + str(srf.get("extra", "")) for w in ("furrow", "sillon")),
                    "%s (a field is tilled: scanned furrows, relief)" % srf.get("texture"))
        if any(w in txt for w in ("fence", "clôture")):
            add("LOOK", pid + " fence real + shadow", any(w in str(lk.get("fence", "")).lower() for w in ("shadow", "ombre")), lk.get("fence", "look.fence: real wood, varied posts, sagging wires, casts shadows"))
        if any(w in txt for w in ("grass", "herbe")) and any(w in txt for w in ("road", "route")):
            g = lk.get("grass", {}); add("LOOK", pid + " roadside grass height + both sides", bool(g.get("height_cm")) and bool(g.get("both_sides")), json.dumps(g) if g else "look.grass: {height_cm, colour, both_sides: true}")
    add("LOOK", "grade measured", bool(P.get("grade", {}).get("method")), json.dumps(P.get("grade", {})) if P.get("grade") else "grade: {method: tools/grade_match.py, reference: ...} (or the style bible values)")
    # OBJECTS
    objs = {o["id"]: o for o in P.get("objects", [])}; chars = {c["id"] for c in P.get("characters", [])}
    for oid, o in objs.items():
        add("OBJECTS", oid + " source", bool(o.get("source")), o.get("source", "missing"))
        add("OBJECTS", oid + " material", bool(o.get("material") or o.get("texture")), o.get("material") or o.get("texture") or "missing")
        if any(w in (oid + " " + str(o.get("source", ""))).lower() for w in ("car", "suv", "truck", "vehicle", "voiture", "f1")):
            mt = str(o.get("material", "")).lower()
            add("OBJECTS", oid + " vehicle paint + glass", any(w in mt for w in ("glass", "vitre", "verre")) and any(w in mt for w in ("paint", "peinture", "blanc", "rouge", "#", "metal", "métal", "mat")),
                o.get("material", "") + " (declare the paint, never the asset's texture, and clear glass)")
    for c in P.get("characters", []): add("OBJECTS", "character %s puppet" % c["id"], bool(c.get("puppet")), c.get("puppet", "missing"))
    # SHOTS / CAMERA / ACTIONS / STATE
    shots = P.get("shots", []); t = 0.0; n_act = 0
    all_ids = {a["id"] for s in shots for a in s.get("actions", [])}        # a state carried over from an earlier shot names that shot's action
    for s in sorted(shots, key=lambda s: s["t0"]):
        sid = s.get("id", "?")
        add("SHOTS", sid + " starts where the last ended", abs(s["t0"] - t) < 0.25 or s.get("overlap_ok"), "t0 %.2f vs %.2f" % (s["t0"], t)); t = max(t, s["t1"])
        add("SHOTS", sid + " place", s.get("place") in places, str(s.get("place")))
        add("SHOTS", sid + " narration", bool(s.get("narration")), s.get("narration", "missing"))
        add("SHOTS", sid + " transitions", bool(s.get("transition_in")) and bool(s.get("transition_out")), "%s -> %s" % (s.get("transition_in"), s.get("transition_out")))
        cam = s.get("camera", [])
        add("CAMERA", sid + " keys", len(cam) >= 2, "%d keys" % len(cam))
        for a, b in zip(cam, cam[1:]):
            same = a.get("pos") == b.get("pos") and a.get("aim") == b.get("aim") and a.get("lens") == b.get("lens")
            add("CAMERA", "%s %s->%s moves" % (sid, a.get("t"), b.get("t")), not same and b.get("move") != "hold", b.get("move", ""))
        add("CAMERA", sid + " hand-held drift", bool(s.get("handheld", True)), "street.handheld() on every frame")
        acts = s.get("actions", []); n_act += len(acts); ids = {a["id"] for a in acts}
        for a in acts:
            aid = "%s/%s" % (sid, a["id"]); who = a.get("who")
            add("ACTIONS", aid + " who declared", who in chars or who in objs, str(who))
            add("ACTIONS", aid + " animation", bool(a.get("anim")), a.get("anim", "missing"))
            for k, name in (("micro", "micro-animation"), ("reactions", "reaction"), ("consequences", "lasting consequence"), ("sfx", "sound effect")):
                add("ACTIONS", aid + " " + name, bool(a.get(k)), "; ".join(map(str, a.get(k, []))) or "missing: every action has %s (CB 2026-11-19)" % name)
            txt = (a.get("what", "") + " " + a.get("recipe", "")).lower()
            rec = [r for r in lib if r["id"] == a.get("recipe")] or [r for r in lib if any(tr in txt for tr in r["triggers"])]
            if rec:
                planned = " ".join(map(str, a.get("reactions", []) + a.get("consequences", []))).lower()
                miss = [x for x in rec[0]["reactions"] + rec[0]["consequences"] if not any(wd in planned for wd in re.findall(r"[a-z]{5,}", x.lower())[:3])]
                add("ACTIONS", aid + " vs recipe " + rec[0]["id"], not miss, "maybe forgotten: " + " | ".join(miss) if miss else "covered", warn=True)
            else: add("ACTIONS", aid + " recipe", False, "no recipe matches: add one to library/reactions/reactions.json when it is built", warn=True)
        for c in s.get("state_changes", []):
            ok = c.get("by_action") in ids or c.get("by_action") in all_ids or c.get("by_action") in ("cut", "offscreen", "fade", "behind_object")
            add("STATE", "%s %s %s" % (sid, c.get("who"), c.get("change")), ok, "by " + str(c.get("by_action")) + ("" if ok else ": every entry/exit/change is carried by an action (no pop)"))
        add("SHOTS", sid + " fx", bool(s.get("fx")), "; ".join(s.get("fx", [])) or "no effect planned", warn=True)
        add("SHOTS", sid + " ambience", bool(s.get("sound", {}).get("ambience")), str(s.get("sound", {}).get("ambience")))
    add("SHOTS", "cover the duration", abs(t - d) < 0.5, "%.2f / %.2f s" % (t, d))
    rate = n_act / max(d, 1) * 10; add("RHYTHM", "actions per 10 s", rate >= 6, "%.1f (style ~11 events per 10 s)" % rate, warn=True)
    add("RHYTHM", "music bed", bool(P.get("sound", {}).get("music")), str(P.get("sound", {}).get("music")))
    add("RHYTHM", "loudness target", P.get("sound", {}).get("lufs") == -14, str(P.get("sound", {}).get("lufs")), warn=True)
    # STORY (style bible v2, measured on 7 reference videos)
    full = P.get("kind", "video") == "video"; sw = not full
    hk = P.get("hook", {}); add("STORY", "hook action shown in the 1st second", hk.get("t", 99) <= 1.0 and hk.get("action") in all_ids, json.dumps(hk) if hk else "missing: hook {action, t}", warn=sw)
    facts = P.get("facts", []); txt = v.get("text", "")
    nums = set(x.strip(",.:") for x in re.findall(r"\d[\d,.:]*", txt)); covered = " ".join(str(f.get("fact", "")) for f in facts)
    miss = sorted(n for n in nums if n not in covered)
    add("STORY", "facts written in the set", bool(facts) and all(f.get("prop") for f in facts) and not miss, ("missing for: %s" % miss) if miss else "%d facts" % len(facts), warn=sw)
    moods = {p.get("light", {}).get("mood", pid) for pid, p in places.items()} | {s.get("mood") for s in shots if s.get("mood")}
    add("STORY", ">= 2 light moods", len(moods) >= 2, ", ".join(map(str, moods)), warn=sw)
    types = [s.get("shot_type", "") for s in shots] + [k.get("framing", "") for s in shots for k in s.get("camera", [])]
    add("STORY", "emotion close-up", any("close" in t for t in types), "shot_type / framing 'close' or 'extreme_close'", warn=sw)
    add("STORY", "insert shot", any("insert" in t for t in types), "shot_type / framing 'insert' (top-down detail of the story object)", warn=sw)
    cap = P.get("captions", {}); add("STORY", "captions spec", bool(cap.get("style")) and cap.get("words", [0, 9])[1] <= 3, json.dumps(cap) if cap else "missing", warn=sw)
    add("STORY", "loop to the first image", bool(P.get("loop")), str(P.get("loop", "none")), warn=True)
    # LESSONS
    les = json.load(open(os.path.join(SKILL, "memory", "lessons_learned.json")))["lessons"]
    rem = [l for l in les if l.get("status") == "validated" and any(x in ("every shot", "every card character", "every held prop") for x in l.get("applies_to", []))]
    for l in rem: add("LESSONS", l["id"], l["id"] in P.get("lessons_planned", []), l["problem"][:110] + "... -> list it in lessons_planned with how the plan avoids it")
    return out

def main(a):
    P = json.load(open(a[0])); R = check(P); f = [r for r in R if r["status"] == "FAIL"]; w = [r for r in R if r["status"] == "WARN"]
    for r in R:
        if r["status"] != "PASS": print("%-4s %-8s %-48s %s" % (r["status"], r["area"], r["item"][:48], r["msg"][:150]))
    print("PLAN %s: %d PASS, %d WARN, %d FAIL" % ("PASS" if not f else "FAIL", len(R) - len(f) - len(w), len(w), len(f)))
    if "--report" in a: json.dump({"ok": not f, "rows": R}, open(a[a.index("--report") + 1], "w"), indent=1, ensure_ascii=False)
    return 1 if f else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
