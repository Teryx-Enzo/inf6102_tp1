from utils import *
import numpy as np
from random import choice, choices
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
        
        
        return len(list(self._artpieces))
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
            
            if x > 0:
                # Coin en haut de la pièce
                for i in range(art_piece.width()):
                    if (self.matrix_place[x + i - 1, y + art_piece.height()] == 1 and 
                        self.matrix_place[x + i, y + art_piece.height()] == 0):
                        self.coins_bas_gauche.add((x + i, y + art_piece.height()))
        
        if x + art_piece.width() < self.width() and y + art_piece.height() <= self.height(): # Sanity check 2
            # Coin en bas-droite de la pièce
            if self.matrix_place[x + art_piece.width(), y] == 0:
                self.coins_bas_gauche.add((x + art_piece.width(), y))
            
            if y > 0:
                # Coins à droite de la pièce
                for j in range(art_piece.height()):
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


def initial_greedy(instance: Instance) -> List:
    """
    Génère une solution initiale gloutonne en plaçant les tableaux par surface décroissante.
    """
    walls = []
    wallw, wallh = instance.wall.width(), instance.wall.height()

    # Tri des tableaux par aire décroissante.
    artpieces = sorted(instance.artpieces_dict.items(),
                       key = lambda x: instance.artpieces_dict[x[0]].width()*instance.artpieces_dict[x[0]].height(),
                       reverse = True)

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


def solve(instance: Instance) -> Solution:
    """Write your code here

    Args:
        instance (Instance): An Instance object containing all you need to solve the problem

    Returns:
        Solution: A solution object initialized with 
                  a list of tuples of the form (<artipiece_id>, <wall_id>, <x_pos>, <y_pos>)
    """
    walls = initial_greedy(instance)
    value = 0

    for wall in walls:
        value += wall.count()**2

    for _ in tqdm(range(1000)): # Critère d'arrêt à définir
        temp_walls = walls.copy()

        # À étoffer : choisir un mur de départ et un mur cible en particulier !
        o = choices(range(len(temp_walls)), weights=[1/(wall.count()**2) for wall in temp_walls])[0]
        
        old_wall = temp_walls[o]
        
        new_wall_chosen = False

        #on choisit un nouveau mur a condition qu'il reste des coins de libres
        while not new_wall_chosen : 
            try : 
                n = choice(range(len(temp_walls)))  # Choisir 2 murs distincts ou non
                new_wall = temp_walls[n]
                coin_bg = choice(list(new_wall.coins_bas_gauche))
                new_wall_chosen = True

            except Exception as e:
                new_wall_chosen = False

        

        # À étoffer aussi : heuristique pr choisir un bon tableau
        art = choice(list(old_wall._artpieces)) # On ne récupère que l'index
        x, y = old_wall.retrait_artpiece(instance.artpieces_dict[art])
        
        #print(new_wall.coins_bas_gauche, coin_bg, instance.artpieces_dict[art].width(), instance.artpieces_dict[art].height())
        new_wall.maj_ajout_artpiece(instance.artpieces_dict[art], *coin_bg)

        solution = []
        new_value = 0
        for i in range(len(temp_walls)):
            solution += temp_walls[i].gen_for_solution(i)
            new_value += temp_walls[i].count()**2
        
        if instance.is_valid_solution(Solution(solution)) and new_value >= value:
            if len(old_wall._artpieces) == 0:
                temp_walls.remove(old_wall)
            walls = temp_walls
            value = new_value
            print(new_value)
        else:
            _, _ = new_wall.retrait_artpiece(instance.artpieces_dict[art])
            old_wall.maj_ajout_artpiece(instance.artpieces_dict[art], x, y)
    
    # Regénérer la solution avec la dernière configuration autorisée (stockée dans walls)
    solution = []
    for i in range(len(walls)):
        solution += walls[i].gen_for_solution(i)

    return Solution(solution)
