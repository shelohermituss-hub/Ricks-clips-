# Ghost Army comparée à la référence forteresse : écarts et plan de correction (2026-11-18)

**Référence :** `references/REFERENCE_LOOK_BIBLE.md` v2.0 OFFICIELLE. Captures dans `references/fortress/`, cibles chiffrées dans `production/config/reference_standard.json`.

**Mesure :** `tools/production_controller.py compare-reference`. Le même code a mesuré la référence (elle passe les 10 seuils, voir `references/fortress/reference_compare_self.json`) et le film (`REFERENCE_COMPARE.md`).

**Preuve visuelle :**
- `references/fortress/compare_ghost_army_2026-11-18.jpg` (paires référence / Ghost Army) ;
- `references/fortress/frames/` ;
- `references/fortress/motion_strips_*.jpg`.

> **Limite à connaître.** La seule vidéo complète de Ghost Army est la preview v1 (`v1/ghost_army_preview_v1.mp4`, non étalonnée). Elle date d'**avant** les corrections des notes v1 et de l'audit d'animation, qui ont été vérifiées sur des images de test, pas sur un film complet.
> - Les chiffres ci-dessous décrivent donc la v1.
> - Les écarts structurels (modélisation, caméra, coupes, effets) restent vrais aujourd'hui, car ces corrections ne les ont pas traités.
> - L'exposition de la route de nuit et les matériaux des intérieurs ont déjà progressé depuis la v1. Leur nouvelle mesure demande une preview v2 (étape 0 du plan).
>
> Aucun élément n'est déclaré conforme ici sans mesure ou image.

Échelle de gravité :
- **Critique** : empêche d'atteindre la référence.
- **Important** : visible pour un spectateur attentif.
- **Mineur** : finition.

---
## 1. Mesures globales

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
| 0 | Film complet | État actuel non mesuré | Base chiffrée de la version corrigée | Preview v2 en demi-résolution de l'état actuel (sans rien changer), puis `compare-reference` | `render_gpu.mjs --scale .5`, `production_controller.py compare-reference` | `REFERENCE_COMPARE.md` v2 et planche |
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
