import random
from enum import Enum


class Cell:
    class State(Enum):
        UNKNOWN = 0
        OPENED = 1
        MARKED = 2

    def __init__(self, row, column):
        self.state = Cell.State.UNKNOWN
        self.is_mine = False
        self.mines = 0
        self.row = row
        self.column = column

    @property
    def is_unknown(self):
        return self.state == Cell.State.UNKNOWN

    @property
    def is_opened(self):
        return self.state == Cell.State.OPENED

    @property
    def is_marked(self):
        return self.state == Cell.State.MARKED

    def __repr__(self):
        if self.is_unknown:
            return '?'
        elif self.is_marked:
            return 'F'
        elif self.is_mine:
            return 'X'
        else:
            return str(self.mines if self.mines > 0 else ' ')


class Grid:
    def __init__(self, height=10, width=10, mines=10):
        self.height = height
        self.width = width
        self._state = [[Cell(row, column) for column in range(height)] for row in range(width)]
        self._mines = self._fill(mines)
        self._marks = []

    def __getitem__(self, key):
        return self._state[key[0]][key[1]]

    def open(self, row, col):
        cell = self[row, col]
        if not cell.is_unknown:
            return

        if cell.is_mine:
            for mine in self._mines:
                if not mine.is_marked:
                    mine.state = Cell.State.OPENED

        cell.state = Cell.State.OPENED
        if cell.mines == 0:
            for neighbor in self._neighbors(row, col):
                self.open(neighbor.row, neighbor.column)

    def mark(self, row, col):
        cell = self[row, col]
        if cell.is_unknown and len(self._marks) < len(self._mines):
            cell.state = Cell.State.MARKED
            self._marks.append(cell)
        elif cell.is_marked:
            cell.state = Cell.State.UNKNOWN
            self._marks.remove(cell)

    def is_completed(self):
        for mine in self._mines:
            if mine.is_opened:
                return True

        for mine in self._mines:
            if not mine.is_marked:
                return False

        return True

    def _fill(self, n):
        mines = {}
        while len(mines) < n:
            position = random.randrange(self.width), random.randrange(self.height)
            if position in mines:
                continue

            cell = self[position]
            cell.is_mine = True
            mines[position] = cell

        for mine in mines.values():
            for neighbor in self._neighbors(mine.row, mine.column):
                neighbor.mines += 1

        return mines.values()

    def _neighbors(self, row, col):
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if i in range(self.width) and j in range(self.height):
                    yield self[i, j]

    def __repr__(self):
        def row():
            for i in range(self.height):
                yield str(self._state[i])

        return '\n'.join(row())
