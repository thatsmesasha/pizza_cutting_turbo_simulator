from src.pizza import Pizza, Direction

import numpy as np
import json

POSITIVE_REWARD = 1.0
NEUTRAL_REWARD  = 0.0
NEGATIVE_REWARD = -0.1

class ActionNotFoundException(Exception):
    pass

class GoogleEngineer:
    def __init__(self, pizza_config):
        self.pizza = Pizza(pizza_config['pizza_lines'])
        self.min_each_ingredient_per_slice = pizza_config['l']
        self.max_ingredients_per_slice = pizza_config['h']
        self.cursor_position = (0,0)
        self.slice_mode = False
        self.valid_slices = []
        self.score = 0

    def score_of(self, slice):
        if min(self.pizza.ingredients.of(slice)) >= self.min_each_ingredient_per_slice:
            return slice.ingredients
        return 0

    def increase(self, direction):
        slice = self.pizza.slice_at(self.cursor_position)
        new_slice = self.pizza.increase(slice, direction, self.max_ingredients_per_slice)
        if (new_slice is not None and min(self.pizza.ingredients.of(new_slice)) >=
            self.min_each_ingredient_per_slice):

            if slice in self.valid_slices:
                self.valid_slices.remove(slice)
            self.valid_slices.append(new_slice)
            score = self.score_of(new_slice) - self.score_of(slice)
            self.score += score
            return score * POSITIVE_REWARD
        return NEUTRAL_REWARD if new_slice is not None else NEGATIVE_REWARD

    def do(self, action):
        if action not in ['right', 'down', 'next']:
            raise ActionNotFoundException('Action \'{}\' is not recognised.'.format(action))

        if action == 'next':
            ri, ci = self.cursor_position
            self.cursor_position = (ri,ci+1) if ci+1 < self.pizza.c else (ri+1,0)
            return NEUTRAL_REWARD

        reward = self.increase(Direction[action])
        return reward

    def state(self):
        return {
            'ingredients_map': self.pizza.ingredients._map.tolist(),
            'slices_map': self.pizza._map.tolist(),
            'cursor_position': self.cursor_position,
            'slice_mode': self.slice_mode,
            'min_each_ingredient_per_slice': self.min_each_ingredient_per_slice,
            'max_ingredients_per_slice': self.max_ingredients_per_slice,
        }

    def is_done(self):
        ri,ci = self.cursor_position
        return self.cursor_position == (self.pizza.r-1,self.pizza.c-1) or \
            (np.min(self.pizza._map[ri][ci:]) != -1 and ri == self.pizza.r-1) or \
            (np.min(self.pizza._map[ri][ci:]) != -1 and np.min(self.pizza._map[ri+1:]) != -1)
