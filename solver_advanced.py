from utils import *
import numpy as np
from time import time
from random import shuffle

class CustomWall(Wall):
    """ 
    You are completely free to extend classes defined in utils,
    this might prove useful or enhance code readability
    """
    def __init__(self, w, h):
        super().__init__(w, h)
        self.matrix_place = np.zeros((w, h))
        self.coins_bas_gauche = set()
        self.coins_bas_gauche.add((0, 0))


    def maj_ajout_artpiece(self, art_piece, x, y):
        """
        Ajout du tableau art_piece au mur à la coordonnée (x,y) si c'est possible. Mise à jour de la liste des coins.

        Args:
            art_piece (ArtPiece): le tableau à ajouter
            x, y (int): les coordonnées sur le mur où ajouter le coin inférieur gauche du tableau

        Returns:
            faisable (Bool): l'ajout est possible (et fait) ou non
        """
        w, h = art_piece.width(), art_piece.height()

        # Vérification de la possibilité d'ajout
        if (y + art_piece.height() > self.height() or                     # Dépassement
            x + art_piece.width() > self.width() or
            np.count_nonzero(self.matrix_place[x:x+w, y:y+h] == 0) != w*h # Chevauchement
            ):
            return False
        
        # Ajout du tableau au dictionnaire du mur
        self._artpieces[art_piece.get_idx()] = (x,y)

        # Mise à jour de la matrice de masque
        self.matrix_place[x:x+w, y:y+h] = 1

        # Mise à jour de la liste des coins
        self.coins_bas_gauche.discard((x, y))
        if y + art_piece.height() < self.height() and x + art_piece.width() <= self.width(): # Sanity check pour éviter les erreur d'OOB
            # Coin à en haut-gauche de la pièce
            if self.matrix_place[x, y + art_piece.height()] == 0:
                self.coins_bas_gauche.add((x, y + art_piece.height()))
            
            # Coins en haut de la pièce
            for i in range(art_piece.width()):
                if x + i > 0:
                    if (self.matrix_place[x + i - 1, y + art_piece.height()] == 1 and 
                        self.matrix_place[x + i, y + art_piece.height()] == 0):
                        self.coins_bas_gauche.add((x + i, y + art_piece.height()))
        
        if x + art_piece.width() < self.width() and y + art_piece.height() <= self.height(): # Sanity check 2
            # Coin en bas-droite de la pièce
            if self.matrix_place[x + art_piece.width(), y] == 0:
                self.coins_bas_gauche.add((x + art_piece.width(), y))
            
            # Coins à droite de la pièce
            for j in range(art_piece.height()):
                if y + j > 0:
                    if (self.matrix_place[x + art_piece.width(), y + j - 1] == 1 and
                        self.matrix_place[x + art_piece.width(), y + j] == 0):
                        self.coins_bas_gauche.add((x + art_piece.width(), y + j))
        
        return True


def build(instance, artpieces) -> List:
    """
    Génère l'ensemble des murs nécessaires pour placer les tableaux présentés dans l'ordre de artpieces.

    Args:
        instance (Instance): L'instance du problème à résoudre
        artpieces (List): Liste ordonnée d'items de dictionnaire (index, ArtPiece), qui sont les tableaux à placer
    
    Returns:
        walls (List[CustomWall]): Liste de murs avec tous les tableaux de artpieces
    """
    walls = []
    wallw, wallh = instance.wall.width(), instance.wall.height()

    for _, art_piece in artpieces:
        placed = False
        
        # Pour chaque tableau on essaye de le mettre sur un mur deja occupé
        for wall in walls:
            coins = list(wall.coins_bas_gauche)
            num_coin = 0

            while not placed and num_coin < len(coins) :
                x, y = coins[num_coin]
                placed = wall.maj_ajout_artpiece(art_piece, x, y)
                num_coin += 1

        # Sinon on la met sur un nouveau mur
        if not placed:
            walls.append(CustomWall(wallw, wallh))
            _ = walls[-1].maj_ajout_artpiece(art_piece, 0, 0)
    
    return walls


def initial_greedy(instance: Instance) -> List:
    """
    Génère une solution initiale gloutonne en classant les tableaux par surface décroissante.

    Args:
        instance (Instance): L'instance du problème à résoudre
    
    Returns:
        artpieces (List): Liste ordonnée d'items de dictionnaire (index, ArtPiece), qui sont les tableaux à placer
    """
    artpieces = sorted(instance.artpieces_dict.items(),
                       key = lambda x: instance.artpieces_dict[x[0]].width()*instance.artpieces_dict[x[0]].height(),
                       reverse = True)
    
    return artpieces


def deux_swap(artpieces):
    """
    Génère une liste de voisins de la solution artpieces en échangeant pour chaque voisin 2 tableaux distincts.

    Args:
        artpieces (List): Liste d'items de dictionnaire (index, ArtPiece), solution actuelle.
    
    Returns:
        deux_swap_neigh (List[List]) : Liste de voisins de artpieces.
    """
    n = len(artpieces)
    deux_swap_neigh = []
    artpieces = list(artpieces)
    for i in range(n):
        for j in range(i+1,n):
            neigh = artpieces.copy()
            neigh[i] = artpieces[j]
            neigh[j] = artpieces[i]
            deux_swap_neigh.append(neigh)

    return deux_swap_neigh


def metric(instance, voisin):
    """
    Métrique d'évaluation : moyenne du nombre de tableaux au carré sur chaque mur.
    """
    walls = build(instance, voisin)

    return sum([len(wall._artpieces)**2 for wall in walls])/len(walls)


def solve(instance: Instance) -> Solution:
    """
    Args:
        instance (Instance): An Instance object containing all you need to solve the problem

    Returns:
        Solution: A solution object initialized with 
                  a list of tuples of the form (<artipiece_id>, <wall_id>, <x_pos>, <y_pos>)
    """
    # Métriques de temps d'exécution
    t0 = time()
    iteration_duration = 0

    if 'hard' in instance.filepath:
        credit_temps = 300
    else:
        credit_temps = 60

    # Initialisation gloutonne
    artpieces = initial_greedy(instance)
    value = metric(instance, artpieces)

    best_value = value
    best_artpieces = artpieces.copy()
    
    while ((time()-t0) + iteration_duration) < credit_temps-5:
        non_improving_steps = 0
        
        while non_improving_steps < 10 and ((time()-t0) + iteration_duration) < credit_temps-5:
            # Temps de départ d'une itération
            t1 = time()

            voisins = deux_swap(artpieces)

            # On classe les voisins selon la métrique, et on garde le meilleur
            voisins = sorted(voisins, key = lambda x: metric(instance,x), reverse = True)

            non_improving_steps += 1

            if metric(instance, voisins[0]) > value:
                value = metric(instance, voisins[0]) # Pas optimal mais peu coûteux à évaluer devant l'évaluation de tous les voisins.
                artpieces = voisins[0]
                non_improving_steps = 0

            iteration_duration = time() - t1

        # Mise à jour de la meilleure solution trouvée à date
        if value > best_value:
            best_value = value
            best_artpieces = artpieces
        
        # Restart
        artpieces = list(instance.artpieces_dict.items())
        shuffle(artpieces)
        value = metric(instance, artpieces)
    
    # Générer la solution optimale contenue dans best_artpieces
    walls = build(instance, best_artpieces)
    solution = []
    for i in range(len(walls)):
        solution += walls[i].gen_for_solution(i)

    return Solution(solution)
