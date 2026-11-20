"""exploding-whale: THE DRAWN WORLD (CB 2026-11-20, side by side with the references: "pratiquement rien n'a été fait").
What the references have and a photo world (HDRI sky + scanned sand) has not, done here on top of sets/beach.py:
  1. an ink line around every 3D object (inverted hull: works in Cycles with motion blur) so the 3D goes with the drawn characters
  2. a painted sky (peach horizon -> blue zenith) with drawn clouds, a stylised sea (turquoise -> deep blue) with white foam drawings
  3. flat decided colours (blue / orange opposition) with drawn detail (planks, stripes, bands), coloured shadows (blue ambient, warm sun)
  4. a dressed beach: rowboat, jetty, buoys, traps, umbrella, shells, starfish, kelp, a lighthouse on the far headland, a sail on the horizon
    import toon; toon.stylize(scene, whale); toon.dress(col)"""
import bpy, bmesh, math, random
from mathutils import Vector
import beach
from beach import col, mesh_obj, height, SEA_Z, SHORE_Y

INK = (.035, .03, .07)
STYLE = "real"          # "real": real sky, scanned sand, real water, PBR surfaces, no ink line on the 3D (CB 2026-11-20, reference: The Instinct That Makes You Crash) | "drawn": the painted world

# ------------------------------------------------------------------------------------------------------------ node helpers
def _m(N, L, op, a, b=None, c=None, clamp=False):
    n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]

def _mix(N, L, fac, a, b):
    n = N.new("ShaderNodeMix"); n.data_type = "RGBA"
    for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(v, (int, float)): sock.default_value = v
        elif isinstance(v, (tuple, list)): sock.default_value = (*v[:3], 1)
        else: L.new(v, sock)
    return n.outputs[2]

def _ramp(N, L, fac, stops, interp="LINEAR"):
    r = N.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = interp; e = r.color_ramp.elements
    while len(e) < len(stops): e.new(.5)
    for el, (p, c) in zip(e, stops): el.position = p; el.color = (*c, 1)
    L.new(fac, r.inputs["Fac"]); return r.outputs["Color"]

