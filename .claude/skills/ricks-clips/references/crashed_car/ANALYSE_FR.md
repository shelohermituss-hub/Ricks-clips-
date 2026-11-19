# Analyse — « He Crashed His Own Car For Science » (référence Rick's Clips)

Source : `references/crashed_car/source.mp4`, copie du fichier envoyé par CB le 19/11.

Matériaux de travail dans ce dossier :
- planches à 2 images par seconde : `sheet_00..03.jpg` ;
- images clés en 540×960 : `hi/` ;
- transcription mot à mot : `words.json`, `transcript.txt` ;
- mesures image par seconde : `ref_measures.json`.

Tout ce qui suit est mesuré ou observé sur la vidéo.

## 1. Fiche technique (mesurée)

| | Valeur |
|---|---|
| Format | 1080×1920 (9:16), 30 i/s, H.264 à 3,5 Mb/s, AAC stéréo 44,1 kHz |
| Durée | **51,5 s**, soit 1 545 images |
| Narration | **177 mots, 3,44 mots/s**, du début à la fin sans trou : une seule pause supérieure à 0,35 s (0,40 s après « everywhere ») |
| Loudness | **−13,9 LUFS** intégré, plage de 2,8 LU (très compressé, standard Shorts) |
| Fond sonore | toujours présent : environ 7,6 dB sous la voix pendant les micro-pauses. Énergie surtout entre 150 et 500 Hz : musique douce et ambiance, plus des bruitages ponctuels. |
| Coupes franches détectées | 10 en 51 s. Toutes les autres transitions sont des **mouvements continus** : balayages flous, passages à travers un objet, fondus courts. |
| Lieux | **11 lieux différents** en 51 s |

## 2. Mesures d'image (par seconde, `reference_compare.py`)

| Mesure | Médiane | Min – max | Notre démo ferme (GPU) |
|---|---|---|---|
| Luminance | 0,429 | 0,17 – 0,64 | 0,37 |
| Saturation | 0,405 | 0,23 – **0,70** (pics voulus : ciel crépusculaire, néon) | 0,54 (trop constante) |
| **Mouvement** | **41,8** (médiane ×1000 : 35,8) | 8,8 – 86,9 | **14,7** : 2,4 fois moins |
| Netteté des contours | 0,073 | 0,036 – 0,109 | 0,064 |
| Noirs écrasés / blancs brûlés | 0,008 / 0,009 | jusqu'à 0,07 | proches |
| Pics d'action par 10 s | **11,5** | | 4,7 |

**Conclusions :**
1. L'écart principal n'est pas la couleur : c'est **le mouvement**. La caméra ne s'arrête presque jamais, et il se passe quelque chose toutes les 0,9 s.
2. Rick lui-même échoue à 3 de nos gates (netteté ≥ 0,075, noirs ≤ 0,01, saturation > 0,6 pendant 4 s). Ces seuils sont **plus sévères que la référence** et seront recalés sur ces mesures.

## 3. Découpage plan par plan

Temps en secondes ; les mots sont ceux de la narration.

