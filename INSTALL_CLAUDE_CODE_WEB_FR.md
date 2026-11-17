# RicksClips Claude Code Web V1.3 — installation

## Contenu

Le Skill est placé dans `.claude/skills/ricks-clips/SKILL.md`, au format normal de Claude Code. Les 16 agents sont copiés dans `.claude/agents/`. Les règles, personnages, templates, motion library, outils, Asset Hub, exemples et références du paquet V1.2 sont conservés.

## Installation initiale

1. Décompresse l'archive et pousse tout le dossier sur GitHub. Ne supprime pas le dossier caché `.claude/`.
2. Ouvre `claude.ai/code`, connecte GitHub et sélectionne le dépôt.
3. Dans le sélecteur Cloud Environment, crée ou modifie un environnement `RicksClips Web`.
4. Choisis `Limited` comme accès réseau et garde `Allow package managers` activé. Ajoute les domaines de `CLOUD_NETWORK_DOMAINS.txt` dans Allowed domains.
5. Dans `Setup script`, téléverse `.claude/skills/ricks-clips/scripts/cloud_environment_setup.sh` puis enregistre.
6. Démarre une nouvelle session cloud. Le setup script installe Blender et FFmpeg ; le hook de `.claude/settings.json` installe les paquets Python et Node.
7. Invoque `/ricks-clips` et demande l'installation, le diagnostic et les tests offline.

La configuration du setup script est une opération unique dans les paramètres cloud. Un dépôt GitHub ne peut pas modifier lui-même ces paramètres enregistrés dans le compte Claude. Le fichier de setup est un petit script texte : dans la fenêtre Setup script, utilise **Choose file** pour sélectionner ce fichier (64 Ko maximum), puis sauvegarde.

## Clés API

Ajoute les clés dans **Network Secrets** de l'environnement cloud, jamais dans GitHub ni dans les variables ordinaires :
- Fish Audio : `api.fish.audio`, en-tête `Authorization`, préfixe `Bearer`.
- Sketchfab : `api.sketchfab.com`, en-tête `Authorization`, préfixe `Bearer`.

Poly Haven et ambientCG n'exigent pas de clé. Fab reste un processus d'acquisition manuel sous la responsabilité du propriétaire du compte. Le compte BlenderKit de Windows n'est pas transféré dans le cloud.

## Limite de rendu

La machine cloud n'est pas une station GPU garantie. Three.js est configuré pour un aperçu WebGL logiciel via `--software`, et Blender fonctionne en mode headless/CPU. Il faut mesurer un test court avant toute production longue. Un rendu final 1080x1920/30 FPS peut nécessiter le PC local ou un runner GPU.

## Prompt à donner à Claude

`/ricks-clips` puis :

> Installe et vérifie RicksClips dans cet environnement cloud. Lis CLOUD_MODE.md, exécute les scripts d'installation et de diagnostic, tous les smoke tests offline et corrige les problèmes détectés. Ne crée pas encore de film. Rends un rapport exact PASS/WARN/FAIL avec les versions installées.
