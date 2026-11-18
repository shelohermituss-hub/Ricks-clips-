# Architecture RicksClips — pipeline Blender `rc` (livrable 1)

Version finale de la restructuration (mission maîtresse). Elle remplace la cible décrite en mission 0 (`docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md`) partout où le code a tranché.
Tout ce qui est écrit ici correspond à du code présent dans le dépôt et testé par `tools/tests/test_rc.py`.

## 1. Principes

1. **Une seule source pour le monde : Blender.** Décor, accessoires, physique, effets, lumière et rendu vivent dans une scène `.blend` construite par le paquet `blender/rc/`.
   - Le JavaScript (`templates/threejs_film/`) ne sert plus qu'à **dessiner les personnages 2D** (SVG → PNG), via le service de cartes.
   - L'ancien pipeline de décors three.js est **hérité** : il reste sur disque, mais aucun nouveau travail ne s'y fait.
2. **Tout état animé est précalculé** en images clés : animation, physique, tissu et effets. Le rendu d'une image ne dépend que de son numéro (déterminisme testé).
3. **Rien d'inchangé n'est recalculé.** Toute étape coûteuse passe par le cache par contenu `rc.cache` : assets, matières, téléchargements, cartes, images rendues.
4. **Instances partout où un objet se répète** : Geometry Nodes, instances par point avec variantes et vent.
5. **La palette est une donnée** : le LookDev reconstruit les matières à partir de la palette du lieu et calibre l'exposition sur la référence.
6. **Aucune phase n'est PASS sans preuve** : `tools/rc_pipeline.py` écrit chaque contrôle avec sa mesure et ses fichiers. NOT_RUN n'est jamais compté comme PASS.

## 2. Arborescence

```
demos/<nom>/  ou  episodes/<ep>/        données d'une production
  pipeline.json                         où sont le lieu, les pistes, les cartes ; réglages de rendu local et GPU
  places/<lieu>/place.json              le lieu (schéma v3) : terrain, assets, lignes, biomes, plans, animation, physique, tissu, effets, lookdev
  tracks.json                           pistes des personnages (jeu image par image) pour le service de cartes
  jobs/2NN_*.sh                         tâches exécutées sur le pod GPU
  build/                                produits régénérables (ignorés par git) : cartes, scène .blend, images
  production/                           PREUVES : PIPELINE_STATE.json, rapports, planches, vidéos de contrôle

blender/rc/                             le paquet Blender (Python dans Blender 5.2.2)
library/assets/<catégorie>/<id>/asset.json   la bibliothèque (métadonnées ; les fichiers lourds viennent du cache)
tools/rc_pipeline.py                    A. contrôleur de production : 12 phases, gates, état
tools/render_manager.py                 J. tranches, reprise, preuve GPU, benchmark, encodage, manifeste
tools/card_service.py                   E. pistes → dessins des personnages (cache par contenu)
scripts/runpod/                         pod GPU : pod.py (création, récupération vérifiée, suppression), blender_pod.sh (exécuteur de tâches)
```

## 3. Modules (A à K)

| | Module | Fichier | Rôle | Interface principale |
|---|---|---|---|---|
| A | Contrôleur de production | `tools/rc_pipeline.py` | Enchaîne les 12 phases, s'arrête au premier échec, écrit `production/PIPELINE_STATE.json` | `run <dossier> [--from N --to N --render local\|none\|fetched]`, `status <dossier>` |
| B | Bibliothèque d'assets | `rc/library.py`, `rc/bl_library.py`, `rc/fetch.py` | Catalogue `asset.json`, construction (script, fichier, Poly Haven, ambientCG), LOD automatiques, variantes, rapport `LIBRARY.md` | `library.resolve(id) -> (.blend, stats)` |
| — | Cache par contenu | `rc/cache.py` | Clé `sha256(type + entrées + code + version de Blender)` ; jamais de suppression automatique | `get_or_build(kind, inputs, build_fn)`, `python -m rc.cache stats\|verify\|gc --dry-run` |
| C | Constructeur d'environnement | `rc/envbuild.py`, `rc/geo.py` | Terrain (relief, zones plates, masque de chemin), lignes (clôtures), biomes d'éparpillement, choix du LOD selon la distance | appelé par `assemble` |
| D | Assemblage de scène | `rc/assemble.py`, `rc/place.py` | `place.json` (validé) → scène `.blend`, par phases | `build(place, out_blend, upto=1..9)` |
| E | Intégration des personnages | `rc/characters.py`, `tools/card_service.py`, `templates/blender_look/from_lock.py` | Cartes 2D en séquences d'images, collées au sol, ombre, accessoires 3D tenus en main | `place_cards(scene, lock, who, camera, ground=)` |
| F | Animation | `rc/animate.py` | Recettes précalculées : `lift_set`, `path`, `orbit`, `bob`, `hinge`, `flicker`, `look_at`, `vehicle_drive`, `spin`, tissu (Cloth → clés de forme) | `apply(scene, specs, fps, ground)` |
| G | Interactions et physique | `rc/physics.py` | 8 événements (`crash`, `drop`, `topple`, `roll`, `glass_shatter`, `door_break`, `collapse`, `deform`), déclenchement au contact, liaisons cassables, précalcul en clés puis suppression du monde physique | `run(scene, spec, src_fn, ground)` |
| H | Effets visuels | `rc/vfx.py` | Poussière, fumée, feu (lumière vacillante), étincelles balistiques, pluie, brume, explosion stylisée, éclaboussure ; images liées à un événement physique (`"@nom+n"`) | `apply(scene, specs, ground)` |
| I | LookDev | `rc/lookdev.py` | Préréglages de matières (usure par AO et pointiness), teinte des plantes, couches de terrain, rig de lumière, étalonnage dans le compositeur, calibration multi-images | `apply(rules)`, `light_rig`, `grade`, `calibrate_*` |
| J | Gestion du rendu | `rc/render.py`, `tools/render_manager.py` | Cycles, EEVEE et Workbench ; graine fixe ; GPU obligatoire sur demande ; cache d'images ; tranches et reprise ; `gpu_usage.csv` ; benchmark | `render`, `bench`, `encode`, `verify` |
| K | Contrôle qualité | `rc/qa.py` | Statistiques (objets, instances, primitives, triangles, matières texturées), contact des personnages, clés d'animation, **pénétration au sol par sommet** | `scene_stats`, `character_contact`, `animation_keys`, `ground_penetration` |
| — | Son | `rc/sound.py` | Piste stéréo 48 kHz construite depuis les événements de la scène (ambiance + bruitages calés sur les images calculées) | `python -m rc.sound place.json report.json out.wav` |

