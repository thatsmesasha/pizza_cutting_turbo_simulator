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
    config_line_description = '\n' + \
        ' - 1 line containing the following natural numbers separated by single spaces:\n' + \
        '   - R (1 <= R <= 1000) is the number of rows,\n' + \
        '   - C (1 <= C <= 1000) is the number of columns,\n' + \
        '   - L (1 <= L <= 1000) is the minimum number of each ingredient cells in a slice,\n' + \
        '   - H (1 <= H <= 1000) is the maximum total number of cells of a slice\n'

    pizza_lines_description = '\n' + \
        ' - R lines describing the rows of the pizza (one row after another). Each of\n' + \
        '   these lines contains C characters describing the ingredients in the cells\n' + \
        '   of the row (one cell after another). Each character is either "M" (for mushroom)\n' + \
        '   or "T" (for tomato).\n'

    input_actions_description = '\n' + \
        ' For input type one of "right", "down", "left", "up" to move/increase in specific direction \n' + \
        ' and "toggle" for toggling slice mode. Input will be read line by line.\n' + \
        ' You can overwrite how you pass the input with parameter --wasd (check its help).\n' + \
        ' When the slice mode is on, passing directions actions will increase the slice\n' + \
        ' at the position of the cursor. Otherwise, the cursor will move in the specified\n' + \
        ' direction. Some moves will not do anything and you will receive the reward equal 0.\n'

    input_files_description = '\n' + \
        ' Before each action there will be a file "<name>/<step_index>_state.json"\n' + \
        ' containing state and reward information. If <name> parameter\n' + \
        ' was not provided, states will not be saved into files. Initial state\n' + \
        ' will be inside the file "<name>/0_state.json".\n' + \
        '\n' + \
        ' After each step there will be a file "slices.txt" in the current directory\n' + \
        ' that consists of:\n' + \
        '   - 1 line containing a single natural number S (0 <= S <= R * C),\n' + \
        '     representing the total number of slices to be cut.\n' + \
        '   - S lines describing the slices. Each of these lines contain\n' + \
        '     the following natural numbers separated by single spaces:\n' + \
        '     - r1, c1, r2, c2 (0 <= r1,r2 < R,0 <= c1,c2 < C) describe\n' + \
        '       a slice of pizza delimited by the rows r1 and r2 and\n' + \
        '       the columns c1 and c2, including the cells of the delimiting\n' + \
        '       rows and columns.\n' + \
        '\n' + \
        ' The game ends when slices cannot be increased anymore or the game reached\n' + \
        ' maximum actions.\n' + \
        '\n' + \
        ' At the end, there will be a file "<name>/ready_pizza_state.json"\n' + \
        ' containing the last state in the game with total reward.\n' + \
        '\n' + \
        ' File "<name>/ready_pizza_state.json" is the same as the last \n' + \
        ' "<name>/<step_index>_state.json". It is provided for convinience and to \n' + \
        ' indicate the end of the game.\n' + \
        ' Note that both files will override existing files.\n'


    def __init__(self, args):
        self.name = args.get('name', None)
        if self.name and not os.path.exists(self.name):
            os.makedirs(self.name)

        self.max_steps = args.get('max_steps')
        self.wasd = args.get('wasd')

    def save_state(self, name, state):
        filename = os.path.join(self.name, '{}_state.json'.format(name))
        with open(filename, 'w') as f:
            json.dump(state, f, separators=(',',':'))

    def save_last_state_with_total_reward(self):
        self.save_state('ready_pizza', { **self.state, 'reward': self.score })

    def save_slices(self):
        with open('slices.txt', 'w') as f:
            f.write(str(len(self.slices))+ '\n')
            for slice in self.slices:
                f.write(str(slice) + '\n')

    def input_pizza_config(self):
        config_line = input('')
        r, c, l, h = [int(n) for n in config_line.split(' ')]

        pizza_lines = []
        for ri in range(r):
            line = input('')
            pizza_lines.append(line)
        return { 'pizza_lines': pizza_lines, 'r': r, 'c': c, 'l': l, 'h': h }

    def end(self):
        if self.name: self.save_state('ready_pizza', { **self.state, 'reward': self.score })

    def run(self):
        action_input = KeyInput() if self.wasd else StandardInput()

        pizza_config = self.input_pizza_config()
        google_engineer = GoogleEngineer(pizza_config)
        unique_ingredients = google_engineer.pizza.ingredients._unique.tolist()

        self.state = {
            **google_engineer.state(),
            'reward': 0,
            'action': 'none',
            'unique_ingredients': unique_ingredients}
        self.score = 0

        if self.name: self.save_state(0, self.state)

        for i in range(1, self.max_steps + 1):
            if not google_engineer.pizza.can_increase_more(): break

            try:
                action = action_input.next()
            except EOFError:
                break
            reward = google_engineer.do(action)
            self.score = google_engineer.score
            self.state = {
                **google_engineer.state(),
                'reward': reward,
                'action': action,
                'unique_ingredients': unique_ingredients}
            if self.name: self.save_state(i, self.state)
            self.slices = sorted(google_engineer.valid_slices, key=lambda s: s.as_tuple)
            self.save_slices()
        self.end()




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Cutting pizza for my friends',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog= '\n' + \
        ' Expects input as follows:' + \
        Game.config_line_description + \
        Game.pizza_lines_description + \
        Game.input_actions_description + \
        Game.input_files_description)

        # TODO: info what in the states file


    parser.add_argument('--name', required=True, help='folder where the states will be saved')
    parser.add_argument('--max_steps', type=int, default=100, help='maximum steps to do before quiting')
    parser.add_argument('--wasd', action='store_true', help='instead of passing "right", "down", "left", ' + \
        '"up", "toggle" you can use wasd keys and spacebar for toggle; do not include newline')
    args = parser.parse_args()
    game = Game(args.__dict__)

    try:
        game.run()
    except KeyboardInterrupt:
        game.end()
