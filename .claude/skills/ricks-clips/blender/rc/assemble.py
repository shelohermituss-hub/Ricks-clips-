"""rc.assemble — D. Scene Assembly (Mission 1, phase-aware v3: deliverable 2/4, 2026-11-18). Runs inside Blender.
place.json (schema v3, rc.place) -> one self-contained scene .blend, built PHASE BY PHASE so the pipeline (tools/rc_pipeline.py) can stop
after any phase and prove it:
    1 environment  terrain (relief, flat zones, path mask) + assets + lines (fences/walls) + scatter (biomes, LOD by distance)
    3 cameras      shots: several cameras, each bound to its frame range with timeline markers (cuts happen in the render)
    4 characters   cards from tools/card_service.mjs (+ 3D props held in a hand)
    5 animation    recipes (rc.animate)          6 physics  events (rc.physics)       7 polish  cloth (rc.animate.cloth) + wind
    8 fx           effects (rc.vfx)              9 lookdev  light rig + palette-first materials + grade settings
Collections: RC_TERRAIN RC_ASSETS RC_LINES RC_SCATTER RC_CAMERA RC_LIGHTS RC_CHARACTERS RC_PHYSICS RC_FX.
Nothing depends on the frame rendered before (PI-012): placements are static or baked to keys, scatters are seeded."""
import json, math, os, sys
import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rc import SKILL, geo, library, bl_library, lookdev, animate, physics, vfx, characters, envbuild, place as placemod  # noqa: E402

def _col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def _source(aid, cols, sub=None):
    key = aid + ("__" + sub if sub else "")
    if key not in cols:
        blend, _ = library.resolve(aid, log=lambda *a: None); cols[key] = bl_library.link_asset(blend, key, None)
    return cols[key]

def _material(aid):
    blend, _ = library.resolve(aid, log=lambda *a: None)
    with bpy.data.libraries.load(blend, link=False) as (src, dst): dst.materials = [aid]   # appended: self-contained scene
    return dst.materials[0]

def flat_mat(spec):                                              # a named palette material; rc.lookdev gives it its PBR detail by name
    m = bpy.data.materials.get(spec["name"]) or bpy.data.materials.new(spec["name"]); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lookdev._hex(spec["color"]), 1); return m

def _from_lock():
    sys.path.insert(0, os.path.join(SKILL, "templates")); from blender_look import from_lock; return from_lock

def _film_camera(scene, ep, frames):                             # v2 compatibility: the camera of a film plan (camera_baked.json)
    fl = _from_lock(); cb = json.load(open(os.path.join(SKILL, ep, "out", "plan", "camera_baked.json")))
    fl.camera(scene, [dict(c, f=i) for i, c in enumerate(cb["frames"]) if frames[0] <= i <= frames[1]]); cam = scene.camera
    for c in list(cam.users_collection): c.objects.unlink(cam)
    _col("RC_CAMERA").objects.link(cam); return cam

def shots(scene, S):
    """one camera per shot; static (camera) or keyed (keys, linear between keys); a timeline marker binds it at its first frame"""
    fl = _from_lock(); cams = []
    for s in S:
        d = bpy.data.cameras.new("Cam_" + s["name"]); d.sensor_fit = "VERTICAL"; d.sensor_height = 24; d.clip_end = 5000; d.dof.use_dof = s.get("fstop") is not None
        if s.get("fstop"): d.dof.aperture_fstop = s["fstop"]
        o = bpy.data.objects.new("Cam_" + s["name"], d); _col("RC_CAMERA").objects.link(o); o.rotation_mode = "QUATERNION"
        keys = s.get("keys") or [dict(s["camera"], f=s["frames"][0])]; prev = None
        for k in keys:
            o.location = k["pos"]; q = fl._rot(k["pos"], k["aim"], None, k.get("roll", 0.0))
            if prev is not None and q.dot(prev) < 0: q.negate()
            o.rotation_quaternion = q; prev = q.copy(); d.lens = 12 / math.tan(math.radians(k.get("fov_v", 45)) / 2)
            if s.get("fstop"): d.dof.focus_distance = math.dist(k["pos"], k["aim"]); d.dof.keyframe_insert("focus_distance", frame=k["f"])
            o.keyframe_insert("location", frame=k["f"]); o.keyframe_insert("rotation_quaternion", frame=k["f"]); d.keyframe_insert("lens", frame=k["f"])
        for ad in (o.animation_data, d.animation_data):
            if ad and ad.action:
                for fc in fl._fcurves(ad.action):
                    for kp in fc.keyframe_points: kp.interpolation = s.get("interp", "BEZIER") if len(keys) > 2 else "LINEAR"
        m = scene.timeline_markers.new(s["name"], frame=s["frames"][0]); m.camera = o; cams.append(o)
    scene.camera = cams[0]; return cams

