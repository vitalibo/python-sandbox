import collections
import random


class Grid:
    _view: str = """\
┌─────────┬─────────┬─────────┐
│ %  %  % │ %  %  % │ %  %  % │
│ %  %  % │ %  %  % │ %  %  % │
│ %  %  % │ %  %  % │ %  %  % │
├─────────┼─────────┼─────────┤
│ %  %  % │ %  %  % │ %  %  % │
│ %  %  % │ %  %  % │ %  %  % │
│ %  %  % │ %  %  % │ %  %  % │
├─────────┼─────────┼─────────┤
│ %  %  % │ %  %  % │ %  %  % │
│ %  %  % │ %  %  % │ %  %  % │
│ %  %  % │ %  %  % │ %  %  % │
└─────────┴─────────┴─────────┘\
""".replace('%', '%s')

    def __init__(self, filling_percent=0.25):
        self._state = [' ' for _ in range(9 * 9)]
        self._fill()
        if not self.is_resolved():
            raise ValueError('generated grid is not resolved')
        self._clean(filling_percent)
        self._unmodified = tuple(divmod(i, 9) for i, v in enumerate(self._state) if v != ' ')

    def __getitem__(self, key):
        if isinstance(key, tuple):
            key = key[0] * 9 + key[1]
        return self._state[key]

    def __setitem__(self, key, value):
        if value not in ' 123456789':
            raise ValueError('unsupported value')
        if isinstance(key, tuple):
            key = key[0] * 9 + key[1]
        self._state[key] = value

    def __repr__(self):
        return self._view % tuple(self._state)

    @property
    def unmodified(self):
        return self._unmodified

    def is_resolved(self):
        if ' ' in self._state:
            return False
        for _ in self.mistakes():
            return False
        return True

    def mistakes(self):
        for items in self._slices():
            for _, count in collections.Counter(i for _, _, i in items if i != ' ').items():
                if count > 1:
                    yield from tuple((x, y) for x, y, _ in items)

    def _fill(self):
        for idx in range(9 * 9):
            y, x = divmod(idx, 9)
            if self[y, x] == ' ':
                for value in random.sample([str(i) for i in range(1, 10)], k=9):
                    items = self._slice_row(y) + self._slice_column(x) + self._slice_square(y // 3 * 3, x // 3 * 3)
                    if value not in [i for _, _, i in items]:
                        self[y, x] = value
                        if self.is_resolved():
                            return True
                        if self._fill():
                            return True
                break
        self[y, x] = ' '

    def _clean(self, percent):
        if percent < 0.01 or percent > 0.99:
            raise ValueError('filling percent should be in range [0.01, 0.99]')

        for _ in range(int(9 * 9 * (1 - percent))):
            y = random.randint(0, 8)
            x = random.randint(0, 8)
            while self[y, x] == ' ':
                y = random.randint(0, 8)
                x = random.randint(0, 8)
            self[y, x] = ' '

    def _slices(self):
        for i in range(3):
            for j in range(3):
                yield self._slice_square(i * 3, j * 3)
        for i in range(9):
            yield self._slice_row(i)
            yield self._slice_column(i)

    def _slice_square(self, sy, sx):
        def fn():
            for y in range(3):
                for x in range(3):
                    yield sy + y, sx + x, self[sy + y, sx + x]

        return tuple(fn())

    def _slice_row(self, sy):
        def fn():
            for x in range(9):
                yield sy, x, self[sy, x]

        return tuple(fn())

    def _slice_column(self, sx):
        def fn():
            for y in range(9):
                yield y, sx, self[y, sx]

        return tuple(fn())