# ------------------------------------------------------------------------------------------------------------ materials
def paint(name, rgb, rough=.55, planks=None, stripes=None, band=None, emit=0.0):
    """a flat decided colour with DRAWN detail. planks=(axis, spacing, width): thin ink lines every `spacing` m; stripes=(axis, spacing, rgb2):
    two colours alternating; band=(axis, above, rgb2): a second colour above a height. Axis in object space (0 x, 1 y, 2 z)."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = .25; tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0]); c = None
    if stripes: c = _mix(N, L, _m(N, L, "LESS_THAN", _m(N, L, "FRACT", _m(N, L, "DIVIDE", sep.outputs[stripes[0]], stripes[1])), .5), rgb, stripes[2])
    if band: c = _mix(N, L, _m(N, L, "GREATER_THAN", sep.outputs[band[0]], band[1]), c if c is not None else rgb, band[2])
    if planks: c = _mix(N, L, _m(N, L, "LESS_THAN", _m(N, L, "FRACT", _m(N, L, "DIVIDE", sep.outputs[planks[0]], planks[1])), planks[2] / planks[1]), c if c is not None else rgb, tuple(v * .28 for v in rgb))
    if c is None: b.inputs["Base Color"].default_value = (*rgb, 1)
    else: L.new(c, b.inputs["Base Color"])
    c0 = c
    if STYLE == "real" and not emit:                                                                  # a real surface: patches of wear in the gloss, a fine grain, dirt in the creases, dust on top, a clear coat on glossy paint
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = .65; L.new(tc.outputs["Object"], nz.inputs["Vector"])
        fn = N.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 90; fn.inputs["Detail"].default_value = 3; L.new(tc.outputs["Object"], fn.inputs["Vector"])
        L.new(_m(N, L, "MULTIPLY_ADD", nz.outputs["Fac"], .45, rough - .2, clamp=True), b.inputs["Roughness"])
        ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = .25; ao.samples = 4; geo = N.new("ShaderNodeNewGeometry"); sp2 = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sp2.inputs[0])
        src = c if c is not None else rgb
        c = _mix(N, L, _m(N, L, "MULTIPLY", _m(N, L, "SUBTRACT", 1.0, ao.outputs["AO"]), 1.4, clamp=True), src, tuple(v * .25 for v in rgb))
        c = _mix(N, L, _m(N, L, "MULTIPLY", _m(N, L, "MULTIPLY_ADD", nz.outputs["Fac"], 1.6, -.55, clamp=True), .22), c, tuple(v * .6 + .12 for v in rgb))          # sun-bleached patches
        c = _mix(N, L, _m(N, L, "MULTIPLY", _m(N, L, "MULTIPLY_ADD", sp2.outputs["Z"], 1.6, -.8, clamp=True), .3), c, (.62, .57, .48)); L.new(c, b.inputs["Base Color"])
        bev = N.new("ShaderNodeBevel"); bev.samples = 4; bev.inputs["Radius"].default_value = .012; bmp = N.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = .08; bmp.inputs["Distance"].default_value = .01
        L.new(fn.outputs["Fac"], bmp.inputs["Height"]); L.new(bev.outputs["Normal"], bmp.inputs["Normal"]); L.new(bmp.outputs["Normal"], b.inputs["Normal"])
        if rough < .45: b.inputs["Coat Weight"].default_value = .35; b.inputs["Coat Roughness"].default_value = .08
    if emit:
        if c is None: b.inputs["Emission Color"].default_value = (*rgb, 1)
        else: L.new(c, b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    return m

def line_mat():
    """the ink line: a dark shell seen only from inside out (inverted hull), invisible to shadow rays"""
    m = bpy.data.materials.get("ink_line")
    if m: return m
    m = bpy.data.materials.new("ink_line"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); mix = N.new("ShaderNodeMixShader"); em = N.new("ShaderNodeEmission"); tr = N.new("ShaderNodeBsdfTransparent")
    em.inputs["Color"].default_value = (*INK, 1); em.inputs["Strength"].default_value = 1.0; geo = N.new("ShaderNodeNewGeometry"); lp = N.new("ShaderNodeLightPath")
    hide = _m(N, L, "MAXIMUM", geo.outputs["Backfacing"], _m(N, L, "SUBTRACT", 1.0, lp.outputs["Is Camera Ray"]))
    L.new(hide, mix.inputs[0]); L.new(em.outputs[0], mix.inputs[1]); L.new(tr.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs["Surface"]); return m

def outline(o, t=.02):
    if STYLE == "real" or o.type != "MESH" or o.modifiers.get("ink_line"): return o
    o.data.materials.append(line_mat()); md = o.modifiers.new("ink_line", "SOLIDIFY"); md.thickness = t * 1.8; md.offset = 1.0; md.use_flip_normals = True; md.use_rim = False
    md.material_offset = len(o.data.materials) - 1; md.use_quality_normals = True; return o

# ------------------------------------------------------------------------------------------------------------ the painted sky
def sky(scene, ambient=(.50, .60, 1.0), k=.30, sun=(95, 24)):
    """camera rays: a painted gradient (peach at the horizon, blue above, as in the references' sea shots); light: a blue ambient, so that
    every shadow is coloured"""
    w = scene.world; nt = w.node_tree; N, L = nt.nodes, nt.links; N.clear(); out = N.new("ShaderNodeOutputWorld")
    tc = N.new("ShaderNodeTexCoord"); nrm = N.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; L.new(tc.outputs["Generated"], nrm.inputs[0]); sep = N.new("ShaderNodeSeparateXYZ"); L.new(nrm.outputs[0], sep.inputs[0])
    grad = _ramp(N, L, _m(N, L, "ADD", sep.outputs["Z"], .02, clamp=True),
                 (((0.0, (1.0, .56, .34)), (.03, (1.0, .74, .56)), (.07, (.98, .86, .80))) if sun[1] < 35 else ((0.0, (.86, .96, 1.0)), (.03, (.78, .94, 1.0)), (.07, (.64, .90, 1.0)))) + ((.13, (.50, .86, 1.0)), (.27, (.14, .52, 1.0)), (.5, (.07, .36, .95)), (.85, (.05, .24, .82))))                 # low sun: a peach horizon; high sun (noon): a pale cyan horizon, never grey
    el, az = math.radians(sun[1]), math.radians(sun[0]); sd = N.new("ShaderNodeVectorMath"); sd.operation = "DOT_PRODUCT"; sd.inputs[1].default_value = (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)); L.new(nrm.outputs[0], sd.inputs[0])
    halo = _m(N, L, "POWER", _m(N, L, "MAXIMUM", sd.outputs["Value"], 0.0), 5.0); core = _m(N, L, "GREATER_THAN", sd.outputs["Value"], .9988)
    grad = _mix(N, L, _m(N, L, "MULTIPLY", halo, .55), grad, (1.0, .90, .66)); grad = _mix(N, L, core, grad, (1.0, .98, .86))                # the sun: a warm halo and a drawn disc
    lp = N.new("ShaderNodeLightPath"); cam = N.new("ShaderNodeBackground"); L.new(grad, cam.inputs["Color"]); cam.inputs["Strength"].default_value = 1.0
    amb = N.new("ShaderNodeBackground"); amb.inputs["Color"].default_value = (*ambient, 1); amb.inputs["Strength"].default_value = k
    mix = N.new("ShaderNodeMixShader"); L.new(lp.outputs["Is Camera Ray"], mix.inputs[0]); L.new(amb.outputs[0], mix.inputs[1]); L.new(cam.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs["Surface"])

def clouds(c, seed=4, dist=900.0, sun=(95, 24)):
    """a drawn sky in three layers (the references' skies are never one row of clouds): big cumulus (white on top, warm on the sun side,
    lavender under), a line of small clouds sitting on the horizon, long thin streaks high up; and a few gulls far away"""
    m = bpy.data.materials.new("cloud_paint"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear(); out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
    base = _ramp(N, L, _m(N, L, "MULTIPLY_ADD", sep.outputs["Z"], .5, .5), ((.28, (.56, .60, .98)), (.44, (.84, .86, 1.0)), (.58, (1.0, .99, .97))))
    el, az = math.radians(sun[1]), math.radians(sun[0]); sd = N.new("ShaderNodeVectorMath"); sd.operation = "DOT_PRODUCT"; sd.inputs[1].default_value = (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)); L.new(geo.outputs["Normal"], sd.inputs[0])
    L.new(_mix(N, L, _m(N, L, "MULTIPLY", _m(N, L, "GREATER_THAN", sd.outputs["Value"], .45), .55), base, (1.0, .86, .68)), em.inputs["Color"]); em.inputs["Strength"].default_value = 1.05
    L.new(em.outputs[0], out.inputs["Surface"]); R = random.Random(seed)
    def puff(name, k, az, el, s, flat=.8, d=dist):
        bm = bmesh.new(); x = 0.0
        for j in range(k):
            r = R.uniform(.55, 1.0) * (1.0 - abs(j - (k - 1) / 2) / k); mat = bmesh.ops.create_icosphere(bm, subdivisions=4, radius=r)
            bmesh.ops.translate(bm, verts=mat["verts"], vec=(x, R.uniform(-.2, .2), r * .55)); x += r * 1.05
            if R.random() < .5 and r > .5:
                m2 = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r * .6); bmesh.ops.translate(bm, verts=m2["verts"], vec=(x - r * 1.3, 0, r * 1.15))   # a second storey
        for v in bm.verts: v.co.z = max(v.co.z, 0.0); v.co.x -= x / 2
        o = mesh_obj(name, bm, m, c, smooth=True); a, e = math.radians(az), math.radians(el)
        o.location = (d * math.sin(a) * math.cos(e), d * math.cos(a) * math.cos(e), d * math.sin(e)); o.scale = (s, s, s * flat); o.rotation_euler = (0, 0, -a)
        o.visible_shadow = o.visible_diffuse = o.visible_glossy = False; return o
    for i in range(14): puff("cloud%02d" % i, R.randint(5, 9), R.uniform(-85, 85) if i < 10 else R.uniform(100, 260), R.uniform(7, 30), R.uniform(45, 92))
    for i in range(16): puff("cloud_h%02d" % i, R.randint(4, 7), -90 + i * 12 + R.uniform(-4, 4), R.uniform(1.6, 3.6), R.uniform(22, 40), .7, 1500.0)       # the horizon line
    for i in range(9): puff("cloud_s%02d" % i, R.randint(8, 12), R.uniform(-80, 80), R.uniform(36, 62), R.uniform(60, 110), .12)                           # high streaks
    for i in range(9): puff("cloud_z%02d" % i, R.randint(5, 8), R.uniform(0, 360), R.uniform(56, 86), R.uniform(55, 95), .5)                              # overhead: a camera that looks straight up never finds an empty blue
    gm = paint("far_gull", (.98, .98, 1.0), .5, emit=1.0)
    for i in range(9):                                                                         # gulls far out: two strokes each
        a = math.radians(R.uniform(-40, 40)); e = math.radians(R.uniform(6, 22)); d = R.uniform(140, 260); bm = bmesh.new(); w = R.uniform(1.6, 2.6)
        vs = [bm.verts.new(p) for p in ((-w, 0, .5 * w * .5), (-w * .5, 0, w * .32), (0, 0, 0), (w * .5, 0, w * .32), (w, 0, .5 * w * .5), (0, 0, -.28 * w))]
        bm.faces.new((vs[0], vs[1], vs[2], vs[5])); bm.faces.new((vs[2], vs[3], vs[4], vs[5]))
        o = mesh_obj("far_gull%d" % i, bm, gm, c); o.location = (d * math.sin(a) * math.cos(e), d * math.cos(a) * math.cos(e), d * math.sin(e)); o.rotation_euler = (0, R.uniform(-.3, .3), -a); o.visible_shadow = False
        o.keyframe_insert("location", frame=0); o.location.x += R.uniform(-22, 22); o.location.z += R.uniform(-3, 5); o.keyframe_insert("location", frame=240)

# ------------------------------------------------------------------------------------------------------------ sea and sand
def sea():
    """the drawn sea: turquoise at the beach, deep blue far out; white foam DRAWINGS (curved lines that roll in) and a foam edge on the sand"""
    m = bpy.data.materials["sea"]; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear(); out = N.new("ShaderNodeOutputMaterial"); b = N.new("ShaderNodeBsdfPrincipled"); L.new(b.outputs[0], out.inputs["Surface"])
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sep.inputs[0]); d = _m(N, L, "SUBTRACT", sep.outputs["Y"], SHORE_Y - 3.0)
    base = _ramp(N, L, _m(N, L, "DIVIDE", d, 420.0, clamp=True), ((0.0, (.30, .92, .86)), (.03, (.05, .72, .86)), (.14, (.02, .40, .90)), (.5, (.02, .20, .66)), (1.0, (.03, .13, .50))))
    mp = N.new("ShaderNodeMapping"); L.new(geo.outputs["Position"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (.035, .16, 1)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.3; nz.inputs["Detail"].default_value = 2; L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Y"; wv.inputs["Scale"].default_value = 1.0; wv.inputs["Distortion"].default_value = 16.0; wv.inputs["Detail"].default_value = 2.0; wv.inputs["Detail Scale"].default_value = 1.4
    L.new(mp.outputs["Vector"], wv.inputs["Vector"]); dr = wv.inputs["Phase Offset"].driver_add("default_value").driver; dr.expression = "frame*0.05"
    lines = _m(N, L, "MULTIPLY", _m(N, L, "GREATER_THAN", wv.outputs["Fac"], .955), _m(N, L, "GREATER_THAN", nz.outputs["Fac"], .42))            # broken curved strokes, not stripes
    lines = _m(N, L, "MULTIPLY", lines, _m(N, L, "SUBTRACT", 1.0, _m(N, L, "DIVIDE", d, 260.0, clamp=True), clamp=True))                    # none far out (they would flicker)
    en = N.new("ShaderNodeTexNoise"); en.inputs["Scale"].default_value = .35; L.new(geo.outputs["Position"], en.inputs["Vector"])
    edge = _m(N, L, "LESS_THAN", d, _m(N, L, "MULTIPLY_ADD", en.outputs["Fac"], 3.0, 1.2))                                                  # the foam edge lying on the sand
    foam = _m(N, L, "MAXIMUM", lines, edge); colr = _mix(N, L, foam, base, (1.0, 1.0, 1.0))
    L.new(colr, b.inputs["Base Color"]); L.new(colr, b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = .30; b.inputs["Roughness"].default_value = .22; b.inputs["Specular IOR Level"].default_value = .35

def sand():
    """the drawn sand (CB 2026-11-20: "le sable est jaune, je n'aime pas, une couleur plus blanche" + more drawing on the ground): a pale
    cream, cooler and shiny where the sea wets it, almost white on the dunes; on it, DRAWN: groups of curved ripple strokes, soft
    lavender hollows, speckles (grains, bits of shell), lace of dried foam along the wet line"""
    m = bpy.data.materials["beach_sand"]; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear(); out = N.new("ShaderNodeOutputMaterial"); b = N.new("ShaderNodeBsdfPrincipled"); L.new(b.outputs[0], out.inputs["Surface"])
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sep.inputs[0])
    def noise(scale, detail=3):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; L.new(geo.outputs["Position"], n.inputs["Vector"]); return n.outputs["Fac"]
    big = noise(.09); mid = noise(.45, 2); grp = noise(.22, 2)
    y = _m(N, L, "ADD", sep.outputs["Y"], _m(N, L, "MULTIPLY_ADD", big, 5.0, -2.5))                                                          # the wet line wanders
    wet = _m(N, L, "DIVIDE", _m(N, L, "SUBTRACT", y, SHORE_Y - 10.5), 6.0, clamp=True)
    base = _ramp(N, L, _m(N, L, "MULTIPLY_ADD", sep.outputs["Y"], 1 / 60.0, .75, clamp=True), ((0.0, (.93, .90, .84)), (.5, (.88, .83, .74)), (1.0, (.85, .79, .69))))   # dunes almost white
    base = _mix(N, L, _m(N, L, "MULTIPLY", _m(N, L, "GREATER_THAN", mid, .56), .45), base, (.62, .62, .82))                                  # soft lavender hollows, hard edged: drawn, not shaded
    base = _mix(N, L, _m(N, L, "MULTIPLY_ADD", big, .5, -.1, clamp=True), base, (.90, .80, .64))                                              # large warmer patches
    mp = N.new("ShaderNodeMapping"); L.new(geo.outputs["Position"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (.3, 1.5, 1)
    wv = N.new("ShaderNodeTexWave"); wv.bands_direction = "Y"; wv.inputs["Scale"].default_value = 1.0; wv.inputs["Distortion"].default_value = 14.0; wv.inputs["Detail"].default_value = 2.0; wv.inputs["Detail Scale"].default_value = 1.6; L.new(mp.outputs["Vector"], wv.inputs["Vector"])
    strokes = _m(N, L, "MULTIPLY", _m(N, L, "GREATER_THAN", wv.outputs["Fac"], .90), _m(N, L, "GREATER_THAN", grp, .50))                      # ripple strokes, in groups
    base = _mix(N, L, _m(N, L, "MULTIPLY", strokes, .8), base, (.50, .42, .40))
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 5.5; L.new(geo.outputs["Position"], vo.inputs["Vector"])
    dots = _m(N, L, "MULTIPLY", _m(N, L, "LESS_THAN", vo.outputs["Distance"], .075), _m(N, L, "GREATER_THAN", noise(1.3, 1), .52))            # speckles, in patches
    base = _mix(N, L, _m(N, L, "MULTIPLY", dots, .6), base, (.55, .46, .44))
    lw = N.new("ShaderNodeTexWave"); lw.bands_direction = "Y"; lw.inputs["Scale"].default_value = .55; lw.inputs["Distortion"].default_value = 6.0; lw.inputs["Detail"].default_value = 2.0; L.new(geo.outputs["Position"], lw.inputs["Vector"])
    lace = _m(N, L, "MULTIPLY", _m(N, L, "GREATER_THAN", lw.outputs["Fac"], .93), _m(N, L, "MULTIPLY", wet, _m(N, L, "SUBTRACT", 1.0, wet), clamp=True))   # dried foam where wet meets dry
    colr = _mix(N, L, wet, base, (.56, .55, .60)); colr = _mix(N, L, _m(N, L, "MULTIPLY", lace, 3.2, clamp=True), colr, (1.0, 1.0, 1.0)); L.new(colr, b.inputs["Base Color"])
    L.new(_m(N, L, "MULTIPLY_ADD", wet, -.64, .9), b.inputs["Roughness"]); b.inputs["Specular IOR Level"].default_value = .3

def recolor(o, rgb, detail=.5, rough=.5):
    """keep a model's own texture only as drawn detail (its light and dark), over ONE decided colour"""
    for sl in o.material_slots:
        m = sl.material
        if not m or not m.use_nodes or m.name == "ink_line": continue
        nt = m.node_tree; N, L = nt.nodes, nt.links; b = N.get("Principled BSDF")
        if not b: continue
        if b.inputs["Base Color"].links:
            src = b.inputs["Base Color"].links[0].from_socket; bw = N.new("ShaderNodeRGBToBW"); L.new(src, bw.inputs[0])
            L.new(_mix(N, L, _m(N, L, "MULTIPLY_ADD", bw.outputs[0], 2.2 * detail, .5 - .5 * detail, clamp=True), tuple(v * .45 for v in rgb), tuple(min(1, v * 1.5) for v in rgb)), b.inputs["Base Color"])
        else: b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Roughness"].default_value = rough

def stylize(scene, whale=None, sun_color=(1.0, .90, .74), sun=(95, 24), dim=1.0):
    """turn the photo beach into the drawn beach (call after beach.build and after the shot's own objects exist)"""
    if STYLE == "real": return realist(scene, whale, sun)
    sky(scene, sun=sun, k=.30 * dim); clouds(col("L_SET"), sun=sun); sea(); sand()
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "SUN": o.data.color = sun_color; o.data.energy *= (.7 if sun[1] < 35 else .55) * dim       # the pale sand is held by the LAMP, not by the exposure: sky, clouds and characters keep their brightness (CB 2026-11-20)
        if o.name.startswith("bounce_fill"): o.data.energy *= .35 * dim
        if o.name.startswith("rock"):
            o.data.materials.clear(); o.data.materials.append(paint("rock_paint", (.13, .16, .27), .5)); outline(o, .05)
        if o.name.startswith("driftwood"):
            o.data.materials.clear(); o.data.materials.append(paint("wood_paint", (.80, .56, .34), .7, planks=(2, .34, .03))); outline(o, .03)
    for o in bpy.data.objects:                                                                     # the drawn characters stay WHITE: mostly their own light (CB 2026-11-20: "les personnages blancs semblent assombris")
        if o.name.startswith("Card_"):
            for m in o.data.materials:
                for nd in (m.node_tree.nodes if m and m.use_nodes else ()):
                    if nd.type == "MIX_SHADER" and not nd.inputs[0].links: nd.inputs[0].default_value = max(nd.inputs[0].default_value, .86)
    if whale:
        for o in whale.children_recursive:
            if o.type == "MESH": recolor(o, (.15, .23, .43), .6, .4); outline(o, .04 / whale.scale.x)      # model units
    g = bpy.data.materials.get("marram")
    if g:
        b = g.node_tree.nodes.get("Principled BSDF"); src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
        if src:
            hs = g.node_tree.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Hue"].default_value = .56; hs.inputs["Saturation"].default_value = 1.9; hs.inputs["Value"].default_value = 1.25
            g.node_tree.links.new(src, hs.inputs["Color"]); g.node_tree.links.new(hs.outputs["Color"], b.inputs["Base Color"])

# ------------------------------------------------------------------------------------------------------------ props
def _box(name, size, loc, mat, c, rot=(0, 0, 0), parent=None, line=.015, bevel=.012):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel: bmesh.ops.bevel(bm, geom=bm.edges[:], offset=min(bevel, min(size) * .3), segments=2, affect="EDGES")
    o = mesh_obj(name, bm, mat, c); o.location = loc; o.rotation_euler = rot; o.parent = parent
    return outline(o, line) if line else o

def _cyl(name, r, h, loc, mat, c, rot=(0, 0, 0), parent=None, line=.015, r2=None, seg=20):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = mesh_obj(name, bm, mat, c, smooth=True); o.location = loc; o.rotation_euler = rot; o.parent = parent
    try: o.data.set_sharp_from_angle(angle=.9)
    except Exception: pass
    return outline(o, line) if line else o

def _ball(name, r, loc, mat, c, scale=(1, 1, 1), parent=None, line=.015, seed=0, rough=0.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r); R = random.Random(seed)
    if rough:
        a, b, cc = R.uniform(2, 5), R.uniform(2, 5), R.uniform(0, 6)
        for v in bm.verts: v.co *= 1 + rough * math.sin(v.co.x * a / r + cc) * math.cos(v.co.y * b / r)
    o = mesh_obj(name, bm, mat, c, smooth=True); o.location = loc; o.scale = scale; o.parent = parent
    return outline(o, line) if line else o

def _ring(name, r, t, loc, mat, c, rot=(0, 0, 0), parent=None):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = t; cu.bevel_resolution = 3; sp = cu.splines.new("POLY"); sp.points.add(31); sp.use_cyclic_u = True
    for i, p in enumerate(sp.points): p.co = (r * math.cos(i * math.tau / 32), r * math.sin(i * math.tau / 32), 0, 1)
    o = bpy.data.objects.new(name, cu); c.objects.link(o); cu.materials.append(mat); o.location = loc; o.rotation_euler = rot; o.parent = parent; return o

def _root(name, c, at, yaw=0.0, tilt=(0, 0)):
    o = bpy.data.objects.new(name, None); c.objects.link(o); o.location = (at[0], at[1], at[2] if len(at) > 2 else height(at[0], at[1])); o.rotation_euler = (tilt[0], tilt[1], yaw); return o

WHITE, RED, BLUE, ORANGE, NAVY, WOOD, ROPE = (.95, .94, .9), (.86, .09, .06), (.06, .30, .78), (1.0, .42, .05), (.05, .10, .30), (.62, .36, .18), (.86, .72, .46)

def rowboat(c, at, yaw):
    """a clinker rowing boat pulled up on the sand: white hull, blue top strake, plank lines, two thwarts, two oars"""
    R = _root("rowboat", c, at, yaw, (math.radians(9), 0)); bm = bmesh.new(); S = []; n = 12
    for i in range(n + 1):
        x = -1.9 + 3.8 * i / n; t = x / 1.9; w = .72 * (1 - abs(t) ** 2.4) ** .5 if abs(t) < 1 else 0.0; w = max(w, .02); k = .1 * t * t
        S.append([bm.verts.new(p) for p in ((x, w, .52 + k), (x, w * .86, .2 + k), (x, w * .4, .03 + k), (x, 0, 0 + k), (x, -w * .4, .03 + k), (x, -w * .86, .2 + k), (x, -w, .52 + k))])
    for i in range(n):
        for j in range(6): bm.faces.new((S[i][j], S[i + 1][j], S[i + 1][j + 1], S[i][j + 1]))
    o = mesh_obj("rowboat_hull", bm, paint("boat_hull", WHITE, .5, planks=(2, .11, .012), band=(2, .40, BLUE)), c, smooth=True); o.parent = R
    md = o.modifiers.new("wall", "SOLIDIFY"); md.thickness = .035; md.offset = 0; outline(o, .02)
    seat = paint("boat_seat", WOOD, .6, planks=(0, .12, .012))
    for x in (-.7, .5): _box("thwart", (.26, 1.25, .04), (x, 0, .4), seat, c, parent=R, line=.012)
    for s in (-1, 1):
        _cyl("oar", .025, 2.5, (.1, s * .45, .5), paint("oar_wood", (.80, .60, .36), .5), c, rot=(0, math.radians(90), s * .12), parent=R, line=.01)
        _box("oar_blade", (.5, .16, .025), (1.5, s * .6, .5), paint("oar_blade", RED, .5), c, rot=(0, 0, s * .12), parent=R, line=.01)
    return R

def jetty(c, x=-10.4, y0=10.0, y1=33.0):
    """a small wooden jetty walking into the sea: paired posts, a plank deck, a lifebuoy on the last post"""
    post = paint("jetty_post", (.42, .24, .13), .7, planks=(2, .5, .03)); deck = paint("jetty_deck", (.72, .46, .24), .65, planks=(1, .32, .03)); z = SEA_Z + 1.25
    _box("jetty_deck", (1.9, y1 - y0, .1), (x, (y0 + y1) / 2, z), deck, c, line=.03); y = y0 + .6
    while y < y1:
        for s in (-1, 1): _cyl("jetty_post", .13, 2.6, (x + s * .95, y, z - .9), post, c, line=.025, seg=12)
        _box("jetty_beam", (2.1, .14, .14), (x, y, z - .12), post, c, line=.02); y += 3.2
    _ring("lifebuoy", .32, .09, (x + 1.1, y1 - .7, z + .55), paint("buoy_ring", ORANGE, .5, stripes=(0, .32, WHITE)), c, rot=(0, math.radians(90), 0))

def umbrella(c, at, yaw=0.0):
    """a striped beach umbrella planted askew, a deck chair, a red cooler: the colour accent of the beach"""
    R = _root("umbrella", c, at, yaw, (math.radians(10), math.radians(6)))
    _cyl("umb_pole", .022, 2.3, (0, 0, 1.15), paint("umb_pole", (.9, .9, .88), .4), c, parent=R, line=.008, seg=10)
    _cyl("umb_top", 1.25, .5, (0, 0, 2.2), paint("umb_cloth", RED, .7, stripes=(0, .42, WHITE)), c, parent=R, r2=.03, line=.02, seg=10)
    ch = _root("chair", c, (at[0] + .9, at[1] - .5), yaw + .5); fr = paint("chair_wood", WOOD, .6); cl = paint("chair_cloth", BLUE, .8, stripes=(1, .16, WHITE))
    _box("chair_seat", (.55, .6, .03), (0, 0, .28), cl, c, rot=(math.radians(-12), 0, 0), parent=ch, line=.01)
    _box("chair_back", (.55, .03, .75), (0, .36, .6), cl, c, rot=(math.radians(-22), 0, 0), parent=ch, line=.01)
    for s in (-1, 1): _box("chair_leg", (.03, .8, .03), (s * .29, .05, .2), fr, c, rot=(math.radians(28), 0, 0), parent=ch, line=.008)
    co = _root("cooler", c, (at[0] - .8, at[1] - .3), yaw - .3)
    _box("cooler_body", (.55, .36, .3), (0, 0, .15), paint("cooler_red", RED, .4), c, parent=co, line=.012); _box("cooler_lid", (.58, .39, .07), (0, 0, .335), paint("cooler_lid", WHITE, .4), c, parent=co, line=.012)

def tackle(c, at, seed=1):
    """what the fishermen left: lobster traps, striped buoys, a coil of rope"""
    R = random.Random(seed); trap = paint("trap_wood", (.70, .44, .22), .7, planks=(0, .13, .028)); x, y = at
    for i, (dx, dy, dzz, rz) in enumerate(((0, 0, 0, .2), (.95, .15, 0, -.1), (.45, .1, .42, .35))):
        _box("trap%d" % i, (.8, .5, .4), (x + dx, y + dy, height(x + dx, y + dy) + .2 + dzz), trap, c, rot=(0, 0, rz), line=.014)
    for i, (dx, dy, colr) in enumerate(((-.8, .3, RED), (-1.2, -.3, ORANGE), (1.9, -.2, BLUE))):
        _ball("buoy%d" % i, .2, (x + dx, y + dy, height(x + dx, y + dy) + .2), paint("buoy_%d" % i, colr, .4, band=(2, .04, WHITE)), c, scale=(1, 1, 1.25), line=.012)
    for k in range(4): _ring("rope%d" % k, .3 - k * .012, .03, (x + .4, y - .85, height(x, y - .85) + .04 + k * .05), paint("rope", ROPE, .8), c)

def litter(c, seed=7, clear=()):
    """the tide line: starfish, shells, kelp, pebbles (small readable shapes, each with its ink line)"""
    R = random.Random(seed); star = paint("starfish", ORANGE, .6); shell = paint("shell", (1.0, .80, .76), .4); kelp = paint("kelp", (.10, .36, .16), .5); peb = paint("pebble", (.36, .40, .52), .5)
    def free(x, y): return all((x - cx) ** 2 + (y - cy) ** 2 > r * r for cx, cy, r in clear)
    for i in range(170):
        if i < 60: x, y = R.uniform(-30, 34), R.uniform(4.5, 10.5)
        else: x, y = R.uniform(-14, 18), R.uniform(-12.0, -5.2)
        if not free(x, y): continue
        z = height(x, y); k = R.random()
        if k < .22:
            bm = bmesh.new(); r = R.uniform(.11, .2); vs = [bm.verts.new((math.cos(j * math.tau / 10) * (r if j % 2 == 0 else r * .42), math.sin(j * math.tau / 10) * (r if j % 2 == 0 else r * .42), 0)) for j in range(10)]
            f = bm.faces.new(vs); bmesh.ops.extrude_face_region(bm, geom=[f]); [setattr(v.co, "z", .035) for v in f.verts]
            o = mesh_obj("starfish%d" % i, bm, star, c); o.location = (x, y, z + .005); o.rotation_euler = (0, 0, R.uniform(0, 6)); outline(o, .012)
        elif k < .48: _ball("shell%d" % i, R.uniform(.05, .1), (x, y, z + .02), shell, c, scale=(1, .8, .45), line=.01)
        elif k < .74: o = _ball("kelp%d" % i, R.uniform(.25, .6), (x, y, z + .02), kelp, c, scale=(1, .28, .07), line=.012, seed=i, rough=.25); o.rotation_euler = (0, 0, R.uniform(0, 3))
        else: _ball("pebble%d" % i, R.uniform(.06, .16), (x, y, z + .02), peb, c, scale=(1, .8, .55), line=.01, seed=i, rough=.12)

def far(c):
    """what closes the horizon: a headland with a striped lighthouse (its lamp lit), a sail far out"""
    hl = _ball("headland", 1.0, (150.0, 720.0, SEA_Z - 4), paint("headland", (.16, .42, .40), .8), c, scale=(190, 100, 46), line=0, seed=3, rough=.12)
    _ball("headland_cliff", 1.0, (120.0, 690.0, SEA_Z - 6), paint("headland_cliff", (.72, .52, .40), .8), c, scale=(150, 70, 22), line=0, seed=5, rough=.15)
    lh = _root("lighthouse", c, (118.0, 705.0, SEA_Z + 36.0))
    _cyl("lh_tower", 4.6, 30, (0, 0, 15), paint("lh_tower", WHITE, .5, stripes=(2, 10.0, RED)), c, parent=lh, r2=3.2, line=.7)
    _cyl("lh_gallery", 4.2, 1.2, (0, 0, 30.6), paint("lh_dark", NAVY, .5), c, parent=lh, line=.6); _cyl("lh_lamp", 2.4, 4.2, (0, 0, 33.3), paint("lh_lamp", (1.0, .86, .35), .4, emit=4.0), c, parent=lh, line=.5)
    _cyl("lh_roof", 3.2, 3.2, (0, 0, 37.0), paint("lh_roof", RED, .5), c, parent=lh, r2=.1, line=.6)
    sb = _root("sailboat", c, (-34.0, 235.0, SEA_Z)); _box("sb_hull", (9, 2.6, 1.3), (0, 0, .5), paint("sb_hull", WHITE, .5, band=(2, .1, RED)), c, parent=sb, line=.22, bevel=.3)
    _cyl("sb_mast", .12, 13, (.5, 0, 7.5), paint("sb_mast", WOOD, .5), c, parent=sb, line=.1, seg=8)
    for nm, pts in (("sb_main", ((.3, 0, 1.8), (-4.6, 0, 1.8), (.3, 0, 13.6))), ("sb_jib", ((.8, 0, 1.6), (4.6, 0, 1.6), (.8, 0, 12.0)))):
        bm = bmesh.new(); bm.faces.new([bm.verts.new(p) for p in pts]); o = mesh_obj(nm, bm, paint("sb_sail", (1.0, .97, .88), .8, emit=.25), c); o.parent = sb

def gull(c, at, yaw=0.0, z=None):
    """a seagull standing: white body, grey wing, yellow beak, two orange legs"""
    R = _root("gull", c, at if z is None else (at[0], at[1], z), yaw); wh = paint("gull_body", WHITE, .6); gr = paint("gull_wing", (.55, .60, .70), .6)
    _ball("gull_body", .13, (0, 0, .30), wh, c, scale=(1.5, .85, .9), parent=R, line=.008); _ball("gull_wing", .11, (-.04, 0, .33), gr, c, scale=(1.5, .95, .6), parent=R, line=.006)
    _ball("gull_head", .075, (.17, 0, .44), wh, c, parent=R, line=.006); _cyl("gull_beak", .022, .1, (.27, 0, .43), paint("gull_beak", (1.0, .70, .05), .4), c, rot=(0, math.radians(90), 0), parent=R, r2=.004, line=.004, seg=8)
    _ball("gull_eye", .012, (.215, .05, .46), paint("gull_eye", INK, .3), c, parent=R, line=0); _ball("gull_eye2", .012, (.215, -.05, .46), paint("gull_eye", INK, .3), c, parent=R, line=0)
    for s in (-1, 1): _cyl("gull_leg", .008, .2, (0, s * .04, .1), paint("gull_leg", ORANGE, .5), c, parent=R, line=.003, seg=6)
    return R

def castle(c, at):
    """a sand castle with a paper flag, a red bucket and a blue spade: somebody was playing here an hour ago"""
    R = _root("castle", c, at); sd = paint("castle_sand", (.90, .82, .68), .9)
    _cyl("castle_base", .42, .22, (0, 0, .11), sd, c, parent=R, r2=.36, line=.012, seg=16)
    for i, (x, y) in enumerate(((.26, .26), (-.26, .26), (.26, -.26), (-.26, -.26), (0, 0))):
        h = .5 if i == 4 else .34; _cyl("castle_tower%d" % i, .13 if i == 4 else .1, h, (x, y, .22 + h / 2 - .06), sd, c, parent=R, r2=.09 if i == 4 else .075, line=.01, seg=12)
    _cyl("flag_pole", .006, .3, (0, 0, .8), paint("flag_pole", WOOD, .5), c, parent=R, line=.003, seg=6); _box("flag", (.16, .004, .1), (.085, 0, .9), paint("flag_red", RED, .6), c, parent=R, line=.005, bevel=0)
    b = _root("bucket", c, (at[0] + .75, at[1] - .25), .3, (math.radians(72), 0)); _cyl("bucket_body", .13, .24, (0, 0, .12), paint("bucket_red", RED, .35), c, parent=b, r2=.16, line=.01, seg=16)
    s = _root("spade", c, (at[0] - .7, at[1] - .35), 1.1); _box("spade_blade", (.2, .14, .02), (0, 0, .02), paint("spade_blue", BLUE, .4), c, parent=s, line=.008); _cyl("spade_handle", .014, .34, (-.26, 0, .02), paint("spade_blue", BLUE, .4), c, rot=(0, math.radians(90), 0), parent=s, line=.006, seg=8)

def crate(c, at, yaw, word="FISH"):
    """a fish crate washed up, its word stencilled on the side"""
    R = _root("crate", c, at, yaw, (math.radians(7), 0)); _box("crate_body", (.9, .6, .45), (0, 0, .2), paint("crate_wood", (.74, .47, .22), .7, planks=(2, .15, .022)), c, parent=R, line=.014)
    cu = bpy.data.curves.new("crate_word", "FONT"); cu.body = word; cu.size = .2; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.extrude = .004
    o = bpy.data.objects.new("crate_word", cu); c.objects.link(o); cu.materials.append(paint("crate_ink", NAVY, .6)); o.parent = R; o.location = (0, -.305, .2); o.rotation_euler = (math.radians(90), 0, 0)

def fore(c):
    """the near sand of the low cameras (never an empty half picture)"""
    castle(c, (10.25, -3.6)); crate(c, (-.6, -8.4), .5); gull(c, (3.1, -7.6), 2.2); gull(c, (3.9, -7.1), 2.9); gull(c, (6.5, -9.6), .6); gull(c, (12.6, -6.9), 2.0)
    gull(c, (-10.4, 31.0), 1.2, SEA_Z + 1.32); gull(c, (-10.1, 26.5), -1.0, SEA_Z + 1.32)
    crab = _root("crab", c, (1.3, -9.6), .4); cr = paint("crab_red", RED, .4); _ball("crab_body", .09, (0, 0, .07), cr, c, scale=(1.3, 1, .55), parent=crab, line=.006)
    for s in (-1, 1):
        _ball("crab_claw", .04, (.1, s * .12, .08), cr, c, scale=(1.3, 1, .7), parent=crab, line=.004)
        for k in range(3): _cyl("crab_leg", .008, .12, (-.04 + k * .04, s * .13, .04), cr, c, rot=(math.radians(60) * s, 0, 0), parent=crab, line=.003, seg=6)

def wave(c, width=70.0, depth=11.0):
    """the wave that lays the whale on the sand: a sheet of clear turquoise water with a scalloped lip of white foam and lace behind it
    (not a white slab). Returns its root: the LIP is at the root's y; move the root."""
    R_ = bpy.data.objects.new("wave", None); c.objects.link(R_); R = random.Random(11); bm = bmesh.new(); n = 60; lip = []
    for i in range(n + 1):
        x = -width / 2 + width * i / n; f = -.9 * math.sin(i * .7) - .5 * math.sin(i * 1.9 + 1); lip.append((x, f)); a = bm.verts.new((x, f, 0)); b = bm.verts.new((x, depth, 0))
        if i: bm.faces.new((pa, a, b, pb))
        pa, pb = a, b
    m = bpy.data.materials.new("wave_water"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; bs = N["Principled BSDF"]; tc = N.new("ShaderNodeTexCoord")
    wv = N.new("ShaderNodeTexWave"); wv.bands_direction = "Y"; wv.inputs["Scale"].default_value = .9; wv.inputs["Distortion"].default_value = 7.0; wv.inputs["Detail"].default_value = 2.0; L.new(tc.outputs["Object"], wv.inputs["Vector"])
    colr = _mix(N, L, _m(N, L, "GREATER_THAN", wv.outputs["Fac"], .9), (.30, .90, .86), (1, 1, 1)); L.new(colr, bs.inputs["Base Color"]); L.new(colr, bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = .38; bs.inputs["Roughness"].default_value = .2
    o = mesh_obj("wave_sheet", bm, m, c); o.parent = R_; o.visible_shadow = False; fm = paint("wave_foam", (1, 1, 1), .5, emit=.75)
    for i, (x, f) in enumerate(lip):
        for k in range(2):
            b = _ball("wave_lip", R.uniform(.45, .8), (x + R.uniform(-.3, .3), f + k * R.uniform(.3, .7), .02), fm, c, scale=(1.15, .8, .16), parent=R_, line=0); b.visible_shadow = False
    return R_

def dress(c, clear=()):
    """the beach of shot 02 and of every beach shot: nothing empty (references: 10-20 readable things per picture)"""
    rowboat(c, (-11.5, 6.6), math.radians(68)); jetty(c); umbrella(c, (12.6, 6.0), .4); tackle(c, (8.6, 7.2)); litter(c, clear=clear); far(c); fore(c)

def ink_all(skip=("Card_", "Contact_")):
    if STYLE == "real": return
    """the ink line on everything the shot itself built or imported (props, vehicles, pieces): thickness follows the size of the object"""
    for o in list(col("L_OBJECTS").all_objects) + [o for o in bpy.data.objects if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name in ("blubber", "blast_sand", "blast_smoke")]:
        if o.type != "MESH" or o.name.startswith(skip) or o.modifiers.get("ink_line") or not o.data.polygons: continue
        if o.name.startswith("col") and o.data.materials and o.data.materials[0].name.startswith("blast_"): outline(o, .05); continue   # the blast column is drawn too
        if any(m and (m.name == "ink_line" or m.name.startswith(("ink_", "chalk", "sign_", "stink"))) for m in o.data.materials): continue
        s = max(1e-4, abs(o.matrix_world.to_scale().x)); outline(o, min(.03, max(.006, max(o.dimensions) * .01)) / s / 1.8)


# ------------------------------------------------------------------------------------------------------------ THE REAL WORLD (CB 2026-11-20)
def glass(o):
    """a real window: dark, mirror smooth, it reflects the sky"""
    for m in o.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
        if not b: continue
        for inp in ("Base Color", "Roughness", "Alpha"):
            for l in list(b.inputs[inp].links): m.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (.02, .035, .05, 1); b.inputs["Roughness"].default_value = .03; b.inputs["Alpha"].default_value = 1.0; b.inputs["Specular IOR Level"].default_value = 1.0
        b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = .0

def smoke_mat(name, rgb, density=.9, glow=.0):
    """real smoke for the blast: a volume, thick in the heart and torn at the edge, lit by the sun"""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear(); out = N.new("ShaderNodeOutputMaterial")
    v = N.new("ShaderNodeVolumePrincipled"); v.inputs["Color"].default_value = (*rgb, 1); v.inputs["Anisotropy"].default_value = .25; tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.4; nz.inputs["Detail"].default_value = 5; nz.inputs["Roughness"].default_value = .6; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    L.new(_m(N, L, "MULTIPLY", _m(N, L, "MULTIPLY_ADD", nz.outputs["Fac"], 3.2, -1.15, clamp=True), density), v.inputs["Density"]); L.new(v.outputs[0], out.inputs["Volume"])
    v.inputs["Emission Color"].default_value = (*rgb, 1); v.inputs["Emission Strength"].default_value = glow; return m                  # a little of its own light: thick smoke in full sun is bright, not black

def realist(scene, whale=None, sun=(95, 24)):
    """the photo beach kept (real sky, scanned sand, real water) and FINISHED: characters readable, glass that reflects, sun rays in a light
    sea haze, real smoke for the blast"""
    from rc import look
    for o in bpy.data.objects:
        if o.name.startswith("Card_"):
            for m in o.data.materials:
                for nd in (m.node_tree.nodes if m and m.use_nodes else ()):
                    if nd.type == "MIX_SHADER" and not nd.inputs[0].links: nd.inputs[0].default_value = max(nd.inputs[0].default_value, .72)
        if o.type == "MESH" and any(m and m.name == "Material.001" for m in o.data.materials) and o.name.startswith("Object_"): glass(o)
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name in ("blast_sand", "blast_smoke"):
            nm = o.data.materials[0].name; o.data.materials.clear(); o.data.materials.append(smoke_mat(nm + "_vol", (.92, .86, .74) if nm == "blast_sand" else (.40, .36, .34), 1.0 if nm == "blast_sand" else .9, .28 if nm == "blast_sand" else .08)); o.visible_shadow = True
    for o in [o for o in bpy.data.objects if o.name.startswith("blast_smoke") and o.type == "MESH"]: bpy.data.objects.remove(o)   # the effect's own puffs inside the column made a square of grain: the column IS the smoke
    # no haze VOLUME and no beam cards: at preview samples they render as grain (seen 2026-11-20); the haze is the mist pass and the sun rays are drawn by the compositor (kit.grade, Mo["sun_xy"])

def sun_rays(c, sun, n=9, seed=5, strength=.07):
    """SUN RAYS you can see on an open beach: broad soft slanted beams falling between the whale and the sea, along the sun's direction,
    additive light that fades along the beam and at its edges (the reference shows such beams in every daylight exterior)"""
    R = random.Random(seed); el, az = math.radians(sun[1]), math.radians(sun[0]); d = -Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    m = bpy.data.materials.new("sun_ray"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear(); out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sx.inputs[0])
    fade = _m(N, L, "MULTIPLY", _m(N, L, "SINE", _m(N, L, "MULTIPLY", sx.outputs["X"], math.pi)), _m(N, L, "SINE", _m(N, L, "MULTIPLY", sx.outputs["Y"], math.pi)))
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1, .93, .78, 1); L.new(_m(N, L, "MULTIPLY", _m(N, L, "POWER", fade, 1.6), strength), em.inputs["Strength"])
    tr = N.new("ShaderNodeBsdfTransparent"); add = N.new("ShaderNodeAddShader"); L.new(tr.outputs[0], add.inputs[0]); L.new(em.outputs[0], add.inputs[1]); L.new(add.outputs[0], out.inputs["Surface"])
    side = d.cross(Vector((0, 1, 0))); side = (side if side.length > .2 else d.cross(Vector((1, 0, 0)))).normalized()          # wide as seen from cameras that look toward the sea
    for i in range(n):
        p1 = Vector((R.uniform(-30, 34), R.uniform(3, 34), -1.0)); p0 = p1 - d * (R.uniform(28, 44) / max(.25, -d.z)); w0, w1 = R.uniform(.8, 1.8), R.uniform(2.2, 4.5)
        bm = bmesh.new(); uv = bm.loops.layers.uv.new(); f = bm.faces.new([bm.verts.new(v) for v in (p0 - side * w0, p0 + side * w0, p1 + side * w1, p1 - side * w1)])
        for lp, q in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uv].uv = q
        o = mesh_obj("sun_ray%d" % i, bm, m, c); o.visible_shadow = o.visible_glossy = o.visible_diffuse = False
