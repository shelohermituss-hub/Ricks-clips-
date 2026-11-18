# Direction artistique — environnements riches et détaillés

## Objectif
Atteindre le niveau de finition, de densité et de profondeur de la référence de la forteresse, tout en respectant l'histoire et la direction artistique du film courant.

## Règle de densité
Chaque lieu comporte au minimum une lecture claire en trois plans :
- premier plan : éléments proches, silhouettes et détails qui donnent de la profondeur ;
- plan moyen : sujets d'action, architecture et accessoires narratifs ;
- arrière-plan : structures, paysage, végétation, ciel, atmosphère et profondeur.

Ne pas remplir chaque zone au hasard. La densité doit guider le regard et soutenir l'action. Les zones de repos visuel sont intentionnelles.

## Architecture et géométrie
- Silhouette crédible, volumes secondaires, moulures, joints, encadrements, poutres, supports et raccords.
- Variations de dimensions et d'orientation pour éviter l'aspect cloné.
- Géométrie de proximité sur les objets héro ; détails moins coûteux sur l'arrière-plan.
- Pas de cubes ou cylindres recolorés comme rendu définitif d'un asset héro.

## Sols et paysages
- Relief et transitions de terrain.
- Traces, ornières, empreintes, fissures, herbe, gravier, boue, neige ou débris selon le contexte.
- Variation de roughness et normal maps.
- Traces persistantes après le passage des personnages ou véhicules quand la scène l'exige.

## Matériaux
- Utiliser des cartes PBR disponibles : base color/albedo, normal, roughness, metallic, ambient occlusion et height/displacement si utile.
- Éviter les surfaces uniformes et les répétitions évidentes.
- Ajouter variation contrôlée, usure, poussière, humidité et salissures cohérentes avec le lieu.
- Vérifier l'échelle UV et la résolution des textures à la distance caméra réelle.

## Palette et éclairage
- Créer une palette par lieu et une palette globale de film.
- Sources lumineuses motivées par la scène.
- Séparer sujet et arrière-plan sans halos artificiels excessifs.
- Garder les détails dans les ombres nocturnes.
- Éviter clipping des hautes lumières et aplats noirs.
- Color grading appliqué à tous les plans, pas seulement au viewport.

## Objets héro
Un objet héro doit être inspecté en plan rapproché avant d'être accepté. Pour les véhicules, bâtiments, équipements, meubles ou objets narratifs : silhouette, pièces extérieures visibles, matériaux, texture, échelle, orientation, contact au sol, ombres et cohérence temporelle.

## Score d'acceptation
Noter chaque lieu de 0 à 4 pour : géométrie, variété, matériaux, profondeur, éclairage, atmosphère, cohérence historique/artistique et animation environnementale.
- 0 : absent / cassé
- 1 : blockout / primitive
- 2 : lisible mais pauvre
- 3 : détaillé et cohérent
- 4 : niveau de finition de référence

Un lieu principal ne passe pas en rendu final si l'un des critères essentiels (géométrie, matériaux, profondeur, éclairage, cohérence) est inférieur à 3, sauf dérogation expliquée.
