# Brief — deep analysis of ONE reference video (style_analysis mission)

You analyse **one** video in depth. Another analyst does each of the four other videos; a lead then compares the five. Your output must be
**evidence-based, timecoded and reusable**: it will become production rules for RicksClips (3D cartoon true-story Shorts built in Blender:
3D sets, stick-figure characters). Write the analysis **in French**. Keep file names, CSV headers and status words exactly as below.

Working folder (all paths relative to it): `/home/user/Ricks-clips-/.claude/skills/ricks-clips/references/style_analysis/`
Run tools from `/home/user/Ricks-clips-/.claude/skills/ricks-clips/` with `.venv/bin/python references/style_analysis/tools/x.py ...`
(`x.py` docstring lists the commands: `seq`, `still`, `crop`, `color`, `kmeans`). Frame numbers are 0-based at 30 fps; timecode = frame / 30,
written `00:00:SS.mmm`.

## What is already measured for you (read these first)
- `data/<V>/tech.json` — file facts. `data/<V>/words.json` — every spoken word with start/end (speech-to-text: the text can contain errors).
- `data/<V>/cuts_auto.json` — cut / fast-move CANDIDATES from frame difference. They are candidates: **verify each by eye**, and look for cuts
  the detector missed (dissolves, whip pans, hidden cuts). `data/<V>/frame_diff.json` has the per-frame difference (`diff[i]`) if you need it.
- `data/<V>/per_second.json` — luma, saturation, contrast, motion per second. `data/<V>/audio.json` — loudness, 50 ms RMS envelope, onsets, quiet spans.
- `evidence/<V>/overview_NN.jpg` — the WHOLE video at 2 fps (frame number burnt in). `_work/<V>/f10/tNNNN.jpg` — the whole video at 10 fps
  (file N = frame (N-1)*3).

## Method (three levels — the mission requires all three, and an honest record of what you really looked at)
- **Level A, full coverage**: read every `overview_NN.jpg`. Build the complete shot list (verify cuts by eye; note continuous takes).
- **Level B, each shot**: look at enough frames of every shot to describe beginning / development / action / reaction / end. Use
  `x.py seq <V> f0 f1 3` (10 fps) and read the contact sheets it prints. Denser for long shots, gestures, expression changes, camera moves.
- **Level C, frame by frame**: for the richest passages (impacts, falls, collisions, destruction, fast gestures, expression changes, several
  characters acting at once, complex camera moves, VFX birth/evolution/death, consequences that persist, hard joins) run
  `x.py seq <V> f0 f1 1` and READ every sheet. Aim for at least 8 such passages, more if the video is rich. Record the exact frame ranges.
- Keep a log as you go: which ranges were inspected frame by frame, which at 10 fps, which only at 2 fps.
- Save 40 to 70 evidence stills / crops with `x.py still` / `x.py crop` (they are kept in git): one or more per shot, plus the key moments of each
  event chain and close crops of characters, materials and details. Cite them by file name in the analysis.
- Sample colours with `x.py color` (regions you choose on named frames) and `x.py kmeans`; never invent a hex value.
- The audio cannot be listened to: you have the word timings, the RMS envelope, onsets and loudness only. Say so. Infer sound events only where
  an onset coincides with a visible event, and label them INFÉRÉ. Do not transcribe long passages of the narration (short quotes only).

## Evidence rules (strict)
Every important statement carries a status: **OBSERVÉ** (seen in the frames), **MESURÉ** (from a measurement), **INFÉRÉ** (plausible, not proven),
**INCONNU** (cannot be determined), **RECOMMANDATION** (a proposal for RicksClips, not a claim about how the original was made).
Cite `V0x`, timecode, shot id, frame number, evidence file. Never present a guess as a fact. You cannot know the software, engine, rig or texture
sources: propose equivalents labelled **reconstruction proposée**. No vague words ("cinématique", "détaillé", "réaliste") without saying which
visible elements produce the effect, where, and how to formalise it. Never claim frame-by-frame inspection you did not do.
Do not generalise from one shot. Separate what is constant in this video from what happens once.

