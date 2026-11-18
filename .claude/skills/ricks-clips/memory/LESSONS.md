# Production lessons (generated from memory/lessons_learned.json — do not edit by hand)

Read the VALIDATED lessons at the start of every film (`production_controller.py init` prints them). A lesson is promoted only with a
demonstrated cause, a reproducible fix, tests, before/after evidence and a regression check (CB_RULES 11g).

## PI-001 — Characters animated with static kit poses (40/64 acts), planner 2-frame walks and glides:  [validated, blocker]

- **Where:** ghost-army whole film
- **Root cause:** acts authored with blocking poses (stand, knock, hold_up...) and walk=True; film.json had no tween, so poses snapped; motion polish (breath/blink) only runs on library moves
- **Fix:** every act is a registered m:<id> library move; position changes use m:walk/run/bike with linear travel at real speeds; tween {ones:true, face_frames:0, move_blend:6}; new moves are registered in templates/motion_styles/library.mjs; gate D runs tools/anim_audit.py
- **Files:** tools/anim_audit.py, templates/motion_styles/moves/act_lift.mjs, templates/motion_styles/library.mjs, templates/threejs_film/puppets.mjs, templates/threejs_film/film.js, episodes/ghost-army/build/make_film.py
- **Tests:** tools/tests/test_production_intelligence.py :: PI-001 anim_audit FAILs the v1 film; tools/tests/test_production_intelligence.py :: PI-001 anim_audit PASSes the current film
- **Evidence:** episodes/ghost-army/audit/ANIMATION_VFX_AUDIT.md; episodes/ghost-army/production/REVIEW/clip_00000_00150.jpg
- **Regression check:** anim_audit on the v1 film.json (git c3937a0) reports STATIC 37 -> FAIL; current film PASS

  - history: 2026-11-18: tested -> validated
## PI-002 — Effects silently disappeared (shell bursts, river moonlight, a fade) although node --check [validated, high]

- **Where:** ghost-army 00:56, 01:00
- **Root cause:** an inline // note written after code on a long one-line statement swallowed the rest of the line
- **Fix:** inline notes use /* */; tools/lint_set_modules.py flags a // that follows code and is followed by code; gate E runs it on every episode set module
- **Files:** tools/lint_set_modules.py, tools/tests/fixtures/swallowed_comment.js
- **Tests:** tools/tests/test_production_intelligence.py :: PI-002 lint catches swallowed code (fixture); tools/tests/test_production_intelligence.py :: PI-002 Ghost Army set module is clean
- **Evidence:** tools/tests/fixtures/swallowed_comment.js; episodes/ghost-army/sets/ghost.js
- **Regression check:** the lint flags the bug in git history (commits 63d3a57, 6759b96) and 3/3 fixture lines, 0 false positives on the 2 clean fixture lines and on the current set

  - history: 2026-11-18: tested -> validated
## PI-003 — A character entering a new place slid for 0.5 s from its old coordinates after the cut, an [validated, high]

- **Where:** ghost-army 00:10.6 (camp), 01:01.5 (bedroom)
- **Root cause:** film_plan baked a place-entering act as a normal move (default move_s 0.5) keyed one frame after the body/place key
- **Fix:** film_plan.py: an act that enters another place lands on the same frame as the place switch (_land), no move
- **Files:** tools/film_plan.py
- **Tests:** tools/tests/test_production_intelligence.py :: PI-003 entering a place never slides
- **Evidence:** tools/tests/test_production_intelligence.py; episodes/ghost-army/production/REVIEW/clip_02040_02136.jpg
- **Regression check:** the test strips every move_s from place-entering acts and bakes: before the fix 4.52 m one-frame pop (lou f319) and 0.5 s slides; after 0.00 m

  - history: 2026-11-18: tested -> validated
## PI-004 — Framing gates (head cut, figure size) measured figures that are not in the shot's place. [tested, medium]

- **Where:** ghost-army 
- **Root cause:** the plan checker's framing loop ignored st.place while the renderer hides off-place figures
- **Fix:** film_plan.py framing loop skips a figure whose place differs from the camera's place
- **Files:** tools/film_plan.py
- **Tests:** tools/film_plan.py check episodes/ghost-army/film.json
- **Evidence:** episodes/ghost-army/out/plan/plan_report.md
- **Regression check:** 

## PI-005 — A wide white haze over the night river. [tested, medium]

- **Where:** ghost-army 00:58-01:01
- **Root cause:** the moon key light glinted on the reflective water toward the camera and the bloom spread it (found by zeroing light groups one by one)
- **Fix:** night key light placed on the camera side; water specularIntensity lowered; reflection kept through the env map
- **Files:** episodes/ghost-army/sets/ghost.js
- **Tests:** 
- **Evidence:** 
- **Regression check:** 

## PI-006 — Characters placed inside a hero object's footprint (lifters inside the hull) and the objec [validated, high]

- **Where:** ghost-army 00:00-00:03
- **Root cause:** positions chosen by eye in plan space without the object's measured footprint and contact height
- **Fix:** compute the object's footprint in plan space (rotation included) and stage contacts on its sides; check with tools/frame_checks/check.mjs body_in_mesh
- **Files:** episodes/ghost-army/build/make_film.py, episodes/ghost-army/sets/ghost.js
- **Tests:** node tools/frame_checks/check.mjs episodes/ghost-army/film.json (0 body_in_mesh FAIL in the hook)
- **Evidence:** episodes/ghost-army/production/REVIEW/clip_00000_00150.jpg; production/evidence/pi_test_shot_clip_f72-129.jpg
- **Regression check:** frame checks report the old staging as body_in_mesh FAIL (tank_track) and the new one clean

  - history: 2026-11-18: tested -> validated
