# Analyse — « The Instinct That Makes You Crash » (vidéo de CB, à reproduire)

Source : `references/crash_instinct/source.mp4`, envoyée par CB le 19/11 (gardée en local, ignorée par Git).
Déjà versionnés : mesures (`summary.json`, `ref_measures.json`, `loudness.json`), transcription mot à mot (`words.json`), planches à 2 i/s (`sheet_00..05.jpg`).

## 0. Droits (précisé par CB le 19/11)

CB est l'auteur de cette vidéo (« C'est ma vidéo »). But : la **reproduire entièrement** : même narration, mêmes plans, même style, tout recréé par nous (modèles, décors, personnages, animation, son). Aucune image ni aucun son de la source n'entre dans le résultat ; elle sert uniquement de référence de comparaison.

## 1. Fiche technique (mesurée)

| | Valeur |
|---|---|
| Format | 720×1280 (9:16), 30 i/s, H.264 1,6 Mb/s, AAC stéréo 44,1 kHz |
| Durée | **59,49 s**, 1 783 images |
| Narration | 217 mots, **3,67 mots/s**, pause max 0,36 s |
| Loudness | **−14,0 LUFS**, plage 2,5 LU |
| Mouvement (médiane par seconde) | 25,6 ; pics d'action 8,4 / 10 s |
| Image | luminance 0,43 ; **saturation 0,29** (la plus basse des 7 : herbe et ciel désaturés le jour, nuit bleu-gris) |
| Coupes franches (différence d'image, mesurée) | images 96, 658, 687, 732, 815, 938, 1069, 1122, 1206, 1232, 1369, 1473, 1552, 1638, 1754. De 3,2 à 21,9 s, tout s'enchaîne en **mouvements et fondus** |

## 2. Structure du récit

Crochet (« If you plant a tree… cars will steer right into it ») → « You see » (la route droite, l'arbre unique) → escalade (un crash par semaine, la flèche, les crashs doublent, le dépanneur s'enrichit) → le shérif (crash à 15 mph, l'arbre abattu) → retournement (il percute la souche) → explication (« target fixation », nuit, pluie, vue conducteur) → chute (« Even when it's just a stump »).

## 3. Découpage plan par plan

Temps en secondes ; images entre crochets (30 i/s). « Coupe » = coupe franche mesurée ; « enchaîné » = transition par mouvement ou fondu, à préciser en 10 i/s dans `shots/sNN.md`.

| # | Temps | Narration | Lieu et décor | Caméra | Action | Sortie |
|---|---|---|---|---|---|---|
| 1 | 0,0 – 3,2 [0–95] | If you plant a tree beside an empty road, cars will steer right into it. | Bord de route de campagne plate : herbe haute, clôture barbelée à piquets en bois, route grise à ligne blanche, champs, ciel pâle à gros nuages | Plan moyen sur le héros, puis **recul et descente rapides** (0,8–1,5 s) au niveau de la route, puis lente dérive | Le héros (chemise vert-bleu, casquette de camionneur rouge et blanche) jette une graine dans un trou ; **un grand arbre tombe du ciel** et se plante ; le choc le projette assis dans l'herbe ; une voiture blanche arrive et **dévie droit vers l'arbre** (poussière) | coupe |
| 2 | 3,2 – 5,5 | You see, the road runs dead | Pied de l'arbre, gros plan bas | Plan serré, puis recul | La voiture s'écrase contre le tronc : feuilles qui tombent, **un pneu roule** jusqu'au héros assis ; capot fumant | enchaîné |
| 3 | 5,5 – 8,0 | straight for miles. And the only thing beside it | **Vue aérienne** : route rectiligne jusqu'à l'horizon, champs labourés en bandes, l'arbre seul avec son ombre longue | Survol lent, légère descente | — | enchaîné |
| 4 | 8,0 – 9,5 | is this one tree. But | Arbre au bord de la route, voiture accidentée dessous, héros | Approche au ras de la route | — | enchaîné |
| 5 | 9,5 – 12,0 | somehow, somebody hits it every week. | Panneau **« DAYS SINCE LAST CRASH » 7** cloué à l'arbre | Plan fixe-dérive sur le panneau | Une voiture bleue percute l'arbre (10,5) ; le chiffre passe **à 0** (11,5), pile de pneus | enchaîné |
| 6 | 12,0 – 13,0 | So the town nails a | Tronc, échelle | Gros plan | Ouvrier de la ville (casque orange, gilet vert) sur l'échelle, cloue | enchaîné |
| 7 | 13,0 – 15,5 | giant flashing arrow to it so nobody can miss it. | **Flèche géante à ampoules « DON'T HIT THIS TREE »** fixée à l'arbre, boîtier électrique | Plan moyen, léger travelling | Les ampoules clignotent ; deux ouvriers (casques blancs) contents | enchaîné (la lumière passe au **soir**) |
| 8 | 15,5 – 17,0 | Yet the crashes double. | Même lieu au crépuscule | Plan moyen | Une voiture jaune **et** une voiture bleu-vert percutent l'arbre | **fondu enchaîné** |
| 9 | 17,0 – 19,0 | The tow truck guy starts parking out there | Dépanneuse rouge « TOWING 24 HR », panneau sur le toit **« TREE TOWING – $ CASH ONLY $ »**, parasol | Plan rapproché, recul | Le dépanneur (casquette) assis dans la cabine, se penche | enchaîné |
| 10 | 19,0 – 21,9 | with a lawn chair. And he's never made more money in his life. | Bord de route : chaise longue, voiture bleue écrasée, flèche | Plan moyen, travelling | Il s'installe dans sa chaise longue, lunettes de soleil, **billets qui volent** | coupe |
| 11 | 21,9 – 22,9 | Eventually, the sheriff | Panneau **« SHERIFF'S OFFICE »** (étoile), voiture de shérif vert et blanc | Gros plan à la portière | Le shérif (chapeau de cow-boy marron, lunettes d'aviateur, moustache) au volant | coupe |
| 12 | 22,9 – 24,4 | drives out to see what's going on. | Petite ville : briques, cheminées d'usine qui fument, feux | Caméra derrière la voiture qui s'éloigne | La voiture quitte la ville | coupe |
| 13 | 24,4 – 27,2 | He goes 15 miles an hour with both hands on the wheel and | Radar **« YOUR SPEED 15 »**, piéton (violet) | Plan large, puis gros plans dans l'habitacle | Le piéton le dépasse à pied ; mains à 10 h 10 | coupe |
| 14 | 27,2 – 31,3 | slams right into it. He climbs out furious, grabs an ax off the tow truck, | Arbre, flèche, dépanneuse | Profil puis face au shérif | La voiture percute l'arbre ; il sort, **yeux rouges lumineux**, débris qui tournoient ; il prend la hache sur la dépanneuse | coupe |
| 15 | 31,3 – 35,6 | and chops the thing down. While the tow truck guy watches his whole business fall over. | Arbre ; ciel qui s'ouvre (rayons) ; champ et clôture | Rotations rapides, puis plan sur le dépanneur | Coup de hache (éclair), **l'arbre s'envole dans une tornade**, trou de ciel ; le dépanneur dans sa chaise regarde, la clôture tombe | coupe |
| 16 | 35,6 – 37,4 | The second his cruiser's fixed, the sheriff | **Garage** intérieur, néons | Plan moyen | Voiture cabossée, pare-brise étoilé → réparée (37,0), le dépanneur-mécanicien sourit | coupe |
| 17 | 37,4 – 40,2 | drives back out to enjoy his nice empty road and | Route droite, champs | Portière, puis vue aérienne qui suit | Le shérif repart content | coupe |
| 18 | 40,2 – 41,1 | plows straight into | Souche, flèche, champs | Profil latéral | La voiture **se dresse à la verticale** sur la souche | coupe |
| 19 | 41,1 – 43,4 | the stump. So how does this keep happening? | Idem ; puis gros plan | Profil, puis très gros plan du shérif | La voiture retombe, poussière ; visage du shérif ahuri | enchaîné |
| 20 | 43,4 – 45,6 | Well, it's called target fixation. | **Nuit, pluie** : vue conducteur sur la route, panneau vert **« TARGET FIXATION »** | Caméra embarquée | — | coupe |
| 21 | 45,6 – 49,1 | After miles of nothing, that tree sticks out like a lighthouse. | Nuit, pluie, route infinie ; l'arbre au loin éclairé **comme un phare** (faisceaux) | Caméra derrière un SUV blanc | — | coupe |
| 22 | 49,1 – 51,7 | Especially with a giant flashing arrow pointing at it. | Vue conducteur, essuie-glaces ; la flèche clignote près de l'arbre | Caméra embarquée, approche | — | coupe |
| 23 | 51,7 – 54,6 | So every driver's eyes lock onto it and won't let go. | Shérif dans sa voiture la nuit (désodorisant sapin) | Gros plan par le pare-brise, push-in | Ses yeux deviennent des **spirales hypnotiques**, visage éclairé par la flèche | coupe |
| 24 | 54,6 – 58,5 | And while they stare, their hands slowly turn the wheel toward it. Even when it's just a | Vue conducteur | Caméra embarquée | **Le volant tourne lentement** vers la souche et la flèche | coupe |
| 25 | 58,5 – 59,5 | stump. | Nuit : flèche et souche, voiture de shérif | Plan large latéral | La voiture percute la souche (gerbe, éclat) | fin |

