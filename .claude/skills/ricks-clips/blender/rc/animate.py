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

def apply(scene, specs, fps=30):
    rep = {}
    for s in specs:
        ob = bpy.data.objects.get(s["target"])
        if ob is None: rep[s["target"]] = "MISSING"; continue
        if s["type"] == "lift_set": lift_set(ob, s["frames"][0], s["frames"][1], s["at"], math.radians(s.get("rot", 0)), tuple(s.get("lift", (0, 60))), s.get("set", 103), s.get("dent", 110), s.get("height", 1.55))
        elif s["type"] == "path": path(ob, s["frames"][0], s["frames"][1], s["points"], s["speed"], fps, s.get("z", 0.0), s.get("shake", 0.0), s.get("start"), math.radians(s.get("heading_offset", 0)))
        rep[s["target"]] = s["type"]
    return rep
