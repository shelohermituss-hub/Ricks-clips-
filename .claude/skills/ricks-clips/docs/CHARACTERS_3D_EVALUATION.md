# Évaluation — personnages 3D riggés face aux cartes 2D (livrable 5, volet « hybride »)

**Décision demandée par la mission maîtresse :** évaluer, sans remplacer le système 2D validé.
**Recommandation :** garder les cartes 2D pour tous les personnages qui jouent. Réserver d'éventuels personnages 3D à des usages précis, après un essai mesuré (section 5). Aucun essai 3D n'a été fait dans cette mission : les chiffres 3D ci-dessous sont **NON MESURÉS**.

## 1. Le système actuel (mesuré sur la démo cour de ferme)

| Point | Mesure ou fait |
|---|---|
| Distribution | 150 personnages vectoriels verrouillés (gabarit v12), style Ricks Clips validé par CB |
| Production des dessins | `tools/card_service.py` : 438 dessins pour le fermier et 435 pour le forgeron (450 images), environ 5 min CPU pour les deux, cache par contenu |
| Intégration dans Blender | cartes en séquence d'images, collées au sol par lancer de rayon, ombre portée, caméra active suivie plan par plan |
| Contact au sol | gate de phase 4 : pieds à 2 cm au plus du sol (`qa.character_contact`) |
| Hybride 2D + 3D | accessoire 3D tenu en main : positions des mains exportées dans `index.json`, l'objet suit la main (la hache du forgeron dans la démo) |

Points forts :
- le style dessiné, cœur de l'identité visuelle ;
- les expressions et poses de la bibliothèque de mouvements ;
- un coût faible ;
- un rendu indépendant de l'ordre des images.

Limites connues :
- la carte est plane : un plan de caméra très latéral (plus de 60° par rapport à la carte) montre son épaisseur nulle ;
- les occlusions partielles (un personnage *dans* un véhicule, assis derrière une table) demandent un découpage de la carte ;
- pas de contact physique réel avec la simulation (pousser, être bousculé).

## 2. Ce qu'apporterait un personnage 3D riggé

| Besoin | 2D (cartes) | 3D riggé |
|---|---|---|
| Plan qui tourne autour du personnage | limité par l'angle de la carte | naturel |
| Personnage assis dans un véhicule, occlusions | découpage manuel | naturel |
| Interaction physique (bousculé, ramasse un objet lourd) | jouée et précalculée par l'animateur | possible par contraintes et IK |
| Foule lointaine (plus de 20 silhouettes) | une carte par personne, coût en dessins | instances d'un même modèle à poses variées |
| Style Ricks Clips (trait, expressions) | **natif** | à recréer (shader toon et contours) : risque élevé d'écart de style |
| Expressions faciales | bibliothèque complète | à construire : formes de bouche, yeux, sourcils |

## 3. Coûts et risques du 3D (estimations, non mesurées)

- **Assets** : un personnage riggé par rôle, aux proportions du gabarit v12. Sources possibles, toutes à vérifier une par une avant usage :
  - modèles CC0 avec armature ;
  - générateurs à licence de sortie libre ;
  - rig Rigify maison.

  La licence de chaque fichier doit être contrôlée : l'Asset Hub refuse déjà ce qui n'est pas clairement autorisé.
- **Animation** : les mouvements de la bibliothèque 2D (`templates/motion_styles/`) ne se transfèrent pas tels quels. Il faudrait recibler des cycles (marche, idle, gestes) ou les animer à la main.
- **Rendu** : la peau, les vêtements et les cheveux ajoutent des matières et du temps GPU. Aucun chiffre ne vaut avant un essai.
- **Cohérence** : mélanger 2D et 3D dans un même plan est le risque principal pour le style. CB a validé le style 2D, pas un style 3D.

## 4. Quand le 3D vaudrait la peine

1. **Silhouettes lointaines et foules** : un même modèle simple, sans visage, en instances. Le risque de style est faible car les personnages sont petits à l'écran.
2. **Plans orbitaux serrés** autour d'un personnage, quand l'histoire l'exige vraiment.
3. **Interactions physiques** où le personnage subit la simulation.

Dans tous les autres cas, la carte 2D reste meilleure, et de loin, en rapport qualité/coût.

## 5. Essai proposé (non lancé, il demande l'accord de CB)

1. Un seul modèle de silhouette sous licence vérifiée, rig simple, cycle de marche.
2. Dix instances en fond de la cour de ferme, à plus de 15 m de la caméra du plan 1.
3. Mesures :
   - temps de rendu par image avec et sans foule ;
   - avis de CB sur le mélange de styles, avec planche côte à côte ;
   - gate de contact au sol.
4. Décision PASS ou FAIL sur ces mesures, puis seulement intégration éventuelle dans `rc/characters.py` (`place_rigged`, même interface que `place_cards`).
