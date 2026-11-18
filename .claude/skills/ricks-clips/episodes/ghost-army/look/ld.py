"""Ghost Army LookDev library (pipeline stage 9, prototype 2026-11-18). Runs inside Blender on top of templates/blender_look/from_lock.
Everything here only ADDS look: real PBR texture sets, real models in place of visible primitives, dressing, light, air.
Layout, camera and timing come from the lock and are never touched (from_lock refuses a changed plan).

Assets: Poly Haven only in the prototype (CC0, no account); every file fetched is listed in <OUT>/credits.json.
Mapping: box projection on object coordinates (the lock meshes have no reliable UVs), scale in metres per tile.
"""
import bpy, bmesh, os, json, math, random, re, urllib.request, time
from mathutils import Vector, Matrix

CACHE = os.environ.get("PH_CACHE", "/root/ph"); CREDITS = []
UA = {"User-Agent": "RicksClips-LookDev/1.0 (Blender asset fetch)"}   # Poly Haven refuses the default Python agent (403)
def _open(url, timeout=120): return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
def _get(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return dst
    os.makedirs(os.path.dirname(dst), exist_ok=True); tmp = dst + ".part"
    for k in range(4):
        try:
            with _open(url) as r, open(tmp, "wb") as f: f.write(r.read())
            os.replace(tmp, dst); return dst
        except Exception as e: print("download retry", url, e); time.sleep(2 + 3 * k)
    raise RuntimeError("download failed " + url)
def _files(aid): return json.load(_open("https://api.polyhaven.com/files/" + aid, timeout=60))
def tex(aid, res="2k"):
    """a Poly Haven texture set -> {diff, rough, nor, ao, disp} local paths (jpg/png)"""
    F = _files(aid); out = {}
    for key, names in (("diff", ("Diffuse", "diffuse")), ("rough", ("Rough", "rough")), ("nor", ("nor_gl",)), ("ao", ("AO", "ao")), ("disp", ("Displacement", "disp"))):
        for n in names:
            if n in F and res in F[n]:
                ent = F[n][res].get("jpg") or F[n][res].get("png"); out[key] = _get(ent["url"], os.path.join(CACHE, aid, os.path.basename(ent["url"]))); break
    CREDITS.append(dict(id=aid, kind="texture", res=res, license="CC0", source="https://polyhaven.com/a/" + aid)); return out
def hdri(aid, res="2k"):
    F = _files(aid); ent = F["hdri"][res]["hdr"]; CREDITS.append(dict(id=aid, kind="hdri", res=res, license="CC0", source="https://polyhaven.com/a/" + aid))
    return _get(ent["url"], os.path.join(CACHE, aid, os.path.basename(ent["url"])))
def model(aid, res="1k"):
    """a Poly Haven model -> local .gltf path (with its bin + textures next to it)"""
    F = _files(aid); g = F["gltf"][res]["gltf"]; d = os.path.join(CACHE, aid, res); main = _get(g["url"], os.path.join(d, os.path.basename(g["url"])))
    for rel, ent in (g.get("include") or {}).items(): _get(ent["url"], os.path.join(d, rel))
    CREDITS.append(dict(id=aid, kind="model", res=res, license="CC0", source="https://polyhaven.com/a/" + aid)); return main

# ---------------------------------------------------------------- materials
def pbr(name, aid, tile=1.0, res="2k", disp=0.0, tint=None, rough_mul=1.0, rough_add=0.0, bump=1.0, wet=0.0):
    """Principled PBR from a texture set. tile = metres per repeat. disp > 0 = real displacement (Cycles), else normal map only.
    wet: 0..1 darkens and makes it glossy (night road). tint: RGB multiplier."""
    T = tex(aid, res); m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, Lk = nt.nodes, nt.links
    P = N["Principled BSDF"]; tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / tile,) * 3
    Lk.new(tc.outputs["Object"], mp.inputs["Vector"])
    def img(path, colour):
        n = N.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(path, check_existing=True); n.projection = "BOX"; n.projection_blend = .25
        n.image.colorspace_settings.name = "sRGB" if colour else "Non-Color"; Lk.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    base = img(T["diff"], True).outputs["Color"]
    if "ao" in T:
        ao = img(T["ao"], False); mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = .6
        Lk.new(base, mx.inputs["A"]); Lk.new(ao.outputs["Color"], mx.inputs["B"]); base = mx.outputs["Result"]
    if tint or wet:
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
        t = list(tint or (1, 1, 1)); k = 1 - .45 * wet; mx.inputs["B"].default_value = (t[0] * k, t[1] * k, t[2] * k, 1); Lk.new(base, mx.inputs["A"]); base = mx.outputs["Result"]
    Lk.new(base, P.inputs["Base Color"])
    if "rough" in T:
        r = img(T["rough"], False); mth = N.new("ShaderNodeMath"); mth.operation = "MULTIPLY_ADD"; mth.inputs[1].default_value = rough_mul * (1 - .75 * wet); mth.inputs[2].default_value = rough_add
        Lk.new(r.outputs["Color"], mth.inputs[0]); Lk.new(mth.outputs[0], P.inputs["Roughness"])
    if "nor" in T:
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump; Lk.new(img(T["nor"], False).outputs["Color"], nm.inputs["Color"]); Lk.new(nm.outputs["Normal"], P.inputs["Normal"])
    if disp and "disp" in T:
        dn = N.new("ShaderNodeDisplacement"); dn.inputs["Scale"].default_value = disp; dn.inputs["Midlevel"].default_value = .5
        Lk.new(img(T["disp"], False).outputs["Color"], dn.inputs["Height"]); Lk.new(dn.outputs["Displacement"], N["Material Output"].inputs["Displacement"])
        try: m.displacement_method = "BOTH"
        except Exception: pass
    return m
