"""rc.envbuild — C. Environment Builder (deliverable 4, 2026-11-18). Runs inside Blender.
  terrain(spec, col, material)  displaced ground grid with REAL relief (sum of seeded waves), FLAT ZONES where the action stands
                                (blended edge) and a per-vertex PATH MASK (attribute "path_mask", 0..1) along path polylines, so the
                                path is painted INTO the terrain material (rc.lookdev "layers") instead of a floating strip
  lines(spec, src, col)         an asset repeated along a polyline (fences, walls, posts), oriented to the segment, seeded jitter
  scatter(spec, src, col, lod_src)  instanced scatter with optional LOD split by distance to a camera point (near = full asset,
                                far = <id>__lod1), wind, variants
  BIOMES                        named scatter presets (meadow, hedge, path_edge, muddy_yard, woodland_floor) expanded into rules
Everything is seeded and frame-independent; repeated things are always instances (one object per rule)."""
import math, random
import bpy
from mathutils import Vector

def _seg_d(p, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay; t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy + 1e-12)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)

def _poly_d(p, pts): return min(_seg_d(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))

def smooth(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def terrain(spec, col, material=None, name="terrain"):
    sx, sy = spec["size"]; res = spec.get("res", 96); H = spec.get("height", 2.0); R = random.Random(spec.get("seed", 1))
    waves = [(R.uniform(0, 6.28), R.uniform(.015, .06), R.uniform(.015, .06), R.uniform(.5, 1.0)) for _ in range(6)]
    flats = spec.get("flat", []); paths = spec.get("paths", [])
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=res, y_subdivisions=res, size=1); ob = bpy.context.object; ob.name = name
    ob.scale = (sx, sy, 1); bpy.ops.object.transform_apply(scale=True); me = ob.data
    pm = me.attributes.new("path_mask", "FLOAT", "POINT")
    for i, v in enumerate(me.vertices):
        x, y = v.co.x, v.co.y; z = H * sum(a * math.sin(x * fx + p) * math.cos(y * fy + p * .7) for p, fx, fy, a in waves) / 3
        k = 1.0                                                               # flat zones: 0 inside, smooth rise over `blend` metres
        for f in flats: k = min(k, smooth((math.hypot(x - f["center"][0], y - f["center"][1]) - f["radius"]) / f.get("blend", 6.0)))
        m = 0.0
        for pth in paths:
            d = _poly_d((x, y), pth["points"]); w = pth["width"] / 2; m = max(m, 1 - smooth((d - w) / pth.get("feather", 1.2)))
            k = min(k, smooth((d - w) / 3.0) * .7 + .3)                     # paths run nearly flat
        v.co.z = z * k - .03 * m                                              # a path is a slight hollow (ruts) and is painted by the mask
        pm.data[i].value = m
    for p in me.polygons: p.use_smooth = True
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob)
    if material: me.materials.append(material)
    return ob

def ground_z(ground, x, y):
    if ground is None: return 0.0
    hit = ground.ray_cast(ground.matrix_world.inverted() @ Vector((x, y, 500)), Vector((0, 0, -1)))
    return (ground.matrix_world @ hit[1]).z if hit[0] else 0.0

def lines(spec, src, col, ground=None, instancer=None):
    """repeat `src` along spec["points"] every spec["spacing"] metres (fences: one section per spacing), oriented to the segment"""
    R = random.Random(spec.get("seed", 1)); P = spec["points"]; sp = spec.get("spacing", 4.0); pts, rots, scl = [], [], []
    for i in range(len(P) - 1):
        a, b = Vector((*P[i], 0)), Vector((*P[i + 1], 0)); L = (b - a).length; n = max(1, round(L / sp)); h = math.atan2(b.y - a.y, b.x - a.x)
        for k in range(n):
            c = a + (b - a) * ((k + .5) / n); pts.append((c.x, c.y, ground_z(ground, c.x, c.y))); rots.append((0, 0, h + R.uniform(-.02, .02))); scl.append((L / n / sp, 1, 1 + R.uniform(-.04, .04)))
    return instancer(spec.get("name", "line"), pts, src, col, rots, scl)

def drape(pts, ground):
    return [(x, y, ground_z(ground, x, y) + z) for x, y, z in pts]

BIOMES = {   # density per m2, scale range, wind; the asset ids are library ids
    "meadow":         [("grass_medium_02", .9, (1.0, 1.7), .06), ("dandelion_01", .04, (.9, 1.3), .08)],
    "hedge":          [("shrub_04", 3.5, (6.5, 9.5), .035), ("shrub_03", 1.5, (5.0, 7.0), .04), ("nettle_plant", 1.5, (2.5, 3.6), .05)],
    "path_edge":      [("grass_medium_02", 1.6, (1.2, 2.0), .06), ("nettle_plant", .25, (1.6, 2.4), .05)],
    "muddy_yard":     [("grass_medium_02", .12, (.7, 1.1), .05)],
    "woodland_floor": [("fern_02", .2, (1.0, 1.6), .03), ("grass_medium_02", .5, (.9, 1.4), .05)],
}

def biome_rules(biome, zone, seed, exclude=(), density=1.0, name=None, lod=None):
    area = _zone_area(zone); out = []
    for i, (aid, dens, sc, wind) in enumerate(BIOMES[biome]):
        out.append({"asset": aid, "name": "%s_%s_%d" % (name or biome, aid, i), "zone": zone, "count": int(area * dens * density), "seed": seed + 17 * i, "scale": list(sc), "wind": wind, "exclude": list(exclude), **({"lod": lod} if lod else {})})
    return out

def _zone_area(z):
    if "radius" in z: return math.pi * z["radius"] ** 2
    if "from" in z: return math.dist(z["from"], z["to"]) * z["width"]
    P = z["polygon"]; return abs(sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))) / 2

def split_lod(pts, rots, scl, cam_xy, near):
    """indices near the camera (full asset) and far (LOD1)"""
    n, f = [], []
    for i, p in enumerate(pts): (n if math.hypot(p[0] - cam_xy[0], p[1] - cam_xy[1]) <= near else f).append(i)
    pick = lambda I: ([pts[i] for i in I], [rots[i] for i in I], [scl[i] for i in I])
    return pick(n), pick(f)
