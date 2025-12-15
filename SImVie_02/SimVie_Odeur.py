import math, random
from SimVie_Neurone import Neurone

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
# Glandes
# ------------------------------------------------------------

class Glande() :
    def __init__(self, creature_id, valeur_envie, position):
        self.creature_id = creature_id
        self.position = position
        self.valeur_pheromone = valeur_envie * 5
        self.rayon_senteur = valeur_envie * 1.5

    def emettre_pheromones(self, valeur_envie, position):
        self.position = position
        self.valeur_envie = valeur_envie
        self.valeur_pheromone = valeur_envie * 5
        self.rayon_senteur = valeur_envie * 1.5


# ------------------------------------------------------------
# Aliment
# ------------------------------------------------------------
class Aliment:
    def __init__(self, position, valeur_nourriture):
        self.position = position
        self.valeur_nourriture = valeur_nourriture * 5
        self.taille = valeur_nourriture * 0.1
        self.rayon_senteur = valeur_nourriture

class Nez:
    def __init__(self, genre, taille_creature, sensibilite_olfactive, position, orientation):

        self.position = position
        self.orientation = orientation

        self.hemi_nourriture_gauche = 0
        self.hemi_nourriture_droite = 0

        if genre == 'm':
            self.hemi_pheromone_droite = 0
            self.hemi_pheromone_gauche = 0

        self.sensibilite_olfactive = sensibilite_olfactive
        self.portee_olfactive = (20 + math.sqrt(taille_creature) * 30) * self.sensibilite_olfactive

        self.capteur = Capteur()
        self.genre = genre

    def sentir(self, aliments, glandes):

        for a in aliments:

            d = distance(self.position, a.position)

            if d < (self.portee_olfactive + a.rayon_senteur):

                ang = angle_relatif(self.position, a.position)
                rel = (ang - self.orientation + 540) % 360 - 180
                odeur = a.valeur_nourriture / (d + 1)

                if -180 <= rel < 0:
                    self.hemi_nourriture_gauche += odeur
                elif 0 <= rel < 180:
                    self.hemi_nourriture_droite += odeur
        
        if self.genre == 'm':
            for g in glandes:
                d = distance(self.position, g.position)

                if d < (self.portee_olfactive + g.rayon_senteur):

                    ang = angle_relatif(self.position, g.position)
                    rel = (ang - self.orientation + 540) % 360 - 180
                    odeur = g.valeur_pheromone / (d + 1)

                    if -180 < rel < 0:
                        self.hemi_pheromone_gauche += odeur
                    elif 0 <= rel < 180:
                        self.hemi_pheromone_droite += odeur

        if self.hemi_nourriture_droite < self.hemi_nourriture_gauche:
            self.hemi_nourriture_droite = 0
        else :
            self.hemi_nourriture_gauche = 0

        self.hemi_nourriture_gauche = min(1.0, self.hemi_nourriture_gauche / 10) 
        self.hemi_nourriture_droite = min(1.0, self.hemi_nourriture_droite / 10) 
        if self.genre == 'm':
            self.hemi_pheromone_gauche = min(1.0, self.hemi_pheromone_gauche / 10) 
            self.hemi_pheromone_droite = min(1.0, self.hemi_pheromone_droite / 10) 

    def maj_stimuli(self, droite_o, gauche_o, droite_v, gauche_v):
        if droite_o :
            self.hemi_nourriture_droite = 0
        if gauche_o :
            self.hemi_nourriture_gauche = 0
        if droite_v :
            self.hemi_pheromone_droite = 0
        if gauche_v :
            self.hemi_pheromone_gauche = 0
    
