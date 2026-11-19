# PROJECT_STATE — état du projet RicksClips au 19/11/2026

Document de référence de l'état chiffré. La passation complète est dans `HANDOFF.md`. `S/` = `.claude/skills/ricks-clips/`.

Statuts :
- **FAIT** : avec preuve ;
- **PARTIEL** ;
- **NON FAIT** ;
- **NOT_RUN** : jamais exécuté, ce qui ne vaut jamais PASS.

## 1. Vue d'ensemble

| Chantier | Statut | Où |
|---|---|---|
| Mission maîtresse de restructuration (15 livrables) | 14 PASS, 1 PARTIEL (n° 14, vidéo prototype) | `S/docs/RAPPORT_MIGRATION_FR.md` §2 |
| Démo cour de ferme | Phases 1 à 11 PASS, **phase 12 FAIL** (standard forteresse 5/10 en GPU, 6/10 en CPU), livrée telle quelle sur décision de CB | `S/demos/farmyard/production/` |
| Reproduction de la vidéo de CB « crashed_car » | **PARTIEL** : 2 plans sur 15 | `S/demos/crashed_car/`, `S/references/crashed_car/` |
| Méthode nouvelle vidéo sans référence | **FAIT** (outils et documents) ; **NOT_RUN** sur une vraie vidéo | `S/docs/PREPRODUCTION_FR.md` |
| Base de style : 7 vidéos de référence de CB analysées | **FAIT** (19/11) | `S/references/ANALYSE_7_VIDEOS_FR.md`, `S/references/STYLE_BIBLE_FR.md` v2 |
| Ghost Army | **Archivé** (rien supprimé) | `S/episodes/ghost-army/ARCHIVED.md` |

## 2. crashed_car, plan par plan

| Plan | Temps (s) | Analyse détaillée | Script | Continuité | Rendu | Avis de CB |
|---|---|---|---|---|---|---|
| 1 — rue, crash dans les barils | 0 – 4,1 | dans `ANALYSE_FR.md` §3 (pas de `s01.md`) | `s01_driveway.py` | PASS (version d'avant le contrôle des sauts de pose) | v2, 270×480 | **Accepté tel quel** |
| 2 — stand + virage | 4,07 – 8,27 | `shots/s02.md` (avec entrées et sorties, caméra, surfaces) | `s02_pit.py`, `s02_corner.py` | **PASS** (0 partout) | v2, par couches, 21 min 54 s | « presque exactement ce que je voulais ». 4 corrections + 2 manques ouverts |
| 3 à 15 | 8,27 – 51,5 | NON FAIT | NON FAIT | — | — | — |
| Voix, son, sous-titres, montage, rendu GPU final | — | NON FAIT | — | — | — | Plafond GPU non fixé |

## 3. Tests (dernière exécution : 19/11)

- `tools/tests/test_rc.py` : **27/27 PASS**.
- `tools/tests/test_pod_guard.py` : **13/13 PASS**.
- `tools/tests/test_plan_check.py` : **PASS** (avec les contrôles STORY).
- `continuity.py` sur le plan 2 : **PASS**.

## 4. GPU et coûts

- RunPod, 1 session (pod `572kwozsr0osyn`) : **1,06 $**, terminée et supprimée après récupération vérifiée.
- Solde au 19/11 : **3,58 $**, **0 pod**.
- Dépense résiduelle de 0,005 $/h sans pod : non expliquée (`OPEN_ISSUES.md`).
- Plafond de la mission maîtresse : 3 $. Aucun budget n'est encore fixé pour crashed_car.

## 5. Git

- Branche : `ccr-00f60cb8-lenpig`.
- Dernier commit de travail avant passation : `d07c50f`.
- Le commit de passation est indiqué dans `CHANGELOG.md`.

## 6. Prochaine action

`HANDOFF.md` §12 : **nouvelle vidéo avec la nouvelle méthode** (décision de CB du 19/11). Demander le sujet, puis script, voix, `plan.json` et `plan_check` PASS avant toute construction. crashed_car est en pause.
