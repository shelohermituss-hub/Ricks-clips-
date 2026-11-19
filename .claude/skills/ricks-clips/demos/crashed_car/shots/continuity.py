"""AUTOMATIC CONTINUITY CHECK (CB rule 2026-11-19: "tout doit passer par une action").
Run on a built shot BEFORE any render:
    blender -b <shot.blend> --python demos/crashed_car/shots/continuity.py -- <report.json> [--frames a-b]
It walks every frame of the shot and reports, for everything the camera sees:
  POP       an object/character card that turns visible/invisible (hide_render) while it is on screen in the frame before or after
  TELEPORT  a jump in world position that is not part of a motion: |step| > 0.25 m and > 4x the steps around it
  SHRINK    a jump in scale (> 15 % in one frame) — a helmet that shrinks instead of being moved
  POSE_POP  a drawn character whose new move does not ease in (tools/card_anchors.py measures it on the drawings; a card without
            anchors.json is reported ANCHORS_MISSING: run card_anchors.py first)
  HOLD      the camera does not move (position < 1 mm, rotation < 0.03 deg, lens unchanged) for 2+ consecutive frames
Exit code 1 if anything is found (the render must not start), 0 when clean.
Two cases are recognised as real actions and reported as ALLOWED (never silently):
  BREAK  an object disappears and its own pieces (names "<object>_...") appear at the same place on the same frame (barrel bursting into staves)
  FX     effects (objects in the L_FX collection) are born small and grow/fade by design; their POP/GROW are listed apart, not failures
An intentional hidden swap (behind a moving object, inside a cut) is declared on the object: custom property rc_swap_ok = "143,158"
(frames); it is then reported as ALLOWED with its reason (rc_swap_why), never silently."""
import sys, json, math

def _cands(bpy):
    """objects worth checking: anything animated itself or through a parent (static set pieces cannot pop)"""
    def anim(o):
        while o:
            if o.animation_data and o.animation_data.action: return True
            o = o.parent
        return False
    return [o for o in bpy.data.objects if o.type in ("MESH", "EMPTY", "CURVE", "FONT") and anim(o) and not o.name.startswith("rc_airbit")]

def _onscreen(sc, cam, o, margin=0.02):
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    if o.type == "EMPTY":
        pts = [o.matrix_world.translation]
    else:
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    vs = [world_to_camera_view(sc, cam, p) for p in pts]
    if all(v.z <= 0 for v in vs): return False, None
    xs = [v.x for v in vs if v.z > 0]; ys = [v.y for v in vs if v.z > 0]
    inside = max(xs) > -margin and min(xs) < 1 + margin and max(ys) > -margin and min(ys) < 1 + margin
    return inside, ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)

def _vis(o):
    while o:
        if o.hide_render: return False
        o = o.parent
    return True

