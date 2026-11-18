# Production state — ghost-army (updated 2026-11-18)

## Pipeline position (WORKFLOW.md 1-12)
| # | Stage | State |
|---|---|---|
| 1 | Story | done |
| 2 | Script | done (approved) |
| 3 | Voice | done (approved) |
| 4 | Rick examples | done |
| 5 | film.json plan | done (0 FAIL, 8 WARN) |
| 6 | Sets + storyboard | done (rough board approved) |
| 7 | Full three.js preview | done, iterated: v1, v2, **V3** (540x960, 2026-11-18) |
| 8 | Lock (`render.mjs --export-lock`) | NOT DONE (the out/lock folder is an old test, not a lock of V3) |
| 9 | Blender look pass / LookDev (`templates/blender_look/from_lock.py`, materials, lights, scatter, post) | NOT DONE on this film |
| 10 | Final render | NOT DONE (needs CB approval) |
| 11 | Sound | done for the preview (mix -14.97 LUFS / -1.0 dBTP); re-check after lock |
| 12 | Captions, QA, delivery | NOT DONE |

## LookDev audit (2026-11-18, V3 frames + renderer inventory)
- Blockout and geometry: done.
- Detailed modelling: partial. Hero objects are Blender models; set dressing is still primitives (café 100 %, photo 83 %, field 67 %, radio 66 %, bedroom 64 %, attic 58 %, camp 40 %, road/river 35 %).
- PBR textures: partial. Procedural only, no photographic PBR sets; textured share 35-77 % (standard >= 85 %).
- Dressing: partial. Light: partial (shadows only within 14 m, no AO, no GI). Atmosphere: partial (exteriors yes, interiors no). Vegetation/terrain: partial. Grade: nearly done.
- Verdict: dressed blockout in interiors, partial LookDev outside; stage 9 never run.

## Next (in order)
1. Finish stage 7 fixes still open (V3 completion report section F).
2. Stage 8: lock the V3 film.
3. Stage 9: LookDev per place (Blender from_lock + PBR Poly Haven / ambientCG + light + air), a comparative test on 3 shots first, CB approves one still per place.
4. Stage 10: final render (RunPod 4090, GPU path fixed) after CB approval. 5. Stage 12: QA and delivery.
