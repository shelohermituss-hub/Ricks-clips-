# V01 — « The Pink Prison Cell Experiment » — analyse

Statuts : **OBSERVÉ** (vu), **MESURÉ** (mesure), **INFÉRÉ** (plausible), **INCONNU**, **RECOMMANDATION** (proposition RicksClips).
Preuves : `evidence/V01/V01_fNNNNN_*.jpg` (images 720×1280), image = numéro d'image source à 30 i/s. Catalogues : `data/V01/shots.csv`, `events.csv`, `assets.csv`, `palette.json`, `coverage.json`.

## 0. Fiche technique et couverture réelle
- MESURÉ : 65,29 s, 1957 images, 720×1280 (9:16), 30 i/s, H.264 ~1,12 Mb/s, AAC 44,1 kHz stéréo 128 kb/s, SHA-256 `9b5e215a…` (`data/V01/tech.json`).
- Couverture (détail : `data/V01/coverage.json`, statut **PARTIAL**) :
  - niveau A : vidéo entière lue à 2 i/s (4 planches) ;
  - niveau B : chaque plan vu par ses images clés et les 69 captures ;
  - niveau C : image par image sur 750-797 (piétinement), 1524-1547 (arrachage du banc) et 1384-1407 (entrée dans le moniteur).
- Non lus image par image : la rage (798-869) et le bras de fer (1030-1077).

