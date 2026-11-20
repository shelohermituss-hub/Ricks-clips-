# V02 — « Why Drivers Started Filming The Road » — analyse

Statuts : **OBSERVÉ**, **MESURÉ**, **INFÉRÉ**, **INCONNU**, **RECOMMANDATION**. Preuves : `evidence/V02/`. Catalogues : `data/V02/shots.csv`, `events.csv`, `assets.csv`, `palette.json`, `coverage.json`.

## 0. Fiche technique et couverture réelle
- MESURÉ :
  - 62,30 s, 1867 images, 720×1280, 30 i/s, H.264 ~1,59 Mb/s, AAC 44,1 kHz stéréo ;
  - −14,1 LUFS, plage 2,2 LU, crête −1,9 dBTP, corrélation stéréo 0,996 ;
  - 237 mots (3,83 mots/s), pause maximale 0,36 s.
- Couverture (statut **PARTIAL**, voir `coverage.json`) :
  - niveau A : 4 planches à 2 i/s lues en entier ;
  - niveau C : image par image sur 80-103 (premier choc) et 908-931 (choc de nuit) ;
  - 77 captures de l'analyste précédent réutilisées et recoupées avec les planches.

## 1. Structure et rythme
- **19 plans en 62 s** (durée médiane ≈ 3 s) : c'est la vidéo la plus découpée des cinq, avec 8 coupes franches vérifiées.
- Des **18 candidats** du détecteur, 10 sont l'essuie-glace qui balaie l'image dashcam (1710-1767) et non des coupes (vérifié à l'œil).
- Transitions :
  - coupes franches ;
  - fondus d'environ 0,3 s (144, 309, 960) ;
  - **recul à travers le pare-brise** (37) ;
  - **balayage d'essuie-glace** comme volet (1308) ;
  - **rembobinage** en fondu sur la vidéo dashcam (1691).
- Arc :
  - crochet par l'action (freinage à l'image 0) ;
  - l'arnaque, puis sa règle (« celui de derrière a toujours tort ») ;
  - la récompense, montrée par la matière : tampon, billets ;
  - répétition et méthode (choix des victimes, complice) ;
  - absurdité : il casse aussi sa voiture neuve ;
  - soupçon (assureur) ;
  - réponse effrontée ;
  - la cible calme sous la pluie ;
  - retournement par un geste (il montre la dashcam) ;
  - preuve (image dashcam) ;
  - chute : l'invention de la dashcam.
- **Voix et image** (MESURÉ) :
  - « smashes » → contact à 84 ;
  - « PAID » visible quand on entend « pays » (372) ;
  - « fifth neck injury » → compteur qui passe à 0 ;
  - « points at a little box » → doigt (1600) ;
  - « absolutely nothing » → voiture arrêtée sans contact (1790).

## 2. Timeline (résumé ; détail dans `shots.csv`)
| Plan | Images | Lieu / moment | Action |
|---|---|---|---|
| S01 | 0-39 | habitacle, jour | freinage et sourire mauvais ; recul à travers la vitre |
| S02-S03 | 40-143 | autoroute, jour | le SUV blanc percute l'arrière ; débris, panneau au sol |
| S04 | 144-208 | vue depuis le SUV | il sort en boitant, main au cou |
| S05 | 209-308 | autoroute arrêtée | faux pleurs, aparté narquois, bouchon |
| S06-S07 | 309-479 | pelouse de banlieue | tampon PAID, lit d'hôpital, explosion de billets |
| S08 | 480-555 | autre autoroute | 2e arnaque (voiture turquoise) |
| S09 | 555-830 | autoroute au crépuscule | choix des victimes, complice qui encadre |
| S10 | 831-884 | garage | geyser de billets |
| S11 | 884-960 | allée, nuit | voiture de sport neuve qui tombe du ciel, choc, aile sur le toit |
| S12 | 960-1100 | bureau d'assurance | appel, compteur 2 → 0 |
| S13 | 1101-1160 | piscine, nuit | « really weak neck » |
| S14 | 1161-1307 | allée, nuit | le policier verbalise l'autre conducteur |
| S15-S17 | 1308-1656 | pluie | homme calme, freinage, il montre la dashcam |
| S18 | 1657-1829 | vue dashcam | preuve : route vide, freinage pour rien |
| S19 | 1830-1866 | intérieur du break | sourire final |

## 3. Personnages
- Même famille que les autres vidéos :
  - tête blanche ronde à contour noir épais ;
  - membres en traits noirs ;
  - torse habillé coloré : t-shirt jaune de l'escroc, chemise verte de la victime, costume de l'assureur, uniforme et chapeau de ranger du policier, chemise bordeaux de l'homme calme.
- Rôles lus aux accessoires : chapeau de policier, costume et cravate, lunettes posées sur la tête de l'escroc (OBSERVÉ, `V02_f00030_crop_driver_design.jpg`).
- **Personnages dans les voitures** :
  - tous les conducteurs sont visibles derrière des **vitres claires** (OBSERVÉ à 75-135, 590-830) ;
  - leur visage réagit au choc : yeux ronds du conducteur du SUV à 99-103 (OBSERVÉ image par image).
