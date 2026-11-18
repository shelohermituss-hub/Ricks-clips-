"""rc.animate — F. Animation Engine (Mission 2, 2026-11-18). Runs inside Blender.
Every animated value is BAKED as keys, one per frame, from a pure function of the frame number (never from the previous frame's state):
a frame renders the same alone or inside a slice (PI-012). Recipes are named, data-driven from place.json "animation":
  lift_set   the field hook: a held tank above its four lifters, a small bob while held, lowered between lift[1] and set,
             a squash on the dent (same curve as the approved V3 / ghost.js, so the timing matches the voice)
  path       an object moving along points at a speed (vehicles), heading along the path, optional engine shake
Micro-animation of vegetation is in rc.geo (wind on instances, geometry nodes, scene time)."""
import math
import bpy

def sm(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def _bake(ob, f0, f1, fn):
    for f in range(f0, f1 + 1):
        loc, rot, scl = fn(f); ob.location = loc; ob.rotation_euler = rot; ob.scale = scl
        ob.keyframe_insert("location", frame=f); ob.keyframe_insert("rotation_euler", frame=f); ob.keyframe_insert("scale", frame=f)

def lift_set(ob, f0, f1, at, rot_z, lift=(0, 60), set_f=103, dent=110, height=1.55):
    def fn(f):
        b = sm((f - lift[1]) / (set_f - lift[1])); z = height * (1 - b) + .03 * math.sin(f * .21) * (1 - b)
        d = max(0.0, 1 - abs(f - dent) / 10); sag = .12 * d
        return (at[0], at[1], at[2] + z), (0, 0, rot_z), (1, 1, 1 - .45 * sag)
    _bake(ob, f0, f1, fn)

def path(ob, f0, f1, pts, speed, fps=30, z=0.0, shake=0.0, start=None, heading_offset=0.0):
    P = [tuple(p) for p in pts]; segs = [(P[i], P[i + 1], math.dist(P[i], P[i + 1])) for i in range(len(P) - 1)]; total = sum(s[2] for s in segs); t0 = f0 if start is None else start
    def at(dist):
        dist = max(0.0, min(total, dist))
        for a, b, L in segs:
            if dist <= L: k = dist / L; return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), math.atan2(b[1] - a[1], b[0] - a[0])
            dist -= L
        a, b, _ = segs[-1]; return b, math.atan2(b[1] - a[1], b[0] - a[0])
    def fn(f):
        (x, y), h = at(max(0, f - t0) * speed / fps); jit = shake * math.sin(f * 2.7) * (1 if f >= t0 else .3)
        return (x, y, z + jit), (0, jit * .3, h + heading_offset), (1, 1, 1)
    _bake(ob, f0, f1, fn)

def hinge(ob, f0, f1, open_f, close_f=None, angle=95, axis="Z", ease=12):
    """a door/shutter/lid on its hinge (object origin ON the hinge): opens over `ease` frames from open_f, optional close"""
    i = "XYZ".index(axis); base = list(ob.rotation_euler)
    def fn(f):
        k = sm((f - open_f) / ease) - (sm((f - close_f) / ease) if close_f is not None else 0); r = list(base); r[i] = base[i] + math.radians(angle) * k
        return tuple(ob.location), tuple(r), tuple(ob.scale)
    _bake(ob, f0, f1, fn)

def bob(ob, f0, f1, amp=4.0, period=2.4, fps=30, axis="X", phase=0.0):
    """a hanging object swinging (lantern, sign, washing): angle = amp * sin(2 pi t / period)"""
    i = "XYZ".index(axis); base = list(ob.rotation_euler); loc = tuple(ob.location); sc = tuple(ob.scale)
    def fn(f): r = list(base); r[i] = base[i] + math.radians(amp) * math.sin(2 * math.pi * f / fps / period + phase); return loc, tuple(r), sc
    _bake(ob, f0, f1, fn)

def orbit(ob, f0, f1, center, radius, height, deg_per_s, fps=30, start_deg=0.0):
    def fn(f):
        a = math.radians(start_deg + deg_per_s * (f - f0) / fps); return (center[0] + radius * math.cos(a), center[1] + radius * math.sin(a), height), (0, 0, a + math.pi / 2), (1, 1, 1)
    _bake(ob, f0, f1, fn)

