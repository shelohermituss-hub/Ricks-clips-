# Audit technique — RicksClips Skill V1.1

**Date de l’audit et du patch : 16 novembre 2026**  
**Périmètre :** les trois archives fournies par l’utilisateur, fusionnées sous `RicksClips_Skill_V1.1`.  
**Statut :** audit statique terminé; correctifs de maintenance ciblés appliqués; validation visuelle GPU non effectuée.

## 1. Fusion et inventaire

Les trois ZIP sources ont été fusionnés sans collision de chemins. Les archives sources ont été conservées intactes. Le paquet fusionné corrigé contient 853 fichiers, rapport d’audit inclus (environ 171,8 MB décompressés); le skill et ses ressources représentent 852 fichiers avant ajout du rapport :

| Zone | Contenu vérifié |
|---|---:|
| `agents/` | 16 agents spécialisés + brief du stretch builder |
| `rules/dept/` | 16 slices de département, plus `lead`, `stretch-builder` et l’index |
| `templates/` | 525 fichiers : film kit Three.js, personnages vectoriels, look kit, poses et mouvements |
| `tools/` | 153 scripts après ajout du contrôle de livraison |
| `references/` | 47 fichiers |
| `examples/lightning-spear/` | 39 fichiers de documentation et de code; pas de vidéo ni d’audio |
| `templates/motion_styles/moves/` | 48 modules de mouvement |

Les trois archives contenaient respectivement 640, 182 et 36 entrées ZIP. Les chemins de fichiers réels se sont combinés sans doublons.

## 2. Architecture réelle

### Film et environnements

Le rendu du film repose sur `templates/threejs_film/`. Le monde, les décors, la caméra et les effets sont réalisés en Three.js. Les personnages sont des marionnettes vectorielles 2D placées à une profondeur réelle dans cet environnement 3D.

Le point d’entrée de rendu GPU est `templates/threejs_film/render_gpu.mjs`. `film.js` appelle les fonctions de `look3d.mjs`. Le kit `kit3d` apporte quatre familles de fonctions :

- matériaux PBR pour les métaux et surfaces mouillées;
- relief et variations de surface pour pierre, brique, pavés, bois, boue, écorce et herbe;
- ciel et nuages multicouches, avec variantes d’orage et flash;
- arbres avec troncs ramifiés, cartes de feuillage instanciées et mouvement léger.

**Découverte importante :** le moteur garde `kit3d` désactivé par défaut pour préserver la compatibilité des anciens films. Le modèle de nouveau film n’activait pas cette option. Les nouveaux projets pouvaient donc hériter du rendu simplifié sans demander explicitement le kit de réalisme.

### Personnages et mouvements

Le pont de mouvements existe déjà dans le code :

- `templates/motion_styles/library.mjs` : registre des styles et sélecteur;
- `templates/motion_styles/moves/*.mjs` : modules des actions;
- `templates/motion_styles/rig.mjs` et `cloth_live.mjs` : calcul du corps et suivi des vêtements;
- `templates/threejs_film/render_gpu.mjs` : copie ces modules dans son cache privé;
- `templates/threejs_film/puppets.mjs` : interprète les poses `m:<id>` par le registre `LIB`.

Il y a 48 modules dans la bibliothèque. Le moteur standard ne charge pas les chemins arbitraires de mouvements placés dans un dossier d’épisode. Plusieurs règles et briefs mentionnaient pourtant d’anciens fichiers de motion studio qui ne sont pas livrés. C’était une contradiction directe entre documentation et code.

### Blender

Les dossiers `templates/blender_look/` et `templates/blender_cine/` conservent des outils et méthodes utiles. Toutefois, le flux V1.1 courant est Three.js-first et le livre de règles indique que Blender n’est utilisé que pour des couches spécifiques lorsqu’elles sont demandées. Les documents plus anciens pouvaient encore faire croire que le monde complet devait obligatoirement être construit et fini dans Blender.

## 3. Défauts détectés et correctifs appliqués

### A. Cohérence des règles et installation

**Défauts constatés**

