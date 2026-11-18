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

def _centre(o): return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8

def realize(scene, asset_col, name, at, rot_z, col):
    """copy the asset's objects as real, independent objects at the placement (meshes copied: each piece may be cut)"""
    from mathutils import Matrix
    M = Matrix.Translation(Vector(at)) @ Matrix.Rotation(rot_z, 4, "Z"); out = []
    for o in asset_col.all_objects:
        if o.type != "MESH": continue
        c = o.copy(); c.data = o.data.copy(); c.parent = None; c.matrix_world = M @ o.matrix_world; c.name = name + ":" + o.name.split(".")[0]
        col.objects.link(c); out.append(c)
    return out

def join(parts, name):
    """merge an asset's parts (body, lid, latch...) into ONE rigid body: small interpenetrating parts simulated separately explode apart
    (measured 2026-11-18: crate latches thrown 33 m)"""
    if len(parts) == 1: return parts[0]
    main = max(parts, key=_volume)
    with bpy.context.temp_override(active_object=main, object=main, selected_objects=parts, selected_editable_objects=parts): bpy.ops.object.join()
    main.name = name; return main

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

# ------------------------------------------------------------------ shared simulation core (deliverable 7, 2026-11-18)
DENS = {"wood": 600, "wood_dark": 650, "iron": 7800, "steel": 7800, "glass": 2500, "stone": 2400, "straw": 120, "rubber": 1100}