Ligne de commande Blender (une ligne `RC_RESULT <json>` par commande) :
`blender -b --factory-startup --python blender/rc/cli.py -- assemble|stats|render|calibrate|qa ...`

## 4. Flux de données

```
library/assets/*/asset.json ──resolve──▶ cache (asset_build, asset_blend, material_blend, download)
                                                      │
tracks.json ──card_service──▶ build/cards/<qui>/ (cache "cards")         │
                                     │                                   ▼
places/<lieu>/place.json ──validate──▶ assemble.build ──▶ build/scene.blend
   phase 1 terrain, assets, lignes, biomes (LOD)                         │
   phase 3 caméras par plan (marqueurs)                                  │
   phase 4 personnages (cartes, sol, accessoires)                        │
   phase 5 animation   6 physique   7 tissu   8 effets   9 LookDev       │
                                                                         ▼
                    qa (contact, clés, pénétration, stats) ──▶ production/scene_qa.json
                    calibrate (référence forteresse) ──▶ exposition, balance des blancs
                    render_manager (local ou pod GPU) ──▶ build/frames/f#####.png + RENDER_MANIFEST.json
                    rc.sound + ffmpeg (raccords) ──▶ production/<film>.mp4 ──▶ reference_compare
```

## 5. Les 12 phases et leurs gates (`tools/rc_pipeline.py`)

| # | Phase | Gate mesurée |
|---|---|---|
| 1 | Environment build | objets ≤ 3000 ; ratio d'instances ≥ 0,5 ; ratio de primitives ≤ 0,10 ; relief du terrain |
| 2 | Set dressing | chaque règle d'éparpillement a placé des points ; lignes posées ; ≥ 10 assets de la bibliothèque |
| 3 | Camera blocking | une caméra par plan ; plans contigus sans trou ; animatique Workbench rendu |
| 4 | Character integration | tous les personnages placés ; pieds à ≤ 2 cm du sol sur les images échantillonnées ; ombre portée |
| 5 | Animation blocking | chaque cible animée existe et porte des clés |
| 6 | Interaction system | pièces déplacées après le déclenchement ; aucune projection > 12 m ; vertex enfoncé de plus de 5 cm : aucun |
| 7 | Animation polish | tissu précalculé sur toutes les images ; vent sur la végétation |
| 8 | VFX | chaque effet construit ; effets liés à un événement calés sur l'image d'impact calculée |
| 9 | LookDev | ≥ 85 % de matières texturées ; luminance calibrée à ±10 % de la référence |
| 10 | Validation finale | images début, milieu, fin de chaque plan ; indépendance de l'ordre (image seule = image dans un lot, ≤ 1/255) |
| 11 | Render | toutes les images rendues et vérifiées par sha256 ; périphérique enregistré par tranche ; secondes par image |
| 12 | Post-production | vidéo avec image et son ; comparaison au standard forteresse (`reference_compare.py`) |

## 6. Règles de sécurité conservées

- **Pods** : `pod.py` refuse de supprimer un pod tant que les sorties attendues n'ont pas été récupérées et vérifiées (manifeste sha256). Le chien de garde **arrête** le pod (volume conservé) au lieu de le supprimer.
- **GPU** : `--gpu` rend le GPU obligatoire ; sans périphérique OPTIX/CUDA, la commande échoue au lieu de rendre en CPU en silence. Preuve : `cycles_devices.txt` et `gpu_usage.csv`.
- **Secrets** : aucune clé dans le dépôt ni dans les journaux ; les clés passent par les secrets réseau de l'environnement.
- **Licences** : chaque `asset.json` porte source, licence et auteur. Les assets Poly Haven et ambientCG sont CC0.

## 7. Ce qui n'est plus utilisé (hérité, conservé sur disque)

- Décors three.js (`templates/threejs_film/kit*`, `set` des `film.json`) et le LookDev three.js (`lookdev_pod.sh`). Ils restent utilisables pour les épisodes anciens, mais ne reçoivent plus d'évolution.
- `templates/blender_look/` : seule la fonction `from_lock.card` (chargement des cartes) est encore appelée par `rc/characters.py`.

Le détail de chaque composant (conservé, modifié, remplacé ou retiré) est dans `docs/RAPPORT_MIGRATION_FR.md`.
