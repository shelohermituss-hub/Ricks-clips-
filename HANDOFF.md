# HANDOFF — reprise du projet RicksClips par une nouvelle session Claude Code

Rédigé le **19/11/2026** pour qu'une autre session, éventuellement sur un autre compte, reprenne le travail **sans l'historique de la conversation**.

Règle suivie dans ce document : une tâche n'est marquée faite que si elle a une preuve (commit, fichier, mesure ou test). Sinon elle est marquée **non faite**, **PARTIEL** ou **NOT_RUN**.

Documents liés, à la racine :
- `PROJECT_STATE.md` : état chiffré ;
- `ARCHITECTURE.md` : architecture actuelle et cible ;
- `DECISIONS.md` : décisions et justifications ;
- `MIGRATION_PLAN.md` : étapes restantes ;
- `OPEN_ISSUES.md` : problèmes connus ;
- `CHANGELOG.md` : historique.

Tous les chemins `S/...` désignent `.claude/skills/ricks-clips/...`, le dossier du skill qui contient tout le code.

---

## 0. Démarrage en 10 minutes (à faire dans cet ordre)

1. **Branche** : `git checkout ccr-00f60cb8-lenpig && git pull`. C'est la seule branche de travail.
2. **Lire** :
   - ce fichier ;
   - `S/START_HERE.md` (section « NEW VIDEO ») ;
   - `S/CB_RULES.md` §11h, les règles de CB, qui sont prioritaires ;
   - `S/docs/PREPRODUCTION_FR.md` ;
   - `S/memory/LESSONS.md`.
3. **Vérifier l'environnement** : `blender --version` (attendu : 5.2.2 LTS), `node --version` (attendu : 22), `ffmpeg -version`, `python3` avec numpy et PIL.
   - Si Blender manque : voir `S/INSTALL.md` et `S/CLOUD_MODE.md`.
4. **Secrets** : uniquement en *secrets réseau* de l'environnement, jamais dans le chat, les fichiers ou les journaux.
   - `SKETCHFAB_OAUTH_TOKEN`, pour retélécharger la F1 et la berline ;
   - `RUNPOD_API_KEY`, seulement si CB autorise un rendu GPU ;
   - la clé Fish Audio, pour la voix.
   - Les hôtes de chaque pod RunPod (`<pod>-8000.proxy.runpod.net`) doivent être ajoutés aux hôtes autorisés de l'environnement.
5. **Tests rapides** (aucun rendu lourd) :
   - `cd S && python3 tools/tests/test_plan_check.py` (attendu : PASS) ;
   - `python3 tools/tests/test_rc.py` (attendu : 27/27 PASS, environ 2 min) ;
   - `.venv/bin/python tools/tests/test_pod_guard.py` (attendu : 13/13 PASS), s'il y a un `.venv`.
6. **Fichiers absents d'une session neuve** (non versionnés, voir §10) :
   - la vidéo source de CB ;
   - les dossiers `build/` ;
   - le cache `~/.ricksclips/cache` ;
   - les modèles Sketchfab.

   Ils se régénèrent ou se retéléchargent, **sauf la vidéo source, qu'il faut redemander à CB.**

---

## 1. La mission en cours

**A. Mission maîtresse de restructuration** (`MISSION_MAITRESSE_RESTRUCTURATION_RICKSCLIPS`, CB, 18/11).
- Le fichier de mission lui-même **n'est pas dans le dépôt** : il a été fourni dans la conversation.
- Son contenu est repris dans `S/docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md` et `S/docs/RAPPORT_MIGRATION_FR.md`.
- Objet : passer d'un pipeline three.js (décors) + Blender (habillage) à un pipeline **Blender complet** (`S/blender/rc/`), avec bibliothèque d'assets, caches, physique, effets, LookDev, contrôle qualité, rendu GPU sur RunPod (plafond **3 $**), une démo « cour de ferme » et 15 livrables.
- Ghost Army est **archivé sans suppression**.
- **État** : 14 livrables PASS (n° 1 à 13 et 15), 1 PARTIEL (n° 14, vidéo prototype). Détail : `S/docs/RAPPORT_MIGRATION_FR.md` §2.