class Sim:
    """one rigid-body world for one event: add pieces, passive colliders, animated strikers, breakable joints, then bake() simulates and
    turns every piece's motion into plain keys and removes the world (no live simulation in the file: frame-order independent)."""
    def __init__(self, scene, f0, f1, substeps=20, iters=30):
        self.sc, self.f0, self.f1 = scene, f0, f1; self.parts, self.passive, self.joints = [], [], 0; self.col = _col(scene, "RC_PHYSICS")
        if scene.rigidbody_world is None:
            with bpy.context.temp_override(scene=scene): bpy.ops.rigidbody.world_add()
        rw = scene.rigidbody_world; rw.collection = _col(scene, "RC_RIGIDBODY_%d" % f0); rw.point_cache.frame_start, rw.point_cache.frame_end = f0, f1
        rw.substeps_per_frame = substeps; rw.solver_iterations = iters; self.rw = rw; self.release = {}
    def rb(self, o, kind, mass=1.0, shape="CONVEX_HULL", friction=.75, bounce=.12, group=0):
        if o.name not in self.rw.collection.objects: self.rw.collection.objects.link(o)
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
            if o.rigid_body is None: bpy.ops.rigidbody.object_add()
        r = o.rigid_body; r.type = kind; r.collision_shape = shape; r.friction = friction; r.restitution = bounce; r.linear_damping = .08; r.angular_damping = .12
        r.use_margin = True; r.collision_margin = .001                                   # tiny margin: touching pieces do not push each other apart at release
        if kind == "ACTIVE": r.mass = max(.05, mass)
        for g in range(20): r.collision_collections[g] = (g == group) or (kind == "PASSIVE" and g < 2)
        return r
    def piece(self, o, release, density=None, group=0, shape="CONVEX_HULL", bounce=.12, friction=.75, damping=None):
        m = o.data.materials[0].name.split(".")[0] if o.type == "MESH" and o.data.materials else "wood"
        r = self.rb(o, "ACTIVE", _volume(o) * (density or DENS.get(m, 600)), shape=shape, group=group, bounce=bounce, friction=friction)
        if damping is not None: r.linear_damping = r.angular_damping = damping
        if release > self.f0:
            r.kinematic = True; r.keyframe_insert("kinematic", frame=self.f0); r.kinematic = True; r.keyframe_insert("kinematic", frame=release - 1)
            r.kinematic = False; r.keyframe_insert("kinematic", frame=release)
        self.parts.append(o); self.release[o.name] = release; return r
    def collider(self, o, shape="MESH"):
        r = self.rb(o, "PASSIVE", shape=shape); self.passive.append(o)
        if shape == "MESH": r.mesh_source = "FINAL"; r.collision_margin = .01      # a triangle-mesh ground is paper-thin: a small margin stops pieces pressed through it
    def striker(self, follow, box, name="striker"):
        """an animated box (in `follow`'s local metres) keyed from `follow` every frame (a parented rigid body is unreliable in Bullet)"""
        from mathutils import Matrix
        lo, hi = box; bpy.ops.mesh.primitive_cube_add(size=1); px = bpy.context.object; px.name = name
        for c in list(px.users_collection): c.objects.unlink(px)
        self.col.objects.link(px); px.dimensions = [hi[i] - lo[i] for i in range(3)]; bpy.ops.object.transform_apply(scale=True)
        off = Vector([(lo[i] + hi[i]) / 2 for i in range(3)]); px.hide_render = True; px.display_type = "WIRE"
        for f in range(self.f0, self.f1 + 1):
            self.sc.frame_set(f); px.matrix_world = follow.matrix_world @ Matrix.Translation(off); px.keyframe_insert("location", frame=f); px.keyframe_insert("rotation_euler", frame=f)
        r = self.rb(px, "PASSIVE", shape="BOX"); r.kinematic = True; self.passive.append(px); return px
    def contact_frame(self, striker, targets, gap=.05):
        """first frame where the striker's box reaches any target's box (+gap): the release frame (no jump before the impact)"""
        bpy.context.view_layer.update(); T = [_aabb(o) for o in targets]
        for f in range(self.f0, self.f1 + 1):
            self.sc.frame_set(f); lo, hi = _aabb(striker)
            if any(all(lo[k] - gap <= h[k] and l[k] - gap <= hi[k] for k in range(3)) for l, h in T): return f
        return self.f1
    def joints_between(self, parts, strength, weak=None, tol=.03, kind="FIXED"):
        weak = weak or {}; bpy.context.view_layer.update(); B = {o.name: _aabb(o) for o in parts}; n0 = self.joints
        for i, a in enumerate(parts):
            la, ha = B[a.name]
            for b in parts[i + 1:]:
                lb, hb = B[b.name]
                if all(la[k] - tol <= hb[k] and lb[k] - tol <= ha[k] for k in range(3)):
                    self.joint(a, b, min([v for p, v in weak.items() if p in a.name or p in b.name] or [strength]), kind, ((la + ha) / 2 + (lb + hb) / 2) / 2)
        return self.joints - n0
    def joint(self, a, b, threshold, kind="FIXED", at=None, axis_rot=None):
        e = bpy.data.objects.new("joint_%04d" % self.joints, None); self.col.objects.link(e); e.location = at if at is not None else (a.matrix_world.translation + b.matrix_world.translation) / 2
        if axis_rot: e.rotation_euler = axis_rot
        with bpy.context.temp_override(object=e, active_object=e, selected_objects=[e]): bpy.ops.rigidbody.constraint_add()
        c = e.rigid_body_constraint; c.type = kind; c.object1, c.object2 = a, b; c.use_breaking = threshold is not None; c.disable_collisions = True
        if threshold is not None: c.breaking_threshold = threshold
        self.joints += 1; return c
    def bake(self, track_names=(), before=None):
        sc = self.sc
        with bpy.context.temp_override(scene=sc): bpy.ops.ptcache.free_bake_all()
        sc.frame_set(self.f0)
        with bpy.context.temp_override(scene=sc, point_cache=self.rw.point_cache): bpy.ops.ptcache.bake(bake=True)
        M = {o.name: [] for o in self.parts}
        for f in range(self.f0, self.f1 + 1):
            sc.frame_set(f)
            for o in self.parts: M[o.name].append(o.matrix_world.copy())
        for o in self.parts + self.passive:
            if o.name in self.rw.collection.objects: self.rw.collection.objects.unlink(o)
            if o.rigid_body:
                with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]): bpy.ops.rigidbody.object_remove()
        for o in self.parts:
            if o.animation_data: o.animation_data_clear()
            o.rotation_mode = "QUATERNION"; prev = None
            for i, m in enumerate(M[o.name]):
                loc, q, s_ = m.decompose()
                if prev is not None and q.dot(prev) < 0: q.negate()
                prev = q; o.location = loc; o.rotation_quaternion = q; o.scale = s_
                o.keyframe_insert("location", frame=self.f0 + i); o.keyframe_insert("rotation_quaternion", frame=self.f0 + i)
        for o in [o for o in self.col.objects if o.name.startswith("joint_")]: bpy.data.objects.remove(o, do_unlink=True)
        with bpy.context.temp_override(scene=sc): bpy.ops.rigidbody.world_remove()
        b = before if before is not None else self.f0; moved, far, track = 0, 0.0, {}
        for o in self.parts:
            sc.frame_set(b); p0 = _centre(o); sc.frame_set(self.f1); p1 = _centre(o); d = (p1 - p0).length   # world bbox centre (origins can sit anywhere)
            moved += d > .05; far = max(far, d)
            nm = o.name.split(":")[-1]
            if any(t in nm for t in track_names): track[nm] = {"before": [round(v, 2) for v in p0], "end": [round(v, 2) for v in p1], "moved_m": round(d, 2)}
        # PROJECTION measure: peak speed of each FREE piece (after its release; a piece kinematic for the whole event is authored motion,
        # not simulation). A pushed piece moves at the pusher's speed; a thrown or exploding one is fast (gate: < 15 m/s).
        fps = sc.render.fps / sc.render.fps_base; vmax, vwho = 0.0, None; rmax, rwho = 0.0, None
        for o in self.parts:
            r0 = self.release.get(o.name, self.f0)
            if r0 > self.f1: continue
            T = [m.translation for m in M[o.name]]; i0 = max(1, r0 - self.f0 + 1)
            for i in range(i0, len(T)):
                v = (T[i] - T[i - 1]).length * fps
                if v > vmax: vmax, vwho = v, o.name
                up = T[i].z - T[i0 - 1].z                                  # LAUNCH measure: height gained above the release height
                if up > rmax: rmax, rwho = up, o.name
        return {"pieces": len(self.parts), "joints": self.joints, "pieces_moved": moved, "max_moved_m": round(far, 2), "max_speed_ms": round(vmax, 2), "fastest": vwho, "max_rise_m": round(rmax, 2), "highest": rwho, "track": track}

