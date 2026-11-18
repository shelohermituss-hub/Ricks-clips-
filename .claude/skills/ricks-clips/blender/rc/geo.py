"""rc.geo — shared geometry helpers for the builders (runs inside Blender). Mission 1, 2026-11-18.
  instancer(name, points, src, collection, rots=None, scales=None)   ONE object whose geometry nodes put `src` (an object or a
       collection) on every point with its own rotation (euler XYZ) and scale: thousands of copies, one object (QA-014 / PI-011)
  scatter_points(zone, count, seed, exclude, scale_range, rot_z=True)  deterministic points (own RNG from the seed, never global random)
  terrain(name, size, res, height, seed, collection)                   a displaced ground grid (real relief, not a flat plane)"""
import math, random
import bpy

def _gn_instancer(name, src, pick=False, seed=0, wind=0.0):
    nt = bpy.data.node_groups.new(name, "GeometryNodeTree")
    nt.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"); nt.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = nt.nodes, nt.links; gi, go, iop = N.new("NodeGroupInput"), N.new("NodeGroupOutput"), N.new("GeometryNodeInstanceOnPoints")
    if isinstance(src, bpy.types.Collection):
        info = N.new("GeometryNodeCollectionInfo"); info.inputs["Collection"].default_value = src; info.transform_space = "ORIGINAL"
        info.inputs["Separate Children"].default_value = pick; info.inputs["Reset Children"].default_value = True; out = info.outputs[0]
    else:
        info = N.new("GeometryNodeObjectInfo"); info.inputs["Object"].default_value = src; info.transform_space = "ORIGINAL"; out = info.outputs["Geometry"]
    ra, sa = N.new("GeometryNodeInputNamedAttribute"), N.new("GeometryNodeInputNamedAttribute"); ra.data_type = sa.data_type = "FLOAT_VECTOR"
    ra.inputs["Name"].default_value = "inst_rot"; sa.inputs["Name"].default_value = "inst_scale"; e2r = N.new("FunctionNodeEulerToRotation")
    L.new(gi.outputs[0], iop.inputs["Points"]); L.new(out, iop.inputs["Instance"]); L.new(ra.outputs["Attribute"], e2r.inputs[0]); L.new(e2r.outputs[0], iop.inputs["Rotation"])
    L.new(sa.outputs["Attribute"], iop.inputs["Scale"]); last = iop.outputs["Instances"]
    if wind:                                                     # WIND (micro-animation): each instance leans by a noise of (position, scene time): a pure function of the frame
        st = N.new("GeometryNodeInputSceneTime"); pos = N.new("GeometryNodeInputPosition"); sh = N.new("ShaderNodeVectorMath"); sh.operation = "SCALE"; sh.inputs[3].default_value = .15
        L.new(pos.outputs[0], sh.inputs[0]); nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = 1.0
        L.new(sh.outputs[0], nz.inputs["Vector"]); tw = N.new("ShaderNodeMath"); tw.operation = "MULTIPLY"; tw.inputs[1].default_value = .35; L.new(st.outputs["Seconds"], tw.inputs[0]); L.new(tw.outputs[0], nz.inputs["W"])
        sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (.5, .5, .5); L.new(nz.outputs["Color"], sub.inputs[0])
        amp = N.new("ShaderNodeVectorMath"); amp.operation = "MULTIPLY"; amp.inputs[1].default_value = (wind, wind, 0); L.new(sub.outputs[0], amp.inputs[0])
        e2 = N.new("FunctionNodeEulerToRotation"); L.new(amp.outputs[0], e2.inputs[0]); rot = N.new("GeometryNodeRotateInstances"); rot.inputs["Local Space"].default_value = True
        L.new(last, rot.inputs["Instances"]); L.new(e2.outputs[0], rot.inputs["Rotation"]); last = rot.outputs["Instances"]
    L.new(last, go.inputs[0])
    if pick:                                                     # one variant per point: seeded random index from the point id (frame-independent)
        iop.inputs["Pick Instance"].default_value = True; rv = N.new("FunctionNodeRandomValue"); rv.data_type = "INT"
        rv.inputs["Min"].default_value = 0; rv.inputs["Max"].default_value = 10000; rv.inputs["Seed"].default_value = seed
        L.new(rv.outputs[2] if len(rv.outputs) > 2 else rv.outputs[0], iop.inputs["Instance Index"])
    return nt

