# Guide utilisateur — produire une scène avec le pipeline Blender `rc`

Ce guide suit l'exemple réel du dépôt : la démo **cour de ferme** (`demos/farmyard/`).
Toutes les commandes se lancent depuis `.claude/skills/ricks-clips/`. Blender 5.2.2 doit être dans le `PATH` (ou désigné par `RICKCLIPS_BLENDER`).

## 1. Créer une production

```
demos/<nom>/
  pipeline.json                 {"place": "places/<lieu>/place.json", "tracks": "tracks.json", "cards": "build/cards", "render": {...}}
  places/<lieu>/place.json      le lieu (voir docs/REFERENCE_SCHEMAS.md)
  tracks.json                   le jeu des personnages
  jobs/201_render.sh            (facultatif) la tâche de rendu GPU sur pod
```
`build/` et `production/` sont créés par le pipeline. `build/` est régénérable et ignoré par git. `production/` contient les preuves et se commite.

## 2. Ajouter un asset à la bibliothèque

1. Créer `library/assets/<fournisseur>/<id>/asset.json`. Exemple Poly Haven (CC0) :
   ```json
   {"schema_version": 1, "id": "barrel_01", "name": "Barrel", "kind": "model", "category": "prop", "tier": "foreground",
    "source": {"provider": "polyhaven", "url": "https://polyhaven.com/a/Barrel_01"},
    "license": {"name": "CC0", "url": "https://polyhaven.com/license", "author": "Poly Haven"},
    "build": {"type": "polyhaven_model", "source_id": "Barrel_01", "res": "1k", "scale": 1.0}}
   ```
   Autres types de construction :
   - `script` : un modèle construit dans Blender par un script du dépôt ;
   - `file` : un fichier fourni ;
   - `polyhaven_maps` et `ambientcg_maps` : des jeux de textures ;
   - `maps` : des textures locales.
2. Vérifier et construire (le résultat va au cache, une seule fois) :
   ```
   python3 -c "import sys; sys.path.insert(0,'blender'); from rc import library; print(library.resolve('barrel_01'))"
   python3 -c "import sys; sys.path.insert(0,'blender'); from rc import library; library.report()"     # met à jour library/assets/LIBRARY.md
   ```
3. Options utiles dans `asset.json` :
   - `"lods_auto": [0.25, 0.06]` crée des LOD par Decimate. Ils s'appellent `<id>__lod1`, `<id>__lod2`.
   - `"variants"` : chaque instance éparpillée choisit une variante au hasard (graine fixe).

**Règles :**
- Licence obligatoire.
- Aucun asset d'arme ou militaire via l'Asset Hub.
- Aucune primitive (boîte, cylindre nu) comme objet principal : le gate de la phase 1 les compte.

## 3. Décrire le lieu (`place.json`)

