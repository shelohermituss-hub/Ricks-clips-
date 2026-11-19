# Bible de style — la référence quand il n'y a pas de vidéo de référence

**Version 2 (19/11), construite sur 7 vidéos de CB** :
- crashed_car ;
- pink_prison ;
- dashcam ;
- mine_salting ;
- crash_instinct ;
- whale_boat ;
- plane_fall.

Mesures et observations : `references/ANALYSE_7_VIDEOS_FR.md`. Analyse fine du plan par plan : `references/crashed_car/ANALYSE_FR.md`.

- **Règle commune** = vraie dans toutes les vidéos analysées. Elle est obligatoire.
- **Option** = varie d'une vidéo à l'autre. Elle est choisie selon l'histoire et notée dans le plan.

Toute nouvelle vidéo est planifiée contre cette bible (`tools/plan_check.py`). Un écart volontaire est écrit dans le plan avec sa raison. Chaque nouvelle vidéo de référence passe par `tools/analyze_reference.py`, puis enrichit le tableau §10.

## 1. Format, durée, rythme (mesurés sur 7 vidéos)

| | Règle commune | Plage mesurée |
|---|---|---|
| Format | 9:16, 30 i/s, livré en 1080×1920 | 720p à 1080p |
| Durée | 50 à 85 s | 49,6 – 83,1 s |
| Narration | 3,3 à 3,8 mots/s, **voix continue** de 0 s à la fin, aucune pause au-delà de 0,7 s | 3,21 – 3,83 ; pause max 0,36 – 0,70 s |
| Mixage | **−14 LUFS** intégré, plage de 2 à 3 LU | −13,9 à −14,2 |
| Événements | 7 à 14 pics d'action par 10 s, **cible environ 10** | 7,2 – 14,2 (médiane 10,8) |
| Mouvement d'image | médiane seconde par seconde de **20 à 65**. Cible ≥ 25, plus haute pour une histoire d'action | 20,2 – 65,2 (médiane 30,6) |
| Images figées | ≤ 3 % | 0,1 – 3,3 % (dashcam 8,6 %) |
| Lieux | **6 à 15**, chacun construit **pour le cadre** | — |
| Coupes franches | option : 0 (tout en fondus et mouvements) à ≈ 1 toutes les 5 s, seulement sur un changement de lieu ou de temps | 0 – 12 |
| Lumière d'image | luminance 0,38 – 0,52, saturation 0,29 – 0,55, contraste ≈ 0,19 – 0,22, netteté ≥ 0,072 | — |

## 2. Histoire et narration

1. **Crochet** : la 1re phrase est l'action la plus surprenante, au passé, et l'**image la montre dès la 1re seconde**.
   - « He slammed the brakes… »
   - « A whale crashed into their boat… »
   - « He loaded the shotgun with gold… »
2. **« You see, »** fait la bascule vers l'explication (5 vidéos sur 7).
3. **Escalade en 3 à 5 temps**, chacun avec son image forte, puis un **retournement**.
4. **Dernière phrase-chute** : l'origine (« that's how the dashcam was invented »), la révélation ou l'ironie (« Even when it's just a stump. »).
5. **Boucle** quand c'est possible : la dernière image renvoie à la première (crashed, whale).
6. Un **personnage secondaire** réagit pour le comique : le dépanneur sur sa chaise longue, le copain, le voisin aux jumelles.

## 3. Sous-titres (identiques dans les 7)

- 1 à 3 mots à la fois, **blancs, gras, police ronde, contour noir épais**, centrés vers **70 % de la hauteur**.
- Changent sur chaque mot, calés sur `words.json`.

## 4. Caméra : toujours vivante

- **Jamais à l'arrêt** : mouvement nommé + dérive façon caméra à l'épaule (`street.handheld`) sur chaque plan.
- **Les personnages sont grands dans le cadre.**
  - Plans moyens et gros plans : la tête occupe 30 à 60 % de la hauteur.
  - **Au moins un très gros plan d'émotion** par vidéo : visage, œil.
  - Plans larges seulement pour situer.
- **Vocabulaire de plans** :
  - **plans d'insert** sur l'objet du récit, souvent vus de dessus (peinture, billets, batée, chronomètre, compteurs) ;
  - **plans subjectifs** : derrière le pare-brise, interface de dashcam, jumelles, vision en tunnel, flou et noir à l'évanouissement ;
  - drone et vue aérienne ;
  - travellings au ras du sol ou de la route ;
  - contre-plongée ;
  - plan débullé.
- **Transitions continues** : fondu court, balayage flou, passage à travers un objet, masque. Coupe franche seulement sur un saut de lieu ou de temps.

## 5. Monde