def simple(name, col, rough=.6, metal=0.0, emit=None, emit_strength=0.0, transmission=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; P = m.node_tree.nodes["Principled BSDF"]
    P.inputs["Base Color"].default_value = (*col, 1); P.inputs["Roughness"].default_value = rough; P.inputs["Metallic"].default_value = metal
    if transmission: P.inputs["Transmission Weight"].default_value = transmission
    if emit: P.inputs["Emission Color"].default_value = (*emit, 1); P.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1: P.inputs["Alpha"].default_value = alpha
    return m
def foliage(name, col=(.12, .22, .06), var=.35):
    """leaves: colour variation by object position, a little subsurface/translucency so backlit leaves glow"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, Lk = nt.nodes, nt.links; P = N["Principled BSDF"]
    oi = N.new("ShaderNodeObjectInfo"); ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (col[0] * (1 - var), col[1] * (1 - var * .5), col[2] * (1 - var), 1)
    ramp.color_ramp.elements[1].color = (col[0] * (1 + var * 1.4), col[1] * (1 + var), col[2] * (1 + var * .4), 1); Lk.new(oi.outputs["Random"], ramp.inputs["Fac"]); Lk.new(ramp.outputs["Color"], P.inputs["Base Color"])
    P.inputs["Roughness"].default_value = .55
    try: P.inputs["Subsurface Weight"].default_value = .15; P.inputs["Transmission Weight"].default_value = .1
    except Exception: pass
    return m
def assign(pattern, mat, objs=None, hide=False):
    """give every mesh whose name matches `pattern` (regex on the name without .001 suffixes) the material; returns the count"""
    rx = re.compile(pattern); n = 0
    for o in (objs or bpy.data.objects):
        if o.type != "MESH" or not rx.search(o.name.split(".")[0]): continue
        if hide: o.hide_render = True; o.hide_viewport = True; n += 1; continue
        o.data.materials.clear(); o.data.materials.append(mat); n += 1
    return n
def objects(pattern):
    rx = re.compile(pattern); return [o for o in bpy.data.objects if o.type == "MESH" and rx.search(o.name.split(".")[0])]

# ---------------------------------------------------------------- models in place of primitives
_LOADED = {}
def load_model(aid, res="1k"):
    """import a Poly Haven model once into a hidden collection; returns (collection, bbox min, bbox max) in its own space"""
    if aid in _LOADED: return _LOADED[aid]
    path = model(aid, res); before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path); new = [o for o in bpy.data.objects if o not in before]
    col = bpy.data.collections.new("ast_" + aid); bpy.context.scene.collection.children.link(col)
    for o in new:
        for c in o.users_collection: c.objects.unlink(o)
        col.objects.link(o)
    pts = [o.matrix_world @ Vector(c) for o in new if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    col.hide_render = True; col.hide_viewport = True
    for o in new: o.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))   # pivot: bottom centre
    bpy.context.view_layer.update(); _LOADED[aid] = (col, hi - lo); return _LOADED[aid]
def instance(aid, loc, rot_z=0.0, scale=1.0, name=None):
    col, size = load_model(aid); e = bpy.data.objects.new(name or ("inst_" + aid), None); e.instance_type = "COLLECTION"; e.instance_collection = col
    bpy.context.scene.collection.objects.link(e); e.location = loc; e.rotation_euler = (0, 0, rot_z); e.scale = (scale,) * 3; return e
def replace(pattern, aid, fit="height", extra_rot=0.0, keep_original=False):
    """put the model where every matching primitive stands (bottom centre of its world bbox), scaled to its height (or
    footprint), turned like it; the primitive is hidden. Returns the number replaced."""
    col, size = load_model(aid); n = 0
    for o in objects(pattern):
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]; lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        dims = hi - lo; s = (dims.z / max(size.z, 1e-4)) if fit == "height" else (max(dims.x, dims.y) / max(size.x, size.y, 1e-4))
        rz = o.matrix_world.to_euler().z + extra_rot
        instance(aid, Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)), rz, s, "rep_" + o.name)
        if not keep_original: o.hide_render = True; o.hide_viewport = True
        n += 1
    return n

# ---------------------------------------------------------------- the lock's instanced foliage
def foliage_groups():
    """the glTF importer turns every three.js InstancedMesh into one object per instance, all named 'Mesh' (the field has ~50k).
    Group them by shared mesh data and sort each group by size and distance:
      grass  - small blade clumps (<= 1 m tall, few vertices)     flowers - tiny (< .12 m)
      hedge  - leaf clumps .4-3 m within 120 m                     copse   - big blobs or anything beyond 120 m
    Returns {kind: [objects]} for the foliage-material objects only."""
    by = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or not any(s.material and "foliage" in s.material.name.lower() for s in o.material_slots): continue
        by.setdefault(o.data.name, []).append(o)
    out = {"grass": [], "flowers": [], "hedge": [], "copse": []}
    for key, objs in by.items():
        o0 = objs[0]; nv = len(o0.data.vertices); dims = sorted(o.dimensions.z for o in objs)[len(objs) // 2]; dist = sorted(o.matrix_world.translation.length for o in objs)[len(objs) // 2]
        kind = "flowers" if dims < .12 else "grass" if (dims <= 1.0 and nv <= 80) else "copse" if (dist > 120 or dims > 3.0) else "hedge"
        out[kind] += objs
    return out
def replace_objs(objs, aid, fit="height", every=1):
    """replace a list of objects by instances of a model (bottom centre, scaled); every=k keeps one in k (the others hidden)"""
    col, size = load_model(aid); n = 0
    for i, o in enumerate(objs):
        o.hide_render = True; o.hide_viewport = True
        if i % every: continue
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]; lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        d = hi - lo; s = (d.z / max(size.z, 1e-4)) if fit == "height" else (max(d.x, d.y) / max(size.x, size.y, 1e-4))
        instance(aid, Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)), (i * 2.399) % 6.283, s, "rep_" + aid); n += 1
    return n

# ---------------------------------------------------------------- dressing
def scatter(aids, count, area, keep_clear, seed=1, scale=(.8, 1.3), ground_z=0.0, avoid=None, near=None, name="scatter"):
    """instances of the models in `aids` over area (x0, y0, x1, y1), never inside a keep-clear disc (camera path, characters)
    or an `avoid(x, y)` region; `near` = (x, y, r): denser near that point (the lens). Returns the count placed."""
    R = random.Random(seed); n = 0; tries = 0
    while n < count and tries < count * 20:
        tries += 1
        if near and R.random() < .6: a = R.uniform(0, 6.283); r = near[2] * math.sqrt(R.random()); x, y = near[0] + math.cos(a) * r, near[1] + math.sin(a) * r
        else: x, y = R.uniform(area[0], area[2]), R.uniform(area[1], area[3])
        if any(math.hypot(x - cx, y - cy) < cr for cx, cy, cr in keep_clear): continue
        if avoid and avoid(x, y): continue
        instance(R.choice(aids), Vector((x, y, ground_z)), R.uniform(0, 6.283), R.uniform(*scale), name); n += 1
    return n

# ---------------------------------------------------------------- light and air
def world_hdri(aid, strength=1.0, rot=0.0, visible=False, bg=(0.02, .03, .06)):
    """HDRI lighting; visible False = the camera sees `bg` (our own sky/backdrop stays), the HDRI only lights and reflects"""
    path = hdri(aid); w = bpy.context.scene.world or bpy.data.worlds.new("W"); bpy.context.scene.world = w; w.use_nodes = True; nt = w.node_tree; N, Lk = nt.nodes, nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputWorld"); env = N.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(path, check_existing=True)
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, rot); Lk.new(tc.outputs["Generated"], mp.inputs["Vector"]); Lk.new(mp.outputs["Vector"], env.inputs["Vector"])
    b1 = N.new("ShaderNodeBackground"); b1.inputs["Strength"].default_value = strength; Lk.new(env.outputs["Color"], b1.inputs["Color"])
    if visible: Lk.new(b1.outputs["Background"], out.inputs["Surface"]); return w
    b2 = N.new("ShaderNodeBackground"); b2.inputs["Color"].default_value = (*bg, 1); lp = N.new("ShaderNodeLightPath"); mx = N.new("ShaderNodeMixShader")
    Lk.new(lp.outputs["Is Camera Ray"], mx.inputs["Fac"]); Lk.new(b1.outputs["Background"], mx.inputs[1]); Lk.new(b2.outputs["Background"], mx.inputs[2]); Lk.new(mx.outputs["Shader"], out.inputs["Surface"]); return w
def sun(name, direction, energy, color=(1, .95, .88), angle=.02):
    d = bpy.data.lights.new(name, "SUN"); d.energy = energy; d.color = color; d.angle = angle; o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = Vector(direction).normalized().to_track_quat("Z", "Y").to_euler(); return o
def point(name, loc, watts, color=(1, .7, .4), radius=.08):
    d = bpy.data.lights.new(name, "POINT"); d.energy = watts; d.color = color; d.shadow_soft_size = radius; o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o); o.location = loc; return o
def area(name, loc, look_at, watts, size=1.0, color=(1, .95, .9)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = watts; d.size = size; d.color = color; o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(look_at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
def fog_box(center, size, density, color=(.8, .85, .95), anisotropy=.3, name="air"):
    """volumetric air: a box with Principled Volume (Cycles and EEVEE)"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center); o = bpy.context.active_object; o.name = name; o.scale = size
    m = bpy.data.materials.new(name); m.use_nodes = True; N, Lk = m.node_tree.nodes, m.node_tree.links; N.remove(N["Principled BSDF"]); v = N.new("ShaderNodeVolumePrincipled")
    v.inputs["Density"].default_value = density; v.inputs["Color"].default_value = (*color, 1); v.inputs["Anisotropy"].default_value = anisotropy; Lk.new(v.outputs["Volume"], N["Material Output"].inputs["Volume"])
    o.data.materials.append(m); o.visible_shadow = False; return o

# ---------------------------------------------------------------- render + proofs
def cycles(samples=128, res_pct=37.5):
    sc = bpy.context.scene; p = bpy.context.preferences.addons["cycles"].preferences; p.compute_device_type = "OPTIX"; p.get_devices()
    for d in p.devices: d.use = d.type in ("OPTIX",)
    sc.render.engine = "CYCLES"; sc.cycles.device = "GPU"; sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"
    sc.render.resolution_percentage = int(round(res_pct)) if res_pct >= 1 else 38; sc.render.resolution_x, sc.render.resolution_y = 1440, 2560
    sc.render.resolution_percentage = 100; sc.render.resolution_x, sc.render.resolution_y = int(1440 * res_pct / 100), int(2560 * res_pct / 100)
    sc.cycles.max_bounces = 8; sc.cycles.volume_bounces = 1; sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
def still(path, frame):
    sc = bpy.context.scene; sc.frame_set(frame); sc.render.filepath = path; t = time.time(); bpy.ops.render.render(write_still=True); return round(time.time() - t, 1)
def proofs(out, tag, frames, clay_only=False):
    """for each frame: the look, a clay pass (light + AO + shadows only) and a depth view; returns timings"""
    sc = bpy.context.scene; vl = sc.view_layers[0]; T = {}
    for f in frames:
        if not clay_only: T["look_%d" % f] = still(os.path.join(out, "%s_look_f%05d.png" % (tag, f)), f)
    clay = simple("clay", (.62, .62, .62), rough=.8); vl.material_override = clay
    for f in frames: T["clay_%d" % f] = still(os.path.join(out, "%s_clay_f%05d.png" % (tag, f)), f)
    d = bpy.data.materials.new("depth"); d.use_nodes = True; N, Lk = d.node_tree.nodes, d.node_tree.links; N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0; mr.inputs["From Max"].default_value = -60; em = N.new("ShaderNodeEmission")
    Lk.new(tc.outputs["Camera"], sep.inputs["Vector"]); Lk.new(sep.outputs["Z"], mr.inputs["Value"]); Lk.new(mr.outputs["Result"], em.inputs["Strength"]); Lk.new(em.outputs["Emission"], N["Material Output"].inputs["Surface"])
    vl.material_override = d; s0 = sc.cycles.samples; sc.cycles.samples = 16
    for f in frames[:1]: T["depth_%d" % f] = still(os.path.join(out, "%s_depth_f%05d.png" % (tag, f)), f)
    sc.cycles.samples = s0; vl.material_override = None; return T
def write_credits(out):
    json.dump(CREDITS, open(os.path.join(out, "credits.json"), "w"), indent=1)
