# Référence des schémas — pipeline `rc`

Ces trois fichiers décrivent une production :
- `place.json` (le lieu, schéma v3) ;
- `tracks.json` (le jeu des personnages) ;
- `asset.json` (un élément de la bibliothèque).

Le validateur exécutable est `blender/rc/place.py`. Le schéma JSON généré est `blender/rc/schema/place.schema.json` (`python3 -m rc.place schema`).
Exemple complet et testé : `demos/farmyard/places/farmyard/place.json`.

Conventions :
- unités en mètres ;
- angles en degrés ;
- images numérotées depuis `frames[0]` ;
- `[x, y]` dans le plan du sol, `z` vers le haut.

Toute section aléatoire exige une `seed` : une même graine donne le même résultat.

---

## 1. `place.json` (v3)

### En-tête
| Clé | Type | Rôle |
|---|---|---|
| `schema_version` | 3 | obligatoire (2 reste lisible) |
| `place_id` | texte | obligatoire |
| `root` | texte | dossier de base des chemins relatifs (défaut : dossier du fichier) |
| `frames` | `[a, b]` | images de la scène |
| `fps` | entier | 30 par défaut |
| `palette` | `{nom: "#hex"}` | palette validée du lieu |

### `terrain`
`{size [x, y], res, height, seed, material {name, color}, flat [{center, radius, blend}], paths [{points, width, feather}]}`
- `flat` aplanit le sol sous les actions, avec une transition de `blend` mètres.
- `paths` creuse les chemins et écrit l'attribut `path_mask` (0 à 1), utilisé par la règle LookDev `layers`.

### `assets`
`{asset, name, at [x, y, z], rot, scale, realize, on_ground}`
- `asset` : un id de la bibliothèque. `name` sert de préfixe aux objets : `name:objet`, par exemple `shed:shed_door`.
- `realize: true` crée des copies réelles et modifiables (portes, vitres) au lieu d'une instance.
- `on_ground` (vrai par défaut) ajoute la hauteur du terrain à `z`.

### `lines`
`{asset, name, points [[x, y], ...], spacing, seed}` : un asset répété le long d'une polyligne et posé sur le sol (clôtures, murets).

### `scatter`
`{biome | asset, name, zone, seed, density | count, scale [a, b], wind, exclude [zones], lod {camera [x, y], near}}`
- **Zone** :
  - `{"center": [x, y], "radius": r}` ;
  - `{"polygon": [[x, y], ...]}` ;
  - `{"from": [x, y], "to": [x, y], "width": w}`.
- **Biomes** (`rc/envbuild.py: BIOMES`, densité par m²) :
  - `meadow` : herbe et pissenlits ;
  - `hedge` : arbustes et orties ;
  - `path_edge` : herbe haute et orties ;
  - `muddy_yard` : herbe rare ;
  - `woodland_floor` : fougères et herbe.
- `lod` : au-delà de `near` mètres de la caméra, le LOD 1 de l'asset est utilisé (mesuré : 872 instances proches, 5 068 lointaines).

### `shots`
`{name, frames [a, b], camera {pos, aim, fov_v} | keys [{f, pos, aim, fov_v}], fstop, join}`
- Un plan reçoit une caméra et un marqueur de timeline. Les plans doivent couvrir `frames` sans trou (gate de phase 3).
- `join` : `"cut"` ou `"dissolve:N"` (fondu de N images avec le plan précédent, appliqué en post-production).

### `characters`
`{cards, who [...], self_lit, props [{who, asset, hand, scale, frames [a, b]}]}`
- `cards` est le dossier `cards/` produit par `tools/card_service.py`, relatif à `root`.
- `self_lit` (0 à 1) : la part de lumière propre de la carte.
- `props` : un asset 3D suit la main `hand` (0 ou 1) de la carte sur les images données.

