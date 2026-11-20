"""EMOTION SIGNS (references/style_analysis, 5 reference videos, 2026-11-20): the drawn 2D marks the references put on a character for an
extreme emotion or a force. All five videos use them (CHARACTER_DESIGN_AND_ANIMATION.md §2, VFX_AND_COMPOSITING_BIBLE.md §2):
  lightning(card, f0, f1)          red jagged bolts radiating from the body, REDRAWN EVERY FRAME (V01 798-821: never a looping shape)
  shock_ring(card, frame)          a thin circle that grows from the torso to the frame edge in 4 frames (V01 817-820, V05 778-781)
  glow_eyes(card, frame)           red glowing eyes that switch on in ONE frame, no fade (V04 883), with a small red light
  spiral_eyes(card, f0, f1)        red/white hypnotic spirals that turn (V04 1590-1620)
  dollar_eyes(card, frame)         green $ eyes that pop in one frame (V03 2436)
  sweat_drop(card, frame)          a blue drop with a highlight beside the head, slides a little (V02 1657)
  aura(card, f0, f1)               dark-red halo around the body + pebbles floating up and down, before a strike (V05 762-768)
  scribble(card, f0, f1)           a wobbly black loop above the head, redrawn every 3 frames: puzzlement (V05 370)
  impact_lines(at, frame)          short radial strokes on the ground around a contact point, moving outward (V01 1524-1544)
Signs are flat (2D), emissive, cast no shadow, live in the L_FX collection and are PARENTED TO THE CARD (cards face the camera with -Y,
local X = right, local Z = up, origin at the feet), so they follow the character. Head / eye positions come from the card's anchors
(tools/card_anchors.py) or are given explicitly. Timings are the ones measured on the references (frames at 30 fps).
Use them from a shot script or from a plan: actions[].sign = "lightning" | "glow_eyes" | ... (plan_check STYLE5 requires a sign on an
extreme emotion)."""
import bpy, bmesh, math, random, json, os
from mathutils import Vector

FX = "L_FX"
RED, WHITE, BLACK, GREEN, BLUE = (1.0, .06, .04), (1, 1, 1), (.02, .02, .025), (.15, .85, .25), (.35, .7, 1.0)

