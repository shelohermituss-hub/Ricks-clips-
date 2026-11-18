# Ghost Army comparée à la référence forteresse : écarts et plan de correction (mis à jour le 2026-11-18 avec la preview v2)

**Référence :** `references/REFERENCE_LOOK_BIBLE.md` v2.0 OFFICIELLE. Captures dans `references/fortress/`, cibles chiffrées dans `production/config/reference_standard.json`.

**Mesure :** `tools/production_controller.py compare-reference`. Le même code mesure la référence (elle passe les 10 seuils, voir `references/fortress/reference_compare_self.json`) et chaque version du film.

Aucun élément n'est déclaré conforme ici sans mesure ET image. Une métrique seule ne prouve jamais la qualité esthétique (voir §0.4).

Échelle de gravité :
- **Critique** : empêche d'atteindre la référence.
- **Important** : visible pour un spectateur attentif.
- **Mineur** : finition.

---
## 0. Étape 0 — preview v2 : mesure de l'état réel (2026-11-18)

### 0.1 Ce qui a été rendu, sans rien modifier
- **Version du projet :** commit `b060146`, arbre de travail propre. Aucun fichier de scène, d'animation, d'asset, de montage ou de son modifié.
- **Empreintes des fichiers d'entrée** (16 premiers caractères du sha256) :
  - `film.json` : 3c3548a239cc692d ;
  - `sets/ghost.js` : 86c065bdb9032ac5 ;
  - `sound/mix.wav` : b2078781308cd90c ;
  - `grade/grade.json` : 13d74eb0b93c265d.
- **Rendu :** les 2 137 images, 540×960 (demi-résolution), avec `render_gpu.mjs --scale 0.5` en 3 tranches parallèles (WebGL logiciel, 1 h 01 au total) ; 0 image manquante.
- **Deux montages,** tous deux avec le mixage son existant (`mix.wav`, inchangé) :
  - `v2/ghost_army_preview_v2_raw.mp4` : sans étalonnage, comme la v1, pour une comparaison juste ;
  - `v2/ghost_army_preview_v2_graded.mp4` : avec `grade.py apply` et sa calibration existante, ni recalibrée ni modifiée (journal : `grade/grade_log.json`, 2 137 images).
- **Durée :** 71,23 s, identique à la v1.
- **Preuves conservées :**
  - planche forteresse / v1 / v2 : `references/fortress/compare_ghost_army_v2_2026-11-18.jpg` ;
  - planche 1 image par seconde : `v2/review/v2_overview_1fps.jpg` ;
  - bandes continues : `v2/review/v2_clip_hook_lift_f0-150.jpg`, `v2_clip_river_f1400-1580.jpg`, `v2_clip_strike_f1670-1845.jpg` ;
  - mesures : `production/REFERENCE_COMPARE_{v1,v2_raw,v2_graded}.json/md` et `REFERENCE_COMPARE_by_take.json`.
- **Fenêtres « nuit » mesurées** (identiques pour les trois versions) : route 26,4-34,0 ; rivière 46,7-52,7 ; frappe 55,7-61,5 ; chambre 61,5-66,4.

### 0.2 Indicateurs globaux

| Mesure | Forteresse | v1 (brute) | v2 brute | v2 étalonnée | Seuil |
|---|---|---|---|---|---|
| Détail d'image | 0.095 | 0.047 | 0.051 | **0.053** FAIL | ≥ 0.075 |
| Luminance jour | 0.433 | 0.331 | 0.342 | **0.414** PASS | 0.36-0.50 |
| Luminance nuit | — | 0.150 | 0.187 | **0.309** PASS | ≥ 0.25 |
| Noirs bouchés | 0.07 % | 6.5 % | 2.0 % | **0.09 %** PASS | ≤ 1 % |
| Hautes lumières brûlées | 0.55 % | 0.1 % | 0.09 % | **0.02 %** PASS | ≤ 1,5 % |
| Saturation | 0.40 | 0.72 | 0.68 | **0.57** FAIL | 0.32-0.52 |
| Secondes au-dessus de 0.60 de saturation | 0 | 69 | 60 | **27** FAIL | 0 |
| Images figées | 0 % | 5.3 % | **0.8 %** PASS | 0.4 % (*) | ≤ 2 % |
| Mouvement médian ×1000 | 35.9 | 8.1 | 8.4 | **9.8** (*) FAIL | ≥ 18 |
| Pics de rythme / 10 s | 10.5 | 5.05 | 5.19 | **5.62** FAIL | ≥ 6 |
| Coupes franches | 0 | 9 | 10 | 9 (**) WARN | 0 non justifiée |