**B. Validation du pipeline sur une vraie vidéo (en cours depuis le 19/11).** CB a fourni **sa propre vidéo**, « He Crashed His Own Car For Science » (51,5 s, 15 plans). Consigne : **la reproduire entièrement**, même narration, mêmes plans, même style, tout recréé par nous.
- Analyse : `S/references/crashed_car/ANALYSE_FR.md`.
- Plans 1 et 2 construits ; plans 3 à 15 **non faits**.

**C. Méthode « nouvelle vidéo sans vidéo de référence »** (demande CB du 19/11).
- Plan de production complet avant de construire, vérifié par `plan_check.py`.
- Catalogue action → réaction → conséquence.
- Bible de style.
- Chaque problème devient une solution permanente.
- **Outils et documents faits** ; **pas encore utilisés sur une vraie nouvelle vidéo**.

---

## 2. Ce qui a été réellement effectué (avec preuve)

| Bloc | Fait | Preuve |
|---|---|---|
| Pipeline `rc` (Blender) | 17 modules Python + `schema/` dans `S/blender/rc/`, orchestrateur `S/tools/rc_pipeline.py` en 12 phases | `S/docs/ARCHITECTURE.md`, `test_rc.py` 27/27 PASS (19/11) |
| Démo cour de ferme | Phases 1 à 11 PASS ; phase 12 FAIL (standard forteresse : 5/10 en GPU, 6/10 en CPU) | `S/demos/farmyard/production/PIPELINE_STATE.json`, `farmyard_demo_gpu_540x960.mp4` |
| Rendu GPU RunPod | 1 session : 450 images, RTX 4090 OptiX, 4,49 s par image, coût **1,06 $**, 494 fichiers récupérés et vérifiés, pod supprimé | `S/docs/RAPPORT_MIGRATION_FR.md` §4.1, `~/.ricksclips/pods/572kwozsr0osyn.json` (local) |
| Analyse de la vidéo de CB | Fiche mesurée, 15 plans, bible du look, transcription (177 mots), mesures par seconde | `S/references/crashed_car/ANALYSE_FR.md`, `words.json`, `ref_measures.json` |
| Plan 1 (rue + crash) | Construit et rendu en 270×480 ; **accepté par CB tel quel** | `S/demos/crashed_car/shots/s01_driveway.py`, commit `c39a31c` |
| Plan 2 (stand + virage), v2 | Analyse détaillée, construction, contrôle de continuité PASS, rendu par couches (21 min 54 s en CPU, 270×480, 12 échantillons), comparaison côte à côte envoyée. CB : « c'est presque exactement ce que je voulais » | `S/references/crashed_car/shots/s02.md`, `shots/s02_pit.py`, `s02_corner.py`, commit `72e8b33` |
| Règles CB du 19/11 | Corriger seulement ce qui change (`--patch`), rendu par couches, analyse détaillée d'abord, tout passe par une action, caméra jamais à l'arrêt, vraies surfaces et ombres, contrôle automatique, plan complet avant construction, réaction et conséquence pour chaque action, chaque problème devient une solution permanente | `S/CB_RULES.md` §11h (fin du fichier) |
| Contrôle de continuité | `S/demos/crashed_car/shots/continuity.py` : apparition, téléportation, rétrécissement, saut de pose, arrêt caméra. Le rendu est refusé s'il échoue (`render_layers.sh`) | ancienne version du plan 2 : 7 apparitions, 2 téléportations, 1 arrêt ; nouvelle version : 0 |
| Repères des cartes | `S/tools/card_anchors.py` mesure la tête, les pieds, les mains et les sauts de pose. Lancé automatiquement par `card_service.py` | `anchors.json` à côté des dessins |
| Méthode sans référence | `S/tools/plan_check.py`, `S/templates/production_plan/` (modèle et exemple rempli), `S/library/reactions/reactions.json` (24 recettes), `S/references/STYLE_BIBLE_FR.md`, `S/docs/PREPRODUCTION_FR.md` | `test_plan_check.py` PASS (19/11) |

