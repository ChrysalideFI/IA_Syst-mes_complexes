import random
import threading
import sys
from arbre import Arbre
from feu import Feu
from robot import Robot


class Grille:
    def __init__(self, taille, prob):
        self.taille = taille
        self.grille = [['*' for _ in range(taille)] for _ in range(taille)]
        self.prob = prob
        self.robot_position = None  # Position actuelle du robot

    def afficher_en_place(self):
        #sys.stdout.write("\033[H\033[J")
        for ligne in self.grille:
            sys.stdout.write(' '.join(
                [cell.symbole if isinstance(cell, (Arbre, Feu, Robot)) else '*' for cell in ligne]
            ) + "\n")
        sys.stdout.flush()

    def placer_au_hasard(self, objet, quantite):
        places_vides = [(i, j) for i in range(self.taille) for j in range(self.taille) if self.grille[i][j] == '*']
        for _ in range(quantite):
            if not places_vides:
                print(f"Pas assez de place pour placer {objet().symbole}")
                break
            i, j = random.choice(places_vides)
            if objet == Robot:
                self.robot_position = (i, j)  # Stocker la position du robot
            self.grille[i][j] = objet()  # Place une instance de la classe
            places_vides.remove((i, j))

        print(f"Position initiale du robot : {self.robot_position}")


    def voisins(self, x, y):
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        voisins = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.taille and 0 <= ny < self.taille:
                voisins.append((nx, ny))
        return voisins

    def mise_a_jour(self):
        input("Appuyer sur entrer pour continuer")
        nouvelle_grille = [ligne[:] for ligne in self.grille]  # Créer une copie de la grille actuelle

        def update_cell(i, j):
            if isinstance(self.grille[i][j], Arbre):
                # Si un arbre a un voisin en feu, il prend feu
                if any(isinstance(self.grille[x][y], Feu) for x, y in self.voisins(i, j)):
                    nouvelle_grille[i][j] = Feu()
            elif isinstance(self.grille[i][j], Feu):
                # Les feux restent des feux
                nouvelle_grille[i][j] = Feu()
            elif self.grille[i][j] == '*' and random.random() < self.prob:
                # Une case vide a une probabilité de devenir un arbre
                nouvelle_grille[i][j] = Arbre()

        # Mise à jour des cellules de la grille
        threads = []
        for i in range(self.taille):
            for j in range(self.taille):
                thread = threading.Thread(target=update_cell, args=(i, j))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        # Déplacer le robot et éteindre les feux voisins dans nouvelle_grille
        if self.robot_position:
            x, y = self.robot_position
            robot = self.grille[x][y]
            
            if not isinstance(robot, Robot):
                raise TypeError(f"Le contenu à la position du robot n'est pas un Robot : {self.grille[x][y]}")

            # Le robot éteint les feux voisins (dans nouvelle_grille)
            robot.eteindre_feu(nouvelle_grille, self.robot_position)

            # Le robot se déplace
            nouvelle_position = robot.se_deplacer(nouvelle_grille, self.robot_position)
            nx, ny = nouvelle_position

            # Vérifiez si le déplacement est valide
            if nouvelle_grille[nx][ny] != '*':
                raise ValueError(f"Position cible du robot invalide : {nx, ny}, contenu : {nouvelle_grille[nx][ny]}")

            # Marquer l'ancienne position comme vide
            print(f"Ancienne position du robot vidée : {self.robot_position}")
            nouvelle_grille[x][y] = '*'  

            # Déplacer le robot à la nouvelle position dans nouvelle_grille
            print(f"Robot déplacé vers : {nouvelle_position}")
            nouvelle_grille[nx][ny] = robot
            self.robot_position = nouvelle_position

            # Vérifiez si nouvelle_grille et la position sont bien mises à jour
            print(f"Vérification après déplacement : Position {self.robot_position}, type : {type(nouvelle_grille[nx][ny])}")

        # Remplacer self.grille par la version mise à jour
        self.grille = nouvelle_grille

