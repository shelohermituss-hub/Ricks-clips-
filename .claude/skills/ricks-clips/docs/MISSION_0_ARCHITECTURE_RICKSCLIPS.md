# MISSION 0 — Audit architectural et plan de restructuration de RicksClips

Date : 2026-11-18. Branche : `ccr-00f60cb8-lenpig`.
Point de restauration avant restructuration : commit `HEAD` au moment de cette mission, avec le tag local `restore/pre-restructuration-2026-11-18`.

**Sources lues :**
- le code réel : `templates/`, `tools/`, `scripts/runpod/`, `episodes/ghost-army/`, `library/`, `memory/` ;
- le rapport `RAPPORT_AUDIT_COMPLET_RICKCLIPS.md`, présent dans le dépôt et lu ;
- les images de référence de la forteresse, `references/fortress/overview_1fps.jpg` (66 s).

**Statuts :** PASS / PARTIAL / FAIL / NOT_RUN. Mesure = VÉRIFIÉ, sinon ESTIMÉ ou DÉCLARÉ.

---

## 1. Ce que montre la référence forteresse (objectif visuel)

On voit sur les 66 images de `overview_1fps.jpg` :
- **Monde construit et rendu dans Blender :** murs de pierre maçonnés (texture et relief), herbe dense en vraie géométrie, chariot en bois détaillé (planches, roues à rayons, ferrures), toitures asiatiques, bannières, sol dallé, paysage en plusieurs plans de profondeur, ciel à nuages.
- **Personnages :** les mêmes cartes 2D vectorielles que RicksClips, plantées dans le monde 3D, avec ombres portées et contact au sol.
- **Lumière :** soleil dur avec ombres longues, une séquence de nuit avec lanternes et pluie, lumière douce du ciel, volumétrie légère.
- **Effets :** étincelles, flèches de feu en trajectoires, explosion stylisée en volume, poussière.
- **Mesures** (`references/fortress/reference_compare_self.json`, VÉRIFIÉ) : détail des contours 0,095 ; luminosité de jour 0,433 ; saturation 0,40 ; 10,47 pics de mouvement par 10 s ; 0 image figée ; 0 coupe sèche.

**Conclusion :** la cible n'est pas du photoréalisme. C'est un **monde 3D stylisé, réellement modélisé et texturé dans Blender**, avec des personnages 2D intégrés. Le système de personnages actuel est donc compatible avec la cible ; c'est **la construction des environnements et le moteur de rendu** qui doivent changer.

---

## 2. Diagnostic de l'architecture actuelle (fondé sur le code)

### 2.1 Deux pipelines concurrents
1. **Pipeline three.js** (le pipeline réel de Ghost Army) :
   - les décors sont écrits en JavaScript (`episodes/ghost-army/sets/ghost.js`, 803 lignes) avec des primitives three.js ;
   - le moteur `templates/threejs_film/film.js` (1 006 lignes) dessine ces décors, plus `look3d.mjs` (509 lignes) pour les matières procédurales, les nuages et les arbres ;
   - les rendus passent par Chromium (`render_gpu.mjs`) ;
   - le verrouillage (`--export-lock`) exporte ensuite les décors en glTF vers Blender.
2. **Pipeline Blender** (`templates/blender_look/`, 4 628 lignes) :
   - `from_lock.py` reconstruit un lieu à partir du verrouillage glTF ;
   - `materials.py` (bibliothèque procédurale), `lights.py`, `render.py`, `scatter.py`, `detail.py` ;
   - `lock2.py`, `build_density_v3.py`, `aircraft.py` : un ancien chemin « monde Blender complet » écrit en Python pour Night Witches.

