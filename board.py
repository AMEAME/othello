from __future__ import print_function
from functools import reduce
from copy import deepcopy
import glob
import numpy as np

EMPTY    = 0
PLAYER   = 1
OPPONENT = 2
VALID    = 3

class Board():
  def __init__(self, cells=None):
    if cells is None:
      self.cells = np.zeros(64).reshape([8, 8])
      self[4, 5] = PLAYER
      self[5, 4] = PLAYER
      self[4, 4] = OPPONENT
      self[5, 5] = OPPONENT
    else:
      self.cells = cells

  def clone(self):
    return Board(deepcopy(self.cells))

  def switch_turn(self):
    for row in range(1, 9):
      for col in range(1, 9):
        if self[row, col] == EMPTY: continue
        self[row, col] = OPPONENT if self[row, col] == PLAYER else PLAYER

  def __getitem__(self, disc_pos):
    if (1 <= disc_pos[0] <= 8) and (1 <= disc_pos[1] <= 8):
      return self.cells[disc_pos[1] - 1][disc_pos[0] - 1]
    return EMPTY

  def __setitem__(self, disc_pos, value):
    self.cells[disc_pos[1] - 1][disc_pos[0] - 1] = value
    return self.cells

  def __str__(self):
    rangement = [str(i + 1) + ' ' for i in range(8)]
    string = '  {}\n'.format(reduce(lambda a, e: a + e, rangement, ''))
    for i, row in enumerate(self.cells):
      string += '{} {}\n'.format(i + 1,
                  reduce(lambda a, e: a + DISC_MARK[e] + ' ', row, ''))
    return string
