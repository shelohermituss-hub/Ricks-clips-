"""Semi-realistic "modern game cinematic" look for Cycles: colours, shaders and lights ONLY (CB brief, 20/11).
No geometry and no camera of the scene is changed. Fully idempotent: run it again, nothing is duplicated.

    blender -b scene.blend --python fortnite_cycles_look.py -- [--center x,y,z] [--mute-existing-lights]
            [--skip-prefix Card_,Sign_] [--samples 128] [--sky-gain 0.05] [--save out.blend]
    or paste it in Blender's text editor and press Run (all defaults).

Written for Blender 4.2 -> 5.x. Version differences handled here:
  * sky: 'NISHITA' no longer exists in 5.x -> 'MULTIPLE_SCATTERING' (same model); dust_density -> aerosol_density
  * look names: 'AgX - Medium High Contrast' (4.x) / 'Medium High Contrast' (5.x)
  * compositor: scene.node_tree + Composite node (4.x) / scene.compositing_node_group + Group Output (5.x);
    Glare / Color Balance / Lens Distortion settings are node properties in 4.x and input sockets in 5.x
"""
import bpy, math, sys
from mathutils import Vector

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def opt(k, d=None): return ARGV[ARGV.index(k) + 1] if k in ARGV else d
CENTER = Vector([float(v) for v in opt("--center", "0,0,1").split(",")])
MUTE_EXISTING = "--mute-existing-lights" in ARGV
SKIP_PREFIX = tuple(p for p in opt("--skip-prefix", "").split(",") if p)
SAMPLES = int(opt("--samples", "128"))
# Calibration, measured 20/11 in Blender 5.2: the physical sky at Background strength 1.0 is about 20 times too bright for a sun of 4.8
# (everything burns to white: image luma .86, saturation .06). The sky colour is scaled BEFORE the Background nodes, whose strength stays 1.0.
# Use --sky-gain 1.0 to get the raw brief.
SKY_GAIN = float(opt("--sky-gain", "0.05"))

SUN_EL, SUN_ROT = math.radians(38), math.radians(-45)
COL = "FORTNITE_CYCLES_LIGHTING"; NG = "NG_Fortnite_Cycles_PBR"; PBR_NODE = "FORTNITE_PBR"
ORGANIC = ("leaf", "leaves", "tree", "grass", "bush", "plant", "skin", "face", "foliage", "feuille", "herbe", "peau")
NOTES = []

# ---------------------------------------------------------------- small helpers
def first_ok(obj, attr, values):
    """Set obj.attr to the first accepted value; return it (None when none is accepted)."""
    for v in values:
        try: setattr(obj, attr, v); return v
        except Exception: pass
    NOTES.append("%s: none of %s accepted" % (attr, list(values))); return None

def sock(node, name, kind=None, out=False):
    """Socket by name (and type when two sockets share a name, as in Blender 5 compositor nodes)."""
    for s in (node.outputs if out else node.inputs):
        if s.name == name and (kind is None or s.type == kind) and s.enabled: return s
    for s in (node.outputs if out else node.inputs):
        if s.name == name and (kind is None or s.type == kind): return s
    return None

def set_in(node, name, value, kind=None):
    s = sock(node, name, kind)
    if s is None: return False
    try: s.default_value = value; return True
    except Exception: return False

def set_menu(node, name, candidates):
    s = sock(node, name, "MENU")
    if s is None: return False
    for c in candidates:
        try: s.default_value = c; return True
        except Exception: pass
    NOTES.append("%s.%s: menu value not accepted %s" % (node.bl_idname, name, list(candidates))); return False

def node(nt, idname, name, **props):
    n = nt.nodes.get(name) or nt.nodes.new(idname); n.name = n.label = name
    for k, v in props.items():
        if hasattr(n, k):
            try: setattr(n, k, v)
            except Exception as e: NOTES.append("%s.%s: %s" % (idname, k, e))
    return n