def _shrink(o, k=.985):
    """pre-separation: each fragment shrunk 1.5 % about its own centre so neighbours never start interpenetrated (no pop at release)"""
    from mathutils import Matrix
    c = sum((v.co for v in o.data.vertices), Vector()) / max(1, len(o.data.vertices)); o.data.transform(Matrix.Translation(c) @ Matrix.Scale(k, 4) @ Matrix.Translation(-c))

def _scene_obj(name):
    o = bpy.data.objects.get(name)
    if o is None: raise KeyError("physics: object '%s' not in the scene" % name)
    return o

def crash(scene, spec, asset_col, ground, striker_empty, log=print):
    """tier 3: a striker (vehicle) drives into a prepared, fractured target; released at the computed contact frame"""
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1, substeps=spec.get("substeps", 40)); parts = realize(scene, asset_col, spec.get("name", "target"), spec["at"], math.radians(spec.get("rot", 0)), S.col)
    for pre, fr in (spec.get("fracture") or {}).items():
        for o in [o for o in parts if o.name.split(":")[-1].startswith(pre)]:
            parts.remove(o); parts += fracture(o, fr.get("pieces", 3), fr.get("seed", spec.get("seed", 1)), S.col)
    for o in parts: _shrink(o)
    S.collider(ground); px = S.striker(striker_empty, spec["striker"]["box"]); rel = spec.get("release") or S.contact_frame(px, parts)
    for o in parts: S.piece(o, rel, group=1 if any(k in o.name for k in spec.get("own_group", ["cart_wheel_"])) else 0)
    n = S.joints_between(parts, spec.get("joint_strength", 60), spec.get("weak", {})); log("[physics] crash: %d pieces, %d joints, release f%d" % (len(parts), n, rel))
    r = S.bake(spec.get("track", ("cart_wheel_L", "cart_wheel_R", "cart_axle", "plank_03_frag0")), before=rel - 1); r["release"] = rel; return r

def drop(scene, spec, src_fn, ground):
    """tier 2: an object falls from a height (optional initial tilt) and bounces/settles on the ground and on named colliders"""
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1); col = S.col
    parts = realize(scene, src_fn(spec["asset"]), spec.get("name", spec["asset"]), [spec["at"][0], spec["at"][1], spec["at"][2] + spec.get("height", 2.0)], math.radians(spec.get("rot", 0)), col) if "asset" in spec else [_scene_obj(spec["object"])]
    for o in parts:
        if spec.get("tilt"): o.rotation_euler.x += math.radians(spec["tilt"][0]); o.rotation_euler.y += math.radians(spec["tilt"][1])
    S.collider(ground)
    for c in spec.get("colliders", []): S.collider(_scene_obj(c), "CONVEX_HULL")
    rel = spec.get("release", f0 + 1)
    for o in parts: S.piece(o, rel, bounce=spec.get("bounce", .35))
    if len(parts) > 1: S.joints_between(parts, None)                     # an asset made of several meshes stays one body (unbreakable joints)
    return S.bake(tuple(o.name.split(":")[-1] for o in parts), before=rel - 1)