## 1. Structure narrative et rythme
- **13 plans en 65 s**, durée médiane ≈ 4,6 s (MESURÉ, `shots.csv`). Les plans sont longs parce que la caméra **ne coupe presque jamais** :
  - le détecteur ne trouve que 5 candidats, tous à 1044 (impact du bras de fer) et 1163-1168 (traversée du plafond) (MESURÉ) ;
  - les lieux s'enchaînent par **fondus enchaînés** d'environ 0,3 s (109, 859, 1291, 1718), par un **panoramique filé** (420), en **franchissant une porte avec le personnage** (697-716, avec un gardien qui passe devant l'objectif), en **traversant le plafond** (1150-1170) et en **entrant dans un écran** (1384-1398) (OBSERVÉ).
- **Voix** : 237 mots, 3,65 mots/s, aucune pause de plus de 0,46 s (MESURÉ). La voix ne s'arrête jamais ; les pauses comiques sont dans l'image (réaction figée du détenu à 1057 sur « Wait, what? »).
- **Lien voix-image** (MESURÉ par les mots minutés) : chaque fait chiffré tombe sur son objet.
  - « one pint of red » → versement (170-200) ;
  - « 15 minutes » → très gros plan du chronomètre (585-600) ;
  - « 300 pounds » → coup de pied et fissures (762) ;
  - « two seconds » → la main plaquée (1044) ;
  - « At 15 / At 20 » → calme puis cent pas.
- **Arc** :
  - crochet par l'action dès l'image 0 (on peint déjà) ;
  - règle absurde (dosage exact, repeindre) ;
  - essai (petit détenu) ;
  - vrai cas (le plus gros détenu) ;
  - preuve absurde (bras de fer) ;
  - généralisation (aérien, camion) ;
  - rupture « Until one night » (passage à la nuit) ;
  - escalade en 3 temps ;
  - explication « You see » ;
  - chute « exact opposite » qui reprend le plan calme et le retourne.

## 2. Timeline des plans
| Plan | Images | Lieu | Action | Caméra | Sortie |
|---|---|---|---|---|---|
| S01 | 0-108 | cellule bleue | gardien peint une bande rose ; fiche P-618 | travelling + poussée vers la fiche | fondu |
| S02 | 109-239 | atelier peinture | dosage et versement, spirale rose | poussée, plongée tournante | raccord couleur → fondu |
| S03 | 240-344 | cellule magenta | 3 gardiens repeignent ; nuancier « mauvaise teinte » | dérive, recadrage | coupe |
| S04 | 345-430 | salle commune POD C | gardiens moqueurs | dérive + filé | filé |
| S05 | 430-659 | couloir C-4 | règle des 15 min, essai, chronomètre | poussée rapide (580-585), contre-plongée | coupe sur mouvement |
| S06 | 660-858 | couloir → cellule rose | le plus gros détenu jeté, coup de pied, fissures, rage | suivi + passage de porte, contre-plongée fixe | fondu |
| S07 | 859-930 | couloir | il ressort doux | dérive | coupe |
| S08 | 930-1150 | salle commune | bras de fer : le gardien maigre gagne | dérive, choc à 1044, grue vers la plongée | traversée du plafond |
| S09 | 1150-1290 | toit → campagne → autre prison | généralisation, camion rose | grue continue montée-vol-descente | fondu jour → nuit |
| S10 | 1291-1398 | hall nuit, guérite | le gardien s'endort | dérive, poussée DANS le moniteur | écran |
| S11 | 1398-1556 | cellule rose (caméra de surveillance) | calme → cent pas → arrache le banc | quasi fixe, tremblements | coupe |
| S12 | 1557-1717 | couloir | recul par la porte, explication | recul continu | fondu |
| S13 | 1718-1956 | cellule rose | tricot béat → aiguilles cassées → rage | poussée lente vers le visage | fin |

## 3. Personnages
### Design (OBSERVÉ sur les captures ; proportions estimées sur les planches, non mesurées au pixel)
- **Tête** :
  - grosse tête ronde ou ovoïde blanche à contour noir épais ;
  - environ un quart de la hauteur totale chez les personnages normaux, plus chez le gros détenu, dont le torse est un œuf énorme.
- **Corps** : torse en tube ou œuf habillé ; **membres en simples traits noirs fins** (bras et jambes), sans mains dessinées ou presque (boules ou traits).
- **Visage** :
  - yeux = petits points ou traits ;
  - sourcils très mobiles ;
  - bouche = trait, ou grille de dents en colère (1905-1945) ;
  - pas de nez, ou un nez minimal ;
  - joues roses quand le personnage est béat (1740-1890).
- **Rôle lisible par 2 ou 3 attributs** :
  - gardiens : casquette sombre à étoile + uniforme bleu marine ;
  - scientifique : chemise blanche, cravate rayée brune, cheveux bruns ;
  - détenus : débardeur rayé blanc ou combinaison bleue à matricule, cheveux roux bouclés, lunettes ;
  - le gros détenu : torse énorme à petit tatouage d'ancre (990-1035).
- **Lisibilité à distance** : la silhouette blanche à contour noir se détache de tous les fonds, bleus comme roses (OBSERVÉ à 1155, figures minuscules en plongée encore lisibles).
- **Rendu** : contour net, aplats avec un léger dégradé sur le corps ; ils **projettent des ombres** dans le décor 3D (ombre géante du scientifique sur la porte, 615-645 ; ombre du détenu sur le mur, 1514) (OBSERVÉ). Personnages 2D intégrés à des décors 3D : INFÉRÉ (le contour reste constant quand la caméra tourne).

### Expressions et acting
- Changement d'expression **sur le mot** :
  - le visage du gros détenu passe de narquois à hilare entre 762 et 766, sur « 300 lbs » ;
  - puis à démoniaque (yeux rouges, sourcils en V) à 790, sur « of tattoos » (MESURÉ image par image).
- **Réaction différée** : le perdant du bras de fer reste figé, yeux ronds, environ 0,4 s après le coup (1044 → 1057) (OBSERVÉ).
- Le corps garde souvent la même pose pendant que le visage change ; le jeu passe par le visage et les bras (OBSERVÉ 750-797 : jambes immobiles, bras qui montent progressivement 790-797).

### Corps et poses
- Coup de pied (750-766, image par image) :
  - jambe levée en 8 images (754-761) ;
  - contact en 1 image (762) ;
  - tout le corps reste raide ;
  - aucun recul ni rebond du corps (OBSERVÉ).
- Effort de l'arrachage (1524-1547, image par image) : genoux pliés, corps penché, visage crispé à dents serrées ; tremblements, puis rupture d'un coup à 1545.
- Marche des personnages en arrière-plan : présente mais peu visible (petit détenu 495-560).

### Micro-animations (OBSERVÉ sauf mention)
| Qui | Partie | Déclencheur | Timing | Amplitude | Type | Preuve | Recette |
|---|---|---|---|---|---|---|---|
| gros détenu | bras | montée de la rage | 790-797, 8 images | coudes qui passent des hanches au-dessus de la tête | ponctuel, progressif | `seq_750_797` | les bras montent pendant la phrase, pas d'un coup |
| gros détenu | visage | mot « 300 lbs » | 762-766 | narquois → grand sourire | ponctuel, sur le mot | idem | expression changée au mot, en 2 à 4 images |
| détenu au tricot | aiguilles, tête | cycle | 1725-1890 | petits mouvements d'aiguilles, tête qui oscille | cyclique | `V01_f01740_s14_tricot.jpg` | animation de repos liée à l'objet tenu |
| gardien endormi | tête, paupières | fatigue | 1350-1392 | tête qui tombe, yeux fermés | ponctuel | `V01_f01375_s11_garde_endormi.jpg` | — |
| scientifique | bras + chronomètre | règle | 450-660 | chronomètre levé et tenu près du visage | tenue | `V01_f00475_…` | objet récurrent tenu en hauteur |
| témoins du bras de fer | corps | coup | 1044-1060 | sursaut (INFÉRÉ, non lu image par image) | ponctuel | `V01_f01057_…` | les témoins réagissent aussi |

## 4. Environnements et assets
- **Lieux** :
  - cellules (bleue puis roses) ;
  - atelier peinture ;
  - salle commune POD C sur deux niveaux ;
  - couloir de la porte C-4 ;
  - toit ;
  - campagne vue d'avion ;
  - quai d'une seconde prison ;
  - hall de nuit avec guérite.

  Tous sont des décors 3D cohérents, traversés par la caméra : on passe d'un lieu au lieu voisin, sans décor isolé (OBSERVÉ 1150-1290).
- **Profondeur** :
  - dans la salle commune : premier plan (table), plan moyen (personnages), fond (coursive à balustrade, rangée de portes) ;
  - dans les cellules, peu de profondeur : un coin de pièce en contre-plongée avec le plafond et le néon en diagonale, comme ligne de force (OBSERVÉ 750-797).
- **Assets** (15, `assets.csv`) :
  - héros : fiche P-618, pots et balance, chronomètre, banc scellé, écharpe tricotée ;
  - secondaires : murs, porte C-4, tables, camion rose, guérite et moniteur CRT ;
  - dressing : néons, fenêtres à barreaux, calendrier « 1979 », post-it, tasse ;
  - fond : coursives, campagne en damier.
- **Faits écrits dans le décor** (OBSERVÉ) : fiche « P-618 BAKER-MILLER PINK 1 PINT RED + 1 GALLON WHITE EXACTLY! », nuancier « P-618 », camion « P-618 », plaque « POD C », plaque « C-4 », calendrier « 1979 ».
- **Détails et textures** :
  - parpaings à joints creux lisibles à 2-4 m ;
  - grain discret sur les sols ;
  - pas d'usure ni de saleté marquée : les surfaces sont **propres** ;
  - le détail est dans la forme (joints, rivets, grilles de néon) plus que dans la salissure (OBSERVÉ).
- **LOD** : la campagne aérienne est faite de grandes masses colorées (parcelles, cercles d'irrigation, arbres en boules), sans détail fin (OBSERVÉ 1185-1230).

## 5. Caméra
- **Toujours en mouvement** : 0,7 % des images seulement sont quasi immobiles (MESURÉ, différence moyenne < 0,3). Mouvement médian 4,4/255 par image, le plus calme des cinq vidéos avec V04 (MESURÉ).
- **Échelles** : plans moyens à hauteur de personnage, contre-plongées de cellule (750-858, 1500-1556), très gros plan objet (chronomètre 585-600), plongée de surveillance (1398-1420), plongée verticale (1155), vue aérienne (1170-1230).
- **Focale apparente** : courte à moyenne. Les lignes de briques convergent fort dans les cellules, donc grand angle plausible, environ 18-28 mm équivalent (INFÉRÉ, plage prudente). Profondeur de champ presque toujours infinie, sauf le très gros plan du chronomètre (fond légèrement flou, OBSERVÉ 585-600).
- **Mouvements notables** :
  - poussée rapide de ~5 images sur le chronomètre (580-585, pic de différence 41) ;
  - grue continue de la salle commune jusqu'au ciel puis à une autre prison (1150-1290, environ 4,7 s) ;
  - poussée dans l'écran CRT (1384-1398, 14 images) : l'image du moniteur remplit le cadre, puis la texture d'écran s'efface (OBSERVÉ image par image) ;
  - choc de caméra à l'impact du bras de fer (1044).
- **Recettes** (RECOMMANDATION) :
  - « passer par l'objet » (porte, plafond, écran) au lieu de couper ;
  - « poussée de 5 images sur l'objet chiffré » ;
  - « contre-plongée de coin de pièce » pour la puissance d'un personnage.

## 6. Lumière, palettes, étalonnage
| Ambiance | Où | Lumière (OBSERVÉ) | Palette (MESURÉ, k-means ou échantillons) |
|---|---|---|---|
| Cellule bleue, jour froid | S01 | lumière du jour par une fenêtre à barreaux, néon au plafond, ombres douces | #34566a 44 %, #2c3844, #364561, accent #e4e5e5 |
| Cellule rose | S03, S06, S11, S13 | néon + faisceau doux depuis la fenêtre haute, murs qui éclairent les personnages en rose (le visage blanc du scientifique mesure #b08294) | magenta #f43ca0 / rose moyen #d85482, #f086ae / rose pâle #f292b5 ; sol neutre #8a8794 ; ombres violettes #49425a |
| Salle commune, jour | S04, S08 | **faisceaux volumétriques** de la verrière sur le sol et les tables, contre-jour, atmosphère légèrement voilée | #466784 39 %, gris #9d9da0, ombres #21324d, hautes lumières #edf0f1 |
| Nuit intérieure | S10 | bascule globale au bleu saturé, une seule source chaude (bureau orange, écran rose) | #263d97 66 %, #445398 |
| Extérieur aérien | S09 | soleil haut, ciel bleu, nuages blancs | ciel #8cc4f6, champs #69a47d |

- **Mesures par seconde** (MESURÉ, `data/V01/per_second.json`) : luminosité moyenne 0,52 (de 0,32 la nuit à 0,72 sur l'extérieur aérien) ; saturation moyenne 0,37 (de 0,22 en cellule bleue à 0,62 en rage rose).
- **Étalonnage** : noirs relevés (pas de vrai noir sauf les contours), hautes lumières douces, aucun grain visible, image nette (OBSERVÉ). Léger halo sur les néons et les fenêtres (bloom, OBSERVÉ 1400-1420).
- **Couleur et histoire** : la couleur des murs EST le sujet. La palette suit l'histoire : bleu = avant, rose = effet, rouge = rage.
- **Reconstruction proposée** :
  - murs en matériau émissif faible (0,1-0,2) ou une lumière de remplissage colorée par le mur, pour reproduire le rose renvoyé sur les visages ;
  - volume léger + lampe zone dans la verrière pour les faisceaux ;
  - nuit = changement de balance des blancs vers 9000-10000 K + une lampe chaude locale.

## 7. Animation de l'environnement
- Nuages qui défilent pendant l'aérien (OBSERVÉ 1185-1215).
- Néons fixes, aucun vacillement observé.
- Pas de vent : intérieurs.
- Les éclats de peinture et de béton flottent dans l'air après la rage (1650-1700, éclats roses en suspension), puis restent (OBSERVÉ).

## 8. Interactions, physique et conséquences
Détail : `events.csv` (11 événements). Deux chaînes complètes :

**E05, coup de pied du gros détenu (750-790, image par image)** :
1. État initial : debout, narquois, sol lisse.
2. Anticipation : jambe gauche levée sur 8 images (754-761).
3. Déclencheur : « 300 lbs ».
4. Contact : pied au sol à 762.
5. Réaction : fissures rouges qui rayonnent en 4 images (762-766), petits éclats projetés.
6. Transfert : aucun recul du corps.
7. Déformation : fissures qui s'élargissent jusqu'à 775 puis se figent.
8. Effets secondaires : poussière fine.
9. Décor : le sol reste fissuré.
10. État final : sol fissuré.
11. Persistance : la fissure est encore visible quand il ressort (870-885) (OBSERVÉ).

**E10, arrachage du banc (1500-1556, image par image 1524-1547)** :
1. État initial : assis au banc.
2. Anticipation : penché, genoux pliés, tremblements de 1524 à 1544 (environ 0,7 s), lignes d'impact au sol, ombre géante derrière lui.
3. Déclencheur : « trying to rip the bench ».
4. Contact : mains sur le banc.
5. Rupture à 1545 : le banc éclate en gros blocs blancs anguleux, éclats et poussière.
6. Transfert : le banc est levé au-dessus de la tête (1550).
7. Décor : la dalle est cassée.
8. Persistance : un bloc de béton au sol dans le couloir au plan suivant (1568) (OBSERVÉ).

- **Règle observée** : un effort long et tremblé, puis une rupture d'un coup en blocs nets ; chaque force laisse une trace qui reste au plan suivant.
- **Ce qui n'est PAS montré** : pas de blessure, pas de sang, pas de débris réalistes ; les ruptures sont **stylisées** (blocs à arêtes vives, fissures rouges) (OBSERVÉ).

## 9. VFX et compositing
| Effet | Où | Description (OBSERVÉ) | Méthode |
|---|---|---|---|
| Fissures rouges | 762-790 | lignes rouge foncé ramifiées qui naissent sous le pied et s'étendent en 4-13 images, avec petits fragments noirs | 2D superposé ou décal animé : INCONNU |
| Éclairs de rage | 795-848, 1935-1956 | éclairs rouges épais qui partent du personnage, fond qui rougit | 2D : INFÉRÉ |
| Anneau d'onde | 818 | cercle fin qui s'étend autour du torse | 2D : INFÉRÉ |
| Éclats de peinture | 848 | petits fragments qui sautent du mur | 2D ou particules : INCONNU |
| Lignes d'impact | 1524-1544 | traits radiaux au sol autour des pieds | 2D : INFÉRÉ |
| Ombre géante | 1514-1544 | ombre du personnage agrandie sur le mur, plus grande que nature | lumière basse ou ombre dessinée : INCONNU |
| Blocs de béton | 1545-1556 | gros cubes blancs à arêtes vives | 3D : INFÉRÉ (ils tournent en perspective) |
| Texture CRT | 1393-1400 | lignes de balayage, bords bombés, qui s'effacent en entrant dans l'écran | compositing : INFÉRÉ |
| Faisceaux | 935-1150 | rayons de soleil dans l'air de la salle commune | volumétrique 3D : INFÉRÉ |
| Fondus | 109, 859, 1291, 1718 | fondus enchaînés d'environ 0,3 s | montage |

RECOMMANDATION : les effets d'émotion (éclairs, onde, lignes d'impact) sont graphiques, en 2D. Les ruptures du décor (blocs) sont en volume. Les deux cohabitent.

## 10. Son (sans écoute ; mesures seulement)
- MESURÉ : −14,2 LUFS intégré, plage 2,2 LU (voix très régulière), crête −1,9 dBTP, corrélation stéréo 0,994 (quasi mono), 104 attaques en 65 s, aucun silence de plus de 0,2 s sous −45 dB.
- INFÉRÉ : la voix est continue et la musique toujours présente, puisqu'il n'y a aucun silence. Les attaques coïncident avec le coup de pied (25,4 s) et la claque du bras de fer (34,8 s), ce qui suggère des bruitages d'impact synchronisés à l'image près.
- INCONNU : nature de la musique, timbre de la voix, identité des bruitages.

## 11. Texte à l'écran
- **Sous-titres** (OBSERVÉ sur toutes les planches) :
  - un ou deux mots à la fois, blanc gras arrondi, contour noir épais ;
  - centrés horizontalement, vers 70 % de la hauteur pour les cellules, plus haut sur les plans serrés ;
  - changement à chaque mot.
- **Texte diégétique** : voir §4 (P-618, POD C, C-4, 1979, matricules sur les combinaisons).

## 12. Constant dans cette vidéo, ponctuel, inconnu
- **Constant** :
  - caméra en mouvement ;
  - personnages blancs à contour noir ;
  - décors 3D propres ;
  - voix continue ;
  - sous-titres mot à mot ;
  - transitions sans coupe franche ;
  - couleur qui suit l'histoire.
- **Ponctuel** : la vue aérienne, la nuit, l'entrée dans l'écran CRT, l'ombre géante.
- **Inconnu** : logiciel, moteur, rig des personnages, nature exacte des effets 2D, musique.

## 13. Recettes réutilisables (RECOMMANDATION)
1. **Transition par un objet traversé** : porte, plafond, écran, personnage qui passe devant l'objectif ; fondu de 0,3 s seulement entre deux lieux sans lien spatial.
2. **Fait chiffré = objet en très gros plan sur le mot** : chronomètre, balance, fiche.
3. **Force = trace qui reste** : fissure, bloc au sol ; à vérifier au plan suivant.
4. **Émotion extrême = effet graphique 2D** (éclairs, onde, lignes) + changement de fond, sans changer de décor.
5. **Escalade en 3 temps** sur le même cadre (calme / cent pas / rupture), avec le chiffre dit à chaque temps.
6. **Couleur-sujet** : la teinte du décor raconte l'histoire ; l'éclairage colore les personnages par rebond.
7. **Nuit** = bascule de teinte globale au bleu + une seule source chaude sur le point d'intérêt.

## 14. Journal de couverture
Voir `data/V01/coverage.json`.
- Lu par le chef d'analyse : 4 planches overview (2 i/s, vidéo entière), `seq_750_797` (2 planches, image par image), `seq_1500_1571` planche 1 (1524-1547), `seq_1384_1407` (image par image).
- Captures : 69, faites par l'analyste précédent (session interrompue), réutilisées ; leurs noms et leur contenu ont été recoupés avec les planches overview.
- Couleurs : 16 échantillons + 8 k-means faits par le chef d'analyse.
