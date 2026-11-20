"""Shared tools of the exploding-whale shots (one file per film: shots/film.py). Every shot runs on LOCAL frames 0..n-1.
    blender -b --factory-startup --python shots/film.py -- <shot id> <out.blend> [--res 270x480] [--samples 16] [--still f:png ...] [--anim dir]"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.abspath(os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(EP, "sets")); sys.path.insert(0, HERE)
import beach, props, cast
from rc import render, lookdev, characters, vfx, signs, look
sys.path.insert(0, os.path.join(beach.SKILL, "demos", "crashed_car", "sets")); import street

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d=None: A[A.index(k) + 1] if k in A else d
col = beach.col

def begin(n):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = 0, n - 1; return sc

def key(o, path, f, v=None, interp=None):
    if v is not None: setattr(o, path, v)
    o.keyframe_insert(path, frame=f)

def move(o, keys, H=None, dz=0.0):
    """keys: (frame, x, y[, z]); z from the ground function H when not given"""
    for k in keys:
        f, x, y = k[:3]; z = k[3] if len(k) > 3 else (H(x, y) if H else 0.0) + dz
        o.location = (x, y, z); o.keyframe_insert("location", frame=f)

def linear(o):
    a = o.animation_data.action if o.animation_data else None
    if a is None: return
    for layer in a.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

def cards(sc, sid, cam, paths, H=None, self_lit=.55):
    """place the shot's cards and move them: paths = {who: [(frame, x, y[, z]), ...]}"""
    d = os.path.join(EP, "build", "cards_s" + sid); who = list(cast.SHOTS[sid][1]); n = cast.SHOTS[sid][0]
    characters.place_cards(sc, d, who, cam, self_lit, ground=None); out = {}
    for w in who:
        card = bpy.data.objects["Card_" + w]; disc = bpy.data.objects.get("Contact_" + w)
        for o in (card, disc):
            if o is None: continue
            for uc in list(o.users_collection): uc.objects.unlink(o)
            col("L_OBJECTS").objects.link(o)
            for f in range(-1, n + 12):
                for dp in ("hide_render", "hide_viewport", "location"):
                    try: o.keyframe_delete(dp, frame=f)
                    except RuntimeError: pass
            o.hide_render = o.hide_viewport = False
        card["rc_anchors"] = os.path.join(d, "cards", w, "anchors.json")
        if w in paths: move(card, paths[w], H); linear(card)
        else: card.location = (0, 0, -50)                                  # not used in this shot's blocking
        out[w] = card
    return out

def camera(keys, n, amp=.008, rot=.18, seed=3, clip=4000.0):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col("CAM").objects.link(cam); bpy.context.scene.camera = cam
    cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24; cam.data.clip_end = clip; cam.data.clip_start = .05
    for f, p, a, lens in keys:
        cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f)
        cam.data.dof.focus_distance = max(.3, (Vector(a) - Vector(p)).length); cam.data.dof.keyframe_insert("focus_distance", frame=f)   # a real lens: the subject sharp, the rest soft
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0
    if amp: street.handheld(cam, 0, n - 1, amp=amp, rot_deg=rot, seed=seed)
    return cam

FLAT = ("ink_", "chalk", "gull", "foam", "ring_", "blast_")          # drawn lettering, chalk, effects: stay flat on purpose

