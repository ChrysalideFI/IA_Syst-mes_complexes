import random
from feu import Feu
from color import Color
from queue import PriorityQueue
from collections import deque

class Robot:
    def __init__(self):
        self.symbole = Color.CYAN + 'R' + Color.END
        self.eau_max = 3  # Quantité d'eau maximale
        self.eau_actuelle = 0
        self.carte_feux = None  # Carte des feux reçue depuis la base
        self.survivant_trouve = False
        self.exploration_direction = None  # Direction actuelle d’exploration
        self.cible_non_explore = None

    def recevoir_carte(self, carte_feux):
        """Reçoit la carte des feux de la base."""
        self.carte_feux = carte_feux
        

    def se_deplacer(self, grille, position_actuelle):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Haut, Bas, Gauche, Droite
        ]
        x, y = position_actuelle
        random.shuffle(directions)  # Mélanger les directions pour un mouvement aléatoire

        print(f"Robot essaie de se déplacer depuis {position_actuelle}")
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grille) and 0 <= ny < len(grille):
                # Vérifiez que la case cible est vide et non occupée par un autre robot
                if grille[nx][ny] == '*' and not isinstance(grille[nx][ny], Robot):
                    return nx, ny  # Retourner la nouvelle position valide

        print("Aucune position valide, le robot reste en place.")
        return x, y  # Si aucun mouvement valide, rester en place


    def eteindre_feu(self, grille, position_actuelle):
        if self.eau_actuelle <= 0:
            return False

        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Haut, Bas, Gauche, Droite
        ]
        x, y = position_actuelle

        # Parcourir les cases adjacentes
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grille) and 0 <= ny < len(grille[0]) and isinstance(grille[nx][ny], Feu):
                # Remplacer l'objet Feu par une case vide
                grille[nx][ny] = '*'
                self.eau_actuelle -= 1
                
                return True  # Feu éteint avec succès

        return False  # Aucun feu éteint
    
    def recharger(self):
       
        self.eau_actuelle = self.eau_max
        
    def chercher_chemin(self, depart, objectif, taille, grille):
        """Trouve un chemin du point de départ au point objectif en évitant les obstacles. (A*)"""
        def heuristique(a, b):
            # Distance de Manhattan
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def voisins(position):
            x, y = position
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < taille and 0 <= ny < taille and grille[nx][ny] == '*':
                    yield (nx, ny)
                    
        
        # Initialisation
        frontier = PriorityQueue()
        frontier.put((0, depart))
        came_from = {depart: None}
        cost_so_far = {depart: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current == objectif:
                break

            for next in voisins(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristique(next, objectif)
                    frontier.put((priority, next))
                    came_from[next] = current

            # Vérifier si l'objectif est atteignable
        if objectif not in came_from:
            return []  # Retourner une liste vide si aucun chemin n'existe
        
        # Reconstruire le chemin
        chemin = []
        current = objectif
        while current is not None:
            chemin.append(current)
            current = came_from.get(current)
        chemin.reverse()

        return chemin
    
    def choisir_cible(self, position, feux_attribues):
        """Choisit une cible parmi les feux disponibles, en évitant ceux déjà attribués."""
        x, y = position #position du robot
        cibles_potentielles = [
            (i, j) for i, ligne in enumerate(self.carte_feux)
            for j, feu in enumerate(ligne) if feu is not None and (i, j) not in feux_attribues
        ]

        if not cibles_potentielles:
            return None  # Aucun feu disponible

        # Trouver la cible la plus proche
        cible = min(
            cibles_potentielles,
            key=lambda coord: abs(coord[0] - x) + abs(coord[1] - y)  # Distance de Manhattan
        )
        return cible

    

    def explorer(self, grille, position):
        """Effectue une exploration systématique et évite les allers-retours infinis."""
        x, y = position

        # Limiter la profondeur de récursion pour éviter la boucle infinie
        if self.exploration_direction is None:
            self.exploration_direction = (0, 1)  # Direction initiale : droite

        # Définir une fonction pour vérifier si une case est valide
        def position_valide(nx, ny):
            return 0 <= nx < len(grille) and 0 <= ny < len(grille[0]) and grille[nx][ny] == '*'

        # Essayer différentes directions : droite, bas, gauche, haut
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for direction in directions:
            dx, dy = direction
            nx, ny = x + dx, y + dy

            # Si la nouvelle position est valide (case libre et dans les limites)
            if position_valide(nx, ny):
                self.exploration_direction = direction  # Mettre à jour la direction
                return (nx, ny)

        # Si aucune direction n'est valide (toutes les cases autour sont occupées)
        # Le robot reste sur place, mais on doit éviter l'aller-retour constant.
        # On va ajouter un peu plus de logique pour gérer les allers-retours
        if self.exploration_direction == (0, 1):  # Si la direction actuelle est droite
            self.exploration_direction = (1, 0)  # Passer à bas
        elif self.exploration_direction == (1, 0):  # Si la direction actuelle est bas
            self.exploration_direction = (0, -1)  # Passer à gauche
        elif self.exploration_direction == (0, -1):  # Si la direction actuelle est gauche
            self.exploration_direction = (-1, 0)  # Passer à haut
        else:
            self.exploration_direction = (0, 1)  # Réinitialiser à droite

        # Recalculer la prochaine position dans la nouvelle direction
        dx, dy = self.exploration_direction
        nx, ny = x + dx, y + dy

        # Assurez-vous que la nouvelle position est valide
        if position_valide(nx, ny):
            return (nx, ny)

        return position  # Si aucune direction n'est valide, rester sur place








