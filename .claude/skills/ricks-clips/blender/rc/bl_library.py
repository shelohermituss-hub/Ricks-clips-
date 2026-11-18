"""rc.bl_library — Blender side of the Asset Library (runs inside Blender; called by rc.library). Mission 1, 2026-11-18.
    blender -b --factory-startup --python bl_library.py -- ingest <src.glb|gltf> '<meta json>' <out dir>
    blender -b --factory-startup --python bl_library.py -- material <id> '<maps json>' '<params json>' <out dir>
ingest: imports the model, gathers it under ONE collection named <id> (root empty at the origin), applies the declared scale, marks the
collection as an asset, measures it (rc.qa) and saves <out>/<id>.blend + <out>/ingest.json.
material: one Principled material <id> from PBR maps (base colour, roughness, normal, ao, displacement), saved as <out>/<id>.blend.
link_asset() (imported by rc.assemble) links an asset collection from its .blend and instances it: every placement is an instance."""
import json, os, sys
import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rc import qa  # noqa: E402

def _reset(): bpy.ops.wm.read_factory_settings(use_empty=True)

def ingest(src, meta, out):
    _reset(); before = set(bpy.data.objects)
    if src.lower().endswith((".glb", ".gltf")): bpy.ops.import_scene.gltf(filepath=src)
    else: raise ValueError("unsupported source " + src)
    new = [o for o in bpy.data.objects if o not in before]; aid = meta["id"]
    col = bpy.data.collections.new(aid); bpy.context.scene.collection.children.link(col)
    root = bpy.data.objects.new(aid + "_root", None); col.objects.link(root)
    for o in new:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
        if o.parent is None: o.parent = root
    s = float(meta.get("scale", 1.0)); root.scale = (s, s, s)
    bpy.context.view_layer.update(); stats = qa.collection_stats(col)
    stats.update({"id": aid, "tier": meta.get("tier"), "category": meta.get("category"), "source": os.path.basename(src)})
    parts = meta.get("parts") or []
    names = {o.name for o in col.all_objects}; stats["parts_found"] = [p for p in parts if any(n.startswith(p) for n in names)]
    stats["parts_missing"] = [p for p in parts if p not in stats["parts_found"]]
    col.asset_mark(); col.asset_data.description = "%s (%s, %s)" % (aid, meta.get("category"), meta.get("tier"))
    for t in (meta.get("category"), meta.get("tier")): col.asset_data.tags.new(t)
    os.makedirs(out, exist_ok=True)
    json.dump(stats, open(os.path.join(out, "ingest.json"), "w"), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, aid + ".blend"), compress=True)
    print("INGESTED", aid, json.dumps({k: stats[k] for k in ("dims_m", "tris", "objects", "materials")}))

def material(aid, maps, params, out):
    _reset(); m = bpy.data.materials.new(aid); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); L.new(tc.outputs["Object"], mp.inputs["Vector"]); mp.inputs["Scale"].default_value = [params.get("tile", 1.0)] * 3
    def img(key, non_color):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(maps[key]); t.image.pack()
        if non_color: t.image.colorspace_settings.name = "Non-Color"
        t.projection = "BOX"; t.projection_blend = .2; L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    if "color" in maps: L.new(img("color", False).outputs["Color"], b.inputs["Base Color"])
    if "roughness" in maps: L.new(img("roughness", True).outputs["Color"], b.inputs["Roughness"])
    if "normal" in maps:
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = params.get("normal", 1.0); L.new(img("normal", True).outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    m.use_fake_user = True; m.asset_mark(); os.makedirs(out, exist_ok=True)
    json.dump({"id": aid, "kind": "material", "maps": sorted(maps), "tile": params.get("tile", 1.0)}, open(os.path.join(out, "ingest.json"), "w"), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, aid + ".blend"), compress=True); print("MATERIAL", aid, sorted(maps))

def link_asset(blend, aid, parent_col, link=False):
    """bring the asset collection into this file once and return it; it stays OUT of the scene tree and is drawn only through instances.
    Default APPEND (link=False): the scene .blend is self-contained, so a render pod needs no access to this machine's cache paths."""
    col = bpy.data.collections.get(aid)
    if col is None:
        with bpy.data.libraries.load(blend, link=link) as (src, dst): dst.collections = [aid]
        col = dst.collections[0]
    return col

def instance(col, name, loc, rot_z, scale, parent_col):
    e = bpy.data.objects.new(name, None); e.instance_type = "COLLECTION"; e.instance_collection = col
    e.location = loc; e.rotation_euler = (0, 0, rot_z); e.scale = (scale, scale, scale); parent_col.objects.link(e); return e

if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    if a[0] == "ingest": ingest(a[1], json.loads(a[2]), a[3])
    elif a[0] == "material": material(a[1], json.loads(a[2]), json.loads(a[3]), a[4])
    else: raise SystemExit("unknown command " + a[0])
