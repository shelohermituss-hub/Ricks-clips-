"""LOOK KIT (CB's corrections of 2026-11-19 turned into code; docs/CORRECTIONS_CB_FR.md): what every new daylight exterior gets by default,
with or without a reference video, so the first version is already cinematic and real.
  sky_hdri(scene)            a real cloudy sky photo seen by the camera and lighting the scene, rotated so its sun sits where the sun lamp is
  sun(scene, el, az)         hard sun (angle 2 deg); place it as in the reference (crash_instinct: back-left, 30 deg) -> long hero shadows
  bounce_fill(col)           camera-side soft area light, invisible: nothing black in daylight
  light_shafts(col, parent)  thin sun shafts under a tree / through an opening, attached to it, falling toward the ground
  god_rays(col)              a very light haze volume (0.0015) for the shafts; never one that washes the picture out
  tex(name, ph_id, ...)      scanned CC0 PBR (Poly Haven) with rotation and strong relief: roads, furrowed fields, rough wood, bark
  road_wear(material)        darker patchy wheel paths in each lane + sealed cracks (tar snakes) on top of a scanned asphalt
  pbr(...), srgb(), col(), mesh_obj(), box(), mat()   the small helpers they need (same as demos/crashed_car/sets/street.py)
The SUN list holds the current sun (azimuth, elevation); sun() updates it, sky_hdri()/light_shafts() read it.
Measure the grade with tools/grade_match.py; check every built shot with demos/crashed_car/shots/continuity.py."""
import bpy, bmesh, math
from mathutils import Vector

HDRI = "kloofendal_48d_partly_cloudy_puresky"; HDRI_SUN_DEG = -34.2          # its sun: atan2(y, x) of the brightest pixel (measured), elevation 47.8
SUN = [-32.0, 30.0]                                                             # azimuth (deg, direction the light comes FROM, 0 = +Y, -90 = -X), elevation

def srgb(h): return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))

def col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def mesh_obj(name, bm, material, c, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if material: me.materials.append(material)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); c.objects.link(o); return o

def mat(name, hexcol, rough=.6, metal=0.0):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal; return m

def box(name, c, size, loc, material, bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = mesh_obj(name, bm, material, c); o.location = loc; return o

def pbr(name, ph_id, tile=2.0, tint=None, tint_k=0.0, rough_mul=1.0, normal=1.0, value=1.0):
    """a CC0 Poly Haven PBR set (colour, roughness, normal from rc.fetch's cache) tiled every `tile` metres in object space"""
    if name in bpy.data.materials: return bpy.data.materials[name]
    from rc import fetch
    M = fetch.polyhaven_maps(ph_id, "1k", log=lambda *a: None)
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); L.new(tc.outputs["Object"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (1 / tile,) * 3
    def img(key, nc):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(M[key], check_existing=True)
        if nc: t.image.colorspace_settings.name = "Non-Color"
        t.projection = "BOX"; t.projection_blend = .2; L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    src = img("color", False).outputs["Color"]
    if tint and tint_k > 0:
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = tint_k; L.new(src, mx.inputs[6]); mx.inputs[7].default_value = (*srgb(tint), 1); src = mx.outputs[2]
    if value != 1.0:
        hv = N.new("ShaderNodeHueSaturation"); hv.inputs["Value"].default_value = value; L.new(src, hv.inputs["Color"]); src = hv.outputs["Color"]
    L.new(src, b.inputs["Base Color"])
    if "roughness" in M:
        r = img("roughness", True); rm = N.new("ShaderNodeMath"); rm.operation = "MULTIPLY"; rm.inputs[1].default_value = rough_mul; rm.use_clamp = True
        L.new(r.outputs["Color"], rm.inputs[0]); L.new(rm.outputs[0], b.inputs["Roughness"])
    if "normal" in M:
        n = img("normal", True); nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = normal; L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m

def sky_hdri(scene, strength=1.0, hdri=HDRI, hdri_sun_deg=HDRI_SUN_DEG, sun_az=None):
    """CINEMATIC SKY (CB 2026-11-19): a real cloudy sky photo (Poly Haven CC0) seen by the camera AND lighting the scene (soft fill, so the
    trunk is never black in daylight); rotated so its sun sits where the sun lamp is"""
    from rc import fetch
    w = bpy.data.worlds.new("sky_hdri"); scene.world = w; w.use_nodes = True; nt = w.node_tree; N, L = nt.nodes, nt.links; bg = N["Background"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); env = N.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(fetch.polyhaven_hdri(hdri, "1k", log=lambda *a: None), check_existing=True)
    az = SUN[0] if sun_az is None else sun_az
    want = math.degrees(math.atan2(math.cos(math.radians(az)), math.sin(math.radians(az))))     # direction the light comes from, as atan2(y, x)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(hdri_sun_deg - want))
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], env.inputs["Vector"]); L.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength

