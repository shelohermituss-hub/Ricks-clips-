"""rc command line inside Blender (Mission 1, 2026-11-18):
  blender -b --factory-startup --python blender/rc/cli.py -- assemble <place.json> <out.blend>
  blender -b --factory-startup --python blender/rc/cli.py -- stats <scene.blend> [out.json]
  blender -b --python blender/rc/cli.py -- render <scene.blend> <outdir> <frames a,b,c|a-b> [--engine CYCLES|EEVEE|WORKBENCH] [--res 270x480] [--samples 16] [--seed 0] [--gpu] [--no-denoise]
Every command prints one line "RC_RESULT <json>" for the orchestrator; errors raise (python-exit-code makes Blender exit non-zero)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bpy  # noqa: E402

def _frames(s):
    out = []
    for x in s.split(","):
        a, _, b = x.partition("-"); out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out

def main(a):
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    if a[0] == "assemble":
        from rc import assemble, qa
        rep = assemble.build(a[1], a[2]); rep["stats"] = qa.scene_stats(); bpy.ops.wm.save_mainfile()
        print("RC_RESULT " + json.dumps(rep)); return
    if a[0] == "stats":
        from rc import qa
        bpy.ops.wm.open_mainfile(filepath=a[1]); s = qa.scene_stats()
        if len(a) > 2 and not a[2].startswith("--"): json.dump(s, open(a[2], "w"), indent=1)
        print("RC_RESULT " + json.dumps(s)); return
    if a[0] == "render":
        from rc import render
        bpy.ops.wm.open_mainfile(filepath=a[1]); sc = bpy.context.scene; w, h = map(int, opt("--res", "270x480").split("x"))
        info = render.setup(sc, opt("--engine", "CYCLES"), (w, h), int(opt("--samples", "16")), int(opt("--seed", "0")), gpu="--gpu" in a, denoise="--no-denoise" not in a)
        rep = render.frames(sc, _frames(a[3]), a[2], info); print("RC_RESULT " + json.dumps({k: rep[k] for k in rep if k != "frames"} | {"n": len(rep["frames"]), "sec": [r["seconds"] for r in rep["frames"]]})); return
    raise SystemExit("unknown rc command: %s" % a[0])

main(sys.argv[sys.argv.index("--") + 1:])
