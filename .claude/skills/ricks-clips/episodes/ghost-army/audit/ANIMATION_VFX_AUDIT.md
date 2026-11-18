# THE GHOST ARMY: character animation, micro-animation and VFX audit (2026-11-17/18)

Scope: the real implementation was read and measured before anything was changed. "Done" below means the data or code was changed **and** the result was rendered and looked at (frame strips every 3rd frame over the whole film, plus close crops of every changed beat). Rendering resolution was not touched by this audit.

## 1. How the characters are animated (what the pipeline actually is)

- **Rig.** The cast are 2D vector puppets on cards in the 3D world (`templates/vector2d_characters`, `templates/threejs_film/puppets.mjs`). There is no 3D skeleton. A pose is a set of numbers: body lean/rot, hip height, two feet (lift, knee bend), two hands (reach/drop/bow), head tilt, face. Arm length is fixed (about 209 units), so a hand cannot reach far above the head.
- **Two animation systems exist in the kit.**
  - **Static kit poses** (`stand`, `knock`, `hold_up`, `point_out` ...) are single frozen drawings. With no `tween` in film.json they switch in one frame. The motion-polish layer (breathing, blinks, head follow-through) does **not** run on them. CB_RULES: "NEVER A STATIC KIT POSE ... blocking stand-ins only".
  - **Library moves** (`m:<id>`, `templates/motion_styles`, 198 registered) are time-driven poses with planted bending legs and acted timing. Motion polish (breath, blink, head and hand follow-through) and the cloth lag run on top of them.
- **Position.** The plan (`tools/film_plan.py`) moves a card between act positions:
  - `walk=True` swaps in a 2-frame step toggle, a forbidden stand-in walk.
  - Anything else slides the card. With a walk/run/bike library move playing, the legs move while the card travels.
- **Faces** change as a step (CB rule), with a 5-frame head pop. There is no gaze control: the baked `look` target is not used by the renderer, so eye direction comes only from the face drawing and the facing direction.

## 2. What the v1 preview really had (measured by `audit/anim_audit.py` on the v1 film.json)

