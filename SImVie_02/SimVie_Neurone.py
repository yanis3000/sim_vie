from abc import ABC

# ------------------------------------------------------------
# SimVie_Neurone.py
# ------------------------------------------------------------
import random

class Neurone():
    """Unité de base : reçoit plusieurs entrées (dendrites) et transmet un signal
       à plusieurs autres neurones (axones)."""
    def __init__(self, seuil=1.0):
        self.refractaire = 0  # temps restant avant de pouvoir tirer à nouveau
        self.delai_refractaire = 3  # durée fixe (en cycles)
        self.seuil = seuil # stimulation nécessaire pour que le neurone s'active
        self.entrees = []       # [(neurone_source, poids)]
        self.sorties = []       # [(neurone_cible, poids)]
        self.potentiel = 0.0  #accumuler les signaux entrants avant de décider de "décharger" ou non
        self.actif = False

    def connecter_a(self, cible, poids):
        self.sorties.append((cible, poids))
        cible.entrees.append((self, poids))

    def recevoir(self, signal):
        self.potentiel += signal

    def evaluer(self):
        """Évalue l’état du neurone en fonction des entrées et du seuil."""

        # Si le neurone est encore dans sa phase de repos, il ne peut pas s’activer
        if self.refractaire > 0:
            self.refractaire -= 1
            self.actif = False
            return

        # Calcul du potentiel reçu à partir des neurones d’entrée
        somme = 0
        for src, poids in self.entrees:
            somme += src.actif * poids
        self.potentiel = somme

        # Si le potentiel dépasse le seuil → activation
        if self.potentiel >= self.seuil:
            self.actif = True
            self.refractaire = self.delai_refractaire  # entre en période de repos
        else:
            self.actif = False


class SystemeNerveux:
    """Réseau neuronal hiérarchique :
       capteurs -> ganglions sensoriels -> interneurones -> ganglions moteurs -> moteurs"""
    def __init__(self, ganglion, nb_moteurs=8):
        self.ganglions = ganglion

        self.moteurs_gauche = []
        for m in range(nb_moteurs):
            neurone = Neurone(seuil=0.8)
            self.moteurs_gauche.append(neurone)

        self.moteurs_droite = []
        for m in range(nb_moteurs):
            neurone = Neurone(seuil=0.8)
            self.moteurs_droite.append(neurone)

        for gg in self.ganglions.neurone_gauche:
            for m in random.sample(self.moteurs_droite, k=2):
                gg.connecter_a(m, random.uniform(0.5, 1.0))

        for gd in self.ganglions.neurone_droite:
            for m in random.sample(self.moteurs_gauche, k=2):
                gd.connecter_a(m, random.uniform(0.5, 1.0))

    # --- Simulation d'un cycle d'activité ---
    def cycle(self, creature, stimuli_nourriture, stimuli_pheromone):
        """stimulations : liste de valeurs entre 0 et 1 pour chaque capteur"""

        creature.narines.capteur.activer(stimuli_nourriture, stimuli_pheromone)

        # Propagation à travers le réseau
        creature.narines.capteur.ganglion.propager()

        for n in self.moteurs_gauche:
            n.evaluer()
        for n in self.moteurs_droite:
            n.evaluer()

        # Retourne le taux d’activation motrice global (0-1)
        actifs_gauche = sum(1 for m in self.moteurs_gauche if m.actif)
        actifs_droite = sum(1 for m in self.moteurs_droite if m.actif)
        return [actifs_gauche / len(self.moteurs_gauche), actifs_droite / len(self.moteurs_droite)]
