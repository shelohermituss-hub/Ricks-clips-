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
## PI-016 — Characters and props appeared, disappeared, teleported or shrank in view: the hero 'appear [validated, high]

- **Where:** crashed_car s01 3.0 s, s02 4.75-5.6 s
- **Root cause:** Each case was fixed locally without a rule or a check, so the next shot repeated it; a change of state was built as a visibility/location switch instead of an animated action; and the 2D move-to-move blend silently does nothing when the two moves are drawn in different views (puppets.mjs moveOf), so arms snapped between moves.
- **Fix:** CB_RULES 11h: everything happens through an action, the camera never stops, real surfaces and shadows. demos/crashed_car/shots/continuity.py runs on every built shot BEFORE any render (render_layers.sh refuses to render on FAIL): POP, TELEPORT, SHRINK/GROW, POSE_POP, HOLD; BREAK (a whole replaced by its own pieces) and FX are reported as allowed. tools/card_anchors.py measures head, feet, hands and pose pops on every drawing (card_service runs it automatically) so 3D props follow the drawn head/hands. Shot analyses get a mandatory section 'Entrées / sorties / changements d'état'.
- **Files:** CB_RULES.md, demos/crashed_car/shots/continuity.py, demos/crashed_car/shots/render_layers.sh, tools/card_anchors.py, tools/card_service.py, demos/crashed_car/shots/s02_pit.py, demos/crashed_car/shots/s02_corner.py, demos/crashed_car/tracks_s02.json, references/crashed_car/shots/s02.md
- **Tests:** continuity.py on the old s02_pit build: 7 POP, 2 TELEPORT, 1 HOLD (FAIL, the reported errors); continuity.py on the new s02_pit and s02_corner: PASS 0/0/0; continuity.py caught a new helmet side-swap at 223 in s02_corner; fixed, PASS
- **Evidence:** demos/crashed_car/build/continuity/*.json
- **Regression check:** render_layers.sh refuses to render a part whose continuity report is not ok

## PI-017 — A fresh session (handoff) could not pass tools/tests/test_rc.py: 2 FAIL (library: vintage_ [validated, medium]

- **Where:** pipeline -
- **Root cause:** Files outside git were produced once by hand: a throw-away bike2glb.py (gltf -> 1k glb) never committed, and a film_plan bake the test silently assumed. The handoff listed what to re-download but not how to rebuild derived files.
- **Fix:** tools/gltf_to_glb.py (re-packs the scaled textures: the glTF importer packs images, so scaling alone exported the original 2048 px bytes, 34.5 MB instead of 3.7 MB); test_rc bakes the plan itself when out/ is missing; scripts/restore_untracked.sh restores every untracked input idempotently (Sketchfab models, glb conversions, baked plan); asset.json fetch_note gives the exact rebuild command.
- **Files:** tools/gltf_to_glb.py, tools/tests/test_rc.py, scripts/restore_untracked.sh, library/assets/sketchfab/1795f6e907634afda88fdaf45f67b279/asset.json
- **Tests:** fresh session: test_rc 25/27 FAIL -> 27/27 PASS after the fix; gltf_to_glb: 3.7 MB, 49483 tris, 1024 px JPEG (same numbers as the 2026-11-18 conversion); restore_untracked.sh rebuilds a deleted glb, second run converts nothing
- **Evidence:** tools/tests/test_rc.py output 2026-11-19
- **Regression check:** run scripts/restore_untracked.sh then test_rc.py at every handoff

## PI-018 — Chosen by name, two library moves did not act what the plan said: lift/B raises the arms a [validated, medium]

- **Where:** crash_instinct s01 0.4-1.2 s
- **Root cause:** Moves were picked from their id/feeling labels without measuring what the drawing does over time; there is no front-view 'sit on the ground' move.
- **Fix:** Measure every chosen move on the drawings (card_anchors.py head_top / feet / hands per frame) before building; start a move at the right moment with the pose offset syntax 'm:<id>@<seconds>' (puppets.mjs); preview candidate moves side by side with templates/motion_styles/render.mjs --still. Shot 1 uses inspect/B (squat, hands low) and m:sit/A@0.7 (the plop lands on the word), the hidden seat sunk 0.30 m into a tall grass tuft.
- **Files:** demos/crash_instinct/tracks_s01.json, demos/crash_instinct/shots/s01_plant.py
- **Tests:** anchors before: head 1.87 m during lift/B (no bend), sit starts at +26 frames; anchors after: squat 1.65 m at 12-18, plop 30-36, seated from 48; 0 pose pops
- **Evidence:** demos/crash_instinct/build/cards_s01/cards/planter/anchors.json
- **Regression check:** card_service prints anchors; read head_top/feet per act before building

## PI-019 — Falling leaves teleported (70 TELEPORT) and an acorn cap popped: a random delay was drawn  [validated, medium]

- **Where:** crash_instinct s01
- **Root cause:** Randomness must be drawn once per object, never per frame; a visibility switch on a parent does not carry to children.
- **Fix:** Random values drawn once per object before the frame loop; no visibility switch for a thing that goes into a hole: it sinks under the surface that covers it. continuity.py caught both before any render (the check works as the permanent guard).
- **Files:** demos/crash_instinct/shots/s01_plant.py
- **Tests:** continuity before: POP 1, TELEPORT 70 (FAIL); continuity after: PASS 0 everywhere
- **Evidence:** demos/crash_instinct/build/continuity/s01_plant.json
- **Regression check:** render_layers.sh refuses to render on a continuity FAIL

## PI-020 — A 'hard cut' at frame 96 written in the analysis did not exist: shots 1 and 2 are ONE cont [validated, high]

- **Where:** crash_instinct 3.2 s (frame 96)
- **Root cause:** An improvised per-frame difference detector with a fixed threshold (14) took a 14.1 motion peak for a cut, while the repository tool (tools/analyze_reference.py, shots.json) correctly found no cut before 22.9 s.
- **Fix:** Shot boundaries come from tools/analyze_reference.py shots.json; every boundary is checked at 30 fps around it before a shot is planned (a cut is a one-frame spike, a camera move is a ramp over several frames). A shot that continues the previous take is built ON TOP of the previous shot's script (s02_crash imports s01_plant.build_take), so set, car, card and camera are the same objects.
- **Files:** references/crash_instinct/ANALYSE_FR.md, references/crash_instinct/shots/s02.md, demos/crash_instinct/shots/s01_plant.py, demos/crash_instinct/shots/s02_crash.py
- **Tests:** per-frame difference 88-176: no one-frame spike; ramps at 101-121 and 150-176; continuity.py on s02_crash (frames 96-176): PASS 0 everywhere
- **Evidence:** references/crash_instinct/shots/s02_tr_sheet.jpg
- **Regression check:** shots/sNN.md must cite shots.json and the 30 fps check of each boundary

## PI-021 — A wheel detached from the Sketchfab car rolled around the wrong point and never tipped ove [validated, medium]

- **Where:** crash_instinct s02 4.1-4.9 s
- **Root cause:** glTF parts keep their origin at the model origin (the car centre), not at the part's centre; the tip-over was applied about the axle instead of about the rolling direction.
- **Fix:** Before animating a part on its own: move its mesh origin to its bounding-box centre (mesh.transform(-c), world matrix @ T(c)); spin about the axle, tip about the path direction (s02_crash.wheel_off).
- **Files:** demos/crash_instinct/shots/s02_crash.py
- **Tests:** key frames 126-149: wheel rolls, wobbles, lies flat from 134; continuity PASS
- **Evidence:** demos/crash_instinct/build/keys_s02/compare.jpg
- **Regression check:** look at the part on 3 key frames after detaching it

## PI-022 — CB: no cinematic light. No sun rays, the trunk dark in full daylight, a flat painted sky,  [validated, high]

- **Where:** crash_instinct s01-s02
- **Root cause:** The look was judged by eye on our own frames, never MEASURED against the reference. The sun was front-lit (the reference is backlit). No fill light under the big crown. The sky was a gradient with mesh clouds. The Sketchfab paint kept its metallic/roughness texture and normal map.
- **Fix:** Cinematic kit in sets/roadside.py: visible HDRI sky (Poly Haven, rotated so its sun matches the sun lamp), backlit sun, bounce_fill area light (camera-side, invisible), thin haze volume + light_shafts attached to the tree, shorter and half-dense grass recoloured to measured values. Grade = Standard + Medium Contrast, exposure -0.35, saturation 1.05, chosen by measuring 5 transforms. tools/grade_match.py compares key frames with the reference (luma, saturation, contrast) and must PASS before a preview. Car paint: the asset's texture, metallic, roughness and normal links removed (they made it sparkle), then a SMOOTH METALLIC white (metallic .55, roughness .28, coat .6) as CB asked; untinted glass. Grass: CB found it too dark and dull -> ramp #4e8a2e..#a4d866 (hue 90 vs reference 87-96, lightness .34-.39 vs .29-.38), exposure -0.5.
- **Files:** demos/crash_instinct/sets/roadside.py, demos/crash_instinct/shots/s01_plant.py, demos/crash_instinct/shots/s02_crash.py, tools/grade_match.py
- **Tests:** grade_match before: frame 126 luma 0.65 vs 0.49, frame 46 saturation 0.12 vs 0.35 (FAIL); grade_match after: frames 0, 46, 126, 149 PASS
- **Evidence:** demos/crash_instinct/build/look/grade_sheet.jpg
- **Regression check:** tools/grade_match.py on the key frames of every shot

## PI-023 — CB's corrections kept repeating the same family: flat road without wear or tyre marks, fla [validated, high]

- **Where:** crash_instinct s03 (aerial)
- **Root cause:** Corrections were applied to the shot, not to the method: the first version of a new set started from flat or default values, and nothing in plan_check or the helpers refused it.
- **Fix:** All corrections are now DEFAULTS: blender/rc/look.py (visible HDRI sky rotated to the sun, hard sun, bounce fill, sun shafts, light haze, scanned PBR with relief, road wear: wheel paths + tar snakes), roadside.py (furrowed fields, real fence with varied posts, sagging wires and shadows, same green verge on both sides, LOD grass), plan_check LOOK + vehicle checks (a plan without look is REFUSED: test_plan_check), docs/CORRECTIONS_CB_FR.md (every correction -> rule -> where it is enforced), continuity.py CLIP (camera far clip cuts the set).
- **Files:** blender/rc/look.py, demos/crash_instinct/sets/roadside.py, tools/plan_check.py, tools/tests/test_plan_check.py, docs/CORRECTIONS_CB_FR.md, demos/crashed_car/shots/continuity.py
- **Tests:** test_plan_check: a plan without look FAILS 7 LOOK checks; plans s01-s03 and the example: PLAN PASS with look blocks; continuity PASS with CLIP 0; set moved to rc.look: frame 262 identical (0.00/255)
- **Evidence:** demos/crash_instinct/build/look3/compare.jpg
- **Regression check:** python3 tools/tests/test_plan_check.py

## PI-024 — The camera far clip (Blender default 100 m, then 1000 m) cut the set: the fields stopped a [validated, medium]

- **Where:** crash_instinct s03
- **Root cause:** No check compared the camera's clip_end with how far the set reaches.
- **Fix:** continuity.py CLIP: fails when a big flat set piece reaches farther than clip_end and prints the fix (cam.data.clip_end = N). Default clip_end 4000 m in the shot camera.
- **Files:** demos/crashed_car/shots/continuity.py, demos/crash_instinct/shots/s01_plant.py
- **Tests:** continuity before the fix: CLIP 1 (set reaches 2588 m, clip 1000 m); after: CLIP 0
- **Evidence:** demos/crash_instinct/build/continuity/s03_aerial.json
- **Regression check:** continuity.py runs before every preview and render

## PI-025 — Aerial view: the oak's shadow was a small soft blob toward the camera instead of the long  [validated, high]

- **Where:** crash_instinct s03
- **Root cause:** The visible HDRI sky also LIT the scene at full strength: its own photographed sun (48 deg high) cast a second short shadow and its fill washed out the shadow of the sun lamp. The sun lamp was not the dominant light.
- **Fix:** rc.look.sky_hdri: for every ray but the camera's the sky is capped (no hot sun) and dimmed (light=.5): the lamp is the only sun. Sun height and direction MEASURED on the reference shadow (length / object height, direction on the ground): crash_instinct -48 deg, 15 deg. A sun-only debug render (world strength 0) shows what the lamp really does.
- **Files:** blender/rc/look.py
- **Tests:** frame 180 before: contrast 0.14, shadow 1 crown long; after: contrast 0.20 (ref 0.21), shadow crosses the road and the far verge; grade_match PASS on 180 and 262
- **Evidence:** demos/crash_instinct/build/review/keyframes_ref_vs_ours.jpg
- **Regression check:** grade_match.py on the key frames of every shot

## PI-026 — From the air the grounds were flat colours with visible repeating squares: one green, brow [validated, high]

- **Where:** crash_instinct s03
- **Root cause:** A scanned texture tiled every 2-4 m averages to ONE colour from 15 m up; a multiply tint over a dark scan cannot reach a light target colour; a grazing/high camera needs its own measured values.
- **Fix:** rc.look.tex: recolor (the scan keeps its detail, takes the measured colour), untile (second bigger turned copy mixed by noise), macro (3-25 m patches lighter/darker), stripes (regular rows readable from the air). Target colours are sampled on the reference frame, not guessed.
- **Files:** blender/rc/look.py, demos/crash_instinct/sets/roadside.py
- **Tests:** frame 180: fields #86735a -> gold/ochre/straw rows; road near #6c6c68 -> dark blue-grey; saturation 0.29 (ref 0.30)
- **Evidence:** demos/crash_instinct/build/review/keyframes_ref_vs_ours.jpg
- **Regression check:** key frame from the highest camera of the film, side by side with the reference

## PI-027 — Backlit grass tufts were either dark (sun only) or flat neon green (sky fill): the tree's  [validated, medium]

- **Where:** crash_instinct s03
- **Root cause:** Blades were opaque: with the sun behind, the camera only sees their shadow side.
- **Fix:** Grass and leaves let light through (Translucent mixed at .45 into the blade material): they glow in backlight and the shadows of big objects read on them.
- **Files:** demos/crash_instinct/sets/roadside.py
- **Tests:** frame 180: the oak shadow is readable on the right verge
- **Evidence:** demos/crash_instinct/build/k/v5_180.png
- **Regression check:** key frame with the sun behind the subject

## PI-028 — A fresh session on another account lost 40 minutes on the environment: Blender 4.0 install [validated, medium]

- **Where:** crash_instinct s03
- **Root cause:** The cloud environment (allowed hosts, network secrets) is an account setting, not in git; the Sketchfab secret was saved as Bearer while an API token needs the prefix Token; restore_untracked.sh did not list the SUV.
- **Fix:** restore_untracked.sh downloads the SUV too and says which prefix the secret needs; HANDOFF 0 lists the environment check first (get the environment, hosts of CLOUD_NETWORK_DOMAINS.txt, secret with prefix Token, verify with /v3/me = 200).
- **Files:** scripts/restore_untracked.sh, HANDOFF.md
- **Tests:** api.sketchfab.com/v3/me: 401 with Bearer, 200 with Token; test_rc 27/27 after restore
- **Evidence:** scripts/restore_untracked.sh
- **Regression check:** first step of every new session

## PI-029 — The second imported car came out white instead of blue: the paint was applied to the first [validated, medium]

- **Where:** crash_instinct s04
- **Root cause:** bpy.data.materials.get('body') returns the FIRST material of that name; the second import's material is 'body.001'.
- **Fix:** Materials of an imported model are collected from the imported objects' own slots (dict by base name), never looked up by bare name.
- **Files:** demos/crash_instinct/shots/s04_sign.py
- **Tests:** key frame 324 before: white car; after: blue #2f74d8, clear glass
- **Evidence:** demos/crash_instinct/build/review
- **Regression check:** key frame of every imported vehicle

## PI-030 — Shot 4 was lit with the aerial view's backlight: the tree, the sign and the posts were dar [validated, high]

- **Where:** crash_instinct s04
- **Root cause:** The light was copied from the previous view instead of being read on the reference for THIS view; the reference re-lights each view (shadow of the sign falls behind it: sun on the camera's side).
- **Fix:** Each shot analysis has a table 'clue on the reference -> light' (shadow direction and length, lit faces, sky, glow, fill). rc.look.relight() changes sun, sky rotation, glow and fill together on one frame, off-frame inside a whip.
- **Files:** blender/rc/look.py, demos/crash_instinct/shots/s04_sign.py, references/crash_instinct/shots/s04.md
- **Tests:** frame 309: luma 0.52 -> 0.42 (ref 0.45), saturation 0.27 -> 0.36 (ref 0.40); sky blue; sign and posts lit
- **Evidence:** demos/crash_instinct/build/review
- **Regression check:** grade_match on the key frames of every view

