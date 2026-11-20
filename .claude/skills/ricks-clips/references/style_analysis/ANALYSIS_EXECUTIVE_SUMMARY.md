# Synthèse de l'analyse des 5 vidéos de référence

Statut : **PARTIAL**. Les cinq vidéos ont été ouvertes, mesurées et analysées. La lecture image par image est limitée à 2-3 passages par vidéo et l'audio n'a pas été écouté (`analysis_coverage.md`).

## Identité
Des personnages 2D minimalistes (tête blanche à gros contour noir, membres en traits, torse habillé coloré) jouent dans des décors 3D riches éclairés comme au cinéma. Ils projettent des ombres et prennent la couleur de la lumière du décor. Une voix continue, sous-titrée mot à mot, raconte un fait vrai. Chaque phrase est **montrée par une action physique** qui laisse **une trace durable**, et la caméra ne s'arrête jamais.

## Chiffres
- **5 vidéos** : 59,5 à 83,1 s, 720×1280, 30 i/s, −14 LUFS.
- **87 plans, 53 événements, 72 assets** catalogués.
- **286 captures** de preuve et **20 planches** à 2 i/s.
- **288 images lues une à une** sur 11 passages critiques.

## Constantes (les 5 vidéos)
1. Crochet par l'action à l'image 0.
2. Voix ininterrompue : 3,2-3,8 mots/s, pause maximale 0,36-0,64 s.
3. Caméra jamais fixe : 0-3,1 % d'images immobiles.
4. Même famille de personnages ; rôle lu à 2-3 accessoires.
5. Décors 3D continus, matières propres et lisibles.
6. Action sur le mot, contact sur une image, conséquence persistante.
7. Signes 2D pour les émotions extrêmes : éclairs, yeux lumineux, spirales, $, aura, onde.
8. Au moins 4 ambiances de lumière par vidéo (5 à 10 mesurées), qui suivent le récit.
9. Objet planté au début et payé à la fin.
10. Chute qui retourne ou boucle le début.

## Variantes (à choisir, ne pas uniformiser)
| Paramètre | Plage observée |
|---|---|
| Durée médiane des plans | 2,6 à 4,7 s |
| Mouvement de caméra (/255) | 4,2 à 15,5 |
| Saturation moyenne | 0,28 à 0,44 |
| Nombre de lieux | 1 à 9 |
| Structure | linéaire, anthologie datée, lieu-compteur |
| Textes dans le décor | présents (4 vidéos) ou absents (1) |
| Pluie | 3 vidéos |
| Foule | 1 vidéo |
| Noir et blanc | 1 vidéo |

## Découvertes utiles pour RicksClips
- **Peu de coupes franches pour changer de lieu** : on traverse un objet (porte, plafond, écran, pare-brise), on fait un fouetté de 3 images qui cache un saut de temps, ou un fondu de 0,3 s. La coupe franche sert à accélérer.
- **La lumière est refaite pour chaque vue**, même dans un lieu unique (V04). La nuit est un monde bleu saturé avec une source chaude locale, pas une image sombre.
- **Les chocs sont proportionnés** :
  - choc arrière léger : une pièce se détache ;
  - choc violent : capot froissé, décor arraché ;
  - obstacle fixe : roue qui roule et reste ;
  - explosion : flash puis feu.
- **Le décor accumule l'histoire** : traces, objets ajoutés, tas de billets qui restent jusqu'à la fin.
- **La caméra suit l'énergie** au climax (V05) et tombe avec le personnage (V03).

## Lacunes
- Audio non écouté : musique et bruitages INCONNUS.
- Micro-animations fines (clignements, doigts, respiration) non cherchées image par image sur de longues plages.
- Proportions des personnages estimées, pas mesurées au pixel.
- Méthodes et logiciels des originaux INCONNUS. Les reconstructions proposées sont des RECOMMANDATIONS.

## Trois priorités suivantes
1. **Coder les portes manquantes** de `QUALITY_GATES.md` :
   - G8 : conséquence persistante ;
   - G9 : au moins 4 ambiances ;
   - G13 : transitions déclarées ;
   - G12 : signes d'émotion.

   Ajouter aussi les 8 recettes d'interaction à `library/reactions/reactions.json`.
2. **Benchmark EEVEE Next / Cycles à scène identique** sur un plan RicksClips (temps par image, mesure d'étalonnage, planches) avant de figer le moteur.
3. **Compléter la couverture** : lecture image par image des passages restants listés, et écoute des pistes audio dans un environnement qui le permet.
