

from grille import Grille
from arbre import Arbre
from feu import Feu
from robot import Robot
from base import Base
from survivant import Survivant

class Main:
    def __init__(self, mode_silencieux=False):
        self.taille = 10
        self.prob = float(input('Entrez la probabilité de pousse d\'un arbre (entre 0 et 1) : '))
        self.grille = Grille(self.taille, self.prob, mode_silencieux)
        self.mode_silencieux = mode_silencieux
        self.nb_robot = 7

    def demarrer(self):
        self.grille.placer_au_hasard(Arbre, 20)  # Placer 20 arbres
        self.grille.placer_au_hasard(Feu, 5)  # Placer 5 feux
        self.grille.placer_au_hasard(Robot, self.nb_robot)  # Placer 2 robots
        self.grille.placer_au_hasard(Base, 1)  # Placer 1 base
        self.grille.placer_au_hasard(Survivant, 4)  # Placer 4 survivants
        
        if not self.mode_silencieux:
            print("Grille initiale:")
            self.grille.afficher_en_place()

        for t in range(1000):  # Limite de tours pour éviter les boucles infinies
            if not self.mode_silencieux:
                print(f"\nTour {t + 1}:")
            self.grille.mise_a_jour()

            if not self.mode_silencieux:
                self.grille.afficher_en_place()

            if self.grille.verifier_fin():
                if not self.mode_silencieux:
                    print("\nSimulation terminée.")
                print(f"Résultat : Les robots ont {'gagné' if t < 1000 else 'perdu'} en {t + 1} tours.")
                return  # Fin de la simulation

        print("\nSimulation terminée : Limite de tours atteinte.")
        print("Résultat : Les robots n'ont pas réussi à terminer dans la limite de temps.")

    def executer_simulation(self):
        """Exécute une simulation unique et retourne le résultat et le nombre de tours."""
        self.grille = Grille(self.taille, self.prob, self.mode_silencieux)
        self.grille.placer_au_hasard(Arbre, 20)  # Placer 20 arbres
        self.grille.placer_au_hasard(Feu, 5)  # Placer 5 feux
        self.grille.placer_au_hasard(Robot, self.nb_robot)  # Placer 2 robots
        self.grille.placer_au_hasard(Base, 1)  # Placer 1 base
        self.grille.placer_au_hasard(Survivant, 4)  # Placer 4 survivants

        for t in range(1000):  # Limite de tours pour éviter les boucles infinies
            self.grille.mise_a_jour()
            if self.grille.verifier_fin():
                return t + 1, True  # Retourne le nombre de tours et si les robots ont gagné

        return 1000, False  # Retourne la limite atteinte et une défaite

    def executer_plusieurs_simulations(self, nombre_simulations):
        """Exécute plusieurs simulations et calcule les statistiques."""
        total_tours = 0
        victoires = 0

        for i in range(nombre_simulations):
            print(f"Simulation {i + 1}/{nombre_simulations} en cours...") 
            tours, victoire = self.executer_simulation()
            total_tours += tours
            if victoire:
                victoires += 1

        moyenne_tours = total_tours / nombre_simulations
        taux_victoires = (victoires / nombre_simulations) * 100

        print("\nRésultats des simulations :")
        print(f"Nombre de simulations : {nombre_simulations}")
        print(f"Taux de victoires : {taux_victoires:.2f}%")
        print(f"Nombre moyen de tours : {moyenne_tours:.2f}")
        
        
if __name__ == "__main__":
    mode_silencieux = input("Voulez-vous activer le mode silencieux ? (o/n) : ").strip().lower() == 'o'
    main = Main(mode_silencieux=mode_silencieux)

    if mode_silencieux:
        nombre_simulations = int(input("Combien de simulations souhaitez-vous exécuter ? "))
        main.executer_plusieurs_simulations(nombre_simulations)
    else:
        main.demarrer()

