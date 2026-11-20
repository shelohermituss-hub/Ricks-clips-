"""Fortnite-like look for Cycles (CB 2026-11-20): colours, shaders, light and atmosphere ONLY. No geometry, no camera is changed.
The scene is ANALYSED first (sun, characters, camera path, sizes, materials) and every value is derived from it; nothing is a fixed recipe.
Idempotent: everything this module creates is named FN_*, running it again updates the same nodes and lamps.

    from rc import fortnite; report = fortnite.apply(scene)                       # in a shot script, after the scene is built
    blender -b shot.blend --python blender/rc/fortnite.py -- [--save out.blend] [--no-probe] [--only analyse]

What the style is made of (traits of the Epic cinematics, applied on top of the scene's own sky and sun):
  warm key sun + blue-violet shadows that are never black | cyan rim light behind every character group, seen from the camera
  light aerial haze with distance | stylised PBR: painted variation, lighter edges, tinted hollows, no photo-real grain, clean metals
  vivid but not burnt colours: soft glow, cool lift / warm gain, exposure calibrated by a tiny probe render
"""
import bpy, math, sys
from mathutils import Vector

NG = "NG_FN_StylisedPBR"; COL = "FN_LIGHTING"
ORGANIC = ("leaf", "leaves", "tree", "grass", "bush", "plant", "skin", "foliage", "marram", "feuille", "herbe", "peau")
SHADOW_TINT = (.30, .38, 1.0); RIM = (.45, .85, 1.0); SUN_WARM = (1.0, .92, .78); HAZE = (.62, .78, 1.0, 1)
TARGET_LUMA = .47                 # middle of the daylight range measured on the reference videos (.40-.58)

# ------------------------------------------------------------------ helpers
def _sock(n, name, kind=None, out=False):
    for s in (n.outputs if out else n.inputs):
        if s.name == name and (kind is None or s.type == kind): return s

def _set(n, name, v, kind=None):
    s = _sock(n, name, kind)
    if s is not None:
        try: s.default_value = v; return True
        except Exception: pass
    return False

def _node(nt, idname, name, **props):
    n = nt.nodes.get(name) or nt.nodes.new(idname); n.name = n.label = name
    for k, v in props.items():
        if hasattr(n, k): setattr(n, k, v)
    return n

def _ramp(n, p0, p1, c0=(0, 0, 0, 1), c1=(1, 1, 1, 1)):
    e = n.color_ramp.elements
    while len(e) > 2: e.remove(e[-1])
    e[0].position, e[0].color, e[1].position, e[1].color = p0, c0, p1, c1; return n

def _mix(nt, name, blend, fac=None):
    n = _node(nt, "ShaderNodeMix", name, data_type="RGBA", blend_type=blend, clamp_result=False, clamp_factor=True)
    if fac is not None: n.inputs[0].default_value = fac
    return n
A, B, RES = 6, 7, 2

def _iface(tree, name, in_out, kind, default=None):
    for it in tree.interface.items_tree:
        if it.item_type == "SOCKET" and it.name == name and it.in_out == in_out: s = it; break
    else: s = tree.interface.new_socket(name=name, in_out=in_out, socket_type=kind)
    if default is not None:
        try: s.default_value = default
        except Exception: pass
    return s

# ------------------------------------------------------------------ 1. analysis
def is_character(o):
    return o.type == "MESH" and (any(m and m.name.startswith("Card_") for m in o.data.materials) or any(c.name == "RC_CHARACTERS" for c in o.users_collection))

