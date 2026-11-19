# Analyse des 7 vidéos de référence de CB (19/11)

Les 6 vidéos du 19/11 et « He Crashed His Own Car For Science » (analyse détaillée : `crashed_car/ANALYSE_FR.md`) ont été traitées **de la même façon** par `tools/analyze_reference.py` :
- fiche technique ;
- mesures d'image par seconde ;
- loudness EBU R128 ;
- transcription mot à mot (faster-whisper) ;
- coupes franches ;
- planches à 1 et 2 images par seconde ;
- **regard sur chaque seconde des planches**.

Les vidéos sources restent en local (`references/<nom>/source.mp4`, ignorées par Git). Tout le reste est versionné.

| Dossier | Titre | Durée | Mots | Mots/s | Pause max | LUFS | Coupes | Mvt/s médian | Pics /10 s | Luma | Sat |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `crashed_car` | He Crashed His Own Car For Science | 51,5 | 177 | 3,44 | 0,40 | −13,9 | 4* | 41,8 | 11,5 | 0,42 | 0,42 |
| `pink_prison` | The Pink Prison Cell Experiment | 65,3 | 237 | 3,65 | 0,46 | −14,2 | 0 | 20,2 | 7,2 | 0,52 | 0,37 |
| `dashcam` | Why Drivers Started Filming The Road | 62,3 | 237 | 3,83 | 0,36 | −14,1 | 7 | 22,4 | 8,5 | 0,39 | 0,45 |
| `mine_salting` | How Mine Salting Worked | 61,1 | 231 | 3,79 | 0,70 | −14,1 | 12 | 30,6 | 10,8 | 0,38 | 0,55 |
| `crash_instinct` | The Instinct That Makes You Crash | 59,5 | 217 | 3,67 | 0,36 | −14,0 | 12 | 25,6 | 8,4 | 0,43 | 0,29 |
| `whale_boat` | A Whale Crashed Into Their Boat | 49,6 | 163 | 3,36 | 0,36 | −13,9 | 0 | 35,3 | 11,5 | 0,45 | 0,49 |
| `plane_fall` | He Survived Falling Out Of A Plane | 83,1 | 264 | 3,21 | 0,64 | −13,9 | 2 | 65,2 | 14,2 | 0,41 | 0,44 |
| **Plage** | | **50–83 s** | 163–264 | **3,2–3,8** | ≤ 0,7 | **−14 ±0,2** | 0–12 | **20–65** (méd. 30,6) | **7–14** (méd. 10,8) | 0,38–0,52 | 0,29–0,55 |

\* Coupes mesurées par le même détecteur (`reference_compare`). L'analyse manuelle de crashed_car en comptait 10, car elle incluait les coupes douces. **Mvt/s médian** = médiane du mouvement d'image seconde par seconde (×1000).

## 1. Ce que les 7 ont en commun (devient règle)

**Histoire et voix**
1. **La première phrase est l'action la plus surprenante, racontée au passé et tout de suite** :
   - « He slammed the brakes… » ;
   - « They painted the jail cell pink… » ;
   - « He loaded the shotgun with gold… » ;
   - « A whale crashed into their boat… » ;
   - « He was drinking a can of soda when… ».

   L'image montre cette action dès la première image.
2. **« You see, »** apparaît dans 5 vidéos sur 7. C'est la bascule vers l'explication, après le crochet.
3. Structure : crochet → contexte (« You see ») → escalade en 3 à 5 temps → retournement → **dernière phrase-chute** :
   - l'origine (« that's how the dashcam was invented ») ;
   - la révélation (« a vein of real gold ») ;
   - l'ironie (« Even when it's just a stump. »).
4. Voix **continue** de la première à la dernière seconde, 3,2 à 3,8 mots/s, aucune pause au-delà de 0,7 s. Mixage à **−14 LUFS**, plage de 2 à 3 LU.

