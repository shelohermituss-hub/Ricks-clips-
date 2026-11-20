# Règles apprises — à donner à Claude dans le nouveau dépôt

**But de ce fichier.** Ce sont les règles de méthode apprises en construisant le skill RicksClips (films courts en Blender, décors 3D + personnages 2D en cartes). Elles ne décrivent pas un style : elles décrivent **comment travailler** pour aller vite, ne pas refaire deux fois la même erreur, et ne pas présenter comme « fait » ce qui ne l'est pas. Chaque règle vient d'un problème réel ; le problème est indiqué entre parenthèses.

**Comment l'utiliser.** Claude lit ce fichier en entier au début de chaque session, avant de toucher au code. Quand une règle ne s'applique plus, on la retire ; on ne l'ignore pas en silence.

---

## 1. La règle mère : chaque problème résolu devient une règle

1. **Un problème résolu se documente dans la même séance** : ce qui s'est passé, la cause réelle, la correction, et **un garde-fou** (contrôle automatique, test, ligne dans un modèle) qui empêche qu'il revienne. Une leçon sans garde-fou revient.
2. **Chaque correction de CB devient une règle écrite**, avec sa phrase d'origine entre guillemets, la date, et le fichier de code qui l'applique. Les corrections reviennent par familles : relire la liste avant chaque plan.
3. **Deux fichiers, deux rôles** : un journal des corrections de CB (ce qu'il veut) et un registre des leçons techniques (problème → cause → correction → test → preuve). Les deux sont dans le dépôt, pas seulement dans la mémoire de la session.
4. **Commit et push après chaque étape** : le conteneur cloud est effacé après inactivité ; tout ce qui n'est pas poussé est perdu.

## 2. Rendu : ce qui fait gagner le plus de temps

5. **Jamais le film entier pour corriger.** On corrige sur **2 à 4 images clés par plan**. Le plan en mouvement ne se calcule qu'une fois les images clés validées, et le film entier une seule fois, à la fin. (Problème : 64 minutes de calcul pour 3,2 s de film, puis tout à refaire.)
6. **Une seule image quand on règle un seul point** (cadrage, couleur d'un sol) : 4–5 minutes au lieu de 20.
7. **Processeur = images clés et aperçus rapides. GPU loué = vrais rendus**, uniquement avec l'accord de CB et un plafond de dépense. Mesurer le temps GPU sur une image avant d'annoncer un coût.
8. **Ne recalculer que ce qui a changé** : un aperçu saute les images déjà calculées ; on supprime seulement les images du plan modifié.
9. **Alléger la scène avant d'attendre** : végétation en géométrie seulement près de la caméra (ailleurs une texture), textures réduites à 1–2 K, objets répétés en instances. (Problème : 100 000 touffes d'herbe = 5 minutes par image ; 50 656 objets après un import.)
10. **Vérifier que la reconstruction a réussi avant de lancer un rendu** : chercher `Traceback` **et** `SyntaxError` dans le journal, et regarder l'heure du fichier de scène. (Problème : une heure de rendu sur d'anciennes scènes parce qu'une faute de frappe avait fait échouer la construction sans bruit.)
11. **Annoncer les durées à partir d'une mesure**, pas d'une impression. Mes estimations à l'œil ont été fausses plusieurs fois.
12. **Les calculs longs tournent en arrière-plan**, avec un journal et un marqueur de fin ; pendant ce temps on documente ou on prépare la suite.

## 3. Méthode de construction d'un plan

13. **Analyser avant de construire** : découpage de la référence image par image (10 i/s autour des moments importants), mots de la narration avec leur numéro d'image, fiche du plan (décor, personnages, objets, caméra, effets, son).
14. **Un plan se construit contre une image cible.** Copie : l'image de la référence. Film original : une **image modèle** de même type prise dans une référence (même valeur de cadre, hauteur de caméra, taille du personnage, densité du décor, direction de lumière). Sans image cible, on juge « à l'idée » et on dérive. (Problème : trois looks inventés pour un film original, tous refusés ; la copie, elle, converge.)
15. **Toujours montrer côte à côte** : référence en haut, notre image en dessous, même instant. C'est ce qui rend l'écart lisible, pour CB comme pour Claude.
16. **Mesurer, pas regarder** : luminosité, saturation et contraste de chaque image clé contre la référence (outil de comparaison), avec une tolérance. Les couleurs se **prélèvent à la pipette** sur la référence (sol, herbe, ciel, pierre), elles ne s'inventent pas.
17. **Relever l'angle de caméra de chaque image clé** (plongée, biais, contre-plongée) et le relief (colline, route en S) avant de poser la caméra. Tout cadrer de face est le défaut par défaut : le refuser.
18. **Ne détailler que ce que la caméra du plan voit bien.** Les lointains sont simples mais riches (vrai relief, variations de teinte) ; le premier plan est détaillé.
19. **Les coupes viennent d'une mesure**, pas d'une lecture rapide : une coupe est un pic d'une image, un mouvement de caméra est une rampe sur plusieurs images. Un plan qui continue la prise précédente se construit par-dessus elle. (Problème : une « coupe » notée dans l'analyse n'existait pas.)
20. **Valider un plan avant d'habiller les autres.** On ne propage un look à 15 plans qu'après validation de CB sur un seul.
21. **Ne pas changer de direction à chaque remarque.** Une remarque corrige un point ; elle ne remet pas tout le look à zéro. Si la direction doit vraiment changer, le dire et demander.

## 4. Objets, décors, personnages

22. **Véhicules, machines, outils, bâtiments remarquables = toujours de vrais modèles** (bibliothèques d'assets), jamais des boîtes assemblées. Choisir sur vignettes ; vérifier la licence ; noter l'auteur pour les crédits.
23. **Regarder le modèle avant de l'utiliser** : taille, orientation, noms des pièces et des matériaux (un rendu rapide + la liste des pièces). La pièce qui doit bouger doit être séparée, avec son origine au bon endroit. (Problème : une roue qui tournait autour du mauvais point ; une peinture appliquée à la mauvaise voiture.)
24. **Les matériaux d'un modèle importé se prennent sur ses propres objets**, jamais par nom global.
25. **Chaque personnage est fait pour son rôle** : une planche de personnages par film, assemblée depuis la bibliothèque (tenue, coiffure, accessoire, couleurs). Vérifier le dessin obtenu avant de l'utiliser en 3D.
26. **Vérifier un geste sur le dessin avant de le placer** : un nom de mouvement ne dit pas ce que fait le mouvement.
27. **Les personnages restent nets et clairs** : cartes surtout éclairées par leur propre lumière, pas de flou d'objectif sur elles, taille suffisante dans le cadre.
28. **Un sol clair se tient avec la lampe, pas avec l'exposition.** Baisser l'exposition assombrit aussi le ciel et les personnages.

## 5. Continuité et animation (contrôles avant tout rendu)

29. **Tout arrive par une action** : rien n'apparaît, ne disparaît, ne se téléporte ni ne change de taille à l'image. Un contrôle automatique tourne sur chaque plan **avant** le rendu et refuse de rendre en cas d'échec.
30. **Les conséquences restent** : trous percés, objets posés, fumée, débris.
31. **Toute valeur animée est une fonction du numéro d'image seulement** ; les valeurs aléatoires sont tirées une fois par objet, avant la boucle. (Problème : des feuilles qui se téléportaient ; des images différentes selon l'ordre de calcul.)
32. **La portée de la caméra couvre le décor** (plan de coupe lointain réglé large). (Problème : les champs s'arrêtaient net à l'horizon.)
33. **La caméra ne s'arrête jamais** : légère dérive sur chaque plan.

## 6. Environnement cloud, accès, secrets

34. **Première chose à faire dans une nouvelle session** : vérifier l'environnement (bonne version de Blender, hôtes réseau autorisés, clés enregistrées) et restaurer les fichiers non versionnés avec un script unique et relançable. (Problème : 40 minutes perdues sur un environnement mal préparé.)
35. **Les clés ne passent jamais par la discussion ni par un fichier** : elles sont enregistrées comme secrets réseau de l'environnement. Les scripts qui attendent une variable reçoivent une valeur factice.
36. **Quand un hôte est bloqué, le demander proprement** (la liste exacte des hôtes, une fois), ne pas contourner.
37. **Les gros fichiers téléchargés restent hors Git** (ignorés), avec un journal qui dit d'où ils viennent et sous quelle licence, pour pouvoir les retélécharger.
38. **Jamais supprimer une machine louée avant d'avoir récupéré et vérifié ses résultats.** (Problème : 92 minutes de calcul perdues.)
39. **Un outil Python lancé par Blender n'a pas les mêmes modules que le Python du système** : le dessin d'images (PIL) se fait hors de Blender.

## 7. Blender 5 : pièges déjà rencontrés

40. Pas de ciel `NISHITA` ; le compositeur est `scene.compositing_node_group` avec un nœud de sortie de groupe ; les réglages de plusieurs nœuds (halo, balance des couleurs) sont des **entrées**, pas des propriétés ; les actions sont en couches.
41. `resolution_percentage` est un entier.
42. Un cylindre entièrement lissé s'ombre comme une boule : marquer les arêtes vives.
43. Un matériau qui multiplie par un attribut de couleur rend **noir** sur un objet qui n'a pas cet attribut.
44. Un volume de brume trop petit montre son bord ; un volume ou des cartes de rayons à faible qualité donnent du grain : préférer la passe de brume et le compositeur.
45. Un commentaire `#` au milieu d'une ligne à plusieurs instructions neutralise tout ce qui suit.
46. Deux rendus de la même image doivent donner les mêmes octets : pas de date ni de temps de rendu écrits dans l'image.

## 8. Honnêteté du compte rendu

47. **Dire en première ligne ce qui n'est pas fait.** Ne jamais annoncer « décors faits » si la finition (matières, lumière, étalonnage) ne l'est pas. Un aperçu d'animation s'annonce comme tel.
48. **Distinguer « corrigé dans le code » de « vérifié en image ».** Seul le second compte comme fait.
49. **Lister soi-même ce qui est encore faux** à côté de chaque image envoyée, avant que CB ait à le faire.
50. **Donner les chiffres mesurés tels quels**, y compris quand ils échouent.

## 9. Préférences de travail de CB

- Réponses en **français**, langage simple, sans jargon.
- **Travailler seul** : pas d'agents en parallèle (coût).
- **Pas de demande de fusion (PR)** sans demande explicite.
- **Cycles** est le moteur de rendu.
- Quand CB dit « mode automatique », avancer sans poser de questions jusqu'au bout, puis rendre compte honnêtement.

---

### Ce que ce fichier ne contient pas

Les règles de **style** (couleurs, type de ciel, trait, matières) ne sont pas ici : elles ont changé plusieurs fois et ne sont pas stabilisées. Elles devront être reconstruites dans le nouveau dépôt en reproduisant les vidéos de référence, avec la méthode des sections 3 et 4.