def topple(scene, spec, src_fn, ground):
    """tier 2: an upright object is tipped past its balance (keyed tilt before the release) and falls over"""
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1); col = S.col
    parts = realize(scene, src_fn(spec["asset"]), spec.get("name", spec["asset"]), spec["at"], math.radians(spec.get("rot", 0)), col) if "asset" in spec else [_scene_obj(spec["object"])]
    rel = spec["at_frame"]; ax = 0 if spec.get("axis", "X") == "X" else 1
    for o in parts:
        base = list(o.rotation_euler)
        for f, k in ((f0, 0.0), (rel - 6, 0.0), (rel, 1.0)):
            r = list(base); r[ax] += math.radians(spec.get("tilt", 14)) * k; o.rotation_euler = r; o.keyframe_insert("rotation_euler", frame=f)
    S.collider(ground)
    for o in parts: S.piece(o, rel)
    if len(parts) > 1: S.joints_between(parts, spec.get("joint_strength"))
    return S.bake(tuple(o.name.split(":")[-1] for o in parts), before=rel - 1)

def roll(scene, spec, src_fn, ground):
    """tier 2: an object (barrel, tyre) set rolling: its parts are JOINED into one body (separate interpenetrating parts launched the
    barrel 6.8 m up, farmyard 2026-11-18), it is LAID on its side (axis across the travel direction) and keyed rolling without slipping
    (angle = distance / radius) on the ground until release, then free"""
    from mathutils import Matrix, Quaternion
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1); col = S.col
    parts = realize(scene, src_fn(spec["asset"]), spec.get("name", spec["asset"]), spec["at"], 0.0, col) if "asset" in spec else [_scene_obj(spec["object"])]
    o = join(parts, "%s:%s" % (spec.get("name", "roll"), spec.get("asset", parts[0].name.split(":")[-1])))
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]): bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.context.view_layer.update(); dims = o.dimensions.copy(); r0 = max(spec.get("radius", 0), max(dims.x, dims.y) / 2)   # measured radius wins: a smaller authored radius sank the barrel 2.8 cm and Bullet threw it 1 m up
    lay = Matrix.Rotation(math.pi / 2, 4, "X") if spec.get("lay", True) else Matrix.Identity(4)     # cylinder axis Z -> across the travel
    rel = spec["release"]; d = Vector((*spec["direction"], 0)).normalized(); v = spec.get("speed", 2.0); h = math.atan2(d.y, d.x)
    x0, y0 = spec["at"][0], spec["at"][1]; o.rotation_mode = "QUATERNION"; prev = None
    for f in range(f0, rel + 1):
        s_ = max(0, f - spec.get("push_from", f0)) * v / scene.render.fps; px, py = x0 + d.x * s_, y0 + d.y * s_
        from rc import envbuild
        gz = envbuild.ground_z(ground, px, py) if ground else 0.0
        M = Matrix.Translation((px, py, gz + r0)) @ Matrix.Rotation(h, 4, "Z") @ Matrix.Rotation(s_ / r0, 4, "Y") @ lay
        loc, q, _ = M.decompose()
        if prev is not None and q.dot(prev) < 0: q.negate()
        prev = q; o.location = loc; o.rotation_quaternion = q; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_quaternion", frame=f)
    S.collider(ground)
    for c in spec.get("colliders", []): S.collider(_scene_obj(c), "CONVEX_HULL")
    S.piece(o, rel, shape=spec.get("shape", "CYLINDER"), bounce=.2)
    r = S.bake((o.name.split(":")[-1],), before=f0); r["radius_m"] = round(r0, 3); return r

