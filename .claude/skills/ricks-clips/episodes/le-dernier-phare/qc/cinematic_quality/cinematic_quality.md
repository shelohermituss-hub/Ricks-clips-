# Cinematic Quality Gate — le-dernier-phare

**Result: PASS** — 11 PASS / 0 WARN / 0 FAIL / 0 NOT RUN

| Status | Group | Check | Detail | Action |
|---|---|---|---|---|
| PASS | film | vertical delivery profile | fps=30; size=[1080, 1920]; target=30 fps, [1080, 1920] | Set film.json fps to 30 and size to [1080, 1920] for the standard vertical master. |
| PASS | environment | kit3d look kit enabled | film.json kit3d=True | Enable kit3d for the PBR relief/sky/tree look; individual places can opt out deliberately. |
| PASS | motion | secondary motion polish | motion_polish={'enabled': True, 'head_follow': 0.14, 'hand_follow': 0.08, 'breath': 0.55, 'breath_rate': 2.4, 'auto_blink': True} | Set motion_polish.enabled=true to enable subtle head follow-through, breathing and safe hand follow-through. |
| PASS | film | cast present | cast entries=1 |  |
| PASS | film | places present | places entries=1 |  |
| PASS | film | takes present | takes entries=1 |  |
| PASS | camera | camera bake frames | 240 frames; 0 malformed entries | Re-bake the plan and fix missing positions, aims, fov or place names. |
| PASS | motion | motion-library QA | Motion QA: PASS Modules 42/42 \| LIB refs 195/195 \| styles 330 \| sampled poses 2640 No missing library references, invalid views, malformed contacts/hands, thrown pose functions or non-finite pose numbers found. | Repair missing motion modules/references or invalid pose results shown in motion_quality.json. |
| PASS | delivery | MP4 metadata | Video: 1080x1920 \| avg 30 fps (nominal 30) \| 8.000 s \| codec h264 Audio stream: present Audio: aac \| 48000 Hz \| 2 channel(s) RESULT: PASS — delivery metadata meets the requested contract. | Correct resolution, frame rate, duration and the required audio stream. |
| PASS | delivery | pixel camera/continuity analysis | PASS camera  roll rate p99, deg/f                                 1.57       target <= 1.1 (Rick 1.08) [Rick 0.26-3.02]   PASS camera  whips per minute                                     0.0        target <= 10 (Rick 5.8) [Rick 0.00-11.77]   PASS camera  camera at rest on long words, %                      37.5       target >= 30 (Rick 33; CB: nouns land at rest) [Rick 2.38-52.87]   PASS camera  voice pace, words per second                         3.95       target 3.5-4.5 (Rick 3.7) [Rick 3.36-4.06]   PASS camera  camera dead still (< 0.3 px/f), % of frames          14.59      target <= 21, aim 9 (Rick 9.3) [Rick 1.16-28.76]   PASS scan    frozen spans (camera and picture still 12+ f)        0          target 0: every long hold has a creep or something moving   PASS scan    travels longer than 7 s                              0          target 0 (a flowing move of 3-7 s is wanted since 2026-11-10; Rick's long travels reach 4.8-9.5 s)   PASS scan    one-frame flashes or A-B-A flickers                  0          target 0 unplanned (planned flashes and washes are fine: confirm each)   PASS scan    picture jumps the plan does not explain (not a planned cut, mood change, effect or kick) 0          target 0   WARN plan    rest share: plan 40 % vs picture 52 %                12.3       target within 12 points          FIX: the render does not follow the bake: re-bake, or the set has parallax the plan cannot see (check foreground props)   PASS plan    plan gates failing (tools/film_plan.py check)        0          target 0   PASS faces   first face, s                                        0.0        target <= 1.5   PASS faces   longest stretch without a face, s                    0.0        target <= 6   PASS faces   head centres inside the caption band, %              0.0        target <= 3 (Rick 2.7) MANUAL  sound-off test, three-point shot check, judge agent 8.5+ per panel RESULT: 0 FAIL, 3 WARN of 21 gates -> /home/user/Ricks-clips-/.claude/skills/ricks-clips/episodes/le-dernier-phare/qc/cinematic_quality/film_analysis/film_check.md | Review film_check.md and repair the measured camera/freeze/flicker/face gates. |
| PASS | render | geometry-aware GPU frame checks | frame_checks: le-dernier-phare/film.json  137 of 240 frames (rests f0-9 f109-129)  cast lina result who            rest         check         number    worst at  bad frames what                                                       0 FAIL, 0 WARN, 17 PASS (8.8 s, scan 2.4 s)  ->  /home/user/Ricks-clips-/.claude/skills/ricks-clips/episodes/le-dernier-phare/out/frame_checks.md | Inspect frame_checks.md and FAIL crops; this gate requires the actual Three.js/WebGL renderer. |

## Human review still required

- [ ] Compare representative full-resolution frames side-by-side with the approved visual reference (camera, world detail, materials, light, atmosphere, silhouette).
- [ ] Watch all key actions at speed: planted feet, limb intersections, hand-object contact, expressions, blinks, follow-through and transitions.
- [ ] Inspect at least 16 evenly spaced final-video frames for character/prop drift, background jumps, floating or clipping.
- [ ] Listen to the complete film: voice, music and effects sync, balance, clipping, silence and ending.

This report does not claim aesthetic approval unless the rendered frames and final sound have actually been reviewed.
