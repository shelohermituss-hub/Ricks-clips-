# Plan de production — à écrire EN ENTIER avant de construire quoi que ce soit

Règle de CB, 19/11 : « avant de commencer à construire tu fais un plan ultra détaillé et précis de tout ce dont tu as besoin… tu dois tout écrire avant de commencer ».

**Deux fichiers par vidéo**, dans `episodes/<nom>/plan/` (ou `demos/<nom>/plan/`) :

1. **`plan.json`** : la version que les outils lisent. Format : `plan_example.json`, le plan 2 de crashed_car, rempli.
   - `python3 tools/plan_check.py plan.json` doit dire **PLAN PASS** avant la première ligne de construction.
   - Un WARN reste permis seulement avec sa raison écrite dans le plan (champ `notes`).
2. **`PLAN.md`** : la même chose en clair pour CB, avec les sections ci-dessous. Une section par plan (shot), chacune avec ses sous-sections 4 à 12.

Rien n'est construit tant que le plan n'a pas PASS.

## 1. Histoire et voix
- Le script complet, avec les secondes de chaque ligne.
- Le nombre de mots et le débit : 3,3 à 3,6 mots/s.
- Les mots clés sur lesquels tombent les actions.

## 2. Style
- La bible suivie (`references/STYLE_BIBLE_FR.md`).
- Tout écart voulu, avec sa raison.

## 3. Liste des besoins, avant tout
Personnages, objets, décors, textures, HDRI, sons. Pour chacun :
- sa **source** :
  - un asset existant de `library/assets/catalog.json` ;
  - un asset à télécharger (Sketchfab, Poly Haven, ambientCG), avec sa licence ;
  - ou un asset à construire par script ;
- son **état** : déjà là, à télécharger, ou à construire.

Les téléchargements sont faits au début, en une fois.

## 4. Environnement (par lieu)
- **Sol et grandes surfaces** : texture réelle (`polyhaven:<id>`, avec répétition, teinte, valeur), plus l'usure, les taches et les traces.
- **Décor**, du premier plan au fond : chaque élément avec sa source. Au moins 4 accessoires qui racontent le lieu.
- **Ciel** : dégradé, nuages, HDRI de reflets.
- **Lumière** :
  - soleil : élévation, azimut, énergie, angle ;
  - ciel d'appoint ;
  - lumières pratiques (lampes, néons).
- **Ombres** : quelles structures projettent quelles ombres, et où, dans le cadre.

## 5. Objets
Pour chaque objet :
- sa source ;
- son matériau : peinture vernie, métal, bois, verre ;
- ses **états possibles** : propre, mouillé, sale, enfoncé, cassé, ouvert ;
- les pièces qui peuvent se détacher.

## 6. Personnages
- Le personnage de la distribution et son costume.
- Ses objets tenus en 3D.
- Sa **vue unique** pour tout le plan.
- Son trajet au sol.

## 7. Actions (le cœur du plan)
Pour chaque action :
- **qui**, et les **images** de début et de fin ;
- le **mot** de la narration sur lequel elle tombe ;
- l'**animation** : mouvement de la bibliothèque, trajectoire, poids ;
- les **micro-animations** : respiration, vibration, objet qui oscille, cheveux ;
- les **réactions** : ce que l'action provoque tout de suite (éclaboussure, poussière, débris, secousse, foule) ;
- les **conséquences** qui **restent** : mouillé, cassé, enfoncé, traces, objet déplacé ;
- **`persists`** : où la conséquence se voit encore (ids des plans suivants, `next_shot` ou `end`) — contrôlé par `plan_check` STYLE5 (5 vidéos de référence : chaque trace reste) ;
- **`sign`** pour une émotion extrême (rage, panique, hypnose, cupidité, choc) : éclairs, yeux lumineux, spirales, yeux en $, aura, sueur, gribouillis ;
- les **bruitages**.

Chaque action est rapprochée de sa recette dans `library/reactions/reactions.json`. Si aucune ne convient, on en écrit une nouvelle après la construction.

## 8. Entrées, sorties et changements d'état
Pour chaque personnage et chaque objet : **par quelle action** il entre, sort ou change, image par image. Jamais d'apparition ni de téléportation.

## 9. Caméra
- Les clés : temps, position, visée, focale, et le **nom du mouvement**.
- Elle ne s'arrête jamais, avec en plus une dérive façon caméra à l'épaule.
- Ce qu'elle suit.
- Les transitions d'entrée et de sortie, avec leur **type** : traversée d'un objet (porte, écran, vitre), fouetté de 3 images, fondu de 0,3 s, ou coupe (réservée à l'accélération : `accelerate: true`). Une vidéo complète a **au moins 4 ambiances de lumière** (champ `mood` des plans). Voir `references/style_analysis/`.

## 10. Effets visuels
- Chaque effet, avec l'action qui le déclenche.
- Ses images de début et de fin.
- Sa couche de rendu (FX).

## 11. Son
- L'ambiance du lieu.
- La musique.
- Un bruitage pour chaque action et chaque réaction.
- Le mixage à −14 LUFS.

## 12. Couches de rendu et points de contrôle
- Le contenu de chaque couche : SKY, SET, OBJECTS, FX.
- Les images clés à vérifier avant le rendu complet.

## 13. Leçons appliquées
Chaque leçon validée de `memory/lessons_learned.json` qui s'applique, avec la façon dont le plan l'évite. `plan_check.py` les liste.

## 14. Risques connus
Ce qui pourrait mal tourner, et la parade prévue.

## 15. Champs « histoire » de `plan.json`

Ajoutés le 19/11 à partir des 7 vidéos de référence (`references/ANALYSE_7_VIDEOS_FR.md`). `plan_check.py` les exige pour une vidéo entière (`"kind": "video"`) ; un fragment (`"kind": "fragment"`) ne reçoit que des avertissements.

- **`hook`** : `{"action": "<id>", "t": 0.0}`. La première action surprenante doit être **montrée dans la première seconde**.
- **`facts`** : `[{"fact": "DAYS SINCE LAST CRASH 7", "shot": "s03", "prop": "panneau au bord de la route"}]`. Chaque nombre ou nom de la narration est écrit **dans le décor** : panneau, journal, étiquette, écran, caisse.
- **`captions`** : `{"words": [1, 3], "style": "white bold rounded, thick black outline, 70 % height"}`.
- **`mood`**, par lieu (`light.mood`) ou par plan : au moins **2 ambiances** (jour, crépuscule, nuit, orage, intérieur chaud, souvenir en noir et blanc).
- **`shot_type`**, par plan, ou **`framing`**, par clé de caméra :
  - `close` ou `extreme_close` : au moins un gros plan d'émotion ;
  - `insert` : au moins un détail de l'objet du récit, souvent vu de dessus ;
  - `pov` : subjectif ;
  - `aerial`, `wide`.
- **`loop`** : la dernière image renvoie à la première. Recommandé ; son absence donne un avertissement.
