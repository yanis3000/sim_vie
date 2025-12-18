# Simulation de vie cellulaire
#### Projet créé par Mario Laframboise, Guillaume Foisy et Yanis Boumazouzi 

## Fonctionnalités
### Manipulations humaines dans l'interface
<!-- L'interface est presque la même que celle de départ. C'est surtout le modèle qui a été travaillé. -->

Nous avons conservé l'interface utilisateur de base et avons pris la décision d'ajouter des fonctionnalités supplémentaires pour une meilleure expérience. Nous avons rajouter :

- Une case `Afficher les phéromones` pour afficher leur émission par les créatures femelles.
- Un onglet `Jauges` qui se met à jour dynamiquement lorsqu'on clique sur une créature comprenant :
    - L'identifiant de chacune des créatures, 
    - Leur état : [`Disponible`, `Manger`, `Reproduction`, `Dormir`], 
    - Leur jauge de faim,
    - Leur jauge d'énergie,
    - Leur envie de reproduction.

### Opérations effectuées par l'ordinateur
#### Sprint 1 : 
Le modèle est la partie dans laquelle nous avons été les plus impliqués. Nous avons fait beaucoup de modifications par rapport au code de base. Nous avons repensé plusieurs choses dont :
- La classe `Glande` pour gérer la jauge d'envie des créatures et implémenter l'émission des phéromones
- Notre système d'odorat a été développé en se basant sur la biologie. Nous avons simuler un système de olfactif en créant :
    - Un classe `Nez` qui stocke les stimulis, 
    - Un classe `Capteur` qui réagit aux stimulis et se connecte aux ganglions,
    - Un classe `GanglionOlfactif` pour laisser passer ou bloquer les stimulis.
- On a conçu une classe `Pattes` permettant à ladite créature de s'orienter ou de se diriger.
- On a restructuré la classe `Neurone` pour qu'elle soit plus réaliste.
- Ajout des classes précédemment mentionnées dans `Créature`.
- On a revu le calcul de l'orientation en fonction des neuronnes motrices.
- Distinction des stimulis de gauche et de droite pour l'activation des capteurs.
- On a détecter la position de la nourriture et augmenter le niveau d'énergie.

#### Sprint 2 : 
Dans cette partie du projet, notre attention s'est davantage portée sur la créature en elle-même plutôt que sur les éléments qui la compose.
- Dans la classe `Glande`, nous avons ajouter les glandes aux neuronnes et dans le calcul de déplacement. Il y a aussi distinction entre phéromones détectées à droite et à gauche.
- Dans `Glangion`, nous avons ajouter le rôle de gestion de stimuli, soit on bloque ou on laisse passer les signaux.
- Nous avons fait plusieurs expérimentations neuronales.
- La créateur peut effectuer quelques actions qui prennent chacun leur temps tels que :
    - `Manger` pour que celle-ci soit rassasié et qu'elle ne meurt pas.
    - `Reproduire` afin d'assurer la survie de l'espèce.
    - `Dormir` pour récupérer de l'énergie.
- Nous arrivons à faire apparaiître de la nourriture sur la carte de manière périodique pour ne pas en manquer.

Dans la vue, nous avons réussi à faire plusieurs choses aussi notamment : 
- Ajouter les infos de l'ADN dans l'onglet `Créature`
- Faire apparaître les œufs dans la vue
- Changer la couleur des créatures selon leur genre
- Changer la couleur des créatures lorsqu'ils vieillissent
- Corriger les ronds qui apparaissent quand c'est décoché
