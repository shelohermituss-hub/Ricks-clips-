# Comparatif de moteurs EEVEE / Cycles — 20/11/2026 (QUALITY_GATES G15, PRODUCTION_PIPELINE_SPEC §H)

**Statut : CLOS par décision de CB (20/11) : Cycles est le moteur principal.** Cycles mesuré sur processeur ; EEVEE non mesurable sur cette machine (arrêté à la demande de CB) ; pas d'essai GPU supplémentaire.

## Protocole
- Même scène construite : `demos/crash_instinct/build/s04_sign.blend` (plans 1 à 4 de crash_instinct, prise continue).
- Mêmes images : 180 (vue aérienne), 309 (plan large voiture bleue), 357 (panneau).
- Même taille : 270×480, flou de mouvement coupé. Script : `benchmark/bench.py`.
- Machine : conteneur cloud, 4 cœurs, 15 Go de mémoire, **aucune carte graphique**.
  - Cycles tourne sur le processeur.
  - EEVEE tourne en OpenGL logiciel (Mesa llvmpipe), qui imite une carte graphique sur le processeur.
- Réglages : Cycles 12 échantillons (réglage d'aperçu du projet) ; EEVEE 32 échantillons, ombres et lancer de rayons activés.

## Résultats
| Moteur | Image 180 | Image 309 | Image 357 | Remarque |
|---|---|---|---|---|
| Cycles (processeur, 12 éch.) | 7,4 s | 7,6 s | 10,1 s | + environ 1 s de chargement de la scène |
| EEVEE (OpenGL logiciel) | — | — | — | **plus de 7 min 40 s sans finir la première image** (compilation des shaders et rendu en logiciel) ; arrêté |

Contrôle d'étalonnage des images Cycles (`tools/grade_match.py`, contre la vidéo de référence) :
- 180 : PASS ;
- 309 : contraste 0,19 pour 0,24 ;
- 357 : saturation 0,32 pour 0,23.

Ce sont les mêmes écarts que dans les aperçus du plan 4 (`OPEN_ISSUES` n° 29) : ils viennent de la scène, pas du moteur.
Planche côte à côte : `benchmark/cycles_s04_ref_vs_ours.jpg`.

## Ce qu'on peut conclure
- **Sur une machine sans carte graphique, Cycles est le seul moteur utilisable** : environ 8 s par image en 270×480 à 12 échantillons, soit environ 14 min pour un plan de 100 images en aperçu. EEVEE sans carte graphique est inutilisable : la première image n'est pas finie au bout de 7 min 40 s, plus de 50 fois plus lent.
- **Cela ne dit rien d'EEVEE sur une vraie carte graphique**, où il est fait pour être rapide. La référence de CB (un ancien flux EEVEE de 20 à 30 min) n'est ni confirmée ni infirmée ici.
- Mesure GPU déjà faite le 18/11 (`DECISIONS.md`) : sur RTX 4090, EEVEE 4,0 s contre Cycles 4,5 s par image (environ 10 % plus rapide), avec une différence moyenne de 6,7/255 et des ombres de contact plus faibles. (Correction : la première version de ce rapport disait à tort que ses conditions étaient inconnues.)

## Décision
CB, 20/11 : **Cycles comme moteur principal.** Le test GPU EEVEE / Cycles proposé n'est pas lancé.
