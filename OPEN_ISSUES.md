# OPEN_ISSUES — problèmes connus au 19/11/2026

`S/` = `.claude/skills/ricks-clips/`. Priorité : **P1** bloque la suite, **P2** est visible par CB, **P3** est interne.

## crashed_car

| # | Prio | Problème | Détail / piste |
|---|---|---|---|
| 1 | **P1** (seulement pour reprendre crashed_car) | **La vidéo source de CB n'est pas dans le dépôt** (ignorée par Git, par choix) | Une nouvelle session doit la redemander à CB pour analyser les plans 3 à 15. La transcription (`words.json`), les mesures et les planches sont versionnées |
| 2 | P2 | Plan 2 : le casque 3D est trop gros (le casque de référence est ajusté à la tête) ; les oreillettes de la casquette dépassent un peu en 2A | Le casque a été agrandi (×2,0) pour couvrir les oreillettes. Piste : rayon plus petit et oreillettes cachées par une forme de casque plus basse |
| 3 | P2 | Plan 2 : sol du stand trop sombre ; l'ombre longue du toit n'est pas lisible au sol comme dans la référence | Monter la valeur de `pit_concrete`, orienter le soleil pour projeter le toit dans le cadre |
| 4 | P2 | Plan 2 : asphalte du virage trop sombre, trop de cailloux ; il manque les grandes traces noires de dérapage | Valeur de `track_asphalt`, moins de débris, traces plus marquées |
| 5 | P2 | Plan 2 : deux gestes de bras en environ une image (4,2 s : bras qui descendent dans le cockpit ; 5,8 s : casque qui redescend) | Ils passent juste sous le seuil (0,87 et 0,85 contre 0,9 m par image). Piste : mouvements intermédiaires, ou réparer le mélange des mouvements |
| 6 | P2 | Plan 2 : pas de **poussière à l'atterrissage** du saut (signalé par `plan_check`, recette `jump_landing`) | Ajouter une bouffée de poussière `rc.vfx` à l'image 150 |
| 7 | P2 | Plan 2 : F1 retournée **sans bosses, sans fumée, sans vitre ni pièces tordues** (recette `vehicle_impact`) | Clés de forme et fumée `rc.vfx` |
| 8 | — | ~~Plan 1 : continuité non revérifiée~~ **RÉSOLU 19/11** | continuité PASS à 0 partout avec la version actuelle |
| 9 | P3 | Nuages trop ronds, décalques un peu grands, F1 retournée trop verticale | Points notés pendant le plan 2, non traités |
| 10 | P3 | En-tête de `s02_pit.py` : la docstring décrit encore « 158 the helmet lifts off » | Texte à mettre à jour. Le code est juste |

## Pipeline

| # | Prio | Problème | Détail |
|---|---|---|---|
| 11 | P3 | Outils génériques rangés dans `demos/crashed_car/` | `MIGRATION_PLAN.md`, étape 1 |
| 12 | P3 | `plan_check` et `continuity` ne sont pas branchés dans `rc_pipeline.py` | `MIGRATION_PLAN.md`, étape 2 |
| 13 | P3 | ~~Licence vide dans `catalog.json`~~ : **inexact**, vérifié le 19/11 : les 3 entrées ont déjà la licence CC-BY 4.0 complète. **Reste** : le `license.txt` de la berline crédite **Márcio Meireles** (sketchfab.com/marciomeireles), alors que le catalogue, `s01_driveway.py` et ces documents disent « MMC Works » | Pour le crédit CC-BY, utiliser le nom du `license.txt` |
| 14 | P3 | Le mélange des mouvements est sans effet entre deux vues différentes (cause des sauts de pose) | Contourné : une seule vue par personnage (règle et leçon PI-016) |
| 15 | P3 | Asset Hub : le modèle Sketchfab de « voiture bâchée » est refusé à tort par le filtre armes et militaire | Plan 5 : prévoir une simulation de tissu |
| 16 | P3 | Démo ferme : standard forteresse non atteint (5/10 et 6/10). Corrections enregistrées, effet NOT_RUN | `S/docs/RAPPORT_MIGRATION_FR.md` §4.2 |

