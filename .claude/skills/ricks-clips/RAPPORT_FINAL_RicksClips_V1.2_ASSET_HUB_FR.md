# Rapport de livraison — RicksClips V1.2 Asset Intelligence Hub

**Date : 16 novembre 2026**  
**Base :** RicksClips_Skill_V1.1 fusionné et amélioré précédemment  
**Livraison :** intégration des quatre fournisseurs demandés, conservation des améliorations de maintenance/environnement/animation/qualité, et connexion de la bibliothèque d'assets au renderer Three.js.

## 1. Résumé

Le skill possède désormais une couche commune de recherche, d'acquisition autorisée, de validation, de catalogage, de staging et d'attribution des assets 3D. Il peut interroger Sketchfab, Poly Haven et ambientCG via leurs interfaces publiques/documentées, et Fab par un transfert vers la recherche officielle puis import local du fichier acquis par le propriétaire du compte. Le pont BlenderKit préexistant est conservé.

Le système ne télécharge pas indistinctement tout ce qu'il trouve : il vérifie l'accès et les licences, conserve la provenance, bloque les archives présentant des chemins dangereux, impose des limites de taille et privilégie les modèles GLB/glTF directement utilisables par le renderer.

**Important :** l'intégration logicielle est livrée et testée hors ligne. Aucun modèle réel n'a été téléchargé pendant la préparation de cette archive : les appels réseau sortants ne sont pas disponibles dans cet environnement, et aucun jeton Sketchfab ni accès à un compte Fab n'a été fourni. Les connecteurs sont prêts à être utilisés depuis la station Windows après installation et authentification nécessaires.

## 2. Fournisseurs intégrés

### Sketchfab

- Recherche via la Data API publique.
- Retour de l'UID, nom, créateur, licence, indication de téléchargement, aperçu, nombre de faces et source.
- Téléchargement déclenché par l'endpoint officiel `/v3/models/{UID}/download`, avec le jeton OAuth personnel de l'utilisateur.
- Refus du téléchargement si le modèle n'est pas déclaré téléchargeable par son auteur.
- Liste d'autorisation automatique limitée à CC0 et CC-BY ; les licences inconnues, NC, ND et autres cas non autorisés ne passent pas par le téléchargement automatique.
- Extraction de l'archive glTF dans la bibliothèque locale, avec attribution et manifeste.

Variable d'environnement : `SKETCHFAB_OAUTH_TOKEN`. Le jeton doit être défini dans la session PowerShell de l'utilisateur, jamais dans le skill, les fichiers du film ou Git.

### Fab

- Connecteur de recherche qui génère une URL de recherche officielle Fab correspondant à l'histoire.
- Pas de faux endpoint de téléchargement ni d'automatisation de compte, de panier ou de paiement.
- Acquisition effectuée par le propriétaire dans Fab/Fab Launcher, puis import du fichier local avec `import-local fab`.
- L'import demande une note de preuve d'acquisition et enregistre l'éditeur, l'URL du listing, la licence et les informations fournies. Cette note est une trace de provenance, pas une vérification juridique automatique.

### Poly Haven

- Recherche via l'API publique `/assets`.
- Téléchargement via `/files/{asset_id}`.
- Classification des ressources : HDRI, texture et modèle.
- Pour les matériaux, conservation de toutes les cartes PBR disponibles à la résolution choisie au lieu de télécharger une seule carte.
- Contrôle MD5 lorsqu'il est fourni par l'API, hash SHA-256 local, manifeste et mention `Powered by Poly Haven` dans les crédits du film lorsque l'API live est utilisée.
- User-Agent propre à RicksClips, personnalisable avec `RICKCLIPS_ASSET_HUB_USER_AGENT`.

### ambientCG

- Utilisation de l'API v3, pas de l'ancienne API v2.
- Recherche par mots-clés et type, avec métadonnées des téléchargements demandées.
- Téléchargement des packs et extraction sécurisée.
- Conservation du nom/ID original (sensible à la casse), des URLs, de la licence CC0 et des hashes.
- Les erreurs ou indisponibilités du fournisseur sont remontées sans faire échouer les recherches des autres fournisseurs.

### BlenderKit conservé

Le pont BlenderKit existant n'a pas été remplacé. La recherche continue à utiliser l'installation Blender et l'extension connectée au compte de l'utilisateur. Les fichiers acquis par cette voie peuvent être normalisés dans le hub avec l'import local.

## 3. Nouveaux modules et fichiers

