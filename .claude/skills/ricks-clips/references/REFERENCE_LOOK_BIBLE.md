# REFERENCE LOOK BIBLE — the official RicksClips quality standard (v2.0, 2026-11-18)

**Status: OFFICIAL.** Source: the user's **fortress reference video** (Chinese fortress, the 82-rocket cart, an army in the fields, a rain night, a fire finale).
- Video: 66.9 s, 1080×1920, 30 fps, H.264 + AAC; sha256 `e2bac85c10d6…`
- Local copy, not committed: `references/video/fortress_reference/fortress_reference.mp4`
- Permanent captures in `references/fortress/`:
  - `frames/`: 26 representative frames, full resolution, numbered with their time
  - `overview_1fps.jpg`: the whole film, one frame per second
  - `motion_strips_*.jpg`: continuous strips around transitions and actions
  - `reference_measures.json`: per-second measurements
  - `compare_ghost_army_2026-11-18.jpg`: first comparison
- Machine-readable targets: `production/config/reference_standard.json`, used by `tools/production_controller.py compare-reference` and gate F.

v1.0 of this file was PROVISIONAL (built from `references/look_locked/`). It stays in Git history. The look_locked stills remain approved references for night-camp moods.

The reference sets a **level of finish and of life**, not a décor to copy. Characters stay the approved 2D vector cast. In the reference itself they are the same kind of card puppets as ours, which proves the gap is in the world, the camera, the effects and the finish, not in the character style.

---
## 1. What the reference does (observed frame by frame and measured)

### 1.1 Environments and geometry
- **Architecture is built, not suggested.**
  - Fortress walls are individual stone blocks with bevelled edges, recessed mortar and per-block colour variation.
  - Crenellations, towers with conical red roofs, an arched gate with voussoir stones and a studded wooden door.
  - Pagoda gatehouses with layered eaves, brackets, red columns and railings.
  - Banners carry embroidered emblems (tiger, chevron) and fringes.
- **Props are real models at hero quality.**
  - **The 82-hole rocket box:** board grain, 82 drilled holes with lit rims, brass end caps.
  - **Each rocket:** a bamboo shaft with node rings, string bindings and a paper tube with printed marks.
  - **The cart:** spoked wheels and a wooden frame with joints.
  - **The grinding wheel:** a stone disc on a wooden stand with a water trough.
  - **Also:** a hand drill on a hose, lanterns with glowing paper, coiled ropes, ladders, quilted cloth.
- **Terrain at three scales.**
  - **Near:** dense, long, individually lit grass blades that cover the ground up to the lens.
  - **Middle:** dirt paths with pebbles, stone paving with joints and wear.
  - **Far:** a terraced patchwork of fields in several tints, a river, tree clusters, rolling hills and rocky peaks.
- **Crowds are real:** hundreds of instanced soldiers with varied faces, helmets, shields and banners, filling the frame to the horizon.

### 1.2 Materials, textures, imperfections
- **No flat-coloured surfaces at camera distance.** Stone, wood, cloth, metal and paving each carry a texture and a normal or bump relief.
- **Wear and variation:** stone tint varies block by block, wood shows its grain, metal helmets carry highlights and rivets, cloth shows quilting, and chainmail has a real mail pattern on the cards.
- **PBR response:** metal reflects the sky, lantern paper glows, and wet stone at night shines under the rain.

### 1.3 Light, shadows, atmosphere
- One clear **sun or moon key** with soft shadows, plus **ambient occlusion** in corners, under props and at the feet.
- **Practical lights:** lanterns, the lit gate tunnel, the rocket fire.
- **Aerial perspective:** far hills fade into blue haze, and clouds are volumetric with lit tops.
- **Time of day as drama:** day, then a **rain night** (blue, readable, rain streaks, lantern pools), then a **sunset** (warm rim, lens bloom), then a bright day for the finale.
- **Measured over the whole film:**
  - mean luma 0.43;
  - saturation 0.40 (rich but not candy);
  - crushed blacks 0.07 %, burned highlights 0.55 %;
  - contrast (luma std) 0.18.

### 1.4 Character animation and interaction
- **Actions are performed with objects:**
  - a character **carries** the board and places it on the cart;
  - a **drill** turns in the hand while sawdust falls;
  - a coat is **thrown** and flies in an arc onto the cart;
  - a **slap** sends a helmet spinning away on a real arc while debris flies;
  - characters **react** in groups (heads turn, mouths open).
- **Every action has a consequence that stays:** holes stay drilled, the coat stays on the cart, the rockets stay in their holes, smoke lingers.

### 1.5 Camera and composition
- **The camera never rests:** median frame-to-frame change 35.8 (×1000) and **0 % still frames**.
- **No hard cuts (0 detected).** Shots join through:
  - **push-throughs:** a fast dolly through a face or object into the next subject, with motion blur;
  - **short dissolves** of 3-6 frames;
  - **follow moves:** the camera tracks a thrown object.
- **About 10.5 transition or fast-move peaks per 10 s** (8-frame luma change > 0.08), so a new picture idea roughly every second.
- **Composition:**
  - extreme close-ups on the hero object (holes, a rocket tip, the fuse);
  - low hero angles;
  - wide establishing aerials;
  - foreground grass or props framing almost every shot;
  - the subject large in frame.