- `CB_RULES.md` à la racine et `rules/CB_RULES.md` divergeaient : la copie lue par les sessions cloud ne contenait pas les dernières règles du maître.
- `tools/slice_rules.py` générait les tranches de départements, mais ne synchronisait pas la copie `rules/CB_RULES.md`.
- `install.py` installait sous `~/.claude/skills/ricks-clips-v1-1/`, tandis que `tools/refresh_installed_skill.py` visait l’ancien dossier `cartoon-3d-short`.
- La logique d’installation et de rafraîchissement était dupliquée, donc susceptible de diverger.

**Correctifs**

- `tools/slice_rules.py` copie désormais le livre maître vers `rules/CB_RULES.md` avant de régénérer les slices et l’index.
- `install.py` régénère les règles et les slices avant installation.
- `tools/refresh_installed_skill.py` délègue maintenant à `install.py`; il n’existe plus deux chemins concurrents d’installation.
- Les slices ont été régénérées à la date du patch. Les deux fichiers `CB_RULES.md` ont le même SHA-256 et sont identiques octet par octet.

### B. Contrôle des vues de personnages

**Défaut constaté**

`tools/check_views.mjs` ignorait les personnages dont le module source était absent, puis pouvait annoncer `PASS` en ne vérifiant que les autres. Le manifeste `templates/vector2d_characters/views_golden/rows.json` contient 11 personnages, mais 7 entrées s’appuient sur 4 fichiers source non présents dans ces archives :

- `episodes/baboon-signalman/cast/sheets/jack.mjs`
- `episodes/goldrush/cast/sheets/goldrush.mjs`
- `episodes/goldrush/cast/sheets/goldrush2.mjs`
- `episodes/goldrush/cast/sheets/goldrush_today.mjs`

Les images de référence approuvées ne remplacent pas les modules source nécessaires pour redessiner et comparer les vues.

**Correctif**

Le contrôle signale désormais les sources manquantes comme des échecs. Le mode `--update` refuse de remplacer les images approuvées tant que toutes les sources requises ne sont pas présentes. Aucun module de personnage absent n’a été inventé.

### C. Mouvements : documentation et runtime

**Défauts constatés**

Les fichiers `agents/animator.md` et `CB_RULES.md` renvoyaient vers `studio-motion/STUDIO_MOTION.md`, `templates/motion_styles/studio.mjs`, `check_motion.mjs`, `check_motion_ep.mjs`, des dossiers cloud et une syntaxe de chargement de mouvements spécifiques à un épisode. Ces éléments ne font pas partie de la livraison et ne sont pas chargés par le renderer standard.

Le pont réel `m:<id>` vers la bibliothèque centrale est, lui, déjà intégré. Les scripts disponibles vérifient certains aspects du plan et du film rendu, mais il n’y a pas de gate automatisé complet pour IK, contacts, interpolation du corps et glissement des pieds.

**Correctifs**

- Le livre maître indique maintenant la véritable chaîne d’exécution et les chemins pris en charge.
- Les mouvements supplémentaires doivent être ajoutés sous `templates/motion_styles/moves/` puis enregistrés dans `library.mjs`.
- La séquence artistique anticipation/action/réaction/settle reste une consigne de chorégraphie, mais n’est plus décrite comme un moteur externe absent.
- L’agent animateur distingue les contrôles automatiques disponibles des vérifications manuelles nécessaires.

### D. Réalisme des environnements

**Défaut constaté**

`kit3d` était désactivé par défaut et le modèle `templates/film_example/film.json` ne l’activait pas. Cela pouvait produire un film avec des matériaux de type toon simplifiés, un ciel standard et des arbres simplifiés, même si la bibliothèque de réalisme était présente.

**Correctif**

Le modèle des nouveaux films active maintenant `"kit3d": true`. Les films existants ne sont pas modifiés. Le renderer reste compatible avec les anciens films sans option `kit3d`.

**Limites du kit à garder visibles**

Le propre document `templates/threejs_film/PBR_FEATURES.md` note encore des nuages un peu trop lisses/simples, des détails de ciel d’orage qui ne sont pas toujours assez lisibles, et des limites de masque lorsque des cartes de feuilles passent devant un personnage. Le `CHANGELOG.md` signale aussi un ciel d’orage qui devient noir avec une longue focale. Ce sont des points ouverts, pas des problèmes que le patch a prétendu résoudre.

