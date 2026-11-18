"""rc.vfx — H. VFX Engine (Mission 2, 2026-11-18). Runs inside Blender. Effects live IN the 3D scene (lit, occluded, shadowed), are
seeded and baked, and are triggered at a frame by place.json "fx":
  dust_burst  {at, frame, count, radius, height, color, seed}  a ring of soft dust puffs that rise, spread and fade (impact, set-down);
              each puff is a small volume sphere whose scale/density are keyed per frame from a pure function of the frame
Volumes render in Cycles and EEVEE; the puff count stays small (tens), so it is cheap."""
import math, random
import bpy
from mathutils import Vector

def _dust_mat(color, name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); v = N.new("ShaderNodeVolumePrincipled"); v.inputs["Color"].default_value = (*color, 1)
    tc = N.new("ShaderNodeTexCoord"); gr = N.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"; L.new(tc.outputs["Object"], gr.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    a = N.new("ShaderNodeMath"); a.operation = "MULTIPLY"; L.new(gr.outputs["Fac"], a.inputs[0]); L.new(nz.outputs["Fac"], a.inputs[1])
    d = N.new("ShaderNodeMath"); d.operation = "MULTIPLY"; d.name = "density"; d.inputs[1].default_value = 2.5; L.new(a.outputs[0], d.inputs[0])
    L.new(d.outputs[0], v.inputs["Density"]); L.new(v.outputs[0], out.inputs["Volume"]); return m

def dust_burst(scene, name, at, frame, count=14, radius=1.2, height=.9, color=(.62, .55, .44), seed=1, life=45):
    R = random.Random(seed); col = bpy.data.collections.get("RC_FX") or bpy.data.collections.new("RC_FX")
    if col.name not in scene.collection.children: scene.collection.children.link(col)
    for i in range(count):
        a = 2 * math.pi * i / count + R.uniform(-.2, .2); sp = R.uniform(.6, 1.2); m = _dust_mat(color, "%s_dust_%02d" % (name, i))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0); o = bpy.context.object; o.name = "%s_puff_%02d" % (name, i)
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o); o.data.materials.append(m); o.visible_shadow = False; dn = m.node_tree.nodes["density"].inputs[1]
        for f in range(frame - 1, frame + life + 1):
            k = max(0.0, (f - frame) / life); r = radius * sp * (1 - (1 - k) ** 2); s = .05 + .55 * sp * k ** .6
            o.location = (at[0] + math.cos(a) * r, at[1] + math.sin(a) * r, at[2] + .1 + height * k ** .8 * sp)
            o.scale = (s, s, s * .8); o.keyframe_insert("location", frame=f); o.keyframe_insert("scale", frame=f)
            o.hide_render = f < frame or f >= frame + life; o.keyframe_insert("hide_render", frame=f)
            dn.default_value = 2.5 * (1 - k) ** 1.5 if f >= frame else 0; dn.keyframe_insert("default_value", frame=f)
    return count

def _fxcol(scene):
    col = bpy.data.collections.get("RC_FX") or bpy.data.collections.new("RC_FX")
    if col.name not in scene.collection.children: scene.collection.children.link(col)
    return col

def _vol_mat(name, color, density=2.5, emission=0.0, emit_color=None, noise_scale=3.0):
    m = _dust_mat(color, name); nt = m.node_tree; v = [n for n in nt.nodes if n.type == "PRINCIPLED_VOLUME"][0]
    if emission:                                                     # emission follows the density FIELD (bright core, fading edge); a constant
        v.inputs["Emission Color"].default_value = (*(emit_color or color), 1)   # strength lit the whole sphere like a ball (seen on the farmyard sheet)
        fld = nt.nodes["density"].inputs[0].links[0].from_socket; pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.0
        em = nt.nodes.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = emission
        nt.links.new(fld, pw.inputs[0]); nt.links.new(pw.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], v.inputs["Emission Strength"])
    nt.nodes["density"].inputs[1].default_value = density
    for n in nt.nodes:
        if n.type == "TEX_NOISE": n.inputs["Scale"].default_value = noise_scale
    return m

