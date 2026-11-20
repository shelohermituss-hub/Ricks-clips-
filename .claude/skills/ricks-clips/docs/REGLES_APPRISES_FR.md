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
9. **Vérifier que la reconstruction a réussi avant de lancer un rendu** : chercher `Traceback` **et** `SyntaxError` dans le journal, et regarder l'heure du fichier de scène. (Problème : une heure de rendu sur d'anciennes scènes parce qu'une faute de frappe avait fait échouer la construction sans bruit.)
10. **Annoncer les durées à partir d'une mesure**, pas d'une impression. Mes estimations à l'œil ont été fausses plusieurs fois.
11. **Les calculs longs tournent en arrière-plan**, avec un journal et un marqueur de fin ; pendant ce temps on documente ou on prépare la suite.

## 3. Environnement cloud, accès, secrets

12. **Première chose à faire dans une nouvelle session** : vérifier l'environnement (bonne version de Blender, hôtes réseau autorisés, clés enregistrées) et restaurer les fichiers non versionnés avec un script unique et relançable. (Problème : 40 minutes perdues sur un environnement mal préparé.)
13. **Les clés ne passent jamais par la discussion ni par un fichier** : elles sont enregistrées comme secrets réseau de l'environnement. Les scripts qui attendent une variable reçoivent une valeur factice.
14. **Quand un hôte est bloqué, le demander proprement** (la liste exacte des hôtes, une fois), ne pas contourner.
15. **Les gros fichiers téléchargés restent hors Git** (ignorés), avec un journal qui dit d'où ils viennent et sous quelle licence, pour pouvoir les retélécharger.
16. **Jamais supprimer une machine louée avant d'avoir récupéré et vérifié ses résultats.** (Problème : 92 minutes de calcul perdues.)
17. **Un outil Python lancé par Blender n'a pas les mêmes modules que le Python du système** : le dessin d'images (PIL) se fait hors de Blender.

## 4. Blender 5 : pièges déjà rencontrés

18. Pas de ciel `NISHITA` ; le compositeur est `scene.compositing_node_group` avec un nœud de sortie de groupe ; les réglages de plusieurs nœuds (halo, balance des couleurs) sont des **entrées**, pas des propriétés ; les actions sont en couches.
19. `resolution_percentage` est un entier.
20. Un cylindre entièrement lissé s'ombre comme une boule : marquer les arêtes vives.
21. Un matériau qui multiplie par un attribut de couleur rend **noir** sur un objet qui n'a pas cet attribut.
22. Un volume de brume trop petit montre son bord ; un volume ou des cartes de rayons à faible qualité donnent du grain : préférer la passe de brume et le compositeur.
23. Un commentaire `#` au milieu d'une ligne à plusieurs instructions neutralise tout ce qui suit.
24. Deux rendus de la même image doivent donner les mêmes octets : pas de date ni de temps de rendu écrits dans l'image.

## 5. Honnêteté du compte rendu

25. **Dire en première ligne ce qui n'est pas fait.** Ne jamais annoncer « décors faits » si la finition (matières, lumière, étalonnage) ne l'est pas. Un aperçu d'animation s'annonce comme tel.
26. **Distinguer « corrigé dans le code » de « vérifié en image ».** Seul le second compte comme fait.
27. **Lister soi-même ce qui est encore faux** à côté de chaque image envoyée, avant que CB ait à le faire.
28. **Donner les chiffres mesurés tels quels**, y compris quand ils échouent.

## 6. Préférences de travail de CB

- Réponses en **français**, langage simple, sans jargon.
- **Travailler seul** : pas d'agents en parallèle (coût).
- **Pas de demande de fusion (PR)** sans demande explicite.
- **Cycles** est le moteur de rendu.
- Quand CB dit « mode automatique », avancer sans poser de questions jusqu'au bout, puis rendre compte honnêtement.

---

### Ce que ce fichier ne contient pas

Les règles de **style** (couleurs, type de ciel, trait, matières) et les règles de **construction des plans, des décors, des personnages et de l'animation** ne sont pas ici : elles seront reconstruites dans le nouveau dépôt.
