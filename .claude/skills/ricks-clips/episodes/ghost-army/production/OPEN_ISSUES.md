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
