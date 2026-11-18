"""rc.place — place.json schema v3 + validator (deliverables 2/4, 2026-11-18). Pure Python, no dependency.
One SPEC drives both the validator (`validate(P)` -> list of problems, used by rc.assemble before building) and the documentation
schema (`python3 -m rc.place schema` writes blender/rc/schema/place.schema.json). Version 2 files (the Mission 2 prototype) still load.

Top level (v3):
  schema_version 3 | place_id | root (folder for relative paths: cards, references; default = the place file's folder)
  frames [a, b] | fps (30) | palette {name: "#hex"}
  light     {preset, key_dir, view_transform, exposure, white_balance}
  terrain   {size [x, y], res, height, seed, material {name, color}, flat [{center, radius, blend}], paths [{points, width, feather}]}
  assets    [{asset, name, at [x, y, z], rot (deg), scale, physics (bool: realised by a physics event)}]
  lines     [{asset, name, points [[x, y]...], spacing, seed}]
  scatter   [{asset | biome, name, zone, count | density, seed, scale [a, b], wind, exclude [...], lod {camera [x, y], near}}]
  shots     [{name, frames [a, b], camera {pos, aim, fov_v} | keys [{f, pos, aim, fov_v}], fstop, join "cut" | "dissolve:N"}]
  characters {cards (folder of card_service output), who [...], self_lit, props [{who, hand, asset}]}
  animation [{type, target, frames, ...}]      types: rc.animate.RECIPES
  physics   [{type, ...}]                      types: rc.physics.EVENTS
  cloth     [{type, ...}]                      types: flag, line_cloth
  fx        [{type, frame, ...}]               types: rc.vfx.EFFECTS
  lookdev   {rules {material: rule}, calibrate {reference, frame}}
Zones: {"center": [x, y], "radius": r} | {"polygon": [[x, y]...]} | {"from": [x, y], "to": [x, y], "width": w}"""
import json, os, sys

ANIM = {"lift_set", "path", "orbit", "bob", "hinge", "flicker", "look_at", "vehicle_drive", "spin"}
PHYS = {"crash", "drop", "topple", "roll", "door_break", "glass_shatter", "collapse", "deform"}
FX = {"dust_burst", "smoke", "fire", "sparks", "rain", "explosion_stylized", "haze", "splash"}
CLOTH = {"flag", "line_cloth"}
SECTIONS = {"schema_version": int, "place_id": str, "root": str, "frames": list, "fps": int, "palette": dict, "light": dict, "terrain": dict, "assets": list,
            "lines": list, "scatter": list, "strips": list, "shots": list, "camera": dict, "characters": dict, "animation": list, "physics": list, "cloth": list,
            "fx": list, "lookdev": dict, "episode": str, "_note": str}

def _zone_ok(z):
    return isinstance(z, dict) and (("center" in z and "radius" in z) or "polygon" in z or ("from" in z and "to" in z and "width" in z))

def validate(P, asset_ids=None):
    E = []
    for k, v in P.items():
        if k.startswith("_"): continue
        if k not in SECTIONS: E.append("unknown section '%s'" % k)
        elif not isinstance(v, SECTIONS[k]): E.append("section '%s' must be %s" % (k, SECTIONS[k].__name__))
    for k in ("schema_version", "place_id"):
        if k not in P: E.append("missing " + k)
    fr = P.get("frames", [0, 0])
    def known(aid, where):
        if asset_ids is not None and aid not in asset_ids: E.append("%s: asset '%s' not in the library" % (where, aid))
    for i, a in enumerate(P.get("assets", [])):
        if not {"asset", "at"} <= set(a): E.append("assets[%d] needs asset and at" % i)
        else: known(a["asset"], "assets[%d]" % i)
    for i, l in enumerate(P.get("lines", [])):
        if not {"asset", "points"} <= set(l) or len(l.get("points", [])) < 2: E.append("lines[%d] needs asset and >= 2 points" % i)
        else: known(l["asset"], "lines[%d]" % i)
    for i, s in enumerate(P.get("scatter", [])):
        if "biome" not in s and "asset" not in s: E.append("scatter[%d] needs asset or biome" % i)
        if "asset" in s: known(s["asset"], "scatter[%d]" % i)
        if not _zone_ok(s.get("zone")): E.append("scatter[%d] zone invalid" % i)
        if "seed" not in s: E.append("scatter[%d] needs a seed (determinism)" % i)
    for i, s in enumerate(P.get("shots", [])):
        if "frames" not in s or ("camera" not in s and "keys" not in s): E.append("shots[%d] needs frames and camera|keys" % i)
        elif not (fr[0] <= s["frames"][0] <= s["frames"][1] <= fr[1]): E.append("shots[%d] frames %s outside place frames %s" % (i, s["frames"], fr))
    for sec, kinds in (("animation", ANIM), ("physics", PHYS), ("fx", FX), ("cloth", CLOTH)):
        for i, e in enumerate(P.get(sec, [])):
            if e.get("type") not in kinds: E.append("%s[%d] type '%s' not in %s" % (sec, i, e.get("type"), sorted(kinds)))
    for i, e in enumerate(P.get("physics", [])):
        if "seed" not in e and e.get("type") in ("glass_shatter", "crash", "collapse"): E.append("physics[%d] needs a seed (determinism)" % i)
    return E

def schema():
    zone = {"oneOf": [{"type": "object", "required": ["center", "radius"]}, {"type": "object", "required": ["polygon"]}, {"type": "object", "required": ["from", "to", "width"]}]}
    ev = lambda kinds: {"type": "array", "items": {"type": "object", "required": ["type"], "properties": {"type": {"enum": sorted(kinds)}}}}
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "rc/place.schema.json", "title": "RicksClips place (rc v3)", "type": "object",
            "required": ["schema_version", "place_id"],
            "properties": {"schema_version": {"enum": [2, 3]}, "place_id": {"type": "string"}, "root": {"type": "string"}, "frames": {"type": "array", "minItems": 2, "maxItems": 2},
                           "fps": {"type": "integer"}, "palette": {"type": "object"}, "light": {"type": "object"}, "terrain": {"type": "object"},
                           "assets": {"type": "array", "items": {"type": "object", "required": ["asset", "at"]}},
                           "lines": {"type": "array", "items": {"type": "object", "required": ["asset", "points"]}},
                           "scatter": {"type": "array", "items": {"type": "object", "required": ["zone", "seed"], "properties": {"zone": zone}}},
                           "shots": {"type": "array", "items": {"type": "object", "required": ["frames"]}}, "characters": {"type": "object"},
                           "animation": ev(ANIM), "physics": ev(PHYS), "fx": ev(FX), "cloth": ev(CLOTH), "lookdev": {"type": "object"}}}

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "schema":
        p = os.path.join(os.path.dirname(__file__), "schema", "place.schema.json"); os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(schema(), open(p, "w"), indent=1); print("wrote", p)
    elif a and a[0] == "validate":
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from rc import library
        probs = validate(json.load(open(a[1])), set(library.index())); print("\n".join(probs) or "VALID"); sys.exit(1 if probs else 0)