| Measure | v1 | now |
|---|---|---|
| acts that are frozen kit drawings | **40 of 64** | 0 of 73 |
| acts that are library moves | 5 | 57 (+7 hidden place changes, +9 face-only beats) |
| planner 2-frame walks | 3 | 0 |
| glides (position slides with no legs) | 7 (carriers 3.7 m in 0.4 s; Lou 4.3 m in 0.4 s across the tank) | 0 |
| bikes | 21 m in 1.3 s (≈16 m/s) with normal pedalling | 9 m in 2 s (≈4.5 m/s), then a slow roll to a stop |
| `film.tween` | none: every pose change snapped in one frame | `ones` (new pose every frame), faces as a step, **6-frame move-to-move blend** (new kit feature) |
| breathing / blinks on screen | only on the 5 library acts | on every act |
| moves still running when the next beat starts | 1 (Lou's "very strong" flex was overwritten by a late walk) | 0 (new OVERLAP check) |
| entering a new place | 0.5 s slide from the previous place's coordinates (e.g. the boy at 61.5 s) | instant, hidden by the cut |
| frame-check FAILs | 33 groups | 1 group: the stocky and short carriers are hidden behind the tank, f100-109 (real occlusion, not clipping) |

Tools that now guard this: `audit/anim_audit.py` (method per act, glides, pops, overlaps), `tools/frame_checks/check.mjs` (clipping, edge cuts, faces covered, feet), `tools/check_motion_quality.mjs` (library integrity: PASS, 198/198 refs, 2,688 sampled poses).

## 3. Shot by shot (times from the voice)

Status key: **R** = replaced or refined and inspected; **K** = kept, it was already right; **L** = limitation.

| Shot / time | Characters and method now | Defects found (v1) | Done | Remaining / limitation |
|---|---|---|---|---|
| **t_hook 0.0-3.4** lift and set-down | 4 GIs: `lift/A` hold, then `lift/B` set-down (**new moves**: knees give under the load, sway, foot shuffle; dip, lower, straighten) | Static `hold_up`. The tank slid 3.6 m over men standing still and floated ≈0.5 m above their hands. Lou and the stocky GI stood inside the hull outline, so the hull came down through them. | R: tank stays over them and rests on their hands (hold height 1.55); all four hold the long sides (footprint measured); the tank comes down with them | L: two GIs are hidden behind the hull for 10 frames, which is natural. Hands are the cast's round fists and do not wrap the hull. |
| **3.4** "suitcase" | Lou `lift/C` pat (**new**: hand on hip, two pats); the dent pops on the hull (set event) | Static `knock`, Lou slid 1.6 m into place | R: pats where he stands, on the word | — |
| **3.6-6** bicycles | farmer `bike/A`, boy `bike/B`, then `bike/C` | 16 m/s; static `flinch` / `point_out` on the bikes (the body pose changed while the bike drawing stayed) | R: realistic speed, a lazy pedal while rolling to a stop | L: no dismount; their shock is carried by the faces |
| **6.2-7.9** "a soldier winks ... very strong" | Lou `walk/B` (1.4 m/s) → `idle/A` → `cheer/A` | Planner walk, static `hands_hips`; the flex was cropped out of the close-up | R: fists beside the head (the close-up crops lower gestures) | — |
| **8.6-9.6** "made of rubber" | Lou `run/C` (4.2 m/s, he sprints) → `push/B` at the valve; air whistle and the barrel sags (set event) | Lou slid 4.3 m in 0.4 s | R | L: the push is mimed at chest height, the valve is on the deck |
| **t_camp 10.6-26.4** | Lou `write/A` → `walk/B` → `board/A` → `cheer/A`; GIs `sweep/A`, `push/A`, `walk/C`; bulldozer drives in | Static `write`, `push`, `point_out`; planner walk; a GI parked inside a tank | R | L: the bulldozer and its tracks are rigid (no tread scroll) |
| **t_road 26.4-34** | Sound operator `idle/A` → `button/A` (finger raised, proud poke) | Static `stand` / `finger_up` | R | — |
| **t_radio 34-38.7** | Operator `write/A` / `write/B` (fast) on "Morse" | Static `write`; a chair blocked his legs | R: the chair moved aside | L: the Morse key's own tap is a set animation, not hand-driven |
| **t_cafe 38.7-43** | Lou `whisper/A`; waitress `carry/A` (tray) → `walk/A` out; spy `sit/C`; sergeant `idle/B` (arms crossed, foot tap) | All static; the waitress used a planner walk; the spy sat on air | R: a stool under the spy | L: the tray and newspaper are mimed (library flat props are off in 3D) |
| **t_sergeant 43-46.6** | Sergeant `laugh/A` → `laugh/B` (points) → `laugh/C` (wheeze, bent double) | Static `hands_hips` / `point_out` between laughs | R | — |
| **t_river 46.7-52.7** | Lou `board/A` → `thumbs/A`; decoys inflate in a wave (set) | Static poses | R | — |
| **t_photo 52.7-55.7** | Interpreter `inspect/A` (loupe creep) → `button/A` ("sends every gun") | Static `lean_in` / `point_out` | R | — |
| **t_strike + crane 55.7-60.5** | Shells: fireball (hot core, fading shell), earth debris, smoke puffs, light flash; decoys thrown; sergeant on his boat `idle/B` → `turn/A` | Burst glow white-out; solid orange balls; no debris | R | L: about 2.8 s crane (bible: about 4 s) |
| **t_cross 60.5** | Sergeant `turn/A`, faces think → surprised → shocked | Static `flinch`; a 0.4 s slide across the crane on his place change | R | — |
| **t_bed 61.5-66.4** | Boy `idle/A` → `thumbs/A` at the window; the blanket lump breathes | Static `hands_hips`; slid into the room for 0.5 s | R | — |
| **t_attic 66.4-71.2** | Old Lou `idle/A` → `whisper/A` ("shh"); grandchild `inspect/B` → `lift/A`; the skin rises above her head | Static poses; the skin rose beside her, then covered her face | R | L: the skin hovers just above her hands (it is not gripped) |

**Continuity across cuts.** A character's first beat in a new place now starts in place on the cut. Moves continue across camera travels inside a take. Faces carry across cuts unless the beat changes them.

**Sync with the voice.** Beats are keyed to words in `words.json`; walks are timed to arrive before their beat (OVERLAP check: 0). Events are set-driven on the same frames: dent on "suitcase", deflate on "rubber", the inflation wave, the shells, the crossing, and the skin lift.

## 4. Micro-animation (A)

| Item | State |
|---|---|
| Idle breathing | **R**: on every act now (motion polish, 0.55 amplitude, 2.15 rad/s); the lift moves add their own load-bearing breath and sway |
| Blinks | **R**: auto blink on every act (per character seed, about every 2.9-4.2 s) |
| Eye direction | **L**: not supported by the renderer (gaze comes from the face drawing); characters face their target via view/direction |
| Head movement | **R**: head follow-through on body rotation plus each move's own head acting; 5-frame head pop on face changes |
| Expressions | **K**: 27 face beats on their words |
| Hands / fingers | **K / L**: round-fist hands by rule (CB, "never a 3D hand"); no fingers to animate |
| Weight shifts | **R**: lift moves (knee give, shuffle), idle sways, walks with planted feet |
| Clothing, straps, hair | **K / L**: cloth lag runs for long cloth (trench coat, apron); helmets, straps and short hair are rigid |
| Transitions | **R**: 6-frame move-to-move blend (kit change in `puppets.mjs` and `film.js`) |

## 5. Environment, VFX and cinematic (B-D)

| Item | Before | Now (rendered and inspected) | Limitation |
|---|---|---|---|
| Wind on trees and grass | kit default everywhere | **R**: per place (dawn 0.32, camp 0.5, night road 0.62 gusty, river 0.7) | hedge clumps are static (instanced); no flags in the story |
| Clouds | kit sky drifts | **K** | — |
| Water | reflective, rippled | **R**: moving ripple rings round the boat and pontoons (subtle) | no wakes behind the tanks; no reflections of objects |
| Smoke / fog / dust | — | **R**: cigarette smoke in the radio tent (bible P4); shell smoke puffs; dust only where it has a reason (dawn pollen, lamp-lit dust, attic sunbeam); fog per place | — |
| Light changes | shell flashes | **K / R**: flashes softened (no white-out); hooded lamp on the half-track; attic window light shaft (bible P9) | — |
| Objects reacting | dent, deflate, blanket breath, decoys thrown | **R**: tank lowered with its lifters; skin lifted into her hands | — |
| Explosions | solid orange balls, glow white-out | **R**: hot core inside a fading shell, earth thrown up and falling back, smoke rising, softer glow | stylised, not volumetric |
| Splashes | — | **R**: ripples | no splash particles (the crossing is silent in the story) |
| Volumetric light | — | **R**: attic shaft | no god rays elsewhere |
| Motion blur | none | **R**: only on fast camera travels (230 frames), weighted by measured speed, never across a cut (0.16 at 31 px/f, 0 on rests) | it is a post blend of neighbouring frames, not a true shutter |
| Depth of field | wides sharp, close-ups 0.35 | **K** (CB_RULES line 82) | — |
| Lens effects | vignette, bloom | **K**; no flares added (decorative) | — |
| Shadows / AO | cast shadows + flat contact disc | **R**: soft contact shadow under every character (kit) | no SSAO pass |
| Grain | none | **R**: luma grain σ 0.010 in the grade | — |

## 6. Not done, on purpose or because the pipeline cannot

- No dismount from the bicycles. The bike is a flat library prop, and a dismount would need a new 3D bike with hand and foot contacts.
- No gaze direction or finger animation (renderer and CB rule).
- No physics cloth or hair beyond the kit's cloth lag.
- No particles added for decoration: no sparks, embers or fireflies.
