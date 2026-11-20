# Spécification du système de production RicksClips (sans code, sans modification du pipeline)

Chaque module dit ce qu'il reçoit, ce qu'il produit, quelle règle de la bible il applique et quel contrôle le vérifie. Les noms d'outils existants sont cités quand ils couvrent déjà une partie. Rien n'a été codé ni modifié pendant cette mission.

## Ordre de fabrication
Script → voix minutée → **A** Style Director → **B/C/D/E/F/G** en parallèle sur le plan → contrôle (`plan_check`) → construction Blender par plan → contrôle (`continuity`) → images clés → mesure d'étalonnage → aperçu → **H** rendu → son et montage.

## A. Style Director
- **Entrée** : script, mots minutés, sujet.
- **Sortie** : `style.json` avec la structure choisie (linéaire, anthologie datée, lieu-compteur), le nombre de lieux, une ambiance de lumière par étape (au moins 4), le niveau de saturation visé (plage 0,28-0,44 selon le ton), le rythme visé (durée médiane des plans de 2,6 à 4,7 s), et la liste des objets plantés et payés.
- **Règles** : bible §2 (C1-C14) et §3 (variantes).
- **Contrôle** : `plan_check` STYLE et STORY (existant, à étendre aux ambiances et aux objets plantés).

## B. Character System
- **Entrée** : rôles du script.
- **Sortie** : par personnage, design original (tête blanche, traits, 2-3 accessoires de rôle), costumes par époque, une vue, bibliothèque d'expressions et de signes 2D, mouvements, cycle de repos lié à l'objet tenu, réactions de témoin.
- **Règles** : `CHARACTER_DESIGN_AND_ANIMATION.md`.
- **Existant** : `card_service.py`, `card_anchors.py`, distribution des 150 personnages.
- **Contrôle** : `continuity` POSE_POP ; expression sur le mot (à ajouter).

## C. Environment System
- **Entrée** : lieux et étapes.
- **Sortie** : décors continus (traversables d'un lieu à l'autre si la caméra passe), trois couches de profondeur, assets classés (héros avec états, secondaires, dressing, fond), textes diégétiques, objets ajoutés par les conséquences, LOD.
- **Règles** : `ENVIRONMENT_AND_ASSET_BIBLE.md`.
- **Existant** : `rc/look.py`, `asset_hub.py`, `rc.geo`.
- **Contrôle** : `plan_check` PLACES et LOOK.

## D. Camera System
- **Entrée** : plans, mots-clés.
- **Sortie** : pour chaque plan, recette de caméra (`CAMERA_AND_EDITING_LANGUAGE.md` §3), mouvements avec début, fin, durée et easing, transition de sortie (objet traversé, fouetté de 3 images, fondu de 0,3 s, coupe réservée à l'accélération), tremblement aux impacts.
- **Existant** : `street.handheld`, `film_plan.py`.
- **Contrôle** : `continuity` HOLD ; vérification « transition déclarée ».

## E. Lighting & Color System
- **Entrée** : ambiances par étape.
- **Sortie** : soleil unique placé par vue (lumière refaite cachée dans les transitions), ciel, rayons, nuit = monde bleu + sources chaudes, accent rouge, étalonnage par plan (désaturé, noir et blanc, doré selon l'émotion).
- **Règles** : `LIGHTING_COLOR_AND_MATERIAL_BIBLE.md`.
- **Existant** : `rc/look.py` (`sky_hdri`, `sun`, `relight`, `sun_glow`, `tex`), `grade_match.py`.
- **Contrôle** : `grade_match` par plan contre la plage choisie.

## F. Animation & Interaction System
- **Entrée** : actions du script.
- **Sortie** : pour chaque action, chaîne en 9 étapes (`INTERACTION_AND_PHYSICS_LANGUAGE.md` §1) avec durées, conséquences persistantes enregistrées et reprises dans les plans suivants, réactions des témoins.
- **Existant** : `library/reactions/reactions.json`, `rc.physics`.
- **Contrôle** : `plan_check` ACTIONS ; vérification de la persistance d'un plan à l'autre (à ajouter).

## G. VFX System
- **Entrée** : événements.
- **Sortie** : effets 2D (signes) et 3D (matière) avec naissance sur l'image du contact, durée, persistance, couche FX.
- **Règles** : `VFX_AND_COMPOSITING_BIBLE.md`.
- **Existant** : `rc.vfx`, `layers.py`.
- **Contrôle** : `continuity` FX (naissance autorisée et déclarée).

## H. Render & Performance System
- **Choix du moteur par benchmark à scène identique** : même plan, même résolution, mêmes images clés.
  1. Rendre avec **EEVEE Next** puis avec **Cycles**.
  2. Mesurer : temps par image, mémoire, et écart d'étalonnage (`grade_match`) avec la référence.
  3. Juger à l'œil côte à côte les ombres, la transparence (vitres), le volumétrique (rayons) et l'émission.
  4. Le moteur n'est choisi qu'avec ces chiffres. Ne pas choisir Cycles par réputation.
- **Référence historique de CB** : l'ancien flux EEVEE prenait 20-30 min. C'est à revérifier sur un projet comparable, ce n'est pas une garantie.
- **Mesure déjà notée dans ce dépôt** (`HANDOFF.md` §6, `DECISIONS.md`) : EEVEE environ 10 % plus rapide que Cycles, « pour une qualité moindre ». Les conditions de cette mesure ne sont pas reprises ici : à refaire sur un plan de style RicksClips actuel.
- **Contenu** : ombres, transparence, volumes, instances (foule, herbe), LOD, cache, rendu par couches et par lots, preuve d'utilisation du GPU, temps par image.
- **Existant** : `render_manager.py`, `layers.py`, `scripts/runpod/pod.py`, `preview.sh`.
- **Contrôle** : manifeste de rendu, preuve GPU, coût plafonné par CB.

## Responsabilités
Les agents existants du dépôt (`.claude/agents`) couvrent déjà ces modules :

| Module | Agent(s) |
|---|---|
| A | writer, camera-director |
| B | character-artist, animator |
| C | set-builder, 3d-designer, background-painter, props-hero |
| D | camera-director |
| E | lighting-director, look-finisher |
| F | animator, props-hero |
| G | vfx-artist |
| Son | sound-designer |
| Montage | editor-compositor |
| Contrôle | production-controller, storyboard-judge, studio-director |
