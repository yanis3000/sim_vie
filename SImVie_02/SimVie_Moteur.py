from SimVie_Neurone import Neurone
import math, random

class Pattes:
    def __init__(self, ganglions, position, orientation, nb_moteurs = 16):
        
        self.position = position
        self.orientation = orientation

        self.actif_gauche = 0
        self.actif_droite = 0

        self.moteurs_gauche = []
        for m in range(nb_moteurs):
            neurone = Neurone(seuil=0.8)
            self.moteurs_gauche.append(neurone)

        self.moteurs_droite = []
        for m in range(nb_moteurs):
            neurone = Neurone(seuil=0.8)
            self.moteurs_droite.append(neurone)

        for gg in ganglions.neurone_gauche:
            for m in random.sample(self.moteurs_gauche, k=2):
                gg.connecter_a(m, 0.5)

        for gd in ganglions.neurone_droite:
            for m in random.sample(self.moteurs_droite, k=2):
                gd.connecter_a(m, 0.5)

    
    def activer(self):
        for n in self.moteurs_gauche:
            n.evaluer()
        for n in self.moteurs_droite:
            n.evaluer()

        self.actif_gauche = sum(m.potentiel for m in self.moteurs_gauche if m.actif) / len(self.moteurs_gauche)
        self.actif_droite = sum(m.potentiel for m in self.moteurs_droite if m.actif) / len(self.moteurs_droite)

    