(*) et (**) : voir §0.4, ces valeurs sont en partie faussées par la mesure.

**Bilan :**
- La v2 étalonnée passe **5 seuils sur 10**, contre 1 pour la v1.
- Les gains viennent surtout de l'exposition. L'étalonnage existant y contribue nettement ; les corrections de décor (nuit, intérieurs) aussi, comme le montre la v2 brute.
- Le détail, la saturation, la vie de la caméra, le rythme et les raccords restent loin de la référence.

### 0.3 Par plan (v1 → v2 brute → v2 étalonnée) et vérification sur les images
Mesures dans `REFERENCE_COMPARE_by_take.json`. Les observations viennent de la planche 1 image par seconde, de la planche comparative et des bandes.

| Prise | Luma | Sat | Bouché | Mouv. | Détail | Ce que montrent les images v2 |
|---|---|---|---|---|---|---|
| t_hook 0-10,6 | .30→.30→.41 | .75→.76→.69 | 3,1→3,4→0,1 % | 18→17→18 | .046→.049→.051 | Char porté puis posé sur ses porteurs aux flancs (bande : correct). **Char toujours en primitives** (inventaire : 71 pièces, 5 616 tris, 96 % de générateurs primitifs). Vélos toujours en 2D plat. Les brins d'herbe se lisent comme des bâtons verts verticaux. Sol lisse. Arbres en boules low-poly. |
| t_camp 10,6-26,4 | .36→.37→.43 | .66→.66→.57 | ≈0 | 22→20→20 | .057→.060→.060 | Props de camp détaillés (compresseurs, table, bulldozer), haies et fleurs présentes. Lointain réduit à une rangée d'arbres et quelques maisons : pas de patchwork ni de brume. Leurres peu visibles. Le sol flou à 12-15 s vient du flou de mouvement de l'étalonnage pendant le mouvement de grue. |
| t_road 26,4-34 | .09→.14→**.30** | .82→.77→.66 | **39,6→6,8→0,3 %** | 17→16→19 | .034→.040→.050 | **Le noir illisible est corrigé :** nuit bleue lisible, pavés, haut-parleur en pavillon et ondes, lampe. Reste : un ciel aux nuages roses peu crédible la nuit, des arbres en cônes lisses, une route vide, ni pluie ni flaques. |
| t_radio 34-38,7 | .35→.35→.38 | .82→.83→.64 | 0 | 15→16→14 | .050→.056→.055 | Peu d'évolution : murs de toile unis, caisses, caméra presque fixe. |
| t_cafe 38,7-42,8 | .48→.45→.45 | .69→.70→.55 | 0 | 22→37→32 | .063→.076→.073 | **Nettement mieux :** étagères garnies, poutres, papier peint, lambris, reflet sur le comptoir. Meilleur détail du film. |
| t_sergeant 42,8-46,7 | .45→.40→.42 | .70→.70→.56 | 0 | 26→19→19 | .058→.068→.066 | Mieux habillé. Une coupe sèche, ajoutée par la note v1 sur le bord du cadre, n'est pas encore notée dans DECISIONS. |
| t_river 46,7-52,7 | .17→.19→.33 | .65→.61→.50 | 1,4→0,8→0,1 % | 16→17→18 | .041→.042→.045 | Plaine de nuit, lampadaire et leurres lisibles. Eau et berges correctes en plan large (57-60 s). Sol et ciel restent pauvres en détail. |
| t_photo 52,7-55,7 | .16→.22→.31 | .55→.46→.44 | 9,2→8,5→0,4 % | 10→14→14 | .041→.053→.055 | **Mieux :** mur de briques, suspension, comptoir. Toujours pas d'insert sur les photos. |
| t_strike 55,7-61,5 | .19→.16→.30 | .71→.72→.58 | ≈0,7→0 % | 23→23→25 | .035→.032→.035 | **Explosion encore insuffisante** (bande 56,3-57,1 s) : sphères orange translucides, puis un flash blanc en disque qui couvre un quart de l'image (proche d'un voile blanc). Pas de champignon, de débris lisibles, ni de fumée qui reste. Les rides sur l'eau se lisent en cercles graphiques. Détail le plus bas du film. |
| t_bed 61,5-66,4 | .18→.29→.31 | .73→.36→.37 | 0 | 9→13→12 | .028→.051→.050 | **Grosse amélioration :** vrai lit avec édredon à carreaux, papier peint, fenêtre avec l'enfant. Pièce encore nue (peu d'objets) et caméra lente. |
| t_attic 66,4-71,2 | .18→.29→.44 | .77→.70→.52 | **11,9→0,9→0 %** | 20→12→13 | **.050→.039→.037** | Plus de noirs bouchés. **Régression :** le rayon de lumière ajouté remplit le cadre d'un voile beige laiteux. Le contraste et le détail baissent, le vieux Lou et l'enfant sont délavés. À corriger. |

