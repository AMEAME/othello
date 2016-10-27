EMPTY = 0
PLAYER = 1
OPPONENT = 2
VALID = 3
OTHELLO_LEN = 8

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
