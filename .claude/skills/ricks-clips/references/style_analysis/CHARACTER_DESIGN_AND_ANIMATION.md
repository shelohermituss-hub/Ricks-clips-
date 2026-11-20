# Personnages : design, jeu, micro-animations

Bible centrale : `RICKCLIPS_REFERENCE_STYLE_BIBLE.md`. Preuves : captures `evidence/V0x/*crop*` et analyses §3.

## 1. Design observé (commun aux cinq vidéos)
- **Tête** :
  - disque ou ovale **blanc** (légèrement grisé ou teinté par la lumière ambiante), **contour noir épais et constant** ;
  - environ un quart de la hauteur du personnage debout (estimé sur les planches, non mesuré au pixel ; INFÉRÉ) ;
  - plus grosse chez les personnages « massifs » (gros détenu V01).
- **Corps** :
  - torse en tube ou en œuf, **habillé et coloré** : c'est la plus grande surface de couleur du personnage ;
  - **bras et jambes en traits noirs fins**, mains et pieds réduits à des petites boules ou à rien.
- **Visage** :
  - yeux = points ou petits traits ;
  - **sourcils très mobiles** ;
  - bouche = trait, grande ouverture, ou grille de dents ;
  - nez absent ou minimal ;
  - joues roses quand le personnage est heureux (V01 1740).
- **Rôle lisible par 2-3 accessoires** (OBSERVÉ) :

  | Rôle | Accessoires |
  |---|---|
  | gardien | casquette à étoile, uniforme marine |
  | policier ou shérif | chapeau, lunettes d'aviateur, moustache |
  | médecin | blouse, cheveux gris, moustache |
  | ouvrier | casque orange, gilet |
  | soldat | casque, bouclier, couleur du camp |
  | scientifique | chemise blanche, cravate |
  | escroc | t-shirt jaune, lunettes sur la tête |

- **Variations d'un même personnage** : costume selon l'époque, mais même visage (V03, cinq costumes du héros).
- **Lisibilité à distance** : la tête blanche reste lisible même minuscule (V01 1155 ; foule V05 1310), car elle contraste avec tous les fonds.
- **Intégration** :
  - les personnages **projettent des ombres** sur le décor 3D (V01 615-645 ; V05) et prennent la teinte de la lumière ambiante (rose V01, bleu de nuit V02) (OBSERVÉ) ;
  - ils sont plats (2D) dans un monde 3D (INFÉRÉ : contour d'épaisseur constante, pas de volume qui tourne) ;
  - méthode exacte : INCONNU.

**Pour RicksClips** : c'est déjà le principe des cartes 2D du pipeline (`tools/card_service.py`). Concevoir des personnages **originaux** dans ce langage (tête blanche, traits, accessoires de rôle) sans reproduire un personnage existant précis.

## 2. Expressions et jeu
| Émotion | Signes observés | Exemples |
|---|---|---|
| Fierté / malice | sourire en coin, sourcils levés d'un côté | V02 30, V04 0, V05 1990 |
| Peur / stupeur | yeux ronds agrandis, bouche ouverte, sueur | V02 99-103, V02 1650, V04 1290 |
| Colère | sourcils en V, dents serrées, **yeux rouges lumineux**, éclairs, aura | V01 790-848, V04 885, V05 762 |
| Hypnose | **yeux en spirale** | V04 1605 |
| Cupidité / gain | **yeux en $** | V03 900, 2445 |
| Douleur feinte | yeux plissés, main au cou | V02 170, 1480 |
| Béatitude | yeux fermés en arc, joues roses | V01 1740-1890 |
| Perplexité | gribouillis au-dessus de la tête | V05 370 |
| Froid | peau bleue, dents qui claquent, buée, glaçon | V03 1350-1395 |

- **Synchronisation** : le changement d'expression tombe **sur le mot** (V01 762-766 « 300 lbs », image par image) en 2-4 images.
- **Réaction différée** : le perdant reste figé environ 0,4 s (V01 1044-1057) ; l'escroc comprend après le geste de l'autre (V02 1600-1650).
- **Impassibilité comme jeu** : le personnage calme pendant que tout s'agite (V02 homme calme ; V05 héros pendant l'assaut).

## 3. Corps et poses
- Le **visage et les bras jouent**, le bas du corps bouge peu (V01 750-797, jambes fixes pendant que les bras montent).
- Les grands mouvements sont rares et francs :
  - saut hors du lit (V02 398) ;
  - projection en arc (V04 19-36) ;
  - danse sur un tas (V02 870) ;
  - couché sur un objet (V05 945) ;
  - chute libre bras écartés (V03).
- **Effort** : genoux pliés, corps penché, tremblements, puis rupture (V01 1524-1545).
- **Geste en deux temps** : armer, puis frapper (V05 774-777).

## 4. Micro-animations (OBSERVÉ, densité limitée par la couverture)
| Type | Exemples | Recette |
|---|---|---|
| Changement de visage sur le mot | V01 762, 790 | 2-4 images, la tête peut faire un petit à-coup |
| Bras qui montent pendant une phrase | V01 790-797 | progression sur 8 images |
| Animation de repos liée à l'objet tenu | tricot V01 1725-1890 ; chronomètre tenu V01 450-660 | cycle lent de l'objet |
| Geste-signature répété | main au cou V02 | même geste à chaque occurrence |
| Témoins qui réagissent | sursaut V05 778-785 ; rires V01 345-410 | les autres personnages réagissent aussi |
| Foule qui oscille | V05 1385-1440 | décalage de phase entre les figures |
| Respiration, buée | V03 1350-1395 | cycle court |
| Vêtements et cheveux au vent | V03 chute | continu pendant le mouvement |

**Limite** : les clignements, la respiration fine et les doigts n'ont pas été cherchés image par image sur de longues plages (couverture partielle, voir `analysis_coverage.md`).

## 5. Spécification pour RicksClips (RECOMMANDATION)
- **Contrôles d'une carte personnage** :
  - vue (une seule par personnage, leçon PI-016) ;
  - expression (bibliothèque : neutre, fierté, peur, colère, béat, ahuri, douleur, perplexe) ;
  - signe 2D superposé (éclairs, yeux lumineux, spirales, $, sueur, gribouillis, aura) ;
  - pose de bras ;
  - mouvement ;
  - accessoire tenu (main mesurée par `card_anchors.py`).
- **Synchronisation** : expression et signe sur le mot (`words.json`), 2-4 images de transition.
- **Repos** : un cycle lié à l'objet tenu, sinon une légère oscillation de la tête et du corps.
- **Témoins** : chaque action forte déclenche une réaction des personnages visibles (sursaut, regard vers la cause).
- **Foule** : un gabarit, des variantes d'accessoires et de couleurs, des phases décalées.
