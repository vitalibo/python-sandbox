import random


class Grid:

    def __init__(self, size: int = 4):
        self.score = 0
        self.size = size
        self._cells = [[0] * self.size for _ in range(self.size)]
        for _ in range(2):
            self._random_cell()

        self._up_index = tuple([[(i, j) for i in range(self.size)] for j in range(self.size)])
        self._down_index = tuple([[(i, j) for i in range(self.size - 1, -1, -1)] for j in range(self.size)])
        self._left_index = tuple([[(i, j) for j in range(self.size)] for i in range(self.size)])
        self._right_index = tuple([[(i, j) for j in range(self.size - 1, -1, -1)] for i in range(self.size)])

    def up(self):
        self._do(self._up_index)

    def down(self):
        self._do(self._down_index)

    def left(self):
        self._do(self._left_index)

    def right(self):
        self._do(self._right_index)

    def _do(self, index):
        modified = self._compress(index)
        if modified:
            self._random_cell()

    def _compress(self, index, dryrun=False):
        modified = False
        for row in range(self.size):
            for column in range(self.size - 1):

                for column_from in range(column, self.size):
                    if self[index[row][column_from]] == 0:
                        for column_to in range(column_from + 1, self.size):
                            if self[index[row][column_to]] != 0:
                                if not dryrun:
                                    for _ in range(column_to - column_from):
                                        self._shift_left(index, row, column_from)
                                modified = True
                                break

                if self[index[row][column]] == self[index[row][column + 1]] \
                        and self[index[row][column]] != 0:
                    if not dryrun:
                        self[index[row][column]] *= 2
                        self._shift_left(index, row, column + 1)
                        self.score += self[index[row][column]]
                    modified = True

        return modified

    def _shift_left(self, index, row, column):
        for j in range(column, self.size - 1):
            self[index[row][j]] = self[index[row][j + 1]]
        self[index[row][self.size - 1]] = 0

    def _random_cell(self):
        choice = random.choice(self._empty_cells())
        self[choice] = random.randint(1, 2)

    def _empty_cells(self):
        return [(i, j) for i in range(self.size) for j in range(self.size) if self[i, j] == 0]

    def __getitem__(self, item):
        i, j = item
        return self._cells[i][j]

    def __setitem__(self, key, value):
        i, j = key
        self._cells[i][j] = value

    def __repr__(self):
        return '\n'.join([str(self._cells[i]) for i in range(self.size)])

    def has_available_move(self):
        if self._empty_cells():
            return True

        def test(index):
            return self._compress(index, dryrun=True)

        return test(self._up_index) or test(self._down_index) or test(self._left_index) or test(self._right_index)
