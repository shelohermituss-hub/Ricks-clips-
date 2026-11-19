"""THE tree of crash_instinct (one object for the whole film: planted -> sign -> flashing arrow -> chopped -> stump).
Reference (references/crash_instinct/ANALYSE_FR.md §4): a stylised oak, ~9 m tall, ONE thick trunk (Ø ~0.8 m) with deep grey-brown bark,
big low Y branches, a broad crown (~10-11 m) made of rounded CLUMPS of leaves, light yellow-green where the sun hits, dark green under.
No library model matched (Poly Haven island trees fork at the base, Sketchfab oaks are sparse), so it is built here:
  trunk   tapered tube with a flared, lobed root base; real bark (Poly Haven jolcham_oak_bark_01, CC0)
  limbs   5 main limbs + 2 twigs each, curved tubes from the trunk top into the clumps
  crown   ~34 clumps on an ellipsoid; each = a dark core (density) + real leaf meshes instanced on its surface,
          sunny variants on the upper half, shaded variants underneath (geometry-nodes instancer, rc.geo)
oak(collection, name, seed, height) -> root empty (animate the root: the whole tree follows); parts named <name>_trunk/_limbs/_core/_leaves*."""
import bpy, bmesh, math, random, os, sys
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "crashed_car", "sets")); sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "blender"))
import street  # noqa: E402

def _tube(bm, pts, radii, seg=14, lobes=0, lobe_amp=0.0):
    """a tube through pts (list of Vector) with a radius per point; optional root lobes on the first rings"""
    rings = []
    for i, (p, r) in enumerate(zip(pts, radii)):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = d.orthogonal().normalized(); b = d.cross(a).normalized(); ring = []
        for k in range(seg):
            t = 2 * math.pi * k / seg; rr = r
            if lobes and i < 4: rr *= 1 + lobe_amp * (1 - i / 4) * max(0, math.cos(lobes * t)) ** 2
            rr *= 1 + .04 * math.sin(t * 5 + i * 1.3)                               # bark irregularity
            ring.append(bm.verts.new(p + (a * math.cos(t) + b * math.sin(t)) * rr))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(seg): bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k]))
    bm.faces.new(rings[-1][::-1])

def _bezier(p0, p1, p2, n):
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in [i / (n - 1) for i in range(n)]]

def _leaf_src(name, hexcol):
    """one real leaf: rounded, slightly cupped, 24 cm, midrib fold; built once per colour"""
    cname = "leafsrc_" + name
    if cname in bpy.data.collections: return bpy.data.collections[cname]
    bm = bmesh.new(); n = 9; outline = []
    for k in range(n):
        t = math.pi * k / (n - 1); w = .085 * math.sin(t) * (1 + .25 * math.sin(3 * t))
        outline.append((w, .12 * math.cos(t)))
    L = [bm.verts.new((x, y, -.02 * (x / .085) ** 2)) for x, y in outline]
    R = [bm.verts.new((-x, y, -.02 * (x / .085) ** 2)) for x, y in outline[1:-1]]
    mid = [bm.verts.new((0, y, .012)) for _, y in outline[1:-1]]
    for i in range(len(mid) - 1):
        bm.faces.new((L[i + 1], L[i + 2], mid[i + 1], mid[i])); bm.faces.new((R[i], mid[i], mid[i + 1], R[i + 1]))
    bm.faces.new((L[0], L[1], mid[0])); bm.faces.new((L[0], mid[0], R[0]))
    bm.faces.new((L[-1], mid[-1], L[-2])); bm.faces.new((L[-1], R[-1], mid[-1]))
    me = bpy.data.meshes.new(cname); bm.to_mesh(me); bm.free()
    m = bpy.data.materials.get("leaf_" + name)
    if not m:
        m = street.mat("leaf_" + name, hexcol, .55); b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Subsurface Weight"].default_value = .25; b.inputs["Subsurface Radius"].default_value = (.4, .6, .2)
        b.inputs["Specular IOR Level"].default_value = .35
    me.materials.append(m)
    c = bpy.data.collections.new(cname); c.objects.link(bpy.data.objects.new(cname, me)); return c

def _leaf_set(name, cols):
    """collection holding several leaf colour variants (the instancer picks one at random per point)"""
    if name in bpy.data.collections: return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    for k, h in enumerate(cols):
        src = _leaf_src("%s%d" % (name, k), h); c.objects.link(src.objects[0])
    return c

