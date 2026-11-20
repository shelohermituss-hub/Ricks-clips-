# V03 — « He Survived Falling Out Of A Plane » — analyse

Statuts : **OBSERVÉ**, **MESURÉ**, **INFÉRÉ**, **INCONNU**, **RECOMMANDATION**. Preuves : `evidence/V03/` (43 captures faites par le chef d'analyse). Catalogues : `data/V03/*.csv`, `palette.json`, `coverage.json`.

## 0. Fiche technique et couverture réelle
- MESURÉ :
  - 83,08 s, 2490 images, 720×1280, 30 i/s, H.264 ~1,67 Mb/s ;
  - −13,9 LUFS, plage **3,9 LU** (la plus large des cinq), crête −0,9 dBTP ;
  - 264 mots (3,21 mots/s, le débit le plus lent), pause maximale 0,64 s.
- Couverture (statut **PARTIAL**) :
  - niveau A : 5 planches à 2 i/s lues en entier ;
  - niveau C : image par image sur 96-119 (porte arrachée) et 1998-2021 (glissière défoncée) ;
  - le reste à 2 i/s.

## 1. Structure et rythme
- **18 plans en 83 s**, durée médiane ≈ 4 s.
- Structure en **anthologie** : un premier accident long (plans S01 à S08, environ 27 s), puis trois accidents courts introduits par un **panneau de temps écrit dans le décor** (« 5 YEARS LATER » sur un panneau de rue, « 10 YEARS LATER GRAND CANYON » sur un panneau routier, « 15 YEARS LATER » sur un écran de caisse), puis la chute qui paie l'objet planté au début (billet de loterie).
- **Transitions** :
  - la caméra suit le héros aspiré par la porte (continu, 96-167) ;
  - **vision tunnel jusqu'au noir** (435-509) ;
  - **réouverture floue** au réveil (510-560) ;
  - **objet géant plein cadre** : un billet qui remplit l'écran (1040) ;
  - coupes franches ;
  - fondu rapide pendant le choc (1998-2005) ;
  - **flashback en noir et blanc** (2280-2330).
- **Voix et image** (MESURÉ) :
  - « burst open » → étincelles puis flash (107-113) ;
  - « a haystack » → la meule imaginée (345-375) ;
  - « passed out » → vignettage (435) ;
  - « 50 feet » → repère « 50 FT » écrit sur la falaise (2100-2115) ;
  - « jackpot » → écran JACKPOT (2445).

## 2. Timeline (résumé ; détail dans `shots.csv`)
| Plan | Images | Lieu | Action |
|---|---|---|---|
| S01-S02 | 0-95 | avion Lucky Air, cabine | il boit un soda près de la porte |
| S03-S04 | 96-167 | porte | étincelles aux rivets, flash, porte arrachée, aspiration |
| S05 | 168-359 | ciel au-dessus des champs | 20 personnes tombent, lui cherche une meule de foin |
| S06-S07 | 360-509 | meule imaginée, puis vue subjective | il s'évanouit, vision qui se ferme en noir |
| S08 | 510-818 | hôpital | réveil flou, « achète un billet de loterie » |
| S09 | 819-1049 | rue dorée | « le plus malchanceux / chanceux » : cheveux brûlés, pluie de billets |
| S10-S12 | 1050-1409 | train, Alaska | déraillement dans le lac, il ressort bleu de froid |
| S13 | 1410-1649 | caserne | 5 ans plus tard : la voiture explose devant les pompiers |
| S14-S17 | 1650-2219 | Grand Canyon | 10 ans plus tard : camion, glissière défoncée, éjection, branche |
| S18 | 2220-2489 | supérette | 15 ans plus tard : flashback, billet, jackpot |

## 3. Personnages
- **Héros** : tête blanche à contour noir, cheveux bruns en pointes, gilet orange sur chemise bleue, membres en traits noirs.
- **Variantes de costume selon l'époque** :
  - bonnet rouge et doudoune au train ;
  - t-shirt jaune à motif au canyon ;
  - survêtement violet et barbe naissante à la fin, plus âgé ;
  - même visage dans toutes les variantes (OBSERVÉ `V03_f01380_*`, `V03_f02115_*`, `V03_f02445_*`).
- **Personnages secondaires** : médecin aux cheveux gris et moustache (`V03_f00690_crop_personnage_medecin.jpg`), infirmière masquée, caissier à casquette, passagers variés (costume, rayures).
- **Expressions fortes** :
  - yeux ronds et bouche grande ouverte en chute ;
  - yeux mi-clos d'évanouissement ;
  - dents qui claquent ;
  - **yeux en symboles $** (900, 2445) ;
  - cheveux qui se dressent, brûlés (870).
- **Conséquences sur le corps** :
  - peau bleue de froid avec un glaçon sur la tête (1380) ;
  - pansements et bleus après les accidents (900-945, visage marqué) ;
  - cheveux brûlés (870) (OBSERVÉ).
- **Micro-animations** :
  - buée qui sort de la bouche dans le froid (1350-1395) ;
  - grelottement ;
  - cheveux et vêtements secoués par le vent en chute (OBSERVÉ, 2 i/s) ;
  - corps des passagers qui tournent chacun à leur vitesse (195-285).

## 4. Environnements et assets
- **Le plus grand nombre de lieux des cinq vidéos** : 9 lieux, chacun avec sa propre ambiance.
  - Lieux : avion, ciel, ferme, hôpital, rue commerçante, train, Alaska (viaduc, lac gelé, montagnes enneigées), caserne, Grand Canyon, supérette.
- **Profondeur** :
  - champs en damier jusqu'à l'horizon pendant la chute ;
  - falaises stratifiées en plusieurs couches de profondeur au canyon ;
  - montagnes enneigées en fond de l'Alaska (OBSERVÉ).
- **Assets** (16, `assets.csv`) :
  - héros : porte de cabine (étiquettes lisibles), canette, billet de loterie, voitures du héros ;
  - secondaires : avion, viaduc et train, caserne et camion de pompiers, camion, supérette.
- **Textes diégétiques** (OBSERVÉ) :
  - logo « LUCKY AIR » (le nom porte le thème) ;
  - « EXIT », journal « GREGS CLIPS », « NEXT STOP: ALASKA » ;
  - panneaux de temps, « 50 FT », « MUST BE 21 », « LOTTERY », « CHECKING », « JACKPOT $1,000,000 », fiche « CONCUSSION ».
- **Détails** : la porte de cabine a des rivets, des étiquettes et une poignée lisibles en plan rapproché (96) ; rayons de supérette remplis de paquets colorés ; strates nettes sur les falaises proches.

## 5. Caméra
- Mouvement médian **15,5 / 255 par image**, de loin le plus élevé des cinq (MESURÉ) : la caméra tombe avec le personnage, survole le canyon et tremble aux chocs.
- **Grammaire** :
  - caméra qui chute avec les personnages (168-359) ;
  - vue subjective avec vignettage (435-509) ;
  - vue subjective du conducteur avec compteurs au premier plan (1785-1997) ;
  - **survol aérien** des lacets (1740-1785) ;
  - plan latéral fixe pendant le choc (2006-2021) ;
  - poussée vers le visage aux moments de réaction.
- **Mise au point** : flou de réveil qui revient progressivement (510-560) ; c'est la seule utilisation nette d'une profondeur de champ comme effet narratif (OBSERVÉ).
- **Recettes** (RECOMMANDATION) : « caméra en chute libre avec le sujet » ; « vision tunnel → noir → réouverture floue » pour une ellipse de perte de conscience.

## 6. Lumière, palettes, étalonnage
Dix ambiances distinctes (MESURÉ par k-means, `palette.json`) :

| Ambiance | Palette | Lumière (OBSERVÉ) |
|---|---|---|
| Ciel au-dessus des nuages | #89a3ee, #dfe3eb | soleil, nuages blancs volumineux |
| Ferme rêvée | #5783c8 | **rayons volumétriques** sur la meule |
| Hôpital au réveil | #97af9f, #8d928f | saturation 0,11-0,20 (MESURÉ 16-26 s) : désaturation narrative |
| Rue dorée | #ac7a53, #ecc66e | soleil bas rasant, ombres longues, façades dorées |
| Intérieur du train | #48251a, #912c2d | lampes chaudes, neige bleue dehors |
| Alaska | #1e4688, #4b7dbd, accent bonnet #8d1d33 | froid bleu, neige |
| Feu au crépuscule | #da773a sur #314ea8 | contraste chaud (feu) / froid (ciel) |
| Grand Canyon | #d85e13, #a04721 | soleil chaud, roches orange saturées |
| Flashback | gris #e1dfe0 à #3f3d3f | **noir et blanc** (saturation 0,02, MESURÉ 77 s) |
| Jackpot | #e3ce5e | bascule globale au doré, rayons |

- Saturation par seconde de 0,02 à 0,76, la plage la plus large des cinq (MESURÉ). **L'étalonnage sert l'émotion** :
  - désaturé = sonné ou souvenir ;
  - saturé chaud = danger (feu, canyon) ;
  - doré = récompense.
- **Effets de lumière** :
  - flash blanc plein cadre aux explosions (110-113 ; 1545) ;
  - contre-jour solaire avec halo derrière la branche (2175) ;
  - phares éblouissants du camion (1845-1935) (OBSERVÉ).
- **Reconstruction proposée** :
  - désaturation et flou au compositing pour le réveil ;
  - flashback = compositing noir et blanc ;
  - explosion = lampe ponctuelle très forte sur 2 images + bloom ;
  - canyon = soleil chaud + matériau de roche stratifiée saturé.

## 7. Animation de l'environnement
- Nuages qui défilent, avion qui s'éloigne (168-359).
- Oiseau près de la meule (360).
- Feu animé qui monte et ondule (1560-1649).
- Jet d'eau de la lance (1620-1640).
- Billets et confettis qui tombent (975-1035, 2445-2489).
- Rochers qui roulent de la falaise (2130-2219) (OBSERVÉ).

## 8. Interactions et conséquences
**E01, porte arrachée (96-140, image par image 96-119)** :
1. État initial : porte fermée, canette au premier plan.
2. Anticipation : une étincelle naît sur un rivet à 102, puis d'autres, une par une, tout autour du cadre (102-109).
3. Contact et rupture : flash blanc à 110 qui sature l'image.
4. Déplacement : la porte part vers l'extérieur (112-119).
5. Effets secondaires : papiers et objets aspirés vers le trou, la canette suit (110-119).
6. La caméra tremble.
7. État final : trou béant ; le héros est aspiré au plan suivant (150) (OBSERVÉ).

**E08, glissière défoncée (1998-2084, image par image 1998-2021)** :
1. Transition : fondu de la vue subjective vers le plan latéral (1998-2005).
2. Contact de la voiture bleue contre la glissière à 2006.
3. **Le capot se froisse et se relève** en 5 images (2008-2013).
4. Les poteaux de glissière sont arrachés et se dressent (2018-2021).
5. Débris de roche et poussière.
6. La voiture bascule dans le vide ; le héros est **éjecté par la portière** (2040), puis tombe de 50 pieds (2085-2115).

**Comparaison importante** : ici la carrosserie **se déforme réellement** (capot froissé, OBSERVÉ), alors que le choc arrière de V02 ne montrait qu'un pare-chocs détaché. L'intensité de la déformation suit la violence du choc.

**E05, déraillement** : cause visible d'abord (les rails s'écartent, 1170-1185), puis chute du viaduc (1245-1260), puis gerbe d'eau et de glace (1275-1290) ; le héros ressort de l'eau au plan suivant.