- **3D stylisée et réaliste de grande qualité** : formes douces et arrondies, proportions un peu exagérées.
- **Surfaces réelles** : scans PBR CC0 (Poly Haven, ambientCG), teintés dans la palette, avec usure, taches et traces.
- **Densité** : un décor raconte son lieu avec au moins 4 accessoires et des inscriptions.
- **TEXTE DANS LE DÉCOR, obligatoire** : chaque **fait chiffré ou nommé** de la narration apparaît comme un objet du décor.
  - panneaux : « DAYS SINCE LAST CRASH 7 → 0 », « 10 YEARS LATER » ;
  - journaux : « MILLIONAIRE DUE TO MORROW » ;
  - étiquettes : « P-618 » ;
  - écrans et minuteurs : « 4:59 », « JACKPOT » ;
  - caisses : « 20 DAYS ».

  Les sauts de temps sont annoncés par un panneau dans le décor.
- **Cartes et schémas** sur papier, posés dans le monde 3D, pour expliquer : carte, coupe, vue aérienne.
- **Objets brillants** : vernis complet et reflets d'un vrai ciel HDRI, visible uniquement dans les reflets.

## 6. Lumière et ambiances

- **Au moins 2 ambiances par vidéo**, en suivant l'histoire :
  - jour franc ;
  - crépuscule violet ;
  - nuit bleue avec lumières chaudes (lanternes, néons, phares) ;
  - orage et pluie ;
  - intérieur chaud ;
  - souvenir en noir et blanc.
- **Soleil franc et dur** (angle 1,5°), ombres portées nettes des structures, ciel d'appoint bas, **ombre de contact** sous tout ce qui est posé.
- Rayons de lumière (lanterne, soleil dans la poussière), liseré de lumière sur les personnages, lumières pratiques colorées.
- Couleur-thème de l'histoire : une couleur forte qui revient (rose, or, rouge, bleu océan).

## 7. Personnages

- **Stick figures 2D** de la distribution, sous forme de cartes éclairées dans le monde 3D.
  - **Un personnage = un dessin = une vue** du début à la fin.
  - Objets tenus en 3D, qui suivent la tête et les mains mesurées (`tools/card_anchors.py`).
- **Le rôle se lit au costume** : shérif, riche au haut-de-forme, mineur, marin, scientifique, prisonnier, pilote.
- **Émotions exagérées sur chaque temps fort** :
  - yeux en dollars ;
  - yeux rouges et veines de rage ;
  - visage bleu de froid ;
  - dents serrées ;
  - goutte de sueur ;
  - yeux exorbités ;
  - le visage change **sur le mot**.

## 8. Actions, réactions, conséquences

- **Tout passe par une action** : rien n'apparaît, ne disparaît, ne saute ni ne rétrécit à l'écran.
- **Chaque action a ses réactions** (catalogue `library/reactions/reactions.json`) :
  - **visibles** : gerbe, poussière, débris, secousse ;
  - **conséquences qui restent** : cabossé, mouillé, cassé, souche, tas de billets, traces ;
  - **micro-animations** ;
  - un **bruitage**.

## 9. Effets visuels

- **Comiques, exagérés et au service de l'histoire** :
  - pluie de billets ;
  - feu de voiture ;
  - tornade de débris ;
  - fissures rouges lumineuses ;
  - veine d'or qui brille ;
  - gerbes et éclaboussures ;
  - neige ;
  - étincelles ;
  - rayons ;
  - confettis.
- Stylisés et opaques plutôt que des volumes coûteux.
- Déclenchés par une action, déterministes (graine fixe).
- Particules en avant-plan devant l'objectif pour la profondeur.

## 10. Mesures par vidéo de référence

| Vidéo | Durée | Mots/s | Mvt/s médian | Pics /10 s | Coupes | LUFS | Luma | Sat |
|---|---|---|---|---|---|---|---|---|
| crashed_car | 51,5 | 3,44 | 41,8 | 11,5 | 4 | −13,9 | 0,42 | 0,42 |
| pink_prison | 65,3 | 3,65 | 20,2 | 7,2 | 0 | −14,2 | 0,52 | 0,37 |
| dashcam | 62,3 | 3,83 | 22,4 | 8,5 | 7 | −14,1 | 0,39 | 0,45 |
| mine_salting | 61,1 | 3,79 | 30,6 | 10,8 | 12 | −14,1 | 0,38 | 0,55 |
| crash_instinct | 59,5 | 3,67 | 25,6 | 8,4 | 12 | −14,0 | 0,43 | 0,29 |
| whale_boat | 49,6 | 3,36 | 35,3 | 11,5 | 0 | −13,9 | 0,45 | 0,49 |
| plane_fall | 83,1 | 3,21 | 65,2 | 14,2 | 2 | −13,9 | 0,41 | 0,44 |