def instancer(name, points, src, collection, rots=None, scales=None, pick=False, seed=0, wind=0.0):
    me = bpy.data.meshes.new(name + "_pts"); me.from_pydata([tuple(p) for p in points], [], []); me.update()
    ra = me.attributes.new("inst_rot", "FLOAT_VECTOR", "POINT"); sa = me.attributes.new("inst_scale", "FLOAT_VECTOR", "POINT")
    for i in range(len(points)):
        ra.data[i].vector = rots[i] if rots else (0, 0, 0)
        s = scales[i] if scales else 1.0; sa.data[i].vector = (s, s, s) if isinstance(s, (int, float)) else s
    ob = bpy.data.objects.new(name, me); collection.objects.link(ob); ob.modifiers.new("instances", "NODES").node_group = _gn_instancer(name, src, pick, seed, wind); return ob

def _seg_dist(zone, x, y):
    (ax, ay), (bx, by) = zone["from"], zone["to"]; dx, dy = bx - ax, by - ay; t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy + 1e-12)))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)

def _inside(zone, x, y):
    if "from" in zone: return _seg_dist(zone, x, y) <= zone["width"] / 2           # a band along a line (hedges, lanes, walls)
    if "radius" in zone: return math.hypot(x - zone["center"][0], y - zone["center"][1]) <= zone["radius"]
    poly = zone["polygon"]; c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi: c = not c
        j = i
    return c

def scatter_points(zone, count, seed, exclude=(), scale_range=(1, 1), rot_z=True, z=0.0, max_tries=50):
    R = random.Random(seed)                                     # own generator: the same seed gives the same points, whatever ran before
    if "from" in zone:
        (ax, ay), (bx, by) = zone["from"], zone["to"]; h = zone["width"] / 2; x0, y0, x1, y1 = min(ax, bx) - h, min(ay, by) - h, max(ax, bx) + h, max(ay, by) + h
    elif "radius" in zone: x0, y0, x1, y1 = zone["center"][0] - zone["radius"], zone["center"][1] - zone["radius"], zone["center"][0] + zone["radius"], zone["center"][1] + zone["radius"]
    else: xs, ys = zip(*zone["polygon"]); x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    P, Rot, S = [], [], []
    for _ in range(count):
        for _t in range(max_tries):
            x, y = R.uniform(x0, x1), R.uniform(y0, y1)
            if _inside(zone, x, y) and not any(_inside(e, x, y) for e in exclude): break
        else: continue
        P.append((x, y, z)); Rot.append((0, 0, R.uniform(0, 2 * math.pi) if rot_z else 0)); S.append(R.uniform(*scale_range))
    return P, Rot, S

def terrain(name, size, res, height, seed, collection, material=None):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=res, y_subdivisions=res, size=1)
    ob = bpy.context.object; ob.name = name; ob.scale = (size[0], size[1], 1); bpy.ops.object.transform_apply(scale=True)
    R = random.Random(seed); ph = [(R.uniform(0, 6.28), R.uniform(.02, .06), R.uniform(.02, .06)) for _ in range(4)]
    for v in ob.data.vertices:                                   # gentle rolling relief (sum of low waves), 0 at the centre zone where the action stands
        x, y = v.co.x, v.co.y; d = min(1.0, math.hypot(x, y) / 25.0)
        v.co.z = height * d * sum(math.sin(x * fx + p) * math.cos(y * fy + p * .7) for p, fx, fy in ph) / 4
    for p in ob.data.polygons: p.use_smooth = True
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob)
    if material: ob.data.materials.append(material)
    return ob