---

## 3. Ce qui n'a PAS encore été effectué

- **crashed_car, plans 3 à 15** : non faits. Aucune analyse détaillée `sNN.md` sauf `s02.md`, aucun script, aucun rendu.
- **crashed_car, plan 2** : 4 corrections demandées et 2 manques signalés par `plan_check`, **non faits** (liste dans `OPEN_ISSUES.md`).
- **crashed_car, son, voix, sous-titres, montage, rendu final GPU** : non faits. Le plafond GPU de cette vidéo n'est **pas fixé par CB**.
- **Plan 1 revérifié avec la dernière version du contrôle** (sauts de pose, repères des cartes) : **NOT_RUN**. Son rapport de continuité date d'avant ces ajouts.
- **Méthode sans référence** : utilisée sur aucune vraie nouvelle vidéo. Le plan 2 a seulement été réécrit comme exemple.
- **Intégration des outils du plan par plan dans `blender/rc/`** : non faite (§5 et `MIGRATION_PLAN.md`).
- **Démo ferme** : le nouveau rendu calibré qui mesurerait l'effet des corrections est **NOT_RUN** (décision CB : pas de second rendu GPU).
- **Personnages 3D riggés** : essai NOT_RUN, en attente de l'accord de CB.
- **Vidéos de référence supplémentaires** : CB a demandé s'il devait en envoyer d'autres, et la réponse a été oui, 3 à 5 vidéos variées. **Aucune reçue à ce jour.**

---

## 4. Architecture actuelle

Résumé ici ; le détail est dans `ARCHITECTURE.md`.
- Tout le code est dans `S/` (skill Claude Code).
- **Deux façons de construire, toutes deux en Blender `rc`** :
  1. **Orchestrateur générique** `tools/rc_pipeline.py` + `places/<lieu>/place.json` : utilisé pour la démo ferme.
  2. **Un script Blender par plan** (`demos/crashed_car/sets/*.py` + `shots/sNN_*.py`), qui appelle les modules `rc` : méthode retenue pour crashed_car, rapide et validée par CB.
- **Personnages** : cartes 2D dessinées par le code JavaScript (`templates/vector2d_characters`, `motion_styles`, `threejs_film/render_gpu.mjs --cards-only`), via `tools/card_service.py`. three.js ne sert plus qu'à dessiner les personnages ; ses décors sont gelés.
- **Rendu** : `tools/render_manager.py` (tranches, reprise, `--patch`, preuve GPU, benchmark) ; découpage en couches `demos/crashed_car/shots/layers.py` (SKY, SET, OBJECTS, FX).
- **GPU** : RunPod via `scripts/runpod/pod.py` + `blender_pod.sh`, avec la protection des résultats.

## 5. Architecture cible validée

Validée par CB le 19/11 : méthode du plan 2 jugée « presque exactement ce que je voulais » ; règles écrites dans `CB_RULES.md` §11h.

Script → voix → **plan complet (`plan.json`, `plan_check` PASS)** → assets téléchargés en une fois → **un script Blender par plan**, avec des décors construits pour le cadre et des cartes 2D → **`continuity.py` PASS** → environ 8 images clés vérifiées à l'œil → **rendu par couches** (CPU en basse définition pour valider, GPU RunPod pour le final) → corrections par `--patch` → son à −14 LUFS, sous-titres, montage.

**Non encore fait dans la cible** : déplacer les outils génériques qui vivent dans `demos/crashed_car/` vers `blender/rc/`, et brancher `plan_check` et `continuity` dans `rc_pipeline.py` (voir `MIGRATION_PLAN.md`).

