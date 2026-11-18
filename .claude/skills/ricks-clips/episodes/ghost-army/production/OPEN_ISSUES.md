# Open issues — ghost-army

Blockers that need a user decision (paid asset, account access, licence, creative change, missing reference).

## OI-1 Fortress reference missing (blocks a non-provisional look bible)
- Cause: the fortress video/stills are not in the repository, uploads or references.zip (searched 2026-11-18).
- Options: the user uploads the video (or 10-20 stills: wide/medium/close, interior/exterior, day/night, action); or keep the provisional bible from `references/look_locked/`.
- Recommendation: upload the video; the rick-researcher then rebuilds `references/REFERENCE_LOOK_BIBLE.md`.

## OI-2 Hero tank is a primitive assembly (gate B/G FAIL for the final)
- Measured: 71 parts, 5,616 triangles, 96 % bare primitive generators (render_gpu --inventory).
- Cause: the Asset Hub refuses tank models (weapon/military category). That refusal is respected, not bypassed.
- Options: (a) model a detailed INFLATABLE Sherman in Blender (rubber seams, valves, patches, sag; exterior only), about 20-40 k tris, then GLB and render test; (b) the user supplies or approves a licensed model; (c) accept a written exception for a stylised decoy.
- Recommendation: (a). It fits the story (a fake, inflatable tank) and needs no purchase.

## OI-3 Bicycles drawn by the 2D bike move
- A real 3D bicycle (Sketchfab CC-BY, VladNeko) is converted and render-tested (production/evidence). The 2D rig cannot ride a 3D bike.
- Options: keep the 2D bikes (WARN, needs acceptance); or restage the cyclists pushing or parked beside 3D bikes.

## 2026-11-18 — fortress reference received
- OI-1 (fortress reference missing) is CLOSED: the bible is OFFICIAL (v2.0); captures in `references/fortress/`.
- OI-4 OPEN: the v1 preview fails 9 of the 10 reference thresholds (`REFERENCE_COMPARE.md`). Gap analysis and a 14-step correction plan are in `REFERENCE_GAP_ANALYSIS.md`, **waiting for the user's approval** before any change to the production.

## 2026-11-18 — state after the audit (supersedes older entries where they conflict)
- OI-2 updated: the hero DECOY is now a modelled Blender asset (85,548 tris). Still primitive: the real tanks at the crossing (96 % primitives) and the 2D bicycles (OI-3).
- OI-4 updated: the V3 preview fails 4 of 10 fortress thresholds (edge, saturation seconds, motion, peaks); see STATE.md.
- OI-5 NEW: stage-8 lock lost with its pod (QA-010). Rebuild through the new Blender pipeline, not by re-running the three.js lock.
- OI-6 NEW: Blender LookDev prototype failed (QA-011); method replaced by the Mission 0 architecture.
- OI-7 NEW: GPU final rendering never proven on a full render since the RunPod GPU fix; needs a paid pod (CB approval).
