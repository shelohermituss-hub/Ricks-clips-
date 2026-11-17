# Rapport de livraison — RicksClips Claude Code Web V1.3

## Résultat

Une édition Claude Code Web du projet RicksClips V1.2 est assemblée sous forme de dépôt GitHub prêt à pousser. Le Skill est installé à l'emplacement standard `.claude/skills/ricks-clips/SKILL.md` et porte la commande `/ricks-clips`.

## Contenu livré

- Le Skill et les règles/ressources de production du paquet RicksClips V1.2 d'origine.
- 16 agents de projet dans `.claude/agents/`.
- Un script Cloud Environment Setup pour installer Blender CLI, FFmpeg et les bibliothèques système manquantes avant le démarrage de Claude.
- Un hook `SessionStart` dans `.claude/settings.json` qui installe un environnement Python isolé et les dépendances npm/Three.js/Playwright, uniquement dans les sessions cloud.
- Un Cloud Doctor qui vérifie Python, Node, npm, Blender, FFmpeg, Chrome, les imports Python, les dépendances JavaScript, l'exécution Blender en arrière-plan, et la disponibilité GPU.
- Un smoke test Chrome/Playwright/WebGL.
- Une configuration de rendu logiciel pour les aperçus cloud, sans prétendre qu'un GPU est présent.
- Une liste de domaines réseau et une procédure Network Secrets pour Sketchfab et Fish Audio.
- Un guide d'installation en français, un guide de fonctionnement cloud et un manifeste SHA-256.

## Vérifications exécutées dans l'environnement de préparation

| Vérification | Résultat |
|---|---|
| 16 tests Python Asset Hub | PASS — 16/16 |
| Motion QA | PASS — 42/42 modules, 195/195 références, 330 styles, 2 640 poses échantillonnées |
| Look3D API smoke test | PASS |
| Three.js Asset Loader tests | PASS |
| Syntaxe Bash des scripts cloud | PASS |
| Syntaxe Node des renderers et du smoke test navigateur | PASS |
| Compilation Python des fichiers modifiés | PASS |
| Validation JSON de `.claude/settings.json` | PASS |
| Intégrité de l'archive ZIP | PASS |

Le test Look3D a affiché un avertissement Node non bloquant (`MODULE_TYPELESS_PACKAGE_JSON`) sur un module existant ; le test s'est terminé avec PASS.

## Limites honnêtes

La machine Claude Code Web n'était pas disponible dans cet environnement de préparation. Par conséquent, l'installation réelle d'APT/Blender, le lancement de Chrome/WebGL dans la VM, l'accès réseau aux fournisseurs, le téléchargement de modèles et le rendu final n'ont pas été exécutés ici. Ils seront vérifiés par `scripts/cloud_doctor.sh` et `scripts/cloud_browser_smoke.mjs` dans la première session Claude Web.

La configuration Cloud Environment est liée au compte Claude et ne peut pas être créée par le dépôt GitHub ou par le Skill lui-même. Une seule configuration initiale est donc requise : sélectionner le Setup script, autoriser les domaines des fournisseurs et ajouter les Network Secrets. Ensuite, les dépendances du projet sont installées automatiquement par le hook de session (ou par la commande manuelle incluse pour les sessions où les hooks de dépôt ne sont pas chargés).

Les machines cloud Anthropic ont des ressources limitées et aucun GPU n'est garanti. Le paquet prépare des aperçus Three.js/WebGL logiciels et Blender headless/CPU ; un rendu long en 1080×1920 à 30 FPS doit être mesuré avant production et pourra nécessiter un GPU local ou un runner dédié.

## Installation rapide

1. Décompresser cette archive et pousser **tout le contenu**, y compris le dossier caché `.claude/`, dans un dépôt GitHub.
2. Ouvrir `claude.ai/code`, sélectionner le dépôt et un Cloud Environment.
3. Dans les paramètres de l'environnement, utiliser `Choose file` pour choisir `.claude/skills/ricks-clips/scripts/cloud_environment_setup.sh` comme Setup script. Le fichier est court et compatible avec la limite de taille indiquée par Claude.
4. Régler le réseau sur `Limited`, garder `Allow package managers` activé, puis ajouter les domaines de `.claude/skills/ricks-clips/CLOUD_NETWORK_DOMAINS.txt`.
5. Ajouter les Network Secrets Fish Audio et Sketchfab selon `CLOUD_MODE.md`.
6. Démarrer une nouvelle session, invoquer `/ricks-clips` et demander :

   > Installe et vérifie RicksClips dans cet environnement cloud. Lis CLOUD_MODE.md, exécute scripts/cloud_session_start.sh et scripts/cloud_doctor.sh, lance tous les smoke tests hors ligne et corrige ce qui peut l'être sans contourner les licences. Ne crée pas encore de film. Donne un rapport exact PASS/WARN/FAIL.

Le dossier `INSTALL_CLAUDE_CODE_WEB_FR.md` dans la racine donne le détail étape par étape.

## Références officielles Claude Code

- https://code.claude.com/docs/en/cloud-environments — environnements cloud, scripts de setup, variables, Network Secrets, hooks et accès réseau.
- https://code.claude.com/docs/en/claude-code-on-the-web — sessions Claude Code Web.