## 6. Décisions techniques (résumé ; détail et justification dans `DECISIONS.md`)

- Blender 5.2.2 + Cycles. EEVEE mesuré à seulement environ 10 % plus rapide, pour une qualité moindre.
- Volumes biaisés : 22,7 s → 1,7 s de préparation.
- Personnages en cartes 2D. Un personnage = un dessin = une seule vue. Accessoires 3D posés sur la tête et les mains mesurées.
- Décors construits pour le cadre, rendu par couches, corrections par `--patch`.
- Textures réelles CC0 (Poly Haven). HDRI vu uniquement par les reflets. Soleil dur et ciel d'appoint bas.
- Caméra jamais à l'arrêt (`street.handheld`).
- Contrôles automatiques avant construction (`plan_check`) et avant rendu (`continuity`).
- GPU : plafond de 3 $ pour la mission, aucun pod sans accord explicite, aucune suppression sans récupération vérifiée.

## 7. Fichiers et modules importants

| Fichier | Rôle |
|---|---|
| `S/CB_RULES.md` (§11h à la fin) | Règles de CB : **prioritaires** |
| `S/START_HERE.md`, `S/docs/PREPRODUCTION_FR.md` | Point d'entrée, méthode pour une nouvelle vidéo |
| `S/references/STYLE_BIBLE_FR.md` | Style à suivre sans vidéo de référence |
| `S/templates/production_plan/PLAN_TEMPLATE_FR.md`, `plan_example.json` | Modèle de plan et exemple rempli (plan 2) |
| `S/tools/plan_check.py` | Barrière avant construction |
| `S/library/reactions/reactions.json` | Catalogue action → réactions, conséquences, micro-animations, sons |
| `S/demos/crashed_car/sets/street.py` | Aides de décor : `mat`, `pbr()`, `hdri_reflections()`, `handheld()`, `sky`, `box`… |
| `S/demos/crashed_car/sets/racetrack.py` | Décors du stand et du virage |
| `S/demos/crashed_car/shots/s01_driveway.py`, `s02_pit.py`, `s02_corner.py` | Plans 1 et 2 |
| `S/demos/crashed_car/shots/continuity.py` | Barrière avant rendu |
| `S/demos/crashed_car/shots/layers.py`, `render_layers.sh` | Découpe en couches et composition ; rendu bloqué si la continuité échoue |
| `S/demos/crashed_car/tracks_s01.json`, `tracks_s02.json` | Jeu des personnages (actions sur la ligne de temps) |
| `S/tools/card_service.py`, `S/tools/card_anchors.py` | Dessins des personnages, repères tête, pieds et mains |
| `S/tools/render_manager.py` | Rendu par tranches, `--patch`, preuve GPU |
| `S/blender/rc/*.py` | Modules : render, physics, vfx, lookdev, fetch (`polyhaven_hdri` ajouté), characters, qa… |
| `S/scripts/runpod/pod.py` | Contrôle de RunPod avec la protection des résultats |
| `S/memory/lessons_learned.json`, `LESSONS.md` | Leçons (PI-001 à PI-016) |
| `S/docs/RAPPORT_MIGRATION_FR.md` | Statut des 15 livrables de la mission maîtresse |

## 8. Problèmes connus

Voir `OPEN_ISSUES.md`. Les plus importants :
1. **La vidéo source de CB n'est pas dans le dépôt** (choix voulu). Une nouvelle session doit la redemander pour analyser les plans 3 à 15.
2. Plan 2 : casque trop gros, sol du stand et asphalte trop sombres, deux gestes de bras très rapides, pas de poussière à l'atterrissage, voiture retournée sans bosses ni fumée.
3. Plan 1 : non revérifié avec le contrôle à jour.
4. Petite dépense RunPod récurrente de **0,005 $/h alors qu'aucun pod n'existe** (stockage probable), non expliquée.
5. Outils génériques encore rangés dans `demos/crashed_car/`.

