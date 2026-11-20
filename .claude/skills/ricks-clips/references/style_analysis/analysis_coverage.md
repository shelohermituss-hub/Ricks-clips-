# Couverture réelle de l'analyse

Statut global de la mission : **PARTIAL** — les cinq sources ont été ouvertes et analysées aux niveaux A, B et C, mais le niveau C (image par image) ne couvre que 2 à 3 passages par vidéo, et l'audio n'a pas été écouté. Détail par vidéo : `data/V0x/coverage.json`.

## Déroulé honnête
- Les cinq vidéos ont été copiées sans modification dans `_sources/` (empreintes SHA-256 identiques aux fichiers reçus, `input_manifest.json`). Un 6e fichier reçu est un doublon exact de V04 (même SHA-256), non analysé à part.
- Une première passe avec 5 analystes en parallèle a été **arrêtée à la demande de CB** (consommation trop rapide). Elle a laissé 207 captures (V01, V02, V05) et des séquences extraites, sans aucune analyse écrite. Ces captures ont été réutilisées et recoupées avec les planches ; tout le texte a été écrit ensuite par un seul analyste (le chef d'analyse), vidéo par vidéo.

| Vidéo | Ouverte | Durée / images | Plans | Captures | Échantillonnage | Image par image | Audio | Statut |
|---|---|---|---|---|---|---|---|---|
| V01 The Pink Prison Cell Experiment | oui | 65.3 s / 1957 | 13 | 69 (+4 planches) | 100 % à 2 i/s ; 10 i/s via captures | 750-797, 1524-1547, 1384-1407 (96 images, 4.9 %) | mesures seulement | PARTIAL |
| V02 Why Drivers Started Filming The Road | oui | 62.3 s / 1867 | 19 | 77 (+4 planches) | 100 % à 2 i/s ; 10 i/s via captures | 80-103, 908-931 (48 images, 2.6 %) | mesures seulement | PARTIAL |
| V03 He Survived Falling Out Of A Plane | oui | 83.1 s / 2490 | 18 | 43 (+5 planches) | 100 % à 2 i/s ; 43 captures du chef d'analyse | 96-119, 1998-2021 (48 images, 1.9 %) | mesures seulement | PARTIAL |
| V04 The Instinct That Makes You Crash | oui | 59.5 s / 1783 | 20 | 36 (+3 planches) | 100 % à 2 i/s ; plans 1-4 à 10 i/s (session de reproduction) | 84-107, 1224-1247 (48 images, 2.7 %) | mesures seulement | PARTIAL |
| V05 How One Cart Stopped an Entire Army | oui | 66.9 s / 2005 | 17 | 61 (+4 planches) | 100 % à 2 i/s ; 10 i/s via captures | 762-785, 1808-1831 (48 images, 2.4 %) | mesures seulement | PARTIAL |

## Passages complexes étudiés
- **V01** : piétinement et fissures 750-797; rage éclairs 788-858 (2 fps + captures); bras de fer 1030-1060 (captures); traversée du toit 1150-1170 (2 fps + mesure de différence); poussée dans le moniteur 1384-1407; arrachage du banc 1524-1547
- **V02** : choc 80-103 (image par image); choc nuit 908-931 (image par image); explosion de billets 440-475 (2 fps + captures); compteur 1054-1071 (capture); replay dashcam 1690-1829 (2 fps + captures)
- **V03** : porte 96-119 (image par image); glissière 1998-2021 (image par image); chute 168-359 (2 fps); déraillement 1125-1289 (2 fps); explosion 1500-1649 (2 fps); éjection et chute 2030-2219 (2 fps)
- **V04** : chute du chêne 14-40; choc + roue 84-140 (image par image 84-107); fouetté 282-285 qui cache une semaine; choc bleu + pile de pneus + compteur 309-351 (10 i/s); coup de hache et ciel ouvert 939-1069 (2 fps); voiture verticale 1224-1247 (image par image)
- **V05** : perçage en macro 0-60; construction de la charrette 436-700 (captures); gifle 762-785 (image par image); parapluie humain 900-1100 (2 fps); étincelle et flammes 1531-1800 (2 fps + captures); lancement 1808-1831 (image par image); explosions 1900-1964 (2 fps)

## Plages seulement échantillonnées
Tout ce qui n'est pas listé « image par image » a été vu à 2 i/s (planches overview, 100 % de chaque vidéo) et, pour certains plans, par des captures ou des séquences à 10 i/s (V04 plans 1-4 lors de la reproduction ; captures de l'analyste interrompu pour V01, V02, V05).

## Limites des outils
- `ffmpeg`/`ffprobe` 6.1.1, OpenCV 5.1, numpy, soundfile, faster-whisper small.en : utilisés.
- **PySceneDetect absent** : coupes détectées par différence d'image + histogramme, puis vérifiées à l'œil ; le seuil manque les fondus et les coupes à luminance égale (V05 : 0 candidat, 4 coupes réelles).
- **Aucune écoute audio possible** : seulement loudness, enveloppe, attaques, corrélation, mots minutés.
- Couleurs : vidéo H.264 8 bits compressée ; quelques échantillons ponctuels ont manqué leur objet et sont marqués REJETÉ (V01, V02) ; V03-V05 décrits par k-means.
- Proportions des personnages estimées sur les planches, non mesurées au pixel.

## Tâches non exécutées
- Lecture image par image des autres passages complexes (rage V01 798-869, bras de fer V01 1030-1077, chocs V02 530-555 et 810-830, déraillement et explosion V03, coup de hache V04, construction et explosions V05).
- Mesure en pixels des proportions des personnages ; recherche systématique des clignements et micro-mouvements fins.
- Écoute et identification de la musique et des bruitages.
- Benchmark EEVEE Next / Cycles (hors mission d'analyse : spécifié dans `PRODUCTION_PIPELINE_SPEC.md` §H).

## Vérifications faites
- Les cinq sources existent, sont décodables, SHA-256 notés ; non modifiées.
- 5 analyses, 87 plans, 53 événements, 72 assets ; les CSV se relisent avec le module `csv` (en-têtes identiques sur les 5 vidéos) et les JSON avec `json.load`.
- Timecodes = image / 30, recalculés par script.
- Provenance des palettes : image, région, méthode dans `palette_catalog.json`.
- Aucun rendu lancé pendant la mission, aucun fichier de production modifié (seul `references/style_analysis/` a été écrit).

## Niveau de confiance
- **Haut** : mesures techniques, structure, liste des plans, ambiances, chaînes d'événements vérifiées image par image.
- **Moyen** : détail des micro-animations, méthodes des effets (INFÉRÉ).
- **Bas / inconnu** : son (musique, bruitages), logiciels et réglages des originaux.
