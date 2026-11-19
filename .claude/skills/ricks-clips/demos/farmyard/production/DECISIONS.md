# Décisions — démo cour de ferme

## Coupes franches voulues (contrôle `hard_cuts` de `reference_compare.py`)

| Temps vidéo | Origine | Pourquoi c'est voulu |
|---|---|---|
| 5,8 s | plan 2 → plan 3 (image 180) | changement de lieu : du cabanon à la meule de foin. `join: "cut"` dans `place.json`. |
| 8,8 s | plan 3 → plan 4 (image 270) | entrée du bulldozer. `join: "cut"`. |
| 12,8 s | plan 4 → plan 5 (image 390) | retour à la cour pour la fin. `join: "cut"`. |
| 13,3 s | éclair de l'explosion stylisée (image 405) | pas une coupe : flash lumineux de l'effet, détecté comme saut de luminance. |

Le fondu de 6 images entre les plans 1 et 2 (`dissolve:6`) décale de 0,2 s toutes les coupes suivantes.
