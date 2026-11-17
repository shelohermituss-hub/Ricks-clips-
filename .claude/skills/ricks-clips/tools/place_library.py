#!/usr/bin/env python3
"""Register and stage reusable RicksClips environment recipes."""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "library" / "places"
ASSETS = ROOT / "library" / "assets"


def clean_id(value):
    value = re.sub(r"[^a-z0-9_-]+", "_", str(value).lower()).strip("_")
    if not value:
        raise ValueError("place id is empty")
    return value


def clean_asset_id(value):
    # Provider asset IDs are case-sensitive (e.g. ambientCG PavingStones036).
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("._")
    if not value or value in {".", ".."}:
        raise ValueError("asset id is empty or unsafe")
    return value[:120]


def validate(data):
    errors = []
    for key in ("schema_version", "place_id", "name", "coordinate_system", "visual_direction", "assets"):
        if key not in data:
            errors.append("missing required field: " + key)
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("coordinate_system") != "film-plan-metres-x-y-forward-z-up":
        errors.append("coordinate_system must be film-plan-metres-x-y-forward-z-up")
    if not isinstance(data.get("assets"), list):
        errors.append("assets must be a list")
    else:
        for i, item in enumerate(data["assets"]):
            for key in ("provider", "asset_id", "role", "license"):
                if not item.get(key): errors.append("assets[%d] missing %s" % (i, key))
            if item.get("provider") not in {"sketchfab", "polyhaven", "ambientcg", "fab", "blenderkit", "manual"}:
                errors.append("assets[%d] has unsupported provider" % i)
            pos = item.get("position", [0, 0, 0])
            if not isinstance(pos, list) or len(pos) != 3:
                errors.append("assets[%d].position must be [x,y,z]" % i)
            if item.get("role") in {"material", "texture", "surface"}:
                targets = item.get("target_materials")
                if not isinstance(targets, list) or not targets or not all(isinstance(x, str) and x.strip() for x in targets):
                    errors.append("assets[%d] material role requires non-empty target_materials matching set material names" % i)
    return errors


def cmd_register(args):
    source = args.manifest.resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        raise ValueError("Invalid place manifest:\n- " + "\n- ".join(errors))
    pid = clean_id(data["place_id"])
    folder = PLACES / pid
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "place.json"
    if target.exists() and not args.replace:
        raise ValueError("Place already exists; use --replace only when intentionally updating it")
    shutil.copy2(source, target)
    print(json.dumps({"status": "REGISTERED", "place_id": pid, "manifest": str(target)}, indent=2))


