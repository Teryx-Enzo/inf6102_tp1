from utils import *
import numpy as np
from random import choice, choices, shuffle
from tqdm import tqdm

class CustomWall(Wall):
    """ 
    You are completely free to extend classes defined in utils,
    this might prove useful or enhance code readability
    """

    def __init__(self, w, h):
        super().__init__(w, h)
        self.matrix_place = np.zeros((w, h))
        self.max_rect_size = (w, h)
        self.max_rect_coord = (0, 0)
        self.coins_bas_gauche = set() ; self.coins_bas_gauche.add((0, 0))

    def count(self):
        return len(self._artpieces)

    def taux_remplissage(self):

        compte = np.count_nonzero(self.matrix_place==0)
        w,h = self.max_rect_size
        area = w*h
        
        if area > 0:
            return area/compte
        else:
            return 0
        
    def maj_ajout_artpiece(self, art_piece, x, y):
        #ajout du tableau au dictionnaire du mur
        self._artpieces[art_piece.get_idx()] = (x,y)

        #mise a jour de la matrice de masque
        w, h = art_piece.width(), art_piece.height()
        self.matrix_place[x:x+w, y:y+h] = 1

        self.max_rect_size, self.max_rect_coord = self.maximalRectangle()

        # Mise à jour de la liste des coins
        self.coins_bas_gauche.discard((x, y))
        if y + art_piece.height() < self.height() and x + art_piece.width() <= self.width(): # Sanity check pour éviter les erreur d'OOB
            
            # Coin à en haut-gauche de la pièce
            if self.matrix_place[x, y + art_piece.height()] == 0:
                self.coins_bas_gauche.add((x, y + art_piece.height()))
            
            # Coin en haut de la pièce
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
                
            #print(self.matrix_place, self.coins_bas_gauche)
            #input('e')
    

    def retrait_artpiece(self, art_piece):
        x, y = self._artpieces[art_piece.get_idx()]

        # Mise à zéro de la matrice de masque
        w, h = art_piece.width(), art_piece.height()
        self.matrix_place[x:x+w, y:y+h] = 0

        # Suppression de la pièce
        self._artpieces.pop(art_piece.get_idx())

        self.max_rect_size, self.max_rect_coord = self.maximalRectangle()

        # Mise à jour de la liste des coins
        self.coins_bas_gauche.add((x, y))  # Rajout des coordonnées du tableau dans la liste des coins

        for i in range(art_piece.width()):
            self.coins_bas_gauche.discard((x + i, y + art_piece.height()))
        
        for j in range(art_piece.height()):
            self.coins_bas_gauche.discard((x + art_piece.width(), y + j))

        return x, y # Pour pouvoir éventuellement annuler

    def maximalRectangle(self):
        """
        Retourne la zone rectangulaire remplie de 0 la plus grande sur le mur.

        Hypothèse simplificatrice : on remplit toujours le mur par le coin inférieur gauche.
            - on peut parcourir la matrice une seule fois pour obtenir les régions contiguës de 0 (heights)
            - on peut déduire rapidement la taille et la coordonnée des zones de 0 avec les valeurs contiguës dans heights.
        """

        heights = [0] * self._w
        for j in range(self._h):
            for i in range(self._w):
                if self.matrix_place[i][j] == 0:
                    heights[i] = heights[i] + 1
                else:
                    heights[i] = 0

        if heights[0] > 0:
            max_rect_size = (self._w, heights[0])
            max_rect_coord = (0, self._h - heights[0])
        else:
            max_rect_size = (0, 0)
            max_rect_coord = (None, None)

        for h in range(1, self._w):
            if heights[h] > max_rect_size[1]:
                # On teste seulement pour une section de hauteur différente (sinon, c'est la même qu'avant mais tronquée)
                if heights[h]*(self._w - h + 1) > max_rect_size[0]*max_rect_size[1]:
                    max_rect_size = (self._w - h, heights[h])
                    max_rect_coord = (h, self._h - heights[h])
            elif heights[h] < max_rect_size[1]:
                max_rect_size = (self._w - h, heights[h])
                max_rect_coord = (max_rect_coord[0], self._h - heights[h])

        return max_rect_size, max_rect_coord


def initial_naive(instance: Instance) -> List:
    walls = []
    wallw, wallh = instance.wall.width(), instance.wall.height()
    
    for i in instance.artpieces_dict:
        walls.append(CustomWall(wallw, wallh))
        walls[-1].maj_ajout_artpiece(instance.artpieces_dict[i], 0, 0)

    return walls


def initial_greedy(instance,artpieces) -> List:
    """
    Génère une solution initiale gloutonne en plaçant les tableaux par surface décroissante.
    """
    walls = []
    wallw, wallh = instance.wall.width(), instance.wall.height()

    

    #Pour chaque oeuvre on essaye de la mettre sur un mur deja occupe
    for _, art_piece in artpieces:
        art_piece.width(), art_piece.height()
        
        placed = False
        w,h  = art_piece.width(), art_piece.height()
        
        #Pour chaque oeuvre on essaye de la mettre sur un mur deja occupe
        for wall in walls:
            if not placed :

                x, y = wall.max_rect_coord
                W, H = wall.max_rect_size

                if w <= W and h <= H:
                    wall.maj_ajout_artpiece(art_piece, x, y)
                    placed = True

        #sinon on la met sur un nouveau mur
        if not placed:
            walls.append(CustomWall(wallw, wallh))
            walls[-1].maj_ajout_artpiece(art_piece, 0, 0)

    for wall in walls:
        wall.coins_bas_gauche.add(wall.max_rect_coord)
    
    return walls

def initial_walls(instance: Instance) -> List:
    """
    Génère une solution initiale gloutonne en plaçant les tableaux par surface décroissante.
    """
    walls = []
    wallw, wallh = instance.wall.width(), instance.wall.height()

    # Tri des tableaux par aire décroissante.
    artpieces = sorted(instance.artpieces_dict.items(),
                       key = lambda x: instance.artpieces_dict[x[0]].width()*instance.artpieces_dict[x[0]].height(),
                       reverse = True)
    
    shuffle(list(instance.artpieces_dict.items()))
    
    return artpieces

def deux_swap(artpieces):
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

    walls = initial_greedy(instance,voisin)

    return sum([wall.count()**2 for wall in walls])

def solve(instance: Instance) -> Solution:
    """Write your code here

    Args:
        instance (Instance): An Instance object containing all you need to solve the problem

    Returns:
        Solution: A solution object initialized with 
                  a list of tuples of the form (<artipiece_id>, <wall_id>, <x_pos>, <y_pos>)
    """

    nb_iter = 3
    artpieces = initial_walls(instance)
    walls = initial_greedy(instance,artpieces)



    value = len(walls)
    for i in tqdm(range(nb_iter)):

        print("génération de 2 swap")
        voisins = deux_swap(artpieces)
        shuffle(voisins)
        voisins = voisins
        #print([metric(instance,x) for x in voisins])
        print("Evaluation des voisins")
        voisins = sorted(voisins, key = lambda x: metric(instance,x), reverse = True)
        #a = [(voisin, metric(instance,voisin)) for voisin in voisins]
        #print(a)
        print("Choix du meilleur")
        artpieces = voisins[0]
        #print(metric(instance,artpieces))
    walls = initial_greedy(instance,artpieces)
    
    # Regénérer la solution avec la dernière configuration autorisée (stockée dans walls)
    solution = []
    for i in range(len(walls)):
        solution += walls[i].gen_for_solution(i)

    return Solution(solution)