## 4. Bible du look (observée)

- **Monde** : 3D cartoon, même famille que crashed_car, mais **moins saturé** (0,29) : herbe vert tendre, ciel bleu pâle à nuages blancs, route gris clair.
- **Arbre héros** : grand feuillu (chêne) à tronc épais très texturé (écorce), feuillage en paquets de feuilles stylisées, ombre longue ; il est **le même objet** dans tout le film (planté → panneau → flèche → abattu → souche).
- **Lumière** : jour franc (soleil bas latéral, ombres longues) ; crépuscule orangé (plan 8) ; **nuit pluvieuse bleu-gris** avec phares, faisceaux et ampoules de la flèche (plans 20 à 25).
- **Personnages** : cartes 2D de notre distribution. Héros/dépanneur : chemise vert-bleu, casquette rouge et blanche. Shérif : chapeau de cow-boy marron, lunettes d'aviateur dorées, moustache, uniforme kaki. Ouvriers : casque orange ou blanc, gilet vert fluo. Piéton : chemise violette.
- **Accessoires et textes dans le décor** : « DAYS SINCE LAST CRASH » (chiffre 7 → 0), flèche à ampoules « DON'T HIT THIS TREE », « TREE TOWING – $ CASH ONLY $ », « TOWING 24 HR », « SHERIFF'S OFFICE », « YOUR SPEED 15 », « TARGET FIXATION », « SHERIFF » sur la portière.
- **Véhicules** : voiture blanche (berline/SUV), voiture bleue, jaune, bleu-vert, dépanneuse rouge, voiture de shérif vert et blanc à gyrophares.
- **Effets** : poussière à l'impact, pneu qui roule, feuilles qui tombent, billets, yeux rouges lumineux, tornade de débris, rayons de ciel, éclair du coup de hache, pluie, faisceaux de phare, yeux en spirale.
- **Sous-titres** : identiques aux autres vidéos (1 à 3 mots, blancs, gras, contour noir, vers 70 % de la hauteur).

## 5. Méthode de reproduction

Celle de crashed_car (CB_RULES §11h) : pour chaque plan, analyse à 10 i/s (`shots/sNN.md`), plan de production (`demos/crash_instinct/plan/sNN.json`) avec `plan_check` PASS, un script Blender par plan, cartes 2D, `continuity.py` PASS, ~8 images clés comparées côte à côte, rendu par couches.