def oak(collection, name="oak", seed=7, height=9.0, crown=10.6):
    from rc import geo
    R = random.Random(seed); s = height / 9.0
    root = bpy.data.objects.new(name, None); collection.objects.link(root)
    bark = street.pbr("oak_bark", "jolcham_oak_bark_01", tile=1.1, value=.95, normal=1.6)
    # trunk: flared lobed base -> 3.1 m, a slight lean
    bm = bmesh.new()
    tp = [Vector((.06 * math.sin(i * .5) * s, .05 * math.cos(i * .4) * s, i * .39 * s)) for i in range(11)]
    tr = [(.62 - .26 * min(1, i / 10) + (.22 if i == 0 else .1 if i == 1 else 0)) * s for i in range(11)]
    _tube(bm, tp, tr, seg=20, lobes=5, lobe_amp=.55); trunk = street.mesh_obj(name + "_trunk", bm, bark, collection, smooth=True); trunk.parent = root
    top = tp[-1]
    # crown clumps on an ellipsoid (flatter underneath)
    C = Vector((0, 0, 6.9 * s)); rx = crown / 2 * .8; rz = 2.4 * s; clumps = []
    while len(clumps) < 52:
        u = R.uniform(-.35, 1.0); a = R.uniform(0, 2 * math.pi); h = math.sqrt(max(0, 1 - u * u)); r = R.uniform(.72, 1.0)
        p = C + Vector((math.cos(a) * h * rx * r, math.sin(a) * h * rx * r, u * rz * r))
        if all((p - q[0]).length > .95 * s for q in clumps): clumps.append((p, R.uniform(.85, 1.45) * s))
    # limbs: 5 main limbs to the biggest outer clumps, 2 twigs each to neighbours
    bm = bmesh.new(); outer = sorted(clumps, key=lambda q: -(Vector((q[0].x, q[0].y, 0)).length))[:5]
    for k, (p, _) in enumerate(outer):
        start = top + Vector((0, 0, -.2 * s)); mid = start.lerp(p, .45) + Vector((0, 0, .9 * s))
        pts = _bezier(start, mid, p, 9); _tube(bm, pts, [(.3 - .22 * i / 8) * s for i in range(9)], seg=10)
        near = sorted(clumps, key=lambda q: (q[0] - pts[4]).length)[1:3]
        for q, _ in near:
            b0 = pts[4]; pts2 = _bezier(b0, b0.lerp(q, .5) + Vector((0, 0, .4 * s)), q, 6); _tube(bm, pts2, [(.11 - .07 * i / 5) * s for i in range(6)], seg=7)
    limbs = street.mesh_obj(name + "_limbs", bm, bark, collection, smooth=True); limbs.parent = root
    # dark core of every clump (no see-through holes), then the leaves on its surface
    core_m = street.mat("oak_core", "#2f5a1e", .8)
    bm = bmesh.new()
    for p, r in clumps:
        sph = bmesh.new(); bmesh.ops.create_icosphere(sph, subdivisions=2, radius=r * .78)
        vm = {}
        for v in sph.verts: vm[v] = bm.verts.new(p + v.co * (1 + .22 * math.sin(v.co.x * 4 + v.co.z * 3 + v.co.y * 2)))
        for f in sph.faces: bm.faces.new([vm[v] for v in f.verts])
        sph.free()
    core = street.mesh_obj(name + "_core", bm, core_m, collection, smooth=True); core.parent = root
    sunny = _leaf_set("oakleaf_sun", ["#bcd85a", "#9fca46", "#82b83a"]); shade = _leaf_set("oakleaf_shade", ["#5f9a2e", "#4b8326", "#3c6e22"])
    up_pts, up_rot, up_sc, dn_pts, dn_rot, dn_sc = [], [], [], [], [], []
    for p, r in clumps:
        n = int(620 * r / 1.4)
        for _ in range(n):
            u = R.uniform(-1, 1); a = R.uniform(0, 2 * math.pi); h = math.sqrt(1 - u * u); nrm = Vector((math.cos(a) * h, math.sin(a) * h, u))
            q = p + nrm * r * R.uniform(.84, 1.06); e = (nrm + Vector((R.uniform(-.4, .4), R.uniform(-.4, .4), R.uniform(-.2, .4)))).normalized().to_track_quat("Z", "Y").to_euler()
            sc_ = R.uniform(1.0, 1.6) * s; lit = nrm.z + .35 * (nrm.x * -.6 + nrm.y * -.5) > -.05      # faces the sun (from -X, -Y, above)
            (up_pts if lit else dn_pts).append(q - root.location); (up_rot if lit else dn_rot).append(tuple(e)); (up_sc if lit else dn_sc).append(sc_)
    l1 = geo.instancer(name + "_leaves_sun", up_pts, sunny, collection, up_rot, up_sc, pick=True, seed=seed, wind=.02); l1.parent = root
    l2 = geo.instancer(name + "_leaves_shade", dn_pts, shade, collection, dn_rot, dn_sc, pick=True, seed=seed + 1, wind=.02); l2.parent = root
    root["rc_note"] = "%d clumps, %d sunny + %d shaded leaves" % (len(clumps), len(up_pts), len(dn_pts))
    return root
