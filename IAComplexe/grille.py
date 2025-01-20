import random
import threading
import sys
from arbre import Arbre
from feu import Feu
from robot import Robot
from base import Base
from survivant import Survivant

class Grille:
    def __init__(self, taille, prob, mode_silencieux=False):
        self.taille = taille
        self.grille = [['*' for _ in range(taille)] for _ in range(taille)]
        self.prob = prob
        self.robot_position = None  # Position actuelle du robot
        self.position_explore = set()
        self.cibles_reservees = set()  # Ensemble des cibles actuellement assignées aux robots
        self.mode_silencieux = mode_silencieux

    def afficher_en_place(self):
        #sys.stdout.write("\033[H\033[J")
        for ligne in self.grille:
            sys.stdout.write(' '.join(
                [cell.symbole if isinstance(cell, (Arbre, Feu, Robot, Base, Survivant)) else '*' for cell in ligne]
            ) + "\n")
        sys.stdout.flush()

    def mettre_a_jour_positions_robots(self):
            """Met à jour la liste des positions des robots en fonction de l'état actuel de la grille."""
            self.robot_positions = [
                (i, j)
                for i in range(self.taille)
                for j in range(self.taille)
                if isinstance(self.grille[i][j], Robot)
            ]
            if not self.mode_silencieux:
                print(f"Positions des robots mises à jour : {self.robot_positions}")
                
    def placer_au_hasard(self, objet, quantite):
       
        places_vides = [(i, j) for i in range(self.taille) for j in range(self.taille) if self.grille[i][j] == '*']
        
        if objet == Robot:
            if not hasattr(self, "robot_positions"):
                self.robot_positions = []  # Initialiser la liste des positions des robots
            
        for _ in range(quantite):
            if not places_vides:
                if not self.mode_silencieux:
                    print(f"Pas assez de place pour placer {objet().symbole}")
                break
            i, j = random.choice(places_vides)
            if objet == Robot:
                self.robot_positions.append((i, j))  # Ajouter la position du robot
                self.position_explore.add((i, j))
            if objet == Base:  # Vérification directe de la classe
                self.base_position = (i, j)  # Sauvegarde la position de la base
            self.grille[i][j] = objet()  # Place une instance de la classe
            
            places_vides.remove((i, j))
            self.mettre_a_jour_positions_robots()

 


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
        if not self.mode_silencieux:
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

        self.mettre_a_jour_positions_robots()
        # La base met à jour la carte des feux
        base.mettre_a_jour_carte(self.grille)

        # La base envoie la carte des feux aux robots
        robots = [nouvelle_grille[x][y] for x, y in self.robot_positions]
        robots = [r for r in robots if isinstance(r, Robot)]
        base.envoyer_carte_aux_robots(robots)
    
        # Gestion des robots
        for index, position in enumerate(self.robot_positions):
            x, y = position
            robot = self.grille[x][y]

            if not isinstance(robot, Robot):
                raise TypeError(f"Le contenu à la position du Robot {index + 1} n'est pas un Robot : {self.grille[x][y]} | Coord : {x, y})")

            if robot.eau_actuelle <= 0:
                # Le robot retourne à la base pour se recharger
               
                if not self.mode_silencieux:
                    print(f"Le Robot {index + 1} se dirige vers la base pour se recharger.")
                base_x, base_y = self.base_position
                

                # Trouver une case adjacente libre à la base
                chemin = []
                for dx, dy in directions:
                    nx, ny = base_x + dx, base_y + dy
                    if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
                        objectif = (nx, ny)
                        chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
                        if chemin:  # Si un chemin valide est trouvé, sortir de la boucle
                            break

                # Si aucun chemin n'est trouvé, lever une alerte et passer
                if not chemin:
                    if not self.mode_silencieux:
                        print(f"Aucune case adjacente accessible pour le Robot {index + 1} autour de la base.")
                    continue  # Passer au robot suivant
                
               

                if len(chemin) > 1:  # Le premier élément est la position actuelle
                    next_position = chemin[1]  # Prochaine étape
                    nx, ny = next_position

                    if nouvelle_grille[nx][ny] == '*':  # Vérifiez que la case est libre
                        # Déplacer le robot
                        nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                        nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                        self.robot_positions[index] = (nx, ny)
                        self.position_explore.add(next_position)
                        if not self.mode_silencieux:
                            print(f"Robot {index + 1} déplacé vers {next_position} en direction de la base.")

                    # Recharger si le robot est arrivé près de la base
                    if self.robot_positions[index] == objectif:
                        if not self.mode_silencieux:
                            print(f"Robot {index + 1} se recharge en eau.")
                        robot.recharger()
                        
            else:
                # Le robot éteint les feux voisins (si il y en a)
                feux_eteints = robot.eteindre_feu(nouvelle_grille, position)
                if feux_eteints:
                    if not self.mode_silencieux:
                        print(f"Robot {index + 1} a éteint des feux voisins., eau restante : {robot.eau_actuelle}")

                 # Vérification des survivants adjacents
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.taille and 0 <= ny < self.taille and isinstance(nouvelle_grille[nx][ny], Survivant):
                        # Survivant trouvé : remplacer par une case vide et retourner à la base
                        if not self.mode_silencieux:
                            print(f"Robot {index + 1} a trouvé un survivant en ({nx}, {ny}) et retourne à la base.")
                        nouvelle_grille[nx][ny] = '*'  # Remplace le survivant par une case vide
                        robot.survivant_trouve = True
                        break

                # Vérifiez si le robot a trouvé un survivant
                if robot.survivant_trouve:
                    base_x, base_y = self.base_position

                    # Vérifiez si le robot est déjà sur une case adjacente à la base
                    for dx, dy in directions:
                        nx, ny = base_x + dx, base_y + dy
                        if (x, y) == (nx, ny):
                            if not self.mode_silencieux:
                                print(f"Robot {index + 1} est arrivé à la base avec le survivant.")
                            robot.survivant_trouve = False
                            break  # Arrêt, le robot a accompli sa mission

                    if not robot.survivant_trouve:  # Si le robot est déjà arrivé à la base
                        continue  # Passer au prochain robot

                    # Si le robot n'est pas encore à la base, chercher un chemin
                    chemin = []
                    for dx, dy in directions:
                        nx, ny = base_x + dx, base_y + dy
                        if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
                            objectif = (nx, ny)
                            chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
                            if not self.mode_silencieux:
                                print(f"Chemin trouvé pour le Robot {index + 1} : {chemin}")
                            if chemin:  # Si un chemin valide est trouvé, sortir de la boucle
                                break

                    # Si aucun chemin n'est trouvé, signaler le problème et passer au prochain robot
                    if not chemin:
                        if not self.mode_silencieux:
                            print(f"Aucune case adjacente accessible pour le Robot {index + 1} autour de la base.")
                        continue

                    # Déplacer le robot selon le chemin trouvé
                    if len(chemin) > 1:
                        next_position = chemin[1]
                        nx, ny = next_position
                        nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                        nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                        self.robot_positions[index] = (nx, ny)
                        self.position_explore.add((nx, nx))
                        if not self.mode_silencieux:
                            print(f"Robot {index + 1} se dirige vers la base avec le survivant.")

                
                else:
                    # Le robot choisit une cible
                    cible = robot.choisir_cible(position, feux_attribues)

                    if cible:
                        
                      
                        feux_attribues.add(cible)  # Marquer la cible comme attribuée
                        cible_x, cible_y = cible
                        for dx, dy in directions:
                            nx, ny = cible_x + dx, cible_y + dy
                            if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
                                objectif = (nx, ny)
                                chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
                                if chemin:
                                    break

                        if objectif is None and cible:
                            if not self.mode_silencieux:
                                print(f"Aucune case adjacente disponible pour le Robot {index + 1} autour de la cible {cible}.")
                            continue  # Passer au robot suivant

                        if len(chemin) > 1 and cible:  # Déplacement progressif
                            next_position = chemin[1]
                            nx, ny = next_position
                            nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                            nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                            self.robot_positions[index] = (nx, ny)
                            self.position_explore.add((nx, nx))

                            if not self.mode_silencieux:
                                print(f"Robot {index + 1} se dirige vers la cible en {cible}.")
                    else:
                        
                        def get_non_explored_positions(parcours, taille_grille):
                            """
                            Fonction qui retourne les positions non explorées (adjacentes aux positions parcourues)
                            :param parcours: Liste des positions déjà parcourues, sous forme de tuples (x, y)
                            :param taille_grille: Taille de la grille (ex : 10 pour une grille 10x10)
                            :return: Liste des positions adjacentes non explorées
                            """
                            non_explored_positions = set()  # Utilisation d'un set pour éviter les doublons
                            explored_positions = set(parcours)  # Positions déjà explorées

                            # Directions possibles (haut, bas, gauche, droite)
                            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

                            # Parcourir les positions déjà explorées
                            for x, y in parcours:
                                # Vérifier les positions adjacentes
                                for dx, dy in directions:
                                    nx, ny = x + dx, y + dy

                                    # Vérifier si la nouvelle position est dans les limites de la grille
                                    if 0 <= nx < taille_grille and 0 <= ny < taille_grille:
                                        # Si la position n'a pas encore été explorée, l'ajouter à la liste
                                        if (nx, ny) not in explored_positions:
                                            non_explored_positions.add((nx, ny))

                            # Retourner la liste des positions non explorées
                            return list(non_explored_positions)
                        
                        def choisir_nouvelle_cible(robot, non_explored, cibles_reservees):
                            """Attribue une nouvelle cible au robot parmi les positions non explorées et non réservées."""
                            for cible in non_explored:
                                if cible not in cibles_reservees:
                                    robot.cible_non_explore = cible
                                    cibles_reservees.add(cible)  # Réserver la cible
                                    if not self.mode_silencieux:
                                        print(f"Nouvelle cible pour le Robot : {robot.cible_non_explore}")
                                    return
                            # Aucune cible disponible
                            robot.cible_non_explore = None
                            if not self.mode_silencieux:
                                print("Aucune cible disponible pour ce robot.")
                        
                        def liberer_cible(cibles_reservees, robot):
                            """Libère la cible actuelle du robot."""
                            if robot.cible_non_explore in cibles_reservees:
                                cibles_reservees.remove(robot.cible_non_explore)

                        def est_adjacente(pos1, pos2):
                            """Vérifie si deux positions sont adjacentes."""
                            x1, y1 = pos1
                            x2, y2 = pos2
                            return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
                        
                        non_explored = get_non_explored_positions(self.position_explore, self.taille)
                        
                       
                        if robot.cible_non_explore is not None:
                            cible_x, cible_y = robot.cible_non_explore
                            # Vérifier si le robot est adjacent à la cible
                            if est_adjacente((x, y), (cible_x, cible_y)):
                                self.position_explore.add(robot.cible_non_explore)  # Marquer la cible comme explorée
                                liberer_cible(self.cibles_reservees, robot)  # Libérer la cible atteinte
                                robot.cible_non_explore = None  # Réinitialiser la cible

    
                        if robot.cible_non_explore in self.position_explore or robot.cible_non_explore is None:
                            liberer_cible(self.cibles_reservees, robot)  # Libérer l'ancienne cible
                            non_explored = get_non_explored_positions(self.position_explore, self.taille)
                            choisir_nouvelle_cible(robot, non_explored, self.cibles_reservees)
                            if robot.cible_non_explore is None:
                                if not self.mode_silencieux:
                                    print("Aucune nouvelle cible disponible pour le robot.")
                                continue  # Passer au prochain robot si aucune cible disponible
                                
                        if robot.cible_non_explore:
                            cible_x, cible_y = robot.cible_non_explore
                            objectif = None
                            chemin = []

                            for dx, dy in directions:
                                nx, ny = cible_x + dx, cible_y + dy
                                if 0 <= nx < self.taille and 0 <= ny < self.taille and nouvelle_grille[nx][ny] == '*':
                                    objectif = (nx, ny)
                                    chemin = robot.chercher_chemin((x, y), objectif, self.taille, nouvelle_grille)
                                    if chemin:
                                        break

                            if objectif is None or not chemin:
                                if not self.mode_silencieux:
                                    print(f"Aucune case adjacente accessible pour le Robot {index + 1} autour de la cible {robot.cible_non_explore}.")
                                robot.cible_non_explore = None  # Réinitialiser la cible pour en choisir une nouvelle
                                continue
                            
                            # Vérifier si le chemin vers l'objectif est vide ou inaccessible
                            if not chemin:
                                if not self.mode_silencieux:
                                    print(f"Chemin inaccessible pour le Robot vers {robot.cible_non_explore}. Réinitialisation.")
                                liberer_cible(self.cibles_reservees, robot)
                                robot.cible_non_explore = None
                                continue  # Passer au prochain robot

                            if len(chemin) > 1:  # Déplacement progressif
                                next_position = chemin[1]
                                nx, ny = next_position
                                nouvelle_grille[x][y] = '*'  # Laisser la position actuelle vide
                                nouvelle_grille[nx][ny] = robot  # Déplacer le robot
                                self.robot_positions[index] = (nx, ny)
                                self.position_explore.add((nx, ny))
                                if not self.mode_silencieux:
                                    print(f"Robot {index + 1} se dirige vers la cible non explorée en {robot.cible_non_explore}.")
            
        # Remplacer self.grille par la version mise à jour
        self.grille = nouvelle_grille
        
    def verifier_fin(self):
        """Vérifie si la simulation doit se terminer."""
        
        # Vérifier s'il reste des feux ou des survivants
       
        reste_feux = any(isinstance(cell, Feu) for row in self.grille for cell in row)
        reste_survivants = any(isinstance(cell, Survivant) for row in self.grille for cell in row)
        if reste_feux or reste_survivants:
            return False  # La simulation continue

        

        # Si aucun feu, aucun survivant et tous les robots sont statiques, la simulation est terminée
        return True


    