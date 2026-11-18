"""rc.library — B. Asset Library (Mission 1, 2026-11-18). Orchestrator side: pure Python (system Python), calls Blender as a subprocess.

Every asset is a folder under library/assets/<provider>/<id>/ with an asset.json (declarative metadata, in git). Built files never go
into git: they are content-addressed entries of rc.cache:
    model built by a Blender script   build.type = "script"   cache "asset_build"  -> the GLB(s) the script writes
    model downloaded (glb/gltf)       build.type = "file"      (no build step; the file is in the library folder)
    every model                       -> cache "asset_blend": ONE .blend with ONE collection named <id>, marked as an asset,
                                         plus ingest.json (measured dimensions, triangles, objects, materials, textures)
    material (PBR maps)               kind = "material"         -> cache "material_blend": one .blend with the material <id>
So `resolve(id)` returns a ready .blend; a second call (or a second film) never rebuilds an unchanged asset.

    python3 -m rc.library index                 list assets + validation
    python3 -m rc.library resolve <id>          build/ingest if needed, print the .blend path and the measured stats
    python3 -m rc.library resolve --all
(run from blender/, or with PYTHONPATH=blender)"""
import glob, json, os, shutil, subprocess, sys
from . import SKILL, cache, fetch

LIB = os.path.join(SKILL, "library", "assets")
BLENDER = os.environ.get("RICKCLIPS_BLENDER", shutil.which("blender") or "blender")
BL_SIDE = os.path.join(os.path.dirname(__file__), "bl_library.py")
CATEGORIES = {"vehicle", "building", "furniture", "vegetation", "rock", "terrain", "prop", "equipment", "machine", "effect", "material", "character_prop"}
TIERS = {"hero", "foreground", "midground", "background"}
REQUIRED = ["id", "name", "kind", "category", "tier", "description", "source", "license", "build"]

def _blender_version():
    try: return subprocess.run([BLENDER, "--version"], capture_output=True, text=True, timeout=60).stdout.split("\n")[0].strip()
    except Exception: return "unknown"

def index():
    out = {}
    for p in sorted(glob.glob(os.path.join(LIB, "*", "*", "asset.json"))):
        a = json.load(open(p)); a["_dir"] = os.path.dirname(p); out[a["id"]] = a
    return out

def validate(a):
    probs = ["missing " + k for k in REQUIRED if not a.get(k)]
    if a.get("kind") not in ("model", "material"): probs.append("kind must be model|material")
    if a.get("category") not in CATEGORIES: probs.append("category not in %s" % sorted(CATEGORIES))
    if a.get("tier") not in TIERS: probs.append("tier not in %s" % sorted(TIERS))
    lic = a.get("license") or {}
    if not lic.get("name"): probs.append("license.name")
    if lic.get("name") not in ("CC0", "custom-original") and not lic.get("url"): probs.append("license.url (attribution licences need it)")
    b = a.get("build") or {}
    if b.get("type") == "script":
        if not os.path.exists(os.path.join(SKILL, b.get("script", ""))): probs.append("build.script not found: %s" % b.get("script"))
        if not b.get("output"): probs.append("build.output (the GLB file name the script writes)")
    elif b.get("type") == "file":
        if not os.path.exists(os.path.join(a["_dir"], b.get("file", ""))): probs.append("build.file not found: %s" % b.get("file"))
    elif b.get("type") in ("polyhaven_model", "polyhaven_maps", "ambientcg_maps"):
        if not b.get("source_id"): probs.append("build.source_id (the provider id to fetch)")
    elif b.get("type") == "maps":
        for k, f in (b.get("maps") or {}).items():
            if not os.path.exists(os.path.join(a["_dir"], f)): probs.append("map %s not found: %s" % (k, f))
    else: probs.append("build.type must be script|file|maps|polyhaven_model|polyhaven_maps|ambientcg_maps")
    return probs

def _run_blender(args, log):
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "3"] + args, capture_output=True, text=True)
    bad = [l for l in (r.stdout + r.stderr).splitlines() if "Traceback" in l or l.startswith("Error") or "Error:" in l and "EGL" not in l]
    if r.returncode != 0 or bad:                            # PI-014: never trust the exit code alone
        raise RuntimeError("blender failed (rc %d): %s\n%s" % (r.returncode, " | ".join(bad[:5]), (r.stdout + r.stderr)[-2500:]))
    return r.stdout

def _script_glb(a, ver, log):
    b = a["build"]; script = os.path.join(SKILL, b["script"]); kit = os.path.join(LIB, "custom", "_blender_kit.py")
    code = [script] + ([kit] if os.path.exists(kit) else [])
    def build(out): _run_blender(["--python", script, "--", out] + b.get("args", []), log)
    d = cache.get_or_build("asset_build", {"script": b["script"], "args": b.get("args", [])}, build, code_files=code, versions={"blender": ver}, log=log)
    f = os.path.join(d, b["output"])
    if not os.path.exists(f): raise RuntimeError("builder did not write %s (has %s)" % (b["output"], os.listdir(d)))
    return f

