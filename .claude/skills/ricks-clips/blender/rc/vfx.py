"""rc.vfx — H. VFX Engine (Mission 2, 2026-11-18). Runs inside Blender. Effects live IN the 3D scene (lit, occluded, shadowed), are
seeded and baked, and are triggered at a frame by place.json "fx":
  dust_burst  {at, frame, count, radius, height, color, seed}  a ring of soft dust puffs that rise, spread and fade (impact, set-down);
              each puff is a small volume sphere whose scale/density are keyed per frame from a pure function of the frame
Volumes render in Cycles and EEVEE; the puff count stays small (tens), so it is cheap."""
import math, random
import bpy

def _dust_mat(color, name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); v = N.new("ShaderNodeVolumePrincipled"); v.inputs["Color"].default_value = (*color, 1)
    tc = N.new("ShaderNodeTexCoord"); gr = N.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"; L.new(tc.outputs["Object"], gr.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    a = N.new("ShaderNodeMath"); a.operation = "MULTIPLY"; L.new(gr.outputs["Fac"], a.inputs[0]); L.new(nz.outputs["Fac"], a.inputs[1])
    d = N.new("ShaderNodeMath"); d.operation = "MULTIPLY"; d.name = "density"; d.inputs[1].default_value = 2.5; L.new(a.outputs[0], d.inputs[0])
    L.new(d.outputs[0], v.inputs["Density"]); L.new(v.outputs[0], out.inputs["Volume"]); return m

def dust_burst(scene, name, at, frame, count=14, radius=1.2, height=.9, color=(.62, .55, .44), seed=1, life=45):
    R = random.Random(seed); col = bpy.data.collections.get("RC_FX") or bpy.data.collections.new("RC_FX")
    if col.name not in scene.collection.children: scene.collection.children.link(col)
    for i in range(count):
        a = 2 * math.pi * i / count + R.uniform(-.2, .2); sp = R.uniform(.6, 1.2); m = _dust_mat(color, "%s_dust_%02d" % (name, i))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0); o = bpy.context.object; o.name = "%s_puff_%02d" % (name, i)
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o); o.data.materials.append(m); o.visible_shadow = False; dn = m.node_tree.nodes["density"].inputs[1]
        for f in range(frame - 1, frame + life + 1):
            k = max(0.0, (f - frame) / life); r = radius * sp * (1 - (1 - k) ** 2); s = .05 + .55 * sp * k ** .6
            o.location = (at[0] + math.cos(a) * r, at[1] + math.sin(a) * r, at[2] + .1 + height * k ** .8 * sp)
            o.scale = (s, s, s * .8); o.keyframe_insert("location", frame=f); o.keyframe_insert("scale", frame=f)
            o.hide_render = f < frame or f >= frame + life; o.keyframe_insert("hide_render", frame=f)
            dn.default_value = 2.5 * (1 - k) ** 1.5 if f >= frame else 0; dn.keyframe_insert("default_value", frame=f)
    return count

def apply(scene, specs):
    n = 0
    for s in specs:
        if s["type"] == "dust_burst":
            n += dust_burst(scene, s.get("name", "dust"), s["at"], s["frame"], s.get("count", 14), s.get("radius", 1.2), s.get("height", .9), tuple(s.get("color", (.62, .55, .44))), s.get("seed", 1), s.get("life", 45))
    return n