## Deliverables (write exactly these files)
1. `per_video/<V>_ANALYSIS.md` — the full analysis, sections:
   0 Fiche technique et couverture réelle · 1 Structure narrative et rythme (durée des plans, coupes/transitions, pauses, accélérations, lien
   voix-image: which word lands on which action) · 2 Timeline des plans (table) · 3 Personnages: design (proportions measured in pixels:
   head/body ratio, limb thickness, outline, eyes, brows, mouth, hair, clothes, accessories, colours, readability by distance), expressions et
   acting, corps et poses, **micro-animations** (for each: who, body part, trigger, timing, duration, amplitude, one-off or cyclic, link to the
   main action, evidence, reusable recipe) · 4 Environnements (per place: geometry, terrain, depth layers, leading lines, action zones, density),
   assets (hero / secondary / dressing / background / transient), details and textures (wear, dirt, joints, roughness variation, at what
   distance they are visible), atmospheric depth, LOD · 5 Caméra (per shot: scale, angle, apparent focal RANGE, depth of field, composition,
   move with start/end/trajectory/duration/easing/settle, shake, relation to the rhythm) + reusable camera recipes · 6 Lumière, palettes,
   matériaux, étalonnage (per mood really present: direction, hardness, key/fill/rim, shadows, contact, sky, volumetrics, reflections; sampled
   palettes with hex/HSV/Lab; blacks, highlights, bloom, vignette, grain, sharpness; compression artefacts vs intent) · 7 Animation de
   l'environnement (wind, grass, smoke, flags, background vehicles…: amplitude, frequency, cause, continuous vs triggered) · 8 **Interactions,
   physique et conséquences** (priority): for each important event the 11-step causal chain: initial state, anticipation, trigger, contact,
   reaction, transfer of motion, deformation/displacement, secondary effects, reaction of the set, final state, **persistence in later shots**;
   for vehicles say honestly what IS and IS NOT shown (dents, detached parts, glass, dust…) · 9 VFX et compositing (per effect: trigger,
   place, duration, size, path, density, colour, transparency, evolution, reaction to light, death, sync with sound; 3D / 2D / compositing /
   editing / unknown) · 10 Son (role and timing only) · 11 Texte à l'écran (captions: font look, size, position, timing vs words; any other
   on-screen text or diegetic lettering) · 12 Ce qui est constant dans cette vidéo / ce qui n'arrive qu'une fois / INCONNU ·
   13 Recettes réutilisables pour RicksClips (RECOMMANDATION) · 14 Journal de couverture.
2. `data/<V>/shots.csv` — header exactly:
   `video,shot_id,frame_start,frame_end,tc_start,tc_end,duration_s,place,time_of_day,characters,main_action,secondary_actions,emotion,shot_type,camera_move,light_change,vfx,sound_events,narrative_function,transition_out,narration_words,evidence`
3. `data/<V>/events.csv` — header exactly:
   `video,event_id,tc_start,tc_end,frame_start,frame_end,shot_id,actor,target,trigger,action,contact_type,primary_response,secondary_responses,set_reaction,final_state,persistence,evidence,confidence,reusable_recipe`
4. `data/<V>/assets.csv` — header exactly:
   `video,asset_id,name,class,place,function,silhouette,approx_scale,apparent_material,detail_level,surface_state,interaction,variants,camera_distance,continuity_role,first_tc,evidence`
   (`class` is one of hero, secondary, dressing, background, transient_vfx)
5. `data/<V>/palette.json` — `{"video": "<V>", "moods": [{"mood": "...", "place": "...", "frames": [...], "samples": [<the JSON printed by x.py color, with a "role" field: dominant / secondary / accent / shadow / highlight / skin / sky ...>], "kmeans": [<x.py kmeans outputs>], "notes": "..."}]}`
6. `data/<V>/coverage.json` — `{"video","frames_total","shots","stills_saved","ranges_frame_by_frame":[[f0,f1,"why"]...],"ranges_10fps":[[f0,f1]...],"ranges_2fps_only":[[f0,f1]...],"complex_passages_studied":[...],"audio":"what was and was not analysed","tool_limits":[...],"not_done":[...],"confidence":"high/medium/low + why","status":"PASS|PARTIAL"}`
CSV rules: UTF-8, comma separated, every field in double quotes, no line breaks inside a field. Validate each CSV with Python's `csv` module and
each JSON with `json.load` before you finish.

## Limits
Analysis and documentation only. Write only inside `references/style_analysis/` (your `per_video/`, `data/<V>/`, `evidence/<V>/`, `_work/<V>/`).
Do not touch the sources, the production code, other analysts' files, or git. No rendering. Do not spawn other agents.
Your final message (to the lead, not the user): 15 lines at most — shot count, event count, asset count, stills saved, frame-by-frame ranges,
the 8 most important findings, and anything you could not do.
