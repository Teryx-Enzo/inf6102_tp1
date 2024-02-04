from utils import *
import numpy as np

class CustomWall(Wall):

    """ You are completely free to extend classes defined in utils,
        this might prove useful or enhance code readability
    """
    def __init__(self, w, h):
        super().__init__(w, h)
        self.matrix_place = np.zeros((w,h))
        self.max_rect = (w,h)
        self.coord_max_rect = (0,0)

    def maj_ajout_artpiece(self, art_piece,x,y):
        print(self.matrix_place)
        #ajout du tableau au dictionnaire du mur
        self._artpieces[art_piece.get_idx()] = (x,y)

        #mise a jour de la matrice de masque
        w,h = art_piece.width(), art_piece.height()
        self.matrix_place[x:x+w,y:y+h] += 1
        self.max_rect, self.coord_max_rect = self.maximalRectangle()
    

    def maximalRectangle(self):
        matrix = self.matrix_place

        
    

        def largestRectangleArea(heights):
            stack = []
            max_area = 0
            max_area_coordinates = (0, 0, 0, 0)  # (x_min, y_min, x_max, y_max)

            for i, h in enumerate(heights + [0]):
                while stack and h < heights[stack[-1]]:
                    height = heights[stack.pop()]
                    width = i if not stack else i - stack[-1] - 1
                    current_area = height * width

                    if current_area > max_area:
                        max_area = current_area
                        max_area_coordinates = (stack[-1] + 1, height, i - 1, height)

                stack.append(i)

            return max_area, max_area_coordinates

        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        max_area = 0
        max_area_coordinates = (0, 0, 0, 0)

        for i in range(rows):
            heights = [0] * cols

            for j in range(cols):
                if matrix[i][j] == 0:
                    heights[j] = heights[j - 1] + 1 if j > 0 else 1

            current_area, current_coordinates = largestRectangleArea(heights)

            if current_area > max_area:
                max_area = current_area
                max_area_coordinates = (current_coordinates[0], i - current_coordinates[1] + 1, current_coordinates[2], i)


        return (max_area_coordinates[2]-max_area_coordinates[0],max_area_coordinates[3]-max_area_coordinates[1]), (max_area_coordinates[0], max_area_coordinates[1])


    
    

    
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

    #Pour chaque oeuvre on essaye de la mettre sur un mur deja occupe
    for id, art_piece in instance.artpieces_dict.items():
        
        placed = False
        w,h  = art_piece.width(), art_piece.height()
        
        #Pour chaque oeuvre on essaye de la mettre sur un mur deja occupe
        for wall in walls:
            if not placed :

                x,y = wall.coord_max_rect
                print(x,y)
                W,H = wall.max_rect
                if w <= W and h<= H:

                    wall.maj_ajout_artpiece(art_piece,x,y)
                    placed = True


        #sinon on la met sur un nouveau mur
        if not placed:
            walls.append(CustomWall(wallw,wallh))
            walls[-1].maj_ajout_artpiece(art_piece,0,0)

    

        
    solution = []
    for i in range(len(walls)):
        solution += walls[i].gen_for_solution(i)

    return Solution(solution)
