from src.ingredients import Ingredients

import numpy as np
from enum import Enum

class Direction(Enum):
    right = 0
    down  = 1
    left  = 2
    up    = 3

    @classmethod
    def opposite(cls, direction):
        return ({
            cls.right: cls.left,
            cls.down: cls.up,
            cls.left: cls.right,
            cls.up: cls.down,
        })[direction]

class Slice:
    delta_increase_slice = {
        Direction.right: (0,0,0,1),
        Direction.down:  (0,0,1,0),
        Direction.left:  (0,-1,0,0),
        Direction.up:    (-1,0,0,0),
    }

    delta_side_fn = {
        Direction.right:  lambda r0,c0,r1,c1: (r0,c1+1,r1,c1+1),
        Direction.down: lambda r0,c0,r1,c1: (r1+1,c0,r1+1,c1),
        Direction.left:   lambda r0,c0,r1,c1: (r0,c0-1,r1,c0-1),
        Direction.up:    lambda r0,c0,r1,c1: (r0-1,c0,r0-1,c1),
    }

    def __init__(self, r0, c0, r1, c1):
        self.r0 = r0
        self.c0 = c0
        self.r1 = r1
        self.c1 = c1

        self.as_tuple = (r0, c0, r1, c1)
        self.ingredients = (self.r1-self.r0+1) * (self.c1-self.c0+1)

    def increase(self, direction):
        return Slice(*tuple(x0+x1 for x0,x1 in zip(self.as_tuple, self.delta_increase_slice[direction])))

    def side(self, direction):
        return Slice(*self.delta_side_fn[direction](*self.as_tuple))

    def is_within(self, slice):
        return \
            self.r0 >= slice.r0 and \
            self.c0 >= slice.c0 and \
            self.r1 <= slice.r1 and \
            self.c1 <= slice.c1

    def __str__(self):
        return '{} {} {} {}'.format(*self.as_tuple)

class Pizza:
    def __init__(self, pizza_lines):
        self.ingredients = Ingredients(pizza_lines)

        self.r, self.c = self.ingredients.shape

        self._dict = {}
        self._map = np.full((self.r,self.c), -1)
        self._map_can_increase = np.full((self.r,self.c,4), False)
        self._map_can_increase[:,:-1,Direction.right.value] = True
        self._map_can_increase[:-1,:,Direction.down.value] = True
        self._map_can_increase[:,1:,Direction.left.value] = True
        self._map_can_increase[1:,:,Direction.up.value] = True

        self.huge_slice = Slice(0,0,self.r-1,self.c-1)

    def slice_ids_in(self, slice):
        slice_ids = list(np.unique(self._map[
            slice.r0:slice.r1+1,
            slice.c0:slice.c1+1]))
        if -1 in slice_ids:
            slice_ids.remove(-1)
        return slice_ids

    def disable_increase_of(self, slice, direction):
        self._map_can_increase[
            slice.r0:slice.r1+1,
            slice.c0:slice.c1+1,
            direction.value] = False

    def disable_increase_around(self, slice, direction, max_ingredients):
        side = slice.side(direction)
        side_increase_direction = Direction.opposite(direction)

        # if on the edge of the pizza
        if not side.is_within(self.huge_slice):
            self.disable_increase_of(slice, direction)
            return

        # if cannot increase anymore because of the max ingredients per slice
        if slice.ingredients + side.ingredients > max_ingredients:
            self.disable_increase_of(slice, direction)

        # disable for all side slices
        side_slice_ids = self.slice_ids_in(side)
        for slice_id in side_slice_ids:
            self.disable_increase_of(self._dict[slice_id], side_increase_direction)
        self.disable_increase_of(side, side_increase_direction)

        # disable for slice if there are slices on the side
        if len(side_slice_ids) > 0:
            self.disable_increase_of(slice, direction)

    def slice_at(self, position):
        ri, ci = position
        slice_id = self._map[ri][ci]
        if slice_id == -1:
            return Slice(ri,ci,ri,ci)
        return self._dict[slice_id]

    def increase(self, slice, direction, max_ingredients):
        slice_id = slice.r0*self.c+slice.c0
        new_slice = slice.increase(direction)
        new_slice_id = new_slice.r0*self.c+new_slice.c0

        if (self._map_can_increase[slice.r0][slice.c0][direction.value] and
            new_slice.ingredients <= max_ingredients):

            if slice.ingredients>1: del self._dict[slice_id]
            self._dict[new_slice_id] = new_slice

            self._map[
                new_slice.r0:new_slice.r1+1,
                new_slice.c0:new_slice.c1+1] = new_slice_id

            for direction in Direction:
                self.disable_increase_around(new_slice, direction, max_ingredients)
                # print(self._map_can_increase)
                # print('----')

            return new_slice
        return None

    def can_increase_more(self):
        # print(self._map_can_increase)
        return np.any(self._map_can_increase)
