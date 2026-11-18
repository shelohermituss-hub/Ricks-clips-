# Pipeline des assets

## Catégories
- HERO : sujet principal ou élément narratif visible en gros plan.
- SECONDARY : accessoires visibles dans les plans moyens.
- BACKGROUND : éléments distants qui construisent la profondeur.
- PROCEDURAL : éléments générés par le renderer ou Blender.

## Ordre de recherche
1. Asset existant déjà dans l'épisode.
2. Bibliothèque locale RicksClips et registre global.
3. BlenderKit si Blender et compte sont disponibles.
4. Sketchfab si le modèle est téléchargeable et licence compatible.
5. Poly Haven et ambientCG pour matériaux, textures, HDRI et modèles disponibles.
6. Fab via le flux d'acquisition autorisé par le compte.
7. Autres sources autorisées déjà intégrées.
8. Création Blender sur mesure si aucun asset approprié n'est trouvé.

## Critères de qualité
- Correspondance du sujet et de l'époque.
- Silhouette et proportions crédibles.
- Géométrie suffisante à la distance caméra.
- UV propres et matériaux assignés.
- Textures manquantes identifiées, sans aplats artificiels.
- Échelle, pivot et orientation validés.
- Pas de dépendance externe manquante.
- Test dans le vrai renderer et inspection visuelle.

## Modèles procéduraux
La modélisation procédurale est permise, mais le résultat doit être une vraie géométrie détaillée avec variation et matériaux. Elle ne doit pas masquer une absence d'asset par des primitives basiques.

## Sécurité juridique et secrets
- Vérifier la licence exacte et les restrictions d'usage.
- Ne pas contourner login, paywall ou accès non autorisé.
- Pas d'achat sans accord.
- Ne jamais inscrire tokens ou clés API dans les fichiers du film, Git, logs ou manifests.
- Conserver créateur, fournisseur, identifiant, URL, licence, date et hash.

## Contrôle d'intégration
Après import, faire un test isolé : ouverture, textures, matériau, normal, échelle, axes, ombres et rendu dans le renderer du film. Un téléchargement réussi n'est pas la preuve d'un asset exploitable.