def check(frames=None):
    import bpy
    sc = bpy.context.scene; cam = sc.camera
    fr = frames or list(range(sc.frame_start, sc.frame_end + 1)); C = _cands(bpy)
    hist = {o.name: [] for o in C}; camh = []
    for f in fr:
        sc.frame_set(f)
        for o in C:
            on, c = _onscreen(sc, cam, o)
            m = o.matrix_world; s = m.to_scale()
            hist[o.name].append({"f": f, "vis": _vis(o), "on": on, "loc": tuple(m.translation), "scale": (s.x + s.y + s.z) / 3})
        cm = cam.matrix_world; camh.append({"f": f, "loc": tuple(cm.translation), "rot": cm.to_quaternion(), "lens": cam.data.lens})
    import bpy as _b
    fxcol = _b.data.collections.get("L_FX"); fx = {o.name for o in fxcol.all_objects} if fxcol else set()
    fx |= {o.name for o in _b.data.objects if any(m and m.name.startswith(("rc_vol", "rc_flame", "rc_dust", "rc_smoke")) for m in getattr(o.data, "materials", []) or [])}
    issues, allowed = [], []
    for name, H in hist.items():
        o = bpy.data.objects[name]; ok = {int(x) for x in str(o.get("rc_swap_ok", "")).replace(" ", "").split(",") if x}
        for i in range(1, len(H)):
            a, b = H[i - 1], H[i]
            if a["vis"] != b["vis"] and (a["on"] or b["on"]):
                row = {"kind": "POP", "object": name, "frame": b["f"], "what": "appears" if b["vis"] else "disappears"}
                (allowed if b["f"] in ok or a["f"] in ok else issues).append(row | ({"why": o.get("rc_swap_why", "")} if b["f"] in ok or a["f"] in ok else {}))
            if not (a["vis"] and b["vis"] and (a["on"] or b["on"])): continue
            step = math.dist(a["loc"], b["loc"])
            around = [math.dist(H[j - 1]["loc"], H[j]["loc"]) for j in (i - 1, i + 1) if 1 <= j < len(H)]
            if step > 0.25 and step > 4 * max(around + [0.02]):
                issues.append({"kind": "TELEPORT", "object": name, "frame": b["f"], "jump_m": round(step, 3), "steps_around_m": [round(x, 3) for x in around]})
            if a["scale"] > 1e-6 and abs(b["scale"] / a["scale"] - 1) > 0.15:
                issues.append({"kind": "SHRINK" if b["scale"] < a["scale"] else "GROW", "object": name, "frame": b["f"], "ratio": round(b["scale"] / a["scale"], 3)})
    # BREAK: whole -> its pieces at the same frame and place; FX: effects are born small and fade by design
    gone = {(x["object"], x["frame"]) for x in issues if x["kind"] == "POP" and x["what"] == "disappears"}
    keep = []
    for x in issues:
        whole = [g for g, f in gone if f == x["frame"] and x["object"].startswith(g + "_")]
        if x["kind"] == "POP" and x["what"] == "appears" and whole:
            Hw = {h["f"]: h for h in hist[whole[0]]}; Hp = {h["f"]: h for h in hist[x["object"]]}
            if math.dist(Hw[x["frame"] - 1]["loc"], Hp[x["frame"]]["loc"]) < 1.5: allowed.append(x | {"why": "BREAK: %s bursts into its pieces" % whole[0]}); continue
        if x["kind"] == "POP" and x["what"] == "disappears" and any(y["kind"] == "POP" and y["frame"] == x["frame"] and y["object"].startswith(x["object"] + "_") for y in issues):
            allowed.append(x | {"why": "BREAK: replaced by its pieces"}); continue
        if x["object"] in fx and x["kind"] in ("POP", "GROW", "SHRINK"): allowed.append(x | {"why": "FX: effect born/fading by design"}); continue
        keep.append(x)
    issues = keep
    import os
    for o in _b.data.objects:                                              # drawn characters: pose pops measured on the drawings
        if not o.name.startswith("Card_") or not o.active_material or not o.active_material.node_tree: continue
        seq = o.active_material.node_tree.nodes.get("seq")
        if not seq or not seq.image: continue
        ap = os.path.join(os.path.dirname(_b.path.abspath(seq.image.filepath)), "anchors.json")
        if not os.path.exists(ap): issues.append({"kind": "ANCHORS_MISSING", "object": o.name, "frame": fr[0], "fix": "python3 tools/card_anchors.py " + os.path.dirname(ap)}); continue
        for pp in json.load(open(ap)).get("_pose_pops", []):
            if fr[0] < pp["frame"] <= fr[-1]: issues.append({"kind": "POSE_POP", "object": o.name} | pp)
    run = []
    for i in range(1, len(camh)):
        a, b = camh[i - 1], camh[i]
        still = math.dist(a["loc"], b["loc"]) < 1e-3 and math.degrees(a["rot"].rotation_difference(b["rot"]).angle) < 0.03 and abs(a["lens"] - b["lens"]) < 1e-3
        if still: run.append(b["f"])
        if (not still or i == len(camh) - 1) and len(run) >= 2:
            issues.append({"kind": "HOLD", "object": cam.name, "frame": run[0] - 1, "to": run[-1], "frames": len(run) + 1})
        if not still: run = []
    speeds = [math.dist(camh[i - 1]["loc"], camh[i]["loc"]) for i in range(1, len(camh))]
    cnt = {k: sum(1 for x in issues if x["kind"] == k) for k in ("POP", "TELEPORT", "SHRINK", "GROW", "POSE_POP", "ANCHORS_MISSING", "HOLD")}
    return {"blend": bpy.data.filepath, "frames": [fr[0], fr[-1]], "checked_objects": len(C), "counts": cnt, "ok": not issues,
            "camera_median_step_m": round(sorted(speeds)[len(speeds) // 2], 4) if speeds else None, "issues": issues, "allowed_swaps": allowed}

if __name__ == "__main__" and "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]; frames = None
    if "--frames" in a:
        x, y = map(int, a[a.index("--frames") + 1].split("-")); frames = list(range(x, y + 1))
    R = check(frames); json.dump(R, open(a[0], "w"), indent=1)
    print("CONTINUITY", "PASS" if R["ok"] else "FAIL", json.dumps(R["counts"]), "camera median step %s m" % R["camera_median_step_m"])
    for x in R["issues"][:40]: print("  ", json.dumps(x))
    sys.exit(0 if R["ok"] else 1)
