# MISSION 1 — Construction des fondations : rapport

Date : 2026-11-18. Branche : `ccr-00f60cb8-lenpig`.
Commits : `1ea5950` (mémoire), puis les commits « Mission 1: … ».
Point de restauration : tag local `restore/pre-restructuration-2026-11-18`.
Statuts : PASS (preuve), PARTIAL, FAIL, NOT_RUN. Aucun pod lancé, aucun rendu complet, rien de supprimé.

## 1. Objectif
Poser les fondations de l'architecture validée en mission 0 :
- organisation Blender ;
- bibliothèque d'assets (Asset Library) ;
- assemblage des scènes ;
- cache persistant ;
- contrôle qualité ;
- intégration RunPod ;
- tests ;
- mémoire de production à jour.

## 2. Fichiers

**Nouveaux** (paquet `blender/rc/`) :
- `__init__.py` : description du paquet.
- `cache.py` : cache par contenu. La clé est le sha256 de (entrées + code + fichiers + versions). Publication atomique, `verify`, jamais de suppression automatique.
- `library.py` : bibliothèque, côté orchestrateur. Index, validation des métadonnées, `resolve(id)` qui construit puis ingère, via le cache.
- `bl_library.py` : bibliothèque, côté Blender. Ingestion en un `.blend` avec une collection marquée comme asset, matières PBR, ajout dans une scène, instances.
- `qa.py` : statistiques réelles d'une scène ou d'un asset. Objets, instances dessinées, triangles, formes primitives, matières texturées (y compris celles des instances), dimensions.
- `geo.py` : instanceur en Geometry Nodes, points d'éparpillement déterministes, terrain à relief.
- `assemble.py` : `place.json` plus caméra précalculée du film donnent une scène `.blend` autonome (assets intégrés, pas de liens vers le cache).
- `render.py` : gestionnaire de rendu. Moteurs, graine fixe, preuve GPU ou échec explicite, PNG sans métadonnées de temps, `render.json` avec le sha256 de chaque image.
- `cli.py` : commandes `assemble`, `stats` et `render` dans Blender.

**Autres nouveaux fichiers :**
- `blender/tests/fixtures/test_place.json` : lieu d'essai (terrain texturé, char héros, bulldozer, 30 leurres, 2 000 vélos en contrainte).
- `library/assets/*/*/asset.json` × 10 : métadonnées des assets existants.
- `production/config/rc_gates.json` : seuils des gates de la phase 1.
- `tools/tests/test_rc.py` : 15 tests des fondations.
- `scripts/runpod/blender_pod.sh` : pod Blender. Contrôle des périphériques Cycles (échec sans GPU), relevé `nvidia-smi` toutes les 2 s, cache sur le volume.
- `docs/MISSION_0_ARCHITECTURE_RICKSCLIPS.md` et ce rapport.

**Modifiés :**
- `tools/production_controller.py` : commande `scene-gates`.
- `templates/threejs_film/film.js` : `window.cardKeys`, la clé de contenu de chaque dessin.
- `templates/threejs_film/render_gpu.mjs` : cache des dessins, options `--who`, `--cards-only` et `--lock-dir`. Le dossier `out/lock` de l'épisode n'est jamais effacé par un test.
- `scripts/runpod/pod.py` : résultats attendus d'un pod `blender_pod.sh`.
- Mémoire : `STATE.md`, `OPEN_ISSUES.md`, `DECISIONS.md`, `QA_LOG.json` (QA-010 à 014), leçons PI-008 à PI-015.

## 3. Résultats et preuves

