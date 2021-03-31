#!/usr/bin/env python3

import argparse
import curses
import functools
from curses import wrapper

from _engine import *

LOGO = """\
                _       _          
               | |     | |         
  ___ _   _  __| | ___ | | ___   _ 
 / __| | | |/ _` |/ _ \\| |/ / | | |
 \\__ \\ |_| | (_| | (_) |   <| |_| |
 |___/\\__,_|\\__,_|\\___/|_|\\_\\\\__,_|\
"""


class Cursor:

    def __init__(self):
        self.value = 0

    def __iadd__(self, other):
        self.value += other if self.value + other in range(9 * 9) else 0
        return self

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __iter__(self):
        return iter(divmod(self.value, 9))


class TermGrid(Grid):
    _GRID = """\
╔═══════════╦═══════════╦═══════════╗
║   │   │   ║   │   │   ║   │   │   ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║   │   │   ║   │   │   ║   │   │   ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║   │   │   ║   │   │   ║   │   │   ║
╠═══════════╬═══════════╬═══════════╣
║   │   │   ║   │   │   ║   │   │   ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║   │   │   ║   │   │   ║   │   │   ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║   │   │   ║   │   │   ║   │   │   ║
╠═══════════╬═══════════╬═══════════╣
║   │   │   ║   │   │   ║   │   │   ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║   │   │   ║   │   │   ║   │   │   ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║   │   │   ║   │   │   ║   │   │   ║
╚═══════════╩═══════════╩═══════════╝\
"""

    def __init__(self, stdscr: curses.window, filling_percent=0.25, begin_y=2, begin_x=2):
        super().__init__(filling_percent)
        self._stdscr = stdscr
        self._grdscr = curses.newwin(20, 37, begin_y, begin_x)
        for i, line in enumerate(self._GRID.split('\n')):
            self._grdscr.addstr(i, 0, line, curses.color_pair(curses.COLOR_GREEN))
        self._cursor = Cursor()

    def refresh(self, force=False):
        is_resolved = self.is_resolved()
        mistakes = tuple(self.mistakes())
        for y, x in map(lambda i: divmod(i, 9), range(9 * 9)):
            attr = curses.A_NORMAL
            if (y, x) in self.unmodified:
                attr = curses.color_pair(curses.COLOR_CYAN)
            if (y, x) in mistakes:
                attr = curses.color_pair(curses.COLOR_RED)
            if (y, x) in self.unmodified:
                attr += curses.A_BOLD
            if is_resolved:
                attr = curses.color_pair(curses.COLOR_CYAN) + curses.A_BLINK
            self._grdscr.addstr(1 + y * 2, 1 + x * 4, f' {self[y, x]} ', attr)
        if force:
            self._grdscr.refresh()

    def getch(self):
        y, x = self._cursor
        self.refresh()
        self._grdscr.addstr(1 + y * 2, 1 + x * 4, f' {self[y, x]} ', curses.A_REVERSE)
        self._grdscr.refresh()
        ch = self._stdscr.getch()
        self._grdscr.addstr(1 + y * 2, 1 + x * 4, f' {self[y, x]} ')
        return ch

    def play(self):
        while not self.is_resolved():
            ch = self.getch()
            y, x = self._cursor
            if ch == curses.KEY_UP:
                self._cursor -= 9
            elif ch == curses.KEY_DOWN:
                self._cursor += 9
            elif ch == curses.KEY_LEFT:
                self._cursor -= 1
            elif ch == curses.KEY_RIGHT:
                self._cursor += 1
            elif ch == 127 and (y, x) not in self.unmodified:
                self[y, x] = ' '
            elif chr(ch) in '123456789' and (y, x) not in self.unmodified:
                self[y, x] = chr(ch)


def main(args, stdscr: curses.window):
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()
    for color in curses.COLOR_GREEN, curses.COLOR_CYAN, curses.COLOR_RED:
        curses.init_pair(color, color, curses.COLOR_BLACK)
    for i, line in enumerate(LOGO.split("\n")):
        stdscr.addstr(i + 2, 42, line, curses.color_pair(curses.COLOR_GREEN))
    stdscr.refresh()

    grid = TermGrid(stdscr, filling_percent=args.filling_percent)
    grid.play()
    grid.refresh(True)
    stdscr.getch()


def parse_args():
    parser = argparse.ArgumentParser(description='Command-line Sudoku game.', add_help=False)
    parser.add_argument('-f', '--filling_percent', type=float, default=0.25, help='Specify percentage of filling.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Display detailed help.')
    return parser.parse_args()


if __name__ == '__main__':
    wrapper(functools.partial(main, parse_args()))
