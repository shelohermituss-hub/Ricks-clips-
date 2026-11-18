"""rc.lookdev — I. LookDev Engine, PALETTE FIRST (Mission 2, 2026-11-18). Runs inside Blender.
Lesson PI-010: a LookDev that swaps the approved colours for photographic albedo fails. Here the colour of every surface stays the approved
one (the material's own base colour from its builder, or a place palette override); a PBR set only adds:
  * value variation   base = colour x (1 + contrast x (lum(albedo)/mean_lum - 1))   (the texture's light/dark pattern, never its hue,
                       except `keep` (default 0.1): a small share of the texture's own tint for natural variation)
  * roughness          from the map, scaled into the material's range
  * relief             normal map (strength per rule)
Procedural rules ("proc") give rubber, iron and grime a fine grain where no photo set fits. Projection: object-space box mapping,
`tile` metres per repeat, so scale is real and never stretched. Rules are matched by material base name (before any ".001").
    rules = {"stone": {"tex": "tex_rustic_stone_wall", "tile": 1.2, "contrast": .8, "normal": 1.0}, "rubber_body": {"proc": "rubber"}, ...}
    report = lookdev.apply(rules)            -> {material: rule used}; unmatched materials are listed (the gate counts them)"""
import os, sys
import bpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rc import fetch, library  # noqa: E402

_MEAN = {}
PRESETS = {   # material presets (deliverable 9): texture set + response + wear; a rule may say {"preset": "stone", "color": "#hex"} and override any key
    "stone":        {"tex": "tex_rustic_stone_wall", "tile": 1.6, "contrast": .85, "normal": 1.2, "rough": [.7, 1.0], "wear": .35},
    "wood":         {"tex": "tex_brown_planks_05", "tile": .9, "contrast": .7, "normal": .8, "rough": [.6, .9], "wear": .3},
    "painted_metal": {"tex": "tex_rusty_painted_metal", "tile": 1.2, "contrast": .55, "normal": .5, "rough": [.45, .8], "wear": .4},
    "rust":         {"tex": "tex_rusty_painted_metal", "tile": .8, "contrast": .9, "normal": .8, "rough": [.7, 1.0], "wear": .2},
    "fabric":       {"proc": "grain", "contrast": .3, "rough": [.8, 1.0], "bump": .3},
    "plaster":      {"tex": "tex_rustic_stone_wall", "tile": 3.0, "contrast": .35, "normal": .4, "rough": [.8, 1.0], "wear": .25},
    "earth":        {"tex": "tex_brown_mud_02", "tile": 2.5, "contrast": .8, "normal": 1.0, "rough": [.6, 1.0]},
    "grass_ground": {"tex": "tex_leafy_grass", "tile": 2.5, "contrast": .9, "normal": .8, "keep": .15, "rough": [.75, 1.0]},
    "straw":        {"proc": "grain", "contrast": .35, "rough": [.75, 1.0], "bump": .4},
    "rubber":       {"proc": "rubber", "contrast": .18, "rough": [.55, .85]},
    "iron":         {"proc": "iron", "contrast": .3, "rough": [.45, .75], "metal": .6},
    "glass":        {"proc": "grain", "contrast": .05, "rough": [.02, .08]},
    "water":        {"proc": "grain", "contrast": .05, "rough": [.02, .06]},
}
def _hex(h): h = h.lstrip("#"); return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))

def _maps(tex_id):
    b = library.index()[tex_id]["build"]
    return fetch.polyhaven_maps(b["source_id"], b.get("res", "1k"), log=lambda *a: None) if b["type"] == "polyhaven_maps" else fetch.ambientcg_maps(b["source_id"], b.get("res", "1K"), log=lambda *a: None)

def _img(path, non_color):
    im = bpy.data.images.get(os.path.basename(path) + ("|nc" if non_color else "")) or bpy.data.images.load(path, check_existing=False)
    im.name = os.path.basename(path) + ("|nc" if non_color else "")
    if non_color: im.colorspace_settings.name = "Non-Color"
    return im