## 9. Tests exécutés (19/11, dans cette session) et résultats

| Test | Résultat |
|---|---|
| `python3 tools/tests/test_plan_check.py` | **PASS** : l'exemple passe ; un plan avec 5 erreurs injectées est refusé sur les 5 |
| `python3 tools/tests/test_rc.py` | **27/27 PASS** en 125 s. Il a d'abord planté au comptage, parce qu'un test renvoyait un dictionnaire ; corrigé en convertissant chaque résultat en booléen, puis relancé. Le test GPU a vérifié la branche « pas de GPU → échec explicite », car cette machine n'a pas de GPU. |
| `.venv/bin/python tools/tests/test_pod_guard.py` | **13/13 PASS** |
| `continuity.py` sur `s02_pit` et `s02_corner` | **PASS** : 0 pour tous les critères |
| `continuity.py` sur `s01` | **PASS**, mais avec la version d'avant l'ajout des sauts de pose. À relancer. |
| `plan_check.py` sur `plan_example.json` | **PASS** : 106 PASS, 5 WARN (manques réels, notés dans `OPEN_ISSUES.md`), 0 FAIL |

## 10. Ressources et assets

**Dans le dépôt :**
- code, règles, documents, mémoire ;
- analyse de la vidéo de CB (planches, transcription, mesures) ;
- catalogue d'assets `S/library/assets/catalog.json` (17 entrées) ;
- vidéos livrées de la démo ferme (`S/demos/farmyard/production/farmyard_demo_gpu_540x960.mp4`, `farmyard_demo_cpu_270x480.mp4`, `p3_animatic_workbench.mp4`).

**Hors dépôt, ignoré par Git, à régénérer :**

| Ressource | Où | Comment la récupérer |
|---|---|---|
| Vidéo source de CB et extractions (`frames/`, `hi/`, `shots/s02/`, `cuts.txt`, *.wav) | `S/references/crashed_car/` | **Redemander la vidéo à CB**, puis réextraire (§12) |
| Rendus et dessins (`build/`) | `S/demos/crashed_car/build` (1,2 Go), `S/demos/farmyard/build` (1,9 Go) | Se reconstruisent avec les scripts (dessins : `card_service.py`, environ 2,5 min par piste ; rendus : `render_layers.sh`) |
| Cache des téléchargements et des assets construits | `~/.ricksclips/cache` (2,0 Go) | Reconstruit automatiquement depuis Poly Haven et ambientCG (CC0) |
| Modèles Sketchfab (fichiers .zip et glTF) | `S/library/assets/sketchfab/` (197 Mo) | `tools/asset_hub.py download sketchfab <id>`, avec le jeton Sketchfab |

**Assets Sketchfab** : licences CC-BY à créditer. Le champ licence est vide dans `catalog.json` (voir `OPEN_ISSUES.md`).
- `ca91852b29bb435d8d0278d9131aa775` : Formula 1 Car Midpoly, LWDream ;
- `58c33766470d46e7b2aed542650494e5` : Generic Sedan Car, MMC Works ;
- `1795f6e907634afda88fdaf45f67b279` : Vintage Bicycle, VladNeko.

**Textures et HDRI Poly Haven (CC0) utilisés par le plan 2** :
- `concrete_floor_worn_001`, `concrete_wall_008`, `asphalt_track` ;
- `asphalt_pit_lane` (téléchargé, non utilisé) ;
- `kloofendal_48d_partly_cloudy_puresky` (HDRI).

**Assets de bibliothèque utilisés** : `old_tyre`, `metal_jerrycan`, `wine_barrel_01`, `island_tree_02`…

## 11. Git, RunPod, pods

**Git :**
- Branche unique de travail : **`ccr-00f60cb8-lenpig`**, locale et `origin`. Aucune autre branche.
- Dernier commit de travail avant cette passation : **`d07c50f`** (méthode nouvelle vidéo).
- Le commit de passation qui ajoute ces 7 fichiers est donné dans le rapport final et dans `CHANGELOG.md`.