### `animation` (`rc/animate.py`) — commun à toutes les recettes : `{type, target, frames [a, b]}`
| `type` | Paramètres |
|---|---|
| `hinge` | `open`, `close`, `angle` (95), `axis` ("Z"), `ease` (12). L'origine de l'objet doit être sur la charnière. |
| `bob` | `amp` (4°), `period` (2,4 s), `axis` ("X"), `phase` |
| `vehicle_drive` | `points`, `speed` (m/s), `start`, `stop`, `heading_offset`, `wheels` [noms], `wheel_radius`. Hauteur prise sur le terrain. |
| `path` | `points`, `speed`, `z`, `shake`, `start`, `heading_offset` |
| `orbit` | `center`, `radius`, `height`, `deg_per_s`, `start_deg` |
| `spin` | `rpm`, `axis` |
| `flicker` | `energy`, `amount` (0,35), `seed`, `rate` : pour une lampe (`target` = objet lumière) |
| `look_at` | `look` : nom de l'objet à regarder |
| `lift_set` | `at`, `rot`, `lift` [a, b], `set`, `dent`, `height` |

### `physics` (`rc/physics.py`) — commun : `{type, name, frames [a, b], seed}`

Toutes les interactions sont précalculées en clés. `name` sert aux références `"@name"` des effets. Le rapport donne `release` (image de déclenchement).