def mean_lum(im):
    if im.name in _MEAN: return _MEAN[im.name]
    import numpy as np
    a = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(a); a = a.reshape(-1, 4)[::7]
    _MEAN[im.name] = float(max(.02, (a[:, :3] @ np.array([.2126, .7152, .0722], dtype=np.float32)).mean())); return _MEAN[im.name]

def _base_color(m):
    p = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
    return tuple(p.inputs["Base Color"].default_value[:3]) if p else (.5, .5, .5)

def _rebuild(m, color, rule):
    nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); b = N.new("ShaderNodeBsdfPrincipled"); L.new(b.outputs[0], out.inputs[0])
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); L.new(tc.outputs["Object"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = [1.0 / rule.get("tile", 1.0)] * 3
    col = N.new("ShaderNodeRGB"); col.outputs[0].default_value = (*color, 1)
    r0, r1 = rule.get("rough", (.45, .95))
    if "tex" in rule:
        M = _maps(rule["tex"])
        def tex(key, nc):
            t = N.new("ShaderNodeTexImage"); t.image = _img(M[key], nc); t.projection = "BOX"; t.projection_blend = .25; L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
        a = tex("color", False); bw = N.new("ShaderNodeRGBToBW"); L.new(a.outputs["Color"], bw.inputs[0])
        k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = rule.get("contrast", .8) / mean_lum(a.image); L.new(bw.outputs[0], k.inputs[0])
        k2 = N.new("ShaderNodeMath"); k2.operation = "ADD"; k2.inputs[1].default_value = 1 - rule.get("contrast", .8); L.new(k.outputs[0], k2.inputs[0])    # 1 + c*(lum/mean - 1)
        mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
        L.new(col.outputs[0], mul.inputs[6]); L.new(k2.outputs[0], mul.inputs[7])
        keep = N.new("ShaderNodeMix"); keep.data_type = "RGBA"; keep.inputs["Factor"].default_value = rule.get("keep", .1)
        tint = N.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"; tint.inputs["Factor"].default_value = 1.0
        L.new(a.outputs["Color"], tint.inputs[6]); tint.inputs[7].default_value = (*[min(4.0, c / mean_lum(a.image)) for c in color], 1)
        L.new(mul.outputs[2], keep.inputs[6]); L.new(tint.outputs[2], keep.inputs[7]); L.new(keep.outputs[2], b.inputs["Base Color"])
        if "roughness" in M:
            r = tex("roughness", True); mr = N.new("ShaderNodeMapRange"); mr.inputs[3].default_value, mr.inputs[4].default_value = r0, r1
            L.new(r.outputs["Color"], mr.inputs[0]); L.new(mr.outputs[0], b.inputs["Roughness"])
        if "normal" in M:
            n = tex("normal", True); nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = rule.get("normal", 1.0)
            L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    else:                                                        # procedural grain: rubber, iron, grime
        kind = rule.get("proc", "grain"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = {"rubber": 40.0, "iron": 25.0}.get(kind, 18.0)
        nz.inputs["Detail"].default_value = 8.0; L.new(mp.outputs["Vector"], nz.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange"); mr.inputs[3].default_value, mr.inputs[4].default_value = 1 - rule.get("contrast", .25), 1 + rule.get("contrast", .25); L.new(nz.outputs["Fac"], mr.inputs[0])
        mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
        L.new(col.outputs[0], mul.inputs[6]); L.new(mr.outputs[0], mul.inputs[7]); L.new(mul.outputs[2], b.inputs["Base Color"])
        rr = N.new("ShaderNodeMapRange"); rr.inputs[3].default_value, rr.inputs[4].default_value = r0, r1; L.new(nz.outputs["Fac"], rr.inputs[0]); L.new(rr.outputs[0], b.inputs["Roughness"])
        bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = rule.get("bump", .25); L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs[0], b.inputs["Normal"])
    if rule.get("wear"):                                         # WEAR & GRIME: cavities darker (AO), worn edges lighter (pointiness), a grime noise
        src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
        if src is not None:
            ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = rule.get("wear_dist", .15); ao.only_local = True
            gm = N.new("ShaderNodeMapRange"); gm.inputs[3].default_value, gm.inputs[4].default_value = 1 - rule["wear"], 1.0; L.new(ao.outputs["AO"], gm.inputs[0])
            ge = N.new("ShaderNodeNewGeometry"); ed = N.new("ShaderNodeMapRange"); ed.inputs[1].default_value, ed.inputs[2].default_value = .5, .56; ed.inputs[3].default_value, ed.inputs[4].default_value = 1.0, 1 + rule["wear"] * .6
            L.new(ge.outputs["Pointiness"], ed.inputs[0]); m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; L.new(gm.outputs[0], m1.inputs[0]); L.new(ed.outputs[0], m1.inputs[1])
            mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0; L.new(src, mx.inputs[6]); L.new(m1.outputs[0], mx.inputs[7]); L.new(mx.outputs[2], b.inputs["Base Color"])
    if rule.get("metal"): b.inputs["Metallic"].default_value = rule["metal"]
    m["rc_lookdev"] = rule.get("tex") or rule.get("proc", "grain")

def _tint(m, rule):
    """TINT rule for downloaded, already textured materials (plants with alpha cut-outs): keep the node tree and its alpha, pull the base
    colour toward the palette colour: out = mix(albedo, palette x lum(albedo)/mean, amount) x value"""
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    if not b or not b.inputs["Base Color"].links or m.get("rc_tinted"): return
    src = b.inputs["Base Color"].links[0].from_socket; N, L = nt.nodes, nt.links; c = _hex(rule["tint"])
    bw = N.new("ShaderNodeRGBToBW"); L.new(src, bw.inputs[0]); k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 1.0 / rule.get("mean", .25); L.new(bw.outputs[0], k.inputs[0])
    pal = N.new("ShaderNodeMix"); pal.data_type = "RGBA"; pal.blend_type = "MULTIPLY"; pal.inputs["Factor"].default_value = 1.0; pal.inputs[6].default_value = (*c, 1); L.new(k.outputs[0], pal.inputs[7])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["Factor"].default_value = rule.get("amount", .6); L.new(src, mx.inputs[6]); L.new(pal.outputs[2], mx.inputs[7])
    L.new(mx.outputs[2], b.inputs["Base Color"]); m["rc_tinted"] = rule["tint"]

def calibrate_white(scene, ref_png, render_fn, iters=3):
    """MEASURED white balance: move the view white-balance temperature until the render's red/blue ratio matches the reference's"""
    import math
    _, ref = _lum_mean(ref_png); vs = scene.view_settings; vs.use_white_balance = True; log = []
    for i in range(iters):
        _, rgb = _lum_mean(render_fn(i)); r = (rgb[0] / max(1e-4, rgb[2])) / (ref[0] / max(1e-4, ref[2]))
        log.append({"iter": i, "temperature": round(vs.white_balance_temperature, 1), "rb_ratio_vs_ref": round(r, 3)})
        if abs(math.log(r)) < .03: break
        vs.white_balance_temperature = max(2500, min(12000, vs.white_balance_temperature * (r ** -.8)))   # measured 2026-11-18: in Blender 5.2 a LOWER setting renders COOLER (6500->3645 K took red/blue from .70 to .18): too cold (r<1) -> raise it
    return log

def _resolve_rule(rules, base):
    r = rules.get(base)
    if r is None: return None
    if "preset" in r: r = {**PRESETS[r["preset"]], **{k: v for k, v in r.items() if k != "preset"}}
    return r

def _layered(m, rules, rule):
    """TERRAIN LAYERS: two palette rules mixed by a mesh attribute (path_mask from rc.envbuild) broken up by noise at the edge, so the
    path is painted INTO the ground (no floating strip, no hard border)"""
    lay = rule["layers"]; base, over = _resolve_rule(rules, lay["base"]), _resolve_rule(rules, lay["over"])
    tmp_a = bpy.data.materials.new(m.name + "_A"); tmp_a.use_nodes = True; tmp_b = bpy.data.materials.new(m.name + "_B"); tmp_b.use_nodes = True
    _rebuild(tmp_a, _hex(base["color"]) if base.get("color") else _base_color(m), base); _rebuild(tmp_b, _hex(over["color"]), over)
    nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links; out = N.new("ShaderNodeOutputMaterial")
    def graft(src):                                              # copy a built material's nodes into this tree, return its BSDF output
        mp = {}
        for n in src.node_tree.nodes:
            if n.type == "OUTPUT_MATERIAL": continue
            c = N.new(n.bl_idname); mp[n.name] = c
            for attr in ("operation", "blend_type", "data_type", "projection", "projection_blend", "image", "noise_dimensions", "only_local"):
                if hasattr(n, attr):
                    try: setattr(c, attr, getattr(n, attr))
                    except Exception: pass
            for i, sk in enumerate(n.inputs):
                if hasattr(sk, "default_value") and i < len(c.inputs):
                    try: c.inputs[i].default_value = sk.default_value
                    except Exception: pass
            if n.type == "RGB": c.outputs[0].default_value = n.outputs[0].default_value
        for l in src.node_tree.links:
            if l.to_node.type == "OUTPUT_MATERIAL": continue
            L.new(mp[l.from_node.name].outputs[l.from_socket.identifier] if l.from_socket.identifier in mp[l.from_node.name].outputs else mp[l.from_node.name].outputs[list(l.from_node.outputs).index(l.from_socket)],
                  mp[l.to_node.name].inputs[list(l.to_node.inputs).index(l.to_socket)])
        return [mp[n.name] for n in src.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0].outputs[0]
    sa, sb = graft(tmp_a), graft(tmp_b)
    at = N.new("ShaderNodeAttribute"); at.attribute_name = lay.get("mask", "path_mask"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = lay.get("edge_scale", 1.6)
    mr = N.new("ShaderNodeMapRange"); mr.inputs[3].default_value, mr.inputs[4].default_value = -lay.get("edge_noise", .35), lay.get("edge_noise", .35); L.new(nz.outputs["Fac"], mr.inputs[0])
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; ad.use_clamp = True; L.new(at.outputs["Fac"], ad.inputs[0]); L.new(mr.outputs[0], ad.inputs[1])
    mix = N.new("ShaderNodeMixShader"); L.new(ad.outputs[0], mix.inputs[0]); L.new(sa, mix.inputs[1]); L.new(sb, mix.inputs[2]); L.new(mix.outputs[0], out.inputs[0])
    bpy.data.materials.remove(tmp_a); bpy.data.materials.remove(tmp_b); m["rc_lookdev"] = "layers"

def light_rig(scene, light):
    """LIGHT RIGS (deliverable 9): a preset of the approved look library (day, morning, golden, night, interior) + view transform,
    measured exposure and white balance, optional haze volume and the compositor grade"""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "templates"))
    from blender_look import look
    look.apply_look(scene, light.get("preset", "day"), key_dir=tuple(light["key_dir"]) if light.get("key_dir") else None)
    vs = scene.view_settings
    if light.get("view_transform"): vs.view_transform = light["view_transform"]; vs.look = "None"
    if "exposure" in light: vs.exposure = light["exposure"]
    if "white_balance" in light: vs.use_white_balance = True; vs.white_balance_temperature = light["white_balance"]
    if light.get("haze"):
        from rc import vfx
        vfx.haze(scene, light["haze"])
    if light.get("grade"): grade(scene, light["grade"])
    return {"preset": light.get("preset", "day"), "view": vs.view_transform, "exposure": vs.exposure, "white_balance": vs.white_balance_temperature if vs.use_white_balance else None}

def grade(scene, g):
    """COMPOSITOR GRADE (same controls as grade/grade.py): saturation, lift/gamma/gain, vignette; done in Blender so every frame and every
    slice gets the identical grade"""
    scene.use_nodes = True; nt = scene.node_tree; N, L = nt.nodes, nt.links
    rl = N.get("Render Layers") or N.new("CompositorNodeRLayers"); comp = N.get("Composite") or N.new("CompositorNodeComposite")
    for l in list(comp.inputs[0].links): L.remove(l)
    hsv = N.new("CompositorNodeHueSat"); hsv.inputs["Saturation"].default_value = g.get("saturation", 1.0); hsv.inputs["Value"].default_value = g.get("value", 1.0)
    cb = N.new("CompositorNodeColorBalance"); cb.correction_method = "LIFT_GAMMA_GAIN"
    cb.lift = [g.get("lift", 1.0)] * 3; cb.gamma = [g.get("gamma", 1.0)] * 3; cb.gain = [g.get("gain", 1.0)] * 3
    L.new(rl.outputs["Image"], hsv.inputs["Image"]); L.new(hsv.outputs[0], cb.inputs["Image"]); last = cb.outputs[0]
    if g.get("vignette"):
        ell = N.new("CompositorNodeEllipseMask"); ell.width, ell.height = .95, .95; bl = N.new("CompositorNodeBlur"); bl.filter_type = "FAST_GAUSS"; bl.use_relative = True; bl.factor_x = bl.factor_y = .25
        L.new(ell.outputs[0], bl.inputs[0]); mx = N.new("CompositorNodeMixRGB"); mx.blend_type = "MULTIPLY"; L.new(last, mx.inputs[1]); mr = N.new("CompositorNodeMapRange")
        mr.inputs[3].default_value, mr.inputs[4].default_value = 1 - g["vignette"], 1.0; L.new(bl.outputs[0], mr.inputs[0]); L.new(mr.outputs[0], mx.inputs[2]); last = mx.outputs[0]
    L.new(last, comp.inputs[0])

def apply(rules, materials=None):
    rep, unmatched = {}, set()
    for m in list(materials or bpy.data.materials):
        if m.library or not m.use_nodes: continue
        base = m.name.split(".")[0]; rule = _resolve_rule(rules, base)
        if rule is not None and "layers" in rule: _layered(m, rules, rule); rep[m.name] = "layers"; continue
        if rule is None: unmatched.add(base); continue
        if "tint" in rule: _tint(m, rule); rep[m.name] = "tint"; continue
        _rebuild(m, _hex(rule["color"]) if rule.get("color") else _base_color(m), rule); rep[m.name] = rule.get("tex") or rule.get("proc", "grain")
    return {"applied": rep, "unmatched": sorted(unmatched)}


def _lum_mean(path):
    import numpy as np
    im = bpy.data.images.load(path, check_existing=False); a = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(a); bpy.data.images.remove(im)
    a = a.reshape(-1, 4)[:, :3]                                  # Blender loads sRGB PNGs as linear floats in .pixels? (no: byte images keep sRGB) -> convert explicitly
    lin = np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)
    return float((lin @ np.array([.2126, .7152, .0722], dtype=np.float32)).mean()), [float(x) for x in lin.mean(0)]

def calibrate_exposure(scene, ref_png, frame, outdir, render_fn, iters=3, clamp=3.0):
    """MEASURED calibration (no eyeballing): render the frame, compare its mean linear luminance with the approved reference frame,
    move the view exposure by log2(ref/render), repeat. Returns the log with the colour ratios (drift report, not corrected here)."""
    import math
    ref_l, ref_rgb = _lum_mean(ref_png); log = []
    for i in range(iters):
        p = render_fn(i); l, rgb = _lum_mean(p); step = math.log2(max(1e-4, ref_l) / max(1e-4, l))
        log.append({"iter": i, "exposure": round(scene.view_settings.exposure, 3), "render_lum": round(l, 4), "ref_lum": round(ref_l, 4), "rgb_ratio": [round(r / max(1e-4, q), 3) for r, q in zip(rgb, ref_rgb)]})
        if abs(step) < .05: break
        scene.view_settings.exposure = max(-clamp, min(clamp, scene.view_settings.exposure + step))
    return log
