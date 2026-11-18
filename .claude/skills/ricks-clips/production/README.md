# Production Intelligence v1.0 — how it is wired into RicksClips (2026-11-18)

The package `RicksClips_Production_Intelligence_Upgrade_v1.0` (delivered spec, French, kept unchanged in `production/spec_fr/`)
asks RicksClips to behave like a supervising production controller: anticipate, inspect, detect defects without waiting for the
user, fix what is safe, prove every fix, and remember validated fixes for the next film. This page says where each part lives
and which entry point runs it. Binding text: `CB_RULES.md` section **11g** (it is copied into every department slice by
`tools/slice_rules.py`, so every agent reads it).

## Integration map
| Package item | Where it lives now | What runs it |
|---|---|---|
| Coordinator / showrunner | the lead session + `tools/production_controller.py` + agent `agents/production-controller.md` | START_HERE "Production Intelligence", CB_RULES 11g, SKILL.md header |
| Phase 0 bootstrap + memory read | `production_controller.py init episodes/<name>` | first step of every film (START_HERE) |
| Global memory | `memory/lessons_learned.json` (schema `production/schemas/lesson.schema.json`), readable `memory/LESSONS.md`, plus the long-form `library/` pitfalls | `init` prints validated lessons; SessionStart hook `scripts/production_memory_brief.sh` |
| Episode memory | `episodes/<name>/production/` (BRIEF, DECISIONS, OPEN_ISSUES, STATE, ASSET_REGISTER, ACTION_EFFECT_MATRIX, QA_LOG, ENV_SCORES, GATES, REVIEW/) | `init` creates it (never overwrites) |
| Quality gates A-G | `production/config/quality_gates.json` → `production_controller.py gates --phase plan/preview/final` → `production/GATES.md/json` | before every full preview and the final (studio-director owns it) |
| Reference look bible | `references/REFERENCE_LOOK_BIBLE.md` + `references/REFERENCE_SHEET_look_locked.jpg` | gate A; ENV_SCORES criteria |
| Environment richness score | `production/ENV_SCORES.json` per place, 0-4 per criterion, evidence required | gate C |
| Asset intelligence | `production/ASSET_REGISTER.json` + Asset Hub (`tools/asset_hub.py`, 11f) + `render_gpu.mjs --inventory` (kit hook `window.sceneInventory`) | gate B: hero primitive/flat-prop detection, licence/provenance, render test |
| Action → effect contract | `production/config/action_effect_matrix.json` (templates) → episode `ACTION_EFFECT_MATRIX.json` with evidence | gate A (exists) and E (rendered, aftermath, audio sync) |
| Animation checks | `tools/anim_audit.py` (static poses, planner walks, glides, overlaps), `tools/frame_checks/check.mjs` (contacts, clipping, edges), film_plan place-entry fix | gate D |
| Set-module safety | `tools/lint_set_modules.py` | gate E |
| Review | `production_controller.py review <ep> <stills> --clip a-b` (overview sheet + continuous strips) | gate F/D continuity |
| QA log / correction loop | `production_controller.py issue ...` → `QA_LOG.json` (waivers with reasons) | gate F |
| Lesson promotion | `production_controller.py lesson-add / lesson-promote` (refuses without tests, evidence files and a regression check) | CB_RULES 11g |
| Grade is real | episode grade writes `grade/grade_log.json` {src, dst, frames_graded} | gate G |
| Final delivery | `gates --phase final --video final.mp4` (ffprobe: 1080x1920, 30 fps, audio, duration) + `REVIEW/final_*.jpg` | gate G |
| Regression tests | `tools/tests/test_production_intelligence.py` (10 tests from real Ghost Army defects) | after any change to these tools |
| Project agents mirror | `tools/sync_project_agents.py` (skill `agents/` → project `.claude/agents/`) | after any agent change |

## Commands (cloud: `.venv/bin/python`)
```bash
.venv/bin/python tools/production_controller.py init  episodes/<name>
node templates/threejs_film/render_gpu.mjs episodes/<name>/film.json --inventory
.venv/bin/python tools/anim_audit.py episodes/<name>/film.json
.venv/bin/python tools/lint_set_modules.py episodes/<name>/sets/*.js
node tools/frame_checks/check.mjs episodes/<name>/film.json
.venv/bin/python tools/production_controller.py gates episodes/<name> --phase preview
.venv/bin/python tools/production_controller.py review episodes/<name> <stills_dir> --clip 0-150 --clip 1680-1760
.venv/bin/python tools/production_controller.py issue episodes/<name> --tc 00:44 --shot t_cafe --sev medium --cat framing --obs "..." --cause "..." --fix "..."
.venv/bin/python tools/production_controller.py lessons
.venv/bin/python tools/tests/test_production_intelligence.py
```

## Honest limits of this release
- The fortress reference is not in the repository; the look bible is PROVISIONAL (built from the approved `look_locked` stills).
- Environment scores are a reviewer's judgement with an evidence image, not an automatic measurement; the inventory gives the
  numbers behind "geometry" (parts, triangles, primitive share, textured materials).
- Gate E checks that evidence files exist and that a reviewer marked the event; it cannot prove by itself that an effect "looks good".
- The rig limits stay: no gaze control in the renderer, round-fist hands, no hand above the head, no physics cloth beyond the cloth lag.
- No automatic purchase, login or licence decision is ever taken: those stop at `OPEN_ISSUES.md` for the user.
