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
from rc import SKILL, geo, library, bl_library  # noqa: E402

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
    t = P.get("terrain")
    if t: geo.terrain("terrain", t["size"], t.get("res", 64), t.get("height", 0), t.get("seed", 1), _col("RC_TERRAIN"), _material(t["material"]) if t.get("material") else None)
    A = _col("RC_ASSETS")
    for a in P.get("assets", []):
        bl_library.instance(_source(a["asset"], cols), a.get("name", a["asset"]), a["at"], math.radians(a.get("rot", 0)), a.get("scale", 1.0), A)
    S = _col("RC_SCATTER")
    for s in P.get("scatter", []):
        pts, rots, scl = geo.scatter_points(s["zone"], s["count"], s["seed"], s.get("exclude", ()), tuple(s.get("scale", (1, 1))))
        var = bool(library.index().get(s["asset"], {}).get("variants"))
        geo.instancer(s.get("name", s["asset"]), pts, _source(s["asset"], cols), S, rots, scl, pick=var, seed=s["seed"]); report.setdefault("scatter", {})[s.get("name", s["asset"])] = len(pts)
    if P.get("camera"): _camera(sc, P["episode"], P["camera"]["frames"])
    if light and P.get("light"):
        sys.path.insert(0, os.path.join(SKILL, "templates"))
        from blender_look import look
        look.apply_look(sc, P["light"].get("preset", "day"))
        for o in [o for o in sc.collection.objects if o.type == "LIGHT"]: sc.collection.objects.unlink(o); _col("RC_LIGHTS").objects.link(o)
    os.makedirs(os.path.dirname(out_blend), exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
    report["assets_used"] = sorted(cols); return report
