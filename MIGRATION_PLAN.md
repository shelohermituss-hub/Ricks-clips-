# MIGRATION_PLAN — de l'architecture actuelle à la cible validée

`S/` = `.claude/skills/ricks-clips/`. Aucune étape n'est destructive : on **ajoute et on déplace en gardant un import de compatibilité** ; rien n'est supprimé sans sauvegarde vérifiée et sans l'accord de CB.

## Fait

| Étape | Preuve |
|---|---|
| Pipeline `blender/rc` + `rc_pipeline.py` en 12 phases | `S/docs/RAPPORT_MIGRATION_FR.md`, `test_rc.py` 27/27 |
| Décors three.js gelés comme hérités, Ghost Army archivé | `S/docs/RAPPORT_MIGRATION_FR.md` §3 |
| Rendu par tranches, `--patch`, preuve GPU, protection RunPod | `tools/render_manager.py`, `test_pod_guard.py` 13/13 |
| Méthode par plan validée sur crashed_car (plans 1 et 2) | `S/demos/crashed_car/`, avis de CB du 19/11 |
| Barrières `plan_check.py` (avant construction) et `continuity.py` (avant rendu) | `test_plan_check.py` PASS ; continuité du plan 2 PASS |

## À faire, dans l'ordre (non fait)

1. **Déplacer les outils génériques hors de `demos/crashed_car/`**.
   - Destinations :
     - `sets/street.py` (`mat`, `pbr`, `hdri_reflections`, `handheld`, `box`, `cyl`, `sky`, `cloud`, `lib_instance`) → `blender/rc/kit.py` ;
     - `shots/continuity.py` → `blender/rc/continuity.py` ;
     - `shots/layers.py` → `blender/rc/layers.py` ;
     - `shots/render_layers.sh` → `tools/render_layers.sh`.
   - Laisser dans les anciens fichiers un import de compatibilité.
   - Vérification :
     - `test_rc.py` ;
     - rebuild de `s02_pit` et `s02_corner`, avec continuité PASS ;
     - sha256 identiques sur 3 images de contrôle par rapport aux rendus actuels.
2. **Brancher les barrières dans `tools/rc_pipeline.py`** : `plan_check` en phase 0, `continuity` avant la phase 11. Ajouter des tests.
3. ~~Relancer `continuity.py` sur le plan 1~~ **FAIT (19/11)** : `anchors.json` généré (0 saut de pose), continuité PASS à 0 partout ; rien à corriger.
4. **Outiller son, voix et montage pour la méthode par plan** : voix et mots minutés, sous-titres de 1 à 3 mots, ambiance et bruitage par action depuis `plan.json`, mixage à −14 LUFS. Réutiliser `rc/sound.py` et `templates/audio`.
5. **Mettre à jour `S/docs/ARCHITECTURE.md` et `S/docs/GUIDE_UTILISATEUR_FR.md`** pour décrire la méthode par plan comme voie principale des nouvelles vidéos.
6. Optionnel, avec l'accord de CB : **rendu de contrôle de la ferme calibrée** (CPU, environ 35 min) pour mesurer l'effet des corrections enregistrées (aujourd'hui NOT_RUN).

## Ne pas faire sans CB

- Supprimer des fichiers hérités (three.js, Ghost Army).
- Lancer un pod GPU ou dépasser un plafond de dépense.
- Changer la palette de référence, les personnages ou la voix.