**Image**
5. **Sous-titres identiques dans les 7** : 1 à 3 mots, blancs, gras, police ronde, contour noir épais, centrés vers 70 % de la hauteur. Ils changent sur chaque mot.
6. Mêmes **stick figures 2D** dans un monde 3D stylisé et réaliste de grande qualité (PBR, lumière dure, profondeur de champ).
7. **Les personnages sont souvent GRANDS dans le cadre** : plans moyens et gros plans où la tête occupe 30 à 60 % de l'image. Il y a aussi des **très gros plans** sur un visage ou un œil quand l'émotion culmine (pink 19 s, whale 39 s, plane 13-14 s, crash 53 s). Nos plans 1 et 2 étaient trop larges.
8. **Chaque rôle se lit au costume** :
   - casquette de shérif et chapeau de cow-boy ;
   - haut-de-forme et moustache du riche ;
   - casque de mineur ;
   - bonnets de marin ;
   - blouse et cravate du scientifique ;
   - tenue de prisonnier.
9. **Émotions exagérées dessinées sur le visage** :
   - yeux en dollars ;
   - yeux rouges de rage avec veines ;
   - visage bleu de froid ;
   - dents serrées ;
   - goutte de sueur ;
   - yeux exorbités.
10. **Chaque fait chiffré ou nommé de la narration apparaît comme TEXTE DANS LE DÉCOR** : panneaux, journaux, étiquettes, écrans, horloges.
    - « DAYS SINCE LAST CRASH 7 → 0 », « DON'T HIT THIS TREE » ;
    - « P-618 BAKER-MILLER PINK », « MILLIONAIRE DUE TO MORROW », « SURE THING MINE » ;
    - le minuteur « 4:59 », « 300 MILES », « PACIFIC OCEAN » ;
    - « 5 YEARS LATER », « 10 YEARS LATER GRAND CANYON », « MUST BE 21 », « JACKPOT $1,000,000 ».
11. **Plans d'insert** : gros plans de détail, souvent en vue de dessus, sur l'objet du récit (peinture versée, billet de 100 et or, batée, tableau de bord, chronomètre, œil de poisson).
12. **Cartes et schémas** sur papier dans le monde 3D : carte du Pacifique avec Point Nemo, schéma de l'œil de poisson, vue aérienne de la campagne.
13. **Plans subjectifs** :
    - conducteur derrière le pare-brise et le tableau de bord (dashcam, crash_instinct, plane) ;
    - jumelles (crashed) ;
    - interface de dashcam avec vitesse et heure (dashcam) ;
    - vision en tunnel (crash_instinct 43 s) ;
    - flou et noir au moment de l'évanouissement (plane 16-17 s).
14. **Au moins deux ambiances de lumière par vidéo** :
    - jour franc ;
    - crépuscule violet ;
    - nuit bleue avec lumières chaudes ;
    - orage et pluie ;
    - intérieur chaud ;
    - souvenir en noir et blanc (plane 76 s).
15. **6 à 15 lieux par vidéo.** Les sauts de temps sont annoncés par un panneau dans le décor.
16. **Caméra toujours vivante** :
    - travellings au ras de la route ;
    - drone ;
    - contre-plongées ;
    - plans débullés ;
    - poussées lentes sur les visages.

    Images figées : moins de 3,5 % du temps, sauf dashcam (8,6 %, plans de tableau de bord tenus).
17. **Transitions** surtout continues :
    - fondus enchaînés courts (pink, whale) ;
    - balayages ;
    - passage à travers un objet ;
    - masque (jumelles, tunnel) ;
    - noir de l'évanouissement.

    Coupes franches entre 0 et 12, sur un changement de lieu ou de temps.
18. **Effets comiques et exagérés, au service de l'histoire** :
    - pluie de billets ;
    - incendie de voiture ;
    - tornade de débris ;
    - fissures rouges au sol (rage) ;
    - veine d'or qui brille ;
    - gerbes d'eau, neige ;
    - rayons de lumière ;
    - étincelles.
19. **Conséquences visibles qui restent** :
    - voiture de shérif cabossée ;
    - souche après l'arbre coupé (la voiture percute ensuite la souche) ;
    - tas de billets ;
    - voilier qui coule ;
    - fragments dispersés.
20. **Personnages secondaires qui réagissent** et petits gags de fond :
    - le dépanneur assis sur sa chaise longue ;
    - le copain qui regarde l'or disparaître ;
    - le voisin aux jumelles.
21. **Boucle** : la dernière image renvoie à la première. C'est le cas de crashed (rue) et de whale (voilier).

