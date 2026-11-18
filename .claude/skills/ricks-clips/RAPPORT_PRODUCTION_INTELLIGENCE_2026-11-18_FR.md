# Rapport d'intégration — RicksClips Production Intelligence v1.0 (2026-11-18)

Sauvegarde avant intégration : tag Git local `backup/pre-production-intelligence-v1` sur le commit `91841af`. L'intégration est poussée sur la branche `ccr-00f60cb8-lenpig`. Aucune image ou référence approuvée n'a été modifiée. `CB_RULES.md` a été sauvegardé dans `references/reports/_backup_CB_RULES_2026-11-18_before_11g.md`.

## 1. Inventaire des points d'intégration (ce qui exécute réellement les règles)

| Exigence du paquet | Point d'entrée réel modifié ou créé |
|---|---|
| Contrôleur / showrunner | `tools/production_controller.py` (init, gates, review, issue, lessons, lesson-add, lesson-promote) ; nouvel agent `agents/production-controller.md` |
| Règles lues par tous les agents | `CB_RULES.md` §11g. `tools/slice_rules.py` la copie dans les 18 tranches `rules/dept/*.md` (vérifié : 18/18) |
| Points d'entrée du skill | `START_HERE.md` (phase 0, gates, revue), en-tête de `SKILL.md`, `WORKFLOW.md`, `library/INDEX.md` |
| Agents spécialisés | bloc « Production Intelligence (CB_RULES 11g) » avec les devoirs propres à chacun des 16 agents, plus 1 nouvel agent, recopiés dans `.claude/agents/` par `tools/sync_project_agents.py` (vérifié : rien d'obsolète) |
| Démarrage de session | nouveau hook SessionStart `scripts/production_memory_brief.sh` dans `.claude/settings.json` (testé : il affiche les leçons et l'état des gates de l'épisode) |
| Mémoire globale | `memory/lessons_learned.json`, `memory/LESSONS.md` (généré), `memory/asset_registry.json`, schémas dans `production/schemas/` |
| Mémoire d'épisode | `episodes/<film>/production/` : BRIEF, DECISIONS, OPEN_ISSUES, STATE, ASSET_REGISTER, ACTION_EFFECT_MATRIX, QA_LOG, ENV_SCORES, GATES, REVIEW |
| Portes A-G | `production/config/quality_gates.json` → `production_controller.py gates`, statuts PASS/WARN/FAIL/NOT_RUN, et NOT_RUN ≠ PASS |
| Référence artistique | `references/REFERENCE_LOOK_BIBLE.md` (PROVISOIRE) et `references/REFERENCE_SHEET_look_locked.jpg` |
| Détection des primitives et placeholders héros | nouveau hook du renderer : `render_gpu.mjs --inventory` (`window.sceneInventory` dans `film.js`). Il mesure, par objet réel : pièces, triangles, part de générateurs primitifs, matériaux texturés |
| Matrice action → effet | `production/config/action_effect_matrix.json` (modèles) et `production/ACTION_EFFECT_MATRIX.json` de l'épisode, avec preuves de rendu |
| Contrôle d'animation | `tools/anim_audit.py` (poses statiques, marches planner, glissements, chevauchements) ; correction du kit `film_plan.py` (entrée dans un lieu) |
| Sécurité des modules de décor | `tools/lint_set_modules.py` |
| Revue et autocorrection | `production_controller.py review` (planche plus extraits continus), `issue` (QA horodaté avec cause racine), dérogations écrites |
| Grade réel | le `grade.py` de l'épisode écrit `grade/grade_log.json`, vérifié par la gate G |
| Tests de non-régression | `tools/tests/test_production_intelligence.py` (10 tests tirés de défauts réels de Ghost Army) |

## 2. Diff (121 fichiers, voir `git show` du commit)
- **Nouveaux outils :**
  - `tools/production_controller.py`, `anim_audit.py`, `lint_set_modules.py`, `sync_project_agents.py`
  - `tools/tests/test_production_intelligence.py` et `tools/tests/fixtures/swallowed_comment.js`
- **Kit :**
  - `templates/threejs_film/film.js` : `window.sceneInventory`
  - `templates/threejs_film/render_gpu.mjs` : `--inventory`
  - `tools/film_plan.py` : entrée dans un lieu, atterrissage sur la même image que le changement de lieu
- **Règles et points d'entrée :** `CB_RULES.md` et son miroir `rules/CB_RULES.md` (§11g), les 18 tranches `rules/dept`, `START_HERE.md`, `SKILL.md`, `WORKFLOW.md`, `library/INDEX.md`, `CHANGELOG.md`
- **Agents :** 16 modifiés et 1 nouveau, dans `agents/` et `.claude/agents/`
- **Hook :** `.claude/settings.json` et `scripts/production_memory_brief.sh`
- **Paquet intégré :**
  - `production/` (config, schemas, spec_fr inchangée, templates, README, evidence)
  - `memory/`
  - `references/REFERENCE_LOOK_BIBLE.md`
- **Épisodes :**
  - mémoire complète `episodes/ghost-army/production/` ; `grade/grade.py` écrit son journal
  - épisode test `episodes/_pi_test/` : liens vers Ghost Army, avec l'asset externe

## 3. Commandes réellement exécutées (extraits)
```
git tag -f backup/pre-production-intelligence-v1 HEAD
unzip RicksClips_Production_Intelligence_Upgrade_v1.0.zip (17 fichiers lus intégralement)
blender -b --python bike2glb.py -- scene.gltf vintage_bicycle_1k.glb     # Sketchfab CC-BY, 49 483 tris, textures 4k->1k, 3,7 Mo
node templates/threejs_film/render_gpu.mjs episodes/_pi_test/film.json --frames 104 ...   # "asset: field vintage_bicycle applied"
node templates/threejs_film/render_gpu.mjs episodes/ghost-army/film.json --inventory     # 536 objets mesurés en 9,7 s
.venv/bin/python tools/production_controller.py init episodes/ghost-army
.venv/bin/python tools/production_controller.py review episodes/ghost-army <stills> --clip ...
.venv/bin/python tools/production_controller.py lesson-add/lesson-promote PI-001..PI-006
.venv/bin/python tools/slice_rules.py ; tools/sync_project_agents.py [--check]
node tools/frame_checks/check.mjs episodes/ghost-army/film.json
.venv/bin/python tools/production_controller.py gates episodes/ghost-army --phase preview|final
.venv/bin/python tools/tests/test_production_intelligence.py
node tools/check_motion_quality.mjs ; tools/test_asset_hub.py ; tools/test_asset_loader.mjs ; tools/test_look3d_api.mjs ; tools/test_motion_polish.mjs
```

## 4. Résultats des tests
| Test | Statut | Preuve |
|---|---|---|
| Suite Production Intelligence (10 tests) | **PASS 10/10** | voir la sortie ; le test PI-003 a d'abord **échoué** et a révélé un vrai pop d'une image dans le kit, corrigé puis revalidé |
| PI-002 lint : 3 bugs historiques détectés, 0 faux positif | PASS | fixture plus historique Git (commits 63d3a57, 6759b96) |
| PI-001 anim_audit : le film v1 échoue (37 poses statiques), le film actuel passe | PASS | `production/anim_audit.json` |
| Test de chargement d'un asset externe autorisé | PASS | `production/evidence/pi_test_external_asset_bicycle_f00104.png` (vélo Sketchfab CC-BY, texturé, ombres) |
| Plan test : asset détaillé, animation, effet, interaction | PASS | `production/evidence/pi_test_shot_clip_f72-129.jpg` (char posé sur ses porteurs, tape « comme une valise », bosse, vélo stable pendant le mouvement de caméra) |
| Motion QA de la bibliothèque (198 références, 2 688 poses) | PASS | |
| Asset Hub / asset loader / look3d / motion polish (tests existants) | PASS | non-régression du kit |
| Compilation Python et JS des fichiers modifiés | PASS | |
| Miroir des agents | PASS | `--check` : rien d'obsolète |
| Hook SessionStart (exécution manuelle) | PASS | affiche 4 leçons validées et l'état des gates |
| Gates Ghost Army, phase preview | PASS 18 · WARN 9 · FAIL 0 · NOT_RUN 6 | `episodes/ghost-army/production/GATES.md` |
| Gates Ghost Army, phase final | **FAIL 5** (attendu et honnête) | char héros en assemblage de primitives ; 5 lieux en géométrie < 3 ; 7/9 actions sans preuve de rendu ; grade pas encore exécuté |
| Hook SessionStart dans une nouvelle session | NOT_RUN | il sera visible à la prochaine session |

Mémoire globale : 6 leçons. PI-001, PI-002, PI-003 et PI-006 sont validées. PI-004 et PI-005 restent `tested` : le contrôleur a **refusé** leur promotion faute de test de régression et de preuve.

## 5. Limitations qui subsistent
1. **La vidéo de la forteresse est introuvable** (dépôt, uploads, references.zip). La bible de référence est **provisoire**, construite sur les 4 images approuvées `look_locked`. Il faut fournir la vidéo, ou 10 à 20 images clés.
2. **Les notes de décor (ENV_SCORES) sont un jugement de revue appuyé sur une image**, pas une mesure automatique. L'inventaire chiffre seulement la géométrie.
3. **La gate E vérifie la présence de preuves et le statut donné par le relecteur.** Elle ne juge pas seule qu'un effet est beau.
4. **Les limites du rig 2D restent** : pas de contrôle du regard dans le renderer, mains en poing rond, pas de main au-dessus de la tête, pas de tissu physique.
5. **Pour Ghost Army, le rendu final reste bloqué par des FAIL réels** :
   - Le **char héros** doit être modélisé dans Blender (version gonflable, extérieur seulement). L'Asset Hub refuse les modèles de char, et ce refus est respecté.
   - Les **lieux** dont la géométrie est notée sous 3 doivent être enrichis.
   - Les **preuves de rendu** manquent pour 7 des 9 actions.
   - Le **grade** doit être exécuté sur le film complet.
6. **Aucun achat, connexion ou décision de licence n'est automatisé** : ces cas vont dans `OPEN_ISSUES.md` pour décision de l'utilisateur.