def god_rays(c, center=(0, 0, 0), size=(34, 34, 16), density=.0015, anisotropy=.75):
    """SUN RAYS (CB 2026-11-19): a light haze volume around the tree; the sun lamp shining through the crown draws the shafts"""
    m = bpy.data.materials.get("god_ray_haze") or bpy.data.materials.new("god_ray_haze"); m.use_nodes = True; nt = m.node_tree
    for n_ in list(nt.nodes):
        if n_.type != "OUTPUT_MATERIAL": nt.nodes.remove(n_)
    v = nt.nodes.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = density; v.inputs["Anisotropy"].default_value = anisotropy
    v.inputs["Color"].default_value = (1, .97, .9, 1); nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    o = box("god_rays", c, size, (center[0], center[1], size[2] / 2 - .05), m, bevel=0); o.visible_shadow = False
    return o

def light_shafts(c, n=10, seed=3, under=(0, 0, 4.4), spread=2.0, length=None, strength=.14, parent=None):
    """SUN RAYS you can SEE (CB 2026-11-19): soft tapered shafts falling from gaps under the crown along the sun direction, additive light
    (transparent + emission, fading along the shaft and at its edges); the reference shows them under the tree in daylight"""
    import random as _r
    R = _r.Random(seed); el, az = math.radians(SUN[1]), math.radians(SUN[0])
    d = -Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))      # the way the light travels
    m = bpy.data.materials.get("light_shaft")
    if not m:
        m = bpy.data.materials.new("light_shaft"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
        for n_ in list(N):
            if n_.type != "OUTPUT_MATERIAL": N.remove(n_)
        tc = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sx.inputs[0])
        along = N.new("ShaderNodeMath"); along.operation = "SUBTRACT"; along.inputs[0].default_value = 1.0; L.new(sx.outputs["Y"], along.inputs[1])
        edge = N.new("ShaderNodeMath"); edge.operation = "SINE"; m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.inputs[1].default_value = math.pi
        L.new(sx.outputs["X"], m2.inputs[0]); L.new(m2.outputs[0], edge.inputs[0])
        k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; L.new(along.outputs[0], k.inputs[0]); L.new(edge.outputs[0], k.inputs[1])
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1, .95, .82, 1)
        st = N.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength; L.new(k.outputs[0], st.inputs[0]); L.new(st.outputs[0], em.inputs["Strength"])
        tr = N.new("ShaderNodeBsdfTransparent"); add = N.new("ShaderNodeAddShader"); L.new(tr.outputs[0], add.inputs[0]); L.new(em.outputs[0], add.inputs[1])
        L.new(add.outputs[0], N["Material Output"].inputs["Surface"])
    side = d.cross(Vector((0, 0, 1))).normalized(); out = []
    for i in range(n):
        p0 = Vector(under) + Vector((R.uniform(-spread, spread), R.uniform(-spread, spread), R.uniform(-.4, .6))); w0, w1 = R.uniform(.06, .16), R.uniform(.18, .38)
        L_ = length or (p0.z / max(.2, -d.z)) * R.uniform(.55, .85)                         # from under the crown down toward the ground, never across the sky
        p1 = p0 + d * L_
        bm = bmesh.new(); uv = bm.loops.layers.uv.new()
        vs = [bm.verts.new(v) for v in (p0 - side * w0, p0 + side * w0, p1 + side * w1, p1 - side * w1)]; f = bm.faces.new(vs)
        for lp, (u_, v_) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uv].uv = (u_, v_)
        o = mesh_obj("light_shaft%d" % i, bm, m, c); o.visible_shadow = False; o.visible_glossy = False; out.append(o)
        if parent: o.parent = parent                                                        # they belong to the tree (fall with it)
    return out

