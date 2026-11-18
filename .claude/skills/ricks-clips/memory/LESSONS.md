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
## PI-007 — The finish level of a film was judged by eye; the Ghost Army v1 preview was far below the  [validated, high]

- **Where:** ghost-army whole film
- **Root cause:** no measured standard: the look bible was provisional and no tool compared a preview with the reference
- **Fix:** official fortress standard (references/REFERENCE_LOOK_BIBLE.md v2.0, production/config/reference_standard.json); tools/reference_compare.py measures the reference and every film with the same code; production_controller.py compare-reference writes production/REFERENCE_COMPARE.md and gate F reads it (WARN preview, FAIL final)
- **Files:** tools/reference_compare.py, tools/production_controller.py, production/config/reference_standard.json, references/REFERENCE_LOOK_BIBLE.md, CB_RULES.md, agents/*.md
- **Tests:** tools/tests/test_production_intelligence.py: reference standard: fortress PASS, v1 preview FAIL
- **Evidence:** references/fortress/reference_compare_self.json; episodes/ghost-army/production/REFERENCE_COMPARE.md; references/fortress/compare_ghost_army_2026-11-18.jpg
- **Regression check:** the fortress passes all 10 thresholds; the v1 preview fails 9 of them

  - history: 2026-11-18: tested -> validated
## PI-008 — A pod was deleted before its results were downloaded: the 92-minute stage-8 lock was lost. [tested, high]

- **Where:** ghost-army pipeline
- **Root cause:** pod.py delete terminated the pod with no check of what it held; results lived only on the container disk; the watchdog also removed pods.
- **Fix:** pod.py: manifest.json (path, size, sha256) published by every pod stage, fetch with sha256 check and FETCH_RECEIPT, delete refused unless every listed file is present locally with the same sha256; explicit logged overrides only; watchdogs STOP pods (volume kept).
- **Files:** scripts/runpod/pod.py, scripts/runpod/manifest.py, scripts/runpod/lookdev_pod.sh, scripts/runpod/render_pod.sh, scripts/runpod/gpu_diag.sh
- **Tests:** tools/tests/test_pod_guard.py: 13/13 PASS (fake pod over local HTTP)
- **Evidence:** episodes/ghost-army/production/QA_LOG.json#QA-010
- **Regression check:** not yet run on a real RunPod pod

## PI-009 — The three.js -> glTF lock flattens every surface to one colour: painted textures, vertex c [proposed, high]

- **Where:** ghost-army pipeline
- **Root cause:** GLTFExporter writes the material base colour; canvas maps, vertex colour and InstancedMesh instanceColor are not carried by the lock materials.
- **Fix:** Do not build a film's look on a lossy export: worlds are built natively in Blender (Mission 0 architecture).
- **Files:** docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md
- **Tests:** 
- **Evidence:** episodes/ghost-army/look/proto/pass2
- **Regression check:** 

## PI-010 — A LookDev that replaces the approved palette with photographic PBR colours fails (Ghost Ar [proposed, high]

- **Where:** ghost-army pipeline
- **Root cause:** Poly Haven textures were used with their own albedo; display transform AgX not calibrated against the approved frames; generic HDRI light.
- **Fix:** LookDev is palette-first: place palette is data, PBR maps give relief/roughness/wear and are tinted to the palette, every place is calibrated against the reference with numbers before CB sees it.
- **Files:** docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md
- **Tests:** 
- **Evidence:** episodes/ghost-army/look/proto/pass2
- **Regression check:** 

## PI-011 — Blender's glTF importer turns each GPU instance into its own object (field: 50,656 objects [proposed, medium]

- **Where:** ghost-army pipeline
- **Root cause:** EXT_mesh_gpu_instancing is expanded on import.
- **Fix:** Repeated things are instanced inside Blender (geometry nodes / collection instances); a QA gate counts objects vs instances.
- **Files:** docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md
- **Tests:** blender 5.2.2 import probe of out/lock/sets/field.glb: 50656 objects, 202 meshes
- **Evidence:** 
- **Regression check:** 

## PI-012 — An effect that reads state kept from the previous render makes a frame depend on frame ord [proposed, high]

- **Where:** ghost-army pipeline
- **Root cause:** scene.onBeforeRender stored the camera, the next update used it.
- **Fix:** Every animated value is a function of the frame number only (baked keys in Blender); a determinism test renders frames alone and in sequence and requires identical pixels.
- **Files:** episodes/ghost-army/sets/ghost.js, templates/threejs_film/film.js
- **Tests:** 
- **Evidence:** 
- **Regression check:** reproducibility test interrupted, NOT RUN

## PI-013 — Poly Haven's API answers 403 to the default Python User-Agent. [tested, low]

- **Where:** ghost-army pipeline
- **Root cause:** the API filters generic clients
- **Fix:** Send a client User-Agent (RicksClips-LookDev/1.0).
- **Files:** episodes/ghost-army/look/ld.py
- **Tests:** LookDev job 005 downloaded assets after the fix
- **Evidence:** 
- **Regression check:** 

## PI-014 — Blender RenderSettings.resolution_percentage is an int: a float (37.5) raises TypeError an [tested, low]

- **Where:** ghost-army pipeline
- **Root cause:** bpy property type; the job runner only read the exit code
- **Fix:** Use int percentages or set resolution_x/y; job runners must scan logs for Traceback/TypeError, not only rc.
- **Files:** episodes/ghost-army/look/smoke.py, episodes/ghost-army/look/place_ld.py
- **Tests:** LookDev job 003 ran after the fix
- **Evidence:** 
- **Regression check:** 

## PI-015 — Two renders of the same Blender frame gave different sha256 although the pictures were the [validated, medium]

- **Where:** pipeline render
- **Root cause:** Cycles writes its timings (total_time, render_time) as PNG text chunks; the OIDN denoiser keeps state between renders of one process.
- **Fix:** rc.render strips PNG text chunks after each write and turns stamps off; determinism is tested without denoise (bit-identical) and the denoise tolerance is 1/255.
- **Files:** blender/rc/render.py, tools/tests/test_rc.py
- **Tests:** tools/tests/test_rc.py: determinism frame alone == frame after frame 0 (sha256 equal)
- **Evidence:** tools/tests/test_rc.py
- **Regression check:** 3 repeated pairs bit-identical on a fresh scene (2026-11-18)

  - history: 2026-11-18: tested -> validated