Ces deux pipelines construisent **les mêmes décors deux fois** :
- les décors existent en JavaScript, puis passent par un export glTF avec pertes ;
- le passage vers Blender **perd les textures, les couleurs par sommet et les couleurs par instance** (constat VÉRIFIÉ lors du LookDev raté) ;
- il **éclate les instances en objets séparés** : 50 656 objets pour seulement 202 maillages dans le champ (VÉRIFIÉ par l'import Blender 5.2.2 local).

C'est la cause structurelle principale de l'échec du LookDev.

### 2.2 Inventaire des composants

| Composant | Fichiers | Fonction | Décision | Raison |
|---|---|---|---|---|
| Plan du film | `film.json`, `tools/film_plan.py` (721 l.), `build/make_film.py` | Plans, stations caméra, actions, effets, humeurs ; précalcul (« bake ») de la caméra et du jeu ; 41 gates | **CONSERVER** | Indépendant du moteur, testé (0 FAIL), produit `camera_baked.json` et `performance_baked.json` lisibles par Blender |
| Personnages 2D | `templates/vector2d_characters/code/*.mjs`, `templates/threejs_film/puppets.mjs`, `poses.mjs`, `motion_styles/` | Distribution de 150 personnages, poses, expressions, mouvements de la bibliothèque, micro-animation | **CONSERVER** le dessin, **ADAPTER** la production | Même style que la forteresse. Le défaut est le coût : 92 min pour les dessins, sans cache entre deux exécutions |
| Export des dessins | `render_gpu.mjs --export-lock` (cartes) | SVG → PNG par état, via Chromium | **REMPLACER** par un service de cartes avec cache | Recalcule tout à chaque verrouillage, en série |
| Décors three.js | `episodes/*/sets/*.js`, `look3d.mjs`, `film.js` (partie décor) | Construction des lieux | **REMPLACER** par des constructeurs Blender | Primitives, export avec pertes, deux moteurs |
| Rendu three.js | `film.js`, `render_gpu.mjs` | Aperçus et animatic | **RETIRER progressivement** pour le décor | Un aperçu Blender (Workbench ou EEVEE à basse résolution) remplace l'animatic, à partir de la même scène |
| Passe Blender | `from_lock.py`, `materials.py`, `lights.py`, `render.py`, `look.py` | Look à partir du verrouillage | **ADAPTER** | Lumières, matières et caméra réutilisables ; l'import du verrouillage devient un simple chemin de migration |
| Monde Blender en Python | `scatter.py`, `detail.py`, `aircraft.py`, `build_density_v3.py` | Construction procédurale, éparpillement (« scatter ») | **ADAPTER** : extraire les fonctions génériques | Réutilisable, mais lié à une seule production |
| Assets sur mesure | `library/assets/custom/_blender_kit.py` + 4 constructeurs (char gonflable, bulldozer, half-track, accessoires) | Modèles Blender scriptés | **CONSERVER**, intégrer à l'Asset Library | Prouvés : char gonflable 85 548 triangles, 6 % de primitives |
| Asset Hub | `tools/asset_hub.py` | Recherche et ingestion Poly Haven, ambientCG, Sketchfab, Fab, BlenderKit avec licences | **CONSERVER** | Fournisseurs joignables (HTTP 200 vérifié le 18/11) ; catalogue presque vide (3 assets) |
| Caméras d'action | `templates/blender_cine/cine.py` | Montures de caméra (poursuite, orbite) précalculées en images clés | **CONSERVER** | Natif Blender |
| Production Intelligence | `tools/production_controller.py`, `memory/`, gates A-G, `reference_compare.py` | Mémoire, gates, mesure contre la référence | **CONSERVER et ÉTENDRE** | Fonctionne (11/11 à 05:32) ; il faut de nouveaux gates Blender |
| RunPod | `scripts/runpod/pod.py`, `*_pod.sh`, `manifest.py` | Pods, protection des résultats (13/13), GPU WebGL | **ADAPTER** | Tâches Blender Cycles, preuve d'utilisation du GPU, cache sur volume |
| Étalonnage, son, montage | `grade/grade.py`, `sound/mix.py`, `edit/joins.py` | Post-production | **CONSERVER** | Indépendants du moteur |
| Règles et agents | `CB_RULES.md`, `rules/dept/*`, `agents/*.md` (17) | Règles par département | **ADAPTER** au nouveau pipeline | Une seule source de règles |

### 2.3 Problèmes structurels et réponse prévue

| Problème (audit) | Cause structurelle | Réponse dans l'architecture cible |
|---|---|---|
| Verrouillage de 92 min | Les dessins sont recalculés en série, sans cache entre exécutions | **Character Card Service** : cache par contenu (sha256 du SVG d'état), plusieurs pages en parallèle, seuls les états nouveaux sont recalculés |
| Absence de cache persistant | Aucun mécanisme commun | **Cache par contenu** (`rc_cache`) partagé par tous les constructeurs |
| 50 656 objets dans le champ | Export glTF suivi d'un import Blender | Les décors sont construits **dans** Blender, avec des Geometry Nodes et des collections instanciées. Pas d'aller-retour glTF |
| Enrichissement three.js sur 3 lieux seulement | Deuxième moteur | Le décor three.js est arrêté ; l'enrichissement se fait dans Blender |
| Véhicules en primitives | Pas de bibliothèque d'assets, construction en code JS | **Asset Library** avec niveaux de détail et gate « aucun héros en primitives » mesuré dans Blender |
| Échec du LookDev | Matières remplacées par des photos, palette perdue, couleurs non calibrées | **LookDev Engine** : la palette d'abord, les textures PBR teintées vers la palette, calibration mesurée contre la référence |
| Pas de preview à jour | Rendu complet coûteux, deux moteurs | Aperçus Blender rapides depuis la même scène ; rendu par tranches avec cache |
| GPU annoncé mais calcul logiciel | Pas de preuve exigée | Render Manager : liste des périphériques Cycles, échantillons `nvidia-smi` pendant le rendu, **échec explicite** s'il n'y a pas de GPU |
| Effet dépendant de l'image précédente | État caché dans le JS | Tout est **précalculé dans le .blend** (images clés, caches de simulation) ; test de déterminisme obligatoire (image seule = image dans la séquence) |
| Tests et gates obsolètes | Pas lancés automatiquement | Gates par phase, lancés par le Production Controller à chaque fin de phase |
| Perte de fichiers à la suppression des pods | Suppression sans vérification | Fait : manifeste avec sha256, `fetch`, `delete` refusé sans copie vérifiée, minuterie qui arrête au lieu de supprimer (13/13 tests). Reste à faire : tester sur un vrai pod |

### 2.4 Capacités mesurées de l'environnement (VÉRIFIÉ le 18/11)

**Local** (conteneur, 4 cœurs CPU, 15 Gio de RAM, pas de GPU) : Blender 5.2.2 LTS fonctionne sans écran.

| Moteur | Image 270×480, scène par défaut |
|---|---|
| EEVEE (OpenGL logiciel) | 15,6 s |
| Cycles CPU, 16 échantillons | 2,3 s |
| Workbench | 0,4 s |

- La physique rigide est précalculée et fonctionne.
- L'outil « Cell Fracture » n'est **pas** fourni avec Blender 5.2 : la fracture sera un module maison (découpe de Voronoï par plans), déterministe.

**Pod RTX 4090** (tâche 003, champ avec 50 720 objets, 540×960, 64 échantillons) :

| Lieu | Cycles OPTIX | EEVEE |
|---|---|---|
| Champ | 125 s | 38,7 s |
| Café | 3,5 s | 1,9 s |
| Route | 4,0 s | 6,1 s |

Ces mesures datent d'avant l'instanciation ; elles sont à refaire sur le prototype.

**Objectif « moins d'une heure pour 2 137 images »** : cela demande en moyenne ≤ 1,68 s par image sur un GPU, ou ≤ 6,7 s par image sur 4 GPU en parallèle. C'est atteignable sur le café et la route avec les mesures actuelles, pas sur le champ tel qu'importé (125 s). C'est donc un objectif à mesurer sur le prototype, pas une promesse.

---

## 3. Architecture cible

```
episodes/<ep>/                         (données d'un film)
  film.json  voice/  sound/            plan, voix, son        (inchangés)
  places/<place>/place.json            NOUVEAU : description du lieu (assets, placements, scatter, palette, lumière)
  out/plan/                            caméra et jeu précalculés (film_plan.py, inchangé)
  out/blend/<place>.blend              scène construite (produit, en cache)
  out/cards/<who>/...                  dessins des personnages (service de cartes, en cache)
  out/render/<take>/f####.png          images rendues (par tranches)

blender/rc/                            NOUVEAU paquet Python Blender (le cœur)
  library.py      B  Asset Library      catalogue, import par lien depuis les .blend d'assets, LOD, variantes
  cache.py        —  cache par contenu  clé sha256(entrées + code + versions) -> sortie ; partagé par tous
  envbuild.py     C  Environment Builder  terrain, architecture, végétation (Geometry Nodes), scatter instancié
  assemble.py     D  Scene Assembly      place.json + caméra précalculée -> scène .blend ; collections normalisées
  characters.py   E  Character Integration  cartes 2D en séquences d'images, ombre, contact, occlusion, éclairage de la carte
  animate.py      F  Animation Engine    jeu précalculé -> images clés ; micro-animations ; vent (Geometry Nodes)
  physics.py      G  Interaction & Physics  3 niveaux ; fracture préparée ; pièces détachables ; précalcul en images clés
  vfx.py          H  VFX Engine          poussière, fumée, étincelles, pluie, débris : précalculés, déterministes
  lookdev.py      I  LookDev Engine      palette d'abord ; PBR teinté ; calibration contre la référence ; préréglages de lumière
  render.py       J  Render Manager      EEVEE / Cycles, tranches, preuve GPU, manifeste
  qa.py           K  Quality Assurance   statistiques de scène (primitives, triangles, instances, textures), déterminisme

tools/production_controller.py     A  Production Controller (étendu) : phases 1 à 12, dépendances, gates, état
tools/card_service.mjs             E  Service de cartes (Chromium) : SVG -> PNG en parallèle, cache par contenu
scripts/runpod/                    J  pods Blender, protection des résultats (fait), preuve GPU
library/assets/<id>/               B  asset.json (métadonnées) + <id>.blend (+ LOD, variantes, pièces) + textures
```

**Règles d'architecture :**
1. **Une seule source pour le monde : Blender.** Le JavaScript ne construit plus de décor. Il ne sert plus qu'à **dessiner les personnages** (SVG vers PNG), où il est irremplaçable et déjà validé.
2. **Tout état animé est précalculé dans le .blend** (images clés, caches) avant le rendu. Le rendu d'une image ne dépend que de son numéro, donc les tranches sont reproductibles.
3. **Toute étape coûteuse passe par `rc_cache`.** Même entrée, pas de recalcul.
4. **Instances partout où un objet se répète** (Geometry Nodes, collections instanciées). Gate : nombre d'objets et ratio instances/objets.
5. **La palette est une donnée.** `place.json` porte la palette validée ; le LookDev la respecte et la mesure.
6. **Aucune étape n'est PASS sans preuve** : image, séquence, mesure, journal ou test.

### 3.1 Interfaces principales
- `place.json` (évolution de `templates/place_library/PLACE_MANIFEST.schema.json`) :
  - `palette` ;
  - `light` (préréglage et surcharges) ;
  - `terrain` ;
  - `assets` : liste de {id, à, rotation, échelle, variante, LOD} ;
  - `scatter` : liste de {asset ou collection, zone, densité, graine, exclusions} ;
  - `interactions` : liste d'événements → physics.py ;
  - `vfx` : liste.
- `library/assets/<id>/asset.json` :
  - id, nom, catégorie, description ;
  - source, licence, auteur, URL ;
  - dimensions en mètres, triangles par LOD, matières, résolution des textures ;
  - dépendances, variantes, pièces détachables, version de Blender ;
  - sha256 des fichiers.
- `rc_cache` : `get_or_build(kind, inputs: dict, build_fn) -> path`. La clé est `sha256(kind + json(inputs) + sha256(code du constructeur) + version de Blender)`. Le cache vit dans `~/.ricksclips/cache` et sur le volume du pod.
- Événement d'interaction (`physics.py`), par exemple :
  `{type: "collision", a: "dozer", b: "cart", at_frame: 120, tier: 3, detach: ["cart_wheel_L"], fracture: {"cart_bed": {pieces: 12, seed: 7}}, damage_shape: "cart_crushed"}`
  donne une simulation, puis un précalcul en images clés et un état final conservé.

### 3.2 Moteur de rendu
La décision se prend par mesure sur le prototype, avec le même plan dans les deux moteurs (EEVEE et Cycles OPTIX) et les mêmes critères : qualité (comparaison à la référence), temps par image, mémoire GPU, compatibilité volumétrique et transparences des cartes.

Pré-hypothèse issue des mesures existantes : Cycles OPTIX est plus rapide sur les lieux légers et l'éclairage indirect est plus juste ; EEVEE est plus rapide sur les scènes très denses. **Non décidé avant mesure.**

---

## 4. Nouveau pipeline (12 phases, livrables et gates)

| # | Phase | Livrable | Gate (preuve) |
|---|---|---|---|
| 1 | Environment build | `out/blend/<place>.blend` construit depuis `place.json` | qa.py : 0 héros en primitives, ratio d'instances, triangles et textures par catégorie ; rendu Workbench et EEVEE de contrôle |
| 2 | Set dressing | `place.json` complet | Densité par cellule d'écran (règle G3 existante) |
| 3 | Camera blocking | Caméra précalculée dans le .blend | Gates de plan existants (`film_plan.py`) ; animatic Workbench |
| 4 | Character integration | Cartes dans la scène | Contact au sol (pieds à moins de 2 cm du sol), ombre présente, échelle |
| 5 | Animation blocking | Images clés du jeu | `anim_audit` (existant) |
| 6 | Interaction system | Simulations précalculées | Le test « état final » diffère de l'état initial ; pièces détachées hors de leur position d'origine ; déterminisme |
| 7 | Animation polish | Micro-animations, vent | Mouvement médian (référence ≥ 18) |
| 8 | VFX | Effets précalculés | Preuve rendue de chaque événement (gate E) |
| 9 | LookDev | Matières et lumière | Dérive de palette, luminosité, saturation et netteté des contours contre la référence ; Material Preview et rendu réel |
| 10 | Validation finale par plan | Image et clip par plan | Validation de l'utilisateur |
| 11 | Rendu GPU | Images par tranches et manifeste | Preuve GPU ; même image quelle que soit la tranche ; fichiers récupérés et vérifiés avant suppression du pod |
| 12 | Post-production | MP4, son, sous-titres | `check_film`, `compare-reference`, gate G |

---

## 5. Stratégie de migration

1. **Ne rien supprimer.** Le pipeline three.js et `from_lock.py` restent utilisables pendant la transition. Les épisodes existants (Ghost Army V3, Le Dernier Phare) restent rendables.
2. **Mission 1, fondations** : paquet `blender/rc/`, avec `cache.py`, `library.py` (+ migration des 4 assets sur mesure et des 3 assets du catalogue), `qa.py` (statistiques de scène), `assemble.py` (lecture de `place.json` et de la caméra précalculée), service de cartes avec cache, Render Manager local, gates Blender dans le contrôleur, tests unitaires. Coût : aucun pod.
3. **Mission 2, prototype** : un lieu de Ghost Army, **le champ**, plus une séquence d'essai de destruction.
   - Pourquoi le champ : le lieu le plus complexe testé (terrain, haies, bocage, véhicules, foule de porteurs, char gonflable), et celui dont l'import échouait (50 656 objets).
   - Contenu :
     - terrain modelé, haies et arbres en vraie géométrie instanciée, ferme ;
     - char gonflable (asset héros) et bulldozer (asset mécanique) ;
     - 2 à 4 personnages (porteurs et Lou) ;
     - l'action « soulever le char » (déjà dans le film), le vent et les micro-animations ;
     - poussière et pétales ;
     - LookDev du matin selon la palette validée ;
     - une caméra cinématographique (station existante).
   - Séquence animée d'environ 150 images (5 s).
   - **Test de destruction mécanique séparé** (environ 90 images) : le bulldozer percute une charrette en bois. Planches fracturées, roue détachée, timon déformé, poussière. Tout est précalculé et vérifié par un rendu dans les deux ordres.
   - Rendu GPU sur RunPod : **nécessite ton autorisation** (coût). Benchmark EEVEE contre Cycles sur ce prototype.
4. **Missions 3 à n** : migration lieu par lieu (`place.json` et assets), du lieu le plus lourd au plus léger : rivière, camp, route, radio, café, photo, chambre, grenier. Chaque lieu est validé par une image de l'utilisateur.
5. **Mission finale** : preview complète, puis rendu final (après accord), puis retrait de la partie décor du pipeline three.js et de `from_lock` (gardés en archive), puis mise à jour des règles et des agents.

**Points de restauration :**
- un commit par module, avec le message « Mission N: … » ;
- un tag local avant chaque mission ;
- l'ancien pipeline reste testé par les tests existants jusqu'à son retrait.

---

## 6. Risques

| Risque | Effet | Parade |
|---|---|---|
| Pas de GPU local | Les aperçus EEVEE sont lents en local (15,6 s pour une petite image) | Workbench et Cycles CPU à basse résolution en local ; EEVEE et Cycles GPU sur pod pour les validations |
| Coût RunPod | Budget | Autorisation pour chaque pod ; coût mesuré et relu sur le solde ; cache sur volume pour ne rien recalculer |
| Licences et refus des sources (Asset Hub refuse le militaire) | Véhicules militaires impossibles à télécharger | Modèles Blender sur mesure (déjà prouvé avec 4 assets) ; métadonnées de licence obligatoires |
| Intégration des cartes 2D dans un éclairage réel | Personnages qui paraissent collés | `characters.py` : ombre de la carte (déjà dans `cards.py`), contact au sol, teinte de la lumière du lieu, occlusion par profondeur réelle |
| Fracture sans Cell Fracture | Module à écrire | Découpe de Voronoï par plans, avec graine fixe ; testé sur le prototype |
| Taille des .blend et des caches | Disque | Cache par contenu avec nettoyage contrôlé (jamais automatique sur un résultat de production) |
| Double maintenance pendant la migration | Dérive | Gel du décor three.js : plus aucune amélioration de décor en JS à partir de la mission 1 |

## 7. Ressources (sans durée inventée)
- **Local (gratuit)** : Blender 5.2.2, 4 cœurs, 15 Gio. Suffisant pour les fondations, les tests unitaires et les rendus de contrôle Workbench et Cycles CPU à basse résolution.
- **RunPod (payant, sur autorisation)** : RTX 4090 à 0,34 $/h (communautaire) ou 0,89 $/h (sécurisé), prix mesurés le 18/11. Usage : benchmark du prototype, rendus de validation, rendu final.
- **Assets** : Poly Haven et ambientCG (CC0, gratuits), Sketchfab et BlenderKit (selon licence, compte de l'utilisateur), modèles sur mesure.

## 8. Protocole de tests et de validation
1. **Tests unitaires** de chaque module `rc` (Blender sans écran), sous `tools/tests/test_rc_*.py` : cache (même clé, pas de reconstruction ; entrée changée, reconstruction), bibliothèque (import par lien, métadonnées valides), qa (comptes exacts sur une scène connue), assemblage (une scène de test produit les collections attendues).
2. **Tests existants** : `test_production_intelligence.py` (11) et `test_pod_guard.py` (13), à chaque mission.
3. **Déterminisme** : pour chaque scène, 3 images rendues seules, puis au sein de leur séquence ; écart attendu de 0 pixel (Cycles avec graine fixe) ou ≤ 0,1 % (EEVEE).
4. **Preuves de phase** : chaque gate de la section 4, avec le fichier de preuve enregistré dans `production/`.
5. **Preuve GPU** : journal Cycles avec le périphérique OPTIX ou CUDA, plus échantillons `nvidia-smi` d'utilisation supérieure à 50 % pendant le rendu. Sinon, FAIL explicite.
6. **Référence** : `compare-reference` sur la séquence du prototype ; les seuils forteresse doivent passer pour accepter le prototype.

## 9. Ordre d'exécution
1. Mission 0 (ce document).
2. Mission 1, fondations : `rc/cache.py` → `rc/library.py` + migration des assets → `rc/qa.py` → `rc/assemble.py` + `place.json` → service de cartes avec cache → `rc/render.py` en local → gates Blender → tests.
3. Mission 2, prototype : le champ, puis l'essai de destruction, puis le LookDev, puis le benchmark GPU (autorisation), puis le rendu de la séquence, puis le rapport.
4. Missions 3 et suivantes : migration lieu par lieu.

## 10. État des travaux interrompus (ancienne mission 1, commit `6b43e9d` et suivant)
- Protection des pods (manifeste, fetch, delete gardé) : **PASS**, 13/13 tests (VÉRIFIÉ). Conservée telle quelle.
- Pods qui publient sur le volume, minuterie qui arrête au lieu de supprimer, archive du verrouillage : écrit, **NOT_RUN** sur un vrai pod.
- Anneaux sonores basés sur la caméra courante, poussière avec graine, variante `--variant enrich` : écrit, **NOT_RUN** (test de reproductibilité interrompu). Ce code three.js reste utile tant que la V3 sert de référence.
- `collapse_instances` dans `from_lock.py` : écrit, **NOT_RUN**. Il ne sert qu'au chemin de migration ; il devient secondaire, puisque les décors seront construits nativement dans Blender.
- Mémoire de production (`STATE.md`, problèmes ouverts, journal QA, 7 leçons) : **NOT_RUN**. Elle sera faite au début de la mission 1.