### 0.4 Métriques à prendre avec prudence (faux positifs possibles)
- **Le grain gonfle le mouvement et efface les images figées.** L'étalonnage ajoute un grain (σ 0.010) différent à chaque image.
  - Réduit à 90×160, il produit à lui seul une différence d'environ 1,5-2 (×1000) entre deux images, juste au-dessous du seuil « image figée » (2).
  - Résultat : en v2 étalonnée, le mouvement passe de 8,4 à 9,8 et les images figées de 0,8 % à 0,4 % **sans que la caméra bouge davantage**.
  - Il faut juger la vie de la caméra sur la version **brute**.
  - À corriger dans l'outil : mesurer avant le grain, ou filtrer le bruit.
- **Le flou de mouvement de l'étalonnage** (filés pendant les mouvements rapides) baisse le détail mesuré sur ces images, alors qu'il est voulu.
- **Le détail d'image mesure les contrastes de bord, pas la qualité de modélisation.** Un char en primitives, bien éclairé et à arêtes nettes, sort autant d'arêtes qu'un modèle riche. Le grain, les sous-titres et les petits objets sombres sur fond clair font aussi monter la valeur. La qualité des modèles se juge par l'inventaire (gate B) et les gros plans, pas par ce chiffre.
- **L'exposition peut passer « grâce à l'étalonnage seul ».** La v2 étalonnée passe la nuit et les noirs bouchés, mais le grenier montre qu'une image claire peut être délavée. Luma en PASS ne veut pas dire image réussie.
- **Les coupes franches :**
  - le détecteur a manqué la coupe crochet → camp (10,6 s) dans la version étalonnée, parce que les deux plans ont la même luminance après étalonnage : c'est un faux négatif ;
  - il compte la coupe vers le sergent (42,8 s), voulue (note v1) mais pas encore notée dans DECISIONS.

  La liste fiable des raccords vient de `out/plan/camera_baked.json` : 10 changements de prise, tous des coupes sèches.
- **La saturation moyenne** inclut les sous-titres blancs et les ciels. Elle indique une tendance, pas le rendu d'une couleur précise.
- **Résolution :** la v1 est en 1080×1920 (agrandie), la v2 en 540×960. Les mesures se font à 90×160, donc l'écart est faible, mais le détail de la v2 peut être très légèrement sous-estimé.

### 0.5 Anciens défauts : résolus, partiellement résolus, toujours présents (vérifiés sur images)

**Résolus**
- Route de nuit noire et illisible : 39,6 % → 0,3 % de noirs bouchés, luma 0,30 ; vérifié sur la planche.
- Noirs bouchés dans le grenier et la photo : 11,9 % et 9,2 % → 0 % et 0,4 %.
- Chambre en boîte bleue unie : vrai lit, édredon, papier peint, fenêtre.
- Café et sergent sans habillage : étagères, poutres, papier peint, lambris ; meilleur détail du film (0,073).
- Pièce photo vide : briques, lampe, comptoir.
- Images figées (QA-002) : 5,3 % → 0,8 % sur la version brute, mesure fiable.
- Char glissant ou flottant, porteurs dans la coque (QA-001) : bande 0-4,8 s, char tenu au-dessus des porteurs puis posé, porteurs aux flancs.