Le rapport de test PBR fourni dans le ZIP indique un temps de rendu de l’image de test d’environ 840 à 967 ms avec `kit3d`, contre 248 ms sans le kit, sur la scène d’essai et la configuration mentionnées dans le document. Ce chiffre n’est pas une mesure de performance de tous les films.

### E. Qualité cinématique et livraison

**Défaut constaté**

Le projet mentionne une sortie verticale 1080×1920 à 30 fps, mais il n’y avait pas un contrôle de livraison autonome et simple pour vérifier ces métadonnées du MP4 final.

**Correctif**

Ajout de `tools/check_delivery.py`. Par défaut, il vérifie la présence d’une vidéo, la résolution 1080×1920, 30 fps et une durée positive avec `ffprobe`. L’option `--require-audio` peut exiger une piste audio. Ce contrôle ne juge pas la qualité des images, la continuité, le mix ou la synchronisation; il complète ces inspections, sans les remplacer.

### F. Ordre de travail et documentation ancienne

`SKILL.md` et `WORKFLOW.md` conservaient des formulations plus anciennes qui semblaient concurrencer le flux lean de V1.1. Une note de priorité a été ajoutée : `CB_RULES.md` et `START_HERE.md` définissent le flux courant; l’ancien workflow détaillé demeure comme référence de savoir-faire, pas comme une obligation de relancer le pipeline Blender complet.

## 4. Vérifications exécutées

| Vérification | Résultat |
|---|---:|
| Scripts Python analysés par AST | 82 — 0 erreur |
| Fichiers JavaScript / MJS vérifiés avec `node --check` | 199 — 0 erreur |
| Fichiers JSON analysés | 60 — 0 erreur |
| Génération des slices | 18 fichiers générés |
| Copie maître `CB_RULES.md` / `rules/CB_RULES.md` | Identiques, SHA-256 identique |
| Syntaxe de `tools/check_views.mjs` | OK |
| Aide CLI de `tools/check_delivery.py` | OK |

Aucun installateur n’a été exécuté sur le profil Claude de l’utilisateur. Aucun `npm install`, rendu Blender ou rendu vidéo GPU n’a été lancé pendant cet audit.

## 5. Ce qui reste à faire sur la machine de rendu

1. Fournir les quatre modules de cast listés en section 3B pour que les 11 personnages approuvés puissent réellement passer le contrôle de vues.
2. Sur la machine cible Windows/NVIDIA, lancer `node templates/threejs_film/render_gpu.mjs <film.json> --gpu-info`, puis faire un rendu test avec `--frames` et `--scale 1`; comparer avec le mode `--software` lorsque nécessaire.
3. Vérifier les ciels d’orage avec longue focale, les arbres placés devant les personnages, les reflets et le coût GPU sur un vrai film.
4. Compléter la gate de mouvement si un contrôle automatique complet des contacts, glissements, IK et transitions est souhaité. En attendant, conserver l’inspection manuelle en animation.
5. Après export final, lancer `python tools/check_delivery.py <final.mp4>` puis effectuer séparément le contrôle visuel, la continuité et l’écoute du mix.

## 6. Fichiers modifiés dans le patch

- `CB_RULES.md`
- `rules/CB_RULES.md` et les fichiers générés de `rules/dept/`
- `tools/slice_rules.py`
- `tools/refresh_installed_skill.py`
- `tools/check_views.mjs`
- `tools/check_delivery.py` (nouveau)
- `install.py`
- `agents/animator.md`
- `SKILL.md`
- `WORKFLOW.md`
- `templates/film_example/film.json`
- `templates/threejs_film/README.md`
- `templates/motion_styles/README.md`
- `START_HERE.md`
- `INSTALL.md`
- `CHANGELOG.md`

**Aucun code de la bibliothèque de personnages verrouillée, des images approuvées, ou des modules de mouvement existants n’a été modifié.** Les ZIP d’origine demeurent inchangés. Le ZIP de base fusionné non patché est fourni séparément pour revenir à l’état initial.
