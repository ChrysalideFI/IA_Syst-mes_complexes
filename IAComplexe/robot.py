import random
from feu import Feu
from color import Color
from queue import PriorityQueue

class Robot:
    def __init__(self):
        self.symbole = Color.CYAN + 'R' + Color.END
        self.eau_max = 3  # Quantité d'eau maximale
        self.eau_actuelle = 0
        self.survivant = None  # Survivant que le robot transporte
        self.carte_feux = None  # Carte des feux reçue depuis la base

    def recevoir_carte(self, carte_feux):
        """Reçoit la carte des feux de la base."""
        self.carte_feux = carte_feux
        print("Carte des feux mise à jour pour le robot.")

    def sauver_survivant(self, grille, position_actuelle):
        """Sauve un survivant et le ramène à la base."""
        x, y = position_actuelle
        if grille[x][y] == 'S':  # Vérifie s'il y a un survivant
            if self.eau_actuelle > 0:
                self.survivant = (x, y)
                grille[x][y] = '*'  # Enleve le survivant de la grille
                print(f"Survivant trouvé à {position_actuelle} et pris en charge par le robot.")
                return True
        return False
    
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
    
    def sauver_survivant(self, grille, position_actuelle):
        """Le robot agit en fonction de sa situation."""
        if self.survivant:
            # Retourner à la base avec le survivant
            base_x, base_y = self.base_position
            if position_actuelle == (base_x, base_y):
                print("Survivant déposé à la base.")
                self.survivant = None
            else:
                return self.se_deplacer_vers_base(grille, position_actuelle)
        else:
            # Sauver un survivant si possible
            if self.sauver_survivant(grille, position_actuelle):
                return self.se_deplacer_vers_base(grille, position_actuelle)
            else:
                return self.se_deplacer(grille, position_actuelle)

    def se_deplacer_vers_base(self, grille, position_actuelle):
        """Se déplacer vers la base."""
        base_x, base_y = self.base_position
        x, y = position_actuelle
        if x < base_x:
            return x + 1, y
        elif x > base_x:
                 return x - 1, y
        elif y < base_y:
            return x, y + 1
        elif y > base_y:
            return x, y - 1
        return x, y  # Rester en place si déjà à la base

    def eteindre_feu(self, grille, position_actuelle):
        if self.eau_actuelle <= 0:
            print("Le robot n'a plus d'eau et doit se recharger.")
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
                print(f"Feu éteint à la position ({nx}, {ny}), eau restante : {self.eau_actuelle}")
                return True  # Feu éteint avec succès

        return False  # Aucun feu éteint
    
    def recharger(self):
        print("Le robot se recharge en eau.")
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
