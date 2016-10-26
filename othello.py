# coding: utf-8
from __future__ import print_function

from config import *
from functools import reduce

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


class Othello(object):

    def __init__(self):
        self.init_board()
        self.valid_moves = []

    def init_board(self):
        self.board = [[EMPTY] * (OTHELLO_LEN) for _ in range(OTHELLO_LEN)]
        for d in DISC_INIT:
            self[d[0]] = d[1]
        self.update_valid_moves()

    def update_valid_moves(self):
        return None

    def switch_turn(self):
        for row in range(OTHELLO_LEN):
            for col in range(OTHELLO_LEN):
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
                range(OTHELLO_LEN - move[0]),
                lambda i: (move[0] + 1 + i, move[1])
            ],
            'bottom': [
                range(OTHELLO_LEN - move[1]),
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
                range(OTHELLO_LEN - max(move)),
                lambda i: (move[0] + 1 + i, move[1] + 1 + i)
            ],
            'top_right': [
                range(min([OTHELLO_LEN - move[0], move[1] - 1])),
                lambda i: (move[0] + 1 + i, move[1] - 1 - i)
            ],
            'bottom_left': [
                range(min([move[0] - 1, OTHELLO_LEN - move[1]])),
                lambda i: (move[0] - 1 - i, move[1]  + 1 + i)
            ]
        }
        for dir in directions:
            self.flip(directions[dir][0], directions[dir][1])

        self.switch_turn()

    def __getitem__(self, disc_pos):
        if 1 <= disc_pos[0] <= OTHELLO_LEN and 1 <= disc_pos[1] <= OTHELLO_LEN:
            return self.board[disc_pos[1] - 1][disc_pos[0] - 1]
        return 0

    def __setitem__(self, disc_pos, value):
        self.board[disc_pos[1] - 1][disc_pos[0] - 1] = value
        return self.board

    def __str__(self):
        def join(a, e):
            return a + DISC_MARK[e] + ' '
        rangement = [str(i + 1) + ' ' for i in range(OTHELLO_LEN)]
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
    for row in range(OTHELLO_LEN):
        for col in range(OTHELLO_LEN):
            if othello[row, col] == PLAYER:
                PLAYER_count += 1
    if PLAYER_count == 32:
        return None
    if display: print(othello)
    return PLAYER if PLAYER_count > 32 else OPPONENT


if __name__ == '__main__':
    record = [l.rstrip().split(',') for l in open('data.csv')][0]
    won_game(record, display=True)
