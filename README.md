## Pizza Cutting Turbo Simulator
[![Generic badge](https://img.shields.io/badge/Python-3.6.3-green.svg)](https://shields.io/)

**_EXPLORE_** different configurations and shapes of pizza

**_IMMERSE_** yourself in the world of a Google engineer trying to cut a pizza for some friends

**_ENGAGE_** with slices, increase them to form bigger ones and earn points

This is a simulator made for a practice problem of Google Hash Code competition in 2019.
They expected me to solve it with algorithms, but I have built a game ! For more
information about the problem, check [google_hash_code_pizza_problem.pdf](./google_hash_code_pizza_problem.pdf).

This simulator was built to train a neural network to complete the competition problem.
Deep Reinforcement Learning, here we go !

#### `TRY IT NOW !`

Go to the terminal:

```
git clone https://github.com/thatsmesasha/pizza_cutting_turbo_simulator.git
cd pizza_cutting_turbo_simulator
pip3 install -r requirements.txt
```

`game.py` is the main game file that reads lines from standard input or keypresses,
renders the game and saves states to the files if specified.

#### Help

More description on the game rules and parameters:

```
python3 -m src.game --help
```

#### Example

To play a game with a keyboard, run in a terminal:

```
python3 -m src.game --wasd --render
```

Sample output of the stream:

```
             _)                                    |    |   _)
       __ \   | _  / _  /   _` |       __|  |   |  __|  __|  |  __ \    _` |
       |   |  |   /    /   (   |      (     |   |  |    |    |  |   |  (   |
       .__/  _| ___| ___| \__,_|     \___| \__,_| \__| \__| _| _|  _| \__, |
       _|                                                              |___/

  |                 |                      _)                    |         |
   __|  |   |   __|  __ \    _ \        __|  |  __ `__ \   |   |  |   _` |  __|   _ \    __|
   |    |   |  |     |   |  (   |     \__ \  |  |   |   |  |   |  |  (   |  |    (   |  |
  \__| \__,_| _|    _.__/  \___/      ____/ _| _|  _|  _| \__,_| _| \__,_| \__| \___/  _|


Welcome to my gameplay where I cut a pizza LIVE for my friends!

      76 69 76 65  6C 61  70 69 7A 7A 61



Rows:                             3
Columns:                          5
Min each ingredient per slice:    1
Max ingredients per slice:        6

Last action:                      down
Last reward:                      2

Cursor position:                  (0,2)
Slice mode:                       on

Step:                             9
Score:                            8


+-------------------------------+
| +---------+ +---+             |
| | T  `  T | |[T]|   T     T   |
| | `  `  ` | | ` |             |
| | `  `  ` | | ` |             |
| | T  `  M | | M |   M     T   |
| | `  `  ` | +---+             |
| | `  `  ` |                   |
| | T  `  T |   T     T     T   |
| +---------+                   |
+-------------------------------+

                                         +---------+
Legend: T M - ingredients  [ ] - cursor  | T  `  M | - slice boundaries
                                         +---------+
Bon appetit !
```