def ramp(n, p0, p1, c0=(0, 0, 0, 1), c1=(1, 1, 1, 1)):
    e = n.color_ramp.elements
    while len(e) > 2: e.remove(e[-1])
    e[0].position, e[0].color, e[1].position, e[1].color = p0, c0, p1, c1; return n

def mix_rgb(nt, name, blend, fac=None):
    n = node(nt, "ShaderNodeMix", name, data_type="RGBA", blend_type=blend, clamp_result=False, clamp_factor=True)
    if fac is not None: n.inputs[0].default_value = fac
    return n
A, B, RES = 6, 7, 2            # ShaderNodeMix: colour sockets A / B, colour result

# ---------------------------------------------------------------- 1. render + colour management
def setup_render(sc):
    sc.render.engine = "CYCLES"; c = sc.cycles; device = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
            try:
                prefs.compute_device_type = kind; prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == kind]
                if gpus:
                    for d in prefs.devices: d.use = d.type == kind
                    device = kind; break
            except Exception: continue
        if device == "CPU":
            try: prefs.compute_device_type = "NONE"
            except Exception: pass
    except Exception as e: NOTES.append("GPU lookup: %s" % e)
    c.device = "GPU" if device != "CPU" else "CPU"
    c.use_denoising = True; first_ok(c, "denoiser", ("OPENIMAGEDENOISE",)); first_ok(c, "denoising_input_passes", ("RGB_ALBEDO_NORMAL",))
    c.samples, c.preview_samples, c.use_adaptive_sampling, c.adaptive_threshold = SAMPLES, 32, True, .02
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces, c.volume_bounces, c.transparent_max_bounces = 8, 3, 4, 6, 2, 8
    c.sample_clamp_direct, c.sample_clamp_indirect = 10.0, 5.0
    first_ok(sc.display_settings, "display_device", ("sRGB",)); vs = sc.view_settings
    vt = first_ok(vs, "view_transform", ("AgX", "Filmic")); lk = first_ok(vs, "look", ("AgX - Medium High Contrast", "Medium High Contrast"))
    act = getattr(getattr(sc, "animation_data", None), "action", None)        # an animated exposure would override the value below
    bags = [act] if act and hasattr(act, "fcurves") else []
    for layer in getattr(act, "layers", []) if act else []:
        for strip in layer.strips: bags += list(getattr(strip, "channelbags", []))
    for bag in bags:
        for f in [f for f in bag.fcurves if f.data_path == "view_settings.exposure"]:
            bag.fcurves.remove(f); NOTES.append("exposure animation removed (fixed 0.25 asked)")
    vs.exposure, vs.gamma = .25, 1.0
    return device, vt, lk

# ---------------------------------------------------------------- 2. world, lights, atmosphere
def sun_dir():      # measured in Blender 5.2: rotation 0 = +Y, positive turns towards +X
    return Vector((math.sin(SUN_ROT) * math.cos(SUN_EL), math.cos(SUN_ROT) * math.cos(SUN_EL), math.sin(SUN_EL)))

