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

## 6. Proportions mesurées au pixel (20/11) — `data/character_measures.csv`
Six personnages debout, mesurés sur une grille de pixels (`tools/grid.py`), dans les coordonnées 720×1280 de la vidéo. La tête inclut le chapeau ou les cheveux quand il y en a, comme on la voit à l'écran.

| Rapport | Min | Médiane | Max | Notre planteur (carte) |
|---|---|---|---|---|
| hauteur de tête / hauteur totale | 0,21 | **0,27** | 0,38 | 0,21 sans casquette, 0,36 avec |
| largeur de tête / largeur du torse | 1,10 | **1,22** | 1,80 | **1,70** |
| hauteur du torse / hauteur de tête | 0,75 | **1,03** | 2,20 | 1,36 |
| jambes / hauteur totale | 0,23 | **0,35** | 0,56 | 0,33 |

Constats (MESURÉ) :
- Les proportions varient beaucoup d'un personnage à l'autre, même dans une vidéo : jambes très longues du scientifique (V01, 0,56), tunique longue (V05).
- La tête est **à peine plus large que le torse** dans la plupart des cas (1,1-1,25). Nos cartes ont une tête nettement plus large que le torse (1,70), dans la plage mais en haut, comme le scientifique de V01.
- Contour : environ 3 % de la largeur de la tête dans les références, environ 4 % sur nos cartes. Mains : petites boules noires au bout de bras-traits, comme chez nous.
- Les visages des références ont un **léger dégradé d'ombre** du côté opposé à la lumière (V03 1365, V04 885) ; les torses ont un volume ombré. Nos cartes ont un aplat avec un reflet : à surveiller dans la comparaison côte à côte.

RECOMMANDATION (**non appliquée** : le gabarit est verrouillé par CB, `templates/vector2d_characters`, « standard (locked) ») : élargir le torse du gabarit standard d'environ 20 à 30 % (`wTop` 72 → 90, `wBot` 106 → 130) pour ramener le rapport tête/torse vers 1,3. À valider par CB, car cela change les 150 personnages.

## 7. Catalogue des timings (image par image, 20/11)
Durées en images à 30 i/s, toutes OBSERVÉES sur les planches image par image citées.

| Type | Passage | Déroulé mesuré |
|---|---|---|
| **Changement d'expression sur un mot** | V01 762-766 | narquois → grand sourire en 2-4 images, sur « 300 lbs » |
| | V02 1657-1664 | coupe sur gros plan : yeux ronds dès la 1re image (1658), goutte de sueur déjà là ; la bouche tombe en arc inquiet **6 images plus tard** (1664), sur « camera ». Ordre : les yeux d'abord, la bouche ensuite |
| | V04 879-883 | sur « furious » : fissures sous les pieds à 879, puis **yeux rouges lumineux qui s'allument d'un coup** à 883 (1 image, sans fondu) |
| | V03 2436-2439 | yeux en $ qui apparaissent d'un coup (2436) avant l'annonce ; anneau doré de flash à 2438-2439 |
| **Clignement** | V05 1474 | yeux fermés sur **1 image**, en plein dialogue, sans arrêter la scène |
| | V03 2434-2435 | paupières mi-closes puis fermées (2 images), puis grands yeux (2436) : clignement de surprise |
| **Réaction des témoins** | V01 1044-1047 | du neutre aux yeux ronds en 3 images après la claque |
| | V05 778-785 | sursaut des voisins pendant l'onde de choc |
| **Geste de bras** | V05 1456-1471 | mains sur le tissu pendant 10 images (1456-1466, préparation), puis le tissu part en 1 image (1467) et vole 8 images en tournant ; le corps du personnage **ne bouge pas** |
| | V05 774-777 | gifle : bras armé 3 images, frappe en 1 image |
| **Sortie de voiture et marche** | V04 860-883 | la portière s'ouvre en 3 images (864-866) ; le corps sort en 6 images (867-872) ; 3-4 pas vers la caméra, jambes alternées, environ 4 images par pas (873-883) ; visage fâché tenu |
| **Grand saut de pose** | V02 1602-1617 | penché au ras du capot pendant 10 images, puis remonte d'un coup jusqu'au pare-brise en environ 5 images (1612-1617) |
| **Corps qui part en arc** | V04 19-36 | projeté en arc puis retombe assis (analyse antérieure à 10 i/s) |

## 8. Catalogue des transitions (image par image)
| Transition | Passage | Déroulé mesuré |
|---|---|---|
| Traverser le plafond | V01 1158-1181 | plongée verticale au-dessus des personnages (1158-1163), la caméra monte, les personnages rapetissent ; à 1167 elle traverse la verrière en **1 image**, à 1169 on est au-dessus du toit ; puis survol des toits et de la campagne en grue continue (1173-1181). Aucune coupe |
| Filé qui change de sujet | V05 52-75 | macro de la perceuse (52-59), filé rapide le long du mur en 4 images (60-63), puis la caméra **monte le long du rempart** jusqu'au pavillon (64-75) ; flou de mouvement fort pendant le filé |
| Traverser une vitre | V02 30-40 | la caméra recule à travers le pare-brise (analyse §1 de V02) |
| Entrer dans un écran | V01 1384-1407 | poussée de 14 images dans le moniteur, la texture d'écran s'efface |
| Fondu | V02 556-563 | fondu de 6 images, qui change en même temps la lumière (jour → crépuscule) |
| Écran noir et révélation | V03 2433-2439 | l'écran de la caisse devient noir (3 images, suspense), une ligne apparaît, puis flash doré plein cadre |

**Règles tirées pour l'animation** (RECOMMANDATION) :
- yeux en 1 image, bouche 4-6 images après ;
- signes lumineux (yeux rouges, $) sans fondu ;
- un clignement de 1-2 images de temps en temps ;
- geste en préparation longue (8-10 images) puis action en 1 image ;
- le corps reste immobile quand seul le bras agit ;
- un pas tous les 4 images environ pour une marche décidée ;
- témoins en réaction 3 images après l'événement.
