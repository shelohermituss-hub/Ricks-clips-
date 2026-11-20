# Portes de qualité

Chaque porte : critère, seuil, **justification** (mesure sur les références), preuve attendue, exemple de réussite et d'échec. Les portes **existantes** dans le dépôt sont indiquées ; les autres sont des RECOMMANDATIONS à coder lors d'une mission de développement (rien n'a été codé ici).

| # | Porte | Seuil | Justification (MESURÉ) | Preuve attendue | Réussite / échec | Existe ? |
|---|---|---|---|---|---|---|
| G1 | Format | 9:16, ≥ 720×1280, 30 i/s | 5 références | ffprobe | 1080×1920 30 i/s / 16:9 | partiel (`plan_check`) |
| G2 | Crochet | action visible à t = 0 | 5 références (images 0) | image 0 + mot 0 | on peint à l'image 0 / paysage vide 2 s | oui (`plan_check` STORY) |
| G3 | Voix continue | pause ≤ 0,6 s ; 3,2-3,8 mots/s | pause max 0,36-0,64 s ; 3,21-3,83 mots/s | words.json | pause max 0,4 s / silence de 1,5 s | partiel (`plan_check` STYLE, débit) |
| G4 | Loudness | −14 ± 1 LUFS ; crête ≤ −1 dBTP | −13,9 à −14,2 ; crêtes −0,9 à −2,1 | ebur128 | −14,0 / −9 LUFS | oui (son) |
| G5 | Caméra jamais fixe | ≤ 2 images consécutives immobiles (hors gag déclaré < 2 s) | 0-3,1 % d'images quasi fixes | `continuity` HOLD | 0 HOLD / 15 images fixes | oui |
| G6 | Rien n'apparaît sans action | 0 POP, 0 TELEPORT (hors swap caché déclaré) | toutes les références | `continuity` | swap dans un fouetté déclaré / objet qui surgit | oui |
| G7 | Fait = action sur le mot | chaque mot-clé du script a une action visible à ± 0,3 s | MESURÉ dans les 5 (§1 des analyses) | plan.json + words.json | « 300 lbs » → impact à 25,4 s / mot sans image | partiel (`plan_check` ACTIONS) |
| G8 | Conséquence persistante | chaque action à conséquence a son état final visible au plan suivant où le lieu apparaît | colonne `persistence` de `event_catalog.csv` | rendu du plan suivant | fissure encore là / sol réparé tout seul | **oui** (`plan_check` STYLE5, champ `persists` de chaque action) |
| G9 | Ambiances | ≥ 4 ambiances de lumière par vidéo, chacune liée à une étape | 5 à 10 par référence | plan.json | jour, crépuscule, nuit, aube / tout en jour égal | **oui** (`plan_check` STYLE5 : FAIL pour une vidéo complète, WARN pour un fragment) |
| G10 | Étalonnage | luminosité, saturation, contraste dans la tolérance de la référence choisie, par plan | plages par seconde (`per_second.json`) | `grade_match` | PASS / saturation constante 0,35 | oui (`grade_match`) |
| G11 | Accent et lisibilité | le visage du personnage principal est la zone la plus contrastée ; un seul accent rouge | §4 de `VISUAL_LANGUAGE.md` | mesure de contraste local | visage net / visage noyé dans le décor | **à créer** |
| G12 | Signes d'émotion | au moins un signe 2D sur chaque émotion extrême du script | 5 références | plan.json | éclairs sur la rage / rage sans signe | **oui** (`plan_check` STYLE5, champ `sign`) |
| G13 | Transitions | chaque changement de lieu déclare sa transition (objet, fouetté, fondu, coupe) ; coupes franches réservées à l'accélération | §2 de `CAMERA_AND_EDITING_LANGUAGE.md` | plan.json | passage par une porte / coupe sèche entre deux lieux calmes | **oui** (`plan_check` STYLE5 : type de transition obligatoire ; coupe entre deux lieux = WARN sauf `accelerate: true`) |
| G14 | Choc de véhicule | anticipation + contact 1 image + pièce détachée ou déformation proportionnée + débris + trace qui reste | V02, V03, V04 image par image | images clés du choc | roue qui roule et reste / voitures qui s'interpénètrent sans dégât | partiel (recettes `vehicle_rear_end`, `vehicle_frontal_crash`, `vehicle_hits_fixed_obstacle` ajoutées le 20/11) |
| G15 | Benchmark moteur | temps par image et écart d'étalonnage mesurés sur EEVEE Next et Cycles, même plan | exigence de la mission | rapport de benchmark | deux chiffres + planches / choix sans mesure | **partiel** (20/11 : Cycles mesuré sur processeur, EEVEE non mesurable sans carte graphique ; `benchmark/BENCHMARK_FR.md`) |

Statuts de contrôle : PASS / WARN / FAIL / NOT_RUN (NOT_RUN ne vaut jamais PASS), comme le contrôleur de production existant.

Mise à jour du 20/11 : G8, G9, G12 et G13 sont codées dans `tools/plan_check.py` (zone STYLE5), testées par `tools/tests/test_plan_check.py` (« STYLE5 PASS »). Les 8 recettes de `INTERACTION_AND_PHYSICS_LANGUAGE.md` §5 sont dans `library/reactions/reactions.json`.
