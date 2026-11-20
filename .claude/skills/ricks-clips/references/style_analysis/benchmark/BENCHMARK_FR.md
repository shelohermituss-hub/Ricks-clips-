# Comparatif de moteurs EEVEE / Cycles — 20/11/2026 (QUALITY_GATES G15, PRODUCTION_PIPELINE_SPEC §H)

**Statut : PARTIEL.** Cycles mesuré ; EEVEE **non mesurable sur cette machine** (arrêté à la demande de CB). Le choix du moteur reste ouvert jusqu'à un essai sur une vraie carte graphique.

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
- Mesure déjà notée dans le dépôt (`HANDOFF.md` §6) : EEVEE environ 10 % plus rapide que Cycles « pour une qualité moindre ». Les conditions de cette mesure ne sont pas connues ici.

## Pour trancher (nécessite l'accord de CB et un plafond de dépense)
Refaire ce même script sur une carte graphique RunPod (RTX 4090 : 0,89 $/h, déjà utilisée le 18/11) :
- les trois mêmes images ;
- EEVEE (32 et 64 échantillons) contre Cycles OptiX (12, 32 et 64 échantillons) ;
- temps par image + `grade_match` + planche côte à côte.

Durée estimée : 15 à 25 min de pod, soit environ 0,25 à 0,40 $. **Aucun pod n'a été créé.**

Point bloquant connu (`OPEN_ISSUES` n° 25) : la scène utilise des modèles Sketchfab que le pod ne peut pas télécharger. Il faut envoyer le `.blend` avec ses fichiers inclus (packed).