def spin(ob, f0, f1, rpm, axis="Z", fps=30):
    i = "XYZ".index(axis); base = list(ob.rotation_euler); loc = tuple(ob.location); sc = tuple(ob.scale)
    def fn(f): r = list(base); r[i] = base[i] + 2 * math.pi * rpm / 60 * (f - f0) / fps; return loc, tuple(r), sc
    _bake(ob, f0, f1, fn)

def flicker(light_ob, f0, f1, base_energy=None, amount=.35, seed=1, rate=9.0, fps=30):
    """a flame or failing bulb: energy follows two summed sines + a seeded hash (frame-only, deterministic)"""
    L = light_ob.data; e0 = base_energy or L.energy
    for f in range(f0, f1 + 1):
        t = f / fps; h = math.sin(f * 12.9898 + seed * 78.233) * 43758.5453; n = h - math.floor(h)
        L.energy = e0 * (1 - amount / 2 + amount * (.35 * math.sin(t * rate) + .25 * math.sin(t * rate * 2.3 + seed) + .4 * n)); L.keyframe_insert("energy", frame=f)

def look_at(ob, f0, f1, target, fps=30):
    loc = tuple(ob.location); sc = tuple(ob.scale)
    def fn(f):
        bpy.context.scene.frame_set(f); tp = target.matrix_world.translation; return loc, (0, 0, math.atan2(tp.y - loc[1], tp.x - loc[0])), sc
    _bake(ob, f0, f1, fn)

def vehicle_drive(ob, f0, f1, pts, speed, fps=30, wheel_radius=.5, wheels=(), ground=None, heading_offset=0.0, start=None, stop=None):
    """a vehicle along a path ON the ground (z from the terrain), heading along the path; named wheel objects (instances or real) turn by
    distance / radius, so wheels roll without sliding. stop: frame where it brakes (eased) and stays."""
    from rc import envbuild
    P = [tuple(p) for p in pts]; segs = [(P[i], P[i + 1], math.dist(P[i], P[i + 1])) for i in range(len(P) - 1)]; total = sum(x[2] for x in segs); t0 = f0 if start is None else start
    def dist_at(f):
        if stop is not None and f > stop: f = stop + (1 - (1 - min(1, (f - stop) / 20)) ** 2) * 10
        return min(total, max(0, f - t0) * speed / fps)
    def at(d):
        for a, b, L in segs:
            if d <= L: k = d / L; return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), math.atan2(b[1] - a[1], b[0] - a[0])
            d -= L
        a, b, _ = segs[-1]; return b, math.atan2(b[1] - a[1], b[0] - a[0])
    def fn(f):
        (x, y), h = at(dist_at(f)); return (x, y, envbuild.ground_z(ground, x, y)), (0, 0, h + heading_offset), (1, 1, 1)
    _bake(ob, f0, f1, fn)
    for wn in wheels:
        w = bpy.data.objects.get(wn)
        if w is None: continue
        base = list(w.rotation_euler)
        for f in range(f0, f1 + 1): w.rotation_euler = (base[0], base[1] + dist_at(f) / wheel_radius, base[2]); w.keyframe_insert("rotation_euler", frame=f)
    return total