### 1.6 VFX and consequences
- **Fuse:** a glowing spark travels along it, throwing sparks.
- **Launch:** the rockets burst out radially, each with a motion streak and a smoke trail; arrows streak across the sky as a mass of lines.
- **Impact:**
  - a brief flash, then a layered fire and smoke envelope that grows, then a mushroom cloud with a hot core;
  - dust and debris fly;
  - the light reaches the surroundings.
- **Hit reactions:** a red impact ring, a puff of debris, a helmet ballistic arc.
- **Weather:** rain streaks, wet sheen, wind in the grass, a dust trail behind the marching army.
- All effects are stylised cinema: readable at phone size, built, peaking, then settling.

### 1.7 Post-processing and cinematic finish
- **Bloom** on lights, sparks and fire.
- **Mild depth of field** on close-ups only.
- **Motion blur** on fast camera moves and flying objects.
- **Sun glare and lens bloom** at sunset.
- **Captions:** a white bold word with a black outline, lower third.
- Consistent saturation and contrast across the shots: one coherent grade per time of day.

### 1.8 Consistency between shots
- One palette per place and time of day.
- Recurring landmarks (banners, the red-roofed tower, the gate) anchor the geography.
- Lighting direction stays consistent inside a sequence.

### 1.9 Defects inside the reference — NOT to copy
- A large out-of-focus foreground object occludes the frame at 26 s (a green blob after the slap).
- The rain-night shot clips a character into the cart frame (around 31-35 s).
- Some dissolves cross two busy frames and read muddy for 2-3 frames.

---
## 2. Minimum standards (a film below these does not reach "reference quality")

| Area | Standard | Measured by |
|---|---|---|
| Hero objects | modelled parts, wear, lettering; ≥ 20 parts, ≥ 12 k tris, ≤ 60 % bare primitives; close-up inspection | `render_gpu.mjs --inventory`, gate B |
| Environment depth | foreground (grass or props at the lens), middle (action), background (layered terrain, haze, sky) in the FRAME | ENV_SCORES depth ≥ 3 with an image; reviewer |
| Surfaces | no flat colour at camera distance; texture plus relief on stone, wood, metal, cloth, ground | inventory textured share ≥ 85 % per place; reviewer |
| Ground cover | dense grass or texture up to the lens in exteriors | reviewer; no flat ground plane in the lower third |
| Image detail | edge density ≥ 0.075 (reference 0.095; neighbour-pixel luma difference at 90×160) | `compare-reference` |
| Exposure | mean luma 0.36-0.50 day, ≥ 0.25 night; crushed ≤ 1 %; burned ≤ 1.5 % | `compare-reference` per second |
| Saturation | 0.32-0.52 overall (reference 0.40); never above 0.60 for a whole shot | `compare-reference` |
| Camera life | still frames ≤ 2 %; median motion ≥ 18 (×1000) | `compare-reference` |
| Transitions | no unmotivated hard cut. Push-through, follow move, or a dissolve of 3-6 frames; a hard cut only for a deliberate shock | film.json takes; `compare-reference` reports cuts |
| Rhythm | a new picture idea every 1-2 s (transition or fast-move peaks ≥ 6 per 10 s) | `compare-reference` |
| Action contract | every important action: anticipation → motion → contact → effect → reaction → persistent aftermath → sound; a continuous strip as evidence | ACTION_EFFECT_MATRIX, gate E |
| VFX | layered (flash, fire envelope, smoke that evolves, debris, light on the set), never a static disc; sparks and trails on launches | strips; gate E |
| Post | bloom on emissives; motion blur only on fast camera and object moves (never on characters); DoF only on close-ups; one coherent grade per light | grade_log; reviewer |

## 3. Rules by department
- **Set-builder / background:** stone walls as blocks or relief with per-block tint; architecture with secondary parts (eaves, brackets, railings, voussoirs, studs); terrain in three scales; dense near grass; a far landscape with field patchwork and haze; recurring landmarks.
- **Props-hero / 3d-designer:** every named object is a real model (Asset Hub first, or a custom Blender model); lettering and wear; close-up proof before use.
- **Lighting:** key plus AO plus practicals; rain or night readable (≥ 0.25 luma); sunsets with rim and glare; haze on far planes.
- **Animator:** objects carried, thrown, turned and placed by the hands; group reactions; consequences persist.
- **Camera:** always moving; push-throughs and follow moves instead of cuts; extreme close-ups of the hero object; foreground framing.
- **VFX:** spark travel, radial bursts with trails, mass streaks, layered explosions; hit rings and debris; weather.
- **Editor / grade:** dissolves of 3-6 frames; bloom; selective motion blur; the saturation and exposure targets above.

## 4. Regressions (a defect that brings a film back below the reference)
1. A hero or recognisable object built as a primitive assembly or a flat card in the final.
2. A flat-coloured ground, wall or prop surface at camera distance.
3. An exterior with no near ground cover, or no far landscape or haze.
4. A held, frozen camera (more than 2 % still frames) or an unmotivated hard cut.
5. An action without visible contact, consequence or aftermath; an object that pops into place.
6. An effect that is a static disc or sphere, a white-out, or that disappears without settling.
7. Crushed blacks above 1 %, or saturation above 0.60 for a whole shot.
8. Clipping of a character into geometry, or a blurry foreground object hiding the subject (see 1.9).
9. Any defect listed in `memory/LESSONS.md` coming back.