**Partiellement résolus**
- Saturation excessive : 0,72 → 0,57 avec l'étalonnage existant, encore au-dessus de 0,52.
- Explosions (QA-003) : plus de disparition ni de boule pleine, mais toujours des sphères puis un flash en disque, sans champignon, débris ni fumée qui reste.
- Rivière : l'eau et les berges sont meilleures ; le sol et le ciel restent pauvres.

**Toujours présents**
- Char héros en primitives (QA-006, gate B).
- Vélos en 2D plat (QA-007).
- Pas de lointain en patchwork ni de brume.
- Herbe en bâtons verticaux.
- Caméra peu vivante : mouvement 8,4 sur la version brute, contre 35,9.
- Rythme insuffisant : 5,2 pics par 10 s.
- 10 coupes sèches, aucun raccord en mouvement.
- Pas de très gros plans de l'objet héros.
- Radio peu habillée.
- Pas de météo.
- Nuages roses la nuit.

**Nouveau défaut**
- Voile laiteux dans le grenier : le détail baisse de 0,050 à 0,037.

### 0.6 Priorités mises à jour
1. **Critique — Char gonflable héros et leurres** (étapes 1-2) : seul FAIL bloquant du rendu final côté assets ; l'objet est à l'écran 26 s.
2. **Critique — Caméra et raccords** (étapes 7-8) : les écarts mesurés les plus grands (mouvement ×4, 10 coupes) ; aucun progrès depuis la v1.
3. **Critique — Explosions et étincelles** (étapes 9-10) : à peine améliorées, et c'est le climax.
4. **Important — Extérieurs** (étape 3) : lointain en patchwork, brume, herbe dense crédible (remplacer les bâtons), ciel de nuit sans nuages roses.
5. **Important — Étalonnage** (étape 6) : ramener la saturation à 0,40-0,50 et **corriger le voile du grenier**. L'exposition est déjà en PASS.
6. **Important — Intérieurs** (étape 4) : radio et chambre d'abord ; le café et la photo sont déjà à niveau correct.
7. **Moins urgent que prévu — Route de nuit** (étape 5) : l'exposition est réglée ; il reste la météo (pluie, flaques), une route animée et le ciel.
8. **Ensuite :** interactions (étape 11), post-production (étape 12) et son (étape 13), sans changement.
9. **Outil** (correction de mesure, sans effet sur le film) : mesurer la vie de la caméra avant le grain ; détecter les raccords à partir de `camera_baked.json`.

Les sections 1 à 3 ci-dessous gardent le constat initial sur la v1 pour l'historique. Le plan de correction (§4) reste valable, dans l'ordre de priorité du §0.6.

---
## 1. Mesures globales (constat initial v1)

| Mesure | Forteresse | Ghost Army v1 | Statut |
|---|---|---|---|
| Détail d'image (arêtes) | 0.095 | **0.047** | FAIL (moitié moins de détail) |
| Luminance jour | 0.433 | **0.292** | FAIL |
| Luminance nuit (27-35 s) | ≥ 0.25 visé | **0.104** | FAIL |
| Noirs bouchés | 0.07 % | **6.5 %** | FAIL |
| Saturation | 0.40 | **0.72** | FAIL ; 69 s sur 71 au-dessus de 0.60 |
| Images figées | 0 % | **5.3 %** | FAIL |
| Mouvement médian (×1000) | 35.9 | **8.1** | FAIL (4,4 fois moins de vie) |
| Pics de rythme / 10 s | 10.5 | **5.05** | FAIL |
| Coupes franches | 0 | **9** (une à chaque changement de prise) | WARN |
| Hautes lumières brûlées | 0.55 % | 0.1 % | PASS |

## 2. Plan par plan (mesures de la v1 par prise ; temps issus de `out/plan/camera_baked.json`)

