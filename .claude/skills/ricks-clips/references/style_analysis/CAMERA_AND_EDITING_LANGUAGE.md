# Caméra et montage

Voir la bible centrale `RICKCLIPS_REFERENCE_STYLE_BIBLE.md`. Mesures : `data/cross_video_measures.json`. Plans : `shot_catalog.csv` (87 plans).

## 1. Mesures (MESURÉ)
| Vidéo | Plans | Durée médiane des plans | Mouvement médian (/255) | Images quasi fixes | Coupes franches vérifiées |
|---|---|---|---|---|---|
| V01 | 13 | 4,70 s | 4,4 | 0,7 % | environ 2 (fondus, filé, passages par objet) |
| V02 | 19 | 2,63 s | 4,9 | 3,1 % (plan dashcam fixe voulu) | environ 8 |
| V03 | 18 | 4,25 s | 15,5 | 0,5 % | environ 8 |
| V04 | 20 | 2,83 s | 4,2 | 0,5 % | 0 avant 22,9 s, puis environ 12 |
| V05 | 17 | 2,63 s | 9,2 | 0,0 % | 4 (pendant l'assaut) |

Méthode : mouvement = différence absolue moyenne de gris entre deux images consécutives, sur des images réduites à 90×160. Coupes : candidats automatiques vérifiés à l'œil. Les fondus et les coupes de même luminance sont manqués par le seul seuil (V05).

## 2. Règles communes
- **R1, la caméra ne s'arrête jamais** (MESURÉ, cinq vidéos). Le seul plan fixe observé est une image de caméra embarquée (V02 S18), justifiée par le récit.
- **R2, peu de coupes franches pour changer de lieu.** Les transitions préférées (OBSERVÉ) :

  | Transition | Exemples |
  |---|---|
  | Traverser un objet | porte V01 697-716 ; plafond V01 1150-1170 ; écran CRT V01 1384-1398 ; pare-brise V02 37 ; porte d'avion V03 96-167 |
  | Fouetté de 3 images (cache un saut de temps ou de lieu) | V01 420 ; V04 282-285 ; V05 66 |
  | Fondu enchaîné d'environ 0,3 s | V01 109, 859, 1291, 1718 ; V02 144, 309 ; V04 363, 465, 510 ; V05 143, 869, 1808 |
  | Objet géant plein cadre | billet V03 1040 |
  | Essuie-glace comme volet | V02 1308 |
  | Vision tunnel → noir → réouverture floue | V03 435-560 |

- **R3, la coupe franche sert l'accélération.** On la trouve dans les séquences d'action ou d'assaut (V05 1173-1452, V02 et V04 en fin de vidéo).
- **R4, choc caméra** : petit tremblement de 3-10 images à chaque impact (V01 1044, V02 84-90, V04 104-107).

## 3. Grammaire des plans (OBSERVÉ, réutilisable)
| Recette | Description | Exemples | Limites |
|---|---|---|---|
| **Longue prise grue** | plan moyen → plongée au ras du sol → grue jusqu'à la vue aérienne → descente | V04 0-281 ; V01 930-1290 | demande un décor continu à toutes les échelles |
| **Travelling de véhicule** | caméra qui roule à la vitesse du sujet, décor qui défile | V02 S02, S08, S09, S15 | — |
| **Vue subjective du conducteur** | tableau de bord au premier plan, route devant | V02 S04, S16 ; V03 S15 ; V04 S15-S19 | — |
| **Contre-plongée de coin de pièce** | plafond et néon en diagonale, personnage puissant | V01 750-858, 1500-1556 | intérieurs |
| **Macro qui glisse sur l'objet** | caméra au ras de la matière, entre les pièces | V05 46, 555, 1530-1740 ; V01 585-600 | objet héros détaillé requis |
| **Caméra en chute libre** | la caméra tombe avec les personnages | V03 168-359 | — |
| **Caméra qui suit l'énergie** | étincelle → corde → tubes → ciel, en un seul mouvement | V05 1531-1815 | — |
| **Plan latéral fixe pour un gag physique** | la caméra ne bouge presque pas pour qu'on lise la position impossible | V04 1224-1260 ; V03 2006-2021 | seule exception à R1, très courte |
| **Poussée de 5 images sur l'objet chiffré** | arrivée rapide sur le chronomètre, l'écran, le panneau | V01 580-585 ; V04 282-285 | — |
| **Plongée de surveillance** | vue haute en coin, texture d'écran | V01 1398-1420 | — |

- **Focales apparentes** : courtes (environ 18-28 mm équivalent) sur les décors et les véhicules, d'après la convergence des lignes (INFÉRÉ, plage prudente) ; plus longues en gros plan d'objet.
- **Profondeur de champ** : presque toujours infinie. Flou seulement en très gros plan (V01 585), au réveil (V03 510-560) et en premier plan d'herbe (V02 330).

## 4. Rythme et voix (MESURÉ)
- Chaque coupe ou changement de cadre tombe sur un mot-clé (`shot_catalog.csv`, colonne `narration_words`).
- La voix ne s'arrête jamais. Les « pauses » comiques sont des **images figées sur une réaction** pendant que la voix continue (V01 1057 « Wait, what? » ; V04 1290 shérif ahuri).
- **Accélération** : les plans raccourcissent pendant l'escalade (V05 assaut : 1,2-3 s ; V02 S15-S19).

## 5. Continuité
- Un même lieu revu garde toutes les traces précédentes (V04).
- Les objets plantés reviennent : chronomètre V01, dashcam V02, billet V03, flèche V04, charrette V05.
- Un saut de temps est toujours **dit dans l'image** : fouetté + changement d'objets (V04), panneau « X YEARS LATER » (V03), fondu jour → nuit (V01).

## 6. Recommandations pour RicksClips
1. Écrire les mouvements de caméra dans le plan de production avec début, fin, durée et easing ; refuser un plan qui contient plus de 2 images fixes (déjà contrôlé par `continuity.py` HOLD).
2. Pour changer de lieu : d'abord chercher un **objet à traverser** ; sinon un fouetté de 3 images ; sinon un fondu de 0,3 s ; la coupe franche est réservée à l'accélération.
3. À chaque impact, ajouter un tremblement de caméra de 3-10 images, décroissant.
4. Un plan quasi fixe n'est permis que pour lire un gag physique (moins de 2 s) ou une image d'écran.
