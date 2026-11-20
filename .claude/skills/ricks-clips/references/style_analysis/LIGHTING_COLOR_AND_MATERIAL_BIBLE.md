# Lumière, couleur, matières, étalonnage

Bible centrale : `RICKCLIPS_REFERENCE_STYLE_BIBLE.md`. Palettes avec provenance : `palette_catalog.json`, région, image, méthode. Mesures par seconde : `data/V0x/per_second.json`.

## 1. Mesures globales (MESURÉ, images réduites à 90×160, moyennes par seconde)
| Vidéo | Luminosité moy. (min-max) | Saturation moy. (min-max) | Contraste moy. | Ambiances distinctes |
|---|---|---|---|---|
| V01 | 0,52 (0,32-0,72) | 0,37 (0,22-0,62) | 0,18 | 5 |
| V02 | 0,40 (0,20-0,62) | 0,44 (0,25-0,68) | 0,22 | 7 |
| V03 | 0,41 (0,06-0,72) | 0,43 (0,02-0,76) | 0,20 | 10 |
| V04 | 0,43 (0,17-0,67) | 0,28 (0,19-0,39) | 0,19 | 8 |
| V05 | 0,43 (0,21-0,63) | 0,39 (0,24-0,52) | 0,18 | 10 |

**Constat** : aucune vidéo n'a une saturation ou une luminosité constante. La plage par seconde va de 0,15 (V04) à 0,74 (V03). **Une seule moyenne ne décrit pas le style.**

## 2. Ambiances réellement présentes (OBSERVÉ)
| Ambiance | Vidéos | Signature mesurée ou observée |
|---|---|---|
| Jour ensoleillé, ciel bleu | toutes | ciel saturé (#2687e7 V02, #4f82d9 V05), ombres nettes, soleil dur |
| Contre-jour (soleil derrière le sujet) | V04, V03 (2175) | ombres longues vers la caméra, halo |
| Rayons volumétriques dans l'air | V01 (salle commune), V03 (meule), V05 (coin de cour), V04 (ciel ouvert) | faisceaux de soleil visibles, intérieur ou extérieur |
| Fin d'après-midi dorée | V03 (rue) | ocre #ac7a53, or #ecc66e |
| Crépuscule violet | V02, V05 | ciel lavande #8a63d7, routes et herbes prune ou sombres, phares |
| Crépuscule chaud | V04 | brun #292523, orange #ad6937 |
| Nuit bleue saturée | V01, V02 | bleu outremer (#263d97 66 % V01, #07187a V02) + une source chaude locale |
| Nuit sous la pluie | V02, V04, V05 | bleus-gris, lanternes ou phares chauds, essuie-glaces |
| Aube et brume | V05 | violet-gris #484051, rose chaud #efdace |
| Intérieur néon froid | V01 | bleu-gris #34566a |
| Intérieur couleur-sujet | V01 (rose) | les murs colorent les personnages par rebond |
| Feu ou explosion | V03, V05 | orange #da773a / #e9ab5a, le feu éclaire le décor |
| Désaturé, souvenir ou sonné | V03 | saturation 0,02 (noir et blanc), 0,11-0,20 (réveil flou) |

## 3. Règles communes
- **L1** : une ambiance par étape du récit, au moins 4 par vidéo (MESURÉ). La bascule se fait dans une transition : fondu jour → nuit (V01 1291), fondu vers la nuit (V05 869), saut de temps (V04 465).
- **L2** : la nuit est un **changement de teinte globale vers le bleu saturé** avec **une ou deux sources chaudes** sur le point d'intérêt, et pas une simple baisse d'exposition (V01, V02, V05).
- **L3** : **lumière refaite par vue**. Un même lieu peut être éclairé différemment selon l'angle, si le changement est caché (V04 : soleil derrière l'arbre en aérien, côté caméra au pied de l'arbre).
- **L4** : un **accent rouge saturé** porte l'attention : voiture héros V02 #db172e, tunique du héros V05, bonnet V03 #8d1d33, yeux de rage V01 et V04.
- **L5** : noirs relevés le jour (aucun vrai noir hors des contours), hautes lumières douces, léger bloom sur les sources (néons, phares, fenêtres), aucun grain visible.

## 4. Matières (OBSERVÉ)
- **Peinture de véhicule** vernie et brillante avec reflets du ciel ; **vitres claires** avec intérieur visible : V02, V03, V04.
- **Pierre** taillée en blocs à joints (V05), parpaing peint (V01), brique (V03, V04).
- **Bois** au grain lisible en macro (V05 charrette, V04 piquets).
- **Végétation** : herbe 3D au premier plan, feuilles en paquets, champs texturés en bandes.
- **Asphalte** gris clair à grain fin (V02) ou bleu-gris usé avec traces (V04).
- **Émissif** : néons, ampoules (flèche V04), écrans (V01, V03), lanternes (V05).
- **Propreté** : peu de crasse ; l'usure existe (asphalte V04, épaves) mais reste modérée.

## 5. Reconstruction Blender (RECOMMANDATION, pas des réglages retrouvés)
- **Moteur** : choisir par **benchmark à scène identique** (EEVEE Next d'abord, Cycles en comparaison), voir `PRODUCTION_PIPELINE_SPEC.md` §H. Les références n'indiquent pas leur moteur (INCONNU).
- **Soleil** : une seule lampe soleil dure (angle ≤ 2°) placée pour l'image ; le ciel HDRI est limité pour l'éclairage (déjà codé : `rc/look.py`, leçon PI-025).
- **Rayons** : volume léger (densité 0,002-0,004) + soleil à travers un feuillage ou une ouverture.
- **Nuit** : balance des blancs vers le bleu (monde bleu saturé) + lampes ponctuelles chaudes ; exposition modérée, pas noire.
- **Couleur-sujet** : murs légèrement émissifs ou remplissage coloré pour teinter les personnages.
- **Désaturé / noir et blanc / doré** : au compositing, par plan, selon l'émotion.
- **Mesure** : `tools/grade_match.py` par plan, sur la plage de la référence choisie, jamais sur une moyenne globale.
