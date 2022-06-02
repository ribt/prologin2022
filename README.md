# Prologin 2022

## Présentation

Prologin est un concours d'informatique organisé tous les ans depuis trente ans et ouvert aux étudiants de moins de 21 ans. Les premières sélections se font en ligne, suivies par une épreuve de qualification au niveau régional et les 100 premiers sont conviés à la finale à Paris. Lors de cette finale, chacun dispose de 36 heures pour coder une intelligence artificielle jouant à un jeu multijoueur.

Le sujet de la finale est [dispo ici](sujet.pdf). Pour résumé, c'est un jeu à deux joueurs, tour par tour (200 tours par joueur). Chaque joueur possède deux files de canards. Le jeu se joue sur une carte 2D (40x40 cases) où sont disposés des papys qui déposent tous les 5 tours une miche de pain à leurs pieds, des obstacles (buissons et barrières) et des nids. Le but est de rapporter un maximum de pains dans les nids, le nombre de points gagnés à chaque tour est égal au nombre de pains déposés dans les nids **au carré**. À chaque tour, chaque file de canards disposent de 5 points d'action. Avancer dans une direction coûte un point et agrandir la file d'un canard coûte 3 points. Il faut trois canards pour porter une miche de pain. Il est également possible de poser un buisson (sur une des cases constructibles) contre 3 points de score. De plus, des trous sont disposés sur la carte, permettant d'accéder au niveau souterrain qui est intégralement constitué de terre mais chaque joueur peut creuser la case qu'il souhaite gratuitement à chaque tour de jeu.

On comprend bien que pour gagner un maximum de points, il faut faire des files de canards gigantesques pour gagner un nombre très important de points. Cependant si la maman canard (celle qui dirige la fille) se prend un obstacle, toute la file disparaît et une file de longueur 5 réapparaît dans une des cases de spawn. Le jeu s'apparente donc légèrement à un Snake.

## Ma stratégie

Le code de mon champion (en Python) est [dispo ici](Champion.py) tel que je l'ai soumis (donc allègrement commenté).

Voici comment fonctionne mon programme :

- Au début, chaque file se déplace très vite (5 déplacements par tour) pour conquérir deux nids (si possible).
- Ensuite, chaque file grossit d'un canard par tour, jusqu'à atteindre la taille de 21 canards (et donc pouvoir porter 7 pains).
- Chaque file va ensuite vers le pain le plus proche ou le nid le plus proche si l'inventaire est plein.
- S'il reste des points d'action à la fin du tour, choisir une case au hasard et se diriger vers elle.



Cette stratégie a été choisie et codée assez rapidement et m'a permis de gagner de nombreux matchs (mon champion s'est classé 2e sur tous les tournois intermédiaires dès la fin du jour 1).

Le soir du jour 1, en discutant avec un autre finaliste, on se demande s'il est possible de poser un buisson sur une case contenant un pain. L'idée retient mon attention ! Si c'est possible, cela peut être intéressant car la plupart des champions doivent se diriger vers le pain le plus proche et utiliser la fonction `trouver_chemin` qui fait partie de l'API... et ne vérifie pas que la case d'arrivée est un obstacle ! Mes tests montrent que c'est possible donc dès que mon champion a suffisamment de points et qu'un pain est sur une case constructible, il pose un buisson par tour sur un des pains (choisi au hasard) dans la limite de 10 buissons posés. C'était très amusant de voir les replays :grin:

J'ai ensuite créé une map obligeant à utiliser les tunnels (map qui a été tout de suite ajoutée dans les tournois !) pour essayer de trouver une stratégie. Après plusieurs essais, j'adopte la stratégie suivante : Si une troupe détecte qu'elle est de taille 1 (c'est-à-dire qu'elle vient de respawn) elle calcule un chemin souterrain entre le trou le plus près de la position actuelle et le trou avec le plus de papys autour. À chaque tour de jeu, le joueur creuse alternativement les cases à creuser choisies par une troupe et l'autre.

Enfin, pendant les dernières heures, j'ai voulu utiliser les buissons de façon beaucoup plus agressive. Si mon score est supérieur à 100, et que la tête d'une maman adverse peut être entourée en posant un, deux ou trois buissons alors je les pose.

### Time out

