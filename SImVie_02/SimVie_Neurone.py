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
    def __init__(self, ganglions_olfactifs, ganglions_vomeronasal):

        # --- satiété, énergie, santé, reproduction --- #

        self.seuil_olfactif = [50, 5, 10, 0]
        self.seuil_vomeronasal = [30, 20, 30, 20]
        self.rules = (True, False, False, False)
        self.jauge = [40, 10, 0, 30]

        self.ganglions_olfactifs = ganglions_olfactifs

        self.ganglions_vomeronasal = ganglions_vomeronasal


    # --- Simulation d'un cycle d'activité ---
    def cycle(self, creature, stimuli_nourriture, stimuli_pheromone):
        """stimulations : liste de valeurs entre 0 et 1 pour chaque capteur"""

        # self.maj_valeur(creature)
        self.maj_ganglions()

        creature.narines.capteur.activer(stimuli_nourriture, stimuli_pheromone)
        # Propagation à travers le réseau
        creature.narines.capteur.ganglion.propager()

        activation = creature.pattes.activer()

        return activation
    

    def maj_valeur(self, creature):
        self.jauge = [creature.sante,
                      creature.satiete,
                      creature.energie,
                      creature.envie_reproduction]

    def maj_ganglions(self):
        rep1 = []
        rep2 = []
        for i in range(len(self.jauge)):
            rep1.append(self.rules[i] if self.jauge[i] <= self.seuil_olfactif[i] else not self.rules[i])
            rep2.append(self.rules[i] if self.jauge[i] <= self.seuil_vomeronasal[i] else not self.rules[i])
        self.ganglions_olfactifs = all(rep1)
        self.ganglions_vomeronasal = all(rep2)
        