Sections, dans l'ordre de construction :
1. `terrain` : taille, relief (`height`, `seed`), `flat` (zones plates sous les actions), `paths` (chemins creusés, qui écrivent l'attribut `path_mask` utilisé par le LookDev).
2. `assets` : objets uniques posés (`at`, `rot`). Ils sont posés sur le sol automatiquement. `"realize": true` rend les pièces d'un asset modifiables, par exemple la porte du cabanon.
3. `lines` : un asset répété le long d'une polyligne, par exemple des clôtures.
4. `scatter` : végétation par **biome** (`meadow`, `hedge`, `path_edge`, `muddy_yard`, `woodland_floor`) ou par asset.
   - On donne une zone : cercle, polygone ou bande.
   - `exclude` réserve les zones de jeu : pieds des personnages, trajets.
   - `lod` choisit le LOD loin de la caméra.
   - Une graine est obligatoire.
5. `shots` : un plan = des images et une caméra (fixe ou par clés). `join` vaut `cut` ou `dissolve:N` (N images de fondu).

Valider sans Blender : `python3 -m rc.place validate <place.json>` (lancé depuis `blender/`). Cela affiche `VALID` ou la liste des problèmes.

## 4. Les personnages

1. Écrire `tracks.json` :
   - la distribution (`cast` : marionnette `cast:<rôle>` et taille) ;
   - les actes (`acts` : image, position, vue, pose `m:<mouvement>`, visage `k:<expression>`).
2. Générer les dessins : `python3 tools/card_service.py demos/<nom>/tracks.json demos/<nom>/build`
   - Les dessins inchangés sont recopiés depuis le cache.
   - `index.json` contient les positions des mains.
3. Dans `place.json` :
   ```json
   "characters": {"cards": "../../build/cards", "who": ["farmer", "smith"], "self_lit": 0.55,
                  "props": [{"who": "smith", "asset": "wooden_axe", "hand": 1, "frames": [0, 199]}]}
   ```
   Les cartes suivent la caméra active du plan. Elles sont posées au sol par lancer de rayon et portent une ombre. Les accessoires 3D suivent la main.

## 5. Animation, interactions, tissu, effets

- `animation` : `hinge` (porte), `bob` (lanterne), `vehicle_drive` (bulldozer sur un trajet, à vitesse donnée), `path`, `orbit`, `spin`, `flicker`, `look_at`, `lift_set`.
- `physics` :
  - les trois niveaux : `drop`, `topple`, `roll` (simples) ; `crash`, `collapse`, `door_break`, `glass_shatter` (fracture et liaisons cassables) ; `deform` (enfoncement par clé de forme) ;
  - le déclenchement se fait **à l'image du contact**, calculée par la trajectoire du percuteur ;
  - tout est précalculé en clés, puis le monde physique est retiré.
- `cloth` : `line_cloth` (linge sur un fil) et `flag`, simulés puis convertis en clés de forme.
- `fx` : `dust_burst`, `smoke`, `fire`, `sparks`, `rain`, `haze`, `explosion_stylized`, `splash`.
  - `"frame": "@cart"` place l'effet sur l'image d'impact calculée par l'événement physique `cart` ; `"@crate_drop+8"` le place 8 images après.
  - Les effets de feu et d'explosion sont purement visuels et fictifs.

## 6. LookDev

```json
"light":   {"preset": "day", "key_dir": [0.55, -0.6, 0.58], "view_transform": "Khronos PBR Neutral", "exposure": 0.2, "white_balance": 7600,
            "grade": {"saturation": 1.05, "vignette": 0.22}},
"lookdev": {"rules": {"stone": {"preset": "stone"}, "roof": {"tex": "tex_clay_roof_tiles", "wear": 0.25},
                      "ground": {"layers": {"base": "meadow_tex", "over": "yard_tex", "mask": "path_mask"}}},
            "calibrate": {"reference": ["../../../../references/fortress/frames"], "frames": [60, 200, 380]}}
```
- **Préréglages** : stone, wood, painted_metal, rust, fabric, plaster, earth, grass_ground, straw, rubber, iron, glass, water.
  - Une règle peut en surcharger chaque clé : `color`, `tile`, `contrast`, `wear`, etc.
  - Une règle peut aussi utiliser `tint`, pour les plantes : elle garde la texture et teinte vers la palette.
- **Balance des blancs** (mesurée sur Blender 5.2.2) : une température **plus basse** donne un rendu **plus froid**.
- **Étalonnage** : il se fait dans le compositeur de Blender (API Blender 5 : `scene.compositing_node_group`), identique sur toutes les images.

## 7. Lancer le pipeline

```
python3 tools/rc_pipeline.py run demos/farmyard                          # phases 1 à 12 ; arrêt au premier échec
python3 tools/rc_pipeline.py run demos/farmyard --from 4 --to 9          # reprendre au milieu
python3 tools/rc_pipeline.py run demos/farmyard --from 11 --render fetched   # vérifier des images rendues sur le pod et déposées dans build/frames
python3 tools/rc_pipeline.py status demos/farmyard
```
Chaque phase écrit ses contrôles et ses preuves dans `production/PIPELINE_STATE.json`. Les vidéos, planches et rapports vont dans `production/`.

## 8. Rendu GPU sur RunPod (payant : autorisation explicite et plafond requis)

1. Commiter et pousser la branche : le pod clone la branche.
2. Créer le pod :
   ```
   .venv/bin/python scripts/runpod/pod.py create demos/farmyard --script blender_pod.sh --branch <branche> --gpu "NVIDIA GeForce RTX 4090" --max-hours 2
   ```
   La clé RunPod est un secret de l'environnement : elle n'est jamais écrite dans le dépôt ni dans les journaux.
3. Le pod vérifie Cycles GPU (échec explicite sans GPU). Il exécute ensuite `jobs/201_render.sh` :
   - les cartes ;
   - l'assemblage ;
   - le benchmark Cycles/EEVEE ;
   - le rendu par tranches avec `gpu_usage.csv` ;
   - l'encodage.
4. Suivre : `pod.py status <id>` ; la page `status.json` publiée par le pod.
5. Récupérer **puis** supprimer : `pod.py fetch <id>` vérifie le manifeste sha256, puis `pod.py delete <id>`. La suppression est refusée tant que la récupération n'est pas vérifiée.

Le gestionnaire de rendu fonctionne aussi en local :
```
python3 tools/render_manager.py render build/scene.blend build/frames --frames 0-449 --slice 30 --res 270x480 --samples 16
python3 tools/render_manager.py bench  build/scene.blend build/bench --frames 60,200,380 --res 540x960 --samples 64 [--gpu]
python3 tools/render_manager.py verify build/frames
```
Une tranche déjà rendue et vérifiée est sautée : relancer après une coupure reprend où on s'était arrêté.

## 9. Tests

```
python3 tools/tests/test_rc.py               # cache, bibliothèque, assemblage, déterminisme, GPU obligatoire, gates, physique, modules, schéma, son, cartes
.venv/bin/python tools/tests/test_pod_guard.py   # protection des pods (aucune suppression sans récupération vérifiée)
```

## 10. Dépannage

| Symptôme | Cause et remède |
|---|---|
| `GPU REQUIRED but Cycles sees no GPU` | Comportement voulu avec `--gpu`. Sur pod : voir `cycles_devices.txt`. En local sans GPU : enlever `--gpu`. |
| Une pièce traverse le sol | Gate de phase 6 (`ground_penetration`). Augmenter `substeps` de l'événement, remonter la boîte du percuteur (`striker.box`). |
| Petites pièces projetées très loin | Pièces d'un même asset qui s'interpénètrent. `collapse` les fusionne déjà en un seul corps ; pour un autre événement, fusionner l'asset (`physics.join`). |
| Un effet se déclenche trop tôt | Vérifier que `"@nom"` désigne bien un événement de `physics` (le rapport `fx_frames` donne l'image résolue). |
| Rendu différent selon l'ordre des images | Une animation non précalculée. Toute nouvelle recette doit poser des clés : le gate de phase 10 le détecte. |
