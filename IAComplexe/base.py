from color import Color
from feu import Feu


class Base:
    def __init__(self):
        self.symbole = Color.BLUE + 'B' + Color.END
        self.carte_feux = None  # La base stocke la carte des feux

    def mettre_a_jour_carte(self, grille):
        """Récupère la carte des feux depuis la grille."""
        taille = len(grille)
        self.carte_feux = [[None for _ in range(taille)] for _ in range(taille)]
        for i in range(taille):
            for j in range(taille):
                if isinstance(grille[i][j], Feu):
                    self.carte_feux[i][j] = (i, j)  # Position du feu
                else:
                    self.carte_feux[i][j] = None

    def envoyer_carte_aux_robots(self, robots):
        """Envoie la carte des feux à tous les robots."""
        for robot in robots:
            robot.recevoir_carte(self.carte_feux)
