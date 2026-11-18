"""rc.qa — K. Quality Assurance, scene side (runs inside Blender). Mission 1, 2026-11-18.
Measures what a scene or an asset REALLY contains, so a gate never has to trust that a module "exists":
  objects (by type), mesh datablocks, instances drawn (depsgraph), triangles evaluated (instances counted at their real count),
  primitive-like meshes (a box, a low cylinder, a bare plane: <= PRIM_VERTS vertices), textured materials (image or procedural
  texture node feeding the shader), bounding dimensions in metres.
    stats = qa.scene_stats()            the whole evaluated scene
    stats = qa.collection_stats(col)    one asset collection (used at ingest)
Thresholds for the gates live in production/config/rc_gates.json (read by tools/production_controller.py)."""
import bpy
from mathutils import Vector

EXEMPT = {"RC_CHARACTERS"}   # collections whose flat meshes are intended (character cards), counted apart
PRIM_VERTS = 40                                   # a mesh with this many vertices or fewer reads as a primitive stand-in (box 8, cylinder 2x16=32)
TEX_NODES = {"TEX_IMAGE", "TEX_NOISE", "TEX_VORONOI", "TEX_WAVE", "TEX_MUSGRAVE", "TEX_BRICK", "TEX_CHECKER", "TEX_MAGIC", "TEX_GRADIENT"}

def textured(m):
    return bool(m and m.use_nodes and any(n.type in TEX_NODES for n in m.node_tree.nodes))

def _mesh_tris(me):
    me.calc_loop_triangles(); return len(me.loop_triangles)

def _stats(objs, depsgraph):
    mesh_objs = [o for o in objs if o.type == "MESH"]
    tris = prim = prim_tris = pts = cards = 0; mats = set(); lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3); per_mesh = {}
    for o in mesh_objs:
        ev = o.evaluated_get(depsgraph); me = ev.to_mesh()
        if me is None: continue
        t = _mesh_tris(me); nv = len(me.vertices); tris += t
        if len(me.polygons) == 0: ev.to_mesh_clear(); pts += 1; continue        # point clouds driving geometry-node instances: not geometry, not a primitive
        if any(c.name in EXEMPT for c in o.users_collection): ev.to_mesh_clear(); cards += 1; continue   # 2D character cards + contact discs: flat by design
        if nv <= PRIM_VERTS: prim += 1; prim_tris += t
        for s in o.material_slots:
            if s.material: mats.add(s.material)
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
        per_mesh[o.name] = {"verts": nv, "tris": t}; ev.to_mesh_clear()
    dims = [round(x, 3) for x in (hi - lo)] if mesh_objs else [0, 0, 0]
    return {"objects": len(objs), "mesh_objects": len(mesh_objs), "mesh_datablocks": len({o.data.name for o in mesh_objs}), "tris": tris,
            "instancer_objects": pts, "character_card_objects": cards, "primitive_like_objects": prim, "primitive_ratio": round(prim / max(1, len(mesh_objs) - pts - cards), 3), "primitive_tris_ratio": round(prim_tris / max(1, tris), 4),
            "materials": len(mats), "textured_materials": sum(1 for m in mats if textured(m)), "dims_m": dims,
            "largest_meshes": sorted(per_mesh.items(), key=lambda kv: -kv[1]["tris"])[:5]}

def collection_stats(col):
    return _stats(list(col.all_objects), bpy.context.evaluated_depsgraph_get())

def scene_stats(scene=None):
    scene = scene or bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
    s = _stats(list(scene.objects), dg)
    inst = 0; inst_tris = 0; imats = set()
    for i in dg.object_instances:                               # what the renderer really draws (geometry-node and collection instances)
        if i.is_instance and i.object.type == "MESH":
            inst += 1
            for sl in i.object.material_slots:
                if sl.material: imats.add(sl.material.original)
            me = i.object.data if hasattr(i.object, "data") else None
            if me is not None and hasattr(me, "polygons"): inst_tris += sum(len(p.vertices) - 2 for p in me.polygons)
    by_type = {}
    for o in scene.objects: by_type[o.type] = by_type.get(o.type, 0) + 1
    smats = {sl.material for o in scene.objects if o.type == "MESH" for sl in o.material_slots if sl.material}
    allm = smats | imats                                         # materials of everything drawn, instanced assets included (a scene gate must see them)
    s["materials"] = len(allm); s["textured_materials"] = sum(1 for m in allm if textured(m)); s["untextured_material_names"] = sorted(m.name for m in allm if not textured(m))[:20]
    s.update({"instances_drawn": inst, "instanced_tris": inst_tris, "total_tris_drawn": s["tris"] + inst_tris, "by_type": by_type,
              "instance_ratio": round(inst / max(1, inst + s["mesh_objects"]), 4)})
    return s

def character_contact(scene=None, step=15, tol=.02):
    """phase-4 gate: on sampled frames, every visible card's feet are on the ground (|card z - terrain z| <= tol) and it casts a shadow"""
    from rc import envbuild
    scene = scene or bpy.context.scene; ground = bpy.data.objects.get("terrain"); out = {}
    for o in [o for o in scene.objects if o.name.startswith("Card_")]:
        worst = 0.0; n = 0
        for f in range(scene.frame_start, scene.frame_end + 1, step):
            scene.frame_set(f)
            if o.hide_render: continue
            p = o.matrix_world.translation; dz = abs(p.z - envbuild.ground_z(ground, p.x, p.y)); worst = max(worst, dz); n += 1
        out[o.name[5:]] = {"frames_checked": n, "max_gap_m": round(worst, 4), "ok": n > 0 and worst <= tol, "casts_shadow": bool(o.visible_shadow)}
    return out

def animation_keys(names):
    """phase-5 gate: each named target carries keys (a recipe really baked)"""
    out = {}
    for nm in names:
        o = bpy.data.objects.get(nm); ad = o.animation_data if o else None
        out[nm] = {"exists": o is not None, "keyed": bool(ad and ad.action)}
    return out