class Capteur:
    def __init__(self, neurone_olfactif=8, neurone_vomeronasal=8):
        self.olfactif_gauche = []
        self.olfactif_droite = []

        for i in range(neurone_olfactif):
            neurone = Neurone(seuil = random.uniform(0.3, 0.6))
            self.olfactif_gauche.append(neurone)
            neurone = Neurone(seuil = random.uniform(0.3, 0.6))
            self.olfactif_droite.append(neurone)

        self.vomeronasal_gauche = []
        self.vomeronasal_droite = []

        for i in range(neurone_vomeronasal):
            neurone = Neurone(seuil = random.uniform(0.3, 0.6))
            self.vomeronasal_gauche.append(neurone)
            neurone = Neurone(seuil = random.uniform(0.3, 0.6))
            self.vomeronasal_droite.append(neurone)

        self.ganglion = GanglionOlfactif(self.olfactif_gauche, self.olfactif_droite, self.vomeronasal_gauche, self.vomeronasal_droite)

    def activer(self, stimuli_nourriture, stimuli_pheromone):
        droite_o = False
        gauche_o = False
        droite_v = False
        gauche_v = False
        
        # Activer les capteurs
        if ( stimuli_nourriture[0] > stimuli_nourriture[1] ):
            for neurone, valeur in zip(self.olfactif_gauche, [stimuli_nourriture[0] for _ in range(len(self.olfactif_gauche))]):
                if ( neurone.seuil < valeur ):
                    neurone.actif = True
                    gauche_o = True
            for neurone, valeur in zip(self.olfactif_droite, [stimuli_nourriture[0] for _ in range(len(self.olfactif_droite))]):
                    neurone.actif = False
        elif ( stimuli_nourriture[0] <= stimuli_nourriture[1]  ):
            for neurone, valeur in zip(self.olfactif_droite, [stimuli_nourriture[1] for _ in range(len(self.olfactif_droite))]):
                if ( neurone.seuil < valeur):
                    neurone.actif = True
                    droite_o = True
            for neurone, valeur in zip(self.olfactif_gauche, [stimuli_nourriture[0] for _ in range(len(self.olfactif_gauche))]):
                    neurone.actif = False
        if ( stimuli_pheromone[0] > stimuli_pheromone[1] ) :
            for neurone, valeur in zip(self.vomeronasal_gauche, [stimuli_pheromone[0] for _ in range(len(self.vomeronasal_gauche))]):
                if ( neurone.seuil < valeur ):
                    neurone.actif = True
                    gauche_v = True
            for neurone, valeur in zip(self.vomeronasal_droite, [stimuli_nourriture[0] for _ in range(len(self.vomeronasal_droite))]):
                neurone.actif = False

        elif ( stimuli_nourriture[0] <= stimuli_pheromone[1] ) :
            for neurone, valeur in zip(self.vomeronasal_droite, [stimuli_pheromone[1] for _ in range(len(self.vomeronasal_droite))]):
                if ( neurone.seuil < valeur ):
                    neurone.actif = True
                    droite_v = True
            for neurone, valeur in zip(self.vomeronasal_gauche, [stimuli_nourriture[0] for _ in range(len(self.vomeronasal_gauche))]):
                neurone.actif = False

        return (droite_o, gauche_o, droite_v, gauche_v)

class GanglionOlfactif:

    def __init__(self, olfactif_gauche, olfactif_droite, vomeronasal_gauche, vomeronasal_droite, nb_neurone = 8):

        self.neurone_olf_gauche = []
        self.neurone_olf_droite = []
        self.neurone_vomero_gauche = []
        self.neurone_vomero_droite = []

        self.olfactif_actif = True
        self.vomeronasal_actif = True

        for i in range(nb_neurone):
            neurone = Neurone(seuil=1.0)
            self.neurone_olf_gauche.append(neurone)
            neurone = Neurone(seuil=1.0)
            self.neurone_olf_droite.append(neurone)
            neurone = Neurone(seuil=1.0)
            self.neurone_vomero_gauche.append(neurone)
            neurone = Neurone(seuil=1.0)
            self.neurone_vomero_droite.append(neurone)

        # Connexions entre couches
        for o in olfactif_gauche:
            for g in random.sample(self.neurone_olf_gauche, k = math.ceil(len(self.neurone_olf_gauche) * 0.9)):
                o.connecter_a(g, 0.5)
            for g in random.sample(self.neurone_olf_droite, k = math.ceil(len(self.neurone_olf_droite) * 0.1)):
                o.connecter_a(g, 0.5)
        for o in olfactif_droite:
            for g in random.sample(self.neurone_olf_gauche, k = math.ceil(len(self.neurone_olf_gauche) * 0.1)):
                o.connecter_a(g, 0.5)
            for g in random.sample(self.neurone_olf_droite, k = math.ceil(len(self.neurone_olf_droite) * 0.9)):
                o.connecter_a(g, 0.5)

        for v in vomeronasal_gauche:
            for g in random.sample(self.neurone_vomero_gauche, k = math.ceil(len(self.neurone_vomero_gauche) * 0.9)):
                v.connecter_a(g, 0.5)
            for g in random.sample(self.neurone_vomero_droite, k = math.ceil(len(self.neurone_vomero_droite) * 0.1)):
                v.connecter_a(g, 0.5)
        for v in vomeronasal_droite:
            for g in random.sample(self.neurone_vomero_gauche, k = math.ceil(len(self.neurone_vomero_gauche) * 0.1)):
                v.connecter_a(g, 0.5)
            for g in random.sample(self.neurone_vomero_droite, k = math.ceil(len(self.neurone_vomero_droite) * 0.9)):
                v.connecter_a(g, 0.5)
        
    def propager(self):
        if( self.olfactif_actif):
            for n in self.neurone_olf_gauche:
                n.evaluer()
            for n in self.neurone_olf_droite:
                n.evaluer()
        else :
            for n in self.neurone_olf_gauche:
                n.actif = False
            for n in self.neurone_olf_droite:
                n.actif = False
        if ( self.vomeronasal_actif):
            for n in self.neurone_vomero_gauche:
                n.evaluer()
            for n in self.neurone_vomero_droite:
                n.evaluer()
        else :
            for n in self.neurone_vomero_gauche:
                n.actif = False
            for n in self.neurone_vomero_droite:
                n.actif = False