def ink(name, rgb, strength=0.0, rough=.6):
    """a painted surface, not a flat colour (CB 2026-11-20: "de la 3D dure, aucun travail de texture"): the roughness varies (worn patches),
    a fine grain catches the sun, the edges are rounded for the highlight (Bevel), dirt sits in the creases (AO) and dust on what faces up"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if strength: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = strength
    if strength or name.startswith(FLAT): return m
    import toon
    if toon.STYLE == "drawn":                                                                        # THE DRAWN WORLD (CB 2026-11-20, style locked): flat decided colour, rounded edge for the highlight; the ink line comes from toon.ink_all
        bev = N.new("ShaderNodeBevel"); bev.samples = 4; bev.inputs["Radius"].default_value = .02; L.new(bev.outputs["Normal"], b.inputs["Normal"]); return m
    tc = N.new("ShaderNodeTexCoord"); big = N.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 1.6; big.inputs["Detail"].default_value = 6; big.inputs["Roughness"].default_value = .65
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 60; fine.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], big.inputs["Vector"]); L.new(tc.outputs["Object"], fine.inputs["Vector"])
    def M(op, a, bv, cv=None):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = True
        for i, v in enumerate((a, bv, cv)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    L.new(M("MULTIPLY_ADD", big.outputs["Fac"], .5, rough - .22), b.inputs["Roughness"])                    # worn / polished patches
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = .35; ao.samples = 4
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
    dust = M("MULTIPLY", M("MULTIPLY_ADD", sep.outputs["Z"], 1.6, -.75), M("MULTIPLY_ADD", big.outputs["Fac"], 1.4, -.25))   # dust settles on what faces the sky
    grime = M("MULTIPLY", M("SUBTRACT", 1.0, ao.outputs["AO"]), 1.5)
    c1 = N.new("ShaderNodeMix"); c1.data_type = "RGBA"; c1.inputs[6].default_value = (*rgb, 1); c1.inputs[7].default_value = (rgb[0] * .22 + .01, rgb[1] * .2 + .008, rgb[2] * .18 + .006, 1); L.new(grime, c1.inputs[0])
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.inputs[7].default_value = (.46, .38, .27, 1); L.new(M("MULTIPLY", dust, .45), c2.inputs[0]); L.new(c1.outputs[2], c2.inputs[6])
    L.new(c2.outputs[2], b.inputs["Base Color"])
    bev = N.new("ShaderNodeBevel"); bev.samples = 4; bev.inputs["Radius"].default_value = .025
    bmp = N.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = .06; bmp.inputs["Distance"].default_value = .01
    L.new(fine.outputs["Fac"], bmp.inputs["Height"]); L.new(bev.outputs["Normal"], bmp.inputs["Normal"]); L.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m

def label(name, body, size, loc, rot, mat, c=None, parent=None, extrude=.004, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.align_x = align; cu.align_y = "CENTER"; cu.extrude = extrude
    o = bpy.data.objects.new(name, cu); (c or col("L_OBJECTS")).objects.link(o); cu.materials.append(mat); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o

def box(name, size, loc, mat, c=None, rot=(0, 0, 0), bevel=.01, parent=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel: bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=2, affect="EDGES")
    o = beach.mesh_obj(name, bm, mat, c or col("L_OBJECTS"), smooth=False); o.location = loc; o.rotation_euler = rot
    if parent: o.parent = parent
    return o

def cyl(name, r, h, loc, mat, c=None, rot=(0, 0, 0), seg=20, parent=None, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = beach.mesh_obj(name, bm, mat, c or col("L_OBJECTS"), smooth=True); o.location = loc; o.rotation_euler = rot
    try: o.data.set_sharp_from_angle(angle=.9)                                                      # flat caps, round side (else a wheel shades like a ball)
    except Exception: pass
    if parent: o.parent = parent
    return o

def blob(name, r, loc, mat, c=None, seed=1, squash=(1, 1, .6), sub=3):
    R = random.Random(seed); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    a, b, cc = R.uniform(2, 5), R.uniform(2, 5), R.uniform(0, 6)
    for v in bm.verts: v.co *= 1 + .16 * math.sin(v.co.x * a / r + cc) * math.cos(v.co.y * b / r); v.co = Vector((v.co.x * squash[0], v.co.y * squash[1], v.co.z * squash[2]))
    o = beach.mesh_obj(name, bm, mat, c or col("L_OBJECTS"), smooth=True); o.location = loc; return o

def show(o, f0, f1=None):
    """the object exists only between two frames (it must enter the frame by an ACTION: use this only out of frame or behind a flash)"""
    for f, h in ((f0 - 1, True), (f0, False)) + (((f1, True),) if f1 is not None else ()):
        o.hide_render = o.hide_viewport = h; o.keyframe_insert("hide_render", frame=f); o.keyframe_insert("hide_viewport", frame=f)

def fx(sc, specs):
    before = set(bpy.data.objects); vfx.apply(sc, specs)
    for o in [o for o in bpy.data.objects if o not in before]:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        col("L_FX").objects.link(o)

def flash(sc, f, frames=4, peak=3.0):
    """white flash on the image itself: exposure keyed in the view settings (2-4 frames, as measured on the references)"""
    v = sc.view_settings; e0 = v.exposure
    for ff, e in ((f - 1, e0), (f, e0 + peak), (f + 1, e0 + peak * .8), (f + frames, e0)): v.exposure = e; v.keyframe_insert("exposure", frame=ff)
    v.exposure = e0

def grade(sc, Mo, haze):
    """THE FINISH OF THE IMAGE (CB 2026-11-20: "aucun travail de color grading, de lighting"): air between the lens and the far things
    (distance haze from the mist pass, never on the sky), a soft bloom on what the sun burns, warm highlights over cool shadows,
    saturation, a vignette that holds the eye, a light sharpen after the denoiser"""
    vl = sc.view_layers[0]; vl.use_pass_mist = True; vl.use_pass_z = True; ms = sc.world.mist_settings; ms.start = 6; ms.depth = 260; ms.falloff = "QUADRATIC"
    ng = bpy.data.node_groups.new("rc_finish", "CompositorNodeTree"); sc.compositing_node_group = ng; N, L = ng.nodes, ng.links
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor"); out = N.new("NodeGroupOutput"); rl = N.new("CompositorNodeRLayers"); rl.scene = sc
    def col_io(n): return [i for i in n.inputs if i.bl_idname == "NodeSocketColor"], [o for o in n.outputs if o.bl_idname == "NodeSocketColor"]
    last = rl.outputs["Image"]
    if haze:
        near = N.new("ShaderNodeMath"); near.operation = "LESS_THAN"; near.inputs[1].default_value = 3000.0; L.new(rl.outputs["Depth"], near.inputs[0])
        fac = N.new("ShaderNodeMath"); fac.operation = "MULTIPLY"; L.new(rl.outputs["Mist"], fac.inputs[0]); L.new(near.outputs[0], fac.inputs[1])
        f2 = N.new("ShaderNodeMath"); f2.operation = "MULTIPLY"; f2.inputs[1].default_value = haze; L.new(fac.outputs[0], f2.inputs[0])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; ci, co = col_io(mx); ci[1].default_value = Mo.get("haze_color", (.62, .78, .95, 1)); L.new(f2.outputs[0], mx.inputs[0]); L.new(last, ci[0]); last = co[0]
    gl = N.new("CompositorNodeGlare"); gl.inputs["Type"].default_value = "Bloom"; gl.inputs["Threshold"].default_value = Mo.get("bloom_at", 1.1); gl.inputs["Strength"].default_value = Mo.get("bloom", .35); gl.inputs["Size"].default_value = .55
    L.new(last, gl.inputs["Image"]); last = gl.outputs["Image"]
    cb = N.new("ColorBalance" if False else "CompositorNodeColorBalance"); cs = [i for i in cb.inputs if i.bl_idname == "NodeSocketColor"]
    for sock, v in zip(cs[1:4], (Mo.get("lift", (.965, .995, 1.045)), Mo.get("gamma", (1.0, 1.0, 1.0)), Mo.get("gain", (1.06, 1.0, .93)))): sock.default_value = (*v, 1.0)
    L.new(last, cb.inputs["Image"]); last = cb.outputs[0]
    hsv = N.new("CompositorNodeHueSat"); hsv.inputs["Saturation"].default_value = Mo.get("sat", 1.0) * 1.06; L.new(last, hsv.inputs["Image"]); last = hsv.outputs[0]
    ell = N.new("CompositorNodeEllipseMask"); ell.inputs["Size"].default_value = (1.0, 1.0); ell.inputs["Value"].default_value = 1.0
    bl = N.new("CompositorNodeBlur"); px = int(sc.render.resolution_x * .28); bl.inputs["Size"].default_value = (px, px)
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 1 - Mo.get("vignette", .22); mr.inputs["To Max"].default_value = 1.0
    vm = N.new("ShaderNodeMix"); vm.data_type = "RGBA"; vm.blend_type = "MULTIPLY"; vm.inputs[0].default_value = 1.0; ci, co = col_io(vm)
    L.new(ell.outputs[0], bl.inputs["Image"]); L.new(bl.outputs[0], mr.inputs["Value"]); L.new(last, ci[0]); L.new(mr.outputs[0], ci[1]); last = co[0]
    sh = N.new("CompositorNodeFilter"); sh.inputs["Type"].default_value = "Diamond Sharpen"; sh.inputs["Factor"].default_value = .12; L.new(last, sh.inputs["Image"]); last = sh.outputs[0]
    L.new(last, out.inputs[0]); sc.render.use_compositing = True

def finish(sc, Mo, expo=(), haze=.5):
    v = sc.view_settings; v.view_transform = "Standard"; v.look = Mo.get("contrast", "Medium High Contrast"); v.exposure = Mo["exposure"]
    for f, d in expo: v.exposure = Mo["exposure"] + d; v.keyframe_insert("exposure", frame=f)       # light per view (rule L3)
    v.exposure = Mo["exposure"] + (expo[0][1] if expo else 0)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .3
    w, h = map(int, opt("--res", "270x480").split("x")); render.setup(sc, "CYCLES", (w, h), int(opt("--samples", "16")), 0); grade(sc, Mo, haze)

def output(sc, out):
    bpy.ops.wm.save_as_mainfile(filepath=out)
    if "--still" in A:
        for tok in A[A.index("--still") + 1:]:
            if tok.startswith("--"): break
            f, png = tok.split(":"); sc.frame_set(int(f)); sc.render.filepath = png; bpy.ops.render.render(write_still=True); print("STILL", png)
    if opt("--anim"):
        sc.render.filepath = os.path.join(opt("--anim"), "f"); sc.render.image_settings.file_format = "PNG"; bpy.ops.render.render(animation=True)
