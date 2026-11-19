"""RENDER IN LAYERS (CB rule 2026-11-19). A shot .blend whose objects sit in the collections L_SKY, L_SET, L_OBJECTS, L_FX (+ L_LIGHTS, cameras
anywhere) is saved as 4 layer .blends; each is rendered alone with tools/render_manager.py (so --patch works per layer); comp() stacks them.
  SKY      world + clouds; everything else excluded                                       (opaque: the background)
  SET      the set + characters, transparent film; objects/fx excluded                    (they are added on top)
  OBJECTS  objects only; the set is HOLDOUT (it hides what is behind it, still lights and reflects), the set's ground objects
           (names in GROUND) become shadow catchers so the objects' shadows land in this layer's alpha
  FX       effects only; set + objects holdout
Inside Blender:  layers.split(<shot.blend>, <outdir>)  -> outdir/<layer>.blend
Outside:         python3 layers.py comp <outdir> <frames a-b> <out frames dir>   (alpha-over SKY < SET < OBJECTS < FX)"""
import os, sys, json
GROUND = ("ground", "pit_floor", "track", "road", "lane", "driveway", "apron", "footpath", "sidewalk", "gravel_trap", "grass_strip",
          "verge", "shoulder_L", "shoulder_R", "dirt_patch")          # crash_instinct roadside (car on the shoulder and the grass)
ORDER = ("SKY", "SET", "OBJECTS", "FX")
COLS = {"SKY": "L_SKY", "SET": "L_SET", "OBJECTS": "L_OBJECTS", "FX": "L_FX"}

def split(blend, outdir):
    import bpy
    os.makedirs(outdir, exist_ok=True); out = {}
    for layer in ORDER:
        bpy.ops.wm.open_mainfile(filepath=blend); sc = bpy.context.scene; vl = bpy.context.view_layer
        def lc(name):
            def walk(l):
                if l.collection.name == name: return l
                for c in l.children:
                    r = walk(c)
                    if r: return r
            return walk(vl.layer_collection)
        mine = COLS[layer]; sc.render.film_transparent = layer != "SKY"
        for other in ORDER:
            l = lc(COLS[other])
            if l is None: continue
            if other == layer: l.exclude = False; l.holdout = False
            elif layer == "SKY": l.exclude = True
            elif ORDER.index(other) < ORDER.index(layer) and other != "SKY": l.exclude = False; l.holdout = True      # in front-of-me layers hide what they cover
            else: l.exclude = True
        if layer in ("SET", "OBJECTS", "FX"):
            sky = lc("L_SKY")
            if sky: sky.exclude = True                                   # clouds belong to SKY only (the world still lights every layer)
        if layer == "OBJECTS":
            for o in bpy.data.objects:
                if o.type == "MESH" and o.name.split(".")[0] in GROUND: o.is_shadow_catcher = True
        p = os.path.join(outdir, layer + ".blend"); bpy.ops.wm.save_as_mainfile(filepath=p); out[layer] = p
    return out

def comp(layer_dirs, frames, out_dir):
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    for f in frames:
        base = None
        for layer in ORDER:
            p = os.path.join(layer_dirs, layer, "f%05d.png" % f)
            if not os.path.exists(p): continue
            im = Image.open(p).convert("RGBA"); base = im if base is None else Image.alpha_composite(base, im)
        base.convert("RGB").save(os.path.join(out_dir, "f%05d.png" % f))

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "comp":
    a, b = map(int, sys.argv[3].split("-")); comp(sys.argv[2], range(a, b + 1), sys.argv[4]); print("comp", sys.argv[4])
elif __name__ == "__main__" and "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]; print("LAYERS", json.dumps(split(args[0], args[1])))
