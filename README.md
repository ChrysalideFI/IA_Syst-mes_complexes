# IA_Systemes_complexes
Système d’Exploration Autonome par Robots d’Essaim pour la Gestion d’Incendies. 

# note

grille AC - case feu
	  - case arbre
	  - case Robot
	  - case QG
	  
	Règle de la modélisation du feu :
	Génération d'arbre aléatoirement sur la grille

	Arbre à feu :
		Si une cellule est un arbre à l’instant t et a au moins un voisin en feu , elle prend
		feu à l’instant t+1, devenant ainsi une cellule en feu.

	Feu à vide :
		Si une cellule est en feu à l’instant t et a au moins un robot en voisin , elle devient
		vide à l’instant t+1.
	
	
	Grille --> Modéliser le feu/arbre --> QG + 1 seul robot --> QG + pleins de robots 
