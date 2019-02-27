import numpy as np

def init(RCLH, pizza_map):
    '''Initialize state, which consists of 3 arrays of shape R,C:
    - state[0,ri,ci] is 1 if the pizza has a tomato at (ri,ci), else -1
    - state[1,ri,ci] is 1 if the ingredient at (ri,ci) belongs to a slice, else 0
    - state[2,ri,ci] is 1 if the current position is bigger or equal (ri,ci), else 0
    Returns a state and current position.
    '''

    state = np.zeros((3,RCLH[0],RCLH[1]))

    # map ingredients to 1 and -1
    state[0][pizza_map == 'T'] = 1.
    state[0][pizza_map == 'M'] = -1.

    # current position starts from top left
    state[2,0,0] = 1.

    return state, (0,0)

def move_next(state, position):
    '''Move position to next available ingredient, going row by row.
    Returns new state, new position, done - true if reached the end of the pizza.'''
    ri,ci = position
    _,R,C = state.shape

    while True:
        ri,ci = (ri+1,0) if ci>=C-1 else (ri,ci+1)
        if (ri,ci)>=(R-1,C-1):
            return state, (R-1,C-1), True

        state[2,ri,ci] = 1.
        if state[1,ri,ci] == 0.:
            break

    return state, (ri,ci), False

def step(RCLH, state, position, shape):
    '''Cut slice from the pizza. Returns new state, reward,
    debug message if cannot cut a slice this shape at this position.'''
    r,c = shape
    r0,c0 = position
    R,C,L,H = RCLH

    if r0+r >= R or c0+c >= C:
        return state, -1, 'Outside the pizza'

    padded_slice = np.zeros((R,C))
    padded_slice[r0:r0+r,c0:c0+c] = np.ones((r,c))

    if np.abs(np.sum(padded_slice*state[0])) > H-2*L:
        return state, -1, 'Not enough ingredients'

    if np.max(padded_slice*state[1]) > 0:
        return state, -1, 'Overlapping other slice'

    reward = r*c
    state[1] += padded_slice

    return state, reward, None

def render(state, position=None, reward=None):
    render_format = \
        'State:\n' + \
        '- ingredients_map:\n' + \
        '{}\n' + \
        '\n' + \
        '- slices_map:\n' + \
        '{}\n' + \
        '\n' + \
        '- position_map:\n' + \
        '{}\n'

    print(render_format.format(*state))
    if position: print('Position: {}'.format(position))
    if reward: print('Reward: {}'.format(reward))

    print('-----------------------')

def make_possible_shapes(R,C,L,H):
    '''Make all possible shapes sizes for given pizza config.'''
    return [
        (ri,ci)
        for ri in range(R)
        for ci in range(C)
        if ri*ci <= H and ri*ci >= 2*L]


if __name__ == '__main__':
        # input data
        input_data = \
        '3 5 1 6\n' + \
        'TMTTM\n' + \
        'MMTTT\n' + \
        'TTTMT\n'

        # preprocess input
        input_lines = input_data.splitlines()
        RCLH = tuple(map(int, input_lines[0].split()))
        pizza_map = np.array([list(l) for l in input_lines[1:]])
        possible_shapes = make_possible_shapes(*RCLH)

        # start game
        state, position = init(RCLH, pizza_map)
        render(state, position=position)

        # decide on slice shape
        shape_id = np.random.randint(0,len(possible_shapes))

        # cut slice
        shape = possible_shapes[shape_id]
        print('Cutting slice with shape {}'.format(shape))
        state, reward, debug_message = step(RCLH, state, position, shape)
        if debug_message: print('Couldn\'t cut slice: {}'.format(debug_message))
        render(state,position=position,reward=reward)

        # go to the next position
        state, position, done = move_next(state, position)
        render(state, position=position)