def resolve(asset_id, log=print):
    """-> (path of the asset .blend, ingest stats). Builds and ingests only on a cache miss."""
    A = index(); a = A.get(asset_id)
    if not a: raise KeyError("unknown asset %s (have %s)" % (asset_id, ", ".join(sorted(A))))
    probs = validate(a)
    if probs: raise ValueError("asset %s invalid: %s" % (asset_id, probs))
    ver = _blender_version(); b = a["build"]
    if a["kind"] == "material":
        if b["type"] == "polyhaven_maps": maps = fetch.polyhaven_maps(b["source_id"], b.get("res", "1k"), log=log)
        elif b["type"] == "ambientcg_maps": maps = fetch.ambientcg_maps(b["source_id"], b.get("res", "1K"), log=log)
        else: maps = {k: os.path.join(a["_dir"], f) for k, f in b["maps"].items()}
        maps = {k: v for k, v in maps.items() if k in ("color", "roughness", "normal")}
        def build(out): _run_blender(["--python", BL_SIDE, "--", "material", asset_id, json.dumps(maps), json.dumps(b.get("params", {})), out], log)
        d = cache.get_or_build("material_blend", {"id": asset_id, "maps": sorted(maps), "params": b.get("params", {})}, build,
                               code_files=[BL_SIDE], input_files=list(maps.values()), versions={"blender": ver}, log=log)
    else:
        src = _script_glb(a, ver, log) if b["type"] == "script" else fetch.polyhaven_model(b["source_id"], b.get("res", "1k"), log=log) if b["type"] == "polyhaven_model" else os.path.join(a["_dir"], b["file"])
        meta = {"id": asset_id, "tier": a["tier"], "category": a["category"], "parts": a.get("parts", []), "scale": b.get("scale", 1.0), "forward": b.get("forward", "X"), "variants": bool(a.get("variants")), "lods": a.get("lods_auto", [])}
        def build(out): _run_blender(["--python", BL_SIDE, "--", "ingest", src, json.dumps(meta), out], log)
        ins = [src] + ([os.path.join(r, n) for r, _, ns in os.walk(os.path.dirname(src)) for n in ns if n != "meta.json"] if src.endswith(".gltf") else [])
        d = cache.get_or_build("asset_blend", meta, build, code_files=[BL_SIDE], input_files=sorted(set(ins)), versions={"blender": ver}, log=log)
    stats = json.load(open(os.path.join(d, "ingest.json")))
    return os.path.join(d, asset_id + ".blend"), stats

def report(path=None):
    """LIBRARY.md: the generated inventory (every asset: kind, category, tier, licence, source, measured size/tris/LODs/textures)"""
    rows = ["# Asset library — generated by `python3 -m rc.library report` (do not edit by hand)", "",
            "| id | kind | category | tier | licence | source | dims m | tris | LOD tris | textured | variants | parts |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    bad = []
    for i, a in index().items():
        try: _, s = resolve(i, log=lambda *x: None)
        except Exception as e: bad.append(i); rows.append("| %s | %s | %s | %s | %s | %s | FAILED: %s |||||" % (i, a["kind"], a["category"], a["tier"], a["license"]["name"], a["source"]["provider"], str(e)[:60])); continue
        lods = "/".join(str(l["tris"]) for l in s.get("lods", [])) or "-"
        rows.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (i, a["kind"], a["category"], a["tier"], a["license"]["name"], a["source"]["provider"],
                    "x".join(str(round(v, 2)) for v in s.get("dims_m", [])) or "-", s.get("tris", "-"), lods, "%s/%s" % (s.get("textured_materials", "-"), s.get("materials", "-")),
                    len(s.get("variants", [])) or "-", ", ".join(s.get("parts_found", [])) or "-"))
    rows += ["", "%d assets, %d failed. Licences: CC0 (Poly Haven, ambientCG), CC-BY-4.0 (credit required: see asset.json), custom-original (scripted here)." % (len(index()), len(bad))]
    p = path or os.path.join(LIB, "LIBRARY.md"); open(p, "w").write("\n".join(rows) + "\n"); return p, bad

def main(argv):
    if not argv or argv[0] == "index":
        for i, a in index().items(): print("%-26s %-8s %-11s %-10s %s" % (i, a["kind"], a["category"], a["tier"], "OK" if not validate(a) else "INVALID " + "; ".join(validate(a))))
        return 0
    if argv[0] == "report":
        p, bad = report(); print("wrote", p, "failed:", bad); return 1 if bad else 0
    if argv[0] == "resolve":
        ids = sorted(index()) if argv[1:] == ["--all"] else argv[1:]; rc = 0
        for i in ids:
            try: p, s = resolve(i); print("RESOLVED %s -> %s %s" % (i, p, json.dumps({k: s[k] for k in s if k in ("dims_m", "tris", "objects", "materials", "textured_materials", "primitive_ratio")})))
            except Exception as e: print("FAILED %s: %s" % (i, str(e)[:600])); rc = 1
        return rc
    print(__doc__); return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
