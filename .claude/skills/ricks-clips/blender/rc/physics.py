"""rc.physics — G. Interaction & Physics Engine (Mission 2, 2026-11-18). Runs inside Blender (Bullet rigid bodies).
Three tiers (Mission 0): 1 = keyed simple interaction (rc.animate), 2 = controlled rigid-body sim, 3 = PREPARED destruction (this module's
`crash`): the target asset becomes real objects, chosen parts are pre-fractured (seeded plane cuts, real cut faces), every piece is a
rigid body (mass from volume x density), neighbouring pieces are held by BREAKABLE fixed joints (weaker joints where a part should come
off, e.g. a wheel), the striker pushes through an animated collision proxy that follows its own baked path, and the result is
SIMULATED then BAKED TO KEYS: after baking there is no simulation state left, every frame is a pure function of its number, so slices
and single frames agree (PI-012). Fracture uses no add-on (Cell Fracture is not bundled with Blender 5.2): bmesh bisect + fill.
  crash spec (place.json "physics"): {"type": "crash", "target_asset": "farm_cart", "name": "cart", "at": [x, y, 0], "rot": deg,
      "striker": {"name": "dozer", "box": [[x0,y0,z0],[x1,y1,z1]] in the striker's local metres},
      "frames": [f0, f1], "release": f, "fracture": {"cart_plank_0": {"pieces": 3, "seed": 1}, ...},
      "joint_strength": 60, "weak": {"cart_wheel_": 12, "cart_shaft_": 25}, "densities": {"wood": 600, "wood_dark": 650, "iron": 7800}}"""
import math, random
import bmesh, bpy
from mathutils import Vector

def _col(scene, name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children: scene.collection.children.link(c)
    return c

def realize(scene, asset_col, name, at, rot_z, col):
    """copy the asset's objects as real, independent objects at the placement (meshes copied: each piece may be cut)"""
    from mathutils import Matrix
    M = Matrix.Translation(Vector(at)) @ Matrix.Rotation(rot_z, 4, "Z"); out = []
    for o in asset_col.all_objects:
        if o.type != "MESH": continue
        c = o.copy(); c.data = o.data.copy(); c.parent = None; c.matrix_world = M @ o.matrix_world; c.name = name + ":" + o.name.split(".")[0]
        col.objects.link(c); out.append(c)
    return out

def fracture(ob, pieces, seed, col):
    """cut a mesh into `pieces` across its longest axis at seeded, slightly tilted planes; returns the pieces (the original is removed)"""
    R = random.Random(seed); bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]; lo = Vector([min(c) for c in zip(*bb)]); hi = Vector([max(c) for c in zip(*bb)])
    ax = max(range(3), key=lambda i: hi[i] - lo[i]); cuts = sorted(R.uniform(.2, .8) for _ in range(pieces - 1)); bounds = [0.0] + cuts + [1.0]; out = []
    for i in range(pieces):
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
        for j, keep_side in ((i, +1), (i + 1, -1)):
            if j in (0, pieces): continue
            n = Vector((0, 0, 0)); n[ax] = 1.0; n[(ax + 1) % 3] = R.uniform(-.35, .35); n[(ax + 2) % 3] = R.uniform(-.2, .2); n.normalize()
            co = lo.copy(); co[ax] = lo[ax] + (hi[ax] - lo[ax]) * bounds[j]
            g = bm.verts[:] + bm.edges[:] + bm.faces[:]
            r = bmesh.ops.bisect_plane(bm, geom=g, plane_co=co, plane_no=n, clear_inner=keep_side > 0, clear_outer=keep_side < 0)
            cut = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
            if cut: bmesh.ops.holes_fill(bm, edges=cut)             # real cut faces: the broken end of the plank is solid wood, not a hole
        if not bm.verts: bm.free(); continue
        me = bpy.data.meshes.new(ob.name + "_frag%d" % i); bm.to_mesh(me); bm.free()
        for m in ob.data.materials: me.materials.append(m)
        p = bpy.data.objects.new(ob.name + "_frag%d" % i, me); col.objects.link(p)
        ctr = sum((v.co for v in me.vertices), Vector()) / max(1, len(me.vertices)); me.transform(__import__("mathutils").Matrix.Translation(-ctr)); p.location = ctr; out.append(p)
    bpy.data.objects.remove(ob, do_unlink=True); return out

def _volume(o):
    bm = bmesh.new(); bm.from_mesh(o.data); v = abs(bm.calc_volume(signed=False)); bm.free(); s = o.scale; return max(1e-5, v * s[0] * s[1] * s[2])

