# ------------------------------------------------------------
# SimVie_Modele.py
# ------------------------------------------------------------
import random, math
from enum import Enum
from SimVie_Utils import Utils as ut
from SimVie_Neurone import SystemeNerveux
from SimVie_Odeur import Glande, Aliment, Nez
from SimVie_Moteur import Pattes

# ------------------------------------------------------------
# Générateur d'id unique
# ------------------------------------------------------------
ID_ACTUEL = 0

def genererIdObjet():
    global ID_ACTUEL
    ID_ACTUEL += 1
    return f"id_{ID_ACTUEL}"

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

class Etat(Enum): # selon la convention, le name reste en majuscule
    DISPONIBLE = 0
    MANGER = 1
    REPRODUCTION = 2
    DORMIR = 3

class Creature:
    def __init__(self, position, taille, id):
        self.id = id
        # --- Param f_quad --- #

        self.count_cycle = 0
        self.count_action = 0
        self.count_limit_action = 0
        self.count_repro_cycle = 0
        
        
        # Santé
        origine = (0, 10) ## 10 = valeur de la santé au début de la simulation
        sommet = (600, 100) ## 100 = valeur de la santé après 600 cycles.
        self.sante_quad = ut.param_fonction_quad(origine, sommet)

        # --- Jauges besoins --- #
        a, b, c = self.sante_quad
        self.sante = (a * math.pow(self.count_cycle, 2)) + (self.count_cycle * b) + c       # Entre 0 et 100
        self.energie = 100
        self.satiete = 100
        self.envie_reproduction = (a * math.pow(self.count_repro_cycle, 2)) + (self.count_repro_cycle * b) + c      
        self.intensite = 0                

        self.position = position
        self.taille = taille
        self.orientation = random.uniform(0, 360)
        self.vitesse = 10  
        self.genre = random.choice(('f', 'm'))
        self.narines = Nez(self.genre, self.taille, random.uniform(0.8, 1.2), self.position, self.orientation)
        self.cerveau = SystemeNerveux(self.narines.capteur.ganglion.olfactif_actif, self.narines.capteur.ganglion.vomeronasal_actif)
        self.pattes = Pattes(self.narines.capteur.ganglion, self.position, self.orientation) 
        
        if self.genre == 'f':  
            self.glande = Glande(self.id, self.envie_reproduction, self.position)
            self.gestation_cap = random.randint(1, 6)

        self.etat = Etat.DISPONIBLE

        self.deg_orientation = 20

        # Aliment en interaction
        self.aliment = None
        self.partenaire = None


    # --- Olfaction directionnelle ---
    def percevoir(self, aliments, glandes):
        self.narines.position = self.position
        self.narines.orientation = self.orientation
        self.narines.sentir(aliments, glandes)

    # --- Comportement global ---
    def agir(self, aliments, glandes):
        """
        Boucle perception-action de la créature.
        Elle perçoit les odeurs, ajuste son orientation, se déplace,
        consomme de l'énergie, et interagit avec les aliments.
        """
        if self.etat == Etat.DISPONIBLE:
            # --- 1. PERCEPTION SENSORIELLE ---
            # Le cerveau reçoit deux entrées : intensité olfactive gauche/droite (0 à 1)

            self.percevoir(aliments, glandes)

            stimuli_nourriture = [self.narines.hemi_nourriture_gauche, 
                    self.narines.hemi_nourriture_droite]
            
            stimuli_pheromone = [0, 0] 
            
            if self.genre == 'm':
                stimuli_pheromone = [self.narines.hemi_pheromone_gauche, 
                        self.narines.hemi_pheromone_droite]
            
            
            # --- 2. TRAITEMENT NEURONAL ---
            # Le système nerveux interne traite les signaux sensoriels
            # et produit une activation motrice globale (de 0 à 1)

            actif_g, actif_d = self.cerveau.cycle(self, stimuli_nourriture, stimuli_pheromone)

            if actif_g > 0 or actif_d > 0 :

                # --- 3. ORIENTATION ---

                # Différence gauche-droite → rotation vers le côté le plus odorant
                delta_orientation = (actif_d - actif_g) * self.deg_orientation
                # Ajout d'un léger bruit aléatoire pour éviter la synchronisation des trajectoires
                self.orientation += delta_orientation + random.uniform(-1, 1)

                # --- 4. DÉPLACEMENT ---
                # L’intensité de mouvement dépend de l’activation moyenne (moyenne des deux narines)
                self.intensite = max(0.05, (actif_g + actif_d) / 2)
                angle = math.radians(self.orientation)
                dx = self.vitesse * self.intensite * math.cos(angle)
                dy = self.vitesse * self.intensite * math.sin(angle)
                self.position = (self.position[0] + dx, self.position[1] + dy)
            else :
                self.intensite = 0

            # --- 5. MÉTABOLISME ---
            # Chaque déplacement consomme de l'énergie.
            # Ici, on modélise une perte de base (0.05) + une dépense proportionnelle à l’activité.
            self.satiete -= 0.1 + (0.1 * self.intensite)
            if self.satiete < 0:
                self.satiete = 0
            elif self.satiete > 100 :
                self.satiete = 100

            self.energie -= 0.5 + (0.1 * self.intensite)
            if self.energie < 0:
                self.energie = 0
            elif self.energie > 100 :
                self.energie = 100

            if self.energie == 0 :
                self.dormir()

            # --- 6. INTERACTION AVEC L’ENVIRONNEMENT ---
            # Si la créature touche un aliment, elle le consomme.
            for a in aliments[:]:
                if not a.targetted :
                    if distance(self.position, a.position) < (self.taille + a.taille):
                        self.manger(a, aliments)

            if self.genre == 'm':
                for g in glandes:
                    if not g.targetted:
                        if distance(self.position, g.position) < (self.taille):
                            if self.se_reproduire(g):
                                self.partenaire = g.creature_id
                                return g.creature_id
        else:
            self.count_action += 1
            if self.count_action >= self.count_limit_action:
                if self.action(aliments) :
                    id = self.partenaire
                    self.partenaire = None
                    return id


    def manger(self, aliment, aliments):
        if self.narines.capteur.ganglion.olfactif_actif:
            self.etat = Etat.MANGER
            self.aliment = aliment
            aliment.targetted = True
            self.count_limit_action = 100

    def dormir(self) :
        self.etat = Etat.DORMIR
        self.count_limit_action = 100

    def se_reproduire(self, glande):
        if self.narines.capteur.ganglion.vomeronasal_actif:
            self.etat = Etat.REPRODUCTION      
            self.count_limit_action = 100
            glande.targetted = True
            return True
        else:
            return False
            
    def action(self, aliments):
        if self.etat == Etat.MANGER:
            self.satiete = max(100, self.satiete + self.aliment.valeur_nourriture)
            aliments.remove(self.aliment)
            self.aliment = None
            self.count_action = 0
            self.etat = Etat.DISPONIBLE
        if self.etat == Etat.REPRODUCTION:
            self.etat = Etat.DISPONIBLE
            self.count_repro_cycle = 0
            self.count_action = 0
            return True
        if self.etat == Etat.DORMIR:
            self.etat = Etat.DISPONIBLE
            self.energie = 100
            self.count_action = 0

    def maj_jauges(self):
        self.count_cycle += 1
        self.count_repro_cycle += 1

        # maj Santé
        a, b, c = self.sante_quad
        self.sante = (a * math.pow(self.count_cycle, 2)) + (self.count_cycle * b) + c

        # maj Reproduction
        self.envie_reproduction = (a * math.pow(self.count_repro_cycle, 2)) + (self.count_repro_cycle * b) + c 

        return self.sante > 0
    