def analyse(sc, step=6):
    """Read the scene: key sun, characters and where the camera sees them best, sizes, materials."""
    from bpy_extras.object_utils import world_to_camera_view as w2c
    suns = sorted((o for o in sc.objects if o.type == "LIGHT" and o.data.type == "SUN" and not o.hide_render and not o.name.startswith("FN_")), key=lambda o: -o.data.energy)
    chars = [o for o in sc.objects if is_character(o) and not o.hide_render]; cam = sc.camera; f_keep = sc.frame_current
    best = {o.name: (9e9, None, None, None) for o in chars}; near, far = 9e9, 0.0
    for f in range(sc.frame_start, sc.frame_end + 1, step):
        sc.frame_set(f); cp = cam.matrix_world.translation.copy()
        for o in chars:
            p = o.matrix_world @ Vector((0, 0, o.dimensions.z * .5 / max(o.scale.z, 1e-6))); v = w2c(sc, cam, p)
            if v.z <= 0: continue
            d = (v.x - .5) ** 2 + (v.y - .5) ** 2
            if 0 <= v.x <= 1 and 0 <= v.y <= 1: near, far = min(near, v.z), max(far, v.z)
            if d < best[o.name][0]: best[o.name] = (d, f, p.copy(), cp)
    sc.frame_set(f_keep)
    groups = []                                   # characters seen at the same moment and close together share one rim light
    for name, (d, f, p, cp) in sorted(best.items(), key=lambda kv: kv[1][1] or 0):
        if p is None: continue
        g = next((g for g in groups if (g["centre"] - p).length < 6 and abs(g["frame"] - f) < 40), None)
        if g: g["names"].append(name); g["pts"].append(p); g["centre"] = sum(g["pts"], Vector()) / len(g["pts"])
        else: groups.append(dict(names=[name], pts=[p], centre=p.copy(), frame=f, cam=cp))
    for g in groups: g["radius"] = max([(q - g["centre"]).length for q in g["pts"]] + [1.2]); g["height"] = max(bpy.data.objects[n].dimensions.z for n in g["names"])
    mats = {"stylised": [], "metal": [], "organic": [], "character": [], "emissive": [], "glass": [], "other": []}
    for m in bpy.data.materials:
        if m.node_tree is None or m.name.startswith("FN_") or m.users == 0: continue
        b = next((n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
        if m.name.startswith("Card_"): mats["character"].append(m.name); continue
        if b is None: mats["other"].append(m.name); continue
        em, tr = b.inputs.get("Emission Strength"), b.inputs.get("Transmission Weight")
        if em is not None and not em.is_linked and em.default_value > 1.0: mats["emissive"].append(m.name); continue
        if tr is not None and not tr.is_linked and tr.default_value > .5: mats["glass"].append(m.name); continue
        mats["stylised"].append(m.name)
        if not b.inputs["Metallic"].is_linked and b.inputs["Metallic"].default_value > .5: mats["metal"].append(m.name)
        if any(k in m.name.lower() for k in ORGANIC): mats["organic"].append(m.name)
    sun = suns[0] if suns else None
    to_sun = (sun.matrix_world.to_quaternion() @ Vector((0, 0, 1))) if sun else Vector((-.5, .5, .6)).normalized()
    return dict(sun=sun.name if sun else None, sun_energy=sun.data.energy if sun else 0.0, to_sun=to_sun, groups=groups, near=near if far else 3.0, far=far or 40.0,
                materials=mats, characters=[o.name for o in chars], view=(sc.view_settings.view_transform, sc.view_settings.look))

# ------------------------------------------------------------------ 2. render + colour management
def setup_render(sc):
    c = sc.cycles; sc.render.engine = "CYCLES"
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces, c.transparent_max_bounces = 8, 3, 4, 6, 8   # 3 diffuse bounces: coloured bounce light
    c.sample_clamp_direct, c.sample_clamp_indirect = 10.0, 5.0; c.use_denoising = True
    try: c.denoiser = "OPENIMAGEDENOISE"; c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    except Exception: pass

# ------------------------------------------------------------------ 3. light
def _lamp(col, name, kind, **props):
    ob = bpy.data.objects.get(name)
    if ob is None: ob = bpy.data.objects.new(name, bpy.data.lights.new(name, kind)); col.objects.link(ob)
    ob.data.type = kind
    for k, v in props.items(): setattr(ob.data, k, v)
    return ob

def setup_lights(sc, an, shadow_fill=.06, rim_gain=1.0):
    col = bpy.data.collections.get(COL) or bpy.data.collections.new(COL)
    if col.name not in sc.collection.children: sc.collection.children.link(col)
    made = []
    if an["sun"]:                                             # the scene's own sun stays where the shot put it: only its colour warms up
        s = sc.objects[an["sun"]].data; s.color = SUN_WARM; s.angle = max(s.angle, math.radians(1.5))
    e_sun = an["sun_energy"] or 5.0
    # blue-violet light from straight above, WITHOUT shadows: it fills every shadow with colour, so no shadow is grey or black
    t = _lamp(col, "FN_SHADOW_TINT", "SUN", energy=e_sun * shadow_fill, color=SHADOW_TINT, angle=math.radians(40)); t.data.use_shadow = False
    t.rotation_euler = (0, 0, 0); made.append(t.name)
    live = set(made)
    rec = bpy.data.collections.get("FN_RIM_RECEIVERS") or bpy.data.collections.new("FN_RIM_RECEIVERS")      # the rim draws silhouettes: it must not paint the ground cyan
    for o in list(rec.objects): rec.objects.unlink(o)
    big = [o for o in sc.objects if o.type == "MESH" and max(o.dimensions.x, o.dimensions.y) >= 20.0]              # grounds, sea, backdrops
    ground_mats = {m.name for o in big for m in o.data.materials if m}                                             # ... and anything made of the same matter (sand mounds)
    for o in sc.objects:
        if o.type not in ("MESH", "CURVE") or o in big or o.name.startswith("FN_"): continue
        if any(m and m.name in ground_mats for m in o.data.materials): continue
        rec.objects.link(o)
    for i, g in enumerate(an["groups"]):                      # one cyan rim light per character group: behind the group as the camera sees it, on the shadow side
        c, cp = g["centre"], g["cam"]; back = Vector((c.x - cp.x, c.y - cp.y, 0)).normalized(); side = Vector((back.y, -back.x, 0))
        if side.dot(an["to_sun"]) > 0: side = -side          # away from the sun: the rim draws the dark side of the silhouette
        d = 3.0 + 1.6 * g["radius"]; pos = c + back * d * .85 + side * d * .5 + Vector((0, 0, g["height"] * .9 + 1.0)); dist = (pos - c).length
        r = _lamp(col, "FN_RIM_%02d" % i, "AREA", shape="RECTANGLE", size=2.0 + g["radius"], size_y=2.0, color=RIM, energy=22.0 * e_sun / 11.0 * dist * dist * rim_gain)
        r.data.spread = math.radians(70)
        try: r.light_linking.receiver_collection = rec
        except Exception: pass
        r.location = pos; r.rotation_euler = (c - pos).to_track_quat("-Z", "Y").to_euler(); live.add(r.name); made.append(r.name)
    for o in list(col.objects):                               # a group that no longer exists loses its rim
        if o.name.startswith("FN_RIM_") and o.name not in live: bpy.data.objects.remove(o)
    return made

# ------------------------------------------------------------------ 4. stylised PBR
def build_group(paint=.07, edge=.12, hollow=.28, vibrance=1.20):
    g = bpy.data.node_groups.get(NG) or bpy.data.node_groups.new(NG, "ShaderNodeTree")
    _iface(g, "Base Color", "INPUT", "NodeSocketColor", (.8, .8, .8, 1)); _iface(g, "Metallic", "INPUT", "NodeSocketFloat", 0.0)
    _iface(g, "Roughness", "INPUT", "NodeSocketFloat", .5); _iface(g, "Normal", "INPUT", "NodeSocketVector")
    _iface(g, "Base Color", "OUTPUT", "NodeSocketColor"); _iface(g, "Roughness", "OUTPUT", "NodeSocketFloat"); _iface(g, "Normal", "OUTPUT", "NodeSocketVector")
    g.nodes.clear(); L = g.links.new
    gi = _node(g, "NodeGroupInput", "IN"); go = _node(g, "NodeGroupOutput", "OUT"); tc = _node(g, "ShaderNodeTexCoord", "COORD"); geo = _node(g, "ShaderNodeNewGeometry", "GEO")
    noise = _node(g, "ShaderNodeTexNoise", "PAINT_NOISE"); _set(noise, "Scale", 9.0); _set(noise, "Detail", 3.0); _set(noise, "Roughness", .6)     # broad brush patches
    nr = _ramp(_node(g, "ShaderNodeValToRGB", "PAINT_RAMP"), .35, .65); m1 = _mix(g, "1_PAINT", "OVERLAY", paint)
    L(tc.outputs["Object"], noise.inputs["Vector"]); L(noise.outputs[0], nr.inputs[0]); L(gi.outputs["Base Color"], m1.inputs[A]); L(nr.outputs[0], m1.inputs[B])
    ao = _node(g, "ShaderNodeAmbientOcclusion", "AO", samples=8); _set(ao, "Distance", .35)                                                       # hollows tinted blue-violet
    ar = _ramp(_node(g, "ShaderNodeValToRGB", "AO_RAMP"), .2, .85, (1, 1, 1, 1), (0, 0, 0, 1)); af = _node(g, "ShaderNodeMath", "AO_FAC", operation="MULTIPLY"); af.inputs[1].default_value = hollow
    m2 = _mix(g, "2_HOLLOW_TINT", "MULTIPLY"); m2.inputs[B].default_value = (.30, .34, .62, 1)
    L(ao.outputs["AO"], ar.inputs[0]); L(ar.outputs[0], af.inputs[0]); L(af.outputs[0], m2.inputs[0]); L(m1.outputs[RES], m2.inputs[A])
    er = _ramp(_node(g, "ShaderNodeValToRGB", "EDGE_RAMP"), .54, .64); m3 = _mix(g, "3_EDGE_LIGHT", "SCREEN", edge)                               # lighter edges
    L(geo.outputs["Pointiness"], er.inputs[0]); L(m2.outputs[RES], m3.inputs[A]); L(er.outputs[0], m3.inputs[B])
    hsv = _node(g, "ShaderNodeHueSaturation", "4_VIBRANCE"); hsv.inputs["Saturation"].default_value = vibrance
    lo = _node(g, "ShaderNodeVectorMath", "4_NO_BLACK", operation="MAXIMUM"); lo.inputs[1].default_value = (.03, .03, .035)
    hi = _node(g, "ShaderNodeVectorMath", "4_NO_BURN", operation="MINIMUM"); hi.inputs[1].default_value = (.88, .88, .88)
    L(m3.outputs[RES], hsv.inputs["Color"]); L(hsv.outputs[0], lo.inputs[0]); L(lo.outputs[0], hi.inputs[0]); L(hi.outputs[0], go.inputs["Base Color"])
    r_d = _node(g, "ShaderNodeMapRange", "5_ROUGH_MATTE"); r_m = _node(g, "ShaderNodeMapRange", "5_ROUGH_METAL")                                  # semi-matte surfaces, clean bright metals
    for n, a, b in ((r_d, .40, .72), (r_m, .18, .40)): n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = a, b; L(gi.outputs["Roughness"], n.inputs["Value"])
    rmix = _node(g, "ShaderNodeMix", "5_ROUGH_MIX", data_type="FLOAT", clamp_factor=True)
    L(gi.outputs["Metallic"], rmix.inputs[0]); L(r_d.outputs[0], rmix.inputs[2]); L(r_m.outputs[0], rmix.inputs[3]); L(rmix.outputs[0], go.inputs["Roughness"])
    nmix = _node(g, "ShaderNodeMix", "6_SOFT_NORMAL", data_type="VECTOR", clamp_factor=True); nmix.inputs[0].default_value = .5                    # half of the photo grain: volume stays, noise goes
    nn = _node(g, "ShaderNodeVectorMath", "6_NORMALIZE", operation="NORMALIZE")
    L(geo.outputs["Normal"], nmix.inputs[4]); L(gi.outputs["Normal"], nmix.inputs[5]); L(nmix.outputs[1], nn.inputs[0]); L(nn.outputs[0], go.inputs["Normal"])
    for i, n in enumerate(g.nodes): n.location = (190 * (i % 8), -230 * (i // 8))
    return g

def setup_materials(an, g):
    done = 0
    for name in an["materials"]["stylised"]:
        m = bpy.data.materials[name]; nt = m.node_tree
        for b in [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"]:
            bc = b.inputs["Base Color"]
            if not (bc.is_linked and bc.links[0].from_node.bl_idname == "ShaderNodeGroup" and bc.links[0].from_node.node_tree == g):
                gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = g; gn.name = gn.label = "FN_PBR"; gn.location = (b.location.x - 240, b.location.y); had_n = b.inputs["Normal"].is_linked
                for k in ("Base Color", "Metallic", "Roughness", "Normal"):
                    s = b.inputs[k]
                    if s.is_linked: nt.links.new(s.links[0].from_socket, gn.inputs[k])
                    else: gn.inputs[k].default_value = s.default_value
                nt.links.new(gn.outputs["Base Color"], bc); nt.links.new(gn.outputs["Roughness"], b.inputs["Roughness"])
                if had_n: nt.links.new(gn.outputs["Normal"], b.inputs["Normal"])
                done += 1
            if name in an["materials"]["organic"]: _set(b, "Subsurface Weight", .25); _set(b, "Subsurface Scale", .05)       # light passes through leaves
    return done

# ------------------------------------------------------------------ 5. compositor: haze with distance, glow, cool shadows / warm lights, calibrated exposure
def setup_compositor(sc, an, haze=.14, exposure=None):
    tree = sc.compositing_node_group
    if tree is None:
        tree = bpy.data.node_groups.new("FN_COMPOSITE", "CompositorNodeTree"); sc.compositing_node_group = tree
    _iface(tree, "Image", "OUTPUT", "NodeSocketColor")
    out = next((n for n in tree.nodes if n.bl_idname == "NodeGroupOutput"), None) or tree.nodes.new("NodeGroupOutput")
    rl = next((n for n in tree.nodes if n.bl_idname == "CompositorNodeRLayers"), None) or tree.nodes.new("CompositorNodeRLayers")
    for vl in sc.view_layers: vl.use_pass_mist = True
    ms = sc.world.mist_settings; ms.start = max(an["near"] * 1.5, 2.0); ms.depth = max(an["far"] * 2.5, ms.start + 30.0); ms.falloff = "LINEAR"   # haze starts behind the subjects
    names = ("FN_HAZE", "FN_GLOW", "FN_BALANCE", "FN_VIBRANCE", "FN_EXPOSURE"); o_in = out.inputs[0]
    src = o_in.links[0].from_socket if o_in.is_linked else rl.outputs["Image"]
    while src.node.name in names:
        i = src.node.inputs[A] if src.node.name == "FN_HAZE" else src.node.inputs[0]; src = i.links[0].from_socket if i.is_linked else rl.outputs["Image"]
    L = tree.links.new
    hz = _mix(tree, "FN_HAZE", "MIX"); hz.inputs[B].default_value = HAZE; hf = _node(tree, "ShaderNodeMath", "FN_HAZE_AMOUNT", operation="MULTIPLY"); hf.inputs[1].default_value = haze
    L(rl.outputs["Mist"], hf.inputs[0]); L(hf.outputs[0], hz.inputs[0]); L(src, hz.inputs[A])
    gl = _node(tree, "CompositorNodeGlare", "FN_GLOW"); _set(gl, "Type", "Fog Glow", "MENU"); _set(gl, "Quality", "High", "MENU"); _set(gl, "Threshold", 1.0); _set(gl, "Strength", .30); _set(gl, "Size", .25)
    cb = _node(tree, "CompositorNodeColorBalance", "FN_BALANCE"); _set(cb, "Type", "Lift/Gamma/Gain", "MENU")
    _set(cb, "Lift", (.96, .98, 1.05, 1), "RGBA"); _set(cb, "Gamma", (1.0, 1.0, 1.0, 1), "RGBA"); _set(cb, "Gain", (1.04, 1.01, .95, 1), "RGBA")
    hs = _node(tree, "CompositorNodeHueSat", "FN_VIBRANCE"); _set(hs, "Saturation", 1.10)
    ex = _node(tree, "CompositorNodeExposure", "FN_EXPOSURE")
    if exposure is not None: _set(ex, "Exposure", exposure)
    L(hz.outputs[RES], gl.inputs[0]); L(gl.outputs[0], _sock(cb, "Image")); L(cb.outputs[0], _sock(hs, "Image")); L(hs.outputs[0], ex.inputs[0]); L(ex.outputs[0], o_in)
    for i, n in enumerate((hf, hz, gl, cb, hs, ex)): n.location = (out.location.x - 200 * (6 - i), out.location.y + 300)
    return ex

def probe(sc, frames, ex, target=TARGET_LUMA, passes=2):
    """Tiny renders on the key moments: the compositor exposure is moved until the mean luminance sits on the target."""
    import numpy as np, tempfile, os
    r = sc.render; keep = (r.resolution_x, r.resolution_y, r.resolution_percentage, sc.cycles.samples, r.filepath, sc.frame_current, r.use_motion_blur)
    r.resolution_x, r.resolution_y, r.resolution_percentage, sc.cycles.samples, r.use_motion_blur = 108, 192, 100, 8, False; path = os.path.join(tempfile.gettempdir(), "fn_probe.png"); log = []
    for _ in range(passes):
        lum = []
        for f in frames:
            sc.frame_set(f); r.filepath = path; bpy.ops.render.render(write_still=True)
            im = bpy.data.images.load(path); a = np.array(im.pixels[:]).reshape(-1, 4)[:, :3]; bpy.data.images.remove(im); lum.append(float((a * [.2126, .7152, .0722]).sum(1).mean()))
        mean = sum(lum) / len(lum); cur = _sock(ex, "Exposure").default_value; log.append((round(cur, 2), [round(v, 2) for v in lum]))
        if abs(mean - target) < .02: break
        _set(ex, "Exposure", cur + max(-1.0, min(1.0, 1.6 * math.log2(target / max(mean, .02)))))
    r.resolution_x, r.resolution_y, r.resolution_percentage, sc.cycles.samples, r.filepath, _, r.use_motion_blur = keep; sc.frame_set(keep[5])
    return log

# ------------------------------------------------------------------ all together
def apply(sc, do_probe=True, **k):
    an = analyse(sc); setup_render(sc); lamps = setup_lights(sc, an, k.get("shadow_fill", .06), k.get("rim_gain", 1.0))
    g = build_group(); n_mat = setup_materials(an, g); ex = setup_compositor(sc, an, k.get("haze", .14), k.get("exposure"))
    span = sc.frame_end - sc.frame_start
    frames = sorted({g["frame"] for g in an["groups"]} | {sc.frame_start + round(span * q) for q in (.15, .5, .85)})     # key moments + three spread over the shot
    log = probe(sc, frames, ex) if do_probe else []
    M = an["materials"]
    print("\n=========== FN LOOK ===========")
    print("scene read  : sun %s (energy %.1f) | %d characters in %d groups %s | subjects %.1f-%.1f m from the camera" % (an["sun"], an["sun_energy"], len(an["characters"]), len(an["groups"]), [(g["names"], "frame %d" % g["frame"]) for g in an["groups"]], an["near"], an["far"]))
    print("lights      : %d set (%s)" % (len(lamps), ", ".join(lamps)))
    print("materials   : %d stylised now, %d in the style in total (metal %d, organic %d) | untouched: characters %d, emissive %d, glass %d, other %d" % (n_mat, len(M["stylised"]), len(M["metal"]), len(M["organic"]), len(M["character"]), len(M["emissive"]), len(M["glass"]), len(M["other"])))
    print("haze        : starts %.1f m, full at %.1f m" % (sc.world.mist_settings.start, sc.world.mist_settings.start + sc.world.mist_settings.depth))
    print("exposure    : %s  (probe: exposure, luminance per key moment) -> final %.2f" % (log, _sock(ex, "Exposure").default_value))
    print("===============================\n")
    return dict(analysis=an, lamps=lamps, materials=n_mat, probe=log)

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    apply(bpy.context.scene, do_probe="--no-probe" not in argv)
    if "--save" in argv: bpy.ops.wm.save_as_mainfile(filepath=argv[argv.index("--save") + 1])
