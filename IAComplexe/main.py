# This is a sample Python script.
from grille import Grille


class Main:
    def __init__(self):
        self.taille = 10  # Taille de la grille
        self.grille = Grille(self.taille)

    def demarrer(self):
        self.grille.placer_au_hasard('A', 20)  # Placer 20 arbres
        self.grille.placer_au_hasard('F', 5)   # Placer 5 feux
        print("Grille initiale:")
        self.grille.afficher()

        for t in range(5):  # Simuler 5 tours
            print(f"\nTour {t + 1}:")
            self.grille.mise_a_jour()
            self.grille.afficher()


if __name__ == "__main__":
    main = Main()
    main.demarrer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
