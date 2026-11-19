# Ce que les corrections de CB ont appris — à appliquer d'office à toute nouvelle scène

CB, le 19/11 : « à chaque correction que je te donne tu dois les apprendre pour t'améliorer et ne pas reproduire la même mauvaise chose … mettre ta méthode à jour pour que naturellement tu puisses produire sans erreur et sans correction ».

Ce document est **la mémoire des corrections**. Toute scène, avec ou sans vidéo de référence, les applique **dès la première version**. Chaque ligne dit :
- ce que CB a corrigé ;
- la règle qui en découle ;
- **où elle est appliquée** : un contrôle qui refuse, un outil, un réglage par défaut du code ou une ligne du modèle de plan.

Une règle seulement écrite ne suffit pas.

Lire avec :
- `CB_RULES.md` §11h, qui fait foi ;
- `references/STYLE_BIBLE_FR.md`, le style ;
- `docs/PREPRODUCTION_FR.md`, l'ordre de travail ;
- `memory/LESSONS.md`, le détail de chaque leçon PI-xxx.

---

## 1. Surfaces : toujours de vraies textures, jamais une couleur plate

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| Sol du stand gris et plat (crashed_car, plan 2) | Sol, route, murs et grandes surfaces en **textures PBR scannées** CC0 (Poly Haven / ambientCG), jamais une couleur + bruit | `plan_check` PLACES (refuse une texture absente) ; `street.pbr`, `roadside.tex` |
| « La route est trop plate … usure et marques de pneus » (crash_instinct, 19/11) | Asphalte scanné usé (`asphalt_02`) + **traces de roues** plus sombres dans chaque voie + **joints de goudron** ; jamais un asphalte uniforme | `roadside.road_wear()` ; `plan_check` LOOK (une route doit déclarer son usure) |
| Asphalte du virage trop sombre, trop de cailloux, sans traces de dérapage (crashed_car, plan 2) | Valeur de l'asphalte calée sur la référence, débris rares, **traces noires** là où une voiture a freiné ou dérapé | `plan_check` ACTIONS (recette `vehicle_brake_skid` : conséquence = traces) |
| « La terre derrière la clôture est plate … traces comme si un tracteur était passé » | Champs en **sillons scannés** (`farm_furrows`), relief marqué (normal ×2,2), sillons dans le sens du travail ; bandes alternées (chaume doré / terre labourée) | `roadside.fields()` ; `plan_check` LOOK (champs = texture de sillons) |
| « La clôture manque de réalisme et n'émet pas d'ombre » | Piquets en **bois brut scanné** (`rough_wood`), tous un peu différents (hauteur, inclinaison, rotation, coupe en biais), **fils qui pendent** entre les piquets, **piquets et fils projettent une ombre** ; clôture des **deux côtés** de la route | `roadside.fence()` ; `plan_check` LOOK |
| Peinture de voiture sans profondeur (crashed_car) | Peinture vernie, reflets d'un vrai ciel (HDRI) | `street.hdri_reflections`, ciel HDRI visible |
| « La voiture scintille … trop mate … blanc métallisé » (crash_instinct) | Ne **jamais** garder la texture de peinture d'un modèle importé (métal/relief qui scintillent) : peinture refaite, lisse, comme la référence ou comme CB le demande (ici blanc métallisé : métal 0,55, rugosité 0,28, vernis 0,6) ; **vitres claires**, jamais teintées | `s01_plant.car()` ; `plan_check` OBJECTS (un véhicule déclare sa peinture et ses vitres) |
| « Le tronc est tout sombre » ; arbre de bibliothèque irréaliste | Écorce scannée (`jolcham_oak_bark_01`) ; si aucun modèle ne ressemble, on **construit** l'objet (chêne : un tronc, branches maîtresses, ~95 paquets irréguliers de vraies feuilles 3D, 4 verts au soleil + 4 à l'ombre) | `sets/oak.py` |
| Marque réelle visible sur une voiture (F1 de crashed_car) | Aucune marque réelle : livrée repeinte, nos propres décalques | Règle « rien de générique » + vérification à l'œil |