class Oeuf:
    def __init__(self, pere, mere):
        self.pere = pere
        self.mere = mere
        self.position = mere.position
        self.duree = random.randint(100, 200)
        self.count = 0

    def cycle(self):
        self.count += 1
        return self.count >= self.duree

# ------------------------------------------------------------
# Modèle général
# ------------------------------------------------------------
class Modele:
    def __init__(self, controleur, largeur_terrain, hauteur_terrain, nb_aliments, nb_creatures):
        self.controleur = controleur
        self.largeur_terrain = largeur_terrain
        self.hauteur_terrain = hauteur_terrain
        self.aliments = []
        self.creatures = []
        self.creatures_to_delete = []
        self.nouvelles_creatures = []
        self.glandes = []
        self.oeuf = []
        self.oeuf_to_delete = []
        self.degree = 20
        self.vitesse = 10
        self.count_food = 0
        self.count_interval = 30
        self.creer_environnement(nb_aliments, nb_creatures)

    def creer_environnement(self, nb_aliments, nb_creatures):
        for _ in range(nb_aliments):
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            self.aliments.append(Aliment(pos, random.randint(10, 100)))
        for _ in range(nb_creatures):
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            c = Creature(pos, random.randint(15, 40), genererIdObjet())
            c.deg_orientation = self.degree
            c.vitesse = self.vitesse
            self.creatures.append(c)
            if c.genre == 'f':
                self.glandes.append(c.glande)

    def mise_a_jour(self):
        self.count_food += 1
        if self.count_food >= self.count_interval:
            pos = (random.randint(0, self.largeur_terrain),
                   random.randint(0, self.hauteur_terrain))
            a = Aliment(pos, random.randint(10, 100))
            self.aliments.append(a)
            self.controleur.vue.creer_aliment(a)
            self.count_food = 0
        for c in self.creatures:
            if c.genre == 'f':
                c.glande.emettre_pheromones(c.envie_reproduction, c.position)
            id = c.agir(self.aliments, self.glandes)
            if id != None:
                for m in self.creatures:
                    if id == m.id:
                        if m.etat == Etat.DISPONIBLE:
                            m.etat = Etat.REPRODUCTION
                            m.count_limit_action = 100
                        else:
                            for _ in range(m.gestation_cap + 1):
                                self.oeuf.append(Oeuf(c, m))
                            m.count_repro_cycle = 0
            if c.maj_jauges() == False:
                self.creatures_to_delete.append(c)
        for c in self.creatures_to_delete:
            if c.genre == 'f':
                self.glandes.remove(c.glande)
            self.creatures.remove(c)
        self.creatures_to_delete = []
        
        for o in self.oeuf:
            if o.cycle():
                self.oeuf_to_delete.append(o)
                c = Creature(o.position, random.randint(15, 40), genererIdObjet())
                c.deg_orientation = self.degree
                c.vitesse = self.vitesse
                self.creatures.append(c)
                self.controleur.vue.creer_creature(c)
                if c.genre == 'f':
                    self.glandes.append(c.glande)
        for o in self.oeuf_to_delete:
            self.oeuf.remove(o)
        self.oeuf_to_delete = []
                        
    def reinitialiser_simulation(self, params):
        random.seed(params["seed"])
        self.largeur = params["largeur"]
        self.hauteur = params["hauteur"]
        self.aliments = []
        self.creatures = []
        self.degree = params["orientation"]
        self.vitesse = params["vitesse"]
        self.creer_environnement(params["nb_aliments"],params["nb_creatures"])
