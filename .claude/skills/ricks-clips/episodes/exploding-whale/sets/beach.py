"""exploding-whale: the Oregon beach (plan/plan.json place "beach" + "dune_top"), one connected set built for every camera of the film.
Layout (metres): the whale lies at the origin along X on the damp sand; the sea is toward +Y (shoreline near y = 13); dry sand toward -Y;
the dunes rise from y = -14 to about 6 m at y = -45 (the crowd's "quarter mile" is staged there: a short-film distance, said by the
1/4 MILE marker); the car park is on the dune top around (24, -50).
Rules applied (docs/CORRECTIONS_CB_FR.md, references/style_analysis): scanned PBR sand without visible tiling + large patches, wet sand
darker and glossy near the water, real visible sky, ONE sun lamp, camera-side fill, dune grass that lets light through, real props.
    import beach; beach.build(scene, mood="grey")"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "blender")); sys.path.insert(0, os.path.join(SKILL, "demos", "crashed_car", "sets"))
from rc import look, geo, fetch  # noqa: E402
from rc.look import tex, col, mesh_obj, mat, srgb  # noqa: E402

SEA_Z = -0.30; SHORE_Y = 13.0
WHALE_GLTF = os.path.join(SKILL, "library", "assets", "sketchfab", "e09c5bd25d92467db1bf938fdb1e701f", "gltf", "scene.gltf")   # "cachalot whale", allthingsaurus, CC-BY 4.0
WHALE_LEN = 13.7                                                                           # 45 feet
MOODS = {   # sun azimuth (from), elevation, energy, sky HDRI, sky fill for lighting, sun glow, exposure, saturation
    "grey":  dict(az=-70, el=20, energy=3.6, hdri="kloppenheim_06_puresky", light=1.0, glow=0.0, exposure=-.25, sat=.92, sky=.75),   # heavy clouds with shape, never a white sheet      # the stink morning
    "noon":  dict(az=150, el=48, energy=9.0, hdri="kloofendal_48d_partly_cloudy_puresky", light=.55, glow=0.0, exposure=-.5, sat=1.08),  # the blast
    "gold":  dict(az=-115, el=14, energy=8.0, hdri="kloofendal_48d_partly_cloudy_puresky", light=.5, glow=.9, exposure=-.4, sat=1.05),   # late afternoon / dusk
    "today": dict(az=120, el=40, energy=8.0, hdri="kloofendal_48d_partly_cloudy_puresky", light=.7, glow=0.0, exposure=-.45, sat=1.1)}

def height(x, y):
    """ground height: gentle slope into the sea, dry beach, then dunes"""
    if y >= -14: return -0.0125 * (y + 11) + .02 * math.sin(x * .21 + y * .13)
    t = min(1.0, (-14 - y) / 30.0); t = t * t * (3 - 2 * t)
    return -0.0125 * (-14 + 11) + t * (5.4 + 1.6 * math.sin(x * .05 + 1) + .9 * math.sin(x * .13 + y * .07) + .5 * math.sin(y * .21))

def ground(c):
    bm = bmesh.new(); nx, ny = 240, 260; X0, X1, Y0, Y1 = -160.0, 160.0, -110.0, 40.0; V = []
    for j in range(ny + 1):
        y = Y0 + (Y1 - Y0) * (j / ny) ** 1.0; row = []
        for i in range(nx + 1):
            x = X0 + (X1 - X0) * i / nx; row.append(bm.verts.new((x, y, height(x, y))))
        V.append(row)
    for j in range(ny):
        for i in range(nx): bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    m = tex("beach_sand", "coast_sand_01", tile=3.0, recolor="#cdb892", value=1.0, normal=1.4, spec=.2, macro=.2)
    nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]; src = b.inputs["Base Color"].links[0].from_socket
    tc = [n for n in N if n.type == "TEX_COORD"][0]; sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sx.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .25; nz.inputs["Detail"].default_value = 3; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    def M(op, a, b_=None, c_=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for k, v in enumerate((a, b_, c_)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[k].default_value = v
            else: L.new(v, n.inputs[k])
        return n.outputs[0]
    # WET SAND: where the ground is low (near the water) the same sand is darker and glossy; the edge of the wet zone wanders (noise)
    zz = M("ADD", sx.outputs["Z"], M("MULTIPLY", M("SUBTRACT", nz.outputs["Fac"], .5), .10))
    wet0 = M("MULTIPLY_ADD", zz, -9.0, .1, clamp=True)                                    # 1 below z = -0.1, 0 above z = 0.01
    # the whale leaks: a dark damp halo around its body (ellipse along X) with a wandering edge
    ex = M("DIVIDE", sx.outputs["X"], WHALE_LEN * .62); ey = M("DIVIDE", sx.outputs["Y"], 3.4)
    rr = M("ADD", M("ADD", M("MULTIPLY", ex, ex), M("MULTIPLY", ey, ey)), M("MULTIPLY", M("SUBTRACT", nz.outputs["Fac"], .5), .5))
    wet = M("MAXIMUM", wet0, M("MULTIPLY_ADD", rr, -1.6, 1.9, clamp=True))
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; L.new(wet, mx.inputs[0]); L.new(src, mx.inputs[6]); mx.inputs[7].default_value = (.46, .43, .40, 1)
    L.new(mx.outputs[2], b.inputs["Base Color"])
    # WIND RIPPLES on the dry sand (fine bands across the wind) + small pits: a beach is never a smooth sheet
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.inputs["Scale"].default_value = 2.6; wv.inputs["Distortion"].default_value = 3.5; wv.inputs["Detail"].default_value = 2.0; wv.inputs["Detail Scale"].default_value = 1.2
    mpw = N.new("ShaderNodeMapping"); mpw.inputs["Rotation"].default_value = (0, 0, math.radians(18)); L.new(tc.outputs["Object"], mpw.inputs["Vector"]); L.new(mpw.outputs["Vector"], wv.inputs["Vector"])
    pit = N.new("ShaderNodeTexNoise"); pit.inputs["Scale"].default_value = 9.0; pit.inputs["Detail"].default_value = 4; L.new(tc.outputs["Object"], pit.inputs["Vector"])
    hgt = M("ADD", M("MULTIPLY", wv.outputs["Fac"], M("MULTIPLY_ADD", wet, -.8, 1.0)), M("MULTIPLY", pit.outputs["Fac"], .5))
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .55; bp.inputs["Distance"].default_value = .05; L.new(hgt, bp.inputs["Height"])
    if b.inputs["Normal"].links: L.new(b.inputs["Normal"].links[0].from_socket, bp.inputs["Normal"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    rsrc = b.inputs["Roughness"].links[0].from_socket if b.inputs["Roughness"].links else None
    rough = M("MULTIPLY", rsrc if rsrc else .8, M("MULTIPLY_ADD", wet, -.72, 1.0))
    L.new(rough, b.inputs["Roughness"]); L.new(M("MULTIPLY_ADD", wet, .35, .2), b.inputs["Specular IOR Level"])
    o = mesh_obj("beach_ground", bm, m, c, smooth=True); return o

def sea(c):
    """the ocean: glossy water reflecting the real sky, moving swell (bump animated with the frame), foam band along the shore"""
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((-400, SHORE_Y - 6, SEA_Z), (400, SHORE_Y - 6, SEA_Z), (400, 2500, SEA_Z), (-400, 2500, SEA_Z))]; bm.faces.new(vs)
    m = bpy.data.materials.new("sea"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); L.new(tc.outputs["Object"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (.06, .35, 1)
    d = mp.inputs["Location"].driver_add("default_value", 1).driver; d.expression = "-frame*0.012"   # the swell rolls toward the beach
    wv = N.new("ShaderNodeTexNoise"); wv.inputs["Scale"].default_value = 1.6; wv.inputs["Detail"].default_value = 5; wv.inputs["Distortion"].default_value = .6; L.new(mp.outputs["Vector"], wv.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .45; bp.inputs["Distance"].default_value = .6; L.new(wv.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sx.inputs[0])
    def M(op, a, b_=None, c_=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for k, v in enumerate((a, b_, c_)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[k].default_value = v
            else: L.new(v, n.inputs[k])
        return n.outputs[0]
    fn = N.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = .5; fn.inputs["Detail"].default_value = 4; L.new(mp.outputs["Vector"], fn.inputs["Vector"])
    dist = M("SUBTRACT", sx.outputs["Y"], SHORE_Y - 1.0)                                    # metres from the water's edge
    foam = M("MULTIPLY", M("MULTIPLY_ADD", dist, -.22, 1.0, clamp=True), M("MULTIPLY_ADD", fn.outputs["Fac"], 3.0, -.9, clamp=True))
    far = M("MULTIPLY", dist, .004, clamp=True)
    c1 = N.new("ShaderNodeMix"); c1.data_type = "RGBA"; L.new(far, c1.inputs[0]); c1.inputs[6].default_value = (*srgb("#3f7f86"), 1); c1.inputs[7].default_value = (*srgb("#1d4660"), 1)
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; L.new(foam, c2.inputs[0]); L.new(c1.outputs[2], c2.inputs[6]); c2.inputs[7].default_value = (.93, .95, .95, 1)
    L.new(c2.outputs[2], b.inputs["Base Color"]); L.new(M("MULTIPLY_ADD", foam, .5, .06), b.inputs["Roughness"]); b.inputs["Specular IOR Level"].default_value = .6
    return mesh_obj("sea", bm, m, c)

def whale(c, at=(0.0, 0.0), yaw=8.0, roll=16.0):
    """the hero: a real whale model, 45 feet, lying on its side in a groove of damp sand, wet glossy skin"""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=WHALE_GLTF); new = [o for o in bpy.data.objects if o not in before]
    for o in [o for o in new if o.type == "MESH" and not o.data.materials]:              # the model ships a stray untextured helper sphere
        new.remove(o); bpy.data.objects.remove(o)
    root = bpy.data.objects.new("whale", None); c.objects.link(root)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(v) for o in new if o.type == "MESH" for v in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    s = WHALE_LEN / max(mx - mn); cen = (mn + mx) / 2
    root.scale = (s,) * 3; root.rotation_euler = (0, math.radians(roll), math.radians(90 + yaw))    # the model lies along Y: roll about its long axis, then turn it along X
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); pts = []                                 # EVALUATED vertices: the model is skinned to an armature
    for o in new:
        if o.type != "MESH": continue
        eo = o.evaluated_get(dg); me = eo.to_mesh(); pts += [eo.matrix_world @ v.co for v in me.vertices]; eo.to_mesh_clear()
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2; cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    belly = min(p.z for p in pts if abs(p.x - cx) < WHALE_LEN * .2)                        # the BODY rests on the sand (flukes and fins hang lower in the file)
    root.location = (at[0] - cx, at[1] - cy, height(at[0], at[1]) - belly - .3)           # sunk 30 cm into the sand (its groove)
    for o in new:
        if o.type != "MESH": continue
        for sl in o.material_slots:
            b = sl.material.node_tree.nodes.get("Principled BSDF") if sl.material and sl.material.use_nodes else None
            if b:
                for inp in ("Roughness", "Metallic"):
                    for l in list(b.inputs[inp].links): sl.material.node_tree.links.remove(l)
                b.inputs["Metallic"].default_value = 0.0
                b.inputs["Roughness"].default_value = .72; b.inputs["Specular IOR Level"].default_value = .22; b.inputs["Coat Weight"].default_value = .06; b.inputs["Coat Roughness"].default_value = .35   # damp skin, not chrome
    return root

def _marram_tuft():
    """one tuft of marram grass: 46 thin curved blades (5 segments each), 0.35-0.8 m, dark at the root, pale straw at the tip"""
    if "marram_tuft" in bpy.data.collections: return bpy.data.collections["marram_tuft"]
    R = random.Random(11); bm = bmesh.new(); cl = bm.loops.layers.color.new("Col")
    for k in range(46):
        a = R.uniform(0, 6.28); r0 = R.uniform(0, .07); h = R.uniform(.35, .8); lean = R.uniform(.08, .42); w = R.uniform(.004, .008)
        d = Vector((math.cos(a), math.sin(a), 0)); n = Vector((-d.y, d.x, 0)); base = d * r0; prev = None
        for i in range(6):
            t = i / 5; p = base + d * lean * t * t * h + Vector((0, 0, h * (t - .18 * t * t))); ww = w * (1 - t * .9)
            cur = (bm.verts.new(p - n * ww), bm.verts.new(p + n * ww))
            if prev:
                f = bm.faces.new((prev[0], prev[1], cur[1], cur[0]))
                for lp in f.loops:
                    tt = lp.vert.co.z / h; lp[cl] = (tt, tt, tt, 1)
            prev = cur
    me = bpy.data.meshes.new("marram_tuft"); bm.to_mesh(me); bm.free()
    m = bpy.data.materials.new("marram"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"; cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*srgb("#4f5e2a"), 1); cr.color_ramp.elements[1].color = (*srgb("#d9d29a"), 1)
    nt.links.new(vc.outputs["Color"], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .6; b.inputs["Specular IOR Level"].default_value = .2
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent"); ms = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(cr.outputs[0], tl.inputs["Color"]); ms.inputs[0].default_value = .4   # lets the light through (PI-027)
    nt.links.new(b.outputs[0], ms.inputs[1]); nt.links.new(tl.outputs[0], ms.inputs[2]); nt.links.new(ms.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    me.materials.append(m); c = bpy.data.collections.new("marram_tuft"); c.objects.link(bpy.data.objects.new("marram_tuft", me)); return c

def dune_grass(c, n=90000, seed=3, clear=()):
    """marram grass on the dunes: thin pale blades in tufts, in drifts along the crests, none on the beach"""
    src = _marram_tuft(); R = random.Random(seed); P, Rt, Sc = [], [], []
    while len(P) < n:
        x = R.uniform(-110, 110); y = R.uniform(-100, -15); z = height(x, y)
        if any((x - cx) ** 2 + (y - cy) ** 2 < r * r for cx, cy, r in clear): continue          # trampled patches (where people stand)
        if z < .4 or R.random() > min(1.0, z / 3.5) * (.2 + .8 * max(0, math.sin(x * .3 + y * .2) * .6 + math.sin(x * .07 - y * .11) * .4 + .3)): continue
        P.append((x, y, z - .02)); Rt.append((R.uniform(-.15, .15), R.uniform(-.15, .15), R.uniform(0, 6.28))); Sc.append(R.uniform(1.0, 1.9))
    return geo.instancer("dune_grass", P, src, c, Rt, Sc, wind=.06)

def rocks_and_wood(c, seed=5):
    """black sea rocks in the surf and far along the beach, driftwood logs on the dry sand (scanned bark)"""
    R = random.Random(seed); rock = tex("sea_rock", "coast_sand_rocks_02", tile=2.0, recolor="#3b3d40", value=1.0, normal=2.0, spec=.4, macro=.15)
    for k in range(22):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        for v in bm.verts:
            v.co *= 1 + .28 * math.sin(v.co.x * 3.1 + k) * math.cos(v.co.y * 2.7 + k * 2) + .12 * math.sin(v.co.z * 7 + k)
        far = k >= 8; x = R.uniform(-140, 140) if far else R.choice((-1, 1)) * R.uniform(22, 70); y = R.uniform(16, 60) if far else R.uniform(9, 20)
        o = mesh_obj("rock%d" % k, bm, rock, c, smooth=True); sc = R.uniform(1.2, 4.5) if far else R.uniform(.5, 1.8)
        o.scale = (sc * R.uniform(.8, 1.5), sc * R.uniform(.8, 1.3), sc * R.uniform(.5, .9)); o.location = (x, y, height(x, y) - .2 * sc if y < SHORE_Y else SEA_Z - .25 * sc); o.rotation_euler = (0, 0, R.uniform(0, 6.28))
    wood = tex("driftwood", "bark_brown_02", tile=.8, recolor="#b9ab98", value=1.0, normal=1.6, spec=.15, macro=.12)
    for k in range(9):
        L_ = R.uniform(2.0, 5.5); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=R.uniform(.12, .28), radius2=R.uniform(.06, .14), depth=L_)
        for v in bm.verts: v.co.x += .08 * math.sin(v.co.z * 2.2 + k); v.co.y += .06 * math.cos(v.co.z * 1.7 + k)
        x = R.uniform(-45, 45); y = R.uniform(-13, -5)
        o = mesh_obj("driftwood%d" % k, bm, wood, c, smooth=True); o.rotation_euler = (math.radians(90), 0, R.uniform(0, 3.14)); o.location = (x, y, height(x, y) + .12)

def traces(c, seed=9):
    """WHAT HAPPENED HERE stays written in the sand: the berm pushed up around the whale, footprints from the dunes to it, the truck's tracks"""
    R = random.Random(seed); sand = bpy.data.materials["beach_sand"]
    bm = bmesh.new(); n = 72; rings = []                                                   # berm: a low ridge of pushed sand around the body
    for k in range(n):
        t = 2 * math.pi * k / n; cx, cy = math.cos(t) * WHALE_LEN * .56, math.sin(t) * 2.5; w = .55 + .2 * math.sin(k * 1.7); hgt = .16 + .09 * math.sin(k * 2.3 + 1)
        d = Vector((math.cos(t) * 2.5, math.sin(t) * WHALE_LEN * .56, 0)).normalized()
        ring = [bm.verts.new((cx + d.x * o_, cy + d.y * o_, height(cx, cy) + z_)) for o_, z_ in ((-w, -.02), (-w * .3, hgt * .8), (0, hgt), (w * .5, hgt * .5), (w, -.02))]
        rings.append(ring)
    for k in range(n):
        a_, b_ = rings[k], rings[(k + 1) % n]
        for i in range(4): bm.faces.new((a_[i], a_[i + 1], b_[i + 1], b_[i]))
    mesh_obj("whale_berm", bm, sand, c, smooth=True)
    dark = bpy.data.materials.get("sand_print")
    if not dark:
        dark = tex("sand_print", "coast_sand_01", tile=3.0, recolor="#9a8a6c", value=1.0, normal=1.4, spec=.15, macro=.1)
    bm = bmesh.new()
    def foot(x, y, yaw, L_=.27, W_=.1):
        c_, s_ = math.cos(yaw), math.sin(yaw); z = height(x, y) + .006; vs = []
        for k in range(12):
            t = 2 * math.pi * k / 12; lx, ly = math.cos(t) * L_ / 2 * (1.0 if math.cos(t) > 0 else .8), math.sin(t) * W_ / 2 * (1 + .25 * math.cos(t))
            vs.append(bm.verts.new((x + lx * c_ - ly * s_, y + lx * s_ + ly * c_, z)))
        bm.faces.new(vs)
    for path in range(9):                                                                  # walkers came down from the dunes to look, and went back
        x0 = R.uniform(-28, 30); y0 = -16.0; x1 = R.uniform(-7, 7); y1 = R.uniform(-4.5, -3.0); steps = int(math.hypot(x1 - x0, y1 - y0) / .7)
        for i in range(steps):
            t = i / steps; x = x0 + (x1 - x0) * t + .25 * math.sin(i * .4 + path); y = y0 + (y1 - y0) * t; yaw = math.atan2(y1 - y0, x1 - x0) + R.uniform(-.15, .15)
            side = (-1) ** i * .11; foot(x - math.sin(yaw) * side, y + math.cos(yaw) * side, yaw)
    for side in (-.85, .85):                                                               # the highway truck's two wheel tracks, with tread blocks
        for i in range(160):
            t = i / 160; x = 34 - 30 * t; y = -15 + 10 * t * t + side; yaw = math.atan2(20 * t, -30)
            if i % 2 == 0: foot(x, y, yaw, L_=.22, W_=.26)
    mesh_obj("sand_prints", bm, dark, c)

def light(scene, mood="grey", az=None, el=None):
    Mo = dict(MOODS[mood]); Mo["az"] = Mo["az"] if az is None else az; Mo["el"] = Mo["el"] if el is None else el   # the sun is placed per view (lesson PI-030)
    look.SUN[0], look.SUN[1] = Mo["az"], Mo["el"]
    look.sky_hdri(scene, strength=Mo.get("sky", 1.0), hdri=Mo["hdri"], glow=Mo["glow"], light=Mo["light"] / Mo.get("sky", 1.0)); look.sun(scene, energy=Mo["energy"])
    look.bounce_fill(col("L_SET"), at=(-8.0, -22.0, 14.0), aim=(0, 0, 1.5), energy=2500.0, size=22.0)   # high and wide: no visible pool of light on the sand
    return Mo

def build(scene, mood="grey", az=None, el=None, clear=()):
    c = col("L_SET"); Mo = light(scene, mood, az, el); ground(c); sea(c); w = whale(col("L_OBJECTS")); traces(c); dune_grass(c, clear=clear); rocks_and_wood(c)
    return c, w, Mo