**RunPod :**
- 1 pod au total, `572kwozsr0osyn` (RTX 4090, 0,89 $/h) : créé le 18/11 à 22:45 UTC, **supprimé le 19/11 à 00:13:27 UTC**, après récupération vérifiée de 494 fichiers (manifeste `7d4d9e90…`).
- **Aucune opération RunPod en cours.** Vérifié le 19/11 avec `pod.py balance` : `pods: []`, solde **3,58 $**.
- Dépense mesurée de la mission : 1,06 $. Depuis, une dépense de **0,005 $/h** sans pod (environ 0,09 $ cumulés) : **à vérifier dans la console RunPod** (volume réseau ?).

**Fichiers à récupérer avant toute suppression d'un pod** (pour tout pod futur) : tout ce que liste le `manifest.json` publié par le pod. `pod.py delete` refuse tant que ce n'est pas fait. Pour un rendu `blender_pod.sh`, au minimum :
- `cycles_devices.txt` (preuve GPU) ;
- `gpu_usage.csv` ;
- `jobs/<job>/frames/RENDER_MANIFEST.json` et **toutes les images** `f*.png` ;
- `jobs/<job>/bench/BENCH.json` ;
- la vidéo encodée du job ;
- `setup.log` et les copies figées `_snap/`.

Procédure : `pod.py fetch <id>` → `pod.py verify <id>` (code de sortie 0) → `pod.py delete <id>`. **Aucun pod n'existe aujourd'hui** : rien n'est à récupérer.

## 12. Prochaine action exacte

**Étape 1 — Restaurer et vérifier (sans rendu lourd)** : §0, étapes 1 à 5.

**Étape 2 — Demander à CB.** Il faut :
- (a) qu'il renvoie la vidéo `He_Crashed_His_Own_Car_For_Science` (à placer dans `S/references/crashed_car/source.mp4`, ignoré par Git) ;
- (b) qu'il choisisse : **corriger d'abord les 4 points du plan 2, ou passer au plan 3**. La dernière réponse proposait de passer au plan 3 et de grouper les corrections du plan 2 à la fin ; CB n'a pas encore répondu.

**Étape 3 — Plan 3** (« he vowed to make the race track safer for all », 8,27 → 11,4 s, images 248 à 342 ; bureau-garage, mur de liège, affiche « STOP CAR. GENTLY. », photos « MY BAD », la dernière image du plan 2 devient une photo épinglée) :

1. Extraire les images à 10 i/s :
   ```
   cd S/references/crashed_car && mkdir -p shots/s03
   ffmpeg -ss 8.27 -to 11.5 -i source.mp4 -vf fps=10 shots/s03/f%04d.jpg
   ```
   Puis faire les planches.
2. Écrire `S/references/crashed_car/shots/s03.md`, au format de `s02.md`, **avec** les sections « Entrées / sorties / changements d'état », caméra, surfaces et ombres.
3. Écrire `S/demos/crashed_car/plan/s03.json` au format de `plan_example.json`, puis `python3 tools/plan_check.py …` jusqu'à **PLAN PASS**.
4. Construire `S/demos/crashed_car/sets/office.py` et `shots/s03_office.py`, sur le modèle de `s02_pit.py`. Écrire la piste `tracks_s03.json`, puis lancer `card_service.py`.
5. Lancer `blender -b build/s03_office.blend --python shots/continuity.py -- build/continuity/s03.json` jusqu'à PASS. Faire environ 8 images clés et les comparer côte à côte avec la référence.
6. `bash S/demos/crashed_car/shots/render_layers.sh s03_office 248-342`. Rendu CPU 270×480 : prévoir 10 à 20 min. **Annoncer le temps mesuré.**
7. Commiter, pousser, envoyer la comparaison côte à côte à CB.