def glass_pieces(ob, cuts, seed, col):
    """a pane cut into shards by seeded random plane cuts in its own plane (Voronoi-like), real cut faces"""
    pieces = [ob]; R = random.Random(seed)
    for c in range(cuts):
        nxt = []; bpy.context.view_layer.update()                      # new shards: matrix_world is stale until the depsgraph updates (shards were born at the origin)
        for p in pieces:
            lo, hi = _aabb(p); mid = Vector([R.uniform(lo[k] + (hi[k] - lo[k]) * .3, lo[k] + (hi[k] - lo[k]) * .7) for k in range(3)])
            a = R.uniform(0, math.pi); n = Vector((math.cos(a), 0, math.sin(a))) if (hi - lo).y < (hi - lo).x else Vector((0, math.cos(a), math.sin(a)))
            halves = []
            for side in (1, -1):
                bm = bmesh.new(); bm.from_mesh(p.data); bm.transform(p.matrix_world)
                r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=mid, plane_no=n, clear_inner=side > 0, clear_outer=side < 0)
                cut = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
                if cut: bmesh.ops.holes_fill(bm, edges=cut)
                if not bm.verts: bm.free(); continue
                me = bpy.data.meshes.new(p.name + "s"); bm.to_mesh(me); bm.free()
                for m in p.data.materials: me.materials.append(m)
                ctr = sum((v.co for v in me.vertices), Vector()) / len(me.vertices); me.transform(__import__("mathutils").Matrix.Translation(-ctr))
                q = bpy.data.objects.new(p.name + ("a" if side > 0 else "b"), me); col.objects.link(q); q.location = ctr; halves.append(q)
            bpy.data.objects.remove(p, do_unlink=True); nxt += halves
        pieces = nxt
    return pieces

def glass_shatter(scene, spec, src_fn, ground):
    """tier 3: a named glass pane is replaced by seeded shards held by weak joints; a striker (object/proxy) or a thrown object breaks it"""
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1, substeps=30); pane = _scene_obj(spec["pane"]); pane_copy = pane.copy(); pane_copy.data = pane.data.copy()
    S.col.objects.link(pane_copy); pane_copy.matrix_world = pane.matrix_world.copy(); pane.hide_render = True; pane.keyframe_insert("hide_render", frame=f0)
    shards = glass_pieces(pane_copy, spec.get("cuts", 4), spec["seed"], S.col)
    for o in shards: _shrink(o, .99)
    S.collider(ground)
    for c in spec.get("colliders", []): S.collider(_scene_obj(c), "CONVEX_HULL")
    if spec.get("striker"): px = S.striker(_scene_obj(spec["striker"]["name"]), spec["striker"]["box"]); rel = S.contact_frame(px, shards)
    else: rel = spec["at_frame"]
    for o in shards: S.piece(o, rel, density=2500, bounce=.2, friction=1.0, damping=.4)   # thin shards: high friction, they skid a little, not metres
    if not spec.get("impulse"): S.joints_between(shards, spec.get("strength", 4), tol=.01)   # a striker cracks it progressively
    if spec.get("impulse"):                                               # a thrown stone: glass is brittle, the pane breaks all at once on the hit                                               # a thrown stone: a small fast drop object aimed at the pane
        st = spec["impulse"]; bpy.ops.mesh.primitive_ico_sphere_add(radius=.05, location=st["from"]); stone = bpy.context.object; stone.name = "thrown_stone"
        for c in list(stone.users_collection): c.objects.unlink(stone)
        S.col.objects.link(stone); tgt = Vector(st["to"]) if isinstance(st["to"], list) else sum(((pane_copy.matrix_world @ Vector(c)) for c in pane_copy.bound_box), Vector()) / 8 if False else (Vector(st["to"]) if isinstance(st["to"], list) else _scene_obj(st["to"]).matrix_world @ (sum((Vector(c) for c in _scene_obj(st["to"]).bound_box), Vector()) / 8)); p0 = Vector(st["from"]); n = st.get("frames", 8)
        for k in range(n + 1): stone.location = p0.lerp(tgt, k / n); stone.keyframe_insert("location", frame=rel - n + k)
        v = (tgt - p0).normalized() * .03; p = tgt.copy(); dg = bpy.context.evaluated_depsgraph_get()   # after the hit: slowed, falls on keys (stays kinematic)
        Gi = ground.matrix_world.inverted(); hit, gp, *_ = ground.ray_cast(Gi @ (tgt + Vector((0, 0, 50))), Gi.to_3x3() @ Vector((0, 0, -1)))   # the ground only
        gz = ((ground.matrix_world @ gp).z if hit else tgt.z - 1.5) + .05; vz = 0.0
        for k in range(1, 40):
            vz -= 9.81 / 900; p = Vector((p.x + v.x, p.y + v.y, max(gz, p.z + vz))); v *= .3 if p.z <= gz else .95
            stone.location = p; stone.keyframe_insert("location", frame=rel + k)
        S.piece(stone, f1 + 1, density=2400)                                # kinematic for the whole simulation: it pushes the shards, nothing pushes it
    r = S.bake(("shed_glass",), before=rel - 1); r["release"] = rel; r["shards"] = len(shards); return r

