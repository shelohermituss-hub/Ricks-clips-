"""Blender-side checks for the WP-3..8 modules (run by tools/tests/test_rc.py::test_modules; prints one 'WPT <json>' line).
Each check builds its own tiny scene, so it proves the module itself, not the farmyard data."""
import bpy, json, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rc import physics, lookdev, vfx, qa, animate

R = {}
def centre(o): return sum((o.matrix_world @ Vector(b) for b in o.bound_box), Vector()) / 8
def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 60
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=20, size=40); g = bpy.context.object; g.name = "terrain"; return sc, g

# 1 glass: shards start at the pane (not the world origin), all fall, land on the ground, none flies off
sc, g = fresh()
bpy.ops.mesh.primitive_grid_add(x_subdivisions=4, y_subdivisions=4, size=.5, location=(5, 5, 1.3), rotation=(1.5708, 0, 0)); p = bpy.context.object; p.name = "pane"
bpy.ops.object.transform_apply(rotation=True); m = p.modifiers.new("s", "SOLIDIFY"); m.thickness = .005; bpy.ops.object.modifier_apply(modifier="s")
r = physics.glass_shatter(sc, {"pane": "pane", "frames": [1, 60], "at_frame": 10, "cuts": 3, "seed": 3, "impulse": {"from": [3.6, 1.4, 1.5], "to": "pane", "frames": 7}}, None, g)
sh = [o for o in bpy.data.objects if o.name.startswith("pane.")]
sc.frame_set(9); start = [centre(o) for o in sh]; sc.frame_set(60); end = [centre(o) for o in sh]
R["glass"] = {"shards": len(sh), "start_at_pane": all((s - Vector((5, 5, 1.3))).length < .4 for s in start), "on_ground": all(e.z < .1 for e in end),
              "max_travel_m": round(max((e - s).length for s, e in zip(start, end)), 2), "joints": r["joints"]}

# 2 collapse: a stack of jointed boxes (multi-part asset joined into one body) does not explode
sc, g = fresh(); col = bpy.data.collections.new("asset"); bpy.context.scene.collection.children.link(col)
for i, (loc, sz) in enumerate((((0, 0, .25), .5), ((0, -.24, .3), .06))):          # a crate body and a latch overlapping it
    bpy.ops.mesh.primitive_cube_add(size=sz, location=loc); o = bpy.context.object; o.name = "part%d" % i
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
r = physics.collapse(sc, {"items": [{"asset": "a", "at": [0, 0, 0]}, {"asset": "a", "at": [0, 0, .52]}], "frames": [1, 60], "at_frame": 5}, lambda a: col, g)
R["collapse"] = {"pieces": r["pieces"], "max_moved_m": r["max_moved_m"]}

# 3 deform: vertices move, the object does not
sc, g = fresh(); bpy.ops.mesh.primitive_uv_sphere_add(radius=.5, location=(0, 0, .5)); s = bpy.context.object; s.name = "barrel"; loc0 = s.location.copy()
r = physics.deform(sc, {"object": "barrel", "point": [0, -.5, .5], "direction": [0, 1, 0], "radius": .3, "depth": .1, "at_frame": 20}, None, g)
sc.frame_set(30); R["deform"] = {"vertices": r["deformed_vertices"], "object_still": (s.location - loc0).length < 1e-6, "key_value_after": round(s.data.shape_keys.key_blocks[-1].value, 2)}

# 4 compositor grade on the Blender 5 API: a group with an output, used by the scene
sc, g = fresh(); ng = lookdev.grade(sc, {"saturation": .9, "gain": 1.1, "vignette": .3})
R["grade"] = {"group": sc.compositing_node_group == ng, "has_output": any(n.bl_idname == "NodeGroupOutput" for n in ng.nodes), "nodes": len(ng.nodes)}

# 5 penetration gate measures a box pushed 20 cm into the ground
sc, g = fresh(); pc = bpy.data.collections.new("RC_PHYSICS"); sc.collection.children.link(pc)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .3)); b = bpy.context.object
for c in list(b.users_collection): c.objects.unlink(b)
pc.objects.link(b); b.keyframe_insert("location", frame=1)
R["penetration"] = qa.ground_penetration(sc, frames=[1])

# 6 vfx sparks and explosion build objects at their frame
sc, g = fresh(); n1 = vfx.sparks(sc, {"at": [0, 0, 1], "frame": 10, "count": 20, "seed": 2}); n2 = vfx.explosion_stylized(sc, {"at": [2, 0, 0], "frame": 15, "seed": 4})
R["vfx"] = {"sparks": n1, "explosion": n2}

print("WPT " + json.dumps(R))
