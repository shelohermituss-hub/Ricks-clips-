# MISSION 2 — Prototype complet : rapport

Date : 2026-11-18.
Preuves : `episodes/ghost-army/production/PROTO_M2/` (vidéos, planches, mesures, gates, temps de rendu).
Statuts : PASS (preuve), PARTIAL, FAIL, NOT_RUN.
Tout a été calculé **en local, sur processeur** (4 cœurs, sans GPU). Aucun pod n'a été lancé.

## 1. Objectif
Prouver toute la chaîne de la nouvelle architecture sur un lieu complexe, en séquence animée et pas seulement en image fixe, plus un test de destruction mécanique. Le lieu choisi est le champ de Ghost Army (images 0 à 150 du film).

Chaîne couverte : environnement détaillé, assets crédibles, véhicule, personnages intégrés, interaction, animation, micro-animation, caméra du film, effets, LookDev, rendu.

## 2. Livrables (vidéos 270×480, Cycles CPU)
| Fichier | Contenu |
|---|---|
| `proto_field.mp4` | Le champ, 151 images (5 s), caméra du film, 6 personnages, char soulevé puis reposé, vent, poussière |
| `proto_field_vs_v3.mp4` | Côte à côte : V3 three.js à gauche, prototype Blender à droite (mêmes images) |
| `proto_crash.mp4` | Destruction : bulldozer à 3 m/s contre la charrette, 121 images (4 s) |
| `sheet_field.jpg`, `sheet_crash.jpg` | Planches de contrôle |

## 3. Résultats par critère

| Critère | État | Preuve |
|---|---|---|
| Environnement détaillé, aucune primitive de remplacement | **PASS** | Gates de la scène 4/4 : 68 objets, 17 970 instances (environ 102 millions de triangles affichés), 0 primitive (les 12 objets plats sont les cartes de personnages et leurs ombres de contact, comptés à part), 61/61 matières texturées (`field_gates.json`) |
| Assets crédibles et réutilisables | **PASS** | 27 assets en bibliothèque, chacun avec fiche, licence et mesures. Nouveaux : 9 modèles Poly Haven CC0 (arbre feuillu, arbustes, herbes, orties, pissenlits, rocher, souche, tronc), 7 jeux PBR, ferme normande sur mesure (55 172 triangles, environ 2 400 tuiles modélisées), charrette sur mesure (33 pièces) |
| Véhicule ou élément mécanique | **PASS** | Bulldozer, half-track et char gonflable texturés (matières PBR teintées vers la palette) |
| Personnages intégrés | **PASS** (vérifié sur images) | 6 cartes. Ombre portée réelle de la silhouette, ombre de contact au sol, lumière du lieu à 45 %. Dessins issus du cache (151 par personnage) |
| Interaction avec un objet | **PASS** | Le char est soulevé puis reposé par les porteurs, avec léger affaissement au contact. Courbe identique à la V3, donc synchronisée avec la voix |
| Micro-animations | **PASS** | Vent dans toute la végétation, calculé à partir du temps de la scène. Respiration et clignements fournis par les dessins de cartes existants |
| Caméra cinématographique | **PASS** | Caméra précalculée du film (stations 0 à 150), reprise telle quelle |
| Effets visuels | **PARTIAL** | Poussière en volume à la pose du char et à l'impact. Visible, mais discrète à cette résolution ; elle multiplie le temps de rendu par 3 sur ces images |
| LookDev complet | **PASS** | La palette d'abord : chaque matière garde sa couleur validée. Calibration mesurée sur l'image V3 numéro 30 : exposition +0,23 EV, balance des blancs 8 038 K. Luminance moyenne 0,1255 contre 0,1264 pour la référence ; rapports R/V/B 1,03 / 1,01 / 0,86 |
| Destruction mécanique contrôlée | **PARTIAL** | Fracture préparée (planches en 3, côtés et extrémités en 2), 55 pièces, 266 liaisons cassables, collision réelle, charrette poussée d'environ 5,2 m, épave finale. Défaut : des planches sautent au moment où la physique prend le relais (image 55), juste avant le contact |
| Séquence animée, pas seulement une image fixe | **PASS** | 151 et 121 images rendues |
| Reproductibilité (rendu par tranches) | **PASS** | Image 72 de la destruction et image 110 du champ : identiques au pixel, seules ou dans la séquence (débruiteur actif). Assemblage reproductible : 3 assemblages donnent 55 pièces et 266 liaisons |
| Rendu GPU | **NOT_RUN** | Demande un pod payant. La tâche `look/jobs/101_proto_gpu.sh` est prête |
| Benchmark EEVEE contre Cycles | **NOT_RUN** | Sur GPU, dans la même tâche |

## 4. Mesure contre le standard forteresse (même plage d'images 0 à 150, même outil)