## 2. Ce qui varie (devient option, choisie par l'histoire)

| Variante | Exemples |
|---|---|
| Rythme calme (mouvement par seconde ≈ 20) ou très rapide (≈ 65) | pink et dashcam calmes ; plane et crashed rapides |
| 0 coupe franche (tout en fondus et mouvements) ou ≈ 1 coupe toutes les 5 s | pink et whale contre mine et crash_instinct |
| Un lieu principal ou un voyage (15 lieux, sauts de temps) | mine contre plane |
| Couleur-thème de l'histoire | rose (pink), or et brun chaud (mine), bleu océan et orange (whale), rouge et vert (crash) |
| Narration à la 3e personne (« he ») ou explication générale (« If you… ») | crash_instinct commence par « If you plant a tree » |

## 3. Notes par vidéo (ce qu'on retient pour la construction)

- **pink_prison** : intérieurs (cellule rose, réfectoire, poste de garde, vue aérienne de la campagne).
  - Gros plans de la peinture versée vue de dessus.
  - Rage en effet : fissures rouges lumineuses dans le sol.
  - Prisonnier au tricot rayé rose et blanc qui s'allonge à travers 3 plans : une conséquence qui dure.
  - Fondus à travers les vitres.
- **dashcam** :
  - plans au ras de l'autoroute, voitures brillantes qui se suivent ;
  - pluie de billets qui s'entasse au sol et reste ;
  - crépuscule violet puis nuit ;
  - bureau d'assurance avec compteur « 2 → 0 » ;
  - plans subjectifs dans la voiture, interface de dashcam en surimpression ;
  - pluie et ciel d'orage.
- **mine_salting** :
  - lumière chaude de lanternes et rayons ;
  - insert de la batée avec paillettes ;
  - gros plan du fusil ;
  - journal « MILLIONAIRE » ;
  - riche au haut-de-forme ;
  - dynamite et étincelles, puis un nuage de poussière qui révèle une veine d'or lumineuse.
- **crash_instinct** :
  - route droite infinie dans les champs, arbre unique ;
  - panneau « DAYS SINCE LAST CRASH » qui passe de 7 à 0 ;
  - flèche lumineuse « DON'T HIT THIS TREE » ;
  - shérif furieux aux yeux rouges, débris en tornade ;
  - arbre abattu puis souche percutée ;
  - nuit d'orage en plan subjectif, vision en tunnel.
- **whale_boat** :
  - océan stylisé brillant, voilier au coucher du soleil ;
  - minuteur rouge « 4:59 » ;
  - inventaire vu de dessus (gilets, caisses « 20 DAYS », boussole) ;
  - carte papier avec Point Nemo ;
  - nuit à la lanterne ;
  - très gros plan de l'œil, schéma « THE FISH EYE » ;
  - cargo, « 300 MILES » sur un panneau flottant ;
  - boucle sur le voilier.
- **plane_fall** :
  - porte d'avion arrachée, chute libre parmi d'autres passagers, botte de foin ;
  - évanouissement en flou puis noir, réveil à l'hôpital ;
  - billets, train dans un lac gelé, visage bleu ;
  - voiture en feu devant une caserne ;
  - « 10 YEARS LATER » au Grand Canyon, chute retenue par un arbre ;
  - souvenir en noir et blanc ;
  - jackpot.

## 4. Conséquences pour notre méthode

1. `STYLE_BIBLE_FR.md` est mise à jour avec ces mesures (plages au lieu d'une seule vidéo) et ces règles.
2. `library/reactions/reactions.json` reçoit les nouvelles actions vues : pluie d'argent, arbre abattu, bateau qui coule, chute libre, évanouissement, véhicule en feu, chute dans l'eau, coup de fusil, explosion qui révèle, émotion extrême, liquide versé.
3. `plan_check.py` vérifie en plus :
   - qu'un **fait chiffré ou nommé** du script a son **texte dans le décor** ;
   - que la vidéo a **au moins 2 ambiances de lumière** ;
   - qu'elle a au moins un **gros plan d'émotion** ;
   - qu'elle a au moins un **plan d'insert** ;
   - que la **première action est montrée dès la première seconde**.