Durant les tournois, mon champion atteignait parfois la limite de 1 seconde d'exécution le forçant à quitter la partie et laisser l'autre joueur finir seul. En rejouant les mêmes matchs manuellement, je n'atteignais pas la limite. J'ai rapidement compris que c'était la partie `S'il reste des points d'action à la fin du tour, choisir une case au hasard et se diriger vers elle.` de ma stratégie qui posait problème. En effet, je choisissais une case totalement au hasard puis je calculais `trouver_chemin` de la position de la maman à cette case et je suivais le chemin si la fonction ne retournait pas une liste vide, sinon je tirais une nouvelle case au hasard. Cela fonctionne très bien et donne l'impression que la file de canard arrive à se sortir de toutes les situations. Cependant, la fonction `trouver_chemin` est un peu coûteuse donc je vais devoir définir un nombre maximum d'appels. Mais si je définis cette constante en lançant les matchs moi-même, elle sera faussée. Il faut calculer cela pendant un tournoi.

J'ai donc tout simplement ajouté trois lignes de code à mon champion pour print le temps d'exécution de la fonction `jouer_tour` pour chaque tour. Ainsi en lançant manuellement les mêmes matchs que ceux du tournoi, je pouvais comparer les écarts de temps de calcul. J'ai ainsi constaté qu'une seconde de temps réel permet de faire 4 à 5 fois moins de choses en mode tournoi. J'ai ainsi fixé une limite de temps à 0,2 seconde durant toute la suite de mes tests pour m'assurer de ne jamais atteindre le time out en tournoi.


### Bilan

Ma stratégie est très simple et absolument pifométrique. La taille de 21 canards et la limite de 2 nids ont été choisies complètement arbitrairement. Mon champion faisant d'excellents résultats à tous les tournois, je n'ai pas pris le temps d'essayer d'ajuster ces constantes.

Les fonctionnalités ajoutées ensuite sont probablement négligeables, sauf peut-être les tunnels qui permettent de se tirer de certaines maps.

Le fait d'induire de l'aléatoire fait que mes files de canards se prenaient un obstacle de temps en temps. Cela arrivait une vingtaine de fois dans les 200 tours. Je pense que cela n'est pas dramatique, au contraire même. Ainsi, sur une carte farfelue créée par les orgas sadiques mon champion ne tournera pas en bourrique puisqu'il va respawn de temps en temps et probablement se comporter différemment depuis ce nouveau point de départ.

La plupart des finalistes qui visaient un bon classement ont appliqué des algorithmes complexes. Beaucoup ont créé leur propre fonction pour chercher un chemin et supprimaient les cases menant à un cul de sac pour ne jamais s'y aventurer. Finalement, un algorithme basique fonctionne aussi bien (mon champion termine 4e), essentiellement car les orgas créent des cartes mettant volontairement à mal les stratégies algorithmiques les plus connues.

## Conseils

Ayant dépassé l'âge limite, je ne pourrai pas me présenter à l'édition 2023 de Prologin, mais je peux donner des conseils pour ceux qui veulent faire ce super concours !

Pour la finale, le plus important est de commencer par un programme très très simple qui marque plus que zéro point (ce qui n'est pas facile que ça). Cela permet de prendre en main l'API et si jamais vous ne parvenez pas à implémenter dans les temps la super stratégie à laquelle vous pensiez, vous pourrez soumettre votre premier champion et vous pourrez être surpris du résultat ! Vous pouvez également travailler par itération en ajoutant les fonctionnalités petit à petit pour que votre champion marque de plus en plus de points sans partir directement dans un programme de plusieurs centaines de lignes qui sera très dur à finir et déboguer en 36h.

Enfin, cette année, j'ai utilisé [git](https://git-scm.com/). C'est un outil créé pour versionner son code. C'est-à-dire créer des sauvegardes régulières et explicites. Cela est essentiellement utilisé sur des gros projets en équipe mais quand on est seul, qu'on a un seul fichier et que le projet dure 36h ça marche aussi :slightly_smiling_face:

Cela permet notamment de créer des "branches" qui sont des versions concurrentes de votre code que vous pouvez ensuite intégrer (ou non) dans votre code qui est dans la branche principale. En clair, ça évite de faire 250 copies du fichier en mettant l'heure dans le nom pour tester différentes stratégies.

Cela vous permet également d'accéder à [l'historique de développement de mon champion](https://github.com/ribt/prologin2022/commits/master/Champion.py) pour voir les étapes de développement.

## Conclusion

Merci aux orgas pour cette super finale (et pour la Nintendo Switch) ! Et bon courage à tous pour les prochaines éditions.