def build(place_path, out_blend, upto=9, light=True):
    P = json.load(open(place_path)); root = os.path.join(os.path.dirname(os.path.abspath(place_path)), P.get("root", "."))
    probs = placemod.validate(P, set(library.index()))
    if probs and P.get("schema_version", 2) >= 3: raise ValueError("place.json invalid: " + "; ".join(probs))
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; cols = {}; report = {"place": P["place_id"], "upto": upto, "phases": []}
    sc.render.fps = P.get("fps", 30)
    if P.get("frames"): sc.frame_start, sc.frame_end = P["frames"]
    # ---- 1 ENVIRONMENT
    t = P.get("terrain"); ground = None
    if t:
        tm = t.get("material"); tm = flat_mat(tm) if isinstance(tm, dict) else (_material(tm) if tm else None)
        ground = (envbuild.terrain(t, _col("RC_TERRAIN"), tm) if P.get("schema_version", 2) >= 3 else geo.terrain("terrain", t["size"], t.get("res", 64), t.get("height", 0), t.get("seed", 1), _col("RC_TERRAIN"), tm))
    for st in P.get("strips", []):                               # v2 strips (kept for old files; v3 paints paths into the terrain)
        (ax, ay), (bx, by) = st["from"], st["to"]; L = math.hypot(bx - ax, by - ay); n = max(2, int(L / 1.0))
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=n, y_subdivisions=4, size=1); o = bpy.context.object; o.name = st["name"]
        o.scale = (L, st["width"], 1); bpy.ops.object.transform_apply(scale=True); o.rotation_euler = (0, 0, math.atan2(by - ay, bx - ax)); o.location = ((ax + bx) / 2, (ay + by) / 2, .5)
        for c in list(o.users_collection): c.objects.unlink(o)
        _col("RC_TERRAIN").objects.link(o); o.data.materials.append(flat_mat(st["material"]))
        if ground: sw = o.modifiers.new("hug", "SHRINKWRAP"); sw.target = ground; sw.wrap_method = "PROJECT"; sw.use_negative_direction = True; sw.offset = st.get("offset", .02)
    A = _col("RC_ASSETS")
    for a in P.get("assets", []):
        if a.get("physics"): continue                               # destructible / simulated placements are realised by rc.physics
        if a.get("realize"):                                        # interactive placements (a door on a hinge, a pane to shatter): real objects "<name>:<part>"
            at = list(a["at"]); at[2] += envbuild.ground_z(ground, at[0], at[1]) if ground else 0
            physics.realize(sc, _source(a["asset"], cols), a.get("name", a["asset"]), at, math.radians(a.get("rot", 0)), A); continue
        at = list(a["at"]); at[2] = at[2] + (envbuild.ground_z(ground, at[0], at[1]) if a.get("on_ground", True) and ground else 0)
        e = bl_library.instance(_source(a["asset"], cols), a.get("name", a["asset"]), at, math.radians(a.get("rot", 0)), a.get("scale", 1.0), A)
        if a.get("hide_from") is not None:                          # gone after an event (burst, destroyed): keyed visibility
            for f, h in ((sc.frame_start, False), (a["hide_from"] - 1, False), (a["hide_from"], True)): e.hide_render = h; e.hide_viewport = h; e.keyframe_insert("hide_render", frame=f); e.keyframe_insert("hide_viewport", frame=f)
    for l in P.get("lines", []):
        envbuild.lines(l, _source(l["asset"], cols), _col("RC_LINES"), ground, geo.instancer); report.setdefault("lines", []).append(l.get("name", l["asset"]))
    S = _col("RC_SCATTER"); rules = []
    for s in P.get("scatter", []):
        if "biome" in s: rules += envbuild.biome_rules(s["biome"], s["zone"], s["seed"], s.get("exclude", ()), s.get("density", 1.0), s.get("name"), s.get("lod"))
        else: rules.append(s)
    for s in rules:
        pts, rots, scl = geo.scatter_points(s["zone"], s["count"], s["seed"], s.get("exclude", ()), tuple(s.get("scale", (1, 1))))
        if ground: pts = envbuild.drape(pts, ground)
        A2 = library.index().get(s["asset"], {}); var = bool(A2.get("variants")); nm = s.get("name", s["asset"]); lod = s.get("lod")
        if lod and A2.get("lods_auto"):
            (pn, rn, sn), (pf, rf, sf) = envbuild.split_lod(pts, rots, scl, lod["camera"], lod["near"])
            if pn: geo.instancer(nm, pn, _source(s["asset"], cols), S, rn, sn, pick=var, seed=s["seed"], wind=s.get("wind", 0.0))
            if pf: geo.instancer(nm + "_lod1", pf, _source(s["asset"], cols, "lod1"), S, rf, sf, pick=var, seed=s["seed"], wind=s.get("wind", 0.0))
            report.setdefault("scatter", {})[nm] = {"near": len(pn), "far_lod1": len(pf)}
        else:
            geo.instancer(nm, pts, _source(s["asset"], cols), S, rots, scl, pick=var, seed=s["seed"], wind=s.get("wind", 0.0)); report.setdefault("scatter", {})[nm] = len(pts)
    report["phases"].append(1)
    # ---- 3 CAMERAS
    if upto >= 3:
        if P.get("shots"): report["cameras"] = [c.name for c in shots(sc, P["shots"])]
        elif P.get("camera") and P["camera"].get("pos"): report["cameras"] = [c.name for c in shots(sc, [{"name": "test", "frames": P.get("frames", [0, 0]), "camera": P["camera"]}])]
        elif P.get("camera"): _film_camera(sc, P["episode"], P["camera"]["frames"])
        report["phases"].append(3)
    # ---- 4 CHARACTERS
    if upto >= 4 and P.get("characters") and sc.camera:
        ch = P["characters"]; lock = os.path.dirname(os.path.normpath(os.path.join(root, ch["cards"]))) if "cards" in ch else os.path.join(SKILL, P["episode"], ch["lock"])
        placed = characters.place_cards(sc, lock, ch["who"], sc.camera, ch.get("self_lit", .55), ground=ground)
        for pr in ch.get("props", []): characters.hold_prop(sc, placed[pr["who"]], _source(pr["asset"], cols), pr)
        report["characters"] = sorted(placed); report["phases"].append(4)
    # ---- 5 ANIMATION
    if upto >= 5 and P.get("animation"): report["animation"] = animate.apply(sc, P["animation"], sc.render.fps, ground=ground); report["phases"].append(5)
    # ---- 6 PHYSICS
    if upto >= 6 and P.get("physics"):
        report["physics"] = [physics.run(sc, ph, lambda aid: _source(aid, cols), ground) for ph in P["physics"]]; report["phases"].append(6)
    # ---- 7 POLISH (cloth; wind is already on the scatters)
    if upto >= 7 and P.get("cloth"): report["cloth"] = [animate.cloth(sc, c, ground) for c in P["cloth"]]; report["phases"].append(7)
    # ---- 8 FX
    if upto >= 8 and P.get("fx"):
        rel = {ph.get("name", ph["type"]): r.get("release") for ph, r in zip(P.get("physics", []), report.get("physics", []))}
        fx = []
        for e in P["fx"]:                                           # "@<physics event name>[+n]": the effect lands on the impact frame the physics computed
            if isinstance(e.get("frame"), str) and e["frame"].startswith("@"):
                nm, _, add = e["frame"][1:].partition("+"); e = dict(e, frame=int(rel.get(nm) or 0) + int(add or 0))
            fx.append(e)
        report["fx_objects"] = vfx.apply(sc, fx, ground=ground); report["fx_frames"] = {e.get("name", e["type"]): e.get("frame") for e in fx}; report["phases"].append(8)
    # ---- 9 LOOKDEV (light rig + materials + grade settings)
    if upto >= 9:
        if light and P.get("light"): report["light"] = lookdev.light_rig(sc, P["light"]); [sc.collection.objects.unlink(o) or _col("RC_LIGHTS").objects.link(o) for o in [o for o in sc.collection.objects if o.type == "LIGHT"]]
        if P.get("lookdev"): report["lookdev"] = lookdev.apply(P["lookdev"]["rules"])
        cal = os.path.join(os.path.dirname(os.path.abspath(place_path)), "calibration.json")
        if os.path.exists(cal):                                         # PERSISTED calibration (phase 9 writes it): a rebuild anywhere (pod) gets the
            C = json.load(open(cal)); vs = sc.view_settings             # same look; it was only in the local .blend before (pod render: 0.37 vs 0.50 luma)
            vs.exposure = C["exposure"]; vs.use_white_balance = True; vs.white_balance_temperature = C["white_balance_temperature"]; report["calibration"] = C
        report["phases"].append(9)
    os.makedirs(os.path.dirname(os.path.abspath(out_blend)), exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
    report["assets_used"] = sorted(cols); sc["rc_build_key"] = report["build_key"] = build_key(P, place_path, root, upto); return report

def build_key(P, place_path, root, upto):
    """CONTENT KEY of an assembled scene (a .blend saved twice is not byte-identical, measured 2026-11-18, so its bytes cannot key the
    frame cache): the place.json, the phases built, the rc package source, the asset build keys used, the character cards' index files
    and the Blender version. Same key = same scene = rendered frames are reused."""
    import glob, hashlib
    h = hashlib.sha256(); h.update(json.dumps(P, sort_keys=True).encode()); h.update(str(upto).encode()); h.update(bpy.app.version_string.encode())
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*.py"))): h.update(open(f, "rb").read())
    for aid in sorted(library.index()): h.update(json.dumps(library.index()[aid], sort_keys=True).encode())
    cal = os.path.join(os.path.dirname(os.path.abspath(place_path)), "calibration.json")
    if os.path.exists(cal): h.update(open(cal, "rb").read())
    ch = P.get("characters", {})
    if ch.get("cards"):
        for f in sorted(glob.glob(os.path.join(root, ch["cards"], "*", "index.json"))): h.update(open(f, "rb").read())
    return h.hexdigest()
