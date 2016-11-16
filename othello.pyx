from __future__ import print_function

from functools import reduce
from copy import deepcopy
from glob import glob
from struct import unpack

import numpy as np
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training, Variable, cuda
from chainer.training import extensions
from neural_net import MLP, Classifier


EMPTY    = 0
PLAYER   = 1
OPPONENT = 2
VALID    = 3

DISC_MARK = {
  EMPTY   : '-',
  PLAYER  : 'O',
  OPPONENT: 'X',
  VALID   : '*'
}

class Board():
  def __init__(self, cells=None):
    self.black_playing = True
    if cells is None:
      self.cells = np.zeros(64, dtype=np.int32).reshape([8, 8])
      self[4, 5] = PLAYER
      self[5, 4] = PLAYER
      self[4, 4] = OPPONENT
      self[5, 5] = OPPONENT
    else:
      self.cells = cells

  def clone(self):
    return Board(deepcopy(self.cells))

  def switch_turn(self):
    self.black_playing = not self.black_playing
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


class Othello():
  def __init__(self):
    self.board = Board()
    self.valid_moves = []
    self.update_valid_moves()

  def make_move(self, move):
    for m in self.valid_moves:
      self.board[m] = EMPTY
    self._flip_disks(self.board, move)
    self.board.switch_turn()
    self.update_valid_moves()

    if not self.valid_moves:
      self.board.switch_turn()
      self.update_valid_moves()

  def update_valid_moves(self):
    del self.valid_moves[:]
    for row in range(1, 9):
      for col in range(1, 9):
        if self.board[row, col] == EMPTY:
          board = self.board.clone()
          if self._flip_disks(board, (row, col)):
            self.valid_moves.append((row, col))
    self.valid_moves = self._uniq(self.valid_moves)
    for m in self.valid_moves:
      self.board[m] = VALID

  def _flip_disks(self, board, move):
    board[move] = PLAYER
    directions = (
      (9 - move[0], ( 1,  0)),
      (9 - move[1], ( 0,  1)),
      (move[0],     (-1,  0)),
      (move[1],     ( 0, -1)),
      (min(move[1],     move[0]),     (-1, -1)),
      (min(9 - move[1], 9 - move[0]), ( 1,  1)),
      (min(move[1],     9 - move[0]), ( 1, -1)),
      (min(9 - move[1], move[0]),     (-1,  1))
    )
    pos_flips = []
    for stop, (x, y) in directions:
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


def make_othello_recoad():
  file_names = glob('WTH/*.wtb')
  records_black = []
  records_white = []
  for file_name in file_names:
    with open(file_name, 'rb') as f:
      for _ in range(unpack('I', f.read(16)[4:8])[0]):
        hands = unpack('B' * 68, f.read(68))
        if hands[6] == 32: continue
        if hands[6] > 32:
          records_black.append(hands[8:])
        else:
          records_white.append(hands[8:])

  out_file = open('othello.csv', 'w')
  for i, record in enumerate(records_black):
    othello = Othello()
    if i % 100 == 0: print(i)
    for move in record:
      if move == 0: break
      if othello.board.black_playing:
        out_file.write('{}{}\n'.format(reduce(lambda a, e: '{}{},'.format(a, e), othello.board.cells.flatten(), ''), move))
      othello.make_move([move // 10, move % 10])
  
  for i, record in enumerate(records_white):
    othello = Othello()
    if i % 100 == 0: print(i)
    for move in record:
      if move == 0: break
      if not othello.board.black_playing:
        out_file.write('{}{}\n'.format(reduce(lambda a, e: '{}{},'.format(a, e), othello.board.cells.flatten(), ''), move))
      othello.make_move([move // 10, move % 10])
  out_file.close()


def main():
  unit = [1000, 1000, 64]
  model = Classifier(MLP(unit))
  # chainer.cuda.get_device(0).use()
  # model.to_gpu()
  optimizer = chainer.optimizers.Adam()
  optimizer.setup(model)
  chainer.serializers.load_npz('othello_model.npz', model)

  othello = Othello()
  for _ in range(60):
    print(othello)
    X1 = np.array([othello.board.cells], dtype=np.float32)
    # X1 = cuda.to_gpu(X1, device=0)
    y = F.softmax(model.predictor(X1))
    y_ = int(y.data.argmax(1)[0])
    y = y_ // 8 * 10 + y_ % 8 + 11
    print("y = {}\n".format(y))
    move = int(input('move: '))
    move = (move // 10, move % 10)
    if move in othello.valid_moves:
      othello.make_move(move)


if __name__ == '__main__':
  from time import time
  s = time()
  make_othello_recoad()
  print(time() - s)
