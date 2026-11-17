# Shared Asset Library

Managed by `tools/asset_hub.py`. Provider files are cached in one folder per provider/asset ID; every ingested asset has an `ASSET_MANIFEST.json` and a record in `catalog.json`.

- `polyhaven/`: public API downloads; CC0 assets.
- `ambientcg/`: public API downloads; CC0 assets.
- `sketchfab/`: only downloadable models with an allowed CC0/CC-BY license; requires the user's own OAuth token for download.
- `fab/`: assets the user acquired through their own Epic/Fab account and imported locally; never auto-downloaded or assumed owned by the skill.
- `blenderkit/`: existing BlenderKit add-on cache is preserved separately at `library/blenderkit/`.

Do not redistribute raw asset files outside the project. Keep each asset's manifest beside its source files. A catalog entry is provenance metadata, not a substitute for reading the full provider license.
