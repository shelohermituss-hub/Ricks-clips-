# Production state — ghost-army (updated 2026-11-18, Mission 1 start)

## Where the project is
The project is being restructured (CB approved Mission 0, `docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md`): Blender becomes the single world engine,
three.js keeps only the character drawings. Ghost Army is the migration target; the **field** is the Mission 2 prototype place.

## Old pipeline position (WORKFLOW.md 1-12) — frozen at this state
| # | Stage | State | Evidence |
|---|---|---|---|
| 1-6 | Story, script, voice, Rick examples, plan, sets + storyboard | done | SCRIPT.md, voice/, film.json (plan 0 FAIL) |
| 7 | Full three.js preview | done to **V3** (05:26); later code changes NOT in any preview | v3/ghost_army_preview_v3_*.mp4 |
| 8 | Lock | **LOST** — done on pod 098nig2lticccc (14/14 card sets, 9 sets, NaN check 0) and the pod was deleted before download. Local out/lock = partial interrupted export (no lock.json) | QA-010 |
| 9 | Blender LookDev | **FAILED** — prototype passes 1-3 on field/café/road, wrong colours | QA-011, look/proto/pass2 |
| 9b | three.js enrichment (alternative) | stills only, 3/9 places; now a variant of film.json (`render_gpu.mjs film.json --variant enrich`), off by default | look/three_enrich/ |
| 10-12 | Final render, captions, delivery | NOT RUN | — |
| 11 | Sound | preview mix done (-14.97 LUFS DECLARED) | sound/ |

## Code fixed but not verified (Mission 1 test list)
- Sound-wave rings use the current frame's camera (QA-012). Seeded dust (QA-013). Variants in film.json (O17). From_lock instance collapse (QA-014, migration path only).
- Pod results guard: tested 13/13 on a fake pod; never run on a real pod.

## Quality numbers (V3 graded vs fortress, 05:32)
edge 0.060 (>= 0.075 FAIL), saturation-seconds 8 (FAIL), motion 12.9 (>= 18 FAIL), peaks 5.47/10 s (FAIL); luma, crushed, burned, saturation, still frames PASS.

## Mission 1 (foundations) — done 2026-11-18, report docs/MISSION_1_FONDATIONS_RAPPORT.md
blender/rc: cache, library (10 assets), qa, geo, assemble, render, cli; card drawing cache; scene-gates; blender_pod.sh (NOT RUN on a pod).
Tests: test_rc 15/15, test_pod_guard 13/13, test_production_intelligence 11/11.

## Next
Mission 2 prototype on the field (sequence ~150 frames) + destruction test (dozer vs cart); GPU benchmark/render needs CB approval.
