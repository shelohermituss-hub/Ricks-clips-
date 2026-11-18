"""rc.characters — E. Character Integration (Mission 2, 2026-11-18). Runs inside Blender.
The 2D cast stays (it is the fortress style too); the cards come from the card drawing service (render_gpu.mjs --export-lock --cards-only
--card-frames a-b, content-cached) and are placed by the proven from_lock.card(): image sequence keyed per frame, feet on the plan
position, turned to the lens about Z. Integration added here:
  * the card material casts a real shadow of its silhouette (alpha) and is lit partly by the scene (self_lit < 1), so the place light
    reaches the character instead of a pasted sticker
  * a soft contact shadow disc under the feet (AO-like darkening where the body meets the ground), keyed with the card's visibility
  * cards are put in collection RC_CHARACTERS"""
import os, sys
import bpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rc import SKILL  # noqa: E402

def _contact_mat():
    m = bpy.data.materials.get("rc_contact")
    if m: return m
    m = bpy.data.materials.new("rc_contact"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); tr = N.new("ShaderNodeBsdfTransparent"); dk = N.new("ShaderNodeBsdfDiffuse"); dk.inputs[0].default_value = (.02, .02, .015, 1)
    mix = N.new("ShaderNodeMixShader"); gr = N.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"; tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 1); L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], gr.inputs[0])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 1.6; L.new(gr.outputs["Fac"], pw.inputs[0])
    k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = .55; L.new(pw.outputs[0], k.inputs[0])
    L.new(k.outputs[0], mix.inputs[0]); L.new(tr.outputs[0], mix.inputs[1]); L.new(dk.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs[0])
    try: m.surface_render_method = "DITHERED"
    except Exception: pass
    return m

def active_camera_proxy(scene):
    """an empty that sits, on every frame, where the ACTIVE camera is (timeline markers switch cameras between shots): cards track it,
    so each card faces the lens of the shot being rendered. Keyed per frame from the markers: a pure function of the frame."""
    e = bpy.data.objects.get("rc_active_cam")
    if e: return e
    e = bpy.data.objects.new("rc_active_cam", None); scene.collection.objects.link(e)
    marks = sorted([m for m in scene.timeline_markers if m.camera], key=lambda m: m.frame)
    for f in range(scene.frame_start, scene.frame_end + 1):
        cam = ([m.camera for m in marks if m.frame <= f] or [scene.camera])[-1]; scene.frame_set(f)
        e.location = cam.matrix_world.translation; e.keyframe_insert("location", frame=f)
    return e

def _snap_to_ground(ob, ground):
    """keep the card's keyed feet ON the terrain: every location key gets z = ground height under (x, y) + its own z offset"""
    from rc import envbuild
    ad = ob.animation_data
    if not (ground and ad and ad.action): return 0
    sys.path.insert(0, os.path.join(SKILL, "templates")); from blender_look import from_lock
    F = {fc.array_index: fc for fc in from_lock._fcurves(ad.action) if fc.data_path == "location"}; n = 0
    for k in F[2].keyframe_points:
        f = k.co[0]; x, y = F[0].evaluate(f), F[1].evaluate(f); k.co[1] = k.co[1] + envbuild.ground_z(ground, x, y); n += 1
    return n

def hold_prop(scene, card, src_col, spec):
    """HYBRID 2D/3D: a 3D asset held in a card's hand. The prop is a collection instance parented to the card, keyed per run to the
    hand position the drawing has (index.json runs[].hands, card-local metres), so it moves with the drawn hand."""
    ob = card["object"]; e = bpy.data.objects.new("held_%s_%s" % (spec["who"], spec["asset"]), None); e.instance_type = "COLLECTION"; e.instance_collection = src_col
    scene.collection.objects.link(e); e.parent = ob; e.scale = [spec.get("scale", 1.0)] * 3; hi = spec.get("hand", 1); off = spec.get("offset", [0, 0, 0])
    for r in card["index"]["runs"]:
        h = (r.get("hands") or [[0, .9], [0, .9]]); u, v = h[min(hi, len(h) - 1)]
        e.location = (u + off[0], -.03 + off[1], v + off[2]); e.keyframe_insert("location", frame=r["f0"])
        e.hide_render = not r.get("visible", True) or (spec.get("frames") and not (spec["frames"][0] <= r["f0"] <= spec["frames"][1])); e.keyframe_insert("hide_render", frame=r["f0"])
    if e.animation_data and e.animation_data.action:
        sys.path.insert(0, os.path.join(SKILL, "templates")); from blender_look import from_lock
        for fc in from_lock._fcurves(e.animation_data.action):
            for k in fc.keyframe_points: k.interpolation = "CONSTANT"
    return e

def place_cards(scene, lock_dir, who_list, cam, self_lit=.55, contact=True, ground=None):
    sys.path.insert(0, os.path.join(SKILL, "templates"))
    from blender_look import from_lock
    col = bpy.data.collections.get("RC_CHARACTERS") or bpy.data.collections.new("RC_CHARACTERS")
    if col.name not in scene.collection.children: scene.collection.children.link(col)
    out = {}
    for who in who_list:
        target = active_camera_proxy(scene) if len([m for m in scene.timeline_markers if m.camera]) > 1 else cam
        c = from_lock.card(scene, lock_dir, who, target, self_lit=self_lit)
        ob = c["object"]; c["ground_keys"] = _snap_to_ground(ob, ground)
        for cc in list(ob.users_collection): cc.objects.unlink(ob)
        col.objects.link(ob); ob.visible_shadow = True
        if contact:                                                       # contact shadow disc, follows the card's keyed location and visibility
            r = (c["index"]["px"][0] * c["index"]["metres_per_px"]) * .32
            bpy.ops.mesh.primitive_circle_add(vertices=32, radius=r, fill_type="NGON"); d = bpy.context.object; d.name = "Contact_" + who
            for cc in list(d.users_collection): cc.objects.unlink(d)
            col.objects.link(d); d.data.materials.append(_contact_mat()); d.visible_shadow = False; d.scale = (1, .55, 1)
            cp = d.constraints.new("COPY_LOCATION"); cp.target = ob; cp.use_offset = False
            d.location = (0, 0, .015); cp.use_offset = True
            if ob.animation_data and ob.animation_data.action:
                for f in sorted({int(k.co[0]) for fc in from_lock._fcurves(ob.animation_data.action) if fc.data_path == "hide_render" for k in fc.keyframe_points}):
                    scene.frame_set(f); d.hide_render = ob.hide_render; d.keyframe_insert("hide_render", frame=f)
        out[who] = c
    return out