def _puffs(scene, name, at, frame, count, seed, life, color, rise, spread, size, density, emission=0.0, emit_color=None, drift=(0, 0)):
    """generic billowing volume puffs (smoke, fire, fireball): each puff = volume sphere keyed per frame (pure function of the frame)"""
    R = random.Random(seed); col = _fxcol(scene); n = 0
    for i in range(count):
        t0 = frame + R.uniform(0, life * .6); a = R.uniform(0, 2 * math.pi); sp = R.uniform(.5, 1.0); m = _vol_mat("%s_m%02d" % (name, i), color, density, emission, emit_color)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0); o = bpy.context.object; o.name = "%s_%02d" % (name, i)
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o); o.data.materials.append(m); o.visible_shadow = emission == 0; dn = m.node_tree.nodes["density"].inputs[1]; L = life * R.uniform(.7, 1.0)
        for f in range(int(frame) - 1, int(t0 + L) + 2):
            k = max(0.0, (f - t0) / L); r = spread * sp * k ** .7; s_ = size * (.3 + 1.2 * k ** .5) * sp
            o.location = (at[0] + math.cos(a) * r + drift[0] * k, at[1] + math.sin(a) * r + drift[1] * k, at[2] + rise * k * sp); o.scale = (s_, s_, s_)
            o.keyframe_insert("location", frame=f); o.keyframe_insert("scale", frame=f); o.hide_render = f < t0 or k >= 1; o.keyframe_insert("hide_render", frame=f)
            dn.default_value = density * (1 - min(k, 1.0)) ** 1.3 if f >= t0 else 0; dn.keyframe_insert("default_value", frame=f)
        n += 1
    return n

def smoke(scene, spec):
    if spec.get("frames"):                                       # continuous smoke (chimney, fire): a new burst every `every` frames
        return sum(smoke(scene, dict(spec, frames=None, frame=f, name="%s_%03d" % (spec.get("name", "smoke"), i), seed=spec.get("seed", 1) * 100 + i, count=spec.get("per_burst", 3)))
                   for i, f in enumerate(range(spec["frames"][0], spec["frames"][1], spec.get("every", 15))))
    return _puffs(scene, spec.get("name", "smoke"), spec["at"], spec["frame"], spec.get("count", 14), spec.get("seed", 1), spec.get("life", 90), tuple(spec.get("color", (.32, .31, .3))), spec.get("rise", 3.5), spec.get("spread", .8), spec.get("size", .6), spec.get("density", 1.6), drift=tuple(spec.get("drift", (1.2, 0))))