| Métrique | V3 three.js | **Prototype Blender** | Seuil |
|---|---|---|---|
| Netteté des contours (« edge detail ») | 0,051 FAIL | **0,078 PASS** | ≥ 0,075 |
| Luminosité de jour | 0,296 FAIL | 0,352 FAIL (proche) | 0,36-0,50 |
| Noirs bouchés | 3,0 % FAIL | 1,2 % FAIL (proche) | ≤ 1 % |
| Blancs brûlés | 0,1 % PASS | 0 % PASS | ≤ 1,5 % |
| Saturation | 0,778 FAIL | 0,575 FAIL | 0,32-0,52 |
| Secondes au-dessus du plafond de saturation | 6 FAIL | **0 PASS** | 0 |
| Images figées | 0,7 % PASS | 1,3 % PASS | ≤ 2 % |
| Mouvement médian | 8,8 FAIL | **31,9 PASS** (*) | ≥ 18 |
| Pics par 10 s | 3,97 FAIL | 5,96 FAIL (proche) | ≥ 6 |
| Coupes sèches | 0 PASS | 0 PASS | 0 |
| **Total** | **3/10** | **6/10** | |

(*) Le grain du rendu à 24 échantillons gonfle la mesure du mouvement (limite connue de l'outil). À revérifier sur un rendu GPU à 64 échantillons.

Le prototype n'a pas encore d'étalonnage final : `grade.py` n'a pas été appliqué. La luminosité, les noirs et la saturation sont réglés par cet étalonnage, comme pour la V3.

## 5. Performances (mesurées en local, 4 cœurs CPU, 270×480)
| Étape | Temps mesuré |
|---|---|
| Ingestion de la bibliothèque, premier passage (téléchargements Poly Haven compris) | 50 s ; ensuite, correspondances dans le cache |
| Dessins des personnages (6 × 151) | 82 à 217 s par personnage ; 0,4 s au second passage (cache) |
| Assemblage du champ (`place.json` vers `.blend`) | 55 s |
| Assemblage et précalcul de la physique de la destruction | 14 s |
| Rendu du champ, 151 images, Cycles CPU, 24 échantillons | 1 695 s (11,2 s par image ; environ 23 s sur les images de poussière) |
| Rendu de la destruction, 121 images, Cycles CPU, 16 échantillons | 1 351 s (11,2 s par image) |

Projection GPU : NOT_RUN. Elle sera mesurée par la tâche 101, et aucune durée n'est promise.

## 6. Problèmes trouvés pendant la mission (et corrigés)
1. Asset Hub ne téléchargeait pas les fichiers liés d'un modèle glTF (`.bin`, textures). Ajout de `rc/fetch.py`, qui télécharge vers le cache avec somme de contrôle.
2. Les fiches asset.json des dossiers de fournisseurs étaient ignorées par Git. `.gitignore` corrigé : les fiches sont versionnées, pas les fichiers.
3. Les ensembles de variantes Poly Haven (plusieurs plantes alignées) sont maintenant éparpillés variante par variante, avec une graine fixe.
4. Balance des blancs : le sens de la correction était inversé. La mesure l'a révélé (le rapport R/B est tombé de 0,70 à 0,18). Corrigé et documenté.
5. Le bulldozer roulait à l'envers (son modèle a l'avant vers -X). Ajout d'une option de décalage de direction.
6. Un volume de collision accroché à un parent animé ne poussait rien. Il reçoit maintenant ses propres images clés.
7. La conversion de la simulation en images clés par Blender ne fonctionne pas sans écran. Remplacée par ma propre conversion.
8. Une roue était projetée à 20 m, à cause de l'interpénétration entre la roue et l'essieu. Les roues ont désormais leur propre groupe de collision : 5,2 m mesurés.
9. Le contrôle qualité comptait les cartes de personnages comme des primitives. Elles sont exclues de ce gate et comptées à part.
10. Le pod Blender aurait relancé les anciennes tâches LookDev 000 à 007. Il ne lance plus que les tâches 100 et suivantes.

## 7. Problèmes ouverts
- **P2, saut des planches au déclenchement de la physique :** chevauchement initial des enveloppes de collision. Piste : marge de collision, déclenchement à l'image du contact, liaisons créées après une légère séparation.
- **P2, plan du chemin (images 135 à 150) :** des arbustes masquent encore une partie des cyclistes, et le bord de la bande du chemin se voit. Les haies sont bien exclues du chemin ; la cause exacte reste à identifier.
- **P2, étalonnage final non appliqué** au prototype (luminosité, noirs, saturation).
- **P3, ciel en simple dégradé :** les nuages de la V3 manquent (`lights.cloud` existe mais n'est pas branché).
- **NOT_RUN :** rendu GPU, benchmark EEVEE contre Cycles, minuterie qui arrête le pod, protection des résultats sur un vrai pod.

## 8. Tests
- `test_rc.py` : 17/17, dont 2 nouveaux tests de physique.
- `test_pod_guard.py` : 13/13.
- `test_production_intelligence.py` : 11/11.

## 9. Prochaine étape proposée
**Tâche 101 sur un pod RTX 4090 (demande ton autorisation) :**
- reconstruction du prototype sur le pod ;
- benchmark EEVEE contre Cycles OPTIX sur 3 images en 540×960 ;
- rendu des 2 séquences en 540×960 sur le moteur retenu ;
- preuve d'utilisation du GPU (`gpu_usage.csv`) ;
- récupération vérifiée avant toute suppression du pod.

**Estimation (ESTIMÉE, non mesurée) :** de 1 à 1,5 h de pod.
- Cloud communautaire à 0,34 $/h : environ 0,5 $.
- Cloud sécurisé à 0,89 $/h : environ 1,3 $.
- Plafond proposé : 3 $, avec une minuterie à 2 h qui arrête le pod sans le supprimer.

Ensuite : corriger les deux défauts P2, puis migrer les autres lieux (mission 3).
