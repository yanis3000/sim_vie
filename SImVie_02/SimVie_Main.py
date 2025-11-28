# ------------------------------------------------------------
# SimVie_Main.py
# ------------------------------------------------------------
from SimVie_Modele import Modele
from SimVie_Vue import Vue

class Controleur:
    def __init__(self):
        self.modele = Modele(self, 5000, 5000)
        self.vue = Vue(self, self.modele)
        self.jouer_tour()
        self.vue.root.mainloop()

    def jouer_tour(self):
        self.modele.mise_a_jour()
        self.vue.rafraichir()
        self.vue.root.after(50, self.jouer_tour)

    def reinitialiser_simulation(self,params):
        self.modele.reinitialiser_simulation(params)
        self.vue.afficher_elements()

if __name__ == "__main__":
    Controleur()
