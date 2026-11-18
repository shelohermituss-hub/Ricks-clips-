# Checklist d'intégration obligatoire pour Claude

## A. Cartographie
- [ ] Identifier la racine exacte du skill utilisé par la session Web.
- [ ] Identifier le vrai point d'entrée de la commande skill.
- [ ] Cartographier les agents, règles, hooks, scripts et renderer réellement exécutés.
- [ ] Identifier les données film.json / shot plan / manifests réellement utilisées.
- [ ] Identifier où sont sauvegardés les épisodes et les assets persistants.

## B. Contrôleur de production
- [ ] Ajouter un coordinateur / showrunner qui lit ces règles au début de chaque film.
- [ ] Faire en sorte que les agents spécialisés reçoivent les exigences correspondant à leur domaine.
- [ ] Ajouter des gates entre préproduction, assets, scènes, animation, VFX, preview et rendu final.
- [ ] Faire remonter au coordinateur les limites, conflits et besoins d'approbation.

## C. Environnements et assets
- [ ] Ajouter un inventaire automatique des assets par plan et par lieu.
- [ ] Détecter les primitives/proxies dans les assets HERO.
- [ ] Connecter le registre d'assets à l'Asset Hub et au renderer.
- [ ] Ajouter un test de présence des textures et dépendances.
- [ ] Ajouter une procédure de création Blender si recherche infructueuse.
- [ ] Vérifier dans le renderer réel que l'asset est détaillé et chargé.

## D. Actions et effets
- [ ] Définir le contrat action → animation → interaction → VFX → état persistant → son.
- [ ] Ajouter une vérification de couverture des événements importants.
- [ ] Contrôler que les effets sont effectivement présents dans les frames rendues.
- [ ] Ajouter des tests de continuité temporelle entre frames.

## E. Revue et autocorrection
- [ ] Générer contact sheets et extraits continus automatiquement.
- [ ] Inspecter les actions importantes, pas uniquement une frame par plan.
- [ ] Produire défauts timecodés avec gravité et cause racine.
- [ ] Corriger les problèmes sûrs automatiquement.
- [ ] Re-rendre et comparer avant/après.
- [ ] Enregistrer seulement les leçons validées.

## F. Mémoire
- [ ] Lire les leçons globales à chaque nouveau film.
- [ ] Créer une mémoire locale par épisode.
- [ ] Ajouter les tests de non-régression pour les erreurs déjà rencontrées.
- [ ] Versionner l'historique des changements.

## G. Vérification réelle
- [ ] Exécuter les tests statiques.
- [ ] Exécuter les tests unitaires et smoke tests.
- [ ] Exécuter un test de chargement d'un asset externe autorisé.
- [ ] Produire un plan test avec asset détaillé, animation, effet et interaction.
- [ ] Inspecter le rendu visuellement.
- [ ] Fournir un diff et un rapport PASS/WARN/FAIL/NOT_RUN.
