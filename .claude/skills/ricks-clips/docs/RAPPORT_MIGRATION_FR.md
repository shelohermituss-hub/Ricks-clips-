# Rapport de migration — restructuration RicksClips (livrable 15)

Mission maîtresse `MISSION_MAITRESSE_RESTRUCTURATION_RICKSCLIPS.md`, 18/11. Décisions de CB :
- démo = **cour de ferme** ;
- plafond GPU de **3 $** ;
- Ghost Army **archivé sans suppression**.

Règle de ce rapport : **PASS uniquement avec preuve** (fichier, mesure ou test). Ce qui n'a pas été exécuté est marqué NOT_RUN, ce qui est incomplet est marqué PARTIEL.

## 1. Position dans le pipeline (règle CB 11g)

Démo `demos/farmyard` : **phases 1 à 11 PASS** (`demos/farmyard/production/PIPELINE_STATE.json`). **Phase 12 FAIL** : la vidéo est livrée avec image et son, mais elle n'atteint pas le standard forteresse (5 mesures sur 10). Voir section 4. Pipeline arrêté là sur décision de CB (19/11 : « ne le relance pas sur le GPU, utilise-le comme ça »).

## 2. Les 15 livrables

| # | Livrable | Statut | Preuve |
|---|---|---|---|
| 1 | Architecture documentée | **PASS** | `docs/ARCHITECTURE.md` (modules A à K, flux, 12 phases, règles) ; `CB_RULES.md` 11h |
| 2 | Pipeline Blender intégré | **PASS** | `tools/rc_pipeline.py` : 12 phases avec gates ; démo phases 1 à 10 PASS de bout en bout |
| 3 | Bibliothèque d'assets persistante | **PASS** | 50 assets valides (`library/assets/LIBRARY.md`), licences renseignées, LOD mesurés (arbre 1 072 212 → 268 053 / 64 332 triangles), résolution d'un asset inchangé = cache (0,11 s, test) |
| 4 | Constructeur d'environnements | **PASS** | `rc/envbuild.py` : relief 4,58 m, zones plates, chemins, clôtures, 5 biomes, LOD par distance (872 proches / 5 068 lointains). Phase 1 : 44 objets pour 7 923 instances, 0 primitive |
| 5 | Intégration des personnages | **PASS** | 438 et 435 dessins (cache par contenu), pieds à 0,0 cm du sol (gate ≤ 2 cm), ombre, accessoire 3D tenu en main ; évaluation 3D : `docs/CHARACTERS_3D_EVALUATION.md` (essai 3D NOT_RUN, demande l'accord de CB) |
| 6 | Animation et micro-animations | **PASS** | 9 recettes précalculées ; porte, lanterne, bulldozer clés (gate 5) ; linge simulé sur 450 images (gate 7) ; vent sur la végétation |
| 7 | Interactions et destruction | **PASS** | 6 événements dans la démo (vitre, chute, roulé, effondrement, enfoncement, choc). Gate 6 : vitesse libre maximale de 9,8 m/s, élévation au lâcher ≤ 0,94 m, enfoncement au sol 4,7 cm au plus (vérification par sommet) |
| 8 | VFX | **PASS** | 8 effets construits ; poussière et étincelles calées sur l'image d'impact calculée (213, 336, 377) ; feu dessin animé et explosion vérifiés à l'œil sur la planche de validation |
| 9 | LookDev | **PASS** | 326 matières sur 329 texturées (les 3 restantes sont émissives) ; luminance 0,2765 contre 0,2703 pour la référence forteresse (écart 2,3 %) ; étalonnage dans le compositeur (API Blender 5) |
| 10 | Gestionnaire de rendu GPU | **PASS** | 450/450 images rendues sur RTX 4090 OptiX (4,49 s par image), preuve GPU, benchmark Cycles/EEVEE, récupération vérifiée sans dérogation, pod supprimé, coût mesuré **1,06 $** (§4.1) |
| 11 | Caches persistants | **PASS** | `rc.cache` (stats, vérification, `gc --dry-run` qui ne fait que lister) ; cache d'images clé = entrées de construction (un .blend réenregistré n'est pas identique à l'octet près, mesuré) |
| 12 | Contrôle qualité | **PASS** | gates par phase, mesurées ; `test_rc.py` **27/27 PASS** ; `test_pod_guard.py` **13/13 PASS** ; indépendance de l'ordre des images : différence 0, octets identiques |
| 13 | Documentation technique complète | **PASS** | `docs/GUIDE_UTILISATEUR_FR.md`, `docs/REFERENCE_SCHEMAS.md`, `docs/ARCHITECTURE.md` ; `WORKFLOW.md`, `SKILL.md`, 15 agents mis à jour (ajouts, rien supprimé) |
| 14 | Vidéo prototype | **PARTIEL** | `production/farmyard_demo_gpu_540x960.mp4` (14,8 s, 540×960, image et son) livrée. Mais **rendue sans calibration** (plus sombre) et **standard forteresse non atteint** : 5/10 (§4.2). Aussi : `farmyard_demo_cpu_270x480.mp4` (calibrée, 6/10) |
| 15 | Rapport de migration | **PASS** | ce document |

## 3. Composants : conservé, modifié, remplacé, hérité

Rien n'a été supprimé du disque.

| Composant | Décision | Détail |
|---|---|---|
| `tools/film_plan.py`, voix, `words.json`, sous-titres | **conservé** | Toujours utilisés pour les films à narration. Le plan bake aussi la piste des cartes (service de cartes). |
| `templates/vector2d_characters/`, `puppets.mjs`, `motion_styles/` | **conservé** | Seul rôle restant de JavaScript : dessiner les personnages. |
| `templates/threejs_film/render_gpu.mjs`, `film.js` | **modifié** | Cache des cartes par contenu, `--who`, `--cards-only`, `--lock-dir`, positions des mains dans `index.json`. |
| `templates/threejs_film/sets`, kit three.js, `film.json.set` | **hérité** | Gelé, utilisable pour les anciens épisodes. Les décors sont désormais construits par `blender/rc/`. |
| `templates/blender_look/from_lock.build`, `lookdev_pod.sh` | **hérité** | Remplacés par les phases 1 à 9 et le pod `blender_pod.sh` ; `from_lock.card` reste utilisé. |
| `templates/blender_look/look.py` (préréglages de lumière) | **conservé** | Appelé par `rc.lookdev.light_rig`. |
| `templates/audio` (`sfx_gen`, `dsp`) | **conservé** | Réutilisé par `rc/sound.py`. |
| `tools/production_controller.py` | **conservé** | Les gates de scène sont réutilisées. Pour le pipeline `rc`, l'état vit dans `PIPELINE_STATE.json`. |
| `scripts/runpod/pod.py`, `manifest.py` | **modifié** | Protection des résultats (aucune suppression sans récupération vérifiée), `--expect`, heures fractionnaires du chien de garde. |
| `scripts/runpod/blender_pod.sh` | **modifié** | Lit `demos/*/jobs`, vérification Cycles GPU obligatoire, `gpu_usage.csv`, cache sur le volume. |
| `episodes/ghost-army` | **archivé** | `ARCHIVED.md`, `STATE.md` archivé ; rien supprimé (décision CB). |
| `blender/rc/` (19 modules), `tools/rc_pipeline.py`, `tools/render_manager.py`, `tools/card_service.py` | **nouveau** | Le pipeline restructuré. |

## 4. Rendu GPU (livrable 10) et vidéo prototype (livrable 14)

### 4.1 Session GPU n° 1 (pod `572kwozsr0osyn`, RTX 4090, 0,89 $/h)

| Point | Mesure |
|---|---|
| Preuve GPU | `cycles_devices.txt` : `OPTIX`, NVIDIA GeForce RTX 4090. `gpu_usage.csv` : 1 264 échantillons, pointe d'utilisation 100 %. |
| Premier benchmark | 47 s par image en moyenne, GPU utilisé à 3 %. **Pod arrêté** (pas supprimé) pour ne pas payer un rendu de 6 h. |
| Cause 1 | Les volumes non biaisés de Blender 5 analysent chaque volume procédural sur le CPU à chaque image : 22,7 s de préparation pour 0,05 s d'échantillonnage. Volumes biaisés : 1,7 s, image identique (écart moyen 0,4 à 0,6 sur 255). |
| Cause 2 | La moyenne du benchmark était trompeuse : 121 s pour la 1re image (compilation des noyaux OptiX), puis 4,5 s. Le benchmark donne désormais la médiane après échauffement. |
| Rendu | 450/450 images en 540×960 à 64 échantillons, **4,49 s par image**, 34 min, sha256 vérifiés. |
| Récupération | 494 fichiers récupérés et vérifiés, 0 échec. Deux fichiers vivants (`gpu_usage.csv`, `setup.log`) ne pouvaient jamais être vérifiés : ils sont désormais listés en copie figée (`_snap/`, tâche 202). **Suppression autorisée par la protection sans aucune dérogation.** |
| Coût réel (solde) | 4,724 $ → 3,669 $ = **1,06 $** |
| Défaut trouvé | Le pod a rendu **sans la calibration de la phase 9**, qui n'existait que dans le `.blend` local : luminance 0,37 contre 0,50 en local. Correctif : la calibration est écrite dans `places/<lieu>/calibration.json` et réappliquée à chaque assemblage (et incluse dans la clé de cache). Ces images non calibrées sont conservées dans `build/frames_gpu_uncalibrated/` et ne servent pas de livrable. |

### 4.2 Vidéo livrée et standard forteresse

**Décision de CB (19/11) :** pas de deuxième rendu GPU. La vidéo GPU est livrée telle quelle, et la correction est sauvegardée pour la suite.

| Mesure (`reference_compare.py`) | Vidéo GPU 540×960 (livrée, non calibrée) | Vidéo CPU 270×480 (calibrée) | Cible |
|---|---|---|---|
| edge_detail | 0,0636 FAIL | 0,0715 FAIL | ≥ 0,075 |
| luma_day | 0,37 PASS | 0,502 FAIL | 0,36 à 0,50 |
| crushed / burned | PASS / PASS | PASS / PASS | ≤ 0,01 / ≤ 0,015 |
| saturation | 0,536 FAIL | 0,51 PASS | 0,32 à 0,52 |
| saturation au-dessus du maximum | 0 s PASS | 0 s PASS | 0 s |
| images figées | 0,2 % PASS | 0,2 % PASS | ≤ 2 % |
| mouvement (médiane) | 14,7 FAIL | 17,5 FAIL | ≥ 18 |
| pics par 10 s | 4,73 FAIL | 6,08 PASS | ≥ 6 |
| coupes franches | 4 WARN, documentées comme voulues dans `production/DECISIONS.md` | idem | — |
| **Total** | **5/10 PASS** | **6/10 PASS** | 10/10 |

**Solution sauvegardée (non encore rendue) :**
- calibration persistée dans `places/farmyard/calibration.json` (exposition 0,991, 10 996 K), réappliquée à chaque assemblage. Vérifié : le `.blend` reconstruit porte exposition 0,991 et 10 996 K ;
- cible de luminance à 0,93 × la référence ;
- netteté dans le compositeur (`sharpen 0.2`) ;
- caméras des plans 2 et 3 plus mobiles.

Ces réglages visent les trois mesures en échec du rendu calibré (luminance, netteté, mouvement). **Leur effet n'est pas mesuré** (NOT_RUN) : il faut un nouveau rendu, par exemple le rendu local en 270×480 (environ 35 min, gratuit) ou un rendu GPU (environ 0,75 $).

## 5. Défauts trouvés et corrigés pendant la mission (avec mesure)

| Défaut | Mesure avant | Correctif | Mesure après |
|---|---|---|---|
| Éclats de vitre nés à l'origine du monde | centres à (0, 0, 0) | mise à jour du graphe de dépendances avant chaque découpe | éclats au niveau de la vitre, au sol, 0,5 à 3,6 m |
| Pierre lancée devenue dynamique | projetée à 47 m | cinématique, freinée après l'impact | tombe derrière la vitre |
| Loquets de caisses (pièces interpénétrées) | projetés à 33 m | pièces d'un asset fusionnées en un corps | vitesse maximale 5,6 m/s |
| Tonneau roulé | lancé à 6,8 m de haut | fusionné, couché, roulement sans glissement | puis 0,89 m (rayon écrit de 0,35 m alors que le rayon mesuré est de 0,378 m) → rayon mesuré prioritaire : **0,04 m** |
| Charrette enfoncée dans le sol | jusqu'à 26 cm | marge du sol, percuteur relevé, 40 sous-pas | 4,7 cm au plus |
| Feu et explosion | boules blanches surexposées | émission liée au champ de densité ; flammes modélisées façon dessin animé | lecture correcte sur la planche |
| Plan 4 : choc hors champ | choc à droite du cadre | caméra qui suit le bulldozer (5 clés calées sur sa trajectoire) | choc dans le cadre |
| Étalonnage | `scene.node_tree` absent en Blender 5 | `compositing_node_group` | test PASS |
| Cache d'images inopérant | .blend jamais identique à l'octet | clé = entrées de construction | — |
| Encodage | largeur 135 px refusée (yuv420p) | dimensions paires | animatique encodée |

**Deux gates ont été affinés après un échec, et ce rapport le dit :**
- **Distance de projection.** La charrette était *poussée* sur 12,1 m par le bulldozer. Pour les événements avec percuteur, le gate mesure désormais la vitesse libre maximale (< 15 m/s).
- **Élévation au lâcher (< 1,5 m).** Ce gate a été ajouté parce que le tonneau volant passait sous le seuil de vitesse.

## 6. Limites restantes (honnêtes)

- **Plan 3** : premier plan de boue peu détaillé, personnages absents du plan. À revoir avec CB.
- **Vidéo finale** : standard forteresse non atteint (§4.2) ; les corrections sont enregistrées mais pas encore rendues.
- **Phase 3** : l'animatique Workbench coûte 9 s par image en CPU logiciel. Cela tient au rendu OpenGL logiciel et aux 8 000 instances de la scène.
- **Personnages 3D riggés** : essai NOT_RUN, en attente de l'accord de CB.
- **Bibliothèque** : les assets du pipeline restent hors du dépôt (cache) et sont reconstruits à la demande depuis les sources CC0 ; un pod neuf les reconstruit donc.
