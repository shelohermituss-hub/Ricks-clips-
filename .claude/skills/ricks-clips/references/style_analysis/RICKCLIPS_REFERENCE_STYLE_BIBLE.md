# RicksClips — bible de style tirée de 5 vidéos de référence

Document central. Il dit **ce qui est commun aux cinq vidéos** (à appliquer toujours), **ce qui varie** (à choisir selon l'histoire) et **où se trouve le détail**.

Statuts : **OBSERVÉ**, **MESURÉ**, **INFÉRÉ**, **INCONNU**, **RECOMMANDATION**.

Sources :
- V01 « The Pink Prison Cell Experiment » ;
- V02 « Why Drivers Started Filming The Road » ;
- V03 « He Survived Falling Out Of A Plane » ;
- V04 « The Instinct That Makes You Crash » ;
- V05 « How One Cart Stopped an Entire Army ».

Inventaire : `input_manifest.json`. Couverture réelle : `analysis_coverage.md` (statut global **PARTIAL**).

| Domaine | Document spécialisé |
|---|---|
| Formes, composition, lisibilité | `VISUAL_LANGUAGE.md` |
| Personnages, jeu, micro-animations | `CHARACTER_DESIGN_AND_ANIMATION.md` |
| Lieux, assets, matières, profondeur | `ENVIRONMENT_AND_ASSET_BIBLE.md` |
| Caméra, montage, rythme | `CAMERA_AND_EDITING_LANGUAGE.md` |
| Lumière, couleur, étalonnage | `LIGHTING_COLOR_AND_MATERIAL_BIBLE.md` |
| Interactions, physique, conséquences | `INTERACTION_AND_PHYSICS_LANGUAGE.md` |
| Effets, compositing | `VFX_AND_COMPOSITING_BIBLE.md` |
| Son | `SOUND_AND_AUDIO_LANGUAGE.md` |
| Fabrication | `PRODUCTION_PIPELINE_SPEC.md` |
| Nouvelle histoire | `ADAPTATION_RULES.md` |
| Contrôles | `QUALITY_GATES.md` |
| Catalogues | `shot_catalog.csv` (87 plans), `event_catalog.csv` (53 événements), `asset_catalog.csv` (72 assets), `palette_catalog.json` |
| Analyses par vidéo | `per_video/V01_ANALYSIS.md` … `V05_ANALYSIS.md` |

---

## 1. Identité en une phrase
Des personnages 2D très simples (tête blanche ronde à gros contour noir, membres en traits) **jouent dans des décors 3D riches et éclairés comme un film**. La caméra ne s'arrête jamais. Chaque fait raconté est **montré par une action physique** qui laisse **une trace durable**. Une voix continue est sous-titrée mot à mot.

## 2. Règles communes aux cinq vidéos (à appliquer toujours)
| # | Règle | Preuve |
|---|---|---|
| C1 | **Format** : 9:16, 720×1280 livré, 30 i/s, 59-83 s | MESURÉ, `input_manifest.json` |
| C2 | **Voix continue**, sans pause de plus de 0,64 s ; 3,2 à 3,8 mots/s ; elle commence à 0,00 s | MESURÉ, `data/cross_video_measures.json` |
| C3 | **Son à −14 LUFS** (−13,9 à −14,2), plage 2,2-3,9 LU, quasi mono (corrélation 0,97-1,00) | MESURÉ |
| C4 | **Crochet par l'action à l'image 0** : on peint (V01), on freine (V02), on boit à côté de la porte (V03), on plante (V04), on perce (V05) | OBSERVÉ, images 0 |
| C5 | **Caméra toujours en mouvement** : 0 à 3,1 % d'images quasi fixes | MESURÉ |
| C6 | **Personnages** : tête blanche ronde à contour noir épais, membres en traits noirs, torse habillé coloré ; rôle lu à 2-3 accessoires ; même design dans les cinq vidéos | OBSERVÉ |
| C7 | **Décors 3D continus et détaillés** où les personnages projettent des ombres | OBSERVÉ (V01 615-645, V04, V05) |
| C8 | **Chaque fait = une action physique visible**, synchronisée sur le mot | MESURÉ (mots minutés), chaque analyse §1 |
| C9 | **Chaque action laisse une conséquence qui reste** au plan suivant (fissure, épave, pile de pneus, tas de billets, sol défoncé, voiture brûlée) | OBSERVÉ, `event_catalog.csv` colonne `persistence` |
| C10 | **Émotion extrême = signe graphique 2D** sur le personnage (éclairs, yeux rouges, spirales, aura, $, gribouillis, sueur) | OBSERVÉ dans les 5 |
| C11 | **La lumière et la couleur changent avec l'histoire** : au moins 4 ambiances par vidéo (V01 : 5, V02 : 7, V03 : 10, V04 : 8, V05 : 10) | MESURÉ (k-means) |
| C12 | **Sous-titres** : 1-2 mots, blanc gras arrondi, contour noir épais, centrés, changés à chaque mot | OBSERVÉ |
| C13 | **Chute** qui retourne ou boucle le début (V01 rage, V02 dashcam, V03 jackpot, V04 même choc qu'au début, V05 sourire devant le champignon) | OBSERVÉ |
| C14 | **Matières propres et lisibles** plutôt que sales : la richesse vient des objets et de la lumière, pas de la crasse | OBSERVÉ |

## 3. Ce qui varie (à choisir selon l'histoire, ne pas uniformiser)
| Paramètre | Plage observée | Exemples |
|---|---|---|
| Durée médiane des plans | 2,6 s (V02, V05) à 4,7 s (V01) | `shot_catalog.csv` |
| Coupes franches | 0 pendant 22,9 s (V04) à environ 8 (V02) | analyses §1 |
| Mouvement de caméra (médiane de différence d'image, sur 255) | 4,2 (V04) à 15,5 (V03) | MESURÉ |
| Saturation moyenne | 0,28 (V04, pastel naturaliste) à 0,44 (V02, vif) | MESURÉ |
| Nombre de lieux | 1 lieu revu 6 fois (V04) à 9 lieux (V03) | analyses §4 |
| Textes dans le décor | nombreux (V01, V03, V04) à aucun (V05) | analyses §4 |
| Ambiance de nuit | absente (V05 : nuit très courte), nuit bleue (V01, V02), nuit pluvieuse (V02, V04, V05) | analyses §6 |
| Structure | linéaire (V01, V02, V05), anthologie datée (V03), lieu-compteur (V04) | analyses §1 |

## 4. Matrice de comparaison
Légende : ●●●●● commun aux cinq ; nombre = vidéos concernées ; « 1 » = une seule ; « ? » = ambigu.

| Caractéristique | V01 | V02 | V03 | V04 | V05 | Statut |
|---|---|---|---|---|---|---|
| Personnages tête blanche + traits | oui | oui | oui | oui | oui | commun aux cinq |
| Décors 3D éclairés | oui | oui | oui | oui | oui | commun aux cinq |
| Caméra toujours en mouvement | oui | oui | oui | oui | oui | commun aux cinq |
| Voix continue −14 LUFS | oui | oui | oui | oui | oui | commun aux cinq |
| Conséquence persistante | oui | oui | oui | oui | oui | commun aux cinq |
| Signe 2D d'émotion | oui | oui | oui | oui | oui | commun aux cinq |
| Changement d'ambiance lumineuse | oui | oui | oui | oui | oui | commun aux cinq |
| Transition « par l'objet » (porte, écran, billet, vitre) | oui | oui | oui | non | non | 3 sur 5 |
| Fouetté qui cache un saut de temps | oui (420) | non | non | oui (282) | oui (66) | 3 sur 5 |
| Nuit | oui | oui | oui (crépuscule) | oui | oui | commun, forme variable |
| Pluie | non | oui | non | oui | oui | 3 sur 5 |
| Véhicule percuté | non | oui | oui | oui | non | 3 sur 5 |
| Carrosserie déformée | — | légère (pare-chocs) | forte (capot froissé) | moyenne (roue, pare-brise) | — | à proportionner |
| Foule de centaines de figures | non | non | non | non | oui | 1, ne pas généraliser |
| Vue aérienne | oui | non | oui | oui | oui | 4 sur 5 |
| Macro sur un objet | oui (chrono) | non | non | non | oui | 2 sur 5 |
| Image dans l'image (écran, dashcam) | oui (CRT) | oui | oui (écrans) | non | non | 3 sur 5 |
| Noir et blanc, flou de réveil | non | non | oui | non | non | 1, effet ponctuel |
| Textes diégétiques | oui | oui | oui | oui | non | 4 sur 5 |
| Objet planté puis payé | oui (chrono) | oui (dashcam) | oui (billet) | oui (flèche) | oui (charrette) | commun aux cinq |

## 5. Guide d'application (RECOMMANDATION)
1. **Écrire** le script : crochet par l'action, voix continue à environ 3,5 mots/s.
2. Pour chaque phrase, désigner **l'action visible** et **sa conséquence qui reste** (`INTERACTION_AND_PHYSICS_LANGUAGE.md`).
3. Choisir une **structure** (linéaire, anthologie datée, lieu-compteur) et le **nombre de lieux** (`ADAPTATION_RULES.md`).
4. Fixer **une ambiance de lumière par étape** du récit (au moins 4) et l'étalonnage par mesure (`LIGHTING_COLOR_AND_MATERIAL_BIBLE.md`).
5. Écrire les **mouvements de caméra** : jamais d'arrêt ; transitions par l'objet ou par fouetté (`CAMERA_AND_EDITING_LANGUAGE.md`).
6. Placer les **signes 2D d'émotion** et les effets (`VFX_AND_COMPOSITING_BIBLE.md`).
7. Contrôler avec les portes de `QUALITY_GATES.md` avant chaque rendu.

## 6. Ce qui reste INCONNU
- Logiciel et moteur de rendu des originaux.
- Méthode exacte des personnages : 2D intégrée à la 3D, INFÉRÉ (contour constant quand la caméra tourne).
- Méthode des effets de feu et d'eau, rig, textures sources.
- Musique, bruitages et timbre des voix : les pistes n'ont pas été écoutées ; seules des mesures ont été faites.