| Élément | État | Preuve (mesurée le 18/11) |
|---|---|---|
| Mémoire de production à jour | **PASS** | `STATE.md` réécrit, `OPEN_ISSUES` OI-2/4/5/6/7, QA-010 à 014, 8 leçons (PI-015 validée avec preuve ; les autres restent « tested » ou « proposed ») |
| Cache persistant | **PASS** | `test_rc` : 4/4. Première résolution des 10 assets : 17,6 s ; la deuxième : 2,5 s, avec 16 correspondances dans le cache sur 17 et seul le vélo reconstruit (son échelle avait changé) |
| Bibliothèque d'assets | **PASS** | 10 asset.json valides ; 8 modèles et 2 matières ingérés en `.blend`. Mesures : char gonflable 85 544 triangles et 0 % de primitives ; bulldozer 24 680 ; half-track 11 376 ; vélo 49 483 |
| Défaut d'échelle détecté par la mesure | **PASS** | Le vélo Sketchfab mesurait 1 013 m ; échelle corrigée dans `asset.json`, il mesure maintenant 1,70 m |
| Assemblage et instanciation | **PASS** | Lieu d'essai : 8 objets, 14 941 instances dessinées (environ 100 millions de triangles), assemblé en 30 s. Pour comparaison, l'import du champ créait 50 656 objets |
| Déterminisme | **PASS** | Image rendue seule ou après une autre : sha256 identiques sans débruiteur ; avec débruiteur OIDN, écart de 1/255 au plus (mesuré). Cause trouvée : métadonnées de temps de Cycles dans le PNG, retirées |
| Preuve GPU, cas sans GPU | **PASS** | `--gpu` sans GPU : échec explicite « GPU REQUIRED » (test) |
| Preuve GPU, cas avec GPU | **NOT_RUN** | Demande un pod payant |
| Cache des dessins de personnages | **PASS** | `radio_op` : 142 dessins en 79,2 s, puis 0,7 s au second passage (0 redessiné), dessins identiques octet par octet |
| Gates de la phase 1 (`scene-gates`) | **PASS** (l'outil) | Sur le lieu d'essai : 3 PASS, 1 FAIL, « matières texturées » (8/31). C'est la vérité : les modèles sur mesure n'ont que des couleurs unies |
| Pod Blender (`blender_pod.sh`) | **NOT_RUN** | Syntaxe vérifiée ; jamais exécuté sur un vrai pod |
| Protection des pods | **PASS** sur faux pod, **NOT_RUN** sur vrai pod | `test_pod_guard` 13/13 |
| Tests Production Intelligence | **PASS** | 11/11. Gates de l'épisode : 21 PASS, 5 WARN, 5 FAIL, 3 NOT_RUN, inchangés |

**Tests exécutés :** `test_rc.py` 15/15, `test_pod_guard.py` 13/13, `test_production_intelligence.py` 11/11.

## 4. Problèmes rencontrés pendant la mission
1. **Mesure trompeuse dans `qa.py`** (corrigée) :
   - les nuages de points qui portent les instances étaient comptés comme primitives ;
   - les matières des assets instanciés n'étaient pas comptées, ce qui faisait passer le gate « texturé » à tort.
2. **Faux échec de déterminisme :**
   - le sha256 du fichier changeait à cause des temps écrits dans le PNG ;
   - à pixels égaux, les fichiers sont maintenant identiques ;
   - le débruiteur ajoute 1/255 d'écart, ce qui est documenté.
3. **Erreur de mon audit :** il affirmait que Blender n'était pas installé localement. Blender 5.2.2 est bien présent dans `/usr/local/bin/blender`, et tous les tests ci-dessus l'utilisent.
4. **Régénération involontaire de `film.json`** par `make_film.py --help`. Vérifié identique ; aucun effet.

## 5. Ce qui reste ouvert (dont l'héritage de l'ancienne mission 1)
- **Modèles sur mesure sans textures :** gate « matières texturées » FAIL. À traiter en mission 2, avec des matières PBR teintées vers la palette.
- **three.js :** le correctif des anneaux sonores et la poussière avec graine sont écrits mais **NOT_RUN**, puisque le test de reproductibilité a été interrompu. Ils ne concernent que l'ancien pipeline, qui reste la référence V3.
- `from_lock.collapse_instances` : **NOT_RUN**. Ce n'est plus nécessaire, la scène native en Blender instancie dès l'assemblage.
- Pod Blender, preuve GPU réelle et minuterie qui arrête au lieu de supprimer : **NOT_RUN**, il faut un pod payant.
- Les modules E à I (intégration des personnages, animation, physique, effets, LookDev) ne sont pas encore écrits. Ils sont prévus pour la mission 2, sur le prototype.

## 6. Prochaine mission : mission 2, le prototype
**Lieu :** le champ de Ghost Army, avec une séquence d'environ 150 images. Contenu :
- terrain, haies et arbres en vraie géométrie instanciée, ferme ;
- char gonflable et bulldozer ;
- porteurs et Lou en cartes ;
- l'action « soulever le char », le vent, la poussière ;
- LookDev selon la palette.

**Test de destruction séparé :** le bulldozer percute une charrette, avec des planches fracturées et une roue détachée, tout précalculé.

**Rendus locaux :** Workbench, puis Cycles CPU à basse résolution.

**Benchmark et rendu GPU sur RunPod :** demandent ton autorisation (coût).
