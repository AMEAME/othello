from othello import Othello, game_won
from config import *
import numpy as np
from functools import reduce


def enocode_serial(move):
  row = int(move[0]) - 1
  col = int(move[1]) - 1
  arr = [0] * 64
  arr[col * 8 + row] = 1
  return arr

def get_data():
  records = [l.rstrip().split() for l in open('data.txt')]
  x_data = []
  y_data = []
  for i, r in enumerate(records):
    print(i)
    winner = game_won(r)
    if winner == None: continue
    if winner == WHITE: winner = 0
    o = Othello()
    for i, move in enumerate(r):
      if move == '0': break
      if i % 2 != winner:
        x_data.append(np.array(reduce(lambda a, e: a + e, o.board)))
        y_data.append(np.array(enocode_serial(move)))
      o.make_move([int(move[0]), int(move[1])])
  return { 'data': np.array(x_data), 'target': np.array(y_data) }


if __name__ == '__main__':
  from time import time
  s = time()
  get_data()
  print('time: {}'.format(time() - s))
