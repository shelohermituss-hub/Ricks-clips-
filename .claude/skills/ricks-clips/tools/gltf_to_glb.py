"""Convert a downloaded Sketchfab glTF folder to one compact .glb for the asset library.

Why it exists: library asset.json files point at `glb/<name>_1k.glb`, but `tools/asset_hub.py download sketchfab <id>`
gives `gltf/scene.gltf` (+ 4k textures). The conversion was once done with a throw-away script, so a fresh session
could not rebuild the file and `test_rc.py` failed (lesson PI-017). This is that step, kept in the repo.

Usage (Blender 5.2):
  blender -b --factory-startup --python tools/gltf_to_glb.py -- <scene.gltf> <out.glb> [--max-px 1024]
or for a library asset whose asset.json says build.file = glb/...:
  blender -b --factory-startup --python tools/gltf_to_glb.py -- --asset library/assets/sketchfab/<id>
"""
import bpy, sys, os, json

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
max_px = 1024
if "--max-px" in argv:
    i = argv.index("--max-px"); max_px = int(argv[i + 1]); del argv[i:i + 2]
if argv and argv[0] == "--asset":
    folder = os.path.abspath(argv[1]); meta = json.load(open(os.path.join(folder, "asset.json")))
    src = os.path.join(folder, "gltf", "scene.gltf"); dst = os.path.join(folder, meta["build"]["file"])
else:
    src, dst = os.path.abspath(argv[0]), os.path.abspath(argv[1])
if not os.path.isfile(src): raise SystemExit("gltf_to_glb: source not found: %s (download it first: tools/asset_hub.py download sketchfab <id>)" % src)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)

resized = 0
for img in bpy.data.images:
    if img.size[0] == 0 or img.source != "FILE": continue
    w, h = img.size
    if max(w, h) > max_px:
        k = max_px / max(w, h); img.scale(max(1, round(w * k)), max(1, round(h * k)))
        # the glTF importer PACKS images: without a re-pack the exporter writes the original full-size bytes
        img.pack(); resized += 1

os.makedirs(os.path.dirname(dst), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_image_format="JPEG", use_selection=False)
tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == "MESH" for p in o.data.polygons)
print("GLB %s" % json.dumps({"out": dst, "mb": round(os.path.getsize(dst) / 1e6, 2), "tris": tris, "textures_resized": resized, "max_px": max_px}))
