# RAPPORT D'AUDIT COMPLET — RicksClips (opérations récentes)

Date de l'audit : 2026-11-18, 15:05-15:30 UTC.
Branche : `ccr-00f60cb8-lenpig` (synchronisée avec `origin`, arbre propre au début de l'audit).
Auditeur : Claude Code (session cloud). Mode **lecture seule** : aucun fichier de production modifié, aucun rendu, aucun test relancé. Le seul fichier créé est ce rapport.

## Légende des statuts de preuve
- **VÉRIFIÉ** : preuve directe relue pendant cet audit (fichier, sortie de commande dans le journal de session, commit Git).
- **DÉCLARÉ** : écrit dans un rapport antérieur, sans nouvelle vérification.
- **NON VÉRIFIÉ** : impossible à confirmer aujourd'hui.
- **ESTIMÉ** : valeur approximative, jamais mesurée.
- **ÉCHEC** : résultat négatif confirmé.

## Sources de preuve utilisées
- `git log` : 56 commits, dont 33 entre le 2026-11-17 18:07 et le 2026-11-18 14:59.
- Journal de session `/root/.claude/projects/-home-user-Ricks-clips-/c2e4e0a8-….jsonl` (95,6 Mo, 8 731 lignes). J'en ai extrait les 459 commandes shell du 18 novembre avec leurs sorties ; les extraits sont dans les annexes.
- Fichiers de l'épisode : `episodes/ghost-army/production/*`, `look/*`, `out/*`, `v1|v2|v3/*`.
- Mémoire : `memory/lessons_learned.json`, `.claude/settings.json`, `agents/` et `.claude/agents/`.
- **Non accessibles** :
  - les fichiers des pods RunPod supprimés (`098nig2lticccc`, `eq0n6km0gocqnk`, `qg67ic2umtuqgo`) ;
  - la facturation finale RunPod du pod LookDev, car le solde n'a pas été relu après suppression ;
  - les sessions antérieures au 2026-11-17 12:05.

---

## 1. Résumé exécutif

Ghost Army a une **preview complète V3** (540×960, 71,23 s, image et son) produite le 18/11 à 05:26 (VÉRIFIÉ, fichiers `v3/*.mp4`). Elle est mesurée contre la référence forteresse et échoue sur 4 seuils sur 10 :
- netteté des contours (« edge detail ») 0,060 pour une cible ≥ 0,075 ;
- 8 secondes au-dessus du plafond de saturation ;
- mouvement médian 12,9 pour une cible ≥ 18 ;
- 5,47 pics par 10 s pour une cible ≥ 6.

**Ce qui a été fait depuis la V3 :**
1. Corrections de l'étape 7, dans le code seulement : aucune preview de contrôle n'a été rendue.
2. Verrouillage (étape 8) réussi sur le pod, puis **perdu** à la suppression du pod (P0).
3. Prototype LookDev Blender sur 3 lieux : **échec**, couleurs non conformes, jugé raté par l'utilisateur.
4. Alternative three.js, ombres et occlusion puis enrichissement des décors : **faite sur 3 lieux sur 9**, en images fixes seulement, activée par un réglage optionnel qui n'est pas dans `film.json`.

**La mémoire de production n'est pas à jour.** `STATE.md` (11:23) indique encore « étape 8 non faite » et ne mentionne ni l'échec LookDev ni l'alternative three.js. `GATES.md` et les tests datent de 05:32, avant 3 commits qui touchent le moteur.

**Aucune preview ne représente l'état actuel du code.**

## 2. Période et périmètre
- **Période principale :** 2026-11-18 00:00 → 15:03 UTC, de l'intégration de Production Intelligence jusqu'à l'enrichissement des décors.
- **Contexte :** 2026-11-17 18:07 → 23:59 (construction de Ghost Army, preview v1, notes v1). LE DERNIER PHARE (17/11) n'est cité que pour le contexte.
- **Périmètre :** opérations de production Ghost Army, outils et kit (`tools/`, `templates/threejs_film/`, `scripts/runpod/`), mémoire Production Intelligence, pods RunPod.

---

## 3. Historique chronologique (UTC, 18/11 sauf mention)

| # | Heure | Opération | Commande ou script | Résultat | Preuve |
|---|---|---|---|---|---|
| H1 | 17/11 21:29 | Mixage son et preview v1 | `sound/mix.py`, assemblage | `v1/ghost_army_preview_v1.mp4` | VÉRIFIÉ (fichier, `06a6712`) |
| H2 | 17/11 22:42-23:10 | Notes v1 (1 à 8) : détail des chars, route de nuit, intérieurs, eau, ombres de contact, étalonnage | `sets/ghost.js`, `grade/grade.py` | commits `63d3a57`…`d7d980f` | VÉRIFIÉ (commits) |
| H3 | 17/11 23:26 → 00:01 | Audit animation et VFX | `audit/anim_audit.py` | 84 actions, 57 mouvements de la bibliothèque, statut PASS | VÉRIFIÉ (`GATES.md`, `f152839`, `91841af`) |
| H4 | 01:22 | Intégration Production Intelligence v1.0 | `tools/production_controller.py`, tests | 11/11 PASS | VÉRIFIÉ (journal, `dcd121d`) |
| H5 | 02:23 | Standard de référence forteresse officiel | `tools/reference_compare.py`, `compare-reference` | Bible v2.0 OFFICIELLE, outil et gate | VÉRIFIÉ (`b060146`) |
| H6 | 03:47 | Étape 0 : preview v2 (demi-résolution) mesurée | `render_gpu.mjs` en 3 tranches locales, `grade.py` | v2 raw et étalonnée ; mesures v1/v2 | VÉRIFIÉ (`9caf89e`, `REFERENCE_COMPARE_v2_*`) |
| H7 | 04:17-04:55 | V3, étapes 1 à 13 (avant rendu) : char gonflable Blender, leurres, prairie, intérieurs, route mouillée, caméra, fondus, explosions | `ghost.js`, `make_film.py`, `film_plan.py`, scripts Blender | commits `4862207`…`4ef2dfc` | VÉRIFIÉ (commits) |
| H8 | 04:42 | Bulldozer Blender et lignes électriques (demande utilisateur) | `build_crawler_dozer.py` | GLB et rendus | VÉRIFIÉ (`36505ce`) |
| H9 | 05:02-05:26 | Rendu V3 sur RunPod 4090 (`eq0n6km0gocqnk`, 0,34 $/h) | `pod.py create --post v3` | 2 137/2 137 images, **mode logiciel, 19 processus** ; MP4 brut et étalonné | VÉRIFIÉ (statut « mode=software », fichiers 05:26) |
| H10 | 05:18-05:28 | Correction GPU et pod de diagnostic (`qg67ic2umtuqgo`, 0,89 $/h) | `gpu_diag.sh`, `render_pod.sh` (bibliothèques X11/GLVND) | GPU NVIDIA atteint après correction | VÉRIFIÉ (`v3/pod/gpu_diag_after_fix.txt`, `c5568a8`) |
| H11 | 05:28 | Suppression des 2 pods, solde relu | `pod.py delete` | 7,2934 $ → 7,1684 $ (0,125 $ débités au moment de la mesure) | VÉRIFIÉ (journal) |
| H12 | 05:32 | Mesures V3, rapport de fin de mission V3, tests | `compare-reference`, tests PI | 11/11 PASS (après 9/11 puis correction du test inventaire) | VÉRIFIÉ (journal, `f213d0a`, `137390f`) |
| H13 | 11:19-11:23 | Audit LookDev (sans modification), règle 11g, `STATE.md` | lecture, `STATE.md` | Rapport présenté ; `STATE.md` écrit | VÉRIFIÉ (`b8625c4`) |
| H14 | 11:27-11:37 | Clôture de l'étape 7 : rythme forteresse, points 2 à 5 | `film_plan.py` (gates forteresse), `ghost.js` | Commit `618e804` ; **pas de rendu de contrôle complet** | VÉRIFIÉ (commit) ; rendu complet : NON EXÉCUTÉ |
| H15 | 11:40-11:44 | Plan LookDev complet, validé par l'utilisateur | — | Plan présenté et validé | VÉRIFIÉ (message utilisateur 11:44) |
| H16 | ≈11:50-12:07 | Verrouillage **local** (étape 8) | `render_gpu.mjs --export-lock` | **Interrompu** (`pkill` à 12:07:13) : 9 décors GLB et 3 dessins de Lou sur 1 380 | VÉRIFIÉ (`out/lock/`, journal) |
| H17 | 12:03-12:04 | Création du pod LookDev `098nig2lticccc` (4090 secure, 0,89 $/h, plafond 3 h) | `pod.py create --script lookdev_pod.sh` | Blender 5.2.2 installé (somme sha256 vérifiée), OPTIX | VÉRIFIÉ (`0319d17`, statut 12:06:37) |
| H18 | 12:07 | Correction du verrouillage : valeurs NaN dans les GLB → `dropInstances` | `ghost.js` | Commit `c8ff681` | VÉRIFIÉ |
| H19 | 12:17-12:18 | 2e export local des décors (inventaire) | `--export-lock` dans une copie locale | Décors exportés, puis arrêt volontaire | VÉRIFIÉ (journal) |
| H20 | 12:07 → 13:38:57 | **Verrouillage sur le pod** : précalcul `film_plan` (2 137 images), 9 décors, mouvements, dessins des 14 personnages | `lookdev_pod.sh` | dessins 14/14 à 13:38:57 ; angle WebGL `vulkan` (GPU) | VÉRIFIÉ (moniteur, `lock.log`) |
| H21 | 13:38-13:40 | Tâche 000 : nouvel export des décors seuls (`--sets-only`) et contrôle NaN | `000_relock.sh` | code retour 0, 96 s, 0 donnée invalide dans les 9 GLB | VÉRIFIÉ (journal) |
| H22 | 13:40 | Tâche 001 : test de fumée | `001_smoke.sh` | code retour 0 mais **`TypeError` résolution float** | ÉCHEC |
| H23 | 13:40 | Tâche 002 : prototype LookDev | `002_lookdev_proto.sh` | même `TypeError` | ÉCHEC |
| H24 | 13:41-13:47 | Tâche 003 : référence Blender (Cycles / EEVEE) | `003_smoke.sh` | 6 rendus, temps mesurés | VÉRIFIÉ (`look/proto/base_*`) |
| H25 | 13:47-13:50 | Tâche 004 : prototype passe 1 | `place_ld.py` | **403 Poly Haven** (User-Agent Python par défaut) | ÉCHEC |
| H26 | 13:51-14:04 | Tâche 005 : passe 1 avec User-Agent | `place_ld.py` | Rendus produits ; remplacements café et route invisibles | ÉCHEC (visuel) |
| H27 | 14:05-14:20 | Tâche 006 : passe 2 | `place_ld.py` | Couleurs fausses : affiches blanches, nuit rose, half-track rouille | ÉCHEC (visuel), preuves `look/proto/pass2/` |
| H28 | 14:22-14:36 | Tâche 007 : passe 3 | `place_ld.py` | 3 lieux terminés ; **sorties jamais téléchargées** | VÉRIFIÉ (fin), sorties perdues |
| H29 | 14:28 | L'utilisateur juge le LookDev « complètement raté » | — | 5 causes analysées | VÉRIFIÉ (message) |
| H30 | 14:38 | Suppression du pod LookDev | `pod.py delete` | `pods_left: []` ; **le verrouillage du pod est perdu** | VÉRIFIÉ |
| H31 | 14:41-14:48 | Aperçu three.js enrichi : occlusion, ombres suivant la caméra, lumière du ciel | `film.js`, `film_enrich.json` | 9 images V3 / enrichi, dérive de couleur mesurée | VÉRIFIÉ (`482544e`, `look/three_enrich/`) |
| H32 | 14:49-14:59 | Enrichissement des décors (option 2) : café, champ, route | `ghost.js` (`set_detail`) | 12 images ; V3 par défaut inchangée (0-0,4 % de pixels) | VÉRIFIÉ (`a0979ee`) |

Interruptions et reprises :
- Le verrouillage local a été interrompu volontairement deux fois (H16, H19) et déplacé sur le pod.
- La session a été compactée à 14:38, avec un résumé automatique sans perte de commits.
- Les moniteurs du pod ont expiré 3 fois au bout de 30 min et ont été relancés.

---

## 4. Réussites confirmées (A) — 15

| # | Opération | Pourquoi A | Preuve |
|---|---|---|---|
| A1 | Production Intelligence v1.0 | 11/11 tests, gates A à G opérationnels | VÉRIFIÉ, journal H4 |
| A2 | Standard de référence forteresse et outil de mesure | La référence passe tous ses seuils (auto-contrôle) | VÉRIFIÉ, `references/fortress/reference_compare_self.json` |
| A3 | Mesure de l'étape 0 (v1, v2 brute, v2 étalonnée) | Rapports `REFERENCE_COMPARE_v1/v2_*` | VÉRIFIÉ |
| A4 | Assets Blender sur mesure : char gonflable (85 548 triangles, 6 % de primitives), bulldozer, half-track, radio, manipulateur morse, table lumineuse, lignes électriques | Inventaire et rendus | VÉRIFIÉ (`GATES.md`, inventaire) ; rendus Blender DÉCLARÉS dans le rapport V3 |
| A5 | Correction du GPU RunPod (WebGL sur NVIDIA) | Diagnostic après correction, et le pod LookDev a exporté avec l'angle `vulkan` | VÉRIFIÉ |
| A6 | Mesure de la V3 contre la forteresse (mesure, pas qualité) | `REFERENCE_COMPARE_v3_raw/graded` | VÉRIFIÉ |
| A7 | Son de la V3 | −14,97 LUFS, −1,0 dBTP | DÉCLARÉ (rapport V3) |
| A8 | Règle 11g (position dans la pipeline à chaque rapport) | `CB_RULES.md` et 18 fichiers de département | VÉRIFIÉ (`b8625c4`) |
| A9 | Audit LookDev et plan LookDev | Présentés, puis plan validé par l'utilisateur | VÉRIFIÉ |
| A10 | Correction NaN du verrouillage | 0 donnée invalide sur les 9 GLB | VÉRIFIÉ (tâche 000) |
| A11 | Option `--sets-only` | Tâche 000 : code retour 0, 96 s | VÉRIFIÉ |
| A12 | Pod de tâches `lookdev_pod.sh` (installation, Blender sha256, file de tâches) | 8 tâches exécutées et publiées | VÉRIFIÉ |
| A13 | Tâche 003 : rendu de référence Blender et temps mesurés | 6 rendus, durées de construction et de rendu | VÉRIFIÉ |
| A14 | Suppression de tous les pods | `pods_left: []` à 05:28 et 14:38 | VÉRIFIÉ |
| A15 | Agents synchronisés | 17 agents identiques une fois les chemins normalisés | VÉRIFIÉ (audit) |

## 5. Réussites partielles (B) — 10

| # | Opération | Ce qui manque | Preuve |
|---|---|---|---|
| B1 | V3, étapes 1 à 13 | Rapport V3 : 5 PASS, 7 PARTIAL, 1 FAIL (caméra sous le seuil de mouvement) | VÉRIFIÉ (`GHOST_ARMY_V3_COMPLETION_REPORT.md` §F) |
| B2 | Rendu V3 sur le pod | Vidéo produite, mais **GPU non utilisé** (logiciel, 19 cœurs) ; fausse coupe dure dans la version étalonnée (fondu chambre → grenier) | VÉRIFIÉ |
| B3 | Corrections après la V3 (leurre proche, loupe, ordre étalonnage puis fondus sur le pod) | Dans le code, vérifiées sur images fixes ; **jamais rendues en vidéo** | VÉRIFIÉ (code) / NON VÉRIFIÉ (vidéo) |
| B4 | Clôture de l'étape 7 (rythme forteresse, points 2 à 5) | Gates du plan PASS ; **rendu de contrôle complet jamais fait** ; preuves des 7 lignes action-effet absentes | VÉRIFIÉ (commit) |
| B5 | **Étape 8, verrouillage** | Réalisé sur le pod (9 décors, dessins 14/14, contrôle NaN), puis **perdu** à la suppression du pod ; localement, seulement un verrouillage partiel interrompu | VÉRIFIÉ |
| B6 | Étalonnage V3 | Saturation 0,505 PASS mais 8 s au-dessus de 0,60 ; preuve du gate pointant vers des dossiers temporaires v2 | VÉRIFIÉ |
| B7 | Fondus et coupes | 8 fondus ou poussées et 2 coupes documentées ; 3 coupes dures détectées dans la V3 étalonnée | VÉRIFIÉ |
| B8 | Effets (explosions, étincelles) | Rapport : PARTIAL ; gate E : preuves rendues pour 2 événements sur 9 | VÉRIFIÉ |
| B9 | Enrichissement three.js (occlusion, ombres suivant la caméra, lumière du ciel) | Images fixes seulement, réglage hors `film.json`, tests non relancés | VÉRIFIÉ |
| B10 | Enrichissement des décors (`set_detail`) | 3 lieux sur 9, images fixes seulement, café plus sombre de 6 à 12 /255, tests non relancés | VÉRIFIÉ |

## 6. Échecs (C) — 7

| # | Opération | Échec | Preuve |
|---|---|---|---|
| C1 | Verrouillage local (H16) | Interrompu volontairement, trop lent : 3 dessins sur 1 380 pour Lou, pas de `lock.json` | VÉRIFIÉ |
| C2 | Tâche 001 (test de fumée) | `TypeError: … resolution_percentage expected an int type, not float` | VÉRIFIÉ |
| C3 | Tâche 002 (prototype) | Même `TypeError` (code retour 0 malgré l'erreur Blender) | VÉRIFIÉ |
| C4 | Tâche 004 (passe 1) | HTTP 403 de l'API Poly Haven | VÉRIFIÉ |
| C5 | Tâche 005 (passe 1 bis) | Objets de remplacement invisibles (collection source masquée au rendu) | VÉRIFIÉ |
| C6 | Tâche 006 (passe 2) | Couleurs non conformes : affiches et papier peint blancs, nuit rose, half-track brun, arbustes secs | VÉRIFIÉ (`look/proto/pass2/`) |
| C7 | Tâche 007 (passe 3) et méthode LookDev Blender | Méthode jugée ratée ; sorties perdues ; gros plan f285 noir (caméra dans la vessie du char) | VÉRIFIÉ (journal) |

## 7. Opérations non exécutées (D) — 10

| # | Opération | Raison |
|---|---|---|
| D1 | Rendu de contrôle complet après les corrections de l'étape 7 | L'utilisateur est passé au verrouillage |
| D2 | Preuves rendues des 7 lignes action-effet | Jamais lancé |
| D3 | Rendu final 1080×1920 (étape 10) | Nécessite l'accord explicite de l'utilisateur |
| D4 | Sous-titres, contrôle qualité et livraison (étape 12) | Dépend de l'étape 10 |
| D5 | LookDev des 6 autres lieux (camp, radio, photo, rivière, chambre, grenier) | Méthode non choisie |
| D6 | LookDev Blender calibré (option 1) | Option non retenue |
| D7 | Tests PI et gates après 05:32 | Jamais relancés, alors que 3 commits touchent le moteur et les outils (`618e804`, `4fcb600`, `482544e`) et 2 touchent `ghost.js` |
| D8 | Mise à jour de `STATE.md`, `OPEN_ISSUES.md` et `QA_LOG` après le verrouillage, le LookDev et l'enrichissement | Jamais faite |
| D9 | Extrait vidéo de l'enrichissement | Proposé, non lancé |
| D10 | Téléchargement du verrouillage et de la passe 3 avant suppression du pod | Oublié |

**Total : 15 A + 10 B + 7 C + 10 D = 42 opérations.**

---

## 8. Problèmes techniques et résolutions

| ID | Problème | Apparition | Module | Erreur exacte / symptôme | Cause | Tentatives → résultat | Statut | Risque |
|---|---|---|---|---|---|---|---|---|
| T1 | Le GPU du pod n'est pas utilisé | H9 | `render_pod.sh` | `GL_RENDERER = ANGLE (Mesa, Vulkan 1.3.255 (llvmpipe …))` | Bibliothèques X11 / GLVND / EGL absentes | Ajout des paquets et de `XDG_RUNTIME_DIR` → GPU atteint (diagnostic, puis verrouillage en `vulkan`) | Résolu ; **aucun rendu vidéo complet en GPU depuis** | Moyen |
| T2 | Pas de 4090 en cloud communautaire | H10 | `pod.py` | `There are no longer any instances available…` | Disponibilité RunPod | Cloud sécurisé à 0,89 $/h | Contourné | Élevé (externe) |
| T3 | Fausse coupe dure dans la V3 étalonnée | H12 | post-traitement du pod | coupe à 42,8 s | Étalonnage appliqué après les fondus | Ordre inversé dans `render_pod.sh` | Corrigé, **non testé** (aucun rendu depuis) | Moyen |
| T4 | Valeurs NaN dans les GLB, import Blender refusé | H17 | `ghost.js` | « bad accessors » | Instances mises à l'échelle zéro | `dropInstances` → 0 donnée invalide | Résolu (tâche 000) | Faible |
| T5 | Export des dessins de personnages lent | H16, H20 | `render_gpu.mjs --export-lock` | 1 380 dessins pour Lou ; 14 personnages en ≈ 92 min sur le pod | SVG converti en PNG en série, un dessin par état | `--sets-only` pour réutiliser les dessins | Contourné | Élevé à chaque nouveau verrouillage |
| T6 | `resolution_percentage` en float | C2, C3 | `smoke.py`, `place_ld.py` | `TypeError … expected an int type, not float` | Valeur 37,5 | `res=100` puis 540×960 | Résolu (tâche 003) | Faible |
| T7 | 403 Poly Haven | C4 | `ld.py` | 403 | User-Agent Python refusé | En-tête UA ajouté | Résolu | Faible |
| T8 | Objets de remplacement invisibles | C5 | `ld.py` | — | `hide_render` sur la collection source | Collection exclue de la couche de vue | Résolu dans le code | — |
| T9 | Couleurs LookDev non conformes | C6, C7 | méthode Blender | — | 5 causes : verrouillage qui aplatit textures et couleurs, textures photo à la place de la palette, AgX non calibré, lumière générique, défauts techniques | Passes 2 et 3 | **Non résolu** (méthode abandonnée ou à refaire) | — |
| T10 | Gros plan f285 noir en Cycles | C7 | scène Blender | — | Caméra à l'intérieur de `hull_bladder` (diagnostic) | Cause trouvée, pas de correction | Non résolu (Blender seulement) | — |
| T11 | Champ : 50 720 objets dans Blender | H24 | import glTF | `set_objects: 50720` | Instances éclatées en objets « Mesh » | Classement par forme | Partiel | Élevé si Blender |
| T12 | **Verrouillage perdu** | H30 | processus | `pods_left: []`, aucun `lock.json` en local | Pod supprimé sans téléchargement | — | **Non résolu** | — |
| T13 | Lueur du phare du half-track dépendante de l'ordre des images | H32 | `ghost.js` (`scene.onBeforeRender` → `CAM`) | f880 diffère de 4,5 % selon l'ordre | L'effet lit la caméra de l'image précédente | Diagnostiqué, pas corrigé | **Non résolu** | **Élevé** : le pod rend en tranches parallèles |
| T14 | Particules de poussière aléatoires | H31 | `film.js` `dustFor` | 0,3-0,4 % de pixels différents d'un rendu à l'autre | `Math.random()` | — | Non résolu | Faible |
| T15 | Lumière du ciel qui bleuit la peinture olive (f285) | H31 | `film.js` `env` | +10 /255 de bleu à `env=.5` | Reflet du ciel | Ramenée à 0,2 (+3,3 /255) | Partiel | Faible |
| T16 | Flaques bleues et clôture qui ressemble à des rails | H32 | `ghost.js` | visuel | Reflet du ciel ; clôture dans l'axe de la caméra | Flaques retirées, clôture déplacée | Résolu (images) | Faible |
| T17 | Rendu d'images figé ponctuellement | 17/11 | `render_gpu.mjs` | — | — | — | DÉCLARÉ, non revérifié | — |

**Corrigés mais jamais testés en non-régression :** T1 (aucun rendu vidéo complet en GPU), T3, B3 (leurre et loupe), points 2 à 5 de l'étape 7 en vidéo, et tous les changements du moteur et des outils depuis 05:32 (D7).

---

## 9. État des départements

| Département | Résultat attendu | État | Travail effectué | Preuve | Problèmes | Travail restant |
|---|---|---|---|---|---|---|
| Script et scénario | Script verrouillé | **PASS** | Script EN, faits sourcés | `SCRIPT.md`, gate A | — | — |
| Voix | Voix approuvée | **PASS** | Voix Fish, 70,6 s | `ec968ed` | — | — |
| Personnages et rigs | 14 rôles de la distribution | **PASS** (preview) | Distribution 2D (cartes) | `film.json`, rendus | Vélos dessinés en 2D (OI-3) | Décision vélos |
| Poses et expressions | Mouvements de la bibliothèque | **PASS** | 84 actions, 57 mouvements de la bibliothèque | gate D | 2 groupes en échec, dérogés | — |
| Animations | Pas d'immobilité ni de glissement | **PASS** | Audit animation | `anim_audit.json` | — | Revérifier après les modifications |
| Interactions | Effets sur les objets | **PARTIAL** | Réactions de groupe | rapport V3 §F 11 | Pas d'objets lancés | — |
| Environnements 3D | Score de détail ≥ 3 | **FAIL** (gate C) | 9 lieux ; enrichissement de 3 lieux (option) | `GATES.md` | Score géométrie de 2 sur 5 lieux (avant enrichissement) | Enrichir 6 lieux, re-noter |
| Assets et modélisation | Pas de placeholder héros | **FAIL** (gate B/G) | Char gonflable, bulldozer, half-track, accessoires | `GATES.md` | « Vrais » chars du passage : 96 % de primitives | Modèle ou décision |
| Textures et PBR | ≥ 85 % de surfaces texturées | **PARTIAL** | Matières procédurales | audit LookDev | 35-77 % texturées | — |
| LookDev Blender | Étape 9 | **FAIL** | Prototype en 3 passes | `look/proto/*` | Couleurs, perte du verrouillage | Choix de méthode |
| LookDev three.js (alternative) | Étape 9 | **PARTIAL** | Occlusion, ombres, lumière du ciel, décors de 3 lieux | `look/three_enrich/*` | Images fixes seulement | Vidéo, 6 lieux, intégration |
| Éclairage | Lumière visible et ombres | **PARTIAL** | Ombres sur 55 m et occlusion (option) | images | En V3 : ombres seulement dans 14 m | Adoption |
| Caméras | Standard forteresse | **PARTIAL** | Gates du plan PASS (forteresse) | `plan_report` | Mouvement V3 12,9 < 18 | Mesure sur une nouvelle preview |
| Effets visuels | 9 événements rendus | **FAIL** (gate E) | Explosions en couches | `GATES.md` | 2 sur 9 avec preuve | Bandes de preuve |
| Montage | Fondus et coupes justifiées | **PARTIAL** | `edit/joins.py` | `DECISIONS.md` | Fausse coupe (corrigée, non testée) | Rendu |
| Étalonnage | Saturation dans la plage | **PARTIAL** | `grade.py` | `REFERENCE_COMPARE_v3_graded` | 8 s > 0,60 | — |
| Audio et synchro | Mix et synchro | **PASS** (preview) | −14,97 LUFS | DÉCLARÉ | Gate E synchro : WARN | Revérifier sur le final |
| Rendu et export final | 1080×1920 | **NOT_RUN** | — | gate G NOT_RUN | — | Après accord |
| Contrôle qualité | Gates à jour | **PARTIAL** | Gates 05:32 : 21 PASS, 5 WARN, 5 FAIL, 3 NOT_RUN | `GATES.md` | Gates obsolètes | Relancer |

---

## 10. Performances

**Mesurées (VÉRIFIÉ) :**
- **Rendu local (WebGL logiciel, 4 cœurs, 15 Gio de RAM)**, en 540×960 :
  - 2 137 images en 3 662 s (1,71 s par image) le 17/11 ;
  - tranches v2 : 1 529 à 3 657 s pour environ 712 images (2,2 à 5,1 s par image) ;
  - images fixes : 1,3 à 7,9 s par image.
  - **La lecture de l'image (« grab ») représente 85 à 93 % du temps** (draw 0,1-0,9 s, grab 1,1-7,3 s).
- **Pod V3 (4090, en logiciel)** : 2 137 images rendues ; temps déclaré de 901 s (DÉCLARÉ). Post-traitement commencé à 980 s écoulées (VÉRIFIÉ, moniteur).
- **Verrouillage sur le pod** : 12:07:06 → 13:38:57, soit **≈ 92 min**, presque entièrement les dessins.
  - Dessins relevés : Lou 1 380, carrier_tall 787, carrier_short 788, carrier_stocky 313, spy 244, waitress 244, sound_op 223, radio_op 142.
  - Les 6 autres personnages : NON VÉRIFIÉ (absents des extraits du journal).
- **Décors GLB** : camp 177,6 Mo, rivière 109,0 Mo, route 87,1 Mo, champ 24,3 Mo, grenier 17,4 Mo, chambre 15,8 Mo, radio 0,75 Mo, café 0,28 Mo, photo 0,22 Mo. Total ≈ 423 Mo. Ré-export `--sets-only` : 96 s.
- **Blender 5.2.2 sur le pod (tâche 003, 540×960, 64 échantillons)** :

| Lieu | Construction | Cycles | EEVEE |
|---|---|---|---|
| Champ (50 720 objets) | 80 s | 125 s | 38,7 s |
| Café | 4,9 s | 3,5 s | 1,9 s |
| Route | 15,3 s | 4,0 s | 6,1 s |

- **Passes LookDev** : 3,0 à 9,1 s par image « look ».
- **Enrichissement three.js en local** : 2,4 s par image (V3) contre 3,8 à 4,1 s par image (enrichi).

**Coûts :**
- V3 et diagnostic : 0,125 $ (VÉRIFIÉ).
- Pod LookDev : 0,89 $/h de ≈ 12:03 à 14:38, soit **≈ 2,3 $ (ESTIMÉ, solde non relu)**.

**Non mesurés :** RAM, CPU et GPU pendant les rendus (NON VÉRIFIÉ). Au moment de l'audit : 760 Mio de RAM utilisés sur 15 Gio, disque à 52 %.

**Opérations répétées inutilement :**
- verrouillage tenté 2 fois en local et fait 2 fois sur le pod ;
- 4 lancements du prototype LookDev (002, 004/005, 006, 007) ;
- dessins de personnages recalculés à chaque verrouillage complet.

**Cache :**
- Un cache de personnages par processus (`--cache`) : 14 dossiers dans le dossier de travail temporaire, qui pèse **5,1 Go** au total.
- Aucun cache des dessins du verrouillage entre deux runs, à part `--sets-only`, qui suppose un `lock.json` existant.

**Goulots d'étranglement :**
1. Les dessins du verrouillage (≈ 92 min).
2. La lecture de l'image côté navigateur.
3. Le WebGL logiciel en local.
4. L'éclatement des instances à l'import glTF dans Blender.

**Optimisations proposées (non appliquées) :**
- dessins en parallèle sur plusieurs pages, avec un cache par état (hash SVG) ;
- lecture des pixels directement sur le GPU au lieu de la composition par toDataURL ;
- garder `EXT_mesh_gpu_instancing` sous forme de collections instanciées dans Blender ;
- **télécharger les sorties du pod avant de le supprimer** (règle à ajouter à `pod.py delete`).

---

## 11. Intégrité des fichiers et du dépôt
- **Git :** branche `ccr-00f60cb8-lenpig` = `origin`, aucune modification non enregistrée, aucun fichier non suivi (VÉRIFIÉ). Taille de `.git` : 335 Mo.
- **`out/` est ignoré par Git** (`.gitignore:23`) : le verrouillage n'est jamais versionné.
- **`out/lock/` local** : 9 GLB (12:08), `motion/` (9 fichiers JSON), `cards/lou/` 3 PNG sur 1 380, **pas de `lock.json`**. C'est un **export incomplet**, qui ne correspond pas au verrouillage réalisé sur le pod.
- **Doublon de configuration** : `film_enrich.json` est une copie de `film.json` plus `post.ao`, `shadow_follow`, `env` et `set_detail`. Toute modification future de `film.json` le rendra divergent.
- **Divergences entre la documentation et la réalité :**
  1. `STATE.md` (11:23) : « étape 8 NOT DONE, étape 9 NOT DONE ». Rien sur le verrouillage du pod, l'échec du LookDev ni l'alternative three.js.
  2. `GATES.md` (05:32) : le gate `grade_applied_to_all_shots` cite des dossiers temporaires `scratchpad/v2raw` et `v2graded` (preuve temporaire, liée à la v2).
  3. `OPEN_ISSUES.md` (02:23) : OI-2 « hero tank primitive » est obsolète (le char gonflable est modélisé), et OI-4 n'est pas mis à jour après la V3.
  4. `QA_LOG.json` : QA-006 à QA-009 ouverts. Les corrections après la V3 (leurre, loupe) n'y sont pas reportées.
  5. Le rapport V3 §E indique « environ 22 minutes au total » pour le pod de rendu ; ce n'est pas revérifiable (facturation non relue).
- **Fichiers temporaires encore utiles :** le dossier de travail temporaire de la session (5,1 Go) contient `pod_ld.json` (URL de statut d'un pod supprimé, sans intérêt), des copies de sauvegarde (`ghost_bak2.js`, `film_before.json`) et les caches. Il sera perdu à la fin de la session.
- **Dépendances :** Blender n'est pas installé localement (seulement sur les pods). Node, Playwright et Chromium locaux fonctionnent (VÉRIFIÉ par les rendus d'aujourd'hui).
- **Secrets :** aucune clé n'apparaît dans ce rapport. Les clés RunPod et autres sont des secrets réseau de l'environnement, jamais lus.

---

## 12. État réel de Ghost Army
- **Terminé et vérifié :**
  - script, voix, plan (0 FAIL), audit d'animation, mix son de la preview ;
  - preview V3 complète (vidéo) et ses mesures ;
  - assets Blender sur mesure.
- **Amélioré depuis la v1 (VÉRIFIÉ sur images et mesures)** :
  - char gonflable modélisé, leurres variés, prairie et paysage lointain, route de nuit mouillée, intérieurs habillés, explosions en couches ;
  - luminosité de nuit de 0,192 à 0,283 ;
  - noirs bouchés de 1,3 % à 0,05 % ;
  - saturation de 0,685 à 0,505.
- **Vérifié uniquement dans le code ou sur images fixes, pas en vidéo :**
  - corrections après la V3 et points 2 à 5 de l'étape 7 ;
  - enrichissement three.js et `set_detail` ;
  - ordre étalonnage puis fondus sur le pod.
- **Non vérifié :**
  - tests et gates depuis 05:32 ;
  - netteté des contours, mouvement et pics avec les modifications ;
  - rendu GPU complet.
- **Défauts visuels encore présents** :
  - détail sous le seuil forteresse ;
  - 8 s de sursaturation ;
  - mouvement 12,9 < 18 ;
  - vrais chars du passage en primitives ;
  - vélos en 2D ;
  - 3 coupes dures ;
  - lueur du phare instable entre tranches ;
  - café enrichi plus sombre ;
  - dossiers de chaises simples.
- **Étapes LookDev effectuées :**
  - audit et plan ;
  - verrouillage (perdu) ;
  - prototype Blender sur 3 lieux en 3 passes (échec) ;
  - aperçu three.js (3 lieux, images fixes).
- **Étapes LookDev jamais exécutées :**
  - méthode calibrée ;
  - les 6 autres lieux ;
  - validation par l'utilisateur d'une image par lieu ;
  - passes finales (ombres, cartes de personnages) dans Blender.
- **Bloquants pour le rendu final :**
  1. Méthode d'étape 9 non décidée.
  2. Aucune preview de l'état actuel.
  3. Gates FAIL (B, C, E, F).
  4. Lueur dépendante de l'ordre des images (rendu en tranches).
  5. Accord de l'utilisateur.
- **Nouvelle preview complète disponible ?** **Non.** La dernière preview complète est la V3 (05:26), antérieure aux commits `618e804`, `482544e` et `a0979ee` et aux corrections après la V3.

## 13. État de Production Intelligence
- **Mémoire globale :** `memory/lessons_learned.json`, 7 leçons. 5 validées (PI-001, 002, 003, 006, 007) et 2 testées mais non promues (PI-004, PI-005). VÉRIFIÉ.
- **Mémoire de l'épisode :** `production/*` existe mais n'est **pas à jour** depuis 11:23 (voir §11).
- **Leçons d'aujourd'hui non enregistrées** (risque de perte à la prochaine session) :
  1. Télécharger les sorties d'un pod avant de le supprimer.
  2. Le verrouillage aplatit textures, couleurs par sommet et couleurs par instance.
  3. Un LookDev doit partir de la palette validée et être calibré, jamais la remplacer.
  4. L'import glTF éclate les instances.
  5. Un effet ne doit jamais dépendre de l'image précédente (rendu en tranches).
  6. Poly Haven exige un User-Agent.
  7. `resolution_percentage` est un entier.
- **Gates :** dernier passage à 05:32 (21 PASS, 5 WARN, 5 FAIL, 3 NOT_RUN). Obsolète.
- **Rapports QA :** QA-001 à 004 corrigés, QA-005 dérogé, QA-006 à 009 ouverts.
- **Matrice action-effet :** 9 événements, preuves rendues pour 2 (gate E FAIL).
- **Synchronisation des agents :** OK (VÉRIFIÉ).
- **Hooks de démarrage :** `.claude/settings.json` lance `cloud_session_start.sh` et `production_memory_brief.sh`. Les deux scripts existent ; leur exécution à l'ouverture de cette session n'est pas visible dans le journal (NON VÉRIFIÉ).
- **Tests de non-régression :** 11/11 PASS à 05:32 (VÉRIFIÉ) ; **NOT_RUN depuis**. Non relancés pendant l'audit, car ils écrivent des fichiers (`GATES.md`, `QA_LOG`, mémoire).

---

## 14. Bloqueurs et problèmes ouverts (22)

| Prio | ID | Problème | Solution recommandée | Dépendances | Preuve de résolution |
|---|---|---|---|---|---|
| P0 | O1 | Verrouillage de l'étape 8 perdu ; seul existe un export local incomplet | Refaire le verrouillage seulement quand la méthode de l'étape 9 l'exige, et **télécharger** `out/lock` avant toute suppression de pod | Choix de méthode (O3) | `lock.json` et 14 dossiers de dessins en local, sommes de contrôle |
| P0 | O2 | Mémoire de production obsolète (`STATE.md`, `OPEN_ISSUES`, `QA_LOG`, leçons du jour) | Mettre à jour `STATE.md` et ajouter les 7 leçons du jour | — | `STATE.md` daté et cohérent ; leçons enregistrées |
| P1 | O3 | Méthode de l'étape 9 non décidée (Blender raté ; three.js sur 3 lieux sur 9) | Décision de l'utilisateur | — | Décision dans `DECISIONS.md` |
| P1 | O4 | Aucune preview de l'état actuel du code | Preview de contrôle complète (540×960) | O3 (inclure ou non l'enrichissement) | MP4 et `compare-reference` |
| P1 | O5 | Tests et gates non relancés depuis 05:32 | Lancer les tests PI et les gates | — | 11/11 et nouveau `GATES.md` |
| P1 | O6 | Lueur du phare dépendante de l'image précédente | Calculer la caméra de l'image courante dans `ghost.js` | — | Même image, quel que soit l'ordre (0 % de différence) |
| P1 | O7 | Seuils forteresse en échec (détail, mouvement, pics, saturation) | Enrichissement des décors, caméra, étalonnage | O4 | `REFERENCE_COMPARE` PASS |
| P1 | O8 | Gate E : 7 événements sur 9 sans preuve rendue | Bandes de preuve action-effet | O4 | Gate E PASS |
| P1 | O9 | Rendu GPU complet jamais prouvé depuis la correction | Le prochain rendu sur pod vérifie le GPU (échoue sans `--allow-cpu`) | — | Journal du pod avec mode GPU |
| P2 | O10 | Vrais chars du passage en primitives (gate B/G) | Modèle Blender sur mesure ou décision | — | Inventaire < 60 % de primitives |
| P2 | O11 | Score de géométrie 2 sur 5 lieux (gate C) | Enrichir les 6 lieux restants | O3 | Gate C PASS |
| P2 | O12 | Fausse coupe dure de la V3 étalonnée | Corrigée dans le script, à prouver | O4 | 0 coupe non justifiée |
| P2 | O13 | Café enrichi plus sombre (−6 à −12 /255) | Compenser l'éclairage | O3 | Dérive < 4 /255 |
| P2 | O14 | Lumière du ciel qui bleuit la peinture (atténuée à 0,2) | Lumière du ciel neutre ou masquée sur la peinture | — | Dérive < 2 /255 |
| P2 | O15 | Vélos en 2D (OI-3) | Décision | — | Décision |
| P2 | O16 | Gros plan f285 noir et 50 720 objets (si Blender) | Déplacer la caméra et garder les instances | O3 = Blender | Rendu non noir, nombre d'objets |
| P2 | O17 | `film_enrich.json` en double de `film.json` | Intégrer les options dans `film.json` ou générer le fichier | O3 | Un seul fichier source |
| P2 | O18 | Preuve d'étalonnage du gate G pointant vers des dossiers temporaires v2 | Relancer le gate sur un rendu durable | O4 | Chemin durable |
| P3 | O19 | Export des dessins lent (≈ 92 min) | Parallélisation et cache par état | — | Temps mesuré |
| P3 | O20 | Lecture d'image = 85-93 % du temps de rendu | Lecture directe sur le GPU | — | ms par image |
| P3 | O21 | Particules de poussière non déterministes | Graine fixe | — | 0 % de différence |
| P3 | O22 | `pod.py` sans commande de solde ; 5,1 Go de fichiers temporaires | Ajouter la commande ; nettoyer | — | — |

## 15. Plan d'action priorisé (non appliqué, attend l'accord)
1. **O2** : mettre la mémoire de production à jour (rien d'autre ne change), pour qu'aucune information ne se perde à la prochaine session.
2. **O3** : décision de l'utilisateur sur la méthode de l'étape 9.
3. **O5 et O6** : relancer tests et gates ; corriger la lueur dépendante de l'ordre.
4. **O4, O9, O12** : preview de contrôle complète sur le pod en GPU, avec téléchargement avant suppression ; mesure contre la forteresse.
5. **O7, O8, O11** : selon les écarts mesurés, enrichir les 6 lieux restants et produire les preuves d'effets.
6. **O1** : verrouillage seulement si la méthode Blender est retenue.
7. Étape 10 (rendu final) après accord explicite, puis étapes 11 et 12.

## 16. Conclusion générale
Le projet a progressé réellement et de façon mesurée jusqu'à la V3. Mais les opérations d'après-midi (verrouillage, LookDev Blender) ont **échoué ou ont été perdues**, et l'alternative three.js n'en est qu'au stade d'aperçu en images fixes.

Le code est propre et versionné. **L'état documenté est en retard sur le réel et aucune vidéo ne reflète le code actuel.** On est à l'**étape 9 (LookDev), méthode non décidée**. Les étapes 10 à 12 ne sont pas commencées, à part le mix son de la preview.

---

## Annexes

### A1. Commandes principales (extraites du journal de session)
```
node templates/threejs_film/render_gpu.mjs episodes/ghost-army/film.json --export-lock --cache …        # H16 / H19, interrompues
.venv/bin/python scripts/runpod/pod.py create --gpu "RTX 4090" --cloud SECURE --script lookdev_pod.sh …  # H17
bash episodes/ghost-army/look/jobs/000_relock.sh   ->  {"rc":0,"seconds":96}
bash episodes/ghost-army/look/jobs/001_smoke.sh    ->  {"rc":0,"seconds":5} + TypeError resolution_percentage
.venv/bin/python scripts/runpod/pod.py delete 098nig2lticccc   ->  {"deleted": "098nig2lticccc"} {"pods_left": []}
node ../../templates/threejs_film/render_gpu.mjs film_enrich.json --frames 30,150,285,800,880,960,1185,1245,1305 --stills-dir look/three_enrich/enr
node ../../templates/threejs_film/render_gpu.mjs film.json --frames 30,150,285,800,880,960,1185,1245,1305 --stills-dir /tmp/claude-0/chk7   # contrôle V3 : 0-0,41 %
```

### A2. Extraits de journaux
```
[status] render mode=software angle= procs=19 frames 2137/2137                       (pod V3, 05:2x)
deviceName = llvmpipe (LLVM 15.0.7, 256 bits)                                        (gpu_diag.txt, avant correction)
{'myself': {'clientBalance': 7.1683981104, 'currentSpendPerHr': 0.005, 'pods': []}}  (05:28)
webgl angle: vulkan                                                                   (pod LookDev, verrouillage)
NANCHECK <9 lieux>.glb bad accessors: 0                                               (tâche 000)
SMOKE {"place": "field", "frame": 285, "engine": "CYCLES", "samples": 64, "build_s": 80.0, "render_s": 125.0, "set_objects": 50720}
DIAG {'step': 'diag f285', … 'hit': [True, [-2.27, 4.75, 2.4], 'hull_bladder']}      (passe 3 : caméra dans la vessie)
PLACE DONE field/cafe/road …                                                          (passe 3, 14:36)
même code, deux rendus de f880 : 0,0 % ; V3 en lot contre f880 seul : 4,52 %          (lueur dépendante de l'ordre)
```

### A3. Fichiers de preuve
- Previews : `episodes/ghost-army/v1/`, `v2/`, `v3/*.mp4` ; `v3/pod/gpu_diag*.txt`.
- Mesures : `episodes/ghost-army/production/REFERENCE_COMPARE_*.json|md`, `GATES.md`, `QA_LOG.json`, `GHOST_ARMY_V3_COMPLETION_REPORT.md`, `STATE.md` (obsolète).
- LookDev Blender : `episodes/ghost-army/look/proto/` (base, passe 1 champ) et `look/proto/pass2/` (31 fichiers). Passe 3 : **perdue**.
- Three.js : `episodes/ghost-army/look/three_enrich/` (`v3/`, `enr/`, `det/`, `compare_*.jpg`, `colour_shift*.txt`).
- Verrouillage local incomplet : `episodes/ghost-army/out/lock/` (non versionné).
- Journal de session : `/root/.claude/projects/-home-user-Ricks-clips-/c2e4e0a8-fcc3-5126-ae4d-aec5b0cb3372.jsonl`. Extractions de l'audit dans le dossier de travail temporaire `/tmp/claude-0/audit_tools.txt` et `/tmp/claude-0/audit_results.txt`, perdues à la fin de la session.