def cloth(scene, spec, ground=None):
    """CLOTH (polish): a flag or a sheet on a line, simulated (Blender Cloth, wind force field, seeded turbulence) then BAKED TO KEYS per
    vertex via shape keys -> no live simulation in the file, every frame a pure function of its number (PI-012)."""
    f0, f1 = spec["frames"]; w, h = spec.get("size", [1.2, .9]); seg = spec.get("segments", 18)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=seg, y_subdivisions=int(seg * h / w), size=1); ob = bpy.context.object; ob.name = spec.get("name", "cloth")
    ob.scale = (w, h, 1); bpy.ops.object.transform_apply(scale=True); ob.rotation_euler = (math.radians(90), 0, math.radians(spec.get("rot", 0))); ob.location = spec["at"]
    bpy.ops.object.transform_apply(rotation=True, location=True); me = ob.data; top = max(v.co.z for v in me.vertices)
    vg = ob.vertex_groups.new(name="pin"); vg.add([v.index for v in me.vertices if abs(v.co.z - top) < 1e-4 and (spec.get("type") == "line_cloth" or v.co.x < min(u.co.x for u in me.vertices) + 1e-4 or True)], 1.0, "REPLACE")
    if spec.get("type") == "flag": vg.remove([v.index for v in me.vertices]); vg.add([v.index for v in me.vertices if abs(v.co.x - min(u.co.x for u in me.vertices)) < 1e-4], 1.0, "REPLACE")
    if spec.get("material"):
        m = bpy.data.materials.get(spec["material"]["name"]) or bpy.data.materials.new(spec["material"]["name"]); m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*[((int(spec["material"]["color"][i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5)], 1); me.materials.append(m)
    so = ob.modifiers.new("thick", "SOLIDIFY"); so.thickness = .004
    cl = ob.modifiers.new("cloth", "CLOTH"); cs = cl.settings; cs.vertex_group_mass = "pin"; cs.quality = 6; cs.mass = spec.get("mass", .15); cl.point_cache.frame_start, cl.point_cache.frame_end = f0, f1
    ob.modifiers.move(1, 0)
    bpy.ops.object.effector_add(type="WIND", location=(ob.location.x - 3, ob.location.y, ob.location.z)); wd = bpy.context.object; wd.name = ob.name + "_wind"
    wd.rotation_euler = (0, math.radians(90), math.radians(spec.get("wind_dir", 0))); wd.field.strength = spec.get("wind", 160); wd.field.noise = spec.get("gust", 3.0); wd.field.seed = spec.get("seed", 1)
    scene.frame_set(f0)
    with bpy.context.temp_override(scene=scene, point_cache=cl.point_cache): bpy.ops.ptcache.bake(bake=True)
    # bake to shape keys (frame-exact): one shape key per frame, keyed 1 on its frame only
    dg = bpy.context.evaluated_depsgraph_get(); frames = {}
    for f in range(f0, f1 + 1):
        scene.frame_set(f); ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); frames[f] = [v.co.copy() for v in ev.to_mesh().vertices]; ev.to_mesh_clear()
    ob.modifiers.remove(ob.modifiers["cloth"]); bpy.data.objects.remove(wd, do_unlink=True); n = len(me.vertices)
    ob.shape_key_add(name="Basis")
    for f, co in frames.items():
        k = ob.shape_key_add(name="f%05d" % f, from_mix=False)
        for i in range(min(n, len(co))): k.data[i].co = co[i]
        for g, val in ((f - 1, 0.0), (f, 1.0), (f + 1, 0.0)): k.value = val; k.keyframe_insert("value", frame=g)
    return {"cloth": ob.name, "frames": len(frames), "verts": n}

def apply(scene, specs, fps=30, ground=None):
    rep = {}
    for s in specs:
        ob = bpy.data.objects.get(s["target"])
        if ob is None: rep[s["target"]] = "MISSING"; continue
        if s["type"] == "lift_set": lift_set(ob, s["frames"][0], s["frames"][1], s["at"], math.radians(s.get("rot", 0)), tuple(s.get("lift", (0, 60))), s.get("set", 103), s.get("dent", 110), s.get("height", 1.55))
        elif s["type"] == "path": path(ob, s["frames"][0], s["frames"][1], s["points"], s["speed"], fps, s.get("z", 0.0), s.get("shake", 0.0), s.get("start"), math.radians(s.get("heading_offset", 0)))
        elif s["type"] == "hinge": hinge(ob, s["frames"][0], s["frames"][1], s["open"], s.get("close"), s.get("angle", 95), s.get("axis", "Z"), s.get("ease", 12))
        elif s["type"] == "bob": bob(ob, s["frames"][0], s["frames"][1], s.get("amp", 4.0), s.get("period", 2.4), fps, s.get("axis", "X"), s.get("phase", 0.0))
        elif s["type"] == "orbit": orbit(ob, s["frames"][0], s["frames"][1], s["center"], s["radius"], s["height"], s["deg_per_s"], fps, s.get("start_deg", 0))
        elif s["type"] == "spin": spin(ob, s["frames"][0], s["frames"][1], s["rpm"], s.get("axis", "Z"), fps)
        elif s["type"] == "flicker": flicker(ob, s["frames"][0], s["frames"][1], s.get("energy"), s.get("amount", .35), s.get("seed", 1), s.get("rate", 9.0), fps)
        elif s["type"] == "look_at": look_at(ob, s["frames"][0], s["frames"][1], bpy.data.objects[s["look"]], fps)
        elif s["type"] == "vehicle_drive": rep[s["target"] + "_m"] = vehicle_drive(ob, s["frames"][0], s["frames"][1], s["points"], s["speed"], fps, s.get("wheel_radius", .5), s.get("wheels", ()), ground, math.radians(s.get("heading_offset", 0)), s.get("start"), s.get("stop"))
        rep[s["target"]] = s["type"]
    return rep
