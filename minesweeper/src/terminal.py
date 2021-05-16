import argparse
import curses
import functools
from curses import wrapper

from _engine import *


class Cursor:

    def __init__(self, height, width):
        self.value = 0
        self.height = height
        self.width = width

    def __iadd__(self, other):
        self.value += other if self.value + other in range(self.height * self.width) else 0
        return self

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __iter__(self):
        return iter(divmod(self.value, self.height))


class MinesweeperGrid(Grid):

    def __init__(self, stdscr, height, width, mines, begin_y=1, begin_x=2):
        super().__init__(height, width, mines)
        self._scr = curses.newwin(2 * height + 2, 4 * width + 1, begin_y, begin_x)
        self._cursor = Cursor(height, width)
        self._stdscr = stdscr
        self._draw_border()
        self._refresh()

    def _refresh(self):
        for i in range(self.height):
            for j in range(self.width):
                cell = self[i, j]
                attr = curses.A_NORMAL
                if cell.is_opened and cell.is_mine:
                    attr = curses.color_pair(curses.COLOR_RED) + curses.A_BOLD
                elif cell.is_marked:
                    attr = curses.color_pair(curses.COLOR_CYAN) + curses.A_BOLD
                elif cell.is_unknown:
                    attr = curses.color_pair(curses.COLOR_GREEN)

                self._scr.addstr(1 + i * 2, 1 + j * 4, f' {cell} ', attr)

        i, j = self._cursor
        self._scr.addstr(1 + i * 2, 1 + j * 4, f' {self[i, j]} ', curses.A_REVERSE)

        self._scr.refresh()

    def play(self):
        while not self.is_completed():
            ch = self._stdscr.getch()
            row, col = self._cursor

            if ch == curses.KEY_UP:
                self._cursor -= self.width
            elif ch == curses.KEY_DOWN:
                self._cursor += self.width
            elif ch == curses.KEY_LEFT:
                self._cursor -= 1
            elif ch == curses.KEY_RIGHT:
                self._cursor += 1
            elif ch == ord('f') or ch == ord('m'):
                self.mark(row, col)
            elif ch == ord(' '):
                self.open(row, col)

            self._refresh()

    def _draw_border(self, horizontal='─', vertical='│', vertical_horizontal='┼',
                     down_right='┌', down_left='┐', up_right='└', up_left='┘',
                     down_horizontal='┬', vertical_left='┤', up_horizontal='┴', vertical_right='├'):

        def add_str(row, left, block, separator, right):
            self._scr.addstr(row, 0, left + (block * 3 + separator) * (self.width - 1) + block * 3 + right,
                             curses.color_pair(curses.COLOR_GREEN))

        add_str(0, down_right, horizontal, down_horizontal, down_left)
        for i in range(self.height - 1):
            for j in range(1, 2):
                add_str(i * 2 + j, vertical, ' ', vertical, vertical)
            add_str(i * 2 + 2, vertical_right, horizontal, vertical_horizontal, vertical_left)
        for i in range(1, 2):
            add_str(self.height * 2 - i, vertical, ' ', vertical, vertical)
        add_str(self.height * 2, up_right, horizontal, up_horizontal, up_left)


def main(args, stdscr: curses.window):
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()
    for color in curses.COLOR_GREEN, curses.COLOR_CYAN, curses.COLOR_RED:
        curses.init_pair(color, color, curses.COLOR_BLACK)
    stdscr.refresh()

    minesweeper = MinesweeperGrid(stdscr, args.height, args.width, args.mines)
    minesweeper.play()

    while True:
        if stdscr.getch() == 10:
            break


def parse_args():
    parser = argparse.ArgumentParser(description='Command-line minesweeper game.', add_help=False)
    parser.add_argument('--height', type=int, default=10, help='Height of game grid.')
    parser.add_argument('--width', type=int, default=10, help='Width of game grid.')
    parser.add_argument('--mines', type=int, default=10, help='Specify number of mines.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Display detailed help.')
    return parser.parse_args()


if __name__ == '__main__':
    wrapper(functools.partial(main, parse_args()))
