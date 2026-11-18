# REFERENCE LOOK BIBLE — level of finish (Production Intelligence v1.0)

**STATUS: PROVISIONAL.** The user's main reference is the analysed **fortress video**. It is not in this repository,
in the uploads, or in `references.zip` (searched 2026-11-18: no video, still, report or note names it). Until it is supplied,
this bible is built from the four **approved** look references in `references/look_locked/` (CB-approved Night Witches stills),
which set the same kind of target: a level of finish, not a décor to copy. When the fortress material arrives: analyse wide,
medium, close, interior, exterior, day, night, action and atmosphere shots, replace the PROVISIONAL marker, and keep this
version in git history (never silently rewrite).

Comparison sheet: `references/REFERENCE_SHEET_look_locked.jpg` (the 4 approved stills, side by side).

## Measured on the approved references (1440x2560 stills)
| still | mean luma | saturation | crushed (<2 %) | burned (>98 %) |
|---|---|---|---|---|
| night_airfield | 0.22 | 0.62 | 0.000 | 0.000 |
| night_camp | 0.21 | 0.61 | 0.000 | 0.000 |
| stage1_airfield | 0.22 | 0.63 | 0.026 | 0.000 |
| stage1_camp | 0.25 | 0.59 | 0.051 | 0.000 |

Read: night frames sit around 0.21-0.25 mean luma with **no** crushed blacks and no burned highlights in the final look;
colour is rich (saturation about 0.6) but the night stays blue with warm practical lights.

## What the finish looks like (observed, 2026-11-18)
1. **Hero objects are modelled, not blocked:** the biplane has two wings with ribs, struts and bracing wires, a radial engine,
   a propeller and landing gear; the bomb has fins, a red band and stencil marks; the crate has planks, slots and battens; the cart
   has spoked wheels and a shaft. No hero is a recoloured box or cylinder.
2. **Three depth planes in every frame:**
   - foreground: big props near the lens (bomb, cart wheel, lantern post, boardwalk planks);
   - middle: the character and the action;
   - background: tents, poles with wires and insulators, trees and smoke.
3. **Silhouette variety:** tents, poles, trees, smoke columns and aircraft read as different shapes against the sky; repeated
   items vary in size, angle and state.
4. **Surfaces carry story and wear:** stencils, paint bands, planks with gaps, sandbags, pebbles, grass clumps of
   several heights.
5. **Motivated light:** one cool key (moon) plus warm practical pools (lanterns, a window), searchlight shafts as visible volumes,
   rim light on characters from the scene source, long shadows.
6. **Atmosphere:** haze and smoke separate the planes; stylised volumetric clouds; stars and planes in the sky give life and scale.
7. **Characters stay the approved 2D vector cast** (cards in the 3D world); only the world gains detail.

## Acceptance criteria for reviews (used by ENV_SCORES.json, gate C)
Score each place 0-4 per criterion. 0 = absent, 1 = blockout/primitive, 2 = readable but poor, 3 = detailed and coherent, 4 = this finish level.
- **geometry:** hero and secondary objects have real parts (target ≥ 20 parts and ≥ 12 k triangles for a hero, < 60 % bare
  primitive generators; measured by `render_gpu.mjs --inventory`).
- **variety:** no visibly cloned row without variation.
- **materials:** textured or relief materials on every large surface; wear and dirt where the place has a reason.
- **depth:** the three planes are present in the frame, not only in the set.
- **lighting:** one motivated key plus practicals, readable shadows, faces lit by the scene source.
- **atmosphere:** haze, smoke or dust that fits the place.
- **coherence:** period, story and palette agree.
- **env_motion:** wind, water, smoke and lights move where the story gives a reason.

A main place does not go to the final render with an essential criterion (geometry, materials, depth, lighting, coherence)
below 3, unless the user accepts a written exception. Grade targets: night mean luma ≥ 0.21 (the reference) with
crushed ≤ 1 %, burned ≤ 0.5 %; day mean 0.40-0.48.
