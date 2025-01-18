from grille import Grille
from arbre import Arbre
from feu import Feu
from robot import Robot
from base import Base
from survivant import Survivant


class Main:
    def __init__(self):
        self.taille = 10
        self.prob = float(input('Entrez la probabilité de pousse d\'un arbre (entre 0 et 1) : '))
        self.grille = Grille(self.taille, self.prob)
        

    def demarrer(self):
        self.grille.placer_au_hasard(Arbre, 20)  # Placer 20 arbres
        self.grille.placer_au_hasard(Feu, 5)  # Placer 5 feux
        self.grille.placer_au_hasard(Robot, 2)  # Placer 1 robot
        self.grille.placer_au_hasard(Base, 1)  # Placer 1 base
        self.grille.placer_au_hasard(Survivant, 5) # Placer 5 survivants
        print("Grille initiale:")
        self.grille.afficher_en_place()

        for t in range(1000):  # Simuler 5 tours
            print(f"\nTour {t + 1}:")
            self.grille.mise_a_jour()
            self.grille.afficher_en_place()


if __name__ == "__main__":
    main = Main()
    main.demarrer()
