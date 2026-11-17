# Initial audit — RicksClips Cloud (2026-11-17, before the finalisation fixes)

## Starting point
- Branch `ccr-00f60cb8-lenpig`, commit `9e1dd28`: V1.3 release imported (manifest 891/891 OK), plus the first round of cloud fixes (system Chrome for Playwright, software path forced in `render_gpu.mjs`, ES modules for `vendor/` and `sets/`, lockfile, Blender 5.2.2 in the setup script).
- Files read: `RAPPORT_INSTALLATION_CLOUD_FR.md`, `CLOUD_MODE.md`, `INSTALL_CLAUDE_CODE_WEB_FR.md`, `START_HERE.md`, `SKILL.md` (cloud section, lean pipeline, headings), `templates/threejs_film/GPU_RENDER.md`, `PBR_FEATURES.md`, `templates/film_example/`.
- Structure: Skill `.claude/skills/ricks-clips/` (SKILL.md, CB_RULES.md, 16 agents in `.claude/agents/` plus copies in `agents/`, `rules/dept/`, `templates/` (threejs_film, vector2d_characters, motion_styles, blender_look, blender_cine, audio, film_example), `tools/` (asset_hub, film_plan, check_*, frame_checks, measure), `library/`, `references/`, `examples/lightning-spear/`). No `episodes/` folder.
- Production pipeline (CB_RULES §11, START_HERE): story and voice → `film.json` (cast, places, takes/camera stations, acts, fx, moods, sound) → `tools/film_plan.py check` (camera bake + gates) → `render_gpu.mjs` (three.js + 2D puppets) → sound (`templates/audio`) → `check_cinematic_quality.py`. Blender is an optional layer, used only on request.

## Already working (measured on 2026-11-17)
Cloud Doctor 12 PASS / 1 WARN (no GPU) / 0 FAIL; Asset Hub 16/16 (offline); Motion QA 42/42; Look3D; Asset Loader; Motion polish; Chrome + Playwright + WebGL 2 (SwiftShader); `film_plan`; pre-render cinematic quality; frame_checks 3/3; Blender 5.2.2 EEVEE and Cycles on a minimal scene; syntax of all files.

## Failing or untested
| Item | State before fixes |
|---|---|
| Providers (Poly Haven, ambientCG, Sketchfab, Fab, BlenderKit, Fish Audio, Hugging Face) | Network blocked (all hosts refused by the proxy) |
| BlenderKit bridge | Crashes when the add-on is missing, but Blender returns 0, so `asset_hub` shows an empty list instead of an error (silent bug) |
| faster-whisper | No weights (huggingface.co blocked); `voice_prep.py` hard-codes `small.en` (English only); no model cache configured |
| TTS voice | Fish Audio only (key missing); no offline fallback |
| `check_views.mjs` | 16 views OK, 7 characters without a source sheet (`episodes/` missing) |
| Real `.blend` / GLB / textures in Blender | Untested |
| FFmpeg assembly / A/V sync | Untested |
| Full pipeline up to a real MP4 | Never run in the cloud |
