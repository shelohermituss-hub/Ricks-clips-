#!/usr/bin/env python3
"""Build episode-level third-party asset attribution from staged ASSET_MANIFEST.json files."""
import argparse
import json
from pathlib import Path

PROVIDER_NOTICES = {
    "polyhaven": "Powered by Poly Haven — assets are CC0; the live API is credited here as requested by Poly Haven.",
    "sketchfab": "Some 3D models provided by Sketchfab. See each entry below for creator, source and exact Creative Commons licence.",
    "ambientcg": "Textures/models from ambientCG (CC0).",
    "fab": "Fab assets are governed by the exact licence recorded below and the owner's acquisition evidence.",
    "blenderkit": "BlenderKit assets are subject to the owner's account and applicable asset licence.",
    "manual": "Locally imported assets; see the provenance and licence details below.",
}


def build_credits(episode: Path) -> Path:
    asset_root = episode / "assets" / "asset_hub"
    rows = []
    if asset_root.exists():
        for path in sorted(asset_root.rglob("ASSET_MANIFEST.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                rows.append({"provider": "unknown", "name": path.parent.name, "error": str(exc)})
                continue
            rows.append({
                "provider": data.get("provider", "unknown"),
                "asset_id": data.get("asset_id", path.parent.name),
                "name": data.get("name", path.parent.name),
                "creator": data.get("creator") or "Creator not supplied",
                "license": data.get("license") or "Licence not supplied",
                "source_url": data.get("source_url") or "Source URL not supplied",
                "license_url": data.get("license_url") or "",
            })
    dedup = {}
    for row in rows:
        dedup[(row.get("provider"), row.get("asset_id"))] = row
    rows = sorted(dedup.values(), key=lambda x: (x.get("provider", ""), x.get("name", "")))
    providers = sorted({x.get("provider", "unknown") for x in rows})
    lines = ["# Third-party asset credits", "", "Generated from the staged `ASSET_MANIFEST.json` files. Keep this file with the episode and make the required attributions available in the final film end credits, player/page, or publication description as applicable.", ""]
    for provider in providers:
        if provider in PROVIDER_NOTICES:
            lines.extend(["## " + provider, "", PROVIDER_NOTICES[provider], ""])
    if rows:
        lines.extend(["## Asset attributions", "", "| Provider | Asset | Creator | Licence | Source | Licence details |", "|---|---|---|---|---|---|"])
        for r in rows:
            if r.get("error"):
                lines.append(f"| {r['provider']} | {r['name']} | — | — | — | Manifest error: {r['error']} |")
                continue
            vals = [r.get("provider"), r.get("name"), r.get("creator"), r.get("license"), r.get("source_url"), r.get("license_url")]
            vals = [str(v or "—").replace("|", "\\|").replace("\n", " ") for v in vals]
            lines.append("| " + " | ".join(vals) + " |")
    else:
        lines.append("No external provider assets have been staged into this episode yet.")
    lines.extend(["", "Do not redistribute raw asset packs separately from the film/project. Review the exact licence before publication; this file is a provenance aid, not legal advice.", ""])
    target = episode / "ASSET_CREDITS.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def main():
    parser = argparse.ArgumentParser(description="Build an episode asset credits/provenance file")
    parser.add_argument("episode", type=Path)
    args = parser.parse_args()
    target = build_credits(args.episode.resolve())
    print(f"ASSET_CREDITS_WRITTEN: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
