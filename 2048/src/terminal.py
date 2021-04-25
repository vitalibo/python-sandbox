import argparse
import curses
import functools
import math
from curses import wrapper

from _engine import *


class TermGrid(Grid):

    def __init__(self, size=4, begin_y=3, begin_x=2):
        super().__init__(size)
        self._scr = curses.newwin(4 * size + 2, 9 * size + 1, begin_y, begin_x)
        self._score_scr = curses.newwin(1, 100, begin_y - 1, begin_x)
        self._draw_border()
        self.refresh()

    def refresh(self):
        for i in range(self.size):
            for j in range(self.size):
                value = ' ' if self[i, j] == 0 else str(self[i, j])
                attr = curses.A_BOLD
                if value != ' ':
                    attr += curses.color_pair(int(1 + math.log2(self[i, j])))

                for l, s in enumerate((' ' * 8, value.center(8), ' ' * 8)):
                    self._scr.addstr(1 + l + i * 4, 1 + j * 9, s, attr)

        self._scr.refresh()

        score, attr = ('Score: %08d', 0) if self.has_available_move() else ('Score: %08d | Game Over', curses.A_BLINK)
        self._score_scr.addstr(0, 0, score % self.score, attr)
        self._score_scr.refresh()

    def _draw_border(self, horizontal='─', vertical='│', vertical_horizontal='┼',
                     down_right='┌', down_left='┐', up_right='└', up_left='┘',
                     down_horizontal='┬', vertical_left='┤', up_horizontal='┴', vertical_right='├'):

        def add_str(row, left, block, separator, right):
            self._scr.addstr(row, 0, left + (block * 8 + separator) * (self.size - 1) + block * 8 + right)

        add_str(0, down_right, horizontal, down_horizontal, down_left)
        for i in range(self.size - 1):
            for j in range(1, 4):
                add_str(i * 4 + j, vertical, ' ', vertical, vertical)
            add_str(i * 4 + 4, vertical_right, horizontal, vertical_horizontal, vertical_left)
        for i in range(1, 4):
            add_str(self.size * 4 - i, vertical, ' ', vertical, vertical)
        add_str(self.size * 4, up_right, horizontal, up_horizontal, up_left)


def main(args, stdscr: curses.window):
    curses.noecho()
    curses.curs_set(0)
    stdscr.refresh()

    curses.start_color()
    colors = ((0x00, 0xE2), (0x00, 0xDC), (0x00, 0xD6), (0x00, 0xD0), (0x00, 0xCA), (0x07, 0xC4),
              (0x07, 0x01), (0x07, 0x05), (0x07, 0x12), (0x07, 0x14), (0x00, 0x02), (0x00, 0x2F))
    for items in [(i + 1, *pair) for i, pair in enumerate(colors)]:
        curses.init_pair(*items)

    grid = TermGrid(size=args.size)
    while grid.has_available_move():
        ch = stdscr.getch()
        if ch == curses.KEY_UP:
            grid.up()
        elif ch == curses.KEY_DOWN:
            grid.down()
        elif ch == curses.KEY_LEFT:
            grid.left()
        elif ch == curses.KEY_RIGHT:
            grid.right()
        grid.refresh()

    stdscr.getch()


def parse_args():
    parser = argparse.ArgumentParser(description='Command-line 2048 game.', add_help=False)
    parser.add_argument('-n', '--size', type=int, default=4, help='Size of game grid.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Display detailed help.')
    return parser.parse_args()


if __name__ == '__main__':
    wrapper(functools.partial(main, parse_args()))
