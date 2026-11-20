# Effets et compositing

Bible centrale : `RICKCLIPS_REFERENCE_STYLE_BIBLE.md`. Détail par vidéo : analyses §9.

## 1. Deux familles d'effets (OBSERVÉ dans les cinq vidéos)
| Famille | Rôle | Exemples | Méthode probable |
|---|---|---|---|
| **Signes graphiques 2D** | dire une émotion ou une force | éclairs rouges (V01, V04), yeux lumineux (V04), spirales (V04), $ (V03), aura et rochers en lévitation (V05), onde de choc circulaire (V01, V05), lignes d'impact (V01), gribouillis (V05), étincelles brillantes (V02), sueur, buée | 2D superposé : INFÉRÉ |
| **Effets physiques en volume** | conséquence matérielle | poussière, débris, étincelles de choc, fumée, feu, eau, billets, dalles de sol, traînées de fusées, explosions | 3D, particules ou volumes : INFÉRÉ |

Les deux cohabitent dans le même plan. Exemple : la gifle de V05, avec aura 2D et onde 2D, puis dalles 3D et casque 3D.

## 2. Catalogue avec timing (OBSERVÉ image par image quand indiqué)
| Effet | Déclencheur | Naissance → fin | Exemple vérifié |
|---|---|---|---|
| Fissures au sol | impact du pied | 4 images de croissance, puis figées et persistantes | V01 762-775 (image par image) |
| Débris de choc | contact de véhicule | projetés 6-10 images dans le sens du choc | V02 92-98 (image par image) |
| Poussière d'accotement | roues dans le bas-côté | **avant** le choc, environ 0,4 s | V04 91-103 (image par image) |
| Étincelles de rupture | pression | une par une sur 7 images, puis flash | V03 102-110 (image par image) |
| Flash blanc | explosion, rupture | 2-4 images plein cadre | V03 110-113, 1545 |
| Étincelles de nuit | choc de nuit | 4-6 images | V02 927-931 (image par image) |
| Aura, rochers en lévitation | colère avant le geste | environ 7 images avant le coup | V05 762-768 (image par image) |
| Onde de choc circulaire | coup | 3-4 images d'expansion | V05 778-781 (image par image) ; V01 818 |
| Flash + gerbe d'étincelles | lancement | environ 10 images | V05 1822-1831 (image par image) |
| Traînées de fumée | fusées | 2 s, s'enroulent | V05 1842-1890 |
| Billets en masse | gain | jaillissent environ 0,5 s, puis tas qui reste | V02 445-475, 840-880 |
| Feu | explosion de voiture | continu, éclaire le décor | V03 1560-1649 |
| Rayons de ciel ouvert | action finale | trou circulaire dans les nuages, faisceaux | V04 975-1050 |
| Pluie | ambiance | continue | V02, V04, V05 |

## 3. Compositing et montage
- **Vignettage subjectif → noir** (V03 435-509).
- **Flou de réveil** qui se dissipe (V03 510-560).
- **Noir et blanc** pour le souvenir (V03 2280-2330).
- **Texture d'écran CRT** puis entrée dans l'écran (V01 1384-1400).
- **HUD de dashcam** : date, heure, vitesse, REC (V02 1657-1829).
- **Rembobinage** en fondu (V02 1691).
- **Changement de fond** pendant la rage : le décor rougit (V01 795-848).
- **Bascule globale de lumière** vers le doré à la récompense (V03 2445-2489).

## 4. Synchronisation
Les effets naissent **sur l'image du contact** ou sur le mot (MESURÉ par les mots minutés).
Les attaques audio coïncident avec les impacts quand ils ont été vérifiés : V01 25,4 s ; V02 2,8 s ; V05 25,9 s. C'est INFÉRÉ : le son n'a pas été écouté.

## 5. Équivalents Blender (reconstruction proposée)
| Effet | Proposition RicksClips | Existant dans le dépôt |
|---|---|---|
| Signes 2D (éclairs, aura, onde, spirales, $) | cartes 2D animées attachées au personnage, couche FX séparée | `rc.vfx`, couches FX de `layers.py` |
| Poussière, débris, étincelles | `rc.vfx` dust_burst / particules avec durée de vie | `rc.vfx` |
| Fumée, feu | volumes ou cartes animées, lampe ponctuelle chaude animée pour l'éclairage | `rc.vfx` smoke |
| Fissures persistantes | décalque animé (croissance en 4 images) qui reste | à créer |
| Flash plein cadre | compositing (2-4 images) + lampe très forte | à créer |
| Vignettage, flou, noir et blanc, CRT, HUD | compositing par plan | `lookdev` en partie |
| Matière en masse (billets) | instances avec simulation ou keyframes, tas persistant | `rc.geo.instancer` |