- **Expressions** :
  - fausse douleur (yeux plissés, bouche ouverte) et sourire en coin en aparté, regard caméra (222) ;
  - l'homme calme reste impassible (paupières mi-closes) du début à la fin, sauf le sourire final (1860) ;
  - goutte de sueur sur l'escroc quand il comprend (1650-1680) (OBSERVÉ).
- **Corps** : saut hors du lit (398, en l'air), danse sur le tas de billets (870), boiterie exagérée.
- **Micro-animations** : main qui reste au cou (geste-signature répété 170, 1447-1480) ; doigt pointé tenu (1600) ; tête qui se colle à la vitre (1648) (OBSERVÉ).

## 4. Environnements et assets
- **Lieux** : autoroute de jour (glissières, murs antibruit, arbres en rideau), autoroute au crépuscule, banlieue (maisons à bardage blanc, pelouses), bureau en hauteur (gratte-ciel derrière la baie), jardin et piscine de nuit, allée de nuit, route sous la pluie, habitacles détaillés.
- **Véhicules** (assets héros, `assets.csv`) :
  - berline rouge (peinture vernie, reflets du ciel), SUV blanc (calandre chromée), voiture de sport vert acide à portes papillon, vieux break beige à bandeau bois ;
  - intérieurs détaillés : compteurs, volant, sièges en velours (OBSERVÉ 150-200, 1500-1650) ;
  - **vitres claires** partout.
- **Faits écrits dans le décor** : tampon « PAID », compteur sur le bureau de l'assureur, incrustations dashcam (date, heure, vitesse en MPH, « REC »).
- **Matière en masse** : liasses de billets en grand nombre qui forment des tas et restent dans le décor (OBSERVÉ 462, 850-960, 1200).
- **Détails** :
  - asphalte gris clair à grain fin avec traces de pneus ;
  - herbe 3D au premier plan, caméra au ras du sol (330) ;
  - les surfaces sont propres, la richesse vient des objets.

## 5. Caméra
- Mouvement médian 4,9 / 255 par image, 3,1 % d'images quasi fixes (MESURÉ). C'est la vidéo la plus stable ; le plan dashcam (S18) est volontairement fixe.
- **Grammaire** :
  - travelling latéral à la vitesse des voitures (S02, S08, S09, S15) ;
  - caméra basse au ras de la route ou de l'herbe (40-98, 330) ;
  - vue subjective du conducteur avec tableau de bord au premier plan (S04, S16) ;
  - plan intérieur serré (S01, S17) ;
  - image dans l'image (S18).
- **Focale apparente** : courte sur les voitures (forte perspective sur le capot à 41, `V02_f00041_S02_front_closeup_wide_lens.jpg`), environ 18-24 mm (INFÉRÉ).
- **Choc caméra** : léger à l'impact (84-90) (OBSERVÉ).
- **Recettes** (RECOMMANDATION) :
  - « travelling de voiture » : caméra qui roule à la vitesse du sujet, le décor défile, le sujet reste cadré ;
  - « recul à travers la vitre » pour sortir d'un habitacle sans coupe.

## 6. Lumière, palettes, étalonnage
| Ambiance | Où | Lumière (OBSERVÉ) | Palette (MESURÉ) |
|---|---|---|---|
| Jour autoroute | S02-S05, S08 | soleil dur, ombres nettes sous les voitures, ciel bleu profond | ciel #2687e7 / #0f7fe6 (S 93 %), asphalte #888894, accent rouge #db172e |
| Jour banlieue | S06-S07 | soleil, herbe saturée | #1576e6, herbe #5b7f31, bardage #cbcdd7 |
| Crépuscule | S09 | ciel lavande, phares allumés, contre-jour | #8a63d7, route #4d2d46, rouge #f01e24 |
| Nuit | S11, S13, S14 | ciel outremer, sources chaudes locales (phares, guirlandes, éclairage de porte) | #07187a, végétation #1f2c1a |
| Bureau | S12 | jour par la baie vitrée | bois #a0542b, ciel #739fd7 |
| Pluie | S15-S17 | couvert, désaturé, gouttes et reflets | #596f72, #2c4042 ; saturation 0,26-0,30 (la plus basse) |

- Saturation par seconde de 0,26 (pluie) à 0,68 (nuit), luminosité de 0,20 à 0,62 (MESURÉ) : **cinq ambiances en 62 s**, chacune liée à une étape de l'histoire. La pluie annonce le retournement.
- Étalonnage : noirs relevés le jour, plus profonds la nuit ; pas de grain ; léger halo sur les phares (OBSERVÉ 600, 900).
- **Reconstruction proposée** :
  - ciel HDRI saturé ou ciel procédural bleu profond ;
  - crépuscule = ciel violet + lampes de phares (spots) + exposition légèrement basse ;
  - nuit = monde bleu, lampes ponctuelles chaudes ;
  - pluie = brume légère, désaturation au compositing, particules de pluie, rugosité basse sur la route mouillée.

## 7. Animation de l'environnement
- Décor qui défile pendant les travellings.
- Billets qui volent et retombent (450-475, 840-880).
- Pluie continue (S15-S17).
- Essuie-glaces (S16, S18).
- Eau de la piscine qui ondule (S13) (OBSERVÉ).

## 8. Interactions et conséquences
**E01, premier choc arrière (40-130, image par image 80-103)** :
1. État initial : la voiture rouge roule devant le SUV blanc.
2. Anticipation : fumée de pneus au freinage (60).
3. Contact à 84 : l'avant du SUV entre dans l'arrière rouge (84-90).
4. Réaction : le pare-chocs rouge se détache et pend (90-98) ; petits débris rouges et noirs projetés vers l'arrière et vers le haut (92-98).
5. Effets secondaires : vapeur et feux stop allumés au gros plan (118) ; visage du conducteur du SUV qui passe de neutre à effrayé (99-103).
6. État final : voitures emboîtées.
7. Persistance : un panneau de carrosserie reste au sol (126) (OBSERVÉ).

**Ce qui n'est PAS montré** dans ce choc : pas de verre brisé, pas d'airbag, pas de capot plié en accordéon, pas de fumée de moteur (OBSERVÉ sur les images 80-143).

**E08, choc de nuit (884-960, image par image 908-931)** :
1. La voiture de sport tombe du ciel avec un nœud rouge (890).
2. Ses portes papillon s'ouvrent et se ferment (903-912).
3. Elle part et frappe une camionnette blanche (921-927).
4. **Étincelles** orange et débris noirs projetés (927-931), puis fumée du capot.
5. Gag : l'aile retombe sur le toit (955).
6. Persistance : la voiture est encore accidentée et fumante au plan S14 (1155-1290) (OBSERVÉ).

**Règle observée** : chaque choc a une anticipation (fumée de pneus ou freinage), un contact sur une image, des débris projetés dans le sens du choc, une pièce qui se détache ou tombe, et une trace qui reste au plan suivant. La nuit ajoute des étincelles visibles.

## 9. VFX
- Fumée de pneus : volume gris clair au ras du sol (60).
- Débris : petits fragments sombres en particules (92-98, 927-931).
- Vapeur : bouffée claire (118).
- Étincelles : traits orange courts, nuit (927-931).
- Fumée de moteur : colonne grise (955).
- Billets : instances de liasses en gerbe puis en tas (462, 850).
- Étincelles brillantes 2D autour du tampon (383).
- Pluie : traits fins et gouttes sur les vitres.
- Incrustations HUD dashcam en 2D (1657-1829) ; rembobinage en fondu (1691).

Méthodes : les billets, débris et étincelles sont en 3D ou en particules (INFÉRÉ, ils suivent la perspective) ; les étincelles du tampon et le HUD sont en 2D (INFÉRÉ).

## 10. Son (mesures seulement)
- Voix continue (aucun silence) ; plage 2,2 LU.
- Attaques compatibles avec les chocs (2,8 s ; 30,9 s) et le tampon (12,4 s) (INFÉRÉ).
- Musique, bruitages et timbre : INCONNU.

## 11. Texte à l'écran
- Sous-titres mot à mot, blanc gras à contour noir, centrés, au tiers inférieur sur les plans larges et plus haut sur les plans serrés (OBSERVÉ).
- Textes diégétiques : PAID, compteur, HUD dashcam.

## 12. Constant / ponctuel / inconnu
- **Constant** :
  - voitures vernies à vitres claires avec conducteur visible ;
  - caméra en mouvement à la vitesse du sujet ;
  - personnages blancs à contour noir ;
  - voix continue ;
  - conséquences matérielles qui restent (billets, épaves).
- **Ponctuel** : crépuscule violet, pluie, image dashcam, piscine.
- **Inconnu** : moteur de rendu, méthode des personnages (2D intégrée, INFÉRÉ), musique.

## 13. Recettes (RECOMMANDATION)
1. **Choc de véhicule à 5 temps** : fumée de pneus, contact sur 1 image, pièce qui se détache, débris dans le sens du choc, pièce qui reste au sol au plan suivant. La nuit, ajouter des étincelles.
2. **Récompense = matière qui déborde** : billets, objets en masse qui s'empilent et restent dans le décor.
3. **Une ambiance par étape de l'histoire** : jour → crépuscule → nuit → pluie au retournement.
4. **Preuve = image dans l'image avec données** (date, vitesse, REC).
5. **Geste-signature** répété : la main au cou, à chaque occurrence de l'arnaque.
6. **Retournement sans parole** : un personnage impassible fait un geste minimal vers l'objet-preuve.

## 14. Journal de couverture
Voir `data/V02/coverage.json`. Lu par le chef d'analyse :
- 4 planches overview ;
- `seq_56_127` planche 1 (80-103, image par image) ;
- `seq_884_967` planche 1 (908-931, image par image) ;
- 15 échantillons de couleur (6 rejetés car hors de l'objet) et 8 k-means.
