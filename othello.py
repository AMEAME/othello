from __future__ import print_function
from functools import reduce
from copy import deepcopy
import glob

import numpy as np
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training, Variable, cuda
from chainer.training import extensions
from neural_net import MLP, Classifier


EMPTY = 0
PLAYER = 1
OPPONENT = 2
VALID = 3

DISC_MARK = {
  EMPTY: '-',
  PLAYER: 'o',
  OPPONENT: 'x',
  VALID: '.'
}

class Board():
  def __init__(self, board=None):
    if board is not None:
      self.cells = board.copy()
      return
    self.cells = [[EMPTY] * (8) for _ in range(8)]
    self[4, 5] = PLAYER
    self[5, 4] = PLAYER
    self[4, 4] = OPPONENT
    self[5, 5] = OPPONENT

  def copy(self):
    return deepcopy(self.cells)

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


class Othello():
  def __init__(self):
    self.board = Board()
    self.valid_moves = []
    self.update_valid_moves()

  def make_move(self, move):
    for m in self.valid_moves:
      self.board[m] = EMPTY
    self._flip_disks(self.board, move)
    self.switch_turn()
    self.update_valid_moves()
    if not self.valid_moves:
      self.switch_turn()

  def update_valid_moves(self):
    del self.valid_moves[:]
    for row in range(1, 9):
      for col in range(1, 9):
        if self.board[row, col] == EMPTY:
          board = Board(self.board)
          if self._flip_disks(board, (row, col)):
            self.valid_moves.append((row, col))
    self.valid_moves = self._uniq(self.valid_moves)
    for m in self.valid_moves:
      self.board[m] = VALID

  def switch_turn(self):
    for row in range(1, 9):
      for col in range(1, 9):
        if self.board[row, col] == EMPTY: continue
        self.board[row, col] = OPPONENT if self.board[row, col] == PLAYER else PLAYER

  def _flip_disks(self, board, move):
    board[move] = PLAYER
    directions = {
      'right' : (9 - move[0], ( 1,  0)),
      'bottom': (9 - move[1], ( 0,  1)),
      'left'  : (move[0],     (-1,  0)),
      'top'   : (move[1],     ( 0, -1)),
      'top_left'    : (min(move[1],     move[0]),     (-1, -1)),
      'bottom_right': (min(9 - move[1], 9 - move[0]), ( 1,  1)),
      'top_right'   : (min(move[1],     9 - move[0]), ( 1, -1)),
      'bottom_left' : (min(9 - move[1], move[0]),     (-1,  1))
    }
    pos_flips = []
    for stop, (x, y) in directions.values():
      pos_flips.append(self._get_flip_positions(board, stop, move, x, y))
    return self._uniq(pos_flips)

  def _get_flip_positions(self, board, stop, move, x, y):
    pos_flips = []
    for i in range(1, stop):
      pos = (move[0] + x * i, move[1] + y * i)
      if board[pos] == EMPTY: break
      if board[pos] == PLAYER:
        for p in pos_flips:
          board[p] = PLAYER
        return pos_flips
      pos_flips.append(pos)
    return []

  def _uniq(self, arr):
    arr = reduce(lambda a, e: a if e in a else a + [e], arr, [])
    return [e for e in arr if e]

  def __str__(self):
    return str(self.board)

def won_game(record, display=False):
  othello = Othello()
  for move in record:
    if move == '0':
      break
    othello.make_move([int(move[0]), int(move[1])])
  PLAYER_count = 0
  for row in range(8):
    for col in range(8):
      if othello[row, col] == PLAYER:
        PLAYER_count += 1
  if PLAYER_count == 32:
    return None
  if display: print(othello)
  return PLAYER if PLAYER_count > 32 else OPPONENT

def make_othello_recoad():
  files = glob.glob('WTH/*')
  records = []
  for f in files:
    for l in open(f, 'rb'):
      l = l[16:]
      for e in [l[i: i + 68] for i in range(0, len(l), 68)]:
        records.append(e[8:])
  for record in records[0:10]:
    othello = Othello()
    for move in record:
      if move == 0: break
      othello.make_move([move // 10, move % 10])
    print(othello)

def main():
  unit = [100, 100, 64]
  model = Classifier(MLP(unit))
  chainer.cuda.get_device(0).use()
  model.to_gpu()
  optimizer = chainer.optimizers.Adam()
  optimizer.setup(model)
  chainer.serializers.load_npz('othello_model.npz', model)

  othello = Othello()
  for _ in range(60):
    print(othello)
    X1 = np.array([othello.board.cells], dtype=np.float32)
    X1 = cuda.to_gpu(X1, device=0)
    y = F.softmax(model.predictor(X1))
    y_ = int(y.data.argmax(1)[0])
    y = y_ // 8 * 10 + y_ % 8 + 11
    print("y = {}\n".format(y))
    move = int(input('move: '))
    othello.make_move((move // 10, move % 10))

if __name__ == '__main__':
  main()
