# coding: utf-8
from __future__ import print_function

from config import *
from functools import reduce

DISC_MARK = {
    EMPTY: '-',
    BLACK: 'x',
    WHITE: 'o'
}

DISC_INIT = [
    [(4, 5), BLACK],
    [(5, 4), BLACK],
    [(4, 4), WHITE],
    [(5, 5), WHITE]
]


class Othello(object):

    def __init__(self):
        self.init_board()
        self.valid_moves = []
        self.now_playing = BLACK

    def init_board(self):
        self.board = [[EMPTY] * (OTHELLO_LEN) for _ in range(OTHELLO_LEN)]
        for d in DISC_INIT:
            self[d[0]] = d[1]
        self.update_valid_moves()

    def update_valid_moves(self):
        return None

    def flip(self, scope, calc_place):
        pos_flip = []
        for i in scope:
            place = calc_place(i)
            if self[place] == EMPTY:
                return
            if self[place] == self.now_playing:
                for p in pos_flip:
                    self[p] = self.now_playing
                return
            pos_flip.append(place)

    def make_move(self, move):
        self[move] = self.now_playing
        directions = {
            'right': [
                range(OTHELLO_LEN - move[0]),
                lambda i: (move[0] + i + 1, move[1])
            ],
            'bottom': [
                range(OTHELLO_LEN - move[1]),
                lambda i: (move[0], move[1] + i + 1)
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
        self.now_playing = WHITE if self.now_playing == BLACK else BLACK

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


def game_won(record, display=False):
    othello = Othello()
    for move in record:
        if move == '0':
            break
        print(move)
        othello.make_move([int(move[0]), int(move[1])])
        print(othello)
    black_count = 0
    for row in range(OTHELLO_LEN):
        for col in range(OTHELLO_LEN):
            if othello[row, col] == BLACK:
                black_count += 1
    if black_count == 32:
        return None
    if display: print(othello)
    return BLACK if black_count > 32 else WHITE


if __name__ == '__main__':
    record = [l.rstrip().split(',') for l in open('data.csv')][0]
    game_won(record, display=True)
