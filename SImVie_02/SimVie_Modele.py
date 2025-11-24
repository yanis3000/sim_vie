# ------------------------------------------------------------
# SimVie_Modele.py
# ------------------------------------------------------------
import random, math
from SimVie_Neurone import SystemeNerveux
from SimVie_Odeur import Glande, Aliment, Nez

# ------------------------------------------------------------
# Données environnementales
# ------------------------------------------------------------
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def angle_relatif(src, cible):
    """Retourne l’angle relatif entre la créature et la cible (en degrés)."""
    dx = cible[0] - src[0]
    dy = cible[1] - src[1]
    return math.degrees(math.atan2(dy, dx))



# ------------------------------------------------------------
# Créature : perçoit, agit, se nourrit
# ------------------------------------------------------------
class Creature:
    def __init__(self, position, taille):
        self.position = position
        self.taille = taille
        self.orientation = random.uniform(0, 360)
        self.vitesse = 20
        self.energie = 100
        self.narines = Nez(self.taille, random.uniform(0.8, 1.2), self.position, self.orientation)
        self.cerveau = SystemeNerveux(self.narines.capteur.ganglion)

        self.envie_reproduction = random.randint(10, 100)
        self.glande = Glande(self.envie_reproduction, self.position)

    # --- Olfaction directionnelle ---
    def percevoir(self, aliments, glandes):
        self.narines.sentir(aliments, glandes, self.glande)

    # --- Comportement global ---
    def agir(self):
        """
        Boucle perception-action de la créature.
        Elle perçoit les odeurs, ajuste son orientation, se déplace,
        consomme de l'énergie, et interagit avec les aliments.
        """
        # --- 1. PERCEPTION SENSORIELLE ---
        # Le cerveau reçoit deux entrées : intensité olfactive gauche/droite (0 à 1)

        stimuli_nourriture = [self.narines.hemi_nourriture_gauche, 
                   self.narines.hemi_nourriture_droite]
        
        stimuli_pheromone = [self.narines.hemi_pheromone_gauche, 
                   self.narines.hemi_pheromone_droite]

        # --- 2. TRAITEMENT NEURONAL ---
        # Le système nerveux interne traite les signaux sensoriels
        # et produit une activation motrice globale (de 0 à 1)

        activation = self.cerveau.cycle(self, stimuli_nourriture, stimuli_pheromone)
        print(activation[0], activation[1])

        # # --- 3. ORIENTATION ---
        # # Différence gauche-droite → rotation vers le côté le plus odorant
        # delta_orientation = (nour_droite - nour_gauche) * 8
        # # Ajout d'un léger bruit aléatoire pour éviter la synchronisation des trajectoires
        # self.orientation += delta_orientation + random.uniform(-1, 1)

        # # --- 4. DÉPLACEMENT ---
        # # L’intensité de mouvement dépend de l’activation moyenne (moyenne des deux narines)
        # intensite = max(0.05, (nour_gauche + nour_droite) / 2)
        # angle = math.radians(self.orientation)
        # dx = self.vitesse * intensite * math.cos(angle)
        # dy = self.vitesse * intensite * math.sin(angle)
        # self.position = (self.position[0] + dx, self.position[1] + dy)

        # # --- 5. MÉTABOLISME ---
        # # Chaque déplacement consomme de l'énergie.
        # # Ici, on modélise une perte de base (0.05) + une dépense proportionnelle à l’activité.
        # self.energie -= 0.05 + (0.2 * intensite)
        # if self.energie < 0:
        #     self.energie = 0

        # # --- 6. INTERACTION AVEC L’ENVIRONNEMENT ---
        # # Si la créature touche un aliment, elle le consomme.
        # for a in aliments[:]:
        #     if distance(self.position, a.position) < (self.taille + a.taille):
        #         self.manger(a, aliments)

    def manger(self, aliment, aliments):
        self.energie = min(100, self.energie + aliment.valeur_nourriture)
        aliments.remove(aliment)

# ------------------------------------------------------------
# Modèle général
# ------------------------------------------------------------
class Modele:
    def __init__(self, controleur, largeur_terrain, hauteur_terrain):
        self.controleur = controleur
        self.largeur_terrain = largeur_terrain
        self.hauteur_terrain = hauteur_terrain
        self.aliments = []
        self.creatures = []
        self.glandes = []
        self.creer_environnement(10, 1)

    def creer_environnement(self, nb_aliments, nb_creatures):
        for _ in range(nb_aliments):
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            self.aliments.append(Aliment(pos, random.randint(10, 100)))
        for _ in range(nb_creatures):
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            c = Creature(pos, random.randint(15, 40))
            self.creatures.append(c)
            self.glandes.append(c.glande)

    def mise_a_jour(self):
        for c in self.creatures:
            c.glande.emettre_pheromones(c.envie_reproduction)
            c.percevoir(self.aliments, self.glandes)
            c.agir()

    def reinitialiser_simulation(self, params):
        random.seed(params["seed"])
        self.largeur = params["largeur"]
        self.hauteur = params["hauteur"]
        self.aliments = []
        self.creatures = []
        self.creer_environnement(params["nb_aliments"],params["nb_creatures"])