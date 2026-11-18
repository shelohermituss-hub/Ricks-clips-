# Mémoire et amélioration continue

## Deux niveaux de mémoire

### Mémoire globale (skill / dépôt)
Contient les pratiques réutilisables, correctifs validés, tests de non-régression, paramètres de rendu éprouvés et standards de finition.

### Mémoire locale (épisode)
Contient les défauts et décisions propres au film, les assets, les plans, les timecodes, les versions et les corrections locales.

## Format obligatoire d'une leçon
Chaque leçon comprend :
- identifiant stable ;
- problème observé et sévérité ;
- épisode, plan et timecode ;
- cause racine démontrée ou hypothèse clairement marquée ;
- correction appliquée ;
- fichiers touchés ;
- tests automatisés ;
- preuves visuelles avant/après ;
- risque de régression ;
- statut : proposed / tested / validated / rejected ;
- décision de promotion globale.

## Règles d'apprentissage
- Ne pas enregistrer une supposition comme vérité.
- Une correction locale ne devient globale qu'après test dans le contexte original et vérification de non-régression.
- Les leçons validées sont lues au début des films suivants.
- Si une ancienne erreur réapparaît, augmenter sa sévérité et créer une tâche de prévention dans le pipeline, pas seulement un correctif local.
- Conserver les anciennes versions des règles et les commits ; pas de réécriture silencieuse.
- Utiliser un registre structuré JSON ou YAML plus un journal lisible humainement.

## Cycle de correction
OBSERVE → LOG → DIAGNOSE → PROPOSE → PATCH → RENDER → COMPARE → TEST → VALIDATE → PROMOTE LESSON.

Les patches sûrs, réversibles et couverts par des tests peuvent être appliqués automatiquement. Les achats, accès privés, actions destructives ou changements créatifs majeurs nécessitent l'autorisation pertinente.