def bounce_fill(c, at=(-3.0, -9.0, 2.2), aim=(0, 0, 2.0), energy=900.0, size=7.0):
    """CINEMATIC FILL (CB 2026-11-19: "le tronc est tout sombre en plein jour"): a big soft area light on the camera side, like a bounce board;
    invisible to the camera and in reflections, it opens the shadow side of the trunk and the characters under the crown"""
    l = bpy.data.lights.new("bounce_fill", "AREA"); l.energy = energy; l.size = size; l.color = srgb("#fff6ea")
    o = bpy.data.objects.new("bounce_fill", l); col("LIGHT").objects.link(o); o.location = at
    o.rotation_euler = (Vector(aim) - Vector(at)).to_track_quat("-Z", "Y").to_euler()
    o.visible_camera = False; o.visible_glossy = False
    return o

def sun(scene, elevation=None, azimuth=None, energy=4.2, angle=2.0):
    elevation = SUN[1] if elevation is None else elevation; azimuth = SUN[0] if azimuth is None else azimuth; SUN[0], SUN[1] = azimuth, elevation
    s = bpy.data.lights.new("sun", "SUN"); s.energy = energy; s.angle = math.radians(angle); s.color = srgb("#fff3e2")
    o = bpy.data.objects.new("sun", s); col("LIGHT").objects.link(o)
    el, az = math.radians(elevation), math.radians(azimuth)                       # azimuth: direction the light COMES FROM, 0 = +Y, -90 = -X
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    o.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); return o

def tex(name, ph_id, tile=2.0, tint=None, tint_k=0.0, value=1.0, rot=0.0, normal=1.0, rough_mul=1.0):
    """a CC0 Poly Haven PBR set like street.pbr, plus a rotation of the pattern (furrows along the road) and a stronger normal (relief)"""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = pbr(name, ph_id, tile=tile, tint=tint, tint_k=tint_k, value=value, normal=normal, rough_mul=rough_mul)
    mp = [n_ for n_ in m.node_tree.nodes if n_.type == "MAPPING"][0]; mp.inputs["Rotation"].default_value = (0, 0, math.radians(rot))
    return m

def road_wear(m):
    """REAL ROAD (CB 2026-11-19: "la route est trop plate ... usure et marques de pneus"): on top of the scanned asphalt, darker polished
    WHEEL PATHS in each lane (two per lane, patchy along the road), and black sealed cracks ("tar snakes") in a Voronoi edge pattern"""
    nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]; src = b.inputs["Base Color"].links[0].from_socket
    tc = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sx.inputs[0])
    def op(o, a, b_=None, v=None):
        n_ = N.new("ShaderNodeMath"); n_.operation = o
        L.new(a, n_.inputs[0]) if not isinstance(a, (int, float)) else n_.inputs.__getitem__(0).__setattr__("default_value", a)
        if b_ is not None:
            L.new(b_, n_.inputs[1]) if not isinstance(b_, (int, float)) else setattr(n_.inputs[1], "default_value", b_)
        return n_.outputs[0]
    ph = op("MULTIPLY", op("SUBTRACT", sx.outputs["X"], 3.3), 2 * math.pi / 1.9)              # wheel paths at x = 3.3, 5.2, 7.1, 9.0
    paths = op("POWER", op("MAXIMUM", op("COSINE", ph), 0.0), 6.0)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .08; nz.inputs["Detail"].default_value = 3; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    patchy = op("MULTIPLY", paths, op("MULTIPLY", nz.outputs["Fac"], 1.6))
    vo = N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = .22; L.new(tc.outputs["Object"], vo.inputs["Vector"])
    nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = .05; L.new(tc.outputs["Object"], nz2.inputs["Vector"])
    cracks = op("MULTIPLY", op("LESS_THAN", vo.outputs["Distance"], .007), op("GREATER_THAN", nz2.outputs["Fac"], .58))
    dark = op("MINIMUM", op("ADD", op("MULTIPLY", patchy, .32), op("MULTIPLY", cracks, .75)), .8)
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; L.new(dark, mx.inputs[0]); L.new(src, mx.inputs[6]); mx.inputs[7].default_value = (.18, .18, .19, 1)
    L.new(mx.outputs[2], b.inputs["Base Color"])
    return m

