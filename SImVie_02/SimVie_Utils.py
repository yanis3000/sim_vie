import math

class Utils:
    @staticmethod
    def param_fonction_quad(origine, sommet):
        """
        Cette fonction sert à trouver les paramètres d'une fonction quadratique.

        Args:
            origine (tuple): Un tuple représentant l'origine de la fonction.
            sommet (tuple): Un tuple représentant le sommet de la fonction.

        Returns:
            tuple: Un tuple sous forme de (a, b, c).
        """
        xo, yo = origine
        xs, ys = sommet

        a = (yo - ys) / math.pow((xo - xs), 2) 
        b = -1 * (xs * (2 * a))
        c = yo

        return (a, b, c) 

    # def 