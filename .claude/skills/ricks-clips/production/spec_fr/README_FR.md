# RicksClips — Production Intelligence Upgrade v1.0

## Objectif

Cette extension décrit le comportement attendu d'un RicksClips qui agit comme un **directeur de production technique supervisé par Claude** : il planifie, construit, vérifie, corrige, documente les leçons utiles et réutilise les solutions validées dans les films suivants.

Elle vise particulièrement :
- des environnements riches, détaillés et cohérents avec la vidéo de référence de la forteresse ;
- des assets 3D réellement détaillés pour les objets importants, au lieu de simples primitives colorées ;
- des actions qui déclenchent des animations, des effets visuels et des conséquences visibles ;
- des micro-animations, interactions, matériaux, éclairages, atmosphère et color grading ;
- une mémoire de production persistante qui évite de répéter les erreurs déjà corrigées.

## Ce que contient l'extension

- `MASTER_PROMPT_CLAUDE_FR.md` : prompt complet à donner à Claude Code Web.
- `docs/PRODUCTION_PIPELINE.md` : pipeline et portes de contrôle.
- `docs/ENVIRONMENT_ART_DIRECTION.md` : standard de richesse et de détail des décors.
- `docs/ASSET_PIPELINE.md` : recherche, création, import, licences et validation des assets.
- `docs/ANIMATION_VFX_INTERACTION.md` : règles d'animation, d'interaction et d'effets visuels.
- `docs/SELF_IMPROVEMENT_MEMORY.md` : mémoire durable, retours d'expérience, tests de non-régression et promotion des corrections.
- `docs/QUALITY_GATES.md` : conditions de réussite avant de déclarer un film final.
- `config/production_profile.json` : profil de production réglable.
- `config/action_effect_matrix.json` : exemples de liens entre action, mouvement, effet, son et conséquence persistante.
- `config/quality_gates.json` : portes de contrôle structurées.
- `memory/lessons_learned.json` : registre initial vide des leçons validées.
- `memory/asset_registry.json` : registre initial des assets utilisés.
- `memory/shot_review_template.md` : modèle de revue plan par plan.
- `schemas/lesson.schema.json` et `schemas/asset.schema.json` : structures de mémoire et d'inventaire.
- `INTEGRATION_CHECKLIST.md` : liste de tâches que Claude doit exécuter pour intégrer réellement les règles dans le skill.

## Installation / utilisation

1. Décompresser ce paquet dans le dépôt RicksClips utilisé par Claude Code Web, idéalement à la racine ou dans un dossier temporaire d'intégration.
2. Ouvrir et envoyer `MASTER_PROMPT_CLAUDE_FR.md` à Claude Code Web.
3. Demander à Claude d'inspecter le dépôt réel, de lire les fichiers existants du skill, puis d'intégrer les règles dans les bons agents, règles, templates, outils et hooks. Il ne doit pas simplement copier ces documents sans les connecter au pipeline.
4. Claude doit d'abord créer une branche ou un commit de sauvegarde, établir l'état initial et présenter un plan d'intégration. Il peut ensuite appliquer les changements réversibles, exécuter les tests et rendre un rapport.
5. Pour chaque nouveau film, le dossier de production doit conserver la mémoire locale du film et lire la mémoire globale validée.

## Important : ce paquet n'est pas une modification déjà fusionnée dans RicksClips

C'est un **paquet d'extension et une spécification d'intégration**. Il n'affirme pas avoir modifié ton skill installé. Claude doit l'intégrer dans la version réelle du dépôt, vérifier les points d'entrée exécutés par les agents et le renderer, puis produire un diff et des preuves de tests.

## Principe directeur

Aucun objet héro, décor principal, véhicule ou accessoire important ne doit rester une primitive provisoire dans le rendu final. Les primitives sont autorisées pour le blockout et les previews uniquement, sauf élément volontairement stylisé et validé par la direction artistique.

Tous les effets doivent rester des **effets cinématographiques visuels fictifs**. Les simulations de tirs, explosions et véhicules servent uniquement à l'image et ne doivent pas chercher à reproduire des mécanismes, performances, procédures ou tactiques réelles.
