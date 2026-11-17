# Reusable Place Library

Each saved place is a story-neutral environment recipe, not a finished film. Keep one folder per place with `place.json`, approved stills, and optional set modules.

The recipe should record: scale/coordinate convention, visual style, lighting presets, weather/air-life, background layers, asset references, asset provenance, placement anchors, and safe camera stations. A story may choose any number of existing places or request a new one; the fortress is just one catalogued world, never the default for unrelated stories.

Before reusing a place, check that its asset files still exist and that its stored licenses cover the new production use. Stage provider assets into an episode with `python tools/asset_hub.py stage <provider> <asset-id> --episode episodes/<episode>` and declare the GLB/glTF path in `film.json` under `places.<place>.assets`.
