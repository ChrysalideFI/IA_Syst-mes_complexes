import random
import threading
import sys
from arbre import Arbre
from feu import Feu
from robot import Robot
from base import Base

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
                [cell.symbole if isinstance(cell, (Arbre, Feu, Robot, Base)) else '*' for cell in ligne]
            ) + "\n")
        sys.stdout.flush()

    def placer_au_hasard(self, objet, quantite):
        print(f"Objet reçu : {objet}, type : {type(objet)}")  # Log pour debug
        places_vides = [(i, j) for i in range(self.taille) for j in range(self.taille) if self.grille[i][j] == '*']
        
        if objet == Robot:
            if not hasattr(self, "robot_positions"):
                self.robot_positions = []  # Initialiser la liste des positions des robots
            
        for _ in range(quantite):
            if not places_vides:
                print(f"Pas assez de place pour placer {objet().symbole}")
                break
            i, j = random.choice(places_vides)
            if objet == Robot:
                self.robot_positions.append((i, j))  # Ajouter la position du robot
            if objet == Base:  # Vérification directe de la classe
                self.base_position = (i, j)  # Sauvegarde la position de la base
            self.grille[i][j] = objet()  # Place une instance de la classe
           
            places_vides.remove((i, j))

        # Debug pour confirmer les positions
        if hasattr(self, "base_position"):
            print(f"Position initiale de la base : {self.base_position}")
        else:
            print("La base n'a pas été placée.")
        if hasattr(self, "robot_positions"):
           print(f"Positions initiales des robots : {self.robot_positions}")
        else:
            print("Le robot n'a pas été placé.")


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

        # gestion des robots
        for index, position in enumerate(self.robot_positions):
            x, y = position
            robot = self.grille[x][y]
            
            if not isinstance(robot, Robot):
                raise TypeError(f"Le contenu à la position du Robot {index + 1} n'est pas un Robot : {self.grille[x][y]} | Coord : {x, y}) ")

            # Vérifier si le robot a besoin de se recharger
            if robot.eau_actuelle <= 0:
                print(f"Le Robot {index + 1} se dirige vers la base pour se recharger.")
                base_x, base_y = self.base_position
                objectif = None  # Initialiser objectif par défaut
                 
                # Trouver une case adjacente libre à la base
                directions = [
                    (-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 1),
                    (1, -1), (1, 0), (1, 1)  
                ]
                for dx, dy in directions:
                    nx, ny = base_x + dx, base_y + dy
                    if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
                        objectif = (nx, ny)
                        break
                
                
                  # Si aucun objectif n'est trouvé, lever une alerte et passer
                if objectif is None:
                    print(f"Aucune case adjacente disponible pour le Robot {index + 1} autour de la base.")
                    continue  # Passer au robot suivant
                
                # Trouver le chemin vers la case adjacente à la base
                chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
                print(chemin)
                
                if len(chemin) > 1:  # Le premier élément est la position actuelle
                    next_position = chemin[1]  # Prochaine étape
                    nx, ny = next_position

                    if nouvelle_grille[nx][ny] == '*':  # Vérifiez que la case est libre
                        # Déplacer le robot
                        nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                        nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                        self.robot_positions[index] = (nx, ny)

                        print(f"Robot {index + 1} déplacé vers {next_position} en direction de la base.")
                        
                     # Recharger si le robot est arrivé près de la base
                    if self.robot_positions[index] == objectif:
                        print(f"Robot {index + 1} se recharge en eau")
                        robot.recharger()
            else:
                # Le robot éteint les feux voisins (dans nouvelle_grille) (si il y en a)
                robot.eteindre_feu(nouvelle_grille, position)

                # Le robot se déplace
                nouvelle_position = robot.se_deplacer(nouvelle_grille, position)
                nx, ny = nouvelle_position

               
                if nouvelle_grille[nx][ny] == '*':  # Vérifiez que la case est libre
                    # Marquer l'ancienne position comme vide
                    print(f"Ancienne position du Robot {index + 1} vidée : {position}")
                    nouvelle_grille[x][y] = '*'  

                    
                    # Déplacer le robot à la nouvelle position dans nouvelle_grille
                    print(f"Robot {index + 1} déplacé vers : {nouvelle_position}")
                    nouvelle_grille[nx][ny] = robot
                    self.robot_positions[index] = nouvelle_position

                # Vérifiez si nouvelle_grille et la position sont bien mises à jour
                print(f"Vérification après déplacement : Position {self.robot_positions[index]}, type : {type(nouvelle_grille[nx][ny])}")
                print(f"Robot {index + 1} eau restante : {robot.eau_actuelle} ")
        # Remplacer self.grille par la version mise à jour
        self.grille = nouvelle_grille

