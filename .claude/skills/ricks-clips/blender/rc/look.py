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
SUN = [-48.0, 15.0]                                                             # azimuth (deg, direction the light comes FROM, 0 = +Y, -90 = -X), elevation

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

def sky_hdri(scene, strength=1.0, hdri=HDRI, hdri_sun_deg=HDRI_SUN_DEG, sun_az=None, glow=.8, light=.5):
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
    # THE LAMP IS THE ONLY SUN (aerial view of crash_instinct, 2026-11-19): the photo's own sun (48 deg high) drew a second, short, soft
    # shadow and its fill washed out the long shadow of the lamp. For every ray but the camera's, the sky is capped (no hot sun) and
    # dimmed to `light`: it stays a soft blue fill, the hard long shadows come from sun() alone.
    lp = N.new("ShaderNodeLightPath"); cap = N.new("ShaderNodeMix"); cap.data_type = "RGBA"; cap.blend_type = "DARKEN"; cap.inputs[0].default_value = 1.0
    L.new(env.outputs["Color"], cap.inputs[6]); cap.inputs[7].default_value = (1.6, 1.6, 1.6, 1)
    pick = N.new("ShaderNodeMix"); pick.data_type = "RGBA"; L.new(lp.outputs["Is Camera Ray"], pick.inputs[0]); L.new(cap.outputs[2], pick.inputs[6]); L.new(env.outputs["Color"], pick.inputs[7])
    L.new(pick.outputs[2], bg.inputs["Color"])
    st = N.new("ShaderNodeMix"); st.data_type = "FLOAT"; L.new(lp.outputs["Is Camera Ray"], st.inputs[0]); st.inputs[2].default_value = light * strength; st.inputs[3].default_value = strength
    L.new(st.outputs[0], bg.inputs["Strength"])
    if glow > 0: sun_glow(w, glow)

