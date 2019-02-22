from src.google_engineer import GoogleEngineer
from src.pizza import Pizza

import numpy as np
import json
import os

class StandardInput:
    def next(self):
        return input('')

class KeyInput:
    key_to_action = {
        'w': 'up',
        'a': 'left',
        's': 'down',
        'd': 'right',
        ' ': 'toggle',
    }

    def __init__(self):
        try:
            import tty, sys
            self.next_char = self.unix_next_char
        except ImportError:
            import msvcrt
            self.next_char = self.windows_next_char

    def unix_next_char(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def windows_next_char(self):
        import msvcrt
        return msvcrt.getch()

    def next(self):
        while True:
            next_char = self.next_char().lower()
            if next_char in 'wasd ':
                return self.key_to_action[next_char]
            elif next_char == 'q' or next_char == '\x03':
                raise EOFError('End of input.')

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

    def put_cursor_at(self, position, slice_mode):
        r,c = position
        self.pizza[self.r_scale*r+2,self.c_scale*c+3] = '<' if slice_mode else '['
        self.pizza[self.r_scale*r+2,self.c_scale*c+5] = '>' if slice_mode else ']'

    def print_from(self, env):
        unique_ingredients = env['information']['unique_ingredients']
        ingredients_map = env['state']['ingredients_map']
        slices_map = env['state']['slices_map']

        r,c = len(ingredients_map),len(ingredients_map[0])
        self.r, self.c = self.r_scale*r+2,self.c_scale*c+3

        self.initialize_pizza(unique_ingredients, ingredients_map)

        # cut slices
        slices = self.find_slices(slices_map)
        self.cut(slices)

        # put cursor
        self.put_cursor_at(env['state']['cursor_position'], env['state']['slice_mode'])

        for line in self.pizza:
            print('    {}'.format(''.join(line)))


class Game:

    legend = '\n' + \
        '                                           +---------+\n' + \
        '  Legend: T M - ingredients  [ ] - cursor  | T  `  M | - slice boundaries\n' + \
        '                                           +---------+'

    hello = '\n' + \
        '             _)                                    |    |   _)               \n' + \
        '       __ \   | _  / _  /   _` |       __|  |   |  __|  __|  |  __ \    _` | \n' + \
        '       |   |  |   /    /   (   |      (     |   |  |    |    |  |   |  (   | \n' + \
        '       .__/  _| ___| ___| \__,_|     \___| \__,_| \__| \__| _| _|  _| \__, | \n' + \
        '      _|                                                              |___/  \n' + \
        '\n' + \
        '  |                 |                      _)                    |         |                \n' + \
        '  __|  |   |   __|  __ \    _ \        __|  |  __ `__ \   |   |  |   _` |  __|   _ \    __| \n' + \
        '  |    |   |  |     |   |  (   |     \__ \  |  |   |   |  |   |  |  (   |  |    (   |  |    \n' + \
        ' \__| \__,_| _|    _.__/  \___/      ____/ _| _|  _|  _| \__,_| _| \__,_| \__| \___/  _|    \n' + \
        '\n' + \
        '\n' + \
        '       Welcome to my gameplay where I cut a pizza LIVE for my friends!\n' + \
        '\n' + \
        '                   76 69 76 65  6C 61  70 69 7A 7A 61 \n' + \
        '\n' + \
        '\n'

    goodbye = '\nBon appetit !'

    def __init__(self, args):
        self.max_steps = args.get('max_steps', float('inf'))
        self.env = None
        self.serve_pizza = ServePizza()

    def init(self, pizza_config):
        self.google_engineer = GoogleEngineer(pizza_config)
        self.unique_ingredients = self.google_engineer.pizza.ingredients._unique.tolist()

        self.step_index = 0

        self.env = {
            'state': self.google_engineer.state(),
            'reward': 0,
            'done': False,
            'information': {
                'step': self.step_index,
                'action': 'none',
                'unique_ingredients': self.unique_ingredients,
                'score': 0,
                'slices': []}}
        return self.env['state'], self.env['reward'], self.env['done'], self.env['information']


    def step(self, action):
        self.step_index += 1
        reward = self.google_engineer.do(action)
        done = not self.google_engineer.pizza.can_increase_more() or self.step_index >= self.max_steps
        slices = sorted(self.google_engineer.valid_slices, key=lambda s: s.as_tuple)

        self.env = {
            'state': self.google_engineer.state(),
            'reward': reward,
            'done': done,
            'information': {
                'step': self.step_index,
                'action': action,
                'unique_ingredients': self.unique_ingredients,
                'score': self.google_engineer.score,
                'slices': [slice.as_tuple for slice in slices]}}
        return self.env['state'], self.env['reward'], self.env['done'], self.env['information']

    def render_information(self):
        print('  Rows:                             {}'.format(len(self.env['state']['ingredients_map'])))
        print('  Columns:                          {}'.format(len(self.env['state']['ingredients_map'][0])))
        print('  Min each ingredient per slice:    {}'.format(self.env['state']['min_each_ingredient_per_slice']))
        print('  Max ingredients per slice:        {}'.format(self.env['state']['max_ingredients_per_slice']))
        print('')
        print('  Last action:                      {}'.format(self.env['information']['action']))
        print('  Last reward:                      {}'.format(self.env['reward']))
        print('')
        print('  Cursor position:                  ({},{})'.format(*self.env['state']['cursor_position']))
        print('  Slice mode:                       {}'.format('on' if self.env['state']['slice_mode'] else 'off'))
        print('')
        print('  Step:                             {}'.format(self.env['information']['step']))
        print('  Score:                            {}'.format(self.env['information']['score']))
        print('')
        print('')


    def render(self):
        print(self.hello)
        self.render_information()
        self.serve_pizza.print_from(self.env)
        print(self.legend)



if __name__ == '__main__':
    pizza_config_line_description = \
        '1 line containing the following natural numbers separated by single spaces:\n' + \
        '   - R (1 <= R <= 1000) is the number of rows,\n' + \
        '   - C (1 <= C <= 1000) is the number of columns,\n' + \
        '   - L (1 <= L <= 1000) is the minimum number of each ingredient cells in a slice,\n' + \
        '   - H (1 <= H <= 1000) is the maximum total number of cells of a slice\n'

    pizza_lines_description = \
        'R lines describing the rows of the pizza (one row after another). Each of\n' + \
        '   these lines contains C characters describing the ingredients in the cells\n' + \
        '   of the row (one cell after another). Each character is either "M" (for mushroom)\n' + \
        '   or "T" (for tomato).\n'

    game_rules = \
        '   You can move around the pizza map and increase slices (input structure is below).\n' + \
        '   The goal is to have maximum score obtaining the maximum amount of ingredients\n' + \
        '   inside valid slices. A valid slice is a slice which satisfies provided slice constraints\n' + \
        '   of having at least the specified minimum of each ingredient per slice and having not more\n' + \
        '   than the maximum of all ingredients per slice.\n' + \
        '   To increase slice, you need to toggle slice mode from OFF to ON. Then any direction that\n' + \
        '   you will pass, will be applied to increase the slice at the cursor position.\n' + \
        '   To disable slice mode, you need to toggle it one more time.\n' + \
        '   Some actions will not change anything and you will not receive any reward for it.\n'


    import argparse
    parser = argparse.ArgumentParser(description='Cutting pizza for my friends',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog= '\n' + \
        ' Game rules:\n' + \
        game_rules + \
        ' Expects input as follows:' + \
        ' - ' + pizza_config_line_description + \
        '\n' + \
        ' - ' + pizza_lines_description + \
        '\n' + \
        ' For input type one of "right", "down", "left", "up" to move/increase in specific direction \n' + \
        ' and "toggle" for toggling slice mode. Input will be read line by line.\n' + \
        ' You can overwrite how you pass the input with parameter --wasd (check its help).\n' + \
        ' When the slice mode is on, passing directions actions will increase the slice\n' + \
        ' at the position of the cursor. Otherwise, the cursor will move in the specified\n' + \
        ' direction.\n' + \
        '\n' + \
        ' Before each action there will be a file "<name>/<step_index>_env.json"\n' + \
        ' containing state, reward, game over and other information. If <name> parameter\n' + \
        ' was not provided, states will not be saved into files. Initial state\n' + \
        ' will be inside the file "<name>/ready_pizza_env.json".\n' + \
        '\n' + \
        ' The game ends when slices cannot be increased anymore or the game reached\n' + \
        ' maximum actions.\n' + \
        '\n' + \
        ' At the end, there will be a file "<name>/ready_pizza_state.json"\n' + \
        ' containing the last state in the game with total reward.\n' + \
        '\n' + \
        ' File "<name>/ready_pizza_env.json" is the same as the last \n' + \
        ' "<name>/<step_index>_env.json". It is provided for convinience and to \n' + \
        ' indicate the end of the game.\n' + \
        ' Note that the files will be overwritten if exist.\n' + \
        '\n' + \
        ' If --output parameter is provided, there will be a file that consists of:\n' + \
        '   - 1 line containing a single natural number S (0 <= S <= R * C),\n' + \
        '     representing the total number of slices to be cut.\n' + \
        '   - S lines describing the slices. Each of these lines contain\n' + \
        '     the following natural numbers separated by single spaces:\n' + \
        '     - r1, c1, r2, c2 (0 <= r1,r2 < R,0 <= c1,c2 < C) describe\n' + \
        '       a slice of pizza delimited by the rows r1 and r2 and\n' + \
        '       the columns c1 and c2, including the cells of the delimiting\n' + \
        '       rows and columns.\n')
        # TODO: info what in the states file


    parser.add_argument('--name', default=None, help='folder where the states will be saved')
    parser.add_argument('--output', default=None, help='a path where to store final slices')
    parser.add_argument('--max_steps', type=int, default=100, help='maximum steps to do before quiting')
    parser.add_argument('--quiet', action='store_true', help='disable output')
    parser.add_argument('--render', action='store_true', help='render the pizza during playing')
    parser.add_argument('--wasd', action='store_true', help='instead of passing "right", "down", "left", ' + \
        '"up", "toggle" you can use wasd keys and spacebar for toggle; this will also print help messages')
    args = parser.parse_args()

    args_dict = args.__dict__
    output = args_dict.get('output')
    wasd = args_dict.get('wasd')
    quiet = args_dict.get('quiet')
    render = args_dict.get('render')
    name = args_dict.get('name')
    max_steps = args_dict.get('max_steps')

    game_args = { 'max_steps': max_steps }
    game = Game(game_args)

    if not quiet:
        print(game.hello)
        print('\n Game rules:\n')
        print(game_rules)
        print()

    try:
        # create folder for states
        if name is not None and not os.path.exists(name):
            os.makedirs(name)

        # get pizza config
        if not quiet:
            print('Input {}'.format(pizza_config_line_description))
            print('For example: 3 5 1 6')
            print()
            print('Your input:')

        config_line = input('')
        print()
        r, c, l, h = [int(n) for n in config_line.split(' ')]

        pizza_lines = []
        if not quiet:
            print()
            print('Input:')
            print(pizza_lines_description)
            print('For example:')
            print()
            print('TTTTT')
            print('TMMMT')
            print('TTTTT')
            print()
            print('Your input:')

        for i in range(r):
            pizza_lines.append(input(''))

        print()
        pizza_config = { 'pizza_lines': pizza_lines, 'r': r, 'c': c, 'l': l, 'h': h }

        # init game
        game.init(pizza_config)
        if render: game.render()
        if name is not None:
            env_filename = os.path.join(name, '{}_env.json'.format(game.env['information']['step']))
            with open(env_filename, 'w') as f:
                json.dump(game.env, f, separators=(',',':'))

        if not quiet:
            print('Now you can use WASD keys to move/increase and space bar for toggling slice mode. Press CTRL-C or q to exit.')
            print()

        # run game
        action_input = KeyInput() if wasd else StandardInput()
        while not game.env['done']:
            # get action
            action = action_input.next()
            game.step(action)
            if render: game.render()
            if name is not None:
                env_filename = os.path.join(name, '{}_env.json'.format(game.env['information']['step']))
                with open(env_filename, 'w') as f:
                    json.dump(game.env, f, separators=(',',':'))



    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        if game.env is not None:
            # save last environment
            if name is not None:
                env_filename = os.path.join(name, 'ready_pizza_env.json')
                with open(env_filename, 'w') as f:
                    json.dump(game.env, f, separators=(',',':'))

            # save slices
            if output:
                with open(output, 'w') as f:
                    slices = game.env['information']['slices']
                    f.write('{}\n'.format(len(slices)))
                    for slice in slices:
                        f.write('{} {} {} {}\n'.format(*slice))

        if not quiet: print(game.goodbye)
