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

def place_cards(scene, lock_dir, who_list, cam, self_lit=.55, contact=True):
    sys.path.insert(0, os.path.join(SKILL, "templates"))
    from blender_look import from_lock
    col = bpy.data.collections.get("RC_CHARACTERS") or bpy.data.collections.new("RC_CHARACTERS")
    if col.name not in scene.collection.children: scene.collection.children.link(col)
    out = {}
    for who in who_list:
        c = from_lock.card(scene, lock_dir, who, cam, self_lit=self_lit)
        ob = c["object"]
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
