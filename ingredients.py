import numpy as np

class Ingredients:
    '''
    Class for calculations of ingredients inside an area.
    '''

    def __init__(self, pizza_lines):
        self._lines = [list(l) for l in pizza_lines]
        self._unique, self._map = np.unique(self._lines, return_inverse=True)
        self._map = self._map.reshape((len(self._lines),len(self._lines[0])))
        self.shape = self._map.shape

        self.total = self.shape[0]*self.shape[1]
        self.total_unique = np.max(self._map)+1

        self.initialize()

    def initialize(self):
        '''
        Create an array for faster calculation of ingredients inside an area.
        '''

        from_origin = np.zeros((*self.shape, self.total_unique))

        for r in range(self.shape[0]):
            for c in range(self.shape[1]):
                ingredient_id = self._map[r][c]
                from_origin[r][c][ingredient_id] = 1
                if r > 0:
                    from_origin[r][c] += from_origin[r-1][c]
                if c > 0:
                    from_origin[r][c] += from_origin[r][c-1]
                if r > 0 and c > 0:
                    from_origin[r][c] -= from_origin[r-1][c-1]

        self._from_origin = from_origin

    def of(self, slice):
        '''
        Return 1d array of number of ingredients, so i-th element is the number of
        ingredient with id i inside specified slice.
        '''

        ingredients_inside_slice = np.copy(self._from_origin[
                slice.r1,
                slice.c1])

        if slice.r0 > 0:
            ingredients_inside_slice -= self._from_origin[slice.r0-1][slice.c1]
        if slice.c0 > 0:
            ingredients_inside_slice -= self._from_origin[slice.r1][slice.c0-1]
        if slice.r0 > 0 and slice.c0 > 0:
            ingredients_inside_slice += self._from_origin[slice.r0-1][slice.c0-1]

        return ingredients_inside_slice