| # | Temps | Narration | Lieu et décor | Caméra | Action | Transition sortante |
|---|---|---|---|---|---|---|
| 1 | 0,0 – 4,1 | He crashed his car right into his own invention, on purpose! | Rue pavillonnaire de jour : maison vert d'eau, garage avec **cible rouge et blanche**, pelouse très verte, boîte aux lettres, bouche d'incendie, ciel bleu saturé, gros nuages | Grand angle en hauteur qui **descend en grue** au ras de l'herbe, puis suit la voiture | Berline bleue qui entre dans l'allée et percute des **barils en bois** : éclats, poussière, sacs projetés. Le héros sort (casquette d'aviateur, lunettes, moustache) | coupe |
| 2 | 4,1 – 8,4 | You see, he was a retired race car driver, and after a bad crash, | **Stand de course** : formule rouge sponsorisée, tribune pleine en arrière-plan, grillage, confettis | Travelling avant lent vers le pilote casqué ; fondu vers une version âgée | Lui casqué dans la F1, puis plus âgé, casque sous le bras ; **une F1 qui se retourne en l'air** derrière lui, gravier projeté | fondu enchaîné (6,5 s), puis coupe |
| 3 | 8,4 – 11,4 | he vowed to make the race track safer for all. | **Bureau-garage** : liège avec fils rouges, affiche « STOP CAR. GENTLY. », coupures « MY BAD », trophées, casque sur étagère, lampe suspendue, lumière de store | Lent push-in, puis rapprochement sur le visage déterminé | Il désigne le tableau | coupe |
| 4 | 11,4 – 12,6 | So, | Tableau blanc : dessin de barils de tailles croissantes | Gros plan avec léger mouvement | — | coupe |
| 5 | 12,6 – 14,1 | he started working on barrels that could stop a car | Allée : barils en bois empilés, lui au marteau ; puis rue avec voiture bâchée | Plans courts, cadrage serré | Bricolage | coupes rapides |
| 6 | 14,1 – 18,0 | right in its tracks. Sure enough, the first prototype didn't go well, | Allée, berline bleue cabossée et fumante, panneau « PATENT PENDING » en bois cassé | Plan moyen, léger panoramique | Voiture qui s'arrête mal, porte ouverte, il sort sonné, fumée | **passage à travers un baril en gros plan** (18,0 s, flou de bougé) |
| 7 | 18,0 – 22,4 | but once he swapped out the wooden barrels for plastic ones, things started looking better. | Allée vue de loin, puis **barils jaunes en plastique** devant la cible ; caddie avec pastèque | Vol caméra rapide vers la maison, puis approche | Barils jaunes posés, test à la pastèque, lui avec presse-papiers | coupe |
| 8 | 22,4 – 24,3 | But the final test was to drive his own car | Rue de jour, berline bleue | Plan moyen, porte ouverte | Il monte dans la voiture | coupe sur un **changement de lumière** |
| 9 | 24,3 – 27,9 | into them at 70 miles per hour. | **Même rue au crépuscule** : ciel violet saturé, bas orangé ; panneau « 70 MPH » (graphique en 3D dans la scène) | Plan sur la voiture, survol rapide de la rue, panneau | Voiture qui démarre, fumée de pneus | coupe |
| 10 | 27,9 – 28,3 | His neighbor | Porche du voisin : chemise orange, chapeau | Plan fixe court | Il regarde | coupe |
| 11 | 28,3 – 29,7 | saw him floor it in his own driveway | **Vue en jumelles** (masque noir à deux cercles), puis rue | Panoramique filé, passage rapide de la voiture | Voiture lancée | flou de bougé |
| 12 | 29,7 – 33,5 | and throw himself onto the floor right before impact. | **Intérieur de la voiture** : siège, plancher, levier, toit | Contre-plongée très proche, caméra embarquée qui tremble | Il se jette au sol, visage crispé, goutte de sueur | coupe |
| 13 | 33,5 – 35,1 | And the crazy part? It worked! | Tableau de bord (autoradio « Sunny Side Radio ») ; allée : voiture intacte devant les barils | Mouvement rapide | Il se relève, bras écartés | **zoom-traversée dans un baril jaune** |
| 14 | 35,1 – 47,5 | Because the barrels hold more sand the further back you go, when a car hits the first one, it bursts the sand everywhere, and has to shove it out of the way. Then the next barrel, and the next, all the way until the car stops at a soft halt. | **Autoroute** : rangée de barils jaunes devant une pile de pont, viaduc, arbres, marquages ; panneau de vitesse (52 → 0) | Travellings latéraux au ras du sol le long des barils ; plans larges ; caméra qui suit la voiture | **Démonstration** : une voiture verte percute les barils un par un, nuages de sable, sable étalé ; une autre voiture repart ; arrêt doux. Conducteur en lunettes de soleil, chien sur la banquette, couvercles « 2,100 LBS SAND » | coupes et balayages |
| 15 | 47,5 – 51,5 | So the next time you see these yellow things on the highway, remember... | Intérieur de voiture sur autoroute (point de vue conducteur), rétroviseur avec les barils ; **retour au plan 1** (rue et cible) | Caméra subjective, puis gros plan sur le rétroviseur | — | **boucle** : la dernière image raccorde sur la première |

## 4. Bible du look (observée)

**Monde :** 3D cartoon de qualité long-métrage TV.
- **Formes** : douces et arrondies, proportions légèrement exagérées (maisons trapues, barils dodus).
- **Arbres** : feuillage en grosses boules « nuage » avec un ombrage par paquets, pas des feuilles réalistes.
- **Herbe** : brins réels, denses, au premier plan.
- **Matériaux** : PBR simplifiés.
  - Couleurs pleines et saturées, peu de textures bruitées.
  - Bois avec veinage visible.
  - Métal peint brillant.
  - Plastique jaune vif avec bande réfléchissante.

**Lumière :**
- **Soleil franc** à ombres portées nettes mais à bord doux.
- Fort rebond de lumière (GI) : les ombres restent lisibles, jamais noires.
- **Ciel bleu profond** avec gros nuages volumétriques blancs.
- Une séquence au crépuscule (violet saturé) pour le soir du test.
- Intérieur éclairé par une lampe chaude et un store qui découpe la lumière.

**Image :**
- Netteté élevée.
- Flou de mouvement sur les mouvements rapides.
- Profondeur de champ légère sur les gros plans.
- Pas de grain.
- Contraste moyen, saturation élevée mais pas uniforme.

**Personnages :**
- Les **mêmes « stick figures »** que notre distribution 2D : tête ronde blanche, trait d'encre noir, yeux et bouche dessinés, corps en bâton, vêtements simples (salopette bleue).
- Ce sont des **cartes 2D** éclairées dans le monde 3D : elles portent une ombre au sol et reçoivent la lumière de la scène.
- Accessoires dessinés : casquette d'aviateur, lunettes, moustache, gouttes de sueur, lunettes de soleil.
- **Notre système de cartes est déjà le bon outil.**

**Textes à l'écran :**
- Sous-titres **1 à 3 mots** à la fois, blancs, gras, police ronde, **contour noir épais**, centrés à environ 72 % de la hauteur.
- Ils changent sur chaque mot.
- Panneaux et inscriptions intégrés au décor : « 70 MPH », « STOP CAR. GENTLY. », « PATENT PENDING », « 2,100 LBS SAND ».

**Montage :**
- 11 lieux en 51 s.
- Transitions surtout par **mouvement** : traversée d'objet, balayage flou.
- Lumière qui change entre jour et crépuscule.
- Retour en boucle sur le plan d'ouverture.

**Son :**
- Voix continue à 3,44 mots/s.
- Fond musical léger permanent.
- Un bruitage sur chaque action : impact, sable, pneus, vent.
- −14 LUFS.

## 5. Écarts entre notre pipeline actuel et cette référence

| Point | Référence | Nous (démo ferme) | Conséquence |
|---|---|---|---|
| Mouvement de caméra | médiane 41,8 | 14,7 | Plans plus vivants : grues, survols, traversées, caméras embarquées |
| Rythme | un événement toutes les 0,9 s, 11 lieux | 5 plans en 15 s | Beaucoup de plans courts, des lieux « légers » |
| Décors | **construits pour le cadre** : seulement ce que voit la caméra | un monde entier (8 000 instances, 1 M de triangles par arbre) | Notre coût de rendu (4,5 s par image) vient de là : préparation de scène |
| Arbres | boules de feuillage stylisées, légères | arbres Poly Haven réalistes | Moins beau **et** plus lent |
| Effets | sable et poussière : nuages opaques stylisés | volumes procéduraux coûteux | Particules et maillages stylisés à la place des volumes |
| Lumière | soleil + GI fort + ciel bleu profond | correct mais plus terne | Réglage de la lumière et du ciel |

## 6. Outil retenu : **Blender + Cycles sur GPU**, avec des décors « pour le cadre »

**Pourquoi Blender :**
- C'est le seul de nos outils qui donne ce rendu : vrai GI, ombres douces, herbe dense, flou de mouvement et profondeur de champ.
- three.js (notre ancien kit) ne fait ni le GI ni ces ombres, et resterait visiblement en dessous.

**Pourquoi Cycles plutôt qu'EEVEE :**
- Mesuré sur RTX 4090 : EEVEE n'est que 10 % plus rapide sur notre scène, et plus plat (ombres de contact faibles).
- Le look de la référence repose justement sur le rebond de lumière.

**La vraie économie vient de la méthode, pas du moteur :**
1. **Un décor léger par lieu**, construit pour la caméra, au lieu d'un monde complet : quelques dizaines d'objets, arbres stylisés de quelques milliers de triangles, herbe uniquement dans le champ.
   - Ce qui coûtait 4 s par image chez nous venait de la taille de la scène.
2. **Effets stylisés** (sable et poussière en maillages et particules) au lieu des volumes procéduraux.
3. **Rendu en 1080×1920 à 32 échantillons + débruiteur OptiX.**
   - Objectif : environ 1,5 à 2 s par image sur RTX 4090, soit 1 545 images en environ 45 min, pour environ 0,70 à 0,90 $.
   - Ce chiffre est **à confirmer sur un plan test** avant tout rendu complet.
4. Personnages : nos cartes 2D (déjà validées), avec un tracé de personnages adapté au besoin. Jeu sur la narration (faster-whisper).
5. Son : voix (Fish Audio), bruitages procéduraux (`rc.sound`) et un fond musical, mixés à −14 LUFS.

## 7. Limite à respecter : reproduire, pas copier

- La vidéo appartient à Rick's Clips. Je peux reproduire **la méthode, le look, le rythme, les mouvements de caméra et la structure**.
- L'histoire est **vraie** (un ancien pilote de course a inventé les barils à sable des autoroutes et les a testés lui-même), donc elle peut être racontée.
- Mais je **n'utiliserai pas la narration mot pour mot de Rick, sa voix, ni ses designs exacts** (personnages, logos « BIG BARREL »).
- Nous écrirons notre propre texte, avec les faits vérifiés et sourcés, avec notre voix et nos personnages de la distribution.
- Le résultat sera très ressemblant en qualité et en style, sans être une copie publiée de son œuvre.

## 8. Plan de production proposé

1. **Plan test** : plan 1, la rue et le crash dans les barils en bois (4 s, 122 images).
   - Rendu local en basse définition pour le look, comparé côte à côte avec la référence (mesures du §2 et planche).
   - Puis 30 images sur GPU pour mesurer le temps réel par image et le coût.
   - **Décision de CB sur ce plan avant le reste.**
2. Script (nos mots, faits vérifiés), voix, mots minutés.
3. Décors des 11 lieux en version légère, en commençant par les lieux qui reviennent : rue et allée (plans 1, 5 à 9, 11, 13) et autoroute (14, 15).
4. Caméras plan par plan (grues, survols, traversées, caméra embarquée) avec la cible de mouvement médian ≥ 35.
5. Effets : éclats de bois, sable, fumée de pneus, confettis, F1 qui se retourne.
6. Rendu GPU en une seule session (plafond à fixer par CB), sous-titres, son, contrôle contre les mesures de ce document.
