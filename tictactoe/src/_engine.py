import abc
import copy
import enum
import functools
import itertools
import random

from math import inf

__all__ = (
    'Sign',
    'Board',
    'Player',
    'RandomStrategyPlayer',
    'MinimaxStrategyPlayer',
    'strategies',
    'play'
)


class Sign(enum.Enum):
    NONE = ' '
    X = 'X'
    O = 'O'

    def __bool__(self):
        return self != Sign.NONE

    def __str__(self):
        return self.value

    def __neg__(self):
        return Sign.NONE if self == Sign.NONE else (Sign.X if self == Sign.O else Sign.O)


class Board:
    _size: int = 3
    _view: str = """\
 % | % | % 
--- --- ---
 % | % | % 
--- --- ---
 % | % | % \
""".replace('%', '%s')

    def __init__(self):
        self._state = [Sign.NONE for _ in range(self._size * self._size)]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            key = key[0] * self._size + key[1]
        return self._state[key]

    def __setitem__(self, key, value):
        if not isinstance(value, Sign):
            raise ValueError('unsupported value')
        if isinstance(key, tuple):
            key = key[0] * self._size + key[1]
        if self._state[key]:
            raise ValueError('cell not empty')
        self._state[key] = value

    def __repr__(self):
        return self._view % tuple(self._state)

    def winner(self):
        for _slice in self._slices():
            if winner := functools.reduce(lambda a, i: a if a == i else None, _slice):
                return winner

    @property
    def empty_cells(self):
        return [i[0] for i in enumerate(self._state) if not i[1]]

    def _slices(self):
        size = self._size
        for i in range(size):
            yield self._state[i * size:i * size + size]
            yield self._state[i::size]
        yield self._state[::size + 1]
        yield self._state[size - 1:size * size - 1:size - 1]


class Player(abc.ABC):

    def __init__(self, sign: Sign):
        self._sign = sign

    @abc.abstractmethod
    def next_move(self, board: Board):
        pass

    @property
    def sign(self) -> Sign:
        return self._sign


class RandomStrategyPlayer(Player):

    def next_move(self, board: Board):
        return random.choice(board.empty_cells)


class MinimaxStrategyPlayer(Player):

    def __init__(self, sign: Sign, max_depth=9):
        super().__init__(sign)
        self._max_depth = max_depth

    def next_move(self, board: Board):
        depth = len(board.empty_cells)
        if depth == 9:
            return random.choice(board.empty_cells)
        else:
            return self._minimax(board, min(depth, self._max_depth), self.sign)[1]

    def _minimax(self, board, depth, sign):
        best = -inf if self.sign == sign else + inf, None

        if board.winner() == -sign:
            return depth + 1 if self.sign == -sign else -depth - 1, None
        elif depth == 0:
            return 0, None

        for cell in board.empty_cells:
            nboard = copy.deepcopy(board)
            nboard[cell] = sign
            score = self._minimax(nboard, depth - 1, -sign)[0], cell
            best = (max if self.sign == sign else min)(score, best)

        return best


strategies = {
    "random": RandomStrategyPlayer,
    "minimax_easy": lambda sign: MinimaxStrategyPlayer(sign, 2),
    "minimax_normal": lambda sign: MinimaxStrategyPlayer(sign, 4),
    "minimax_hard": lambda sign: MinimaxStrategyPlayer(sign),
    "minimax": lambda sign: MinimaxStrategyPlayer(sign)
}


def play(first_player: Player, second_player: Player, board: Board = None, first_step=Sign.X):
    if board is None:
        board = Board()

    for player in itertools.dropwhile(lambda p: p.sign != first_step,
                                      itertools.cycle((first_player, second_player))):
        if not board.empty_cells:
            return None
        step = player.next_move(board)
        board[step] = player.sign
        if winner := board.winner():
            return winner
