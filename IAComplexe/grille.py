import random
import threading
import sys
from arbre import Arbre
from feu import Feu
from robot import Robot
from base import Base
from survivant import Survivant

class Grille:
    def __init__(self, taille, prob):
        self.taille = taille
        self.grille = [['*' for _ in range(taille)] for _ in range(taille)]
        self.prob = prob
        self.robot_position = None  # Position actuelle du robot
        self.carte_survivants = [[None for _ in range(taille)] for _ in range(taille)]  # Initialisation de carte_survivants

    def afficher_en_place(self):
        #sys.stdout.write("\033[H\033[J")
        for ligne in self.grille:
            sys.stdout.write(' '.join(
                [cell.symbole if isinstance(cell, (Arbre, Feu, Robot, Base, Survivant)) else '*' for cell in ligne]
            ) + "\n")
        sys.stdout.flush()

    def placer_au_hasard(self, objet, quantite):
        print(f"Objet reçu : {objet}, type : {type(objet)}")  # Log pour debug
        places_vides = [(i, j) for i in range(self.taille) for j in range(self.taille) if self.grille[i][j] == '*']
        
        if objet == Robot:
            if not hasattr(self, "robot_positions"):
                self.robot_positions = []  # Initialiser la liste des positions des robots
        elif objet == Survivant:
            if not hasattr(self, "survivant_positions"):
                self.survivant_positions = []  # Initialiser la liste des positions des survivants
            
        for _ in range(quantite):
            if not places_vides:
                print(f"Pas assez de place pour placer {objet().symbole}")
                break
            i, j = random.choice(places_vides)
            if objet == Robot:
                self.robot_positions.append((i, j))  # Ajouter la position du robot
            elif objet == Base:  # Vérification directe de la classe
                self.base_position = (i, j)  # Sauvegarde la position de la base
            elif objet == Survivant:
                self.survivant_positions.append((i, j))  # Ajouter la position du survivant
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
        
        # Directions globales pour les cases adjacentes
        directions = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
        
         # Ensemble pour suivre les feux déjà attribués
        feux_attribues = set()
        survivants_attribues = set()  
        
        # objectif ou le robot doit aller (soit la base pour se recharger en eau, soit un feu a eteindre)
        objectif = None

        def update_cell(i, j):
            if isinstance(self.grille[i][j], Arbre):
                # Si un arbre a un voisin en feu, il prend feu
                if any(isinstance(self.grille[x][y], Feu) for x, y in self.voisins(i, j)):
                    nouvelle_grille[i][j] = Feu()
            elif isinstance(self.grille[i][j], Feu):
                # Les feux restent des feux
                nouvelle_grille[i][j] = Feu()
            elif isinstance(self.grille[i][j], Survivant):
                # Les survivants restent des survivants
                nouvelle_grille[i][j] = Survivant()
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

        
        # Récupérer l'objet Base
        base_x, base_y = self.base_position
        base = self.grille[base_x][base_y]
        if not isinstance(base, Base):
            raise TypeError("La position de la base ne contient pas un objet Base.")

        # La base met à jour la carte des feux
        base.mettre_a_jour_carte(self.grille)

        # La base envoie la carte des feux aux robots
        robots = [self.grille[x][y] for x, y in self.robot_positions]
        base.envoyer_carte_aux_robots(robots)
    
        # Gestion des robots
        for index, position in enumerate(self.robot_positions):
            x, y = position
            robot = self.grille[x][y]

            if not isinstance(robot, Robot):
                raise TypeError(f"Le contenu à la position du Robot {index + 1} n'est pas un Robot : {self.grille[x][y]} | Coord : {x, y})")

            if robot.eau_actuelle <= 0:
                # Le robot retourne à la base pour se recharger
                print(f"Le Robot {index + 1} se dirige vers la base pour se recharger.")
                base_x, base_y = self.base_position
                

             
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
                        print(f"Robot {index + 1} se recharge en eau.")
                        robot.recharger()
            else:
                # Le robot éteint les feux voisins (si il y en a)
                feux_eteints = robot.eteindre_feu(nouvelle_grille, position)
                if feux_eteints:
                    print(f"Robot {index + 1} a éteint des feux voisins.")

        #         # Le robot choisit une cible
        #         cible = robot.choisir_cible(position, feux_attribues)

        #         if cible:
        #             feux_attribues.add(cible)  # Marquer la cible comme attribuée
        #             cible_x, cible_y = cible
        #             objectif = None
        #             for dx, dy in directions:
        #                 nx, ny = cible_x + dx, cible_y + dy
        #                 if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
        #                     objectif = (nx, ny)
        #                     break

        #         if objectif is None:
        #             print(f"Aucune case adjacente disponible pour le Robot {index + 1} autour de la cible {cible}.")
        #             continue  # Passer au robot suivant

        #         # Trouver le chemin vers l'objectif
        #         chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
        #         if len(chemin) > 1:  # Déplacement progressif
        #             next_position = chemin[1]
        #             nx, ny = next_position
        #             nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
        #             nouvelle_grille[nx][ny] = robot  # Déplacer le robot
        #             self.robot_positions[index] = (nx, ny)
        #             print(f"Robot {index + 1} se dirige vers la cible en {cible}.")
        #         else:
        #             # Déplacement aléatoire si aucune cible n'est disponible
        #             nouvelle_position = robot.se_deplacer(nouvelle_grille, position)
        #             nx, ny = nouvelle_position

        #             if nouvelle_grille[nx][ny] == '*':  # Vérifiez que la case est libre
        #                 nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
        #                 nouvelle_grille[nx][ny] = robot  # Déplacer le robot
        #                 self.robot_positions[index] = nouvelle_position
        #                 print(f"Robot {index + 1} se déplace aléatoirement.")

        # # Remplacer self.grille par la version mise à jour
        # self.grille = nouvelle_grille

                    # Le robot choisit une cible
                    cible = robot.choisir_cible(position, feux_attribues, survivants_attribues)

                    if cible:
                        cible_x, cible_y = cible
                        if self.carte_survivants[cible_x][cible_y] is not None:
                            survivants_attribues.add(cible)  # Marquer le survivant comme attribué
                        else:
                            feux_attribues.add(cible)  # Marquer le feu comme attribué

                        objectif = None
                        for dx, dy in directions:
                            nx, ny = cible_x + dx, cible_y + dy
                            if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
                                objectif = (nx, ny)
                                break

                        if objectif is None:
                            print(f"Aucune case adjacente disponible pour le Robot {index + 1} autour de la cible {cible}.")
                            continue  # Passer au robot suivant

                        # Trouver le chemin vers l'objectif
                        chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
                        if len(chemin) > 1:  # Déplacement progressif
                            next_position = chemin[1]
                            nx, ny = next_position
                            nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                            nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                            self.robot_positions[index] = (nx, ny)
                            print(f"Robot {index + 1} se dirige vers la cible en {cible}.")
                        else:
                            # Déplacement aléatoire si aucune cible n'est disponible
                            nouvelle_position = robot.se_deplacer(nouvelle_grille, position)
                            nx, ny = nouvelle_position

                            if nouvelle_grille[nx][ny] == '*':  # Vérifiez que la case est libre
                                nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                                nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                                self.robot_positions[index] = nouvelle_position
                                print(f"Robot {index + 1} se déplace aléatoirement.")

        # Remplacer self.grille par la version mise à jour
        self.grille = nouvelle_grille  # Remplacer la grille actuelle par la nouvelle grille