## 9. VFX
| Effet | Où | Description (OBSERVÉ) | Méthode |
|---|---|---|---|
| Étincelles de rupture | 102-109 | étoiles lumineuses qui naissent sur les rivets | 2D lumineux ou particules : INCONNU |
| Flash | 110-113, 1545 | blanc plein cadre | compositing : INFÉRÉ |
| Traits de vitesse | 141-170, 300-345 | traits blancs dans le ciel | 2D : INFÉRÉ |
| Vignettage de perte de conscience | 435-509 | bord noir qui se resserre | compositing |
| Flou de réveil | 510-560 | flou qui diminue | compositing ou profondeur de champ |
| Éclair de malchance | 870 | trait 2D autour de la tête | 2D |
| Billets | 975-1035 | billets qui tombent en grand nombre | 3D : INFÉRÉ |
| Gerbe d'eau et glace | 1275-1295 | éclaboussures blanches | 3D ou particules : INFÉRÉ |
| Buée, glaçon | 1350-1395 | — | 2D et 3D |
| Feu | 1560-1649 | flammes orange qui éclairent le décor | volume ou cartes animées : INCONNU |
| Jet d'eau | 1620-1640 | — | particules : INFÉRÉ |
| Poussière, débris de roche | 2006-2219 | — | particules |
| Rayons dorés, confettis | 2445-2489 | — | 2D et particules |