def _aabb(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; return Vector([min(c) for c in zip(*bb)]), Vector([max(c) for c in zip(*bb)])

def crash(scene, spec, asset_col, ground, striker_empty, log=print):
    col = _col(scene, "RC_PHYSICS"); rot = math.radians(spec.get("rot", 0)); f0, f1 = spec["frames"]
    parts = realize(scene, asset_col, spec.get("name", "target"), spec["at"], rot, col)
    for pre, fr in (spec.get("fracture") or {}).items():
        for o in [o for o in parts if o.name.split(":")[-1].startswith(pre)]:
            parts.remove(o); parts += fracture(o, fr.get("pieces", 3), fr.get("seed", 1), col)
    if scene.rigidbody_world is None: bpy.ops.rigidbody.world_add()
    rw = scene.rigidbody_world; rw.collection = _col(scene, "RC_RIGIDBODY"); rw.point_cache.frame_start, rw.point_cache.frame_end = f0, f1
    rw.substeps_per_frame = 20; rw.solver_iterations = 30
    def rb(o, kind, mass=1.0, shape="CONVEX_HULL"):
        if o.name not in rw.collection.objects: rw.collection.objects.link(o)
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        if o.rigid_body is None: bpy.ops.rigidbody.object_add()
        r = o.rigid_body; r.type = kind; r.collision_shape = shape; r.friction = .75; r.restitution = .12; r.linear_damping = .08; r.angular_damping = .12
        if kind == "ACTIVE": r.mass = mass
        o.select_set(False); return r
    D = spec.get("densities", {"wood": 600, "wood_dark": 650, "iron": 7800})
    for o in parts:
        m = o.data.materials[0].name.split(".")[0] if o.data.materials else "wood"; r = rb(o, "ACTIVE", _volume(o) * D.get(m, 600))
        r.kinematic = True; r.keyframe_insert("kinematic", frame=f0)                  # held still (as built) until the release frame: no settling jitter
        r.kinematic = False; r.keyframe_insert("kinematic", frame=spec.get("release", f0 + 1))
    for o in parts:                                              # wheels go through their axle by design: separate collision group, so a broken
        if any(k in o.name for k in spec.get("own_group", ["cart_wheel_"])):                 # wheel joint does not explode from an overlap
            o.rigid_body.collision_collections[0] = False; o.rigid_body.collision_collections[1] = True
    g = rb(ground, "PASSIVE", shape="MESH"); g.collision_collections[1] = True
    lo, hi = spec["striker"]["box"]; bpy.ops.mesh.primitive_cube_add(size=1); px = bpy.context.object; px.name = "striker_proxy"
    for c in list(px.users_collection): c.objects.unlink(px)
    col.objects.link(px); px.dimensions = [hi[i] - lo[i] for i in range(3)]; bpy.ops.object.transform_apply(scale=True)
    off = Vector([(lo[i] + hi[i]) / 2 for i in range(3)]); px.hide_render = True; px.display_type = "WIRE"
    from mathutils import Matrix
    for f in range(f0, f1 + 1):                                  # the proxy gets its OWN keys copied from the striker (a parented rigid body is not reliable in Bullet)
        scene.frame_set(f); px.matrix_world = striker_empty.matrix_world @ Matrix.Translation(off); px.keyframe_insert("location", frame=f); px.keyframe_insert("rotation_euler", frame=f)
    r = rb(px, "PASSIVE", shape="BOX"); r.kinematic = True; r.collision_collections[1] = True
    S, W = spec.get("joint_strength", 60), spec.get("weak", {}); n = 0; bpy.context.view_layer.update(); boxes = {o.name: _aabb(o) for o in parts}
    for i, a in enumerate(parts):                                                    # breakable joints between touching pieces
        la, ha = boxes[a.name]
        for b in parts[i + 1:]:
            lb, hb = boxes[b.name]
            if all(la[k] - .03 <= hb[k] and lb[k] - .03 <= ha[k] for k in range(3)):
                e = bpy.data.objects.new("joint_%04d" % n, None); col.objects.link(e); e.location = ((la + ha) / 2 + (lb + hb) / 2) / 2
                bpy.context.view_layer.objects.active = e; e.select_set(True); bpy.ops.rigidbody.constraint_add(); e.select_set(False)
                c = e.rigid_body_constraint; c.type = "FIXED"; c.object1, c.object2 = a, b; c.use_breaking = True
                thr = min([v for p, v in W.items() if p in a.name or p in b.name] or [S]); c.breaking_threshold = thr; n += 1
    log("[physics] %d pieces, %d breakable joints" % (len(parts), n))
    bpy.ops.ptcache.free_bake_all(); scene.frame_set(f0)
    with bpy.context.temp_override(scene=scene, point_cache=rw.point_cache): bpy.ops.ptcache.bake(bake=True)
    # simulation -> plain keys (deterministic, slice-safe). Own loop: bpy.ops.rigidbody.bake_to_keyframes needs a UI context (fails headless)
    M = {o.name: [] for o in parts}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        for o in parts: M[o.name].append(o.matrix_world.copy())
    for o in parts:
        rw.collection.objects.unlink(o)
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]): bpy.ops.rigidbody.object_remove()
        o.rotation_mode = "QUATERNION"; prev = None
        for i, m in enumerate(M[o.name]):
            loc, q, sc_ = m.decompose()
            if prev is not None and q.dot(prev) < 0: q.negate()
            prev = q; o.location = loc; o.rotation_quaternion = q; o.keyframe_insert("location", frame=f0 + i); o.keyframe_insert("rotation_quaternion", frame=f0 + i)
    for o in [o for o in col.objects if o.name.startswith("joint_")]: bpy.data.objects.remove(o, do_unlink=True)
    with bpy.context.temp_override(scene=scene): bpy.ops.rigidbody.world_remove()        # no live simulation left in the file
    rel = spec.get("release", f0 + 1); moved, track = 0, {}
    for o in parts:                                              # proof of consequence: where each piece is before the release and at the end
        scene.frame_set(rel - 1); p0 = o.matrix_world.translation.copy(); scene.frame_set(f1); p1 = o.matrix_world.translation.copy(); d = (p1 - p0).length
        if d > .05: moved += 1
        nm = o.name.split(":")[-1]
        if nm in ("cart_wheel_L", "cart_wheel_R", "cart_axle") or nm.endswith("_frag0") and "plank_03" in nm: track[nm] = {"before": [round(v, 2) for v in p0], "end": [round(v, 2) for v in p1], "moved_m": round(d, 2)}
    return {"pieces": len(parts), "joints": n, "pieces_moved_after_release": moved, "track": track}
