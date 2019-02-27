import numpy as np

def init(input_data):
  lines = input_data.splitlines()
  R,C,L,H = list(map(int, lines[0].split()))

  possible_shapes = [
    (r,c)
    for r in range(R)
    for c in range(C)
    if r*c <= H and r*c >= 2*L]

  pizza = np.array(list(map(list, lines[1:])))
  ingredients_map = np.array(pizza == 'T', dtype=np.float16)
  ingredients_map[ingredients_map == 0] = -1

  slices_map = np.zeros((R,C))

  position_map = np.zeros((R,C))
  position = (0,0)
  position_map[position] = 1.

  return R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes

def move_next(state):
  R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes = state

  ri,ci = (position[0]+1,0) if position[1]==C-1 else (position[0],position[1]+1)
  position_map[ri,ci] = 1.

  print(slices_map[ri,ci])
  while slices_map[ri,ci] != 0:
    if (ri,ci)>=(R-1,C-1):
      position = (R-1,C-1)
      print('Reached the end of the pizza')
      new_state = (R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes)
      return new_state, True

    ri,ci = (ri+1,0) if ci==C-1 else (ri,ci+1)
    position_map[ri,ci] = 1.

  position = (ri,ci)
  new_state = (R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes)
  return new_state, False

def step(state, action):
  R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes = state

  r,c = possible_shapes[action]
  r_position,c_position = position

  if r_position+r >= R or c_position+c >= C:
    print('Slice is outside the pizza')
    new_state = (R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes)
    return state, -1


  padded_slice = np.zeros((R,C))
  padded_slice[r_position:r_position+r,c_position:c_position+c] = np.ones((r,c))

  if np.abs(np.sum(padded_slice*ingredients_map)) > H-2*L:
    print('Not enough ingredients')
    return state, -1

  if np.max(padded_slice*slices_map) > 0:
    print('Overlapping other shape')
    return state, -1

  reward = r*c
  slices_map += padded_slice

  new_state = (R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes)
  return new_state, reward

def display(state, reward=None):
  R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes = state

  display_format = \
    'State:\n' + \
    '- ingredients_map:\n' + \
    '{}\n' + \
    '\n' + \
    '- slices_map:\n' + \
    '{}\n' + \
    '\n' + \
    '- position_map:\n' + \
    '{}\n'

  print(display_format.format(ingredients_map,slices_map,position_map))
  if reward: print('Reward: {}'.format(reward))

  print('-----------------------')

if __file__ == '__main__':
    # input data
    input_data = \
    '''3 5 1 6
    TMTTM
    MMTTT
    TTTMT
    '''

    # start game
    state = init(input_data)
    R,C,L,H,ingredients_map,slices_map,position_map,position,possible_shapes = state
    display(state)


    # take actions
    action = np.random.randint(0,len(possible_shapes))
    print('Putting shape {}'.format(possible_shapes[action]))
    state, reward = step(state, action)
    display(state,reward)

    # go to the next position
    state, done = move_next(state)
    display(state)
