from utils import *
import numpy as np

class CustomWall(Wall):

    """ You are completely free to extend classes defined in utils,
        this might prove useful or enhance code readability
    """
    def __init__(self, w, h):
        super().__init__(w, h)
        self.matrix_place = np.zeros((w, h))
        self.max_rect_size = (w, h)
        self.max_rect_coord = (0, 0)

    def maj_ajout_artpiece(self, art_piece,x,y):
        #ajout du tableau au dictionnaire du mur
        self._artpieces[art_piece.get_idx()] = (x,y)

        #mise a jour de la matrice de masque
        w, h = art_piece.width(), art_piece.height()
        self.matrix_place[x:x+w, y:y+h] = 1

        self.max_rect_size, self.max_rect_coord = self.maximalRectangle()
    

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

        return max_rect_size, max_rect_coord


    
    

    
def solve(instance: Instance) -> Solution:
    """Write your code here

    Args:
        instance (Instance): An Instance object containing all you need to solve the problem

    Returns:
        Solution: A solution object initialized with 
                  a list of tuples of the form (<artipiece_id>, <wall_id>, <x_pos>, <y_pos>)
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

        
    solution = []
    for i in range(len(walls)):
        solution += walls[i].gen_for_solution(i)

    return Solution(solution)
