# Start here (for Claude)

## NEW VIDEO, WITH OR WITHOUT A REFERENCE VIDEO (CB 2026-11-19) — read first
`docs/PREPRODUCTION_FR.md`: write the full plan (`templates/production_plan/`), `python3 tools/plan_check.py plan/plan.json` = PLAN PASS
before any build; style = `references/STYLE_BIBLE_FR.md`; every action from `library/reactions/reactions.json` (reaction + lasting
consequence + micro + sound); build one Blender script per shot; `continuity.py` before any render; render in layers; every problem
becomes a lesson + a check/recipe (CB_RULES 11h). Worked example: `demos/crashed_car/` + `references/crashed_car/shots/`.

## CB's corrections are defaults (2026-11-19)
Read `docs/CORRECTIONS_CB_FR.md` before planning any scene: real textures, cinematic light, worn roads, furrowed fields, real fences with shadows, measured grade. Kit: `blender/rc/look.py`. `plan_check` refuses a plan without a `look` block.

## Cloud runtime (Claude Code Web)
If `CLAUDE_CODE_REMOTE=true`, read `CLOUD_MODE.md` first. Use `.venv/bin/python` for Python tools and `render_gpu.mjs --software` for cloud previews. Do not run the Windows installer. On install requests, run `scripts/cloud_session_start.sh` and `scripts/cloud_doctor.sh`, then report exact test results before creating a film.

## Production Intelligence (v1.0, 2026-11-18) — runs around every step below
0. **Phase 0, every film:** `.venv/bin/python tools/production_controller.py init episodes/<name>`. It opens the episode memory (`episodes/<name>/production/`) and prints the VALIDATED global lessons from `memory/lessons_learned.json`. Apply them, then read `library/INDEX.md`. Rules: `CB_RULES.md` section 11g. Wiring and commands: `production/README.md`.
- Before every full preview and before the final: `tools/production_controller.py gates episodes/<name> --phase preview|final`. NOT_RUN is never PASS, and FAIL blocks the final.
- After every preview: `production_controller.py review ... --clip a-b` (sheets plus continuous strips), then log issues and run the correction loop. Promote a lesson only with proof (`lesson-promote`).
- The finish level is set by `references/REFERENCE_LOOK_BIBLE.md` v2.0 OFFICIAL (the fortress reference video; frames in `references/fortress/`). Measure every preview with `tools/production_controller.py compare-reference` (gate F).

## Read order
1. `CB_RULES.md`, section 11 first. It is the lean pipeline and the token rules.
2. `SKILL.md`: read the headings first, then the parts you need.
3. The lead reads all of `CB_RULES.md`. A helper reads only its own slice in `rules/dept/` (see `rules/dept/INDEX.md`).
4. Rebuild the slices with `python tools/slice_rules.py` after any rule change.

## The lean pipeline in 6 steps
1. Pitch three true stories. The user picks one.
2. Script, facts and sources. Voice lines with a style tag on every clause. Then the picture plan (`templates/PICTURE_PLAN.md`).
3. Look bible, cast and sets. Hero props are built first. Helpers work in parallel, each with its rule slice.
4. The one gate: the whole film as a rough board, plus the hook moving. The user approves it, or says what to change.
5. After the gate, Claude works alone: build, render on the GPU (`render_gpu.mjs`), sound, grade, join. Measure numbers before looking at pictures. A fix round uses a fresh helper.
6. Before the GPU render, run `python tools/check_cinematic_quality.py episodes/<name>/film.json`. After rendering, run `python tools/check_cinematic_quality.py episodes/<name>/film.json --video episodes/<name>/final.mp4 --film-analysis --render-geometry` on the production GPU machine. Final film, `YOUTUBE.md`, proof page and token report are delivered together. Automated checks do not replace the full-resolution reference comparison or complete sound review.

## Example film
`examples/lightning-spear/` holds the docs and code of one finished film: script, cast, look bible, picture plan, edit list, briefs, sets, grade, join and sound mix. It has no frames, no video and no audio. Copy its layout for a new film in `episodes/<name>/`.

## Enhanced quality engines (V1.1 final patch)

- Environment: `ctx.terrain.hill/ridge/mountain`, `ctx.detail.rocks/grass`, `ctx.atmosphere.setWind/setFog`, and new `pine` / `birch` species are documented in `templates/threejs_film/PBR_FEATURES.md`. Use them only where they support the story and camera composition.
- Character motion: new films can enable `motion_polish` in `film.json`; it adds subtle head follow-through, breathing, local hand follow-through and automatic blinks, while preserving planted feet and explicit hand targets.
- Cinematic gate: `tools/check_motion_quality.mjs` validates the motion library; `tools/check_cinematic_quality.py` combines configuration, camera bake, motion, video and optional GPU geometry checks. `NOT_RUN` means not validated, never PASS.

## Asset Intelligence Hub (V1.2)
Before building a new environment, read `docs/ASSET_HUB.md`, inspect `library/places/` and `library/assets/catalog.json`, then search the four integrated providers (Sketchfab, Fab, Poly Haven, ambientCG) plus the existing BlenderKit bridge. The story remains the source of truth. Keep exact licence and creator/source metadata. Search, download, validate and stage assets with `tools/asset_hub.py`; register and reuse places with `tools/place_library.py`. PBR materials must name their `target_materials` explicitly.
