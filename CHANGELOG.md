# CHANGELOG — RicksClips (vue d'ensemble, racine du dépôt)

Historique détaillé des versions du skill : `.claude/skills/ricks-clips/CHANGELOG.md` (jusqu'à la V1.1 du 15/11). Pour la suite, voir `git log` sur la branche `ccr-00f60cb8-lenpig`. `S/` = `.claude/skills/ricks-clips/`.

## 19/11/2026 — base de style sur 7 vidéos de référence
- `S/tools/analyze_reference.py` : même analyse pour chaque vidéo (fiche technique, mesures par seconde, LUFS, mots minutés, coupes, planches).
- 6 nouvelles vidéos de CB analysées : pink_prison, dashcam, mine_salting, crash_instinct, whale_boat, plane_fall. Les sources restent en local.
- Documents mis à jour :
  - `S/references/ANALYSE_7_VIDEOS_FR.md` ;
  - `STYLE_BIBLE_FR.md` v2 (plages mesurées sur 7 vidéos, règles communes contre options).
- Catalogue des réactions : +12 recettes (36 au total).
- `plan_check.py` vérifie aussi l'histoire : crochet montré dans la 1re seconde, faits écrits dans le décor, au moins 2 ambiances, gros plan d'émotion, plan d'insert, sous-titres, boucle.
- Décision de CB : la prochaine étape est une nouvelle vidéo avec la nouvelle méthode ; crashed_car est en pause.

## 19/11/2026 — crash_instinct, plans 1 à 3 (branche `ccr-1c670715-ewni3e`)
- Vidéo de CB (il en est l'auteur) analysée ; plans 1 à 3 construits en une prise continue ; décor de route, chêne construit, SUV blanc métallisé et conducteur, voiture écrasée, roue arrachée.
- Méthode : aperçu rapide en une couche (`preview.sh`), `grade_match.py`, `rc/look.py` (lumière cinématique, textures réelles, usure de route), contrôles LOOK dans `plan_check`, contrôle CLIP dans `continuity.py`.
- `docs/CORRECTIONS_CB_FR.md` : toutes les corrections de CB et où elles sont appliquées ; leçons PI-017 à PI-024 ; règles CB_RULES §11h.

## 20/11/2026 — crash_instinct : vue aérienne corrigée, plan 4 préparé
- Environnement cloud « Ricks-clips » créé (hôtes Blender, Poly Haven, ambientCG, Sketchfab ; secret Sketchfab avec le préfixe Token). `restore_untracked.sh` retélécharge aussi le SUV.
- `rc/look.py` : la lampe est le seul soleil (ciel HDRI plafonné et réduit pour l'éclairage), `sun_glow()`, soleil −48° / 15°, `tex()` avec `recolor`, `untile`, `macro`, `stripes`, faisceaux larges et courts, brume 0,004.
- `roadside.py` : route bleu-gris usée, champs or / ocre / paille à rangs, accotement clair, herbe translucide ; touffes d'herbe sous la caméra aérienne.
- Mesures : `grade_match` PASS sur les images 180 et 262 ; continuité du plan 3 PASS.
- Plan 4 : analyse à 10 i/s (`shots/s04.md`), `plan/s04.json` PLAN PASS, recette `counter_flip`, `sets/sign.py`, `shots/s04_sign.py`.
- Plan 4 corrigé d'après CB : voiture de la référence analysée et remplacée (« Generic Kei car », bleu mesuré, vitres claires, intérieur visible), roue avant de la voiture découpée du modèle qui se détache et roule, lumière de la référence analysée vue par vue (`shots/s04.md` §10) et appliquée par `rc.look.relight()` dans le fouetté ; leçons PI-029, PI-030.
- Leçons PI-025 à PI-028 ; `docs/CORRECTIONS_CB_FR.md` complété (9 lignes).

## 19/11/2026 — reprise dans une session neuve (branche `ccr-1c670715-ewni3e`)
- Blender 5.2.2 installé (`download.blender.org` ajouté aux hôtes autorisés de l'environnement).
- Session neuve : `test_rc` 25/27 → **27/27** après correction (leçon PI-017) : `tools/gltf_to_glb.py`, `scripts/restore_untracked.sh`, `test_rc` cuit le plan manquant. `test_pod_guard` 13/13, `test_plan_check` PASS, `test_production_intelligence` 11/11 (après `git fetch --unshallow`).
- Plan 1 : continuité **PASS** avec la version actuelle (MIGRATION_PLAN étape 3).
- OPEN_ISSUES n° 13 corrigé : licence déjà remplie ; vrai écart = auteur de la berline.
- Fusion de `origin/ccr-00f60cb8-lenpig` (7 vidéos de référence, gta6-leak).

## 19/11/2026 — passation
- Ajout à la racine de `HANDOFF.md`, `PROJECT_STATE.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `MIGRATION_PLAN.md`, `OPEN_ISSUES.md` et `CHANGELOG.md`.
- Correction de `S/tools/tests/test_rc.py` : chaque résultat de test est converti en booléen. Un test renvoyait un dictionnaire et faisait planter le comptage final ; le test lui-même passait. Suite relancée : 27/27 PASS.
- Le commit de passation est celui qui ajoute ces fichiers (`git log -1 -- HANDOFF.md`).

## 19/11/2026 — méthode nouvelle vidéo sans référence (`d07c50f`)
- `S/tools/plan_check.py` : barrière avant construction.
- `S/templates/production_plan/` : modèle de plan et exemple rempli.
- `S/library/reactions/reactions.json` : 24 recettes.
- `S/references/STYLE_BIBLE_FR.md`, `S/docs/PREPRODUCTION_FR.md`.
- Nouvelles règles dans `CB_RULES` §11h.
- Test `test_plan_check.py`.

## 19/11/2026 — catalogue d'assets (`66bfda6`)
- Textures Poly Haven CC0 ajoutées au catalogue : asphalt_pit_lane, asphalt_track, concrete_wall_008.

## 19/11/2026 — continuité et plan 2 v2 (`72e8b33`, `f5e81ea`)
- `continuity.py` vérifie avant tout rendu les apparitions, téléportations, rétrécissements, sauts de pose et arrêts caméra. Le rendu est bloqué s'il échoue.
- `card_anchors.py` mesure la tête, les pieds et les mains sur chaque dessin.
- Plan 2 refait en actions continues :
  - un seul personnage, qui saute hors du cockpit ;
  - il retire son casque à deux mains, puis le tient sous le bras ;
  - caméra toujours en mouvement.
- Textures et éclairage :
  - textures PBR CC0 ;
  - pneus et jerrycans ;
  - soleil dur ;
  - peinture vernie et reflets d'un HDRI.
- Ajout de la récupération des HDRI dans `rc.fetch.polyhaven_hdri`.
- Leçon PI-016.
- Rendu par couches en 21 min 54 s.

## 19/11/2026 — plan 2 v1, règles de rendu (`8e2ebd7`, `78b9ece`, `ebb33d4`, `2846c41`)
- Décors du circuit, F1 Sketchfab recolorée, casque, confettis, module de couches.
- Règles :
  - rendu par couches ;
  - analyse détaillée de chaque plan avant construction ;
  - ne corriger que ce qui change ;
  - option `render_manager --patch`.

## 19/11/2026 — plan 1 et analyse de la vidéo de CB (`c39a31c`, `b3311a3`, `ae00e0c`, `497e592`, `d851fcd`, `03e42ed`)
- Analyse complète de « He Crashed His Own Car For Science ». La source reste en local.
- Plan 1 :
  - vrai crash et barils qui éclatent ;
  - héros qui descend de la voiture ;
  - décor enrichi.
- CB l'accepte tel quel.

## 18-19/11/2026 — mission maîtresse de restructuration (`1c9ae34` et précédents)
- Pipeline Blender `rc` (17 modules Python + `schema/`) et orchestrateur en 12 phases.
- Bibliothèque, caches, physique, effets visuels, LookDev, contrôle qualité.
- Démo ferme :
  - rendu GPU RunPod : 1,06 $, pod supprimé après récupération vérifiée ;
  - phase 12 FAIL, livrée telle quelle sur décision de CB.
- Rapport : `S/docs/RAPPORT_MIGRATION_FR.md`.
