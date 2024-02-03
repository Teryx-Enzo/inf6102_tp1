from utils import *

class CustomWall(Wall):

    """ You are completely free to extend classes defined in utils,
        this might prove useful or enhance code readability
    """
    def __init__(self, w, h):
        super().__init__(w, h)
        self.max_rect = (w,h)
        self.coord_max_rect = (0,0)

    def maj_ajout_mur(self, art_piece_id,x,y,w,h):
        self._artpieces[art_piece_id] = ()
    

    def maximalRectangle(matrix):
    

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

        return max_area, max_area_coordinates

    

    
def solve(instance: Instance) -> Solution:
    """Write your code here

    Args:
        instance (Instance): An Instance object containing all you need to solve the problem

    Returns:
        Solution: A solution object initialized with 
                  a list of tuples of the form (<artipiece_id>, <wall_id>, <x_pos>, <y_pos>)
    """
    raise Exception('This should be implemented')