## 2. Lumière : un vrai jeu de lumière cinématique, de jour comme de nuit

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| « Un vrai jeu de lumière cinématique … rayons de soleil … le soleil apparaît sur une partie et projette l'ombre de l'arbre » | Ciel = **HDRI réel visible**, tourné pour que son soleil coïncide avec la lampe soleil ; soleil **placé comme dans la référence** (crash_instinct : contre-jour arrière-gauche, 30° de haut) ; **ombres longues** des grands objets dans le cadre ; le soleil ou sa lueur visibles quand la caméra regarde vers lui | `roadside.sky_hdri()`, `sun()` ; `plan_check` LOOK (ciel HDRI, direction du soleil et ombre héros déclarées) |
| « Le tronc est tout sombre en plein jour » | **Lumière de débouchage** côté caméra (grande source douce invisible) : jamais de noir en plein jour | `roadside.bounce_fill()` ; `plan_check` LOOK (`fill`) |
| « Rayons de soleil » | Sous un arbre ou par une ouverture, au soleil : **faisceaux fins** attachés à l'objet d'où ils tombent, qui vont vers le sol (jamais à travers le ciel), plus une brume très légère | `roadside.light_shafts()`, `god_rays()` ; `plan_check` LOOK (avertit s'il manque des faisceaux sous un arbre de jour) |
| Brume trop forte qui délave l'image | Densité de brume très basse (0,0015) ; elle ne doit jamais faire baisser la saturation mesurée | `tools/grade_match.py` |
| Ciel blanc, puis nuages en boules (crash_instinct) | Ciel photographique réel ; pas de nuages en boules de coton | `sky_hdri()` |
| Lumière douce, ombres faibles (crashed_car) | Soleil dur (angle ≤ 2°), ombres nettes, occlusion au contact | défauts de `sun()`, `plan_check` PLACES (ombres décrites) |

## 3. Couleur et étalonnage : mesurés, jamais à l'œil

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| « Le color grading doit être similaire à celui de la référence » | Étalonnage choisi **par mesure** (luminosité, saturation, contraste) sur les images clés ; plusieurs transformations essayées sur un même rendu | `tools/grade_match.py` (doit dire PASS avant un aperçu) |
| « L'herbe est trop foncée et manque de saturation » | Couleur de l'herbe **mesurée** (teinte, clarté, saturation) sur la référence ; sans référence : vert vif et clair (teinte ≈ 90°, clarté ≈ 0,35) | `roadside.verge_grass()` |
| Saturation trop constante (démo ferme) | Saturation variable selon les plans, comme la référence | `grade_match` |

## 4. Végétation

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| « L'herbe est trop haute et trop dense, ce qui prend du temps à calculer » | Herbe **pas plus haute ni plus dense que la référence** ; haute seulement au premier plan qui l'exige ; densité qui baisse avec la distance (LOD) | `s01_plant.grass_and_flowers()` ; règle LOD de CB_RULES §11h |
| « L'herbe verte autour de l'arbre ne s'étend pas sur toute la route … de l'autre côté presque pas d'herbe, ils doivent être identiques » | Les **deux bords** d'une route ont la même bande verte (même largeur, même herbe) sur toute la longueur ; le sol sous l'herbe a la **même couleur** que les touffes vues de loin | `roadside.ground()`, `grass_and_flowers()` ; `plan_check` LOOK |
| Arbre irréaliste | Voir §1 | `sets/oak.py` |

## 5. Mouvement, personnages, objets

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| Le héros « apparaît d'un coup », le casque saute, le pilote se téléporte (crashed_car) | **Tout passe par une action** : rien n'apparaît, ne disparaît ni ne saute à l'écran | `continuity.py` (POP, TELEPORT, SHRINK, POSE_POP) ; section « Entrées / sorties » obligatoire |
| Bras qui sautent d'une pose à l'autre | Un personnage = **une seule vue** ; mouvements mesurés sur les dessins (`card_anchors.py`) ; décalage `m:<id>@<s>` pour démarrer au bon moment ; se relever = le mouvement assis **joué à l'envers** | `card_service` + `card_anchors` ; recettes `stand_up` ; leçons PI-016, PI-018 |
| Mouvement choisi sur son nom qui ne fait pas l'action | Mesurer chaque mouvement (tête, pieds, mains) avant de construire ; aperçu des candidats avec `motion_styles/render.mjs` | PI-018 |
| Casque trop gros (crashed_car) | Les objets tenus ou portés sont à l'échelle de la tête **mesurée** sur le dessin | `card_anchors` |
| « Ajoute un personnage dans la voiture » | Un véhicule qui roule a son **conducteur** visible derrière des vitres claires, qui réagit (choc : projeté en avant) | `s01_plant.driver()` ; `plan_check` OBJECTS |
| Pièce importée qui tourne autour du mauvais point | Recentrer l'origine d'une pièce importée avant de l'animer | PI-021 |
| Aléatoire tiré à chaque image (feuilles qui sautent) | Aléatoire tiré **une fois par objet** | PI-019 ; `continuity.py` |

## 6. Actions, réactions, conséquences

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| « Une voiture passe dans une flaque, elle est mouillée et la flaque éclabousse » | Chaque action a sa **réaction**, sa **conséquence qui reste**, ses micro-animations et son son | `library/reactions/reactions.json` ; `plan_check` ACTIONS |
| Pas de poussière à l'atterrissage ; épave sans bosses ni fumée (crashed_car) | Atterrissage = bouffée de poussière ; choc de véhicule = carrosserie déformée, rebond, fumée, débris | recettes `jump_landing`, `vehicle_impact` |

## 7. Caméra et découpage

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| « La caméra ne s'arrête jamais » | Un mouvement sur chaque image + dérive à l'épaule | `continuity.py` (HOLD), `street.handheld` |
| Coupe inventée dans l'analyse (PI-020) | Limites de plan prises dans `shots.json` et **vérifiées à 30 i/s** ; une prise continue se construit **sur le script du plan précédent** | PI-020 ; `s02_crash` importe `s01_plant` |
| Ciel à la place des champs au loin (bug de coupure) | `clip_end` de la caméra plus loin que le décor | `continuity.py` (CLIP) |
| Cadrage différent de la référence | Mesurer l'horizon et la taille du sujet sur la référence ; caler la caméra dessus | comparaison côte à côte des images clés |

## 8. Méthode de travail et de rendu

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| Analyse insuffisante avant de construire | Analyse détaillée de chaque plan à 10 i/s (`shots/sNN.md`) | CB_RULES §11h |
| « Plan ultra détaillé avant de construire » | `plan.json` + `plan_check` PASS **avant** la première ligne de construction | `plan_check.py` |
| Temps de correction qui doublent | Corriger seulement ce qui change (`--patch`), images clés d'abord | `render_manager.py --patch` |
| « On va faire comme cela pour tous nos prochains shots » | Rendu **par couches** (ciel, décor, objets, effets) | `layers.py`, `render_layers.sh` |
| 64 min pour 3,2 s sur le processeur | Processeur = images clés + **un aperçu rapide en une couche** ; GPU RunPod pour les vrais rendus (accord et plafond de CB) ; mesurer le temps GPU avant de chiffrer | `preview.sh` ; CB_RULES §11h |
| « Chaque problème devient une solution permanente » | Leçon + contrôle / recette / code / ligne de modèle, dans la même séance | ce document, `memory/`, `plan_check`, `continuity` |