def _flame_mat(name, strength=4.0):
    """cartoon flame: emission whose colour runs from a yellow-white core (facing the camera) to an orange-red rim (fresnel)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = .45; cr = N.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (1.0, .72, .12, 1); cr.color_ramp.elements[1].color = (.95, .12, .0, 1); cr.color_ramp.elements[1].position = .6
    L.new(lw.outputs["Facing"], cr.inputs[0]); L.new(cr.outputs[0], em.inputs["Color"]); L.new(em.outputs[0], out.inputs["Surface"]); return m

def _flame_mesh(name):
    """a teardrop tongue of flame, 1 m tall, origin at its base"""
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=.5)
    for v in bm.verts:
        h = v.co.z + .5; v.co.z = h                                  # 0..1 from the base
        k = (1 - h) ** .8 * (1.3 if h < .35 else 1.0); v.co.x *= k * .9; v.co.y *= k * .9
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = True
    return me

def fire(scene, spec):
    """CARTOON FIRE (reworked 2026-11-18: volume puffs read as pale blobs on the farmyard sheet): a few emissive teardrop tongues whose
    height, width and lean flicker every frame from seeded sines (frame-only, deterministic), small rising embers, and a flickering
    point light (rc.animate.flicker)"""
    from rc import animate
    R = random.Random(spec.get("seed", 1)); f0, f1 = spec["frames"]; at = spec["at"]; size = spec.get("size", .32); col = _fxcol(scene); n = 0
    mat = _flame_mat(spec.get("name", "fire") + "_flame_m", spec.get("emission", 1.6))
    for i in range(spec.get("tongues", 5)):
        o = bpy.data.objects.new("%s_tongue_%d" % (spec.get("name", "fire"), i), _flame_mesh("flame_%d" % i)); col.objects.link(o); o.data.materials.append(mat)
        o.visible_shadow = False; a = 2 * math.pi * i / 5 + R.uniform(-.3, .3); r = R.uniform(.05, .16) if i else 0.0
        o.location = (at[0] + math.cos(a) * r, at[1] + math.sin(a) * r, at[2]); h0 = size * (1.25 if i == 0 else R.uniform(.55, .9)); w0 = h0 * R.uniform(.45, .6)
        ph, rate = R.uniform(0, 6.28), R.uniform(9, 14)
        for f in range(f0, f1 + 1):
            t = f / scene.render.fps; fl = .22 * math.sin(t * rate + ph) + .12 * math.sin(t * rate * 2.7 + ph * 1.7)
            o.scale = (w0 * (1 - .4 * fl), w0 * (1 - .4 * fl), h0 * (1 + fl)); o.rotation_euler = (.18 * math.sin(t * 5.3 + ph), .18 * math.cos(t * 4.1 + ph), 0)
            o.keyframe_insert("scale", frame=f); o.keyframe_insert("rotation_euler", frame=f)
        n += 1
    for k, f in enumerate(range(f0, f1, spec.get("every", 6))):           # embers: tiny bright puffs rising and dying
        n += _puffs(scene, "%s_ember_%03d" % (spec.get("name", "fire"), k), [at[0], at[1], at[2] + size * .6], f, 1, spec.get("seed", 1) * 1000 + k, 14, (.3, .1, .02), spec.get("rise", 1.2), .15, .035, 2.0, emission=30.0, emit_color=(1.0, .5, .1))
    L = bpy.data.lights.new(spec.get("name", "fire") + "_light", "POINT"); L.energy = spec.get("light", 120); L.color = (1.0, .55, .2); L.shadow_soft_size = .3
    o = bpy.data.objects.new(L.name, L); col.objects.link(o); o.location = (at[0], at[1], at[2] + .4)
    animate.flicker(o, f0, f1, L.energy, .5, spec.get("seed", 1), 11.0, scene.render.fps); return n + 1

def sparks(scene, spec):
    """ballistic sparks: small elongated emissive pieces thrown from a point, gravity, short life (motion-blur friendly), seeded"""
    R = random.Random(spec.get("seed", 1)); col = _fxcol(scene); f = spec["frame"]; g = 9.81 / scene.render.fps ** 2; n = spec.get("count", 40)
    m = bpy.data.materials.new(spec.get("name", "sparks") + "_m"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (1.0, .7, .25, 1); em.inputs[1].default_value = spec.get("emission", 40.0); nt.links.new(em.outputs[0], out.inputs[0])
    for i in range(n):
        a, el, v = R.uniform(0, 2 * math.pi), R.uniform(.2, 1.2), R.uniform(2.0, 6.0) / scene.render.fps; vel = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el))) * v
        bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=.006, depth=.08); o = bpy.context.object; o.name = "%s_%02d" % (spec.get("name", "sparks"), i)
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o); o.data.materials.append(m); o.visible_shadow = False; life = int(R.uniform(10, 24)); p = Vector(spec["at"]); u = vel.copy()
        for k in range(-1, life + 2):
            if k >= 0: p = p + u; u.z -= g
            o.location = p; o.rotation_euler = Vector((0, 0, 1)).rotation_difference(u.normalized() if u.length else Vector((0, 0, 1))).to_euler()
            o.hide_render = k < 0 or k >= life; o.keyframe_insert("location", frame=f + k); o.keyframe_insert("rotation_euler", frame=f + k); o.keyframe_insert("hide_render", frame=f + k)
    return n

def rain(scene, spec):
    """rain over an area: one geometry-nodes object, streaks falling with scene time (z = top - (z0 + v t) mod height): frame-only"""
    col = _fxcol(scene); cx, cy, w, d = spec.get("area", [0, 0, 30, 30]); H = spec.get("height", 12.0); n = spec.get("count", 4000); R = random.Random(spec.get("seed", 1))
    me = bpy.data.meshes.new("rain_pts"); me.from_pydata([(cx + R.uniform(-w / 2, w / 2), cy + R.uniform(-d / 2, d / 2), R.uniform(0, H)) for _ in range(n)], [], []); ob = bpy.data.objects.new(spec.get("name", "rain"), me); col.objects.link(ob)
    nt = bpy.data.node_groups.new("rain", "GeometryNodeTree"); nt.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"); nt.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = nt.nodes, nt.links; gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput"); st = N.new("GeometryNodeInputSceneTime"); pos = N.new("GeometryNodeInputPosition"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(pos.outputs[0], sep.inputs[0])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = spec.get("speed", 9.0); L.new(st.outputs["Seconds"], mul.inputs[0])
    add = N.new("ShaderNodeMath"); add.operation = "ADD"; L.new(sep.outputs[2], add.inputs[0]); L.new(mul.outputs[0], add.inputs[1])
    md = N.new("ShaderNodeMath"); md.operation = "FLOORED_MODULO"; md.inputs[1].default_value = H; L.new(add.outputs[0], md.inputs[0])
    z = N.new("ShaderNodeMath"); z.operation = "SUBTRACT"; z.inputs[0].default_value = H; L.new(md.outputs[0], z.inputs[1])
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(sep.outputs[0], cmb.inputs[0]); L.new(sep.outputs[1], cmb.inputs[1]); L.new(z.outputs[0], cmb.inputs[2])
    sp = N.new("GeometryNodeSetPosition"); L.new(gi.outputs[0], sp.inputs["Geometry"]); L.new(cmb.outputs[0], sp.inputs["Position"])
    line = N.new("GeometryNodeCurvePrimitiveLine"); line.inputs["End"].default_value = (0, 0, .35); tm = N.new("GeometryNodeCurveToMesh"); prof = N.new("GeometryNodeCurvePrimitiveCircle"); prof.inputs["Radius"].default_value = .004; prof.inputs["Resolution"].default_value = 3
    L.new(line.outputs[0], tm.inputs["Curve"]); L.new(prof.outputs[0], tm.inputs["Profile Curve"]); iop = N.new("GeometryNodeInstanceOnPoints"); L.new(sp.outputs[0], iop.inputs["Points"]); L.new(tm.outputs[0], iop.inputs["Instance"])
    sm = N.new("GeometryNodeSetMaterial"); m = bpy.data.materials.new("rain_m"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (.75, .8, .9, 1)
    b.inputs["Alpha"].default_value = .35; b.inputs["Roughness"].default_value = .1; sm.inputs["Material"].default_value = m; L.new(iop.outputs[0], sm.inputs["Geometry"]); L.new(sm.outputs[0], go.inputs[0])
    ob.modifiers.new("rain", "NODES").node_group = nt; return n

def haze(scene, spec):
    """atmospheric depth: one large low-density volume box (Principled Volume), colour from the palette"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=spec.get("center", (0, 0, 10))); o = bpy.context.object; o.name = spec.get("name", "haze"); o.scale = spec.get("size", (200, 200, 20))
    for c in list(o.users_collection): c.objects.unlink(o)
    _fxcol(scene).objects.link(o); m = bpy.data.materials.new("haze_m"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); out = nt.nodes.new("ShaderNodeOutputMaterial"); v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (*spec.get("color", (.75, .8, .9)), 1); v.inputs["Density"].default_value = spec.get("density", .004); nt.links.new(v.outputs[0], out.inputs["Volume"]); o.data.materials.append(m); o.visible_shadow = False; return 1

