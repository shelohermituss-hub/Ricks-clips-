"""plan_check: the filled example passes; a plan with the errors CB reported (flat ground, still camera, action without reaction or
sound, a swap without an action) fails on each of them."""
import copy, json, os, sys
SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(SK, "tools"))
import plan_check
P = json.load(open(os.path.join(SK, "templates", "production_plan", "plan_example.json")))
assert not [r for r in plan_check.check(P) if r["status"] == "FAIL"], "example plan must pass"
B = copy.deepcopy(P); B["places"][0]["ground"]["texture"] = "#999b9f"; c = B["shots"][0]["camera"]; c[2] = dict(c[1], t=c[2]["t"])
a = B["shots"][0]["actions"][1]; a["reactions"] = []; a["sfx"] = []; B["shots"][0]["state_changes"].append({"who": "x", "change": "swap", "by_action": None})
F = {(r["area"], r["item"].split()[-1]) for r in plan_check.check(B) if r["status"] == "FAIL"}
for want in (("PLACES", "texture"), ("CAMERA", "moves"), ("ACTIONS", "reaction"), ("STATE", "swap")): assert want in F, (want, F)
assert ("ACTIONS", "effect") in F, F
print("test_plan_check PASS")
# STORY (7 reference videos): a FULL video without a hook in the 1st second, facts in the set or an insert shot is refused
V = copy.deepcopy(P); V["kind"] = "video"
FV = {r["item"] for r in plan_check.check(V) if r["status"] == "FAIL"}
for want in ("hook action shown in the 1st second", "facts written in the set", "insert shot"): assert want in FV, (want, FV)
V["hook"] = {"action": "pose", "t": 0.0}; V["facts"] = [{"fact": "70 MPH", "prop": "speed sign"}]; V["shots"][0]["camera"][1]["framing"] = "insert"
for _i, _s in enumerate(V["shots"]): _s["mood"] = ("dusk", "night rain", "dawn mist", "golden noon")[_i % 4]   # STYLE5: >= 4 light moods in a full video
assert not [r for r in plan_check.check(V) if r["status"] == "FAIL"], [r for r in plan_check.check(V) if r["status"] == "FAIL"]
print("test_plan_check STORY PASS")

# LOOK (CB corrections 2026-11-19): a plan whose places forget the cinematic look / real surfaces is refused
import copy, subprocess as _sp, tempfile as _tf
_SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_P = json.load(open(os.path.join(_SK, "templates", "production_plan", "plan_example.json")))
_bad = copy.deepcopy(_P); [pl.pop("look", None) for pl in _bad["places"]]; _bad.pop("grade", None)
_f = _tf.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(_bad, _f); _f.close()
_r = _sp.run([sys.executable, os.path.join(_SK, "tools", "plan_check.py"), _f.name], capture_output=True, text=True)
_fails = [l for l in _r.stdout.splitlines() if l.startswith("FAIL LOOK")]
assert _r.returncode == 1 and len(_fails) >= 5, "a plan without look must FAIL (got %d LOOK fails)" % len(_fails)
print("test_plan_check LOOK PASS (%d LOOK fails on a plan without look)" % len(_fails))

# STYLE5 (5 reference videos analysed 2026-11-20, references/style_analysis/QUALITY_GATES.md G8 G9 G12 G13): a FULL video with fewer than
# 4 light moods, an exit without a transition kind, a consequence that persists nowhere or in an earlier shot, and a rage without a 2D sign is refused
S = copy.deepcopy(_P); S["kind"] = "video"; S["hook"] = {"action": "pose", "t": 0.0}; S["facts"] = [{"fact": "70 MPH", "prop": "speed sign"}]; S["shots"][0]["camera"][1]["framing"] = "insert"
sh = sorted(S["shots"], key=lambda s: s["t0"]); sh[0]["transition_out"] = "then"; a0 = sh[0]["actions"][0]; a0.pop("persists", None)
a1 = sh[-1]["actions"][0]; a1["persists"] = [sh[0]["id"]]; a1["what"] = "goes into a rage"; a1.pop("sign", None); a1["micro"] = []; a1["reactions"] = ["x"]; sh[-1]["fx"] = []
FS = {r["item"] for r in plan_check.check(S) if r["status"] == "FAIL" and r["area"] == "STYLE5"}
for want in (">= 4 light moods (refs: 5-10)", "%s transition kind declared" % sh[0]["id"], "%s/%s consequence persists" % (sh[0]["id"], a0["id"]),
             "%s/%s consequence persists" % (sh[-1]["id"], a1["id"]), "%s/%s emotion sign" % (sh[-1]["id"], a1["id"])):
    assert want in FS, (want, FS)
print("test_plan_check STYLE5 PASS (%d STYLE5 fails on a bad full video)" % len(FS))
