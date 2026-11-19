# DECISIONS — décisions techniques et leurs justifications

`S/` = `.claude/skills/ricks-clips/`. « CB » = le propriétaire du projet. Dates en 2026.

Les décisions de production de la démo ferme sont aussi dans `S/demos/farmyard/production/DECISIONS.md`.

## Décisions de CB

| Date | Décision | Justification / source |
|---|---|---|
| 18/11 | Restructuration vers un pipeline Blender unique ; ne jamais maintenir deux pipelines concurrents | Mission maîtresse ; three.js est gardé seulement pour dessiner les personnages |
| 18/11 | Démo = cour de ferme ; plafond GPU de **3 $** ; Ghost Army archivé sans suppression | Mission maîtresse |
| 19/11 | Pas de second rendu GPU de la ferme : livrer tel quel et sauvegarder la solution | CB : « ne le relance pas sur le GPU, utilise-le comme ça » |
| 19/11 | Reproduire entièrement la vidéo de CB, tout recréé par nous ; liberté totale sur l'outil | CB : c'est sa vidéo, « même style, rendu… créé par toi » |
| 19/11 | Garder le plan 1 tel quel | CB |
| 19/11 | Corriger seulement ce qui change : images clés d'abord, `--patch`, un seul rendu complet groupé, annoncer le temps réel | CB, après des temps de correction qui doublaient |
| 19/11 | Rendre par couches (ciel, décor, objets, effets) | Proposition de CB, adoptée pour tous les plans |
| 19/11 | Analyser chaque plan en détail avant de le construire | CB |
| 19/11 | Tout passe par une action ; caméra jamais à l'arrêt ; vraies textures et vraies ombres ; contrôle automatique | CB, après des apparitions et téléportations répétées |
| 19/11 | Plan complet avant de construire, une réaction et une conséquence pour chaque action, chaque problème devient une solution permanente | CB, pour les vidéos sans référence |

## Décisions techniques (prises par Claude, mesurées)

| Décision | Justification mesurée |
|---|---|
| **Blender 5.2.2 + Cycles**, pas EEVEE | Benchmark sur RTX 4090 : EEVEE seulement environ 10 % plus rapide (4,0 contre 4,5 s par image), contre une différence moyenne de 6,7/255 et des ombres de contact plus faibles ; le coût est dans la préparation de la scène |
| Volumes biaisés par défaut | Les volumes non biaisés de Blender 5 coûtent 22,7 s de préparation par image, contre 1,7 s biaisés, pour une image identique |
| Benchmark : médiane après échauffement | 1re image GPU à 121 s (compilation OptiX), puis 4,5 s |
| Calibration persistée dans `places/<lieu>/calibration.json` | Le pod a rendu sans la calibration qui n'existait que dans le .blend local |
| Cache d'images indexé sur les entrées de construction | Un .blend réenregistré n'est pas identique à l'octet près |
| Décors **construits pour le cadre** (méthode par plan) | La référence montre 11 lieux en 51 s. Un monde entier coûtait 4,5 s par image en préparation. Un plan se construit en environ 10 s |
| Personnages en **cartes 2D** du code ; **un personnage = un dessin = une seule vue** | Le style de CB, ce sont ces stick figures. Le mélange de deux mouvements ne fonctionne que dans une même vue (`puppets.mjs` moveOf) |
| Objets tenus en 3D, posés sur la tête et les mains **mesurées sur le dessin** (`card_anchors.py`) | Le casque était mal placé et sautait. Mesure par image, pas plus de 12 cm par image |
| Textures CC0 Poly Haven (`street.pbr`) ; HDRI vu **uniquement par les reflets** (`hdri_reflections`) | CB : sol trop plat, peinture sans profondeur. Le ciel visible garde la palette de la référence |
| Soleil dur (angle 1,5°, énergie 6,2), ciel d'appoint 0,42 | Ombres nettes et contrastées comme la référence |
| Dérive « caméra à l'épaule » sur chaque image (`street.handheld`) | CB : « la caméra ne s'arrête jamais ». Contrôle HOLD |
| F1 recolorée par saturation et valeur | Supprime la livrée d'une vraie marque, garde les pièces noires |
| Vue Standard + « Medium High Contrast » | AgX Punchy testé : trop gris face à la référence |
| `render_layers.sh` refuse de rendre si `continuity.py` échoue | Un rendu sur un plan faux est du temps perdu |
| Seuil des sauts de pose à 0,9 m par image | Le geste le plus rapide de la bibliothèque de mouvements fait 0,83 m par image. Deux transitions du plan 2 (0,85 et 0,87) passent juste en dessous : **signalé à CB** |
| `pod.py delete` refuse sans récupération vérifiée | Incident passé : un lock perdu par la suppression d'un pod avant récupération |
