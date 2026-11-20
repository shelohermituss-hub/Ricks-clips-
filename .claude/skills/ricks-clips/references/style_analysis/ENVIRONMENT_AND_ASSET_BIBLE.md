# Environnements, assets, matières, profondeur

Bible centrale : `RICKCLIPS_REFERENCE_STYLE_BIBLE.md`. Catalogue : `asset_catalog.csv` (72 assets classés héros / secondaire / dressing / fond / effet).

## 1. Lieux observés
| Vidéo | Lieux | Particularité |
|---|---|---|
| V01 | cellules, atelier peinture, salle commune sur 2 niveaux, couloir, toit, campagne, quai, hall de nuit | intérieurs carcéraux continus, traversés par la caméra |
| V02 | autoroutes (jour, crépuscule, pluie), banlieue, bureau en hauteur, piscine, habitacles | habitacles détaillés |
| V03 | avion, ciel, ferme, hôpital, rue, train, Alaska, caserne, Grand Canyon, supérette | 9 lieux, un par épisode |
| V04 | un bord de route revu 6 fois, ville, bureau du shérif, garage | **lieu-compteur** |
| V05 | fort, cour, vallée, plaine | paysage très étagé, foule |

## 2. Composition spatiale (OBSERVÉ)
- **Trois couches de profondeur** presque partout :
  - premier plan (herbe haute, table, tableau de bord, rempart) ;
  - plan moyen (personnages, objet héros) ;
  - fond (coursive, vallée, montagnes, horizon de champs).
- **Lignes directrices fortes** : route jusqu'à l'horizon (V02, V04), rempart en diagonale (V05), néon et arête du plafond en diagonale (V01).
- **Échelle** : vues aériennes et plans d'ensemble qui montrent l'étendue (campagne V01, canyon V03, route infinie V04, vallée V05).
- **Zone d'action dégagée** au centre du cadre 9:16, décor dense autour.

## 3. Hiérarchie des assets (MESURÉ par catalogue : 72 assets)
| Classe | Rôle | Niveau de détail | Exemples |
|---|---|---|---|
| Héros | manipulé, vu en gros plan, porte l'histoire | très élevé, lisible en macro, plusieurs états | chronomètre, fiche P-618 (V01) ; voitures, dashcam (V02) ; porte, billet (V03) ; chêne, panneau, flèche (V04) ; charrette (V05) |
| Secondaire | clairement visible, situe l'action | élevé | porte de cellule, dépanneuse, train, supérette |
| Dressing | densité et crédibilité | moyen | néons, fenêtres à barreaux, bannières, lanternes, cadres, post-it |
| Fond | profondeur | faible (masses) | campagne en damier, montagnes, coursives, gratte-ciel |
| Effet transitoire | matérialise un événement | — | fissures, billets, poussière, étincelles |

**Règle observée** : le détail est **concentré sur l'objet héros** (macro V05, gros plan V01). Le fond est fait de grandes masses lisibles.

## 4. Textes dans le décor (4 vidéos sur 5)
Les faits et les repères sont **écrits sur des objets** :
- fiche de recette, nuancier, camion (V01) ;
- tampon PAID, compteur, HUD de dashcam (V02) ;
- logo « Lucky », panneaux de temps, « 50 FT », écran JACKPOT (V03) ;
- DAYS SINCE LAST CRASH, DON'T HIT THIS TREE, TREE TOWING CASH ONLY, YOUR SPEED 15, TARGET FIXATION (V04).

V05 n'en a aucun (cadre historique, INFÉRÉ).

## 5. Matières et micro-détails
- **Lisibles à 2-4 m** : joints de parpaing ou de pierre, rivets, étiquettes, grilles de néon, grain de bois, sillons de champ, strates de falaise.
- **Usure modérée** : asphalte avec traces et fissures colmatées (V04), épaves cabossées. Peu de saleté ; les surfaces restent nettes et colorées.
- **Végétation** : herbe 3D haute au premier plan quand la caméra est basse (V02 330, V04, V05) ; arbres en masses de feuilles séparées (V04).
- **Atmosphère** : brume légère au loin le jour (V05 vallée), brume dense à l'aube (V05), rayons volumétriques (V01, V03, V05), pluie (V02, V04, V05).

## 6. Le décor accumule l'histoire
- **V04** : terre retournée, puis épave, puis compteur, puis pile de pneus, puis flèche, puis dépanneuse, puis souche.
- **V02** : tas de billets, puis voiture accidentée qui fume.
- **V05** : sol défoncé par la gifle.
- Les objets ajoutés **restent** jusqu'à la fin (OBSERVÉ).

## 7. LOD et coût (RECOMMANDATION)
- Objet héros : géométrie et textures de macro, états successifs modélisés (charrette V05 : 9 états).
- Plan moyen : textures PBR scannées 1-2k, sans répétition visible.
- Fond : aplats texturés, arbres en instances simples, couches de brume pour séparer les plans.
- Foule : un gabarit instancié avec variantes d'accessoires.
- Un décor construit **pour être traversé** quand la caméra passe d'un lieu à l'autre (V01 salle commune → toit → campagne → autre prison).