| Prise (temps) | Luma | Sat | Bouché | Mouv. | Détail | Écarts face à la référence | Gravité |
|---|---|---|---|---|---|---|---|
| **t_hook** champ (0-10.6) | .30 | .75 | 3.1 % | 18 | .046 | Char gonflable héros en assemblage de primitives (gate B FAIL), contre les props modélisés de la référence (caisse à 82 trous). Sol vert plat avec brins clairsemés, contre une herbe dense jusqu'à l'objectif. Pas de lointain en patchwork ni de brume. Image trop sombre et trop saturée. | **Critique** |
| **t_camp** camp (10.6-26.4) | .36 | .66 | 1.1 % | 22 | .056 | Le meilleur plan mesuré. Mais les leurres forment une grille de clones identiques, contre une foule variée avec bannières. Les props de camp (compresseurs, caisses) sont des formes simples. Pas de vue aérienne d'établissement. | **Critique** (héros et leurres) / Important |
| **t_road** route de nuit (26.4-34) | **.07** | **.83** | **43.6 %** | 16 | .033 | Presque noir dans la v1 : 44 % de l'image bouchée. La référence a une nuit pluvieuse lisible, avec des flaques de lanternes. Haut-parleur et ondes corrigés depuis (notes v1) mais pas re-mesurés. Route vide, pas de météo. | **Critique** |
| **t_radio** (34-38.7) | .35 | .82 | 0 % | 15 | .050 | Intérieur à murs peu structurés, contre une architecture détaillée (poutres, pierre, objets d'usage). Caméra presque fixe. Saturation excessive. | Important |
| **t_cafe + t_sergeant** (38.7-46.7) | .46 | .69 | 0.1 % | 24 | .060 | Bonne exposition. Matériaux enrichis depuis la v1. Les patches cousus restent sans gros plan d'objet, alors que la référence fait des inserts sur l'objet héros. Saturation élevée. | Important |
| **t_river** (46.7-52.7) | .17 | .65 | 1.4 % | 16 | .041 | Eau, berges et explosions refaites après la v1, non re-mesurées. Explosion : un disque orange dans la v1, contre une enveloppe feu et fumée en couches avec champignon, débris et lumière sur le décor. Sombre. | **Critique** (effets) |
| **t_photo** (52.7-55.7) | .16 | .55 | 9.2 % | **10** | .041 | Plan quasi statique et sombre. Il manque une poussée caméra dans la photo (push-through). | Important |
| **t_strike** (55.7-61.5) | .19 | .72 | 0.8 % | 21 | .034 | Tir et croix : pas d'étincelle qui voyage ni de traînées radiales. Le plan au détail le plus faible du film. | **Critique** (effets) |
| **t_bed** (61.5-66.4) | .19 | .72 | 1.9 % | **10** | .032 | Chambre pauvre en détails (cadre de lit, linge, objets) et caméra presque fixe. | Important |
| **t_attic** (66.4-71.2) | .18 | .79 | **12.4 %** | 17 | .049 | Rayon de lumière ajouté depuis la v1. Les noirs restent bouchés et la saturation excessive. | Important |

## 3. Écarts par département

### Décors / environnements
- **Critique :** les extérieurs n'ont pas de 3e plan (patchwork de champs, collines, brume), ni d'herbe dense jusqu'à l'objectif. Référence : bible §1.1.
- **Important :**
  - les intérieurs ont trop peu de pièces secondaires (poutres, moulures, objets d'usage, usure) ;
  - aucun repère visuel ne revient d'un plan à l'autre.

### Assets héros et props
- **Critique :** le char gonflable héros est en primitives (gate B FAIL ; l'Asset Hub refuse les modèles militaires, refus respecté).
- **Important :**
  - grille de leurres clonés ;
  - compresseurs et caisses simplifiés ;
  - pas de gros plan sur la valve, la couture ou la peinture.

### Matériaux et textures
- **Important :** le détail mesuré est de 0.047 contre 0.095. Il reste des surfaces plates à distance caméra (sol, toile, murs) malgré les canevas ajoutés.

### Lumière, étalonnage, atmosphère
- **Critique :**
  - nuit illisible (0.10) ;
  - noirs bouchés à 6.5 % ;
  - saturation à 0.72 sur tout le film, contre 0.40.

  Le grade calibré (`grade.py`) existe mais n'a jamais été appliqué au film complet.
- **Important :** pas de brume sur les plans lointains ; pas de pluie ni de flaques la nuit.

### Animation et interactions
- **Important :** les actions de l'audit sont corrigées (porter, tapoter, poser, chevauchements). Mais il manque :
  - des objets lancés ou transportés en arc et suivis par la caméra ;
  - des réactions de groupe.

  La matrice action-effet n'a que 2 actions sur 9 avec une preuve de rendu.

### Caméra et composition
- **Critique :**
  - mouvement médian de 8 contre 36 ;
  - 5.3 % d'images figées ;
  - 9 coupes franches et 0 push-through.

  La référence ne s'arrête jamais et enchaîne ses plans par des mouvements.
- **Important :** pas de très gros plans de l'objet héros ; peu d'amorces au premier plan.

### Effets (VFX)
- **Critique :**
  - explosions en disque ou boule, au lieu des couches flash → feu → fumée qui évolue → débris → lumière sur le décor ;
  - pas d'étincelles qui voyagent ni de traînées.
- **Important :** pas de météo (pluie, poussière soulevée).

### Montage et post-production
- **Important :**
  - aucun fondu court ;
  - pas de bloom ;
  - flou de mouvement prévu seulement dans `grade.py`, pas encore appliqué.
- **Mineur :** le style des sous-titres reste à aligner (mot blanc gras, contour noir, tiers inférieur).

---
## 4. Plan de correction (rien n'est lancé avant ton accord)

La colonne « Vérification » renvoie toujours à une image ou une mesure, jamais à une simple affirmation.

| # | Plan / élément | Défaut | Résultat attendu (référence) | Solution technique | Fichiers / modules | Vérification |
|---|---|---|---|---|---|---|
| 0 ✅ FAIT (§0) | Film complet | État actuel non mesuré | Base chiffrée de la version corrigée | Preview v2 en demi-résolution de l'état actuel (sans rien changer), puis `compare-reference` | `render_gpu.mjs --scale .5`, `production_controller.py compare-reference` | `REFERENCE_COMPARE.md` v2 et planche |
| 1 | Char gonflable héros (hook, camp) | Assemblage de primitives | Modèle réel : chambres boudinées, coutures, valves, bâche peinte, pli de caoutchouc, marquages ; ≥ 20 pièces, ≥ 12 k tris | Modélisation sur mesure dans Blender (le Hub refuse les chars, ce refus est respecté) ; export GLB ; remplacement dans `ghost.js`, variantes de teinte pour les leurres | `sets/ghost.js`, `library/assets/custom/inflatable_tank/`, `ASSET_REGISTER.json` | `--inventory` (gate B PASS), gros plan, planche à côté de la caisse à 82 trous |
| 2 | Leurres (camp, champ) | Grille de clones | Foule variée, alignements imparfaits, bannières, gonflés à des niveaux différents | Instances du modèle n°1 avec échelle, rotation et dégonflement variés, placement en lignes irrégulières, fanions et filets | `sets/ghost.js` | Planche plan large ; aucun motif répété visible |
| 3 | Extérieurs (champ, camp, route, rivière) | Pas de 3e plan, herbe clairsemée | Patchwork de champs en plusieurs teintes, haies, collines, brume bleue ; herbe dense au premier plan | Module de lointain (heightfield et champs texturés), brouillard de hauteur, herbe instanciée dense près de la caméra, nuages volumétriques en cartes | `sets/ghost.js` (ou un nouveau module `sets/landscape.js`), agent background-painter | Détail ≥ 0.075 sur ces plans ; ENV_SCORES profondeur ≥ 3 avec image |
| 4 | Intérieurs (radio, café, photo, chambre, grenier) | Peu de pièces secondaires | Poutres, moulures, objets d'usage, usure, praticables lumineux | Habillage par lieu (meubles modélisés, Poly Haven et ambientCG d'abord), normal maps, lampes praticables | `sets/ghost.js`, Asset Hub | Planche par lieu côte à côte avec la référence ; textured share ≥ 85 % |
| 5 | Route de nuit | 0.10 de luma, 44 % bouché | Nuit lisible (≥ 0.25), pluie, flaques réfléchissantes, lanternes | Clé lunaire et fill plus forts, sol mouillé PBR, particules de pluie, lampes praticables (une partie est déjà faite par les notes v1) | `sets/ghost.js`, `grade.py` (look road) | `compare-reference` : luma_night ≥ 0.25, bouché ≤ 1 % |
| 6 | Étalonnage global | Saturation 0.72, noirs bouchés | Saturation 0.32-0.52, luma jour 0.36-0.50 | Recalibrer `LOOK` par lieu sur les cibles du standard, puis appliquer à tout le film (journal de grade) | `grade/grade.py` | `compare-reference` : saturation, luma et bouché en PASS ; gate G |
| 7 | Caméra (toutes les prises) | 8 de mouvement, 5 % figé | Caméra qui vit en continu, très gros plans de l'objet héros, amorces | Dérive lente sur chaque station (pas de `hold` immobile), stations d'insert macro (valve, patch, photo), amorces au premier plan | `build/make_film.py` (stations), `film.json` | still ≤ 2 %, mouvement ≥ 18 ; extraits de revue |
| 8 | Raccords (9 coupes) | Coupes franches | Push-through, mouvement suivi ou fondu de 3-6 images | Transitions dans le kit (`transition: push/dissolve` entre prises) ; une coupe sèche seulement si voulue et notée dans DECISIONS | `templates/threejs_film/film.js`, `tools/film_plan.py`, `make_film.py` | `compare-reference` : 0 coupe non justifiée ; bandes de transition |
| 9 | Explosions (rivière, frappe) | Disque ou boule orange | Flash → enveloppe feu → fumée qui grossit (champignon) → débris → lumière sur le décor → retombée | Système d'effets en couches : sprites animés, lumière ponctuelle à courbe, débris balistiques, fumée persistante. Effets visuels fictifs uniquement | `sets/ghost.js` (bursts), module FX du kit | Bande continue image par image ; ACTION_EFFECT_MATRIX PASS |
| 10 | Tir et étincelles (strike) | Ni trajectoire ni étincelles | Étincelle qui voyage, traînées radiales, gerbes | Traînées en ruban et particules avec durée de vie | Module FX | Bande continue ; détail ≥ 0.075 |
| 11 | Interactions | Peu d'objets lancés ou portés en arc ; pas de réactions de groupe | Objets lancés suivis par la caméra ; têtes qui se tournent | Mouvements `m:` existants plus objets attachés à la main avec trajectoire ; réactions secondaires | `make_film.py`, `motion_styles` | Bandes d'action ; anim_audit PASS |
| 12 | Post-production | Pas de bloom ni de fondu ; flou à appliquer | Bloom sur les émissifs, flou seulement sur les mouvements rapides, DoF sur les gros plans | Bloom et DoF dans le rendu, flou sélectif déjà prêt dans `grade.py` | `film.js`, `grade.py` | Planche finale ; journal de grade |
| 13 | Son | Effets à re-synchroniser après les changements | Chaque contact ou effet a son son | Mettre à jour les repères dans `mix.py` après les nouveaux effets et transitions | `sound/mix.py` | `mix_report.json` ; −15 LUFS, −1 dBTP |

**Ordre proposé :**
1. Étape 0 : mesurer l'existant.
2. Étapes 1-2, puis 3-5 : le monde.
3. Étapes 7-8 : caméra et raccords, avec l'impact sur le montage approuvé signalé.
4. Étapes 9-11 : effets et interactions.
5. Étapes 6, 12 et 13 : grade, post-production et son.
6. Preview v2, puis `gates --phase preview` et `compare-reference`, et ton avis.
7. Seulement ensuite, le rendu natif.

**Ce qui ne change pas sans ton accord :** histoire, voix, musique, personnages 2D, durée et minutage des mots. Les étapes 7 et 8 modifient la manière de passer d'un plan à l'autre ; le montage approuvé reste le même au mot près.

**Coût :** tout se fait ici (CPU et Blender local). Aucun achat d'asset, aucune API payante et aucun GPU RunPod sans ton autorisation explicite.
