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

`game.py` is the main game file that reads lines from standard input or keypresses
and saves states to the files if specified.

`stream.py` is the rendering part of the game, it takes states from the files and
renders them on the screen.

More description on the game rules and parameters:

```
python3 game.py --help
python3 stream.py --help
```

**`Example`**

To play a game with a keyboard and a display:

1) In the first terminal, run and input pizza configuration (check help for
description), and then use wasd and spacebar keys:

```
python3 game.py --wasd --name=test01
```

2) In the second terminal, run:

```
python3 stream.py --refresh_delay=0.5 --name=test01
```

#### Leaked Pictures

```
      _)                                    |    |   _)
__ \   | _  / _  /   _` |       __|  |   |  __|  __|  |  __ \    _` |
|   |  |   /    /   (   |      (     |   |  |    |    |  |   |  (   |
.__/  _| ___| ___| \__,_|     \___| \__,_| \__| \__| _| _|  _| \__, |
_|                                                              |___/
        | _)                         |                                _)
        |  | \ \   /  _ \       __|  __|   __|  _ \   _` |  __ `__ \   |  __ \    _` |
        |  |  \ \ /   __/     \__ \  |    |     __/  (   |  |   |   |  |  |   |  (   |
       _| _|   \_/  \___|     ____/ \__| _|   \___| \__,_| _|  _|  _| _| _|  _| \__, |
                                                                                 |___/


Welcome to my stream where I cut a pizza LIVE for my friends!

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
