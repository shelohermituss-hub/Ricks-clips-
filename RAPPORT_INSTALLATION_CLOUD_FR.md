# Rapport d'installation RicksClips V1.3 dans Claude Code Web

Date : 2026-11-17. Aucune production vidéo n'a été lancée.

## Source et intégrité

- Archive `RicksClips_Claude_Code_Web_V1.3` (156,8 Mo, 892 fichiers) récupérée depuis Google Drive, puis copiée à la racine du dépôt.
- Le manifeste `SHA256SUMS.txt` (891 fichiers) a été vérifié avant toute modification : **891/891 OK**. Ce manifeste décrit la livraison d'origine. Les fichiers corrigés ci-dessous ne correspondent donc plus volontairement à leur somme d'origine.

## Environnement cloud

- Environnement personnel `ricks-clips` (réseau Limited, gestionnaires de paquets autorisés). Domaines autorisés : `drive.google.com`, `drive.usercontent.google.com`, `download.blender.org`.
- Setup script de l'environnement : `scripts/cloud_environment_setup.sh` (version corrigée, testée dans cette session). Il ne sera vraiment éprouvé qu'au démarrage d'une nouvelle session sur cet environnement.
- Machine : Ubuntu 24.04.5 LTS, 4 vCPU, 15 Go de RAM, **aucun GPU**.

## Logiciels installés

| Logiciel | Version | Origine |
|---|---|---|
| Blender | 5.2.2 LTS (`/opt/blender-5.2.2-linux-x64`, lien `/usr/local/bin/blender`) | download.blender.org, SHA-256 vérifié |
| FFmpeg / ffprobe | 6.1.1-3ubuntu5 | apt |
| Python | 3.13.18 | préinstallé |
| Node.js / npm | 22.23.4 / 10.9.9 | préinstallé |
| Chrome for Testing | 153.0.8010.12 (`/usr/bin/google-chrome`) | préinstallé |
| Playwright (projet) | 1.49.1 | npm |
| Three.js | 0.165.0 (npm) + `vendor/three.module.js` | npm / livré |
| WebGL | WebGL 2.0, ANGLE / SwiftShader (logiciel, CPU) | Chrome |

## Dépendances Python (`.venv`)

Pillow 13.0.0, numpy 2.5.5, scipy 1.18.1, soundfile 0.14.0, faster-whisper 1.2.1, opencv-python-headless 5.0.0.93. Dépendances transitives : ctranslate2 4.9.0, onnxruntime 1.32.0, av 19.0.2, huggingface-hub 2.4.0, tokenizers 0.23.3.

## Tests