## 10. Son (mesures seulement)
- Plage de 3,9 LU et crête à −0,9 dBTP : c'est la seule vidéo où les effets montent nettement au-dessus de la voix (INFÉRÉ : explosions et chocs).
- Débit de voix le plus lent (3,21 mots/s) : la vidéo est plus longue et plus « racontée ».
- INCONNU : musique et bruitages.

## 11. Texte à l'écran
- Sous-titres mot à mot identiques aux autres vidéos.
- **Le temps qui passe est écrit dans le décor** (panneau de rue, panneau routier, écran), jamais en carton plein écran (OBSERVÉ).

## 12. Constant / ponctuel / inconnu
- **Constant** :
  - caméra très mobile ;
  - une ambiance de couleur par lieu ;
  - textes diégétiques ;
  - conséquences visibles sur le corps du héros.
- **Ponctuel** : noir et blanc, vision tunnel, flou de réveil.
- **Inconnu** : méthode des effets de feu et d'eau, musique.

## 13. Recettes (RECOMMANDATION)
1. **Anthologie datée** : chaque saut de temps est écrit sur un objet du décor du nouveau lieu (panneau, écran), au premier plan.
2. **Rupture annoncée** : étincelles une par une sur les points d'attache, puis flash plein cadre, puis aspiration ou projection.
3. **Déformation proportionnée** : un choc violent froisse la carrosserie et arrache le décor (glissière) ; un choc léger fait juste tomber une pièce.
4. **Étalonnage émotionnel** : désaturé et flou = sonné ; noir et blanc = souvenir ; doré = récompense ; orange saturé = danger.
5. **Objet planté puis payé** : le billet de loterie montré au plan 8 revient au dernier plan.
6. **Le corps garde la trace** : bleus, cheveux brûlés, peau bleue, costume qui change avec l'âge.

## 14. Journal de couverture
Voir `data/V03/coverage.json`. Lu par le chef d'analyse :
- 5 planches overview ;
- `seq_96_167` planche 0 (96-119, image par image) ;
- `seq_1998_2060` planche 0 (1998-2021, image par image) ;
- 43 captures ;
- 14 k-means.

## 15. Compléments image par image (20/11, priorité 3)
- **Explosion de la voiture 1540-1563** (OBSERVÉ image par image) :
  - il démarre, le visage passe de grimaçant (1540-1545) à des yeux ronds (1546-1551), soit 0,2 s d'anticipation sur le visage ;
  - **flash jaune plein cadre à 1552**, sur 4 images (1552-1555) ;
  - pendant le flash, le personnage est **projeté vers le haut** (1556-1559), cheveux dressés et noircis, taches de suie sur le visage ;
  - les flammes orange apparaissent à 1560 et éclairent la façade ;
  - une passante entre au premier plan, bouche ouverte (1560) ;
  - la voiture reste en flammes.