| Niveau | `type` | Paramètres |
|---|---|---|
| 2 | `drop` | `asset` ou `object`, `at`, `rot`, `height`, `tilt` [x, y], `release`, `bounce`, `colliders` |
| 2 | `topple` | `asset` ou `object`, `at`, `rot`, `at_frame`, `axis`, `tilt` |
| 2 | `roll` | `asset` ou `object`, `at`, `rot`, `direction` [x, y], `speed`, `push_from`, `release`, `radius` |
| 3 | `crash` | `target_asset`, `at`, `rot`, `striker {name, box [[min], [max]]}`, `fracture {préfixe: {pieces, seed}}`, `joint_strength`, `weak {préfixe: force}`, `own_group`, `substeps` (40) |
| 3 | `collapse` | `items [{asset, at, rot}]`, `striker` ou `at_frame`, `joint_strength`. Chaque item est fusionné en un seul corps. |
| 3 | `glass_shatter` | `pane`, `cuts`, `seed`, `strength`, puis `striker` (fissure progressive) **ou** `impulse {from, to, frames}` (pierre lancée : la vitre cède d'un coup) |
| 3 | `door_break` | `door`, `striker`, `hinge_strength` |
| 3 | `deform` | `object`, `point`, `direction`, `radius`, `depth`, `at_frame`, `ease`. Clé de forme : l'objet ne bouge pas. |

Le **percuteur** (`striker`) est une boîte cinématique qui suit l'objet nommé. Le déclenchement est l'image du premier contact de sa boîte avec la cible, calculée sur la trajectoire.

### `cloth`
`{type: "line_cloth" | "flag", name, at, size [l, h], rot, frames, wind, wind_dir, gust, mass, segments, seed, material {name, color}}`
Simulation Cloth convertie en clés de forme image par image.

### `fx` (`rc/vfx.py`) — commun : `{type, name, seed}`
`frame` peut être un nombre ou `"@<physics name>[+n]"`.

| `type` | Paramètres |
|---|---|
| `dust_burst` | `at`, `frame`, `count`, `radius`, `height`, `life` |
| `smoke` | `at`, `frame` ou `frames` [a, b] + `every` + `per_burst` (continu), `rise`, `size`, `density`, `life`, `color`, `drift`, `spread` |
| `fire` | `at`, `frames`, `every`, `life`, `rise`, `size`, `emission`, `light` (W, lumière vacillante) |
| `sparks` | `at`, `frame`, `count`, `emission` |
| `explosion_stylized` | `at`, `frame` : éclair, boule de feu, fumée, débris, onde au sol (visuel fictif) |
| `rain` | `area`, `count`, `height`, `speed` |
| `haze` | `center`, `size`, `density`, `color` |
| `splash` | `at`, `frame`, `count` |

### `light`
`{preset: day|morning|golden|night|interior, key_dir [x, y, z], view_transform, exposure, white_balance (K), grade {saturation, value, lift, gamma, gain, vignette}}`

Mesuré sur Blender 5.2.2 : une `white_balance` plus basse donne un rendu plus froid.

### `lookdev`
`{rules {matière: règle}, calibrate {reference [dossiers], frames [f...]}}`

Une règle prend l'une de ces formes :
- `{"preset": "stone", ...surcharges}` ;
- `{"tex": "<asset texture>", "tile", "contrast", "normal", "rough" [a, b], "wear", "color"}` ;
- `{"tint": "#hex", "amount"}` pour les plantes ;
- `{"layers": {"base": règle, "over": règle, "mask": "path_mask", "edge_noise"}}`.

Préréglages disponibles : `stone`, `wood`, `painted_metal`, `rust`, `fabric`, `plaster`, `earth`, `grass_ground`, `straw`, `rubber`, `iron`, `glass`, `water`.

---

## 2. `tracks.json` (service de cartes)

```json
{"title": "farmyard demo", "fps": 30, "end": 450,
 "cast": {"farmer": {"puppet": "cast:farmer", "height": 1.75}},
 "acts": [{"who": "farmer", "at": 0,  "pos": [-0.8, -2.6, 0], "view": "34",   "dir": -1, "pose": "m:idle/A", "face": "k:happy", "move_s": 0.01},
          {"who": "farmer", "at": 96, "pos": [-5.6, 6.9, 0],  "view": "side", "dir": -1, "pose": "m:walk/A", "face": "k:happy", "move_s": 1.5}]}
```
- `puppet` : un personnage de la distribution 2D (`cast:<rôle>`).
- `pose` : un mouvement de la bibliothèque (`m:<mouvement>/<variante>`).
- `face` : une expression (`k:<nom>`).
- `view` : `front`, `34`, `side` ou `back`. `dir` : 1 ou -1.
- `move_s` : durée du déplacement vers `pos`.

Sortie : `build/cards/<qui>/index.json` avec :
- `px`, `ground_px`, `metres_per_px`, `height_m` ;
- `runs` : pour chaque image, son dessin et les positions des mains (`hands`).

Les dessins `sNNNN.png` sont mis en cache par contenu.

---

## 3. `asset.json` (bibliothèque)

| Clé | Rôle |
|---|---|
| `schema_version`, `id`, `name`, `kind` (model \| textures), `category`, `tier` (hero, foreground, background) | identité |
| `description` | une phrase |
| `source {provider, url}`, `license {name, url, author, commercial_use}` | provenance et licence (obligatoires) |
| `build {type, ...}` | `script` (`script`, `output`), `file`, `polyhaven_model` (`source_id`, `res`, `scale`, `includes`), `polyhaven_maps`, `ambientcg_maps`, `maps` |
| `lods_auto` | ratios Decimate, par exemple `[0.25, 0.06]`, qui donnent les collections `<id>__lod1`, `<id>__lod2` |
| `variants` | objets alternatifs choisis par point d'éparpillement |
| `parts` | pièces détachables nommées (portes, vitres) |

Rapport généré : `library/assets/LIBRARY.md` (licence, dimensions, triangles par LOD, textures).

---

## 4. `pipeline.json` et `PIPELINE_STATE.json`

`pipeline.json` : `{place, tracks, cards, render {local {engine, res, samples}, gpu {...}}, reference_frames}`

`production/PIPELINE_STATE.json` donne, par phase :
`{name, status PASS|FAIL|NOT_RUN, checks [{check, pass, evidence}], evidence [fichiers], seconds, date}`.

## 5. `RENDER_MANIFEST.json` (`tools/render_manager.py`)

`{settings {engine, res, samples, gpu, blend_sha256}, frames {f: {sha256, seconds, cached}}, slices [{slice, device, devices, seconds, cached_frames}], gpu_usage {samples, max_util_pct, mean_util_pct, max_mem_mib}, summary}`