def cmd_list(args):
    rows = []
    if PLACES.exists():
        for file in sorted(PLACES.glob("*/place.json")):
            try:
                d = json.loads(file.read_text(encoding="utf-8"))
                rows.append({"place_id": d.get("place_id"), "name": d.get("name"), "assets": len(d.get("assets", [])), "manifest": str(file)})
            except Exception as exc:
                rows.append({"manifest": str(file), "error": str(exc)})
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_stage(args):
    pid = clean_id(args.place_id)
    source = PLACES / pid / "place.json"
    if not source.exists():
        raise ValueError("Unknown place: " + pid)
    data = json.loads(source.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        raise ValueError("Invalid registered place: " + "; ".join(errors))
    episode = args.episode.resolve()
    episode.mkdir(parents=True, exist_ok=True)
    film_assets, film_materials, staged = [], [], []
    for item in data.get("assets", []):
        maps = {}  # reset for this asset; prevents a previous texture pack leaking into the next record
        provider, aid = item["provider"], clean_asset_id(item["asset_id"])
        asset_dir = ASSETS / provider / aid
        manifest_path = asset_dir / "ASSET_MANIFEST.json"
        if not manifest_path.exists():
            # BlenderKit's existing cache uses a different root. Import locally first to create a uniform manifest.
            raise ValueError("Asset not ingested in Asset Hub: %s/%s. Run asset_hub.py import-local or provider download first." % (provider, aid))
        dst = episode / "assets" / "asset_hub" / provider / aid
        if not dst.exists():
            shutil.copytree(asset_dir, dst)
        manifest = json.loads((dst / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
        files = [f for f in manifest.get("files", []) if f.get("path")]
        gltf_candidates = []
        for f in files:
            original = Path(f["path"])
            # Manifest file paths may be absolute on the authoring computer; resolve against known provider folder if needed.
            try:
                rel = original.resolve().relative_to(asset_dir.resolve())
                local = dst / rel
            except Exception:
                local = dst / original.name
                if not local.exists():
                    matches = list(dst.rglob(original.name))
                    local = matches[0] if matches else local
            if local.exists() and local.suffix.lower() in {".glb", ".gltf"}:
                gltf_candidates.append(local)
        preferred = item.get("file")
        chosen = None
        if preferred:
            p = (dst / preferred).resolve()
            try: p.relative_to(dst.resolve())
            except ValueError: raise ValueError("Asset file path escapes staged folder: " + preferred)
            if p.exists() and p.suffix.lower() in {".glb", ".gltf"}: chosen = p
        if not chosen and gltf_candidates:
            chosen = gltf_candidates[0]
        if chosen:
            rel = chosen.relative_to(episode).as_posix()
            film_assets.append({"id": item.get("name") or aid, "provider": provider, "license": item["license"],
                                "file": rel, "position": item.get("position", [0, 0, 0]),
                                "rotationY": item.get("rotationY", 0), "scale": item.get("scale", 1),
                                "required": bool(item.get("required", False)), "castShadow": item.get("castShadow", True),
                                "receiveShadow": item.get("receiveShadow", True)})
        # Texture/material packages are retained separately and can be applied to named Three.js materials.
        kind = str(manifest.get("kind", "")).lower()
        if kind in {"material", "texture", "terrain"} or item.get("role") in {"material", "texture", "surface"}:
            candidates = []
            for f in files:
                original = Path(f["path"])
                try:
                    rel_src = original.resolve().relative_to(asset_dir.resolve())
                    local = dst / rel_src
                except Exception:
                    local = dst / original.name
                    if not local.exists():
                        matches = list(dst.rglob(original.name))
                        local = matches[0] if matches else local
                if local.exists() and local.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                    candidates.append(local)
            def pick_channel(words):
                ranked = []
                for file in candidates:
                    name = file.stem.lower().replace("-", "_")
                    if any(word in name for word in words):
                        # Prefer the requested resolution and OpenGL normal maps.
                        score = (int("2k" in name or "2048" in name), int("normalgl" in name), -len(name))
                        ranked.append((score, file))
                return max(ranked, default=(None, None), key=lambda x: x[0])[1]
            maps = {}
            for channel, words in {
                "color": ("color", "basecolor", "albedo", "diffuse"),
                "normal": ("normalgl", "normal", "normal_opengl"),
                "roughness": ("roughness", "rough"),
                "metalness": ("metalness", "metallic", "metal"),
                "ao": ("ambientocclusion", "occlusion", "_ao", "ao_"),
                "displacement": ("displacement", "height", "bump")
            }.items():
                selected = pick_channel(words)
                if selected:
                    maps[channel] = selected.relative_to(episode).as_posix()
            if maps:
                film_materials.append({"id": item.get("name") or aid, "provider": provider, "asset_id": aid,
                    "license": item["license"], "maps": maps, "target_materials": item.get("target_materials", []),
                    "repeat": item.get("repeat", [1, 1]), "roughnessFactor": item.get("roughnessFactor"),
                    "metalnessFactor": item.get("metalnessFactor"), "normalScale": item.get("normalScale", [1, 1]),
                    "required": bool(item.get("required", False))})
        staged.append({"provider": provider, "asset_id": aid, "folder": str(dst), "runtime_glb_found": bool(chosen),
                       "conversion_needed": not bool(chosen), "runtime_material_maps": len(maps), "role": item.get("role")})
    outdir = episode / "place_manifests"
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_out = {**data, "staged_at": str(episode), "staged_assets": staged, "film_assets": film_assets, "film_materials": film_materials}
    (outdir / (pid + ".json")).write_text(json.dumps(manifest_out, ensure_ascii=False, indent=2), encoding="utf-8")
    snippet = {"place": pid, "assets": film_assets, "materials": film_materials}
    (outdir / (pid + ".film-place-assets.json")).write_text(json.dumps(snippet, ensure_ascii=False, indent=2), encoding="utf-8")
    from build_asset_credits import build_credits
    credits_file = build_credits(episode)
    print(json.dumps({"status": "STAGED", "place_id": pid, "manifest": str(outdir / (pid + ".json")),
                      "film_json_snippet": str(outdir / (pid + ".film-place-assets.json")),
                      "asset_credits": str(credits_file),
                      "runtime_assets": len(film_assets), "runtime_materials": len(film_materials), "assets": staged}, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="Register reusable environment recipes and stage their assets into episodes")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("register"); r.add_argument("manifest", type=Path); r.add_argument("--replace", action="store_true"); r.set_defaults(func=cmd_register)
    l = sub.add_parser("list"); l.set_defaults(func=cmd_list)
    s = sub.add_parser("stage"); s.add_argument("place_id"); s.add_argument("--episode", required=True, type=Path); s.set_defaults(func=cmd_stage)
    args = p.parse_args()
    try: args.func(args)
    except Exception as exc:
        print("PLACE_LIBRARY_ERROR: " + str(exc), file=sys.stderr); return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
