"""crash_instinct: the "DAYS SINCE LAST CRASH" sign (shot 4, references/crash_instinct/shots/s04.md), built for the frame: two galvanised
steel posts, a red header plate with white lettering, a black split-flap box with one big white digit. flip(root, frame) plays the flap:
the top half of the old digit rotates 180 deg about the hinge and claps down; its back carries the bottom half of the new digit.
Built facing -Y, then turned by `face_deg` (90 = faces +X, the road). Real materials (rc.look.tex), never a flat colour."""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "blender"))
from rc.look import tex, mat, srgb, mesh_obj  # noqa: E402

W, HEAD_H, BOX_H, Z0 = .95, .42, 1.0, 1.25          # plate width, header height, flap box height, bottom of the box above the ground
HINGE = Z0 + BOX_H / 2

def _text_mesh(name, body, size, z, material, c, y=-.02, offset=.0, depth=.004):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.offset = offset; cu.extrude = depth
    tmp = bpy.data.objects.new(name + "_tmp", cu); bpy.context.scene.collection.objects.link(tmp)
    tmp.rotation_euler = (math.radians(90), 0, 0); tmp.location = (0, y, z); bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get())); me.transform(tmp.matrix_world)
    bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu); me.name = name; me.materials.append(material)
    o = bpy.data.objects.new(name, me); c.objects.link(o); return o

def _half(o, keep_top):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, HINGE), plane_no=(0, 0, 1), clear_inner=keep_top, clear_outer=not keep_top)
    bm.to_mesh(o.data); bm.free(); return o

def _box(name, c, size, loc, m):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts); bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    return mesh_obj(name, bm, m, c)

def build(c, at=(0.4, -3.0), face_deg=90.0, old="7", new="0"):
    root = bpy.data.objects.new("crash_sign", None); c.objects.link(root); root.location = (at[0], at[1], 0); root.rotation_euler = (0, 0, math.radians(face_deg))
    steel = tex("sign_steel", "metal_plate", tile=.6, value=1.25, spec=.5, macro=.1); steel.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = .85
    red = tex("sign_red", "painted_metal_shutter", tile=1.2, recolor="#c8202a", value=1.0, spec=.4, macro=.12, untile=False)
    black = tex("sign_black", "painted_metal_shutter", tile=1.2, recolor="#16171a", value=1.0, spec=.35, macro=.1, untile=False)
    white = mat("sign_white", "#f4f3ee", .5); frame = mat("sign_frame", "#c9ccd0", .4, .6)
    parts = []
    for k, x in enumerate((-W / 2 + .1, W / 2 - .1)):                                           # two posts, sunk in the ground
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=.028, radius2=.028, depth=3.3); bmesh.ops.translate(bm, vec=(x, .03, 1.35), verts=bm.verts)
        parts.append(mesh_obj("sign_post%d" % k, bm, steel, c, smooth=True))
    top = Z0 + BOX_H + .04
    parts.append(_box("sign_head_frame", c, (W + .04, .018, HEAD_H + .04), (0, 0, top + HEAD_H / 2), frame))
    parts.append(_box("sign_head", c, (W, .02, HEAD_H), (0, -.004, top + HEAD_H / 2), red))
    parts.append(_text_mesh("sign_text1", "DAYS SINCE", .135, top + HEAD_H * .72, white, c, y=-.016, offset=.006))
    parts.append(_text_mesh("sign_text2", "LAST CRASH", .135, top + HEAD_H * .28, white, c, y=-.016, offset=.006))
    BW = .66
    parts.append(_box("sign_box_frame", c, (BW + .06, .05, BOX_H + .06), (0, .012, Z0 + BOX_H / 2), frame))
    parts.append(_box("sign_box", c, (BW, .05, BOX_H), (0, .004, Z0 + BOX_H / 2), black))
    parts.append(_box("sign_hinge", c, (BW, .012, .012), (0, -.026, HINGE), frame))
    parts.append(_half(_text_mesh("digit_new_top", new, .86, HINGE, white, c, y=-.024, offset=.012), True))      # behind the flap, revealed
    parts.append(_half(_text_mesh("digit_old_bottom", old, .86, HINGE, white, c, y=-.024, offset=.012), False))  # covered when the flap lands
    flap = bpy.data.objects.new("sign_flap", None); c.objects.link(flap); flap.location = (0, -.03, HINGE)
    plate = _box("flap_plate", c, (BW - .02, .006, BOX_H / 2 - .012), (0, -.034, HINGE + BOX_H / 4), black)
    old_top = _half(_text_mesh("digit_old_top", old, .86, HINGE, white, c, y=-.04, offset=.012), True)
    new_bot = _half(_text_mesh("digit_new_bottom", new, .86, HINGE, white, c, y=-.04, offset=.012), False)       # built where it ends, then turned back onto the flap's back
    Minv = Matrix.Translation((0, -.03, HINGE)) @ Matrix.Rotation(-math.pi, 4, "X") @ Matrix.Translation((0, .03, -HINGE)); new_bot.data.transform(Minv)
    for o in (plate, old_top, new_bot):
        o.data.transform(Matrix.Translation((0, .03, -HINGE))); o.parent = flap
    flap.parent = root
    for o in parts: o.parent = root
    root["flap"] = flap.name
    return root

def flip(root, frame, frames=5):
    """the flap claps down over `frames` frames (accelerating like a falling flap), overshoots 6 deg into the box face and settles"""
    flap = bpy.data.objects[root["flap"]]
    flap.rotation_euler = (0, 0, 0); flap.keyframe_insert("rotation_euler", frame=frame - 1)
    for i in range(1, frames + 1):
        t = i / frames; flap.rotation_euler = (math.pi * t * t, 0, 0); flap.keyframe_insert("rotation_euler", frame=frame - 1 + i)
    for f, a in ((frame + frames, 174), (frame + frames + 2, 180)):
        flap.rotation_euler = (math.radians(a), 0, 0); flap.keyframe_insert("rotation_euler", frame=f)

def shake(root, frame, deg=2.2, frames=14):
    """the whole sign rocks on its posts when something heavy hits the ground nearby"""
    rz = root.rotation_euler.z
    for f in range(frame - 1, frame + frames + 1):
        t = f - frame; a = math.radians(deg) * math.exp(-t / 5.0) * math.sin(t * 1.1) if t >= 0 else 0.0
        root.rotation_euler = (a * .4, a, rz); root.keyframe_insert("rotation_euler", frame=f)
