# ------------------------------------------------------------
# SimVie_Modele.py
# ------------------------------------------------------------
import random, math
from SimVie_Neurone import SystemeNerveux
from objects_olfactifs import Glande, Aliment
from organe_olfactif import Nez

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
        self.narines = Nez(self.taille, random.uniform(0.8, 1.2))
        self.cerveau = SystemeNerveux(self.narines.capteur.ganglion)

        self.envie_reproduction = random.randint(10, 100)
        self.glande = Glande(self.envie_reproduction, self.position)

        
    # --- Olfaction directionnelle ---
    def percevoir(self, aliments, glandes):
        self.narines.sentir(aliments, glandes, self.glande)

        # """
        # Retourne deux valeurs (gauche, droite) entre 0 et 1,
        # représentant l'intensité olfactive perçue sur chaque côté.
        # Simule une stéréoscopie olfactive simplifiée.
        # """
        # # --- Accumulateurs pour les deux "narines" ---
        # gauche, droite = 0.0, 0.0
        # g_gauche, g_droite = 0.0, 0.0

        # # --- Boucle sur chaque source d'odeur (aliment) ---
        # for a in aliments:
        #     # Distance euclidienne entre la créature et l'aliment
        #     d = distance(self.position, a.position)

        #     # Si l'aliment est dans la portée olfactive
        #     if d < (self.narines.portee_olfactive + a.rayon_senteur):
        #         # Calcul de l'angle absolu vers la source
        #         ang = angle_relatif(self.position, a.position)
        #         # Conversion en angle relatif à l'orientation du corps
        #         # (normalisation dans l'intervalle -180° à +180°)
        #         rel = (ang - self.orientation + 540) % 360 - 180

        #         # Intensité du signal olfactif : plus c’est proche, plus c’est fort
        #         # On ajoute +1 pour éviter une division par zéro
        #         odeur = a.valeur_nourriture / (d + 1)

        #         # Répartition stéréoscopique :
        #         # - Si la source est dans l’hémisphère gauche (-90° < angle < 0°)
        #         #   → accumulation sur le capteur gauche
        #         # - Si elle est à droite (0° < angle < 90°)
        #         #   → accumulation sur le capteur droit
        #         if -90 < rel < 0:
        #             gauche += odeur
        #         elif 0 <= rel < 90:
        #             droite += odeur

        # for g in glandes:
        #     if self.glande != g:
        #         d = distance(self.position, g.position)

        #         if d < (self.narines.portee_olfactive + g.rayon_senteur):
        #             ang = angle_relatif(self.position, g.position)
        #             rel = (ang - self.orientation + 540) % 360 - 180

        #             g_odeur = g.valeur_pheromone / (d + 1)
        #             if -90 < rel < 0:
        #                 g_gauche += g_odeur
        #             elif 0 <= rel < 90:
        #                 g_droite += g_odeur


        # # --- Normalisation du signal ---
        # # Le rapport /10 permet de limiter la saturation du capteur :
        # # un grand nombre de sources ou une très forte odeur reste borné à 1.0.
        # gauche = min(1.0, gauche / 10)
        # droite = min(1.0, droite / 10)
        # g_gauche = min(1.0, g_gauche / 10)
        # g_droite = min(1.0, g_droite / 10)

        # # Retourne le couple d’intensités olfactives (gauche, droite)
        # return {"aliments" : [gauche, droite], "phéromones" : [g_gauche, g_droite]}

    # --- Comportement global ---
    def agir(self, aliments, glandes):
        """
        Boucle perception-action de la créature.
        Elle perçoit les odeurs, ajuste son orientation, se déplace,
        consomme de l'énergie, et interagit avec les aliments.
        """
        # --- 1. PERCEPTION SENSORIELLE ---
        # Le cerveau reçoit deux entrées : intensité olfactive gauche/droite (0 à 1)

        self.percevoir(aliments, glandes)

        gauche, droite = self.narines.hemi_nourriture_gauche, self.narines.hemi_nourriture_droite
        g_gauche, g_droite = self.narines.hemi_pheromone_gauche, self.narines.hemi_pheromone_droite

        # --- 2. TRAITEMENT NEURONAL ---
        # Le système nerveux interne traite les signaux sensoriels
        # et produit une activation motrice globale (de 0 à 1)

        # activation = self.cerveau.cycle(self.narines.capteur.capteurs, self.narines.capteur.vomeronasal, stimuli)

        # --- 3. ORIENTATION ---
        # Différence gauche-droite → rotation vers le côté le plus odorant
        delta_orientation = (droite - gauche) * 8
        # Ajout d'un léger bruit aléatoire pour éviter la synchronisation des trajectoires
        self.orientation += delta_orientation + random.uniform(-1, 1)

        # --- 4. DÉPLACEMENT ---
        # L’intensité de mouvement dépend de l’activation moyenne (moyenne des deux narines)
        intensite = max(0.05, (gauche + droite) / 2)
        angle = math.radians(self.orientation)
        dx = self.vitesse * intensite * math.cos(angle)
        dy = self.vitesse * intensite * math.sin(angle)
        self.position = (self.position[0] + dx, self.position[1] + dy)

        # --- 5. MÉTABOLISME ---
        # Chaque déplacement consomme de l'énergie.
        # Ici, on modélise une perte de base (0.05) + une dépense proportionnelle à l’activité.
        self.energie -= 0.05 + (0.2 * intensite)
        if self.energie < 0:
            self.energie = 0

        # --- 6. INTERACTION AVEC L’ENVIRONNEMENT ---
        # Si la créature touche un aliment, elle le consomme.
        for a in aliments[:]:
            if distance(self.position, a.position) < (self.taille + a.taille):
                self.manger(a, aliments)

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
        self.creer_environnement(3000, 50)

    def creer_environnement(self, nb_aliments, nb_creatures):
        for _ in range(nb_aliments):
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            self.aliments.append(Aliment(pos, random.randint(10, 100)))
        for _ in range(nb_creatures):
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            self.creatures.append(Creature(pos, random.randint(15, 40)))

    def mise_a_jour(self):
        for c in self.creatures:
            c.agir(self.aliments, [c.glande for c in self.creatures])

    def reinitialiser_simulation(self, params):
        random.seed(params["seed"])
        self.largeur = params["largeur"]
        self.hauteur = params["hauteur"]
        self.aliments = []
        self.creatures = []
        self.creer_environnement(params["nb_aliments"],params["nb_creatures"])