| Fichier | Rôle |
|---|---|
| `tools/asset_hub.py` | CLI unifiée : recherche, téléchargement, import local, validation, catalogue et staging |
| `tools/place_library.py` | Enregistrement, inventaire et staging de lieux réutilisables |
| `tools/build_asset_credits.py` | Construction de la feuille de crédits à partir des manifests des assets staged |
| `tools/test_asset_hub.py` | Tests unitaires et d'intégration simulant les réponses fournisseurs |
| `tools/test_asset_loader.mjs` | Tests hors ligne du chargeur Three.js et des cartes de matériaux |
| `templates/threejs_film/asset_loader.mjs` | Chargement des GLB/glTF et application ciblée des cartes PBR |
| `templates/place_library/PLACE_MANIFEST.schema.json` | Schéma pour les recettes de lieux et les assets/materials associés |
| `templates/place_library/abandoned_port.place.json` | Exemple de recette de lieu, avec asset ID factice à remplacer |
| `library/assets/catalog.json` | Catalogue local vide initialisé |
| `library/assets/README.md` | Règles de cache et de provenance |
| `library/places/README.md` | Organisation de la bibliothèque des lieux |
| `config/asset_hub.env.example` | Variables d'environnement facultatives, sans aucun secret réel |
| `docs/ASSET_HUB.md` | Guide d'installation, fournisseurs, licences, commandes et limitations |

Fichiers centraux mis à jour : `SKILL.md`, `CB_RULES.md`, les tranches `rules/dept/`, `README.md`, `START_HERE.md`, `WORKFLOW.md`, `INSTALL.md`, `CHANGELOG.md`, `templates/threejs_film/film.js`, `templates/threejs_film/film_page.html` et `templates/threejs_film/package.json`.

## 4. Intégration à la production de films

### Bibliothèque locale d'assets

Les ressources ingérées sont rangées dans :

`library/assets/<provider>/<asset_id>/`

Chaque ressource acquise reçoit un `ASSET_MANIFEST.json` avec fournisseur, ID, nom, créateur, licence, URL source, date, taille et hash SHA-256. Le catalogue central est `library/assets/catalog.json`.

### Bibliothèque des lieux

Une recette de lieu peut définir :

- style, palette, moment de la journée, météo et atmosphère ;
- ancres géographiques et stations de caméra ;
- modèles, position, rotation, échelle et ombres ;
- matériaux PBR, cartes, répétition et noms exacts des matériaux à modifier.

La même recette peut être réutilisée dans plusieurs épisodes lorsque la géographie et l'histoire le justifient. Elle ne force pas une histoire à utiliser un décor sans rapport.

### Renderer Three.js

Le renderer reçoit maintenant les tableaux `places.<place>.assets` et `places.<place>.materials` de `film.json`.

- Les modèles GLB/glTF sont chargés localement avec `GLTFLoader`.
- Les coordonnées de plan `[x, y-forward, z-up]` sont converties vers le repère Three.js.
- Les cartes couleur, normales, rugosité, métal, occlusion et déplacement sont chargées séparément.
- Les cartes ne sont appliquées qu'aux matériaux explicitement nommés dans `target_materials`. Le chargeur refuse de remplacer les matériaux de toute la scène si cette liste manque.
- Les assets optionnels en échec apparaissent dans le rapport; un asset déclaré obligatoire fait échouer la configuration du lieu.
- Les matériaux ou modèles qui ne sont pas au format compatible doivent être convertis avant le rendu. Le chargeur navigateur prend en charge GLB/glTF 2.0 pour les modèles et PNG/JPG/JPEG/WebP pour les cartes PBR listées par la bibliothèque.

### Crédits

`tools/build_asset_credits.py` construit `ASSET_CREDITS.md` pour chaque épisode à partir des manifests staged. La feuille est un registre de provenance : les crédits exigés par un fournisseur doivent également être affichés dans les crédits de fin, le lecteur, la page ou la description de publication appropriée.

## 5. Exemples d'utilisation

Recherche multi-fournisseurs :

```powershell
python tools/asset_hub.py search all "weathered medieval harbour warehouse" --kind model --limit 12
```

Recherche puis téléchargement Poly Haven :

```powershell
python tools/asset_hub.py search polyhaven "stone wall" --kind material
python tools/asset_hub.py download polyhaven <ASSET_ID> --resolution 2k
```

Recherche puis téléchargement ambientCG :

```powershell
python tools/asset_hub.py search ambientcg "weathered stone" --kind material
python tools/asset_hub.py download ambientcg <ASSET_ID> --resolution 2K --format auto
```

Sketchfab :

```powershell
$env:SKETCHFAB_OAUTH_TOKEN = "<YOUR_OWN_OAUTH_ACCESS_TOKEN>"
python tools/asset_hub.py search sketchfab "stone lighthouse" --kind model
python tools/asset_hub.py download sketchfab <MODEL_UID>
Remove-Item Env:SKETCHFAB_OAUTH_TOKEN
```

Fab : ouvrir le lien du résultat, vérifier la licence et les formats, acquérir le produit dans son compte puis l'importer :

```powershell
python tools/asset_hub.py import-local fab "C:\Assets\my_environment_pack.zip" --name "my_environment_pack" --license "Fab Standard License" --source-url "https://www.fab.com/listings/<LISTING_ID>" --creator "<PUBLISHER>" --evidence "Produit acquis et visible dans ma bibliothèque Fab"
```

Validation et credits :

