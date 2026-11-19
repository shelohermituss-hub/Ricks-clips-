# Faire une nouvelle vidéo, avec ou sans vidéo de référence

Méthode décidée avec CB le 19/11. Elle s'applique à toute nouvelle vidéo.

## L'ordre de travail

1. **Histoire, script et voix.** Débit de 3,3 à 3,6 mots/s, sans trou ; les mots clés sont repérés.
2. **Plan de production complet** : `plan/plan.json` et `plan/PLAN.md`, à partir de `templates/production_plan/`.
   - Il couvre tout : besoins et sources, lieux, textures, lumière, ombres, objets et leurs états, personnages, actions, micro-animations, **réactions**, **conséquences**, entrées et sorties, caméra, effets, son, couches de rendu, leçons à appliquer, risques.
   - Chaque action est rapprochée du catalogue `library/reactions/reactions.json`.
   - Sans vidéo de référence, la référence est `references/STYLE_BIBLE_FR.md`.
3. **`python3 tools/plan_check.py plan/plan.json`** doit indiquer **PLAN PASS**. Tant qu'il y a un FAIL, rien n'est construit.
4. **Téléchargement de tout ce qui manque, en une fois** : modèles, textures, HDRI, via `tools/asset_hub.py` et `rc.fetch` (gardés en cache).
5. **Construction plan par plan** : un script Blender par plan (`demos/<vidéo>/shots/sNN_*.py`), avec les dessins des personnages produits par `tools/card_service.py`, qui mesure aussi la tête, les pieds et les mains.
6. **Contrôle de continuité automatique** (`continuity.py`) : aucune apparition, téléportation, rétrécissement, saut de pose ni arrêt caméra.
7. **Images clés**, environ 8, vérifiées à l'œil avant le rendu complet.
8. **Rendu par couches** (`shots/render_layers.sh`), qui refuse de rendre si le contrôle échoue. Ensuite, seules les images corrigées sont refaites (`--patch`).
9. **Son et montage** : ambiance, musique, un bruitage par action et par réaction, −14 LUFS.

## Appliquer d'office ce que CB a déjà corrigé

Avant d'écrire un plan, relire `docs/CORRECTIONS_CB_FR.md`. Le plan déclare, pour chaque lieu, un bloc `look` (ciel HDRI visible, d'où vient le soleil, ombre portée du héros, lumière de débouchage, faisceaux, usure de la route, sillons des champs, clôture réelle qui projette une ombre, hauteur de l'herbe et deux côtés identiques) et un bloc `grade` (étalonnage mesuré par `tools/grade_match.py`). `plan_check` refuse un plan qui n'en a pas (contrôles LOOK). Le décor se construit avec `blender/rc/look.py` : ces réglages sont les valeurs par défaut, pas des corrections après coup.

## S'améliorer en construisant

Chaque problème rencontré, qu'il soit signalé par CB, par un contrôle ou vu en regardant les images, suit 4 étapes dans la même séance :

1. il est corrigé ;
2. il est documenté : leçon dans `memory/lessons_learned.json` et `LESSONS.md` ;
3. il est rendu impossible la fois suivante, de préférence dans cet ordre : un contrôle automatique, une recette du catalogue, une fonction du code de construction, une ligne du modèle de plan ou de la bible de style ;
4. il est commité.

`plan_check.py` rappelle ensuite à chaque nouveau plan les leçons qui s'appliquent : la correction vaut pour toutes les vidéos suivantes.

Exemples déjà en place :

| Problème | Solution permanente |
|---|---|
| Personnage ou casque qui apparaît d'un coup | `continuity.py` (POP), plus la section « Entrées / sorties » obligatoire dans le plan |
| Pilote téléporté | `continuity.py` (TELEPORT) |
| Bras qui sautent d'une pose à l'autre | `card_anchors.py` (POSE_POP), et la règle : une seule vue par personnage |
| Caméra statique | `continuity.py` (HOLD), `street.handheld()` et `plan_check.py` (CAMERA) |
| Sol gris plat | `street.pbr()`, scans CC0 ; `plan_check.py` refuse une couleur plate |
| Peinture sans profondeur | vernis, plus `street.hdri_reflections()` |
| Action sans conséquence | `library/reactions/reactions.json` et `plan_check.py` (ACTIONS) |
| Route plate, champs plats, clôture sans ombre, herbe d'un seul côté | `blender/rc/look.py`, `plan_check.py` (LOOK), `docs/CORRECTIONS_CB_FR.md` |
| Lumière plate, tronc noir, pas de rayons de soleil, étalonnage à l'œil | ciel HDRI, soleil placé, débouchage, faisceaux (`rc.look`), `tools/grade_match.py` |
| Ciel du décor coupé au loin | `continuity.py` (CLIP) |
| Aperçu CPU trop long | `preview.sh` (une couche, 4 échantillons), GPU pour les vrais rendus |

## Ajouter une vidéo de référence à la base de style

1. Mesures : `tools/reference_compare.py` (luminance, saturation, mouvement, netteté), découpage plan par plan, transcription mot à mot, loudness.
2. Analyse dans `references/<nom>/ANALYSE_FR.md`, sur le modèle de `references/crashed_car/`.
3. Ajout d'une ligne au tableau §9 de `STYLE_BIBLE_FR.md`. Ce qui est vrai dans **toutes** les vidéos devient une règle commune ; le reste devient une variante.
4. Les nouveaux types d'actions observés deviennent des recettes dans `reactions.json`.
