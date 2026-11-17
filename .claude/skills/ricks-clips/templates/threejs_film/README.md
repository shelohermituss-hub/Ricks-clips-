# Three.js Film Kit — Ricks Clips V1.1

This is the current 3D world, camera and GPU-rendering kit. The film renderer uses the 2D vector puppets as cards at real depth inside the Three.js scene.

## Render entry point

Use `render_gpu.mjs` for current production renders. It supports the film JSON workflow and adds GPU verification, frame ranges and a private per-process puppet/motion cache.

```bash
node render_gpu.mjs <film.json> --gpu-info
node render_gpu.mjs <film.json> --frames 0,60,150 --scale 1 --stills-dir <dir>
node render_gpu.mjs <film.json> --frames 100-129 --scale 1 --stills-dir <dir>
node render_gpu.mjs <film.json> --animatic --scale 1
node render_gpu.mjs <film.json> --scale 1
```

Useful options are documented in `GPU_RENDER.md`: `--gpu-info`, `--frames`, `--scale`, `--headed`, `--cache`, and `--software`. `--software` is for comparison/fallback testing, not a substitute for verifying the intended GPU path. The renderer stops if it detects CPU WebGL unless explicitly allowed. Use `--scale 1` for final 1080×1920 output when the film JSON specifies that size.

## 2D motion bridge

The film renderer already integrates `templates/motion_styles/`. `render_gpu.mjs` copies `library.mjs`, `rig.mjs`, `cloth_live.mjs` and the central `moves/*.mjs` modules into its private cache. `puppets.mjs` resolves a film act with `pose: "m:<id>"` against the registered `LIB` entries. A new move must be added under `templates/motion_styles/moves/` and registered in `library.mjs`; arbitrary episode-local move paths are not loaded by the stock renderer. See `../motion_styles/README.md`.

## V1.1 look kit / PBR

The look kit is documented in `PBR_FEATURES.md`: PBR materials, surface relief, layered sky/clouds, trees, deterministic terrain, instanced ground detail and shared wind/fog controls. `kit3d` remains opt-in for backward compatibility; the V1.1 starter at `../film_example/film.json` enables it for new films. Older episode JSON files are unchanged. The same guide documents the optional motion-polish settings and the combined cinematic-quality gate.

Known limitations documented by the source include a storm-sky issue at long focal lengths, relatively smooth/simple clouds, and alpha-mask limitations for leaf cards placed in front of characters. The procedural terrain/ground-detail APIs and secondary-motion layer are additive and do not fix those pre-existing limits by themselves. GPU render behaviour must be checked on the target Windows/NVIDIA machine; object-graph smoke tests and static checks do not validate final visual quality.

## Dependencies

Install the package dependencies from this folder with `npm install`, and ensure Playwright's Chromium, ffmpeg and the Python dependencies in the root `INSTALL.md` are installed. Keep the original character package and source assets intact.

## Quality tools

- `node tools/check_motion_quality.mjs`: verifies registered motion references and samples the available pose functions.
- `node tools/test_look3d_api.mjs`: headless Three.js object-graph smoke test for terrain, instanced detail, added tree species, wind and fog.
- `python tools/check_cinematic_quality.py <film.json>`: combined config, camera-bake and motion preflight. Add `--video <final.mp4> --film-analysis --render-geometry` after rendering on the production workstation.