```powershell
python tools/asset_hub.py validate library/assets/<provider>/<asset_id>
python tools/asset_hub.py stage <provider> <asset_id> --episode episodes/<episode>
python tools/build_asset_credits.py episodes/<episode>
```

## 6. Licences, sécurité et qualité

- Les téléchargements Sketchfab automatiques sont limités à CC0/CC-BY et à des modèles dont le téléchargement est autorisé par le titulaire.
- Poly Haven et ambientCG sont traités comme CC0 selon leurs conditions publiées ; les crédits liés à l'utilisation de l'API Poly Haven sont ajoutés.
- Fab reste lié à la licence exacte du listing et aux droits d'acquisition du propriétaire du compte.
- Les identifiants de compte et jetons ne sont pas inclus dans le ZIP.
- Tous les téléchargements sont HTTPS-only, avec limites de taille et empreintes ; les extractions rejettent les chemins absolus, les chemins `..`, les chemins de lecteur Windows et les liens symboliques.
- Le système refuse les catégories d'assets hors de son périmètre de décors et d'accessoires ordinaires.
- Aucun personnage tiers ne remplace les marionnettes vectorielles approuvées de RicksClips.
- Le skill conserve les assets bruts dans le cache local et copie dans l'épisode seulement les fichiers nécessaires au rendu. Ne pas redistribuer isolément un pack brut sous licence.

## 7. Vérifications exécutées

Résultats dans l'environnement de préparation :

| Vérification | Résultat |
|---|---:|
| Syntaxe Python (`.py`) | 87 fichiers, 0 erreur |
| Syntaxe JavaScript/MJS (hors dépendances/vendor) | 202 fichiers, 0 erreur |
| Parsing JSON | 63 fichiers, 0 erreur |
| Tests Asset Hub | 16 réussis |
| Régression animation secondaire/clignement | PASS |
| Smoke test des fonctions du kit d'environnement 3D | PASS |
| Smoke test du chargeur Three.js / PBR | PASS |
| Miroir `CB_RULES.md` maître/copie cloud | Identique |

Le test Asset Hub vérifie notamment la recherche ambientCG, la normalisation Poly Haven, les licences Sketchfab, la redirection d'acquisition Fab, l'absence d'import Fab sans note de preuve, le refus de chemins ZIP dangereux, le choix de GLB pour le runtime, la création des crédits et le staging des matériaux par nom de matériau exact.

## 8. Préparation nécessaire sur la machine Windows

1. Extraire le ZIP complet.
2. Ouvrir PowerShell à la racine du skill.
3. Installer la dépendance GLTFLoader épinglée :

```powershell
cd templates/threejs_film
npm install
```

4. Revenir à la racine du skill et installer / rafraîchir Claude en suivant `INSTALL.md`.
5. Lancer les commandes de recherche de test du guide `docs/ASSET_HUB.md`.
6. Pour Sketchfab, définir son propre OAuth token seulement pendant la session de téléchargement. Pour Fab, télécharger les produits via son propre compte puis utiliser `import-local`.

## 9. Limites restantes — indiquées explicitement

- **Aucun téléchargement réel de modèle n'a été fait pendant le packaging.** Les API sont testées par réponses simulées. Les recherches live Poly Haven/ambientCG/Sketchfab doivent être confirmées sur le Windows connecté à Internet.
- **Sketchfab ne téléchargera rien sans le jeton OAuth personnel** et uniquement pour les modèles marqués téléchargeables avec licence admise.
- **Fab n'est pas un téléchargement automatisé** : acquisition via le compte utilisateur puis import local, conformément au fonctionnement documenté du service.
- **BlenderKit requiert Blender et son extension connectée** sur la machine utilisateur.
- **`npm install` est nécessaire une fois** dans `templates/threejs_film`. Le bac à sable n'avait pas de sortie DNS et n'a pas pu télécharger le paquet npm, donc le `package-lock.json` n'a pas pu être mis à jour localement. Utiliser `npm install`, pas `npm ci` sur l'ancien lockfile.
- **Aucun rendu final Windows/Blender/WebGL/GPU n'a été exécuté ici.** Les tests de chargeur utilisent un objet Three.js simulé pour vérifier les textures et les gardes de sécurité; la compatibilité visuelle finale reste à valider sur la station de production.
- Le lieu d'exemple `abandoned_port.place.json` contient volontairement un ID d'asset factice. Il sert de modèle de structure et n'est pas un décor déjà téléchargé.

## 10. Références fournisseurs

- Sketchfab : Data API et Download API. Le téléchargement requiert l'authentification du compte, une demande officielle de téléchargement, puis une archive glTF temporaire ; les crédits auteur/source/licence doivent suivre l'asset.
- Fab : acquisition via le site ou Fab Launcher, avec export depuis la bibliothèque Fab et licence propre au listing.
- Poly Haven : API publique gratuite, assets CC0, User-Agent unique et mention claire de l'origine Poly Haven lorsqu'on s'appuie sur l'API live.
- ambientCG : API v3 GET de recherche/métadonnées/téléchargement ; les assets publiés sont CC0.
