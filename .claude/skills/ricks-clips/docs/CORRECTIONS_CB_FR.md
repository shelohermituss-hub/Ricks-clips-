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
| « La route est trop claire et trop plate : en vue rasante elle reflète le ciel … asphalte sombre, bleu-gris » (vue aérienne, 19/11) | Couleur de la route **mesurée sur la référence** (#3b3a4b vue d'en haut) : teinte bleu-gris, valeur réglée sur l'image, un peu de reflet rasant (spec 0,4) pour qu'elle reste gris clair vue du sol ; vérifier **les deux** vues (aérienne et au sol) | `roadside.road()` ; `grade_match` sur 180 et 262 |
| « Les champs sont brun foncé : bandes dorées / ocre avec de fins sillons réguliers » | Un champ prend **la couleur mesurée** (or #b99d57, ocre #9d8e63, paille #cebc5b) tout en gardant le relief du scan ; rangs réguliers lisibles d'en haut ; 3 tons en bandes | `rc.look.tex(recolor=, stripes=)` ; `roadside.fields()` ; leçon PI-026 |
| Sol d'une seule couleur ou carreaux répétés vus d'en haut ; pas d'herbe sous la caméra aérienne | Tout sol : texture **sans répétition visible** (seconde copie plus grande, tournée, mélangée par un bruit) et **grandes taches** plus claires / plus sombres (3 à 25 m) ; les touffes 3D couvrent tout ce que la caméra la plus haute voit de près | `rc.look.tex(untile=, macro=)` par défaut ; `s01_plant.grass_and_flowers()` |
| Sable trop lisse, ciel gris plat et blanc, herbe clairsemée, peau trop métal (baleine, 20/11 ; points que j'ai signalés et que CB a demandé de corriger) | Un sol naturel porte **ses rides et ses traces** (rides du vent, zone mouillée, bourrelet autour d'un objet lourd, pas, pneus) ; un ciel couvert garde des **nuages qui ont une forme** (jamais un voile blanc) ; une peau mouillée n'est jamais métallique (métal 0, rugosité ≥ 0,6) ; l'herbe est jugée aussi depuis la caméra la plus haute | `episodes/exploding-whale/sets/beach.py` (`ground`, `traces`, `MOODS`, `whale`, `dune_grass`) |
| Peinture de voiture sans profondeur (crashed_car) | Peinture vernie, reflets d'un vrai ciel (HDRI) | `street.hdri_reflections`, ciel HDRI visible |
| « La voiture scintille … trop mate … blanc métallisé » (crash_instinct) | Ne **jamais** garder la texture de peinture d'un modèle importé (métal/relief qui scintillent) : peinture refaite, lisse, comme la référence ou comme CB le demande (ici blanc métallisé : métal 0,55, rugosité 0,28, vernis 0,6) ; **vitres claires**, jamais teintées | `s01_plant.car()` ; `plan_check` OBJECTS (un véhicule déclare sa peinture et ses vitres) |
| « Analyse la voiture … même peinture, vitres transparentes avec vue sur l'intérieur » (plan 4, 20/11) | Un véhicule de la référence est **analysé en pleine définition** (forme, couleur mesurée, peinture, vitres, intérieur, roues) et le modèle est **choisi pour sa forme** ; peinture refaite à la couleur mesurée, vitres claires, intérieur visible et clair, conducteur | `s04_sign.blue_car()` ; `shots/s04.md` §3 |
| Matériau d'un autre objet repeint par erreur (la voiture bleue sortait blanche) | Deux modèles importés ont souvent des matériaux du même nom (« body ») : ne **jamais** chercher un matériau par son nom seul, toujours parmi ceux de l'objet importé | `blue_car()` (`mine`) ; leçon PI-029 |
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
| « L'ombre de l'arbre est beaucoup trop petite … très longue, elle traverse la route et l'herbe » (vue aérienne, 19/11) | **La lampe soleil est le seul soleil** : le ciel HDRI reste visible, mais pour l'éclairage il est plafonné (plus de soleil photographié) et réduit de moitié ; hauteur et direction du soleil **mesurées sur l'ombre de la référence** (longueur de l'ombre / hauteur de l'objet, direction au sol). crash_instinct : −48°, 15° de haut. En cas de doute : rendu de contrôle « soleil seul » | `rc.look.sky_hdri(light=.5)`, `rc.look.SUN` ; leçon PI-025 |
| « Le soleil doit apparaître en lueur en haut à gauche » | Lueur chaude autour de la direction de la lampe soleil, ajoutée au ciel pour la caméra seulement : halo large qui blanchit le ciel du côté du soleil même hors champ, cœur chaud quand on le regarde | `rc.look.sun_glow()` (appelé par `sky_hdri`, `glow=.8`) |
| « Les rayons de soleil sous l'arbre sont trop discrets » | Brume un peu plus dense sous l'arbre (0,004) + faisceaux **larges et doux** (jamais des traits fins), courts quand le soleil est bas (5 à 7,5 m) pour ne pas barrer la route vue d'en haut | `rc.look.god_rays()`, `light_shafts()` |
| Herbe en contre-jour terne ou vert fluo, sans l'ombre de l'arbre dessus | Herbe et feuilles **laissent passer la lumière** (translucide 0,45) : elles brillent à contre-jour et reçoivent les ombres | `roadside.verge_grass()` ; leçon PI-027 |
| « Analyse le jeu de lumière de la scène de référence pour me proposer exactement le même » ; « la scène est trop sombre » (plan 4, 20/11) | La lumière se **lit sur la référence vue par vue** avant de construire : direction et longueur des ombres (→ azimut et hauteur du soleil), quelle face est éclairée, couleur du ciel, lueur ou non, ouverture des ombres ; tableau « indice → lumière » dans `shots/sNN.md` §10. Une référence peut rééclairer chaque vue : quand la lumière change dans une prise continue, elle change **hors champ dans un fouetté** | `rc.look.relight()` ; `s04_sign.week_later_light()` ; leçon PI-030 |
| Lumière douce, ombres faibles (crashed_car) | Soleil dur (angle ≤ 2°), ombres nettes, occlusion au contact | défauts de `sun()`, `plan_check` PLACES (ombres décrites) |

## 3. Couleur et étalonnage : mesurés, jamais à l'œil

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| « Le color grading doit être similaire à celui de la référence » | Étalonnage choisi **par mesure** (luminosité, saturation, contraste) sur les images clés ; plusieurs transformations essayées sur un même rendu | `tools/grade_match.py` (doit dire PASS avant un aperçu) |
| « L'herbe est trop foncée et manque de saturation » | Couleur de l'herbe **mesurée** (teinte, clarté, saturation) sur la référence ; sans référence : vert vif et clair (teinte ≈ 90°, clarté ≈ 0,35) | `roadside.verge_grass()` |
| « Le contraste mesuré est de 0,14 contre 0,21 … corrige dans la scène, pas par un réglage global » | Un écart de contraste se corrige **dans la scène** (soleil dominant, ombres longues, valeurs du sol, lueur du ciel), jamais par l'étalonnage global, qui dégrade les autres plans ; chaque réglage est remesuré sur une vue haute ET une vue au sol | `grade_match.py` (180 : 0,20 pour 0,21 ; 262 : PASS) ; leçon PI-025 |
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
| « Quand la voiture rentre dans l'arbre c'est l'une des roues de la voiture qui se détache et roule » (20/11) | La pièce qui se détache est **celle du modèle** (découpée de son maillage si les quatre roues ne font qu'un objet), du côté de la caméra, visible dès le choc ; elle tourne de la distance roulée, rebondit, roule, vacille, tombe et reste | `s04_sign.wheel_off()` ; recette `wheel_off` |
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
| Un saut dans le temps dans une prise continue (plan 4 : l'épave disparaît, le panneau apparaît) | L'échange se fait **hors champ dans un fouetté** (caméra dans le feuillage) : rien de ce qui change n'est à l'écran l'image d'avant ni l'image d'après ; déclaré dans « Entrées / sorties » | `s04_sign.key_vis()` ; `continuity.py` (POP) |
| Cadrage différent de la référence | Mesurer l'horizon et la taille du sujet sur la référence ; caler la caméra dessus | comparaison côte à côte des images clés |

## 8. Méthode de travail et de rendu

| Correction de CB | Règle | Appliquée par |
|---|---|---|
| Analyse insuffisante avant de construire | Analyse détaillée de chaque plan à 10 i/s (`shots/sNN.md`) | CB_RULES §11h |
| « Plan ultra détaillé avant de construire » | `plan.json` + `plan_check` PASS **avant** la première ligne de construction | `plan_check.py` |
| Temps de correction qui doublent | Corriger seulement ce qui change (`--patch`), images clés d'abord | `render_manager.py --patch` |
| « On va faire comme cela pour tous nos prochains shots » | Rendu **par couches** (ciel, décor, objets, effets) | `layers.py`, `render_layers.sh` |
| 64 min pour 3,2 s sur le processeur | Processeur = images clés + **un aperçu rapide en une couche** ; GPU RunPod pour les vrais rendus (accord et plafond de CB) ; mesurer le temps GPU avant de chiffrer | `preview.sh` ; CB_RULES §11h |
| « Utilise Cycles comme moteur principal » (20/11) | Cycles pour tous les rendus (processeur pour les images clés et aperçus, GPU OptiX pour les vrais rendus) ; pas de nouveau comparatif de moteurs | défaut de `rc.render.setup`, `rc/cli.py`, `render_manager.py` ; `CB_RULES.md` |
| « Chaque problème devient une solution permanente » | Leçon + contrôle / recette / code / ligne de modèle, dans la même séance | ce document, `memory/`, `plan_check`, `continuity` |

## 20/11 — Baleine explosée, plan 1 : couleurs « aussi vives et cinématiques que les références »
- **Remarque de CB** : les couleurs des références sont plus vives, plus saturées et plus cinématiques que les miennes ; j'avais comparé seulement des moyennes globales.
- **Ce qui a été fait** : ciel rendu vif pour la caméra seulement (saturation 1,5, gain 1,85), soleil plus fort (11), sujets plus gros dans le cadre, sable calmé, et **exposition qui suit la vue** (`EXPO_KEYS` dans `shots/s01_button.py` : −0,17 sur la partie dune, qui regarde le côté clair du ciel).
- **Règle retenue** : comparer **côte à côte et par zone** (ciel, sol, sujet) avec des images de référence, pas seulement la moyenne de l'image. Mesure du 20/11 : ciel S73-78 V81-82 côté caisses (références S54-94 V82-89) ; ciel V98 côté dune et sol V71-85 (références V53-67) : **encore trop clairs**, à corriger avant le rendu final.
- **Reste hors plage** : image 70 (fouetté, luminosité 0,60 pour 0,58 max, saturation 0,52 pour 0,48 max) ; images 20 et 40 à la limite de saturation (0,48-0,49).

## 20/11 — Script « look Fortnite Cycles » demandé par CB (`blender/tools/fortnite_cycles_look.py`)
- **Demande** : un script `bpy` idempotent qui règle seulement couleurs, shaders et lumières (ciel physique, soleil, contre-jour cyan, débouchage bleu, volume d'air, groupe `NG_Fortnite_Cycles_PBR`, compositing), sans toucher à la géométrie ni à la caméra.
- **Fait** : script écrit pour Blender 4.2 → 5.x, relancé 3 fois sans doublon (mêmes comptes d'objets, de nœuds et de matériaux). Les cartes 2D des personnages sont laissées intactes (`--skip-prefix Card_`).
- **Écarts par rapport au cahier des charges, imposés par Blender 5.2** : ciel « Nishita » remplacé par `MULTIPLE_SCATTERING` ; `dust_density` devenu `aerosol_density` ; réglages du Glare, du Color Balance et de la distorsion passés en entrées de nœud (mix −0,65 → force 0,35 ; taille 7 → 0,25).
- **Mesuré** : avec le ciel à force 1,0 l'image est brûlée (luminosité 0,86, saturation 0,06). Un calibrage `--sky-gain 0.05` a été ajouté. Même calibré, le plan 1 sort **plus pâle** que notre look précédent (saturation 0,24-0,27 contre 0,43-0,48 ; plage des références 0,26-0,48) : le contre-jour cyan, le débouchage bleu, l'ambiance bleu-violet et la brume neutralisent les couleurs chaudes.
- **Règle retenue** : un cahier des charges chiffré se vérifie par un rendu mesuré avant d'être adopté ; ne jamais annoncer un look sans l'image et la mesure.
- **Décision de CB (20/11)** : script abandonné et retiré du dépôt. On garde le look précédent du plan 1 (ciel à nuages vif, soleil dur, exposition qui suit la vue).

## 20/11 — Style visuel « Fortnite » demandé par CB (`blender/rc/fortnite.py`)
- **Demande** : donner à la vidéo le style des cinématiques Fortnite (semi-réaliste / jeu vidéo / dessin animé moderne), en ne touchant qu'aux couleurs, aux shaders, à la lumière et à l'atmosphère, **adapté automatiquement à la scène**.
- **Fait** : le module lit la scène (soleil, groupes de personnages et moment où la caméra les voit le mieux, distances, matériaux) puis règle : soleil réchauffé, lumière bleu-violet sans ombre qui colore toutes les ombres, un contre-jour cyan par groupe de personnages (jamais sur le sol, par liaison de lumière), brume avec la distance, groupe de shader `NG_FN_StylisedPBR` (variation peinte, arêtes éclaircies, creux teintés, grain adouci, métaux nets, translucidité de la végétation), halo, ombres froides / lumières chaudes, et **exposition calibrée par de petits rendus d'essai**. Relancé deux fois : aucun doublon.
- **Mesuré sur le plan 1** (images 20 et 112) : luminosité 0,49-0,50, saturation 0,51 et 0,43, contraste 0,17-0,20. Le ciel à nuages et la position du soleil du plan sont conservés.
- **Limites** : aucune image de Fortnite n'est dans le dépôt, le style vient de ses traits connus et pas d'une mesure ; les personnages sont des cartes 2D plates, donc ni contre-jour sur leur contour ni translucidité ; pas encore branché dans le script du plan (appliqué sur la scène enregistrée) ; seules 2 images clés vérifiées.
- **Leçons** : (1) un contre-jour doit exclure le sol, sinon il le peint en cyan ; (2) la lumière de remplissage bleue doit rester faible (6 % du soleil), sinon elle éteint les couleurs chaudes ; (3) l'exposition se règle par mesure sur plusieurs moments du plan, pas sur un seul.
- **Décision de CB (20/11)** : style Fortnite abandonné lui aussi, module retiré. Le film garde le look du plan 1 (ciel vif à nuages, soleil dur, exposition par vue). CB passe en mode automatique : construire tous les plans, analyser et corriger chacun, sans rien demander avant la fin.

## Construction autonome du film « Exploding Whale » — leçons de la relecture sur images calculées
- **Relire sur les images calculées, pas seulement sur les images clés** : 4 défauts n'étaient visibles que là (plans 02, 07, 08, 11).
- **Cylindres** : un cylindre entièrement lissé s'ombre comme une boule (roues du camion). `kit.cyl` marque maintenant les arêtes vives (`set_sharp_from_angle`), et les roues ont un moyeu.
- **Anneau de choc au sol** : jamais émissif ni persistant — il blanchissait toute la plage après l'explosion. Couleur sable, disparaît en 16 images.
- **Écume** : une grande plaque blanche se lit comme une dalle. Bande étroite seulement.
- **Petits objets (clés)** : une forme pleine devient un « œuf ». Dessiner la silhouette vraie (anneau ouvert, deux lames, porte-clés) et garder la poussière petite et couleur sable.
- **Vérifier que la reconstruction a réussi** : une faute de syntaxe ne produit pas le mot « Traceback » ; le contrôle cherche maintenant aussi « SyntaxError », et je regarde l'heure du fichier .blend avant de relancer un calcul (une heure de calcul perdue sur d'anciennes scènes).

## CB 2026-11-20 — « le film reste en mode preview : aucun travail de color grading, de lighting, de texture ; de la 3D dure »
- **Constat (CB a raison)** : la finition des plans 02–16 se limitait à un réglage de saturation ; les objets codés (camion, caméra TV, colonne de fumée, panneau, mobilier) avaient une couleur unie sans matière ; pas de brume de distance, pas de halo, pas de flou d'objectif. L'étape « look » (modèles réels + matières + finition, étape 9) n'avait pas été faite et je l'avais présentée à tort comme « décors faits ».
- **Règle** : ne jamais montrer à CB un film dont l'étape look n'est pas faite sans le dire en première ligne. Un aperçu d'animation s'annonce comme tel.
- **Code (v1, test sur 3 images)** : `kit.ink` = surface peinte (rugosité variable, grain, arêtes arrondies, saleté dans les creux, poussière sur le dessus) ; `kit.grade` = brume de distance (jamais sur le ciel), halo doux, hautes lumières chaudes / ombres froides, vignette, netteté ; caméra avec profondeur de champ.
- **Mesure honnête** : l'avant/après v1 est une amélioration légère, pas suffisante. Le vrai levier restant = remplacer les objets codés par de vrais modèles, travailler le sable (relief, sable mouillé, traces) et la fumée en volume.

## CB 2026-11-20 — comparaison avec les références : « pratiquement rien n'a été fait »
Comparaison côte à côte (`episodes/exploding-whale/build/review/comparaison_reference_v1.jpg`). Ce que les références ont et que le film n'a pas :
1. **Trait d'encre sur les objets 3D** (contour sombre + lignes intérieures : planches, joints, rivets) — nos objets 3D n'ont aucun trait, donc ils ne vont pas avec les personnages dessinés.
2. **Monde peint, pas photo** : ciel en dégradé (orange à l'horizon → bleu) avec nuages dessinés, eau stylisée avec dessins d'écume blancs. Nous : photo de ciel + photo de sable = « 3D brute ».
3. **Décors pleins** : chaque image de référence contient 10–20 objets lisibles. Notre plage est vide.
4. **Palette décidée** : 2–3 couleurs fortes opposées (bleu/orange, turquoise/rouge). Nous : beige + gris.
5. **Lumière mise en scène** : lampes chaudes qui rayonnent, reflets au sol, contre-jour sur les personnages, ombres colorées. Nous : un soleil et c'est tout.
6. **Détail dessiné sur chaque objet** : planches, lettres, sangles, bandes de couleur. Nous : boîtes unies.
**Règle** : avant tout aperçu de film, poser 4 images du film à côté de 4 images de référence et lister les écarts. Le « réalisme photo » (HDRI + textures photo) n'est PAS le style des références.

## CB 2026-11-20 — STYLE VALIDÉ : « c'est exactement ce style que je veux, garde-le en tête pour tous les prochains plans et vidéos »
**Le monde dessiné** (code : `episodes/exploding-whale/sets/toon.py`, appliqué au plan 02) est LE style de tous les plans et de toutes les vidéos à venir :
1. Ciel peint en dégradé (orangé à l'horizon → bleu), nuages dessinés en trois couches (gros cumulus, ligne d'horizon, traînées hautes), halo du soleil, oiseaux au loin. Jamais de photo de ciel.
2. Mer dessinée : turquoise au bord → bleu profond, traits d'écume blancs animés, lisière d'écume sur le sable.
3. Sol dessiné, **sable blanc crème, jamais jaune** (CB : « le sable est jaune, je n'aime pas, une couleur plus blanche »), avec du dessin au sol : groupes de traits de rides, creux mauves, mouchetures, dentelle d'écume séchée, sable mouillé plus froid et brillant.
4. Trait d'encre sur CHAQUE objet 3D (coque inversée) ; détail dessiné (planches, rayures, bandes) plutôt que textures photo.
5. Décor plein : 10–20 objets lisibles par image, jamais une moitié d'image vide ; un fond qui ferme l'horizon (cap, phare, voilier).
6. Couleurs décidées qui s'opposent (bleu / orangé-rouge), soleil chaud, ombres bleutées, halo léger, brume de distance teintée.
7. Une vague = eau claire + lèvre d'écume festonnée, jamais une plaque blanche.
**Règle de travail** : valider UN plan à côté des références avant d'habiller les autres ; montrer avant/après + référence sur la même planche.

## CB 2026-11-20 — « le ciel est sous-exposé et les personnages blancs semblent assombris »
- **Cause** : pour empêcher le sable blanc de brûler, j'avais baissé l'exposition de toute l'image (−0,5) : le ciel peint, les nuages et les personnages baissaient avec.
- **Règle** : un sol clair se tient avec la LAMPE (soleil ×0,7, ambiance 0,30), jamais avec l'exposition. Le ciel et les nuages gardent leur pleine valeur ; les personnages dessinés sont éclairés à 86 % par leur propre lumière pour que le blanc reste blanc.
- **Code** : `sets/toon.py` (`stylize`), `shots/film.py` (`_drawn_finish` sans baisse d'exposition).

## CB 2026-11-20 — « pour le camion et le tracteur, cherche de vrais assets, pas des formes assemblées »
- **Règle** : un véhicule ou une machine = TOUJOURS un vrai modèle (Asset Hub : `tools/asset_hub.py search/download sketchfab`), jamais des boîtes et cylindres assemblés. Choisir sur vignettes, licence CC-BY, pièce mobile séparée si le plan l'anime (benne).
- **Fait** : camion = « Tatra 148 dump truck » (Randonavt, CC-BY 4.0), benne sur charnière, repeint orange ; bulldozer = « Stylized Bulldozer » (freddielin, CC-BY 4.0). Code : `shots/film.py` (`model`, `truck`, plan 14).
- **Ciel terne des plans de midi (10, 11)** : les ambiances avaient une exposition négative (−0,42 à −0,5) réglée pour un ciel photo ; elle assombrissait le ciel peint. Elle passe maintenant sur les lampes (exposition 0), horizon cyan pâle à midi.

## CB 2026-11-20 — AUDIT RÉALISME : « les objets et l'environnement doivent avoir un look plus réaliste » (référence : The Instinct That Makes You Crash)
Planche : `episodes/exploding-whale/build/review/audit_realisme_v1.jpg`. Écarts mesurés à l'œil, image par image :
| Point | Référence | Notre film (monde dessiné) | Correction |
|---|---|---|---|
| Ciel | vrais nuages en volume, éclairés par le soleil, brume à l'horizon | dégradé plat + nuages en boules | vrai ciel (photo HDRI vive) + brume |
| Véhicules | peinture vernie, vitres qui reflètent le ciel, chrome, pneus | couleur unie + trait d'encre | textures d'origine du modèle, vernis, vitres miroir, pas de trait |
| Sol | bitume / herbe réels avec relief | sable dessiné à plat | sable scanné, recoloré blanc crème, sable mouillé brillant |
| Mer | (réf. eau réelle dans whale_boat) | aplats + traits | eau réelle qui reflète le ciel, écume au bord |
| Lumière | soleil fort, ombres longues, rayons, halo | soleil seul | rayons de soleil dans une brume légère, halo |
| Fumée | panache réel, doux | boules avec trait | fumée en volume |
| Objets 3D | AUCUN trait d'encre (seuls les personnages 2D en ont) | trait partout | trait retiré en mode réel |
**Règle (remplace « monde dessiné » pour les matières)** : monde RÉEL et cinématographique (ciel réel, textures réelles, reflets, rayons, fumée en volume), personnages 2D dessinés ; on GARDE du travail précédent : décor plein, sable blanc, vrais modèles, couleurs vives, personnages blancs. Code : `sets/toon.py` (`STYLE = "real"`, `realist`, `glass`, `smoke_mat`).

## CB 2026-11-20 — « ce n'est pas du tout bon, ça n'a presque rien à voir avec les références ; pourquoi ne peux-tu pas les reproduire ? »
Causes réelles (constat, pas excuse) :
1. **Méthode** : j'ai changé de look trois fois en une journée (photo → dessiné → réaliste) en réinventant chaque fois, au lieu de prendre UNE image de référence comme cible et de la reproduire élément par élément avec mesure (`tools/reference_compare.py`, `tools/grade_match.py` non utilisés sur ce film).
2. **Assets** : les références sont faites avec des bibliothèques d'assets professionnels cohérents (végétation, véhicules, bâtiments du même style) ; j'ai mélangé photo-scan, modèles Sketchfab de styles différents et objets codés à la main.
3. **Jugement sur des images trop pauvres** : tests à 405×720, 16–24 échantillons, débruités ; la référence est nette en 1080p. Un look ne se valide qu'à qualité finale.
4. **Travail à l'aveugle** : je ne vois pas la scène, seulement des images fixes ; chaque essai coûte plusieurs minutes.
**Règle** : un look se construit en REPRODUISANT une image de référence précise, sur un plan, à qualité finale, avec comparaison mesurée ; rien d'autre n'avance tant que ce plan n'est pas validé par CB.

## CB 2026-11-20 — « dans la démo tu y arrives très bien, pourquoi ne pas utiliser la même méthode ? c'est pour t'imprégner du style que je t'ai donné les références »
- **Règle permanente** : tout nouveau film se construit avec la MÉTHODE DE LA DÉMO (`demos/crash_instinct`) : réglages de lumière MESURÉS sur la référence (mood `ref` de `sets/beach.py` : Standard + Medium Contrast, soleil bas, ciel HDRI naturel, halo, lumière de rebond, rayons en volume local), puis `tools/grade_match.py` image contre image, et correction jusqu'à être dans la tolérance. Jamais de look inventé.
- **Accès** : BlenderKit branché (secret réseau `www.blenderkit.com`, hôtes `assets.blendkit.com` + `public.blenderkit.com`). Commande : `BLENDERKIT_API_KEY=proxy-injected CLAUDE_CODE_REMOTE=true blender -b --factory-startup --python tools/blenderkit_tool.py -- search|get …`. Fichiers hors Git (`library/blenderkit/`, ignoré), journal `library/blenderkit_assets.md`.
- **Décor** : uniquement de vrais modèles (`toon.bk`, `toon.dress_real`) : barque, ponton, parasol, transats, bouée, coffre, voilier.
- **Mesures plan 07** (réf → nous) : v1 rapproché 0,51/0,28/0,23 → 0,57/0,29/0,21 ; large 0,60/0,25/0,20 → 0,77/0,14/0,18 (délavé) ; v2 large → 0,66/0,19/0,19.

## CB 2026-11-20 — CHANGEMENT DE PROGRAMME : « garde cette vidéo de côté, nous allons reproduire les vidéos de référence, comme ça tu apprendras de toi-même ; après, tu me construis une vidéo originale à partir des références »
- **« Exploding Whale » est mis de côté** (`episodes/exploding-whale/`, état : script, voix, sous-titres, animation et cadrages des 16 plans faits ; look non validé — trois essais refusés : photo, dessiné, réaliste). Ne pas y retravailler sans demande de CB.
- **Programme** : 1) reproduire les vidéos de référence plan par plan (assets, étalonnage, environnement, animations, actions, effets, lumière), en notant ce que chaque plan m'apprend ; 2) seulement ensuite, une vidéo originale construite à partir de ces acquis.
- **Point de départ** : `demos/crash_instinct` (« The Instinct That Makes You Crash », 59,5 s, 1 783 images) : plans 1 à 4 reproduits (images 0 à 362) ; reprise au **plan 5** (image 363 : « So the town nails a giant flashing arrow to it… »).
- **Méthode par plan** (celle qui a marché) : fiche de plan depuis la référence (`references/crash_instinct/shots/sNN.md` : découpage, décor, personnages, objets, caméra, effets, son) → construction → images clés à côté de la référence → `tools/grade_match.py` → corrections → aperçu en mouvement à côté de la référence.
- **Assets** : Sketchfab + BlenderKit branchés ; toujours de vrais modèles.