def setup_world(sc):
    w = bpy.data.worlds.get("FORTNITE_WORLD") or bpy.data.worlds.new("FORTNITE_WORLD")
    if sc.world and sc.world != w: sc["fortnite_previous_world"] = sc.world.name; sc.world.use_fake_user = True
    sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    nt = w.node_tree
    for n in list(nt.nodes):
        if not n.name.startswith("FN_"): nt.nodes.remove(n)
    sky = node(nt, "ShaderNodeTexSky", "FN_SKY"); kind = first_ok(sky, "sky_type", ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING"))
    sky.sun_disc = False; sky.sun_elevation, sky.sun_rotation, sky.air_density, sky.ozone_density = SUN_EL, SUN_ROT, 1.3, 1.9
    first_ok(sky, "dust_density", (.85,)) if hasattr(sky, "dust_density") else first_ok(sky, "aerosol_density", (.85,))
    cal = node(nt, "ShaderNodeVectorMath", "FN_SKY_CALIBRATION", operation="SCALE"); set_in(cal, "Scale", SKY_GAIN)
    hsv = node(nt, "ShaderNodeHueSaturation", "FN_SKY_VIVID"); hsv.inputs["Saturation"].default_value, hsv.inputs["Value"].default_value = 1.22, 1.05
    bg_cam = node(nt, "ShaderNodeBackground", "FN_BG_CAMERA"); bg_cam.inputs["Strength"].default_value = 1.0
    bg_sky = node(nt, "ShaderNodeBackground", "FN_BG_SKY_INDIRECT"); bg_sky.inputs["Strength"].default_value = 1.0
    bg_blue = node(nt, "ShaderNodeBackground", "FN_BG_SHADOW_TINT"); bg_blue.inputs["Color"].default_value = (.06, .11, .28, 1); bg_blue.inputs["Strength"].default_value = .95
    mix_ind = node(nt, "ShaderNodeMixShader", "FN_MIX_INDIRECT"); mix_ind.inputs[0].default_value = .5
    lp = node(nt, "ShaderNodeLightPath", "FN_LIGHT_PATH"); mix = node(nt, "ShaderNodeMixShader", "FN_MIX_CAMERA"); out = node(nt, "ShaderNodeOutputWorld", "FN_OUT")
    L = nt.links.new
    L(sky.outputs[0], cal.inputs[0]); L(cal.outputs[0], hsv.inputs["Color"]); L(hsv.outputs[0], bg_cam.inputs["Color"]); L(cal.outputs[0], bg_sky.inputs["Color"])
    L(bg_sky.outputs[0], mix_ind.inputs[1]); L(bg_blue.outputs[0], mix_ind.inputs[2])
    L(lp.outputs["Is Camera Ray"], mix.inputs[0]); L(mix_ind.outputs[0], mix.inputs[1]); L(bg_cam.outputs[0], mix.inputs[2]); L(mix.outputs[0], out.inputs["Surface"])
    for i, n in enumerate((sky, cal, hsv, bg_cam, bg_sky, bg_blue, mix_ind, lp, mix, out)): n.location = (i * 190, -80 * (i % 3))
    return kind

def light(col, name, kind, **props):
    ob = bpy.data.objects.get(name)
    if ob is None or ob.type != "LIGHT": ob = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
    if ob.data.type != kind: ob.data.type = kind
    for c in list(ob.users_collection):
        if c != col: c.objects.unlink(ob)
    if ob.name not in col.objects: col.objects.link(ob)
    for k, v in props.items(): setattr(ob.data, k, v)
    return ob

def aim(ob, pos, target):
    ob.location = pos; ob.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()

def setup_lights(sc):
    col = bpy.data.collections.get(COL) or bpy.data.collections.new(COL)
    if col.name not in sc.collection.children: sc.collection.children.link(col)
    if MUTE_EXISTING:
        muted = [o.name for o in sc.objects if o.type == "LIGHT" and col not in o.users_collection and not o.hide_render]
        for n in muted: sc.objects[n].hide_render = True
        if muted: sc["fortnite_muted_lights"] = ", ".join(sorted((set(str(sc.get("fortnite_muted_lights", "")).split(", ")) | set(muted)) - {""}))
    d = sun_dir(); flat = Vector((d.x, d.y, 0)).normalized(); side = Vector((flat.y, -flat.x, 0))
    sun = light(col, "FORTNITE_SUN", "SUN", energy=4.8, angle=math.radians(2.0), color=(1.0, .94, .82)); aim(sun, CENTER + d * 30, CENTER)
    rim = light(col, "FORTNITE_RIM_LIGHT", "AREA", shape="RECTANGLE", size=6.0, size_y=6.0, color=(.35, .82, 1.0), energy=1400.0)
    aim(rim, CENTER - flat * 9 + Vector((0, 0, 3.5)), CENTER)
    fill = light(col, "FORTNITE_FILL_LIGHT", "AREA", shape="DISK", size=8.0, color=(.55, .75, 1.0), energy=350.0)
    aim(fill, CENTER + side * 9 + Vector((0, 0, 3.0)), CENTER)
    # atmosphere: one wire cube with a Principled Volume
    mat = bpy.data.materials.get("FORTNITE_ATMO_MAT") or bpy.data.materials.new("FORTNITE_ATMO_MAT")
    try: mat.use_nodes = True
    except Exception: pass
    nt = mat.node_tree
    for n in list(nt.nodes):
        if not n.name.startswith("FN_"): nt.nodes.remove(n)
    vol = node(nt, "ShaderNodeVolumePrincipled", "FN_VOLUME"); out = node(nt, "ShaderNodeOutputMaterial", "FN_OUT"); out.location = (260, 0)
    vol.inputs["Color"].default_value = (.58, .76, 1.0, 1); vol.inputs["Density"].default_value = .0018; vol.inputs["Anisotropy"].default_value = .65
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    ob = bpy.data.objects.get("FORTNITE_ATMO_VOLUME")
    if ob is None:
        me = bpy.data.meshes.new("FORTNITE_ATMO_VOLUME"); v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        me.from_pydata(v, [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]); me.update()
        ob = bpy.data.objects.new("FORTNITE_ATMO_VOLUME", me); col.objects.link(ob)
    ob.location, ob.scale, ob.display_type = (0, 0, 10), (60, 60, 35), "WIRE"
    if not ob.data.materials: ob.data.materials.append(mat)
    else: ob.data.materials[0] = mat
    return [sun, rim, fill]

# ---------------------------------------------------------------- 3. stylised PBR node group
def iface(tree, name, in_out, kind, default=None):
    for it in tree.interface.items_tree:
        if it.item_type == "SOCKET" and it.name == name and it.in_out == in_out: s = it; break
    else: s = tree.interface.new_socket(name=name, in_out=in_out, socket_type=kind)
    if default is not None:
        try: s.default_value = default
        except Exception: pass
    return s

def build_group():
    g = bpy.data.node_groups.get(NG) or bpy.data.node_groups.new(NG, "ShaderNodeTree")
    iface(g, "Base Color", "INPUT", "NodeSocketColor", (.8, .8, .8, 1)); iface(g, "Metallic", "INPUT", "NodeSocketFloat", 0.0)
    iface(g, "Roughness", "INPUT", "NodeSocketFloat", .5); iface(g, "Normal", "INPUT", "NodeSocketVector")
    iface(g, "Base Color", "OUTPUT", "NodeSocketColor"); iface(g, "Roughness", "OUTPUT", "NodeSocketFloat"); iface(g, "Normal", "OUTPUT", "NodeSocketVector")
    g.nodes.clear(); L = g.links.new                     # rebuilt on every run: same result, no duplicate
    gi = node(g, "NodeGroupInput", "IN"); go = node(g, "NodeGroupOutput", "OUT"); tc = node(g, "ShaderNodeTexCoord", "COORD"); geo = node(g, "ShaderNodeNewGeometry", "GEO")
    # 1. hand-painted variation
    noise = node(g, "ShaderNodeTexNoise", "PAINT_NOISE"); set_in(noise, "Scale", 12.0); set_in(noise, "Detail", 4.0); set_in(noise, "Roughness", .65)
    nr = ramp(node(g, "ShaderNodeValToRGB", "PAINT_RAMP"), .35, .65); m1 = mix_rgb(g, "1_PAINT_OVERLAY", "OVERLAY", .08)
    L(tc.outputs["Object"], noise.inputs["Vector"]); L(sock(noise, "Factor", out=True) or noise.outputs[0], nr.inputs[0]); L(gi.outputs["Base Color"], m1.inputs[A]); L(nr.outputs[0], m1.inputs[B])
    # 2. coloured ambient occlusion
    ao = node(g, "ShaderNodeAmbientOcclusion", "AO", samples=8); set_in(ao, "Distance", .35)
    ar = ramp(node(g, "ShaderNodeValToRGB", "AO_RAMP"), .2, .85, (1, 1, 1, 1), (0, 0, 0, 1))          # 1 in the hollows
    af = node(g, "ShaderNodeMath", "AO_FAC", operation="MULTIPLY"); af.inputs[1].default_value = .30
    m2 = mix_rgb(g, "2_AO_TINT", "MULTIPLY"); m2.inputs[B].default_value = (.14, .18, .38, 1)
    L(ao.outputs["AO"], ar.inputs[0]); L(ar.outputs[0], af.inputs[0]); L(af.outputs[0], m2.inputs[0]); L(m1.outputs[RES], m2.inputs[A])
    # 3. vertical gradient
    sep = node(g, "ShaderNodeSeparateXYZ", "Z"); zr = ramp(node(g, "ShaderNodeValToRGB", "Z_RAMP"), 0.0, 1.0)
    inv = node(g, "ShaderNodeMath", "Z_LOW", operation="SUBTRACT"); inv.inputs[0].default_value = 1.0
    f_lo = node(g, "ShaderNodeMath", "Z_LOW_FAC", operation="MULTIPLY"); f_lo.inputs[1].default_value = .18
    f_hi = node(g, "ShaderNodeMath", "Z_TOP_FAC", operation="MULTIPLY"); f_hi.inputs[1].default_value = .10
    m3 = mix_rgb(g, "3_BASE_DARKEN", "MULTIPLY"); m3.inputs[B].default_value = (.16, .22, .42, 1)
    m4 = mix_rgb(g, "3_TOP_WARM", "SCREEN"); m4.inputs[B].default_value = (1.0, .96, .88, 1)
    L(tc.outputs["Generated"], sep.inputs[0]); L(sep.outputs["Z"], zr.inputs[0]); L(zr.outputs[0], inv.inputs[1]); L(inv.outputs[0], f_lo.inputs[0]); L(zr.outputs[0], f_hi.inputs[0])
    L(f_lo.outputs[0], m3.inputs[0]); L(m2.outputs[RES], m3.inputs[A]); L(f_hi.outputs[0], m4.inputs[0]); L(m3.outputs[RES], m4.inputs[A])
    # 4. edge highlight
    er = ramp(node(g, "ShaderNodeValToRGB", "EDGE_RAMP"), .52, .61); m5 = mix_rgb(g, "4_EDGE_SCREEN", "SCREEN", .22)
    L(geo.outputs["Pointiness"], er.inputs[0]); L(m4.outputs[RES], m5.inputs[A]); L(er.outputs[0], m5.inputs[B])
    # 5. vibrance + safe range
    hsv = node(g, "ShaderNodeHueSaturation", "5_VIBRANCE"); hsv.inputs["Saturation"].default_value, hsv.inputs["Value"].default_value = 1.18, 1.02
    lo = node(g, "ShaderNodeVectorMath", "5_MIN_004", operation="MAXIMUM"); lo.inputs[1].default_value = (.04, .04, .04)
    hi = node(g, "ShaderNodeVectorMath", "5_MAX_086", operation="MINIMUM"); hi.inputs[1].default_value = (.86, .86, .86)
    L(m5.outputs[RES], hsv.inputs["Color"]); L(hsv.outputs[0], lo.inputs[0]); L(lo.outputs[0], hi.inputs[0]); L(hi.outputs[0], go.inputs["Base Color"])
    # 6. roughness: non-metal .38-.70, metal .20-.42, mixed by Metallic
    r_d = node(g, "ShaderNodeMapRange", "6_ROUGH_NONMETAL"); r_m = node(g, "ShaderNodeMapRange", "6_ROUGH_METAL")
    for n, a, b in ((r_d, .38, .70), (r_m, .20, .42)): n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = a, b; L(gi.outputs["Roughness"], n.inputs["Value"])
    rmix = node(g, "ShaderNodeMix", "6_ROUGH_MIX", data_type="FLOAT", clamp_factor=True)
    L(gi.outputs["Metallic"], rmix.inputs[0]); L(r_d.outputs[0], rmix.inputs[2]); L(r_m.outputs[0], rmix.inputs[3]); L(rmix.outputs[0], go.inputs["Roughness"])
    # 7. normal: 45 % of the detail normal over the geometry normal
    nmix = node(g, "ShaderNodeMix", "7_NORMAL_MIX", data_type="VECTOR", clamp_factor=True); nmix.inputs[0].default_value = .45
    nn = node(g, "ShaderNodeVectorMath", "7_NORMALIZE", operation="NORMALIZE")
    L(geo.outputs["Normal"], nmix.inputs[4]); L(gi.outputs["Normal"], nmix.inputs[5]); L(nmix.outputs[1], nn.inputs[0]); L(nn.outputs[0], go.inputs["Normal"])
    for i, n in enumerate(g.nodes): n.location = (190 * (i % 9), -230 * (i // 9))
    return g

def from_socket(nt, group_in, bsdf_in):
    """Feed a group input with what the BSDF input had: its link, or its value."""
    if bsdf_in.is_linked: nt.links.new(bsdf_in.links[0].from_socket, group_in)
    else:
        try: group_in.default_value = bsdf_in.default_value
        except Exception: pass

def convert_materials(g):
    done, already, skipped = [], [], []
    for m in bpy.data.materials:
        nt = m.node_tree
        if nt is None or m.name.startswith("FORTNITE_"): continue
        bsdfs = [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"]
        if not bsdfs: skipped.append((m.name, "no Principled BSDF")); continue
        if SKIP_PREFIX and m.name.startswith(SKIP_PREFIX): skipped.append((m.name, "skip prefix")); continue
        changed = False
        for b in bsdfs:
            em, tr = b.inputs.get("Emission Strength"), b.inputs.get("Transmission Weight") or b.inputs.get("Transmission")
            if em is not None and not em.is_linked and em.default_value > 1.0: skipped.append((m.name, "emissive")); continue
            if tr is not None and not tr.is_linked and tr.default_value > .5: skipped.append((m.name, "glass")); continue
            bc = b.inputs["Base Color"]
            if bc.is_linked and bc.links[0].from_node.bl_idname == "ShaderNodeGroup" and bc.links[0].from_node.node_tree == g:
                already.append(m.name)
            else:
                gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = g; gn.name = gn.label = PBR_NODE; gn.location = (b.location.x - 240, b.location.y)
                had_normal = b.inputs["Normal"].is_linked
                for k in ("Base Color", "Metallic", "Roughness", "Normal"): from_socket(nt, gn.inputs[k], b.inputs[k])
                nt.links.new(gn.outputs["Base Color"], bc); nt.links.new(gn.outputs["Roughness"], b.inputs["Roughness"])
                if had_normal: nt.links.new(gn.outputs["Normal"], b.inputs["Normal"])     # no detail normal -> the BSDF keeps the true surface normal
                changed = True
            if any(k in m.name.lower() for k in ORGANIC):
                set_in(b, "Subsurface Weight", .25) or set_in(b, "Subsurface", .25); set_in(b, "Subsurface Scale", .05)
        if changed: done.append(m.name)
    return done, sorted(set(already) - set(done)), skipped

# ---------------------------------------------------------------- 4. compositing
def setup_compositor(sc):
    new_api = hasattr(sc, "compositing_node_group")
    if new_api:
        tree = sc.compositing_node_group
        if tree is None:
            tree = bpy.data.node_groups.new("FORTNITE_COMPOSITE", "CompositorNodeTree"); sc.compositing_node_group = tree
        iface(tree, "Image", "OUTPUT", "NodeSocketColor")
        out = next((n for n in tree.nodes if n.bl_idname == "NodeGroupOutput"), None) or tree.nodes.new("NodeGroupOutput")
    else:
        sc.use_nodes = True; tree = sc.node_tree
        out = next((n for n in tree.nodes if n.bl_idname == "CompositorNodeComposite"), None) or tree.nodes.new("CompositorNodeComposite")
    out_in = out.inputs[0]; names = ("FN_GLARE", "FN_COLOR_BALANCE", "FN_LENS")
    # what currently feeds the output (ignoring our own chain)
    src = out_in.links[0].from_socket if out_in.is_linked else None
    while src is not None and src.node.name in names:
        i = src.node.inputs[0]; src = i.links[0].from_socket if i.is_linked else None
    if src is None:
        rl = next((n for n in tree.nodes if n.bl_idname == "CompositorNodeRLayers"), None) or tree.nodes.new("CompositorNodeRLayers")
        try: rl.scene = sc
        except Exception: pass
        src = rl.outputs[0]
    gl = node(tree, "CompositorNodeGlare", names[0]); cb = node(tree, "CompositorNodeColorBalance", names[1]); ld = node(tree, "CompositorNodeLensdist", names[2])
    if hasattr(gl, "glare_type") and not sock(gl, "Type", "MENU"):                         # Blender <= 4.3: properties
        gl.glare_type, gl.quality, gl.threshold, gl.size, gl.mix = "FOG_GLOW", "HIGH", 1.1, 7, -.65
    else:                                                                                  # 4.4+ / 5.x: sockets. mix -0.65 = 35 % of glare; size 7 = 2^(7-9)
        set_menu(gl, "Type", ("Fog Glow", "FOG_GLOW")); set_menu(gl, "Quality", ("High", "HIGH")); set_in(gl, "Threshold", 1.1); set_in(gl, "Strength", .35); set_in(gl, "Size", .25)
    lift, gamma, gain = (.97, .99, 1.03, 1), (1.01, 1.00, .99, 1), (1.03, 1.01, .96, 1)
    if hasattr(cb, "correction_method") and not sock(cb, "Type", "MENU"):
        cb.correction_method = "LIFT_GAMMA_GAIN"; cb.lift, cb.gamma, cb.gain = lift[:3], gamma[:3], gain[:3]
    else:
        set_menu(cb, "Type", ("Lift/Gamma/Gain", "LIFT_GAMMA_GAIN")); set_in(cb, "Lift", lift, "RGBA"); set_in(cb, "Gamma", gamma, "RGBA"); set_in(cb, "Gain", gain, "RGBA")
    set_menu(ld, "Type", ("Radial", "RADIAL")); set_in(ld, "Dispersion", .003) or set_in(ld, "Dispersion", .003, "VALUE"); set_in(ld, "Distortion", 0.0)
    L = tree.links.new
    L(src, gl.inputs[0]); L(gl.outputs[0], cb.inputs[sock(cb, "Image").identifier]); L(cb.outputs[0], ld.inputs[0]); L(ld.outputs[0], out_in)
    x = out.location.x
    for i, n in enumerate((gl, cb, ld)): n.location = (x - 220 * (3 - i), out.location.y + 260)
    return tree.name

# ---------------------------------------------------------------- run
def main():
    sc = bpy.context.scene
    device, vt, lk = setup_render(sc); sky = setup_world(sc); lights = setup_lights(sc)
    g = build_group(); done, already, skipped = convert_materials(g); comp = setup_compositor(sc)
    print("\n================ FORTNITE CYCLES LOOK ================")
    print("Blender %s | Cycles on %s | %d samples | view %s / %s | exposure %.2f" % (bpy.app.version_string, device, sc.cycles.samples, vt, lk, sc.view_settings.exposure))
    print("World FORTNITE_WORLD (sky model %s, sky calibration x%.3f) | atmosphere volume FORTNITE_ATMO_VOLUME" % (sky, SKY_GAIN))
    print("Lights created or reset : %d  (%s)  centre %s" % (len(lights), ", ".join(o.name for o in lights), tuple(round(v, 2) for v in CENTER)))
    if sc.get("fortnite_muted_lights"): print("Existing lights muted   : %s" % sc["fortnite_muted_lights"])
    print("Materials converted now : %d  %s" % (len(done), done))
    print("Already converted       : %d" % len(already))
    print("Materials left alone    : %d  %s" % (len(skipped), skipped))
    print("Compositor chain in     : %s (Glare -> Color Balance -> Lens Distortion)" % comp)
    for n in NOTES: print("NOTE:", n)
    print("======================================================\n")
    if opt("--save"): bpy.ops.wm.save_as_mainfile(filepath=opt("--save"))

main()
