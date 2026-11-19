# Bible de style — la référence quand il n'y a pas de vidéo de référence

**Version 1 (19/11).** Construite à partir de la vidéo de CB « He Crashed His Own Car For Science » (mesures : `references/crashed_car/ANALYSE_FR.md`, `ref_measures.json`) et des leçons des plans 1 et 2.

**Chaque nouvelle vidéo de référence analysée enrichit cette bible.** Les mesures sont ajoutées au tableau §9, et les règles communes à toutes les vidéos remplacent les règles tirées d'une seule.

Toute nouvelle vidéo est planifiée **contre cette bible** (`tools/plan_check.py` vérifie qu'elle est citée). Un écart volontaire est écrit dans le plan avec sa raison.

## 1. Format et rythme (mesurés)

| | Cible |
|---|---|
| Format | 1080×1920, 9:16, 30 i/s |
| Durée | 45 à 75 s |
| Narration | 3,3 à 3,6 mots/s, **sans trou** : aucune pause de plus de 0,4 s |
| Événements | **un toutes les 0,9 s environ** (11,5 pics d'action par 10 s). Il se passe toujours quelque chose : action, réaction, mouvement de caméra, effet. |
| Lieux | beaucoup de lieux « légers » : **11 en 51 s**. Chaque lieu est construit **pour le cadre**, seulement ce que la caméra voit. |
| Coupes franches | environ 1 par 5 s, seulement sur un saut de lieu ou de temps |
| Autres transitions | **par le mouvement** : balayage flou, traversée d'un objet, fondu court de 6 images, image qui devient une photo |
| Boucle | la dernière image renvoie à la première |

## 2. Caméra : elle ne s'arrête jamais

- Mouvement médian mesuré : **41,8**. Notre première démo n'atteignait que 14,7.
- Chaque plan combine un mouvement nommé (poussée, glissement, orbite, grue, suivi, panoramique filé) et une **dérive façon caméra à l'épaule** sur chaque image (`street.handheld`).
- Caméra basse près des objets (≈ 1,2 m), grand angle (champ de 50 à 60°) sur les gros plans, plans larges de côté pour situer l'action.
- Elle **suit l'action** : quand un personnage saute ou qu'une voiture passe, la caméra l'accompagne.
- Flou de mouvement sur les mouvements rapides, profondeur de champ légère sur les gros plans.

## 3. Monde

- **3D cartoon de qualité série TV** : formes douces et arrondies, proportions un peu exagérées.
- **Surfaces réelles** : sol et grandes surfaces en **scans PBR CC0** (Poly Haven, ambientCG), jamais une couleur plate avec du bruit.
  - Teinte gardée dans la palette.
  - Taches, traces et usure ajoutées par-dessus.
- **Végétation** : arbres en boules de feuillage stylisées, herbe en vrais brins denses au premier plan, fleurs.
- **Densité** : un décor n'est jamais vide.
  - Au moins 4 accessoires racontent le lieu : piles de pneus, jerrycans, outils, panneaux.
  - Des inscriptions intégrées au décor : sponsors, panneaux, étiquettes.
- **Objets brillants** (voitures, casques, métal peint) : vernis complet (coat 1,0, rugosité 0,03) et reflets d'un **vrai ciel HDRI**, visible uniquement dans les reflets.

## 4. Lumière et ombres

- **Soleil franc et dur** : angle 1,5°, énergie ≈ 6, de face-côté pour éclairer les visages.
- **Ombres portées nettes** des structures (toits, portiques, arbres) dessinées au sol.
- Ciel d'appoint bas (≈ 0,4) : les ombres restent lisibles et colorées, jamais noires.
- **Ombre de contact** sous chaque personnage et chaque objet posé.
- Ciel bleu profond et gros nuages blancs. Au moins une ambiance différente par vidéo : crépuscule violet, intérieur à lampe chaude, nuit.
- Image : Standard + « Medium High Contrast », saturation élevée mais pas uniforme, contours nets, pas de grain.

## 5. Personnages

- **Stick figures 2D** de notre distribution (cartes éclairées dans le monde 3D) : tête ronde blanche, trait noir, accessoires dessinés.
- **Un personnage = une carte = un dessin du début à la fin.** On ne remplace jamais un personnage par un autre à l'écran.
- **Toutes ses actions dans la même vue** : la transition entre deux mouvements ne fonctionne que dans une même vue.
- Jeu à la frame, avec :
  - anticipation, action nette, retour au repos ;
  - un visage qui change sur le mot ;
  - une goutte de sueur, des étoiles ou une veine quand l'émotion le demande.
- Les objets tenus (casque, outil) sont en **3D** et suivent la tête et les mains **mesurées sur le dessin** (`tools/card_anchors.py`).

## 6. Actions, réactions et conséquences

- **Tout passe par une action** : rien n'apparaît, ne disparaît, ne saute ni ne rétrécit à l'écran.
- **Chaque action a ses réactions**, prises dans le catalogue `library/reactions/reactions.json` :
  - des réactions visibles : éclaboussure, poussière, débris, secousse ;
  - des **conséquences qui restent** : voiture mouillée, carrosserie enfoncée, traces au sol, objet cassé ;
  - des micro-animations : une antenne qui vibre, un enjoliveur qui roule, une respiration ;
  - un bruitage.
- Exemple : une voiture passe dans une flaque.
  - Des gerbes partent de chaque roue.
  - Des gouttes retombent en anneaux.
  - La surface ondule.
  - Le bas de caisse devient mouillé (plus sombre et plus brillant) et goutte.
  - Des traces humides s'effacent sur la route.
  - La flaque se vide un peu.
  - On entend le splash.

## 7. Effets visuels

- Effets stylisés et opaques plutôt que des volumes coûteux : nuages de poussière en boules, flammes cartoon, étincelles.
- Toujours **déclenchés par une action** et **déterministes** (graine fixe).
- Particules en avant-plan qui passent devant l'objectif (confettis, poussière, gouttes) pour la profondeur.

## 8. Son

- Voix continue.
- Musique douce **permanente** environ 7,6 dB sous la voix.
- Une ambiance par lieu : foule, vent, rue, intérieur.
- **Un bruitage sur chaque action et chaque réaction.**
- Mixage final à −14 LUFS.

## 9. Mesures par vidéo de référence (à compléter)

| Vidéo | Durée | Mots/s | Mouvement médian | Lieux | Coupes | LUFS | Saturation médiane |
|---|---|---|---|---|---|---|---|
| crashed_car (CB) | 51,5 s | 3,44 | 41,8 | 11 | 10 | −13,9 | 0,405 |

**Règle commune** = vraie dans toutes les vidéos analysées. **Variante** = propre à une vidéo, gardée comme option.
