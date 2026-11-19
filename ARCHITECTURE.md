# ARCHITECTURE — RicksClips (19/11/2026)

`S/` = `.claude/skills/ricks-clips/`. L'architecture détaillée de la mission maîtresse (modules A à K, 12 phases) est dans `S/docs/ARCHITECTURE.md`. Ce document résume l'**actuel** et la **cible validée**.

## 1. Dépôt

```
/ (racine)                 documents de continuité (HANDOFF, PROJECT_STATE, ARCHITECTURE, DECISIONS, MIGRATION_PLAN, OPEN_ISSUES, CHANGELOG), anciens rapports
.claude/skills/ricks-clips/   LE SKILL : tout le code, les règles, les données
  CB_RULES.md              règles de CB (§11h = les plus récentes, prioritaires)
  START_HERE.md, SKILL.md, WORKFLOW.md   points d'entrée (l'historique three.js y est marqué « hérité »)
  blender/rc/              pipeline Blender : render, physics, vfx, lookdev, fetch, characters, qa, cache, library, envbuild, assemble, sound…
  tools/                   rc_pipeline.py, render_manager.py, card_service.py, card_anchors.py, plan_check.py, asset_hub.py, reference_compare.py, tests/
  templates/               vector2d_characters + motion_styles (personnages 2D), threejs_film (dessin des cartes ; décors hérités), production_plan (modèle de plan)
  library/                 assets (catalog.json ; fichiers des fournisseurs hors Git), reactions/reactions.json
  demos/farmyard/          démo de la mission maîtresse (place.json, jobs GPU, production/)
  demos/crashed_car/       reproduction de la vidéo de CB : sets/, shots/, tracks_*.json, build/ (hors Git)
  references/              crashed_car/ (analyse de la vidéo de CB ; source hors Git), STYLE_BIBLE_FR.md, fortress/
  memory/                  lessons_learned.json, LESSONS.md (leçons PI-001 à PI-016)
  scripts/runpod/          pod.py (protection des résultats), blender_pod.sh, manifest.py
  docs/                    ARCHITECTURE, GUIDE_UTILISATEUR_FR, REFERENCE_SCHEMAS, RAPPORT_MIGRATION_FR, PREPRODUCTION_FR
```

## 2. Architecture actuelle

```
Personnages : tracks_*.json ──> tools/card_service.py ──> film_plan bake + render_gpu.mjs --cards-only ──> cards/<qui>/s####.png + index.json (+ anchors.json)
Monde       : (a) place.json ──> tools/rc_pipeline.py (12 phases) ──> scene.blend              [démo ferme]
              (b) sets/*.py + shots/sNN_*.py (modules rc) ──> build/sNN.blend                [crashed_car, méthode retenue]
Contrôles   : continuity.py (avant rendu) ; qa / gates de rc_pipeline ; reference_compare.py
Rendu       : layers.py split (SKY/SET/OBJECTS/FX) ──> tools/render_manager.py (tranches, --patch) ──> layers.py comp ──> ffmpeg
GPU         : scripts/runpod/pod.py create/fetch/verify/delete + blender_pod.sh (demos/*/jobs)
```

- three.js ne sert plus qu'à **dessiner les personnages**. Ses décors sont gelés (hérités).
- Les outils génériques de la méthode (b) sont rangés pour l'instant dans `demos/crashed_car/`. Il s'agit de `street.pbr`, `hdri_reflections`, `handheld`, `continuity.py`, `layers.py` et `render_layers.sh`.

## 3. Architecture cible validée par CB (19/11)

```
script + voix ─> plan/plan.json + PLAN.md ─> plan_check.py PASS ─> assets en une fois (asset_hub / rc.fetch)
  ─> un script Blender par plan (décors pour le cadre, cartes 2D, objets tenus suivant tête et mains)
  ─> continuity.py PASS ─> ~8 images clés vues ─> rendu par couches (CPU basse déf pour valider, GPU RunPod pour le final)
  ─> corrections par --patch ─> son (−14 LUFS), sous-titres, montage
Chaque problème ─> leçon (memory/) + contrôle / recette / aide de code / ligne de modèle
```

**Écart entre l'actuel et la cible** (voir `MIGRATION_PLAN.md`) :
- les outils génériques sont à déplacer de `demos/crashed_car/` vers `blender/rc/` ;
- `plan_check` et `continuity` sont à brancher dans `rc_pipeline.py` ;
- les étapes son, voix et montage de la méthode par plan sont à outiller pour crashed_car.
