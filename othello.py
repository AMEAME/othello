from __future__ import print_function

from config import *
from functools import reduce
from copy import deepcopy

EMPTY    = 0
PLAYER   = 1
OPPONENT = 2
VALID    = 3

DISC_MARK = {
  EMPTY:    '-',
  PLAYER:   'o',
  OPPONENT: 'x'
}

class Othello():
  def __init__(self):
    self.init_board()
    self.valid_moves = []

  def init_board(self):
    self.board = [[EMPTY] * (8) for _ in range(8)]
    self[4, 5] = PLAYER
    self[5, 4] = PLAYER
    self[4, 4] = OPPONENT
    self[5, 5] = OPPONENT
    self.update_valid_moves()

  def make_move(self, move):
    for m in valid_moves:
      self[m] = EMPTY
    self.flip_disks(self.board, move)
    self.switch_turn()
    self.update_valid_moves()
    if not self.valid_moves:
      self.switch_turn()

  def update_valid_moves(self):
    del self.valid_moves[:]
    for row in range(1, 9):
      for col in range(1, 9):
        if self[row, col] == EMPTY:
          board = deepcopy(self.board)
          if not _flip_disks(board, (row, col)):
            self.valid_moves.append((row, col))
    self.valid_moves = list(set(self.valid_moves))
    for m in self.valid_moves:
      self[m] = VALID

  def switch_turn
    if cell != EMPTY:
      cell = OPPONENT if cell == PLAYER else PLAYER
    else
      cell
    return [[ for cell in row] for row in self.board]
      

  def _flip_disks(self, board, move):
    self[move] = PLAYER
    right  = 9 - move[0]
    bottom = 9 - move[1]
    left   = move[0]
    top    = move[1]
    min_by_size = lambda arr1, arr2: arr1 if len(arr1) < len(arr2) else arr2
    directions = {
      'right' : (right,  ( 1,  0)),
      'bottom': (bottom, ( 0,  1)),
      'left'  : (left,   (-1,  0)),
      'top'   : (top,    ( 0, -1)),
      'top_left'    : (min_by_size(top,    left),  (-1, -1)),
      'bottom_right': (min_by_size(bottom, right), ( 1,  1)),
      'top_right'   : (min_by_size(top,    right), ( 1, -1)),
      'bottom_left' : (min_by_size(bottom, left),  (-1,  1))
    }
    pos_flips = []
    for scope, (x, y) in directions:
      pos_flips.append(get_flip_positions(board, range, move, x, y))
    return pos_flips

  def get_flip_positions(board, scope, move, x, y):
    pos_flips = []
    for i in scope:
      pos = (move[0] + x * i, move[1] + y * i)
      if board[pos] == EMPTY: break
      if board[pos] == PLAYER:
        for p in pos_flips:
          board[p] = PLAYER
        return pos_flips
      pos_flips.append(pos)
    return []

  def __getitem__(self, disc_pos):
    if 1 <= disc_pos[0] <= 8 and 1 <= disc_pos[1] <= 8:
      return self.board[disc_pos[1] - 1][disc_pos[0] - 1]
    return EMPTY

  def __setitem__(self, disc_pos, value):
    self.board[disc_pos[1] - 1][disc_pos[0] - 1] = value
    return self.board

  def __str__(self):
    def join(a, e):
      return a + DISC_MARK[e] + ' '
    rangement = [str(i + 1) + ' ' for i in range(8)]
    string = '  {}\n'.format(reduce(lambda a, e: a + e, rangement, ''))
    for i, row in enumerate(self.board):
      string += '{} {}\n'.format(i + 1, reduce(join, row, ''))
    return string


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


if __name__ == '__main__':
  record = [l.rstrip().split(',') for l in open('data.csv')][0]
  won_game(record, display=True)