def _col():
    c = bpy.data.collections.get(FX) or bpy.data.collections.new(FX)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def _mat(name, rgb, strength=4.0, alpha=1.0):
    """flat emissive ink: unaffected by the scene light, like a drawn mark"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL": N.remove(n)
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1); em.inputs["Strength"].default_value = strength
    if alpha < 1.0:
        tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = alpha
        L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    else: L.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    m["rc_sign"] = 1
    return m

def _obj(name, bm, mat, parent, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); _col().objects.link(o)
    o.visible_shadow = False; o.visible_glossy = False; o.visible_diffuse = False
    if parent is not None: o.parent = parent
    return o

def _only(o, f0, f1):
    """visible from f0 to f1 included (a drawn mark appears / disappears on the frame, like the references)"""
    for f, v in ((f0 - 1, False), (f0, True), (f1, True), (f1 + 1, False)):
        o.hide_render = not v; o.hide_viewport = not v; o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)
    for fc in (o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []):
        for k in fc.keyframe_points: k.interpolation = "CONSTANT"

def anchors(card):
    """head top, head x and feet of a card, in card-local metres (from its anchors.json), plus a default eye height"""
    a = {"head_top": 1.9, "head_x": 0.0, "feet": 0.0}
    try:
        path = card.get("rc_anchors") if hasattr(card, "get") else None
        if path and os.path.exists(path):
            A = json.load(open(path)); k = sorted(x for x in A if x.isdigit())[0]; a.update({kk: A[k][kk] for kk in ("head_top", "head_x", "feet") if kk in A[k]})
    except Exception: pass
    H = a["head_top"] - a["feet"]
    a["eye_z"] = a["feet"] + .69 * H; a["eye_dx"] = .052 * H; a["head_c"] = a["feet"] + .72 * H; a["chest_z"] = a["feet"] + .55 * H; a["H"] = H
    return a

def _ribbon(pts, width):
    """a flat strip in the card plane (X, Z) along a polyline"""
    bm = bmesh.new(); L, R = [], []
    for i, (x, z) in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]; dx, dz = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dz) or 1
        w = width * (1 - .7 * i / max(1, len(pts) - 1))                                    # thins out toward the tip
        nx, nz = -dz / n * w / 2, dx / n * w / 2
        L.append(bm.verts.new((x + nx, -.03, z + nz))); R.append(bm.verts.new((x - nx, -.03, z - nz)))
    for i in range(len(pts) - 1): bm.faces.new((L[i], L[i + 1], R[i + 1], R[i]))
    return bm

def lightning(card, f0, f1, bolts=6, reach=None, width=.035, color=RED, seed=1):
    """V01 798-821: red forked bolts from the torso outward, a new random shape on every frame"""
    a = anchors(card); reach = reach or .55 * a["H"]; m = _mat("sign_red", color, 1.4); R = random.Random(seed); out = []
    for f in range(f0, f1 + 1):
        for b in range(bolts):
            ang = 2 * math.pi * (b + R.uniform(-.3, .3)) / bolts; x, z = a["head_x"] + .12 * math.cos(ang), a["chest_z"] + .12 * math.sin(ang); pts = [(x, z)]
            for s in range(6):
                ang += R.uniform(-.6, .6); step = reach / 6 * R.uniform(.7, 1.2); x += step * math.cos(ang); z += step * math.sin(ang); pts.append((x, z))
            o = _obj("sign_bolt_%d_%d" % (f, b), _ribbon(pts, width), m, card); _only(o, f, f); out.append(o)
            if R.random() < .5:                                                             # a fork
                i = R.randint(2, 4); fx, fz = pts[i]; fa = ang + R.choice((-1, 1)) * R.uniform(.6, 1.1); fp = [(fx, fz)]
                for s in range(3): fx += reach / 8 * math.cos(fa); fz += reach / 8 * math.sin(fa); fa += R.uniform(-.5, .5); fp.append((fx, fz))
                o = _obj("sign_fork_%d_%d" % (f, b), _ribbon(fp, width * .6), m, card); _only(o, f, f); out.append(o)
    return out

def shock_ring(card, frame, frames=4, r0=None, r1=None, width=.03, color=RED):
    """V01 817-820 / V05 778-781: a thin circle born around the torso that reaches the frame edge in 4 frames, then vanishes"""
    a = anchors(card); r0 = r0 or .2 * a["H"]; r1 = r1 or 1.15 * a["H"]
    bm = bmesh.new(); n = 64; o_, i_ = [], []
    for k in range(n):
        t = 2 * math.pi * k / n; c, s = math.cos(t), math.sin(t)
        o_.append(bm.verts.new((c, -.04, s))); i_.append(bm.verts.new((c * (1 - width), -.04, s * (1 - width))))
    for k in range(n): bm.faces.new((o_[k], o_[(k + 1) % n], i_[(k + 1) % n], i_[k]))
    o = _obj("sign_ring_%d" % frame, bm, _mat("sign_ring", color, 1.6), card); o.location = (a["head_x"], 0, a["chest_z"])
    for i in range(frames + 1):
        r = r0 + (r1 - r0) * (i / frames) ** .8; o.scale = (r, 1, r); o.keyframe_insert("scale", frame=frame + i)
    _only(o, frame, frame + frames); return o

def _eyes(card, eyes):
    a = anchors(card); return eyes or [(a["head_x"] - a["eye_dx"], a["eye_z"]), (a["head_x"] + a["eye_dx"], a["eye_z"])], a

def _disc(name, r, mat, parent, at, n=24):
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=n, radius=r)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "X"))
    o = _obj(name, bm, mat, parent); o.location = (at[0], -.05, at[1]); return o

def glow_eyes(card, frame, until=None, eyes=None, r=None, color=RED):
    """V04 883: red glowing eyes switch on in ONE frame (no fade), with a small red light on the face"""
    E, a = _eyes(card, eyes); r = r or .022 * a["H"]; until = until or frame + 60; out = []
    for i, e in enumerate(E):
        o = _disc("sign_eye_glow_%d_%d" % (frame, i), r, _mat("sign_eye_glow", (1.0, .25, .15), 5.0), card, e); _only(o, frame, until); out.append(o)
        h = _disc("sign_eye_halo_%d_%d" % (frame, i), r * 2.0, _mat("sign_eye_halo", color, 1.5, alpha=.3), card, (e[0], e[1])); h.location.y = -.045; _only(h, frame, until); out.append(h)
    l = bpy.data.lights.new("sign_eye_light_%d" % frame, "POINT"); l.energy = 4.0; l.color = color; l.shadow_soft_size = .05
    lo = bpy.data.objects.new(l.name, l); _col().objects.link(lo); lo.parent = card; lo.location = (a["head_x"], -.25, a["eye_z"])
    for f, v in ((frame - 1, 0.0), (frame, 4.0), (until, 4.0), (until + 1, 0.0)): l.energy = v; l.keyframe_insert("energy", frame=f)
    out.append(lo); return out

def _spiral_mat():
    m = bpy.data.materials.get("sign_spiral")
    if m: return m
    m = bpy.data.materials.new("sign_spiral"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL": N.remove(n)
    tc = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sx.inputs[0])
    def M(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    ang = M("DIVIDE", M("ARCTAN2", sx.outputs["Z"], sx.outputs["X"]), 2 * math.pi)                 # disc lies in local X-Z
    rad = M("POWER", M("ADD", M("MULTIPLY", sx.outputs["X"], sx.outputs["X"]), M("MULTIPLY", sx.outputs["Z"], sx.outputs["Z"])), .5)
    band = M("GREATER_THAN", M("FRACT", M("ADD", ang, M("MULTIPLY", rad, 3.0))), .5)
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; L.new(band, mx.inputs[0]); mx.inputs[6].default_value = (1, 1, 1, 1); mx.inputs[7].default_value = (*RED, 1)
    em = N.new("ShaderNodeEmission"); L.new(mx.outputs[2], em.inputs["Color"]); em.inputs["Strength"].default_value = 3.0
    L.new(em.outputs[0], N["Material Output"].inputs["Surface"]); return m

def spiral_eyes(card, f0, f1, eyes=None, r=None, turns_per_s=1.0):
    """V04 1590-1620: hypnotic red/white spirals over the eyes, turning"""
    E, a = _eyes(card, eyes); r = r or .04 * a["H"]; out = []
    for i, e in enumerate(E):
        o = _disc("sign_spiral_%d_%d" % (f0, i), 1.0, _spiral_mat(), card, e, n=40); o.scale = (r, 1, r)
        rim = _disc("sign_spiral_rim_%d_%d" % (f0, i), r * 1.12, _mat("sign_black", BLACK, 1.0), card, e, n=40); rim.location.y = -.045
        for f in (f0, f1): o.rotation_euler = (0, -2 * math.pi * turns_per_s * (f - f0) / 30.0, 0); o.keyframe_insert("rotation_euler", frame=f)
        for fc in (o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []):
            for k in fc.keyframe_points: k.interpolation = "LINEAR"
        _only(o, f0, f1); _only(rim, f0, f1); out += [o, rim]
    return out

def _text(name, body, size, mat, parent, at, y=-.05):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.extrude = .002
    o = bpy.data.objects.new(name, cu); _col().objects.link(o); cu.materials.append(mat); o.parent = parent
    o.rotation_euler = (math.pi / 2, 0, 0); o.location = (at[0], y, at[1]); o.visible_shadow = False; return o

def dollar_eyes(card, frame, until=None, eyes=None, size=None):
    """V03 2436: green $ eyes with a black outline pop in one frame"""
    E, a = _eyes(card, eyes); size = size or .085 * a["H"]; until = until or frame + 60; out = []
    for i, e in enumerate(E):
        bg = _text("sign_dollar_bg_%d_%d" % (frame, i), "$", size * 1.18, _mat("sign_black", BLACK, 1.0), card, e, y=-.045)
        fg = _text("sign_dollar_%d_%d" % (frame, i), "$", size, _mat("sign_green", GREEN, 2.5), card, e, y=-.05)
        _only(bg, frame, until); _only(fg, frame, until); out += [bg, fg]
    return out

def sweat_drop(card, frame, until=None, side=1, size=None):
    """V02 1657: a blue drop with a white highlight beside the head; it slides down a little while it lasts"""
    a = anchors(card); size = size or .075 * a["H"]; until = until or frame + 30
    bm = bmesh.new(); pts = [(0, size)] + [(.5 * size * math.sin(t), -.5 * size * (1 - math.cos(t)) * .9) for t in [math.pi * k / 12 for k in range(1, 24)]]
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]; bm.faces.new(vs)
    o = _obj("sign_sweat_%d" % frame, bm, _mat("sign_blue", BLUE, 2.0), card)
    x = a["head_x"] + side * .14 * a["H"]; z0 = a["head_c"] + .06 * a["H"]
    for f, z in ((frame, z0), (until, z0 - .05 * a["H"])): o.location = (x, -.05, z); o.keyframe_insert("location", frame=f)
    hl = _disc("sign_sweat_hl_%d" % frame, size * .14, _mat("sign_white", WHITE, 2.0), o, (-.15 * size, -.25 * size)); hl.location.y = -.002
    _only(o, frame, until); _only(hl, frame, until); return [o, hl]

def aura(card, f0, f1, pebbles=7, color=(.45, .02, .02), seed=4):
    """V05 762-768: a dark-red halo around the body and pebbles that float up and down before the strike"""
    a = anchors(card); R = random.Random(seed); out = []
    h = _disc("sign_aura_%d" % f0, 1.0, _mat("sign_aura", color, 1.0, alpha=.28), card, (a["head_x"], a["chest_z"] + .1 * a["H"]), n=48)
    h.location.y = .02; h.scale = (.32 * a["H"], 1, .55 * a["H"]); _only(h, f0, f1); out.append(h)
    for k in range(pebbles):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=R.uniform(.02, .05) * a["H"])
        p = _obj("sign_pebble_%d_%d" % (f0, k), bm, _mat("sign_pebble", (.12, .1, .09), .6), card)
        x = a["head_x"] + R.choice((-1, 1)) * R.uniform(.2, .45) * a["H"]; z = R.uniform(.05, .5) * a["H"]; ph = R.uniform(0, 6.28)
        for f in range(f0, f1 + 1, 2): p.location = (x, -.1, z + .04 * a["H"] * math.sin(ph + f * .5)); p.keyframe_insert("location", frame=f)
        _only(p, f0, f1); out.append(p)
    return out

def scribble(card, f0, f1, color=BLACK, seed=7):
    """V05 370: a wobbly black loop above the head (puzzlement), redrawn every 3 frames"""
    a = anchors(card); R = random.Random(seed); m = _mat("sign_black", color, 1.0); out = []; cx, cz = a["head_x"] - .1 * a["H"], a["head_top"] + .06 * a["H"]
    for f in range(f0, f1 + 1, 3):
        pts = [(cx + .1 * a["H"] * math.cos(t) * R.uniform(.8, 1.2) + .03 * a["H"] * t, cz + .05 * a["H"] * math.sin(t) * R.uniform(.8, 1.2)) for t in [k * .45 for k in range(22)]]
        o = _obj("sign_scribble_%d" % f, _ribbon(pts, .02 * a["H"]), m, card); _only(o, f, min(f + 2, f1)); out.append(o)
    return out

def impact_lines(at, frame, frames=6, n=10, r0=.3, r1=.9, color=BLACK, seed=3):
    """V01 1524-1544: short radial strokes on the ground around a contact point, moving outward, then gone"""
    R = random.Random(seed); m = _mat("sign_black", color, 1.0); out = []
    for k in range(n):
        ang = 2 * math.pi * (k + R.uniform(-.3, .3)) / n; c, s = math.cos(ang), math.sin(ang)
        bm = bmesh.new(); w = .025; L = R.uniform(.12, .22)
        vs = [bm.verts.new(v) for v in ((-w * s, w * c, 0), (w * s, -w * c, 0), (L * c + w * s, L * s - w * c, 0), (L * c - w * s, L * s + w * c, 0))]; bm.faces.new(vs)
        o = _obj("sign_impact_%d_%d" % (frame, k), bm, m, None)
        for i in range(frames + 1):
            r = r0 + (r1 - r0) * i / frames; o.location = (at[0] + r * c, at[1] + r * s, (at[2] if len(at) > 2 else 0) + .02); o.keyframe_insert("location", frame=frame + i)
        _only(o, frame, frame + frames); out.append(o)
    return out

SIGNS = {"lightning": lightning, "shock_ring": shock_ring, "glow_eyes": glow_eyes, "spiral_eyes": spiral_eyes, "dollar_eyes": dollar_eyes,
         "sweat_drop": sweat_drop, "aura": aura, "scribble": scribble}