def sun_glow(w, k=1.0, wide=5.0, tight=90.0):
    """THE SUN SEEN IN THE SKY (CB 2026-11-19: "le soleil doit apparaître en lueur en haut à gauche sur la vue aérienne"): a warm white glow
    around the direction of the sun LAMP (SUN), added to the sky for camera rays only (the lighting does not change): a wide halo that
    whitens the sky on the sun's side even when the sun is out of frame, and a hot core where the camera looks at it"""
    nt = w.node_tree; N, L = nt.nodes, nt.links; bg = N["Background"]; src = bg.inputs["Color"].links[0].from_socket
    el, az = math.radians(SUN[1]), math.radians(SUN[0]); d = (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))
    tc = N.new("ShaderNodeTexCoord"); nrm = N.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; L.new(tc.outputs["Generated"], nrm.inputs[0])
    dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; L.new(nrm.outputs["Vector"], dot.inputs[0]); dot.inputs[1].default_value = d
    def m(o, a, b):
        n_ = N.new("ShaderNodeMath"); n_.operation = o
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)): n_.inputs[i].default_value = v
            else: L.new(v, n_.inputs[i])
        return n_.outputs[0]
    c = m("MAXIMUM", dot.outputs["Value"], 0.0)
    g = m("ADD", m("MULTIPLY", m("POWER", c, wide), 1.5 * k), m("MULTIPLY", m("POWER", c, tight), 5.0 * k))
    lp = N.new("ShaderNodeLightPath"); g = m("MULTIPLY", g, lp.outputs["Is Camera Ray"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "ADD"; mx.clamp_result = False; L.new(g, mx.inputs[0]); L.new(src, mx.inputs[6]); mx.inputs[7].default_value = (1, .96, .88, 1)
    L.new(mx.outputs[2], bg.inputs["Color"])

def god_rays(c, center=(0, 0, 0), size=(34, 34, 16), density=.004, anisotropy=.75):
    """SUN RAYS (CB 2026-11-19): a light haze volume around the tree; the sun lamp shining through the crown draws the shafts"""
    m = bpy.data.materials.get("god_ray_haze") or bpy.data.materials.new("god_ray_haze"); m.use_nodes = True; nt = m.node_tree
    for n_ in list(nt.nodes):
        if n_.type != "OUTPUT_MATERIAL": nt.nodes.remove(n_)
    v = nt.nodes.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = density; v.inputs["Anisotropy"].default_value = anisotropy
    v.inputs["Color"].default_value = (1, .97, .9, 1); nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    o = box("god_rays", c, size, (center[0], center[1], size[2] / 2 - .05), m, bevel=0); o.visible_shadow = False
    return o

def light_shafts(c, n=14, seed=3, under=(0, 0, 4.4), spread=2.2, length=None, strength=.14, parent=None):
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
        p0 = Vector(under) + Vector((R.uniform(-spread, spread), R.uniform(-spread, spread), R.uniform(-.4, .6))); w0, w1 = R.uniform(.14, .32), R.uniform(.45, .85)   # broad soft beams, not thin lines
        L_ = length or min((p0.z / max(.2, -d.z)) * R.uniform(.55, .85), R.uniform(5.0, 7.5))   # from under the crown toward the ground, never across the sky; with a low sun they stay near the tree
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

def sun(scene, elevation=None, azimuth=None, energy=9.0, angle=2.0):
    elevation = SUN[1] if elevation is None else elevation; azimuth = SUN[0] if azimuth is None else azimuth; SUN[0], SUN[1] = azimuth, elevation
    s = bpy.data.lights.new("sun", "SUN"); s.energy = energy; s.angle = math.radians(angle); s.color = srgb("#fff3e2")
    o = bpy.data.objects.new("sun", s); col("LIGHT").objects.link(o)
    el, az = math.radians(elevation), math.radians(azimuth)                       # azimuth: direction the light COMES FROM, 0 = +Y, -90 = -X
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    o.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); return o

def _math(N, L, o, a, b=None, c=None, clamp=False):
    """one Math node; each input is a socket or a number"""
    n_ = N.new("ShaderNodeMath"); n_.operation = o; n_.use_clamp = clamp
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n_.inputs[i].default_value = v
        else: L.new(v, n_.inputs[i])
    return n_.outputs[0]

def tex(name, ph_id, tile=2.0, tint=None, tint_k=0.0, value=1.0, rot=0.0, normal=1.0, rough_mul=1.0, spec=.12,
        recolor=None, untile=True, macro=.18, stripes=None):
    """a CC0 Poly Haven PBR set like street.pbr, made for GROUNDS seen from any height (CB 2026-11-19, aerial view of crash_instinct):
      spec .12      LOW specular: from a high or grazing camera a ground mirrors the bright sky and turns light grey. Ground = matte.
      rot           rotation of the pattern (furrows along the road); normal = relief strength
      recolor       "#hex": the scan keeps its light/dark detail but takes exactly this colour (a field must be golden, not the brown of the scan)
      untile        a second, bigger, turned copy of the scan mixed in by a soft noise: no visible repeating squares from the air
      macro         large patches (3-25 m) a little lighter / darker: from far a texture averages to ONE flat colour, a real ground never does
      stripes       (period m, depth 0..1): regular fine dark lines along Y (furrows / drill rows), readable from the air"""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = pbr(name, ph_id, tile=tile, tint=None if recolor else tint, tint_k=0 if recolor else tint_k, value=1.0 if recolor else value, normal=normal, rough_mul=rough_mul)
    nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    b.inputs["Specular IOR Level"].default_value = spec
    mp = [n_ for n_ in N if n_.type == "MAPPING"][0]; mp.inputs["Rotation"].default_value = (0, 0, math.radians(rot))
    tc = [n_ for n_ in N if n_.type == "TEX_COORD"][0]; obj = tc.outputs["Object"]
    src = b.inputs["Base Color"].links[0].from_socket
    ctex = [n_ for n_ in N if n_.type == "TEX_IMAGE" and n_.image.colorspace_settings.name != "Non-Color"][0]
    if untile:
        mp2 = N.new("ShaderNodeMapping"); L.new(obj, mp2.inputs["Vector"]); mp2.inputs["Scale"].default_value = (1 / (tile * 2.7),) * 3
        mp2.inputs["Rotation"].default_value = (0, 0, math.radians(rot if stripes or rot else 37)); mp2.inputs["Location"].default_value = (.37, .61, 0)
        t2 = N.new("ShaderNodeTexImage"); t2.image = ctex.image; t2.projection = "BOX"; t2.projection_blend = .2; L.new(mp2.outputs["Vector"], t2.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .11; nz.inputs["Detail"].default_value = 2; L.new(obj, nz.inputs["Vector"])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; L.new(_math(N, L, "MULTIPLY_ADD", nz.outputs["Fac"], 3.0, -1.0, clamp=True), mx.inputs[0])
        users = [lk.to_socket for lk in ctex.outputs["Color"].links]
        L.new(ctex.outputs["Color"], mx.inputs[6]); L.new(t2.outputs["Color"], mx.inputs[7])
        for sk in users: L.new(mx.outputs[2], sk)
        if src == ctex.outputs["Color"]: src = mx.outputs[2]
    val = None
    def times(v): return v if val is None else _math(N, L, "MULTIPLY", val, v)
    if recolor:
        import numpy as np
        px = np.array(ctex.image.pixels[:], dtype=np.float32).reshape(-1, 4)[::7, :3]
        mean = float((px ** 2.2 @ np.array([.2126, .7152, .0722], dtype=np.float32)).mean()) or .2
        bw = N.new("ShaderNodeRGBToBW"); L.new(src, bw.inputs[0])
        rel = _math(N, L, "MULTIPLY_ADD", bw.outputs[0], .75 / mean, .25)                      # 1.0 = the scan's average brightness
        val = _math(N, L, "MULTIPLY", _math(N, L, "MINIMUM", _math(N, L, "MAXIMUM", rel, .45), 1.6), value)
    if macro:
        n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = .045; n1.inputs["Detail"].default_value = 4; L.new(obj, n1.inputs["Vector"])
        n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = .4; n2.inputs["Detail"].default_value = 3; L.new(obj, n2.inputs["Vector"])
        val = times(_math(N, L, "ADD", _math(N, L, "MULTIPLY_ADD", n1.outputs["Fac"], 2.8 * macro, 1.0 - 2 * macro), _math(N, L, "MULTIPLY", n2.outputs["Fac"], 1.2 * macro)))
    if stripes:
        period, depth = stripes; sx = N.new("ShaderNodeSeparateXYZ"); L.new(obj, sx.inputs[0])
        line = _math(N, L, "POWER", _math(N, L, "MULTIPLY_ADD", _math(N, L, "COSINE", _math(N, L, "MULTIPLY", sx.outputs["X"], 2 * math.pi / period)), .5, .5), 5.0)
        val = times(_math(N, L, "SUBTRACT", 1.0, _math(N, L, "MULTIPLY", line, depth)))
    if val is not None:
        hv = N.new("ShaderNodeHueSaturation"); L.new(val, hv.inputs["Value"])
        if recolor: hv.inputs["Color"].default_value = (*srgb(recolor), 1)
        else: L.new(src, hv.inputs["Color"])
        L.new(hv.outputs["Color"], b.inputs["Base Color"])
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

