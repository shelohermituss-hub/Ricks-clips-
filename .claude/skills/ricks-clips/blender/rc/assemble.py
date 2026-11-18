"""rc.assemble — D. Scene Assembly (runs inside Blender). Mission 1, 2026-11-18.
place.json (episodes/<ep>/places/<place>/place.json) + the baked camera of the film -> one scene .blend, with fixed collections:
    RC_TERRAIN  RC_ASSETS (collection instances, one per placement)  RC_SCATTER (one geometry-node instancer per scatter rule)
    RC_LIGHTS   RC_CAMERA   (later missions add RC_CHARACTERS, RC_FX, RC_PHYSICS)
Nothing here depends on the frame rendered before: every placement is static or baked to keys, every scatter has its own seed.

place.json (schema_version 2):
  {"place_id": "field", "episode": "episodes/ghost-army", "palette": {...}, "light": {"preset": "morning"},
   "terrain": {"size": [160, 160], "res": 96, "height": 2.5, "seed": 3, "material": "coast_land_rocks_01" | null},
   "assets":  [{"asset": "inflatable_tank", "name": "hero_tank", "at": [0, 4, 0], "rot": 0, "scale": 1}],
   "scatter": [{"asset": "inflatable_tank_lod", "name": "decoys", "zone": {"center": [0, 40], "radius": 30} | {"polygon": [[x,y],...]},
                "count": 40, "seed": 7, "scale": [0.95, 1.05], "exclude": [{"center": [0, 4], "radius": 8}]}],
   "camera":  {"frames": [0, 312]}   (frames of the film's camera_baked.json; omitted = no film camera)}"""
import json, math, os, sys
import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rc import SKILL, geo, library, bl_library, lookdev, animate, physics, vfx, characters  # noqa: E402

def _col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def _source(aid, cols):
    if aid not in cols:
        blend, _ = library.resolve(aid, log=lambda *a: None); cols[aid] = bl_library.link_asset(blend, aid, None)
    return cols[aid]

def _material(aid):
    blend, _ = library.resolve(aid, log=lambda *a: None)
    with bpy.data.libraries.load(blend, link=False) as (src, dst): dst.materials = [aid]   # appended: self-contained scene
    return dst.materials[0]

def _camera(scene, ep, frames):
    sys.path.insert(0, os.path.join(SKILL, "templates"))
    from blender_look import from_lock                          # reuse: the camera of the approved plan, keyed per frame (proven on V3 lock tests)
    cb = json.load(open(os.path.join(SKILL, ep, "out", "plan", "camera_baked.json")))
    F = [dict(c, f=i) for i, c in enumerate(cb["frames"]) if frames[0] <= i <= frames[1]]
    from_lock.camera(scene, F); scene.frame_start, scene.frame_end = frames[0], frames[1]
    cam = scene.camera
    for c in list(cam.users_collection): c.objects.unlink(cam)
    _col("RC_CAMERA").objects.link(cam); return cam

