from __future__ import print_function
from functools import reduce


EMPTY = 0
PLAYER = 1
OPPONENT = 2
VALID = 3

DISC_MARK = {
  EMPTY: '-',
  PLAYER: 'o',
  OPPONENT: 'x'
}

DISC_INIT = (
  ((4, 5), PLAYER),
  ((5, 4), PLAYER),
  ((4, 4), OPPONENT),
  ((5, 5), OPPONENT)
)

class Othello:
  def __init__(self):
    self.init_board()
    self.valid_moves = []

  def init_board(self):
    self.board = [[EMPTY] * (8) for _ in range(8)]
    for d in DISC_INIT:
      self[d[0]] = d[1]
    self.update_valid_moves()

  def update_valid_moves(self):
    return None

  def switch_turn(self):
    for row in range(8):
      for col in range(8):
        if self.board[row][col] == EMPTY:
          continue
        self.board[row][col] = OPPONENT if \
          self.board[row][col] == PLAYER else PLAYER

  def flip(self, scope, calc_place):
    pos_flip = []
    for i in scope:
      place = calc_place(i)
      if self[place] == EMPTY:
        return
      if self[place] == PLAYER:
        for p in pos_flip:
          self[p] = PLAYER
        return
      pos_flip.append(place)

  def make_move(self, move):
    self[move] = PLAYER
    directions = {
      'right': [
        range(8 - move[0]),
        lambda i: (move[0] + 1 + i, move[1])
      ],
      'bottom': [
        range(8 - move[1]),
        lambda i: (move[0], move[1] + 1 + i)
      ],
      'left': [
        range(move[0] - 1),
        lambda i: (move[0] - 1 - i, move[1])
      ],
      'top': [
        range(move[1] - 1),
        lambda i: (move[0], move[1] - 1 - i)
      ],
      'top_left': [
        range(min(move) - 1),
        lambda i: (move[0] - 1 - i, move[1] - 1 - i)
      ],
      'bottom_right': [
        range(8 - max(move)),
        lambda i: (move[0] + 1 + i, move[1] + 1 + i)
      ],
      'top_right': [
        range(min([8 - move[0], move[1] - 1])),
        lambda i: (move[0] + 1 + i, move[1] - 1 - i)
      ],
      'bottom_left': [
        range(min([move[0] - 1, 8 - move[1]])),
        lambda i: (move[0] - 1 - i, move[1]  + 1 + i)
      ]
    }
    for dir in directions:
      self.flip(directions[dir][0], directions[dir][1])

    self.switch_turn()

  def __getitem__(self, disc_pos):
    if 1 <= disc_pos[0] <= 8 and 1 <= disc_pos[1] <= 8:
      return self.board[disc_pos[1] - 1][disc_pos[0] - 1]
    return EMPTY

  def __setitem__(self, disc_pos, value):
    self.board[disc_pos[1] - 1][disc_pos[0] - 1] = value
    return self.board

  def __str__(self):
    rangement = [str(i + 1) + ' ' for i in range(8)]
    string = '  {}\n'.format(reduce(lambda a, e: a + e, rangement, ''))
    for i, row in enumerate(self.board):
      string += '{} {}\n'.format(i + 1,
                  reduce(lambda a, e: a + DISC_MARK[e] + ' ', row, ''))
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

def main():
  othello = Othello()

if __name__ == '__main__':
  main()
