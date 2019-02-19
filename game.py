from google_engineer import GoogleEngineer
from pizza import Pizza

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


class Game:

    def __init__(self, args):
        self.max_steps = args.get('max_steps')
        self.env = None

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
        return self.env


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
        return self.env

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


    import argparse
    parser = argparse.ArgumentParser(description='Cutting pizza for my friends',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog= '\n' + \
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
        ' direction. Some moves will not do anything and you will receive the reward equal 0.\n' + \
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
        ' If output parameter is provided, there will be a file that consists of:\n' + \
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
    parser.add_argument('--slices_path', default=None, help='store output slices to a file')
    parser.add_argument('--max_steps', type=int, default=100, help='maximum steps to do before quiting')
    parser.add_argument('--wasd', action='store_true', help='instead of passing "right", "down", "left", ' + \
        '"up", "toggle" you can use wasd keys and spacebar for toggle; this will also print help messages')
    args = parser.parse_args()

    args_dict = args.__dict__
    slices_path = args_dict.get('slices_path')
    wasd = args_dict.get('wasd')
    name = args_dict.get('name')
    max_steps = args_dict.get('max_steps')

    if wasd is not None and name is None:
        raise Exception('Parameter --name must be provided for WASD mode')

    game_args = { 'max_steps': max_steps }
    game = Game(game_args)

    try:
        # create folder for states
        if name is not None and not os.path.exists(name):
            os.makedirs(name)

        # get pizza config
        if wasd:
            print('Input {}'.format(pizza_config_line_description))
            print('For example: 3 5 1 6')
            print()
            print('Your input:')

        config_line = input('')
        print()
        r, c, l, h = [int(n) for n in config_line.split(' ')]

        pizza_lines = []
        if wasd:
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
        env = game.init(pizza_config)
        if name is not None:
            env_filename = os.path.join(name, '{}_env.json'.format(env['information']['step']))
            with open(env_filename, 'w') as f:
                json.dump(env, f, separators=(',',':'))

        if wasd:
            print('To get the display of the game, run in another terminal in the same directory:')
            print('  python3 stream.py --refresh_delay=0.5 --name={}'.format(name))
            print()
            print('Now you can use WASD keys to move/increase and space bar for toggling slice mode. Press CTRL-C or q to exit.')
            print()

        # run game
        action_input = KeyInput() if wasd else StandardInput()
        while not env['done']:
            # get action
            action = action_input.next()
            env = game.step(action)
            if name is not None:
                env_filename = os.path.join(name, '{}_env.json'.format(env['information']['step']))
                with open(env_filename, 'w') as f:
                    json.dump(env, f, separators=(',',':'))



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
            if slices_path:
                with open(slices_path, 'w') as f:
                    slices = game.env['information']['slices']
                    f.write('{}\n'.format(len(slices)))
                    for slice in slices:
                        f.write('{} {} {} {}\n'.format(*slice))
