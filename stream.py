import numpy as np
import os
import json
import time

class ServePizza:

    r_scale = 3
    c_scale = 6

    def initialize_pizza(self, unique_ingredients, ingredients_map):
        # ingredients
        self.pizza = np.full((self.r,self.c), ' ')
        for ri in range(self.r):
            for ci in range(self.c):
                if (ri%self.r_scale==2 and \
                    ci%self.c_scale==4):

                    self.pizza[ri][ci] = unique_ingredients[ingredients_map
                        [(ri-2)//self.r_scale]
                        [(ci-4)//self.c_scale]]

        # outline pizza
        self.pizza[0:self.r:self.r-1, 1:self.c-1] = '-'
        self.pizza[1:self.r-1,        0:self.c:self.c-1] = '|'
        self.pizza[0:self.r:self.r-1, 0:self.c:self.c-1] = '+'

    def find_slices(self, slices_map):
        slices_dict = {}
        for ri in range(len(slices_map)):
            for ci in range(len(slices_map[0])):
                slice_id = slices_map[ri][ci]

                if slice_id in slices_dict:
                    slices_dict[slice_id] = (*slices_dict[slice_id][:2],ri,ci)
                elif slice_id != -1:
                    slices_dict[slice_id] = (ri,ci,ri,ci)

        return slices_dict.values()

    def cut(self, slices):
        for slice in slices:
            r0,c0,r1,c1 = slice
            self.pizza[
                self.r_scale*r0+1: self.r_scale*(r1+1)+1: self.r_scale*(r1-r0+1)-1, # for top, bottom cuts
                self.c_scale*c0+3: self.c_scale*(c1+1), # for every column int the slice
                ] = '-'
            self.pizza[
                self.r_scale*r0+2: self.r_scale*(r1+1), # for every row in the slice
                self.c_scale*c0+2: self.c_scale*(c1+1)+1: self.c_scale*(c1-c0+1)-2, # for left, right cuts
                ] = '|'
            for ri in range(self.r_scale*r0+2, self.r_scale*(r1+1)):
                for ci in range(self.c_scale*c0+4, self.c_scale*(c1+1), 3):
                    if self.pizza[ri,ci] == ' ':
                        self.pizza[ri,ci] = '`'

        for slice in slices:
            r0,c0,r1,c1 = slice
            self.pizza[
                self.r_scale*r0+1: self.r_scale*(r1+1)+1: self.r_scale*(r1-r0+1)-1, # top, bottom rows
                self.c_scale*c0+2: self.c_scale*(c1+1)+1: self.c_scale*(c1-c0+1)-2, # left, right columns
                ] = '+'


    def put_cursor_at(self, position):
        r,c = position
        self.pizza[self.r_scale*r+2,self.c_scale*c+3] = '['
        self.pizza[self.r_scale*r+2,self.c_scale*c+5] = ']'

    def get_from(self, state):
        unique_ingredients = state['unique_ingredients']
        ingredients_map = state['ingredients_map']
        slices_map = state['slices_map']

        r,c = len(ingredients_map),len(ingredients_map[0])
        self.r, self.c = self.r_scale*r+2,self.c_scale*c+3

        self.initialize_pizza(unique_ingredients, ingredients_map)

        # cut slices
        slices = self.find_slices(slices_map)
        self.cut(slices)

        # put cursor
        self.put_cursor_at(state['cursor_position'])

        for line in self.pizza:
            print('    {}'.format(''.join(line)))


class Stream:

    legend = '\n' + \
        '                                           +---------+\n' + \
        '  Legend: T M - ingredients  [ ] - cursor  | T  `  M | - slice boundaries\n' + \
        '                                           +---------+'

    hello = '\n' + \
        '        _)                                    |    |   _)                               \n' + \
        '  __ \   | _  / _  /   _` |       __|  |   |  __|  __|  |  __ \    _` |                 \n' + \
        '  |   |  |   /    /   (   |      (     |   |  |    |    |  |   |  (   |                 \n' + \
        '  .__/  _| ___| ___| \__,_|     \___| \__,_| \__| \__| _| _|  _| \__, |                 \n' + \
        ' _|                                                              |___/                  \n' + \
        '          | _)                         |                                _)               \n' + \
        '          |  | \ \   /  _ \       __|  __|   __|  _ \   _` |  __ `__ \   |  __ \    _` | \n' + \
        '          |  |  \ \ /   __/     \__ \  |    |     __/  (   |  |   |   |  |  |   |  (   | \n' + \
        '         _| _|   \_/  \___|     ____/ \__| _|   \___| \__,_| _|  _|  _| _| _|  _| \__, | \n' + \
        '                                                                                  |___/  \n' + \
        '\n' + \
        '\n' + \
        '       Welcome to my stream where I cut a pizza LIVE for my friends!\n' + \
        '\n' + \
        '                   76 69 76 65  6C 61  70 69 7A 7A 61 \n' + \
        '\n' + \
        '\n'


    goodbye = '\nBon appetit !'


    def __init__(self, args):
        self.name = args.get('name')
        if not os.path.exists(self.name):
            raise IOError('Directory not found: {}'.format(self.name))

        self.padding = args.get('padding')
        self.refresh_delay = args.get('refresh_delay')


        self.step = -1
        self.last_state_path = os.path.join(self.name, 'ready_pizza_state.json')
        self.score = 0

        self.display_legend = not args.get('disable_legend')

    def next_state(self):
        step = self.step+1
        state_path = os.path.join(self.name, '{}_state.json'.format(step))

        while not os.path.exists(state_path) and not os.path.exists(self.last_state_path):
            if self.refresh_delay > 0:
                time.sleep(self.refresh_delay)

        if os.path.exists(state_path):
            while True:
                with open(state_path) as f:
                    if len(f.readlines()) != 0:
                        f.seek(0)
                        state = json.load(f)
                        break
            self.step = step
            return state

        return None

    def display_state_variables(self, state):
        print('\n'*self.padding)
        print(stream.hello)
        print('  Rows:                             {}'.format(len(state['ingredients_map'])))
        print('  Columns:                          {}'.format(len(state['ingredients_map'][0])))
        print('  Min each ingredient per slice:    {}'.format(state['min_each_ingredient_per_slice']))
        print('  Max ingredients per slice:        {}'.format(state['max_ingredients_per_slice']))
        print('')
        print('  Last action:                      {}'.format(state['action']))
        print('  Last reward:                      {}'.format(state['reward']))
        print('')
        print('  Cursor position:                  ({},{})'.format(*state['cursor_position']))
        print('  Slice mode:                       {}'.format('on' if state['slice_mode'] else 'off'))
        print('')
        print('  Step:                             {}'.format(self.step))
        print('  Score:                            {}'.format(self.score))
        print('')
        print('')


    def run(self):
        serve_pizza = ServePizza()
        while True:
            state = self.next_state()
            if state is None: break

            self.score += state['reward']

            self.display_state_variables(state)
            serve_pizza.get_from(state)
            if self.display_legend: print(self.legend)



if __name__ == '__main__':

    ### PARSER
    import argparse
    parser = argparse.ArgumentParser(description='Streaming of how I cut the pizza !',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog= '\n' + \
        ' This program will not run the game. It just reads states from the folder and \n' + \
        ' displays them.\n')

    parser.add_argument('--name', required=True, help='folder where to find the states from the game')
    parser.add_argument('--padding', type=int, default=0, help='empty lines between displaying the game ' + \
        'for better gaming experience')
    parser.add_argument('--refresh_delay', type=float, default=0., help='refresh delay to check for new states')
    parser.add_argument('--disable_legend', action='store_true', help='disable display of the legend')

    args = parser.parse_args()
    stream = Stream(args.__dict__)

    try:
        stream.run()
    except KeyboardInterrupt:
        pass
    finally:
        print(stream.goodbye)
