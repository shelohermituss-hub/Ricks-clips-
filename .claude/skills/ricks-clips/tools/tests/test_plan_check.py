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
