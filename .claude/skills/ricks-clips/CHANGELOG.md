# Changelog

## V1.1 (2026-11-15)

### New
- The lean pipeline: one gate for the user (whole film rough board plus the hook moving), then Claude works alone to the final.
- Rule slices per helper (`rules/dept/`).
- A fresh helper for every fix round.
- Numbers before pictures.
- A token report for every film.
- The look kit kit3d:
  - PBR metal with the sky as reflection.
  - Real-size relief surfaces.
  - Painted storm skies with flash.
  - Kit trees.
  - Real lightning, `fx_bolt`.
  - Hero props built first.
- Face fixes and long-cloth fixes.
- First film on V1.1: 716M tokens instead of 1.66B. 8.9 hours of real work instead of 22.7 hours.

### Bug fixes
- `castkit` ignored `faceShadow`. Fixed.
- `costume_shade` darkened white drawn pixels. Fixed with `keep_drawn_light`.
- Legs are now drawn over long cloth in moves.
- GPU render is now the default (`render_gpu.mjs`).

### Known issue
- The storm sky goes black at a long lens.


## V1.1 maintenance patch — 2026-11-16

- Synchronised `rules/CB_RULES.md` from the root master whenever rule slices are regenerated; installer and refresh now share the same install destination and rule-generation path.
- Replaced stale cloud-only / episode-local motion-tool references with the shipped central motion-library contract already implemented by the Three.js renderer.
- Made the approved-character-view check fail when a required source sheet is missing, instead of silently skipping it and reporting PASS.
- Enabled the V1.1 `kit3d` look option in the new-film starter template (existing episode films remain unchanged).
- Clarified current workflow precedence and marked the older full Blender workflow as historical/optional.
- Added `tools/check_delivery.py` for final MP4 resolution, frame-rate and duration metadata checks.


## V1.1 enhanced final — 2026-11-16

### Environment Realism Engine
- Added deterministic procedural hill, ridge and mountain meshes with altitude/slope colour zones.
- Added instanced rock scatter and grass tufts, additional pine/birch tree silhouettes, and shared directional wind / linear or exponential fog controls.
- Exposed the new APIs through the normal set-builder `ctx` without removing existing PBR, relief, sky, tree or FX interfaces.

### Character Motion Polish
- Added an optional deterministic secondary-motion layer: subtle head follow-through, breathing, safe local-hand follow-through and automatic blink timing.
- Explicit hand targets and planted-foot data are left unchanged; legacy films are unchanged unless they opt in.
- Added an automated integrity/sample checker for all 42 motion modules, 195 library references, 330 exported styles and sampled pose outputs.
- Added a render-level SVG regression test for secondary motion and deterministic automatic blinking (`tools/test_motion_polish.mjs`).

### Cinematic Quality Control
- Added `check_cinematic_quality.py` to combine film configuration, camera-bake, motion-library, MP4 metadata, pixel analysis and optional live GPU geometry checks.
- Extended delivery checks to report frame-rate consistency, audio sample rate/channels and early audio ending when audio is required.
- Added an object-graph smoke test for the new Three.js environment APIs.

### Validation boundary
- Static checks and Node-level geometry/object-graph tests can run without a production GPU. Full image quality, renderer compatibility, actual character interaction and sound remain subject to rendering and human review on the target workstation.


## V1.2 Asset Intelligence Hub — 2026-11-16

- Added a unified asset discovery and ingestion CLI for Sketchfab, Fab, Poly Haven and ambientCG, while preserving the existing BlenderKit bridge.
- Added official-API search/download paths for Poly Haven and ambientCG; added Sketchfab Data API search plus OAuth-gated downloads for downloadable CC0/CC-BY models.
- Added a Fab official listing hand-off and documented local import workflow for files acquired by the user's own Epic/Fab account; no checkout automation or access bypass.
- Added safe archive extraction, HTTPS-only downloads, file-size limits, format checks, provenance manifests, SHA-256 hashes and license/topic gates.
- Added reusable place library manifests and staging, including Three.js GLB/glTF loading and material-targeted PBR texture application.
- Added per-episode asset credit generation and provider/license guidance, including Sketchfab attribution and Poly Haven API credit.
- Added provider setup documentation, environment-variable template, empty local catalog and example place manifest.
- Added offline tests for provider normalization, license rules, archive safety, local Fab import evidence, material staging and asset credits.
- Runtime integration requires `npm install` in `templates/threejs_film` to obtain the pinned Three.js GLTFLoader dependency; no package downloads or third-party assets are bundled.

## 2026-11-18 — Production Intelligence v1.0
- New: `tools/production_controller.py` (episode memory, quality gates A-G, review sheets and strips, QA log, lesson registry with proof-gated promotion), `tools/anim_audit.py`, `tools/lint_set_modules.py`, `tools/sync_project_agents.py`, `tools/tests/test_production_intelligence.py` (10 regression tests), `production/` (configs, schemas, delivered French spec, README), `memory/` (global lessons; 4 validated), `references/REFERENCE_LOOK_BIBLE.md` (PROVISIONAL), agent `production-controller`, SessionStart hook `scripts/production_memory_brief.sh`.
- Kit: `render_gpu.mjs --inventory` + `window.sceneInventory` (what each place really builds); `film_plan.py` place entry lands with the cut on the same frame (PI-003, it fixed a 1-frame pop found by the new test); move-to-move pose blend (`film.tween.move_blend`); soft contact shadows; `lift` moves in the motion library.
- Rules: CB_RULES section 11g (in every department slice); START_HERE, SKILL.md, WORKFLOW.md and library/INDEX.md point to it; every agent has a Production Intelligence block.

## 2026-11-18 — Official fortress reference standard
- `references/REFERENCE_LOOK_BIBLE.md` v2.0 OFFICIAL from the user's fortress video; captures `references/fortress/` (26 frames, overview, motion strips, measures).
- `production/config/reference_standard.json` + `tools/reference_compare.py` + `production_controller.py compare-reference` (gate F; gate A checks the bible is official).
- CB_RULES 11g, START_HERE, production/README and all 17 agents name the standard; lesson PI-007 validated; test suite 11/11.
- Ghost Army: `production/REFERENCE_COMPARE.md`, `production/REFERENCE_GAP_ANALYSIS.md` (gaps + correction plan, awaiting approval).