| Test | Résultat |
|---|---|
| Cloud Doctor (`scripts/cloud_doctor.sh`) | **PASS=12, WARN=1, FAIL=0** (WARN = pas de GPU NVIDIA) |
| Asset Hub, 16 tests unitaires (`tools/test_asset_hub.py`) | PASS 16/16 |
| Motion QA (`tools/check_motion_quality.mjs`) | PASS : 42/42 modules, 195/195 références, 330 styles, 2 640 poses |
| Look3D API (`tools/test_look3d_api.mjs`) | PASS, sans avertissement Node après correction |
| Asset Loader Three.js (`tools/test_asset_loader.mjs`) | PASS |
| Motion polish (`tools/test_motion_polish.mjs`) | PASS |
| Smoke test Chrome + Playwright + WebGL | PASS (SwiftShader) |
| `render_gpu.mjs --gpu-info --software` (copie de `film_example`) | PASS : WebGL 2.0, SwiftShader, mode logiciel |
| `film_plan.py check` (copie de `film_example`) | PASS : 41 gates, 0 FAIL, 1 WARN de contenu |
| `check_cinematic_quality.py`, avant rendu (copie de `film_example`) | PASS : 8 PASS, 0 WARN, 0 FAIL, 2 NOT RUN (vidéo / GPU) |
| frame_checks, 3 films piégés (`tests/run_tests.mjs`) | PASS : 3/3 défauts détectés (3 min 55 s) |
| `test_grips`, `test_lie3d`, `test_faces` (planches) | PASS |
| `outfit_hook_test.mjs` | PASS (empreintes identiques) |
| Rendus Blender 128 px, EEVEE et Cycles CPU | PASS (EEVEE 28 s dont la compilation des shaders, Cycles 0,2 s) |
| Import `blender_look` et `blender_cine` dans Blender 5.2.2 | PASS |
| Analyse syntaxique : 87 fichiers .py, 206 .js/.mjs, 66 .json, scripts bash | PASS |
| `tools/check_views.mjs` (vues personnages approuvées) | **FAIL** : 16 vues identiques ; 7 personnages sans source (dossier `episodes/` absent de l'archive) |
| `check_film.py` | N/A : contrôle une vidéo rendue, et aucune n'existe |
| `views_golden/limbs_v13/chair_scene_test.mjs` | N/A : copie d'archive avec d'anciens chemins (`puppets.mjs`) |

## Corrections appliquées

1. **Lancement de Chrome en cloud.** 22 scripts appelaient `chromium.launch()` sans chemin. Playwright 1.49.1 cherchait alors un navigateur non téléchargé, d'où l'échec de `check_views.mjs`. En cloud seulement (`CLAUDE_CODE_REMOTE=true`), ils utilisent désormais `CHROME_PATH` ou `/usr/bin/google-chrome`, comme `render.mjs`. Le comportement sur le PC Windows ne change pas.
2. **`render_gpu.mjs`.** En cloud, le chemin logiciel (SwiftShader) est maintenant forcé. Avant, sans `--software`, il tentait la voie GPU Direct3D, et `frame_checks` échouait avec le code 2.
3. **Avertissement Node `MODULE_TYPELESS_PACKAGE_JSON`.** Ajout de `package.json` `{"type":"module"}` dans `threejs_film/vendor/` et `threejs_film/sets/` uniquement.
4. **`package-lock.json`.** `three@0.165.0` manquait dans le lockfile ; il a été rafraîchi par `npm install`, comme le demande `CLOUD_MODE.md`.
5. **Blender.** apt ne fournissait que la 4.0.2, alors que le pipeline est audité sur la 5.2.2. `cloud_environment_setup.sh` installe maintenant la 5.2.2 officielle (SHA-256 vérifié) et se replie sur apt en cas d'échec. Le Cloud Doctor signale une version différente de la 5.2, et `download.blender.org` est ajouté à `CLOUD_NETWORK_DOMAINS.txt`.

## Fonctionnalités opérationnelles

- Skill `/ricks-clips` et 16 agents de projet reconnus par Claude Code.
- Hook SessionStart : installation et vérification automatiques du `.venv` et des paquets npm.
- Three.js + Playwright + WebGL logiciel : storyboards, animatiques et aperçus à petite échelle avec `--software`.
- Blender 5.2.2 headless : EEVEE et Cycles en CPU, paquets `blender_look` et `blender_cine`.
- FFmpeg / ffprobe, outils de mesure et de qualité Python, bibliothèque de mouvements, frame_checks, planification (`film_plan.py`).

## Ce qui demande encore une configuration

- **Domaines des fournisseurs d'assets**, actuellement bloqués : Poly Haven, ambientCG, Sketchfab, Fab, BlenderKit, Fish Audio (voir `CLOUD_NETWORK_DOMAINS.txt`). Les entrées génériques (`*.polyhaven.com`, etc.) s'ajoutent dans les paramètres de l'environnement.
- **Clés API, via Network Secrets** : Fish Audio (`api.fish.audio`) et Sketchfab (`api.sketchfab.com`).
- **Modèles faster-whisper** : `huggingface.co` est bloqué, donc le téléchargement des poids pour la transcription n'est pas possible.
- **BlenderKit** : aucune connexion ; le compte Windows n'est pas transféré.
- **Dossier `episodes/`** (baboon-signalman, goldrush…) : absent de l'archive. Il est nécessaire pour que `check_views.mjs` passe entièrement.
- **GPU** : aucun. Les rendus finaux 1080×1920 à 30 fps doivent être mesurés sur un court extrait, ou faits sur le PC GPU.
