import random
from feu import Feu

class Robot:
    def __init__(self):
        self.symbole = 'R'

    def se_deplacer(self, grille, position_actuelle):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Haut, Bas, Gauche, Droite
        ]
        x, y = position_actuelle
        random.shuffle(directions)  # Mélanger les directions pour un mouvement aléatoire

        print(f"Robot essaie de se déplacer depuis {position_actuelle}")
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grille) and 0 <= ny < len(grille) and grille[nx][ny] == '*':
                print(f"Robot se déplace vers {(nx, ny)}")
                return nx, ny  # Retourner la nouvelle position valide

        print("Aucune position valide, le robot reste en place.")
        return x, y  # Si aucun mouvement valide, rester en place


    def eteindre_feu(self, grille, position_actuelle):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Haut, Bas, Gauche, Droite
        ]
        x, y = position_actuelle

        # Parcourir les cases adjacentes
        print("eteindreappeler")
        for dx, dy in directions:
            nx, ny = x + dx, y + dy    
            if 0 <= nx < len(grille) and 0 <= ny < len(grille[0]) and isinstance(grille[nx][ny], Feu):
                # Remplacer le feu par une case vide
                grille[nx][ny] = '*'
                print(f"Feu éteint à la position ({nx}, {ny})")