def door_break(scene, spec, src_fn, ground):
    """tier 3: a hinged door held by HINGE joints (breakable) to an invisible frame; a striker tears it off"""
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1); door = _scene_obj(spec["door"]); frame = door.copy(); frame.data = door.data.copy(); S.col.objects.link(frame)
    frame.matrix_world = door.matrix_world.copy(); frame.hide_render = True; frame.display_type = "WIRE"; frame.scale = (.2, .2, 1.0)
    S.collider(ground); S.collider(frame, "BOX"); px = S.striker(_scene_obj(spec["striker"]["name"]), spec["striker"]["box"]); rel = S.contact_frame(px, [door])
    S.piece(door, rel)
    for z in (.3, 1.7): S.joint(door, frame, spec.get("hinge_strength", 30), "HINGE", door.matrix_world @ Vector((0, 0, z)), (0, 0, 0))
    r = S.bake((door.name.split(":")[-1],), before=rel - 1); r["release"] = rel; return r

def collapse(scene, spec, src_fn, ground):
    """tier 3: a stack/structure of placed assets joined by breakable joints; a support is pulled out (keyed) or a striker hits it"""
    f0, f1 = spec["frames"]; S = Sim(scene, f0, f1); parts = []
    for i, it in enumerate(spec["items"]):
        nm = "%s_%d" % (spec.get("name", "stack"), i); parts.append(join(realize(scene, src_fn(it["asset"]), nm, it["at"], math.radians(it.get("rot", 0)), S.col), nm + ":" + it["asset"]))
    for o in parts: _shrink(o, .995)
    S.collider(ground)
    if spec.get("striker"): px = S.striker(_scene_obj(spec["striker"]["name"]), spec["striker"]["box"]); rel = S.contact_frame(px, parts)
    else: rel = spec["at_frame"]
    for o in parts: S.piece(o, rel)
    S.joints_between(parts, spec.get("joint_strength", 25), tol=.04)
    r = S.bake((), before=rel - 1); r["release"] = rel; return r

def deform(scene, spec, src_fn, ground):
    """tier 3 DEFORMATION (not a move): a dent pressed into a named mesh via a prepared shape key (vertices near the impact point pushed
    along the impact direction with a smooth falloff), keyed 0 -> 1 over `ease` frames at the impact frame; the object itself stays put"""
    ob = _scene_obj(spec["object"]); me = ob.data
    if not me.shape_keys: ob.shape_key_add(name="Basis")
    k = ob.shape_key_add(name=spec.get("name", "dent"), from_mix=False); inv = ob.matrix_world.inverted(); P = inv @ Vector(spec["point"])
    d = (inv.to_3x3() @ Vector(spec["direction"])).normalized(); R0 = spec.get("radius", .5); depth = spec.get("depth", .12); n = 0
    for i, v in enumerate(me.vertices):
        r = (v.co - P).length
        if r < R0: w = (1 - r / R0) ** 2; k.data[i].co = v.co + d * depth * w; n += 1
    f = spec["at_frame"]; e = spec.get("ease", 3)
    k.value = 0; k.keyframe_insert("value", frame=f - 1); k.value = 1; k.keyframe_insert("value", frame=f + e)
    return {"deformed_vertices": n, "object": ob.name, "frame": f}

EVENTS = {"drop": drop, "topple": topple, "roll": roll, "glass_shatter": glass_shatter, "door_break": door_break, "collapse": collapse, "deform": deform}

def run(scene, spec, src_fn, ground):
    if spec["type"] == "crash": r = crash(scene, spec, src_fn(spec["target_asset"]), ground, _scene_obj(spec["striker"]["name"]))
    else: r = EVENTS[spec["type"]](scene, spec, src_fn, ground)
    r["type"] = spec["type"]
    if r.get("release") is None and (spec.get("release") or spec.get("at_frame")): r["release"] = spec.get("release") or spec.get("at_frame")   # fx "@name" refs need it
    return r