def build(place_path, out_blend, light=True):
    P = json.load(open(place_path)); bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; cols = {}; report = {"place": P["place_id"]}
    t = P.get("terrain"); ground = None
    def flat_mat(spec):                                          # a named palette material; rc.lookdev gives it its PBR detail by name
        m = bpy.data.materials.get(spec["name"]) or bpy.data.materials.new(spec["name"]); m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lookdev._hex(spec["color"]), 1); return m
    if t:
        tm = t.get("material"); tm = flat_mat(tm) if isinstance(tm, dict) else (_material(tm) if tm else None)
        ground = geo.terrain("terrain", t["size"], t.get("res", 64), t.get("height", 0), t.get("seed", 1), _col("RC_TERRAIN"), tm)
    for st in P.get("strips", []):                               # lanes, ruts, paths: a strip that hugs the terrain (shrinkwrap), own material
        (ax, ay), (bx, by) = st["from"], st["to"]; L = math.hypot(bx - ax, by - ay); n = max(2, int(L / 1.0))
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=n, y_subdivisions=4, size=1); o = bpy.context.object; o.name = st["name"]
        o.scale = (L, st["width"], 1); bpy.ops.object.transform_apply(scale=True); o.rotation_euler = (0, 0, math.atan2(by - ay, bx - ax)); o.location = ((ax + bx) / 2, (ay + by) / 2, .5)
        for c in list(o.users_collection): c.objects.unlink(o)
        _col("RC_TERRAIN").objects.link(o); o.data.materials.append(flat_mat(st["material"]))
        if ground: sw = o.modifiers.new("hug", "SHRINKWRAP"); sw.target = ground; sw.wrap_method = "PROJECT"; sw.use_negative_direction = True; sw.offset = st.get("offset", .02)
    A = _col("RC_ASSETS")
    for a in P.get("assets", []):
        if a.get("physics"): continue                               # destructible placements are realised by rc.physics below
        bl_library.instance(_source(a["asset"], cols), a.get("name", a["asset"]), a["at"], math.radians(a.get("rot", 0)), a.get("scale", 1.0), A)
    S = _col("RC_SCATTER")
    for s in P.get("scatter", []):
        pts, rots, scl = geo.scatter_points(s["zone"], s["count"], s["seed"], s.get("exclude", ()), tuple(s.get("scale", (1, 1))))
        var = bool(library.index().get(s["asset"], {}).get("variants"))
        geo.instancer(s.get("name", s["asset"]), pts, _source(s["asset"], cols), S, rots, scl, pick=var, seed=s["seed"], wind=s.get("wind", 0.0)); report.setdefault("scatter", {})[s.get("name", s["asset"])] = len(pts)
    cm = P.get("camera")
    if cm and cm.get("pos"):                                     # a fixed test camera (prototype shots that are not in the film plan)
        d = bpy.data.cameras.new("TestCam"); d.sensor_fit = "VERTICAL"; d.sensor_height = 24; d.lens = 12 / math.tan(math.radians(cm.get("fov_v", 45)) / 2); d.clip_end = 5000
        o = bpy.data.objects.new("TestCam", d); _col("RC_CAMERA").objects.link(o); o.location = cm["pos"]
        sys.path.insert(0, os.path.join(SKILL, "templates")); from blender_look import from_lock
        o.rotation_mode = "QUATERNION"; o.rotation_quaternion = from_lock._rot(cm["pos"], cm["aim"], None, 0.0); sc.camera = o
    elif cm: _camera(sc, P["episode"], cm["frames"])
    if light and P.get("light"):
        sys.path.insert(0, os.path.join(SKILL, "templates"))
        from blender_look import look
        look.apply_look(sc, P["light"].get("preset", "day"), key_dir=tuple(P["light"]["key_dir"]) if P["light"].get("key_dir") else None)
        vt = P["light"].get("view_transform")
        if vt: sc.view_settings.view_transform = vt; sc.view_settings.look = "None"   # the three.js preview used Neutral tone mapping: same transform = same colours
        if "exposure" in P["light"]: sc.view_settings.exposure = P["light"]["exposure"]
        if "white_balance" in P["light"]: sc.view_settings.use_white_balance = True; sc.view_settings.white_balance_temperature = P["light"]["white_balance"]
        for o in [o for o in sc.collection.objects if o.type == "LIGHT"]: sc.collection.objects.unlink(o); _col("RC_LIGHTS").objects.link(o)
    fps = 30
    if P.get("animation"): report["animation"] = animate.apply(sc, P["animation"], fps)
    if P.get("physics"):
        for ph in P["physics"]:
            if ph["type"] == "crash":
                report.setdefault("physics", []).append(physics.crash(sc, ph, _source(ph["target_asset"], cols), ground, bpy.data.objects[ph["striker"]["name"]]))
    if P.get("fx"): report["fx_objects"] = vfx.apply(sc, P["fx"])
    if P.get("characters") and sc.camera:
        ch = P["characters"]; lock = os.path.join(SKILL, P["episode"], ch["lock"])
        report["characters"] = sorted(characters.place_cards(sc, lock, ch["who"], sc.camera, ch.get("self_lit", .55)))
    if P.get("lookdev"): report["lookdev"] = lookdev.apply(P["lookdev"]["rules"])
    if P.get("frames"): sc.frame_start, sc.frame_end = P["frames"]
    os.makedirs(os.path.dirname(out_blend), exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
    report["assets_used"] = sorted(cols); return report