## RunPod / compte

| # | Prio | Problème | Détail |
|---|---|---|---|
| 17 | P2 | Dépense de **0,005 $/h** alors que **aucun pod n'existe** (`pod.py balance` du 19/11 : `pods: []`, solde 3,58 $, contre 3,669 $ après la session) | Probablement du stockage (volume réseau ?). **À vérifier dans la console RunPod** ; ne rien supprimer sans l'accord de CB |

## Documentation

| # | Prio | Problème | Détail |
|---|---|---|---|
| 18 | P3 | `S/docs/RAPPORT_MIGRATION_FR.md` §3 annonce « `blender/rc/` (19 modules) » | Compté le 19/11 : 17 modules Python, plus `__init__.py` et `schema/`. À corriger dans ce rapport (non modifié pendant la passation) |
| 19 | P3 | Les 7 vidéos sources de référence ne sont pas dans le dépôt (ignorées par Git) | Les mesures, les transcriptions et les planches sont versionnées. Pour réanalyser une vidéo, la redemander à CB |
| 20 | P3 | Le gabarit de mouvement « cible 41,8 » de crashed_car est remplacé par la plage des 7 vidéos (20 à 65, médiane 30,6) | `CB_RULES` §11h cite encore 41,8 comme exemple : à lire comme « au niveau de la référence choisie » |
| 21 | P3 | Une session neuve ne repassait pas `test_rc` (25/27) : fichiers dérivés faits à la main | **RÉSOLU 19/11** (PI-017) : `tools/gltf_to_glb.py`, `scripts/restore_untracked.sh`, `test_rc` cuit le plan lui-même |
| 22 | P2 | crash_instinct plan 3 : `grade_match` échoue sur le contraste (images 0, 126, 180) ; rayons de soleil trop discrets ; cadrage aérien trop plongeant et arbre trop gros | Régler puis montrer les images clés à CB |
| 23 | P2 | crash_instinct : les dernières corrections de CB (route usée, champs en sillons, clôtures qui projettent une ombre, herbe des deux côtés, soleil arrière-gauche) ne sont pas encore revues par lui | Rendre les images clés 0, 46, 126, 180, 262 |
| 24 | P3 | `rc/look.py` existe mais `sets/roadside.py` ne l'utilise que pour le ciel, le soleil, le débouchage et les faisceaux : `road_wear`/`tex` y sont importés, `pbr`/`mat` viennent encore de `crashed_car/sets/street.py` | Fusionner à terme `street.py` dans `rc/look.py` (MIGRATION_PLAN étape 1) |
| 25 | P3 | Test GPU RunPod non fait ; le pod n'a pas le jeton Sketchfab (la berline et le SUV viennent de Sketchfab) | Convertir ces modèles en `.glb` et les fournir au pod ; accord et plafond de CB |
| 26 | P1 | crash_instinct plan 3, vue aérienne (images 177-231) encore loin de la référence, **non testé après les dernières modifications** : (1) route trop claire (reflet du ciel en vue rasante) : `rc.look.tex(spec=.12)` et valeur d'asphalte 0,7 sont codés mais **jamais rendus** ; (2) champs brun foncé au lieu de dorés (bandes or / ocre) ; (3) l'ombre de l'arbre est beaucoup trop petite (soleil abaissé à 24° dans `rc.look.SUN`, à vérifier) ; (4) contraste mesuré 0,14 contre 0,21 (`grade_match`) ; (5) rayons de soleil et lueur du soleil en haut à gauche trop discrets ; (6) arbre un peu trop petit et la caméra trop haute | Voir le prompt de reprise de CB (19/11). Aucun réglage global d'étalonnage ne règle l'image 180 sans dégrader la 262 : corriger dans la scène |