def explosion_stylized(scene, spec):
    """layered stylised blast (fictional visual, no weapon parameters): flash light, fireball puffs, sparks, then rolling smoke and a
    ground shock ring, all on the same trigger frame"""
    f = spec["frame"]; at = spec["at"]; sd = spec.get("seed", 1); n = 0
    L = bpy.data.lights.new("blast_flash", "POINT"); L.color = (1.0, .75, .4); o = bpy.data.objects.new("blast_flash", L); _fxcol(scene).objects.link(o); o.location = (at[0], at[1], at[2] + 1)
    for g, e in ((f - 1, 0), (f, 6000), (f + 3, 2500), (f + 10, 400), (f + 20, 0)): L.energy = e; L.keyframe_insert("energy", frame=g)
    n += _puffs(scene, "blast_fireball", at, f, 10, sd, 22, (.35, .14, .04), 2.2, 1.2, .9, .4, emission=2.5, emit_color=(1.0, .32, .05))
    n += sparks(scene, {"name": "blast_sparks", "at": [at[0], at[1], at[2] + .5], "frame": f, "count": 50, "seed": sd + 1})
    n += _puffs(scene, "blast_smoke", at, f + 6, 16, sd + 2, 120, (.22, .21, .2), 6.0, 2.5, 1.4, 1.8, drift=(2.0, 0))
    bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=.08, location=(at[0], at[1], at[2] + .05)); ring = bpy.context.object; ring.name = "blast_ring"
    for c in list(ring.users_collection): c.objects.unlink(ring)
    _fxcol(scene).objects.link(ring); ring.data.materials.append(_vol_mat("blast_ring_m", (.6, .55, .45), 2.0))
    for g in range(f - 1, f + 26):
        k = max(0, g - f) / 25; ring.scale = (.2 + 6 * k, .2 + 6 * k, 1); ring.hide_render = g < f or k >= 1; ring.keyframe_insert("scale", frame=g); ring.keyframe_insert("hide_render", frame=g)
    return n + 2

def splash(scene, spec): return sparks(scene, dict(spec, count=spec.get("count", 30), emission=0.0)) if False else _puffs(scene, spec.get("name", "splash"), spec["at"], spec["frame"], spec.get("count", 10), spec.get("seed", 1), 20, (.8, .85, .9), .6, .8, .2, 1.0)

EFFECTS = {"dust_burst": lambda sc, s: dust_burst(sc, s.get("name", "dust"), s["at"], s["frame"], s.get("count", 14), s.get("radius", 1.2), s.get("height", .9), tuple(s.get("color", (.62, .55, .44))), s.get("seed", 1), s.get("life", 45)),
           "smoke": smoke, "fire": fire, "sparks": sparks, "rain": rain, "haze": haze, "explosion_stylized": explosion_stylized, "splash": splash}

def apply(scene, specs, ground=None):
    """returns {effect name: objects made}; every effect is seeded and keyed (no simulation state)"""
    from rc import envbuild
    out = {}
    for s in specs:
        if ground is not None and "at" in s and s.get("on_ground", True): s = dict(s, at=[s["at"][0], s["at"][1], s["at"][2] + envbuild.ground_z(ground, s["at"][0], s["at"][1])])
        out[s.get("name", s["type"])] = EFFECTS[s["type"]](scene, s)
    return out
