#!/usr/bin/env python3

import argparse
import curses
import functools
from curses import wrapper

from _engine import *

LOGO = """
████████╗██╗ ██████╗    ████████╗ █████╗  ██████╗    ████████╗ ██████╗ ███████╗
╚══██╔══╝██║██╔════╝    ╚══██╔══╝██╔══██╗██╔════╝    ╚══██╔══╝██╔═══██╗██╔════╝
   ██║   ██║██║    █████╗  ██║   ███████║██║    █████╗  ██║   ██║   ██║█████╗  
   ██║   ██║██║    ╚════╝  ██║   ██╔══██║██║    ╚════╝  ██║   ██║   ██║██╔══╝  
   ██║   ██║╚██████╗       ██║   ██║  ██║╚██████╗       ██║   ╚██████╔╝███████╗
   ╚═╝   ╚═╝ ╚═════╝       ╚═╝   ╚═╝  ╚═╝ ╚═════╝       ╚═╝    ╚═════╝ ╚══════╝
"""

__all__ = (
    'TermBoard',
    'TermPlayer',
    'Cursor',
    'main'
)


class TermBoard(Board):

    def __init__(self, stdscr, gmscr):
        super().__init__()
        self._gmscr = gmscr
        self._stdscr = stdscr

    def __setitem__(self, key, value):
        super(TermBoard, self).__setitem__(key, value)
        if "_gmscr" in self.__dict__:
            self.refresh()

    def __getstate__(self):
        return self._state

    def __setstate__(self, state):
        self.__dict__['_state'] = state

    def refresh(self):
        for i, line in enumerate(str(self).split('\n')):
            self._gmscr.addstr(i, 0, line, curses.color_pair(curses.COLOR_CYAN))
        self._gmscr.refresh()

    def getch(self, y, x):
        self._gmscr.addstr(y * 2, x * 4, f' {self[y, x]} ', curses.A_REVERSE + curses.color_pair(curses.COLOR_CYAN))
        self._gmscr.refresh()
        ch = self._stdscr.getch()
        self._gmscr.addstr(y * 2, x * 4, f' {self[y, x]} ', curses.color_pair(curses.COLOR_CYAN))
        return ch


class Cursor:

    def __init__(self):
        self.value = 0

    def __iadd__(self, other):
        self.value += other if self.value + other in range(9) else 0
        return self

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __iter__(self):
        return iter(divmod(self.value, 3))


class TermPlayer(Player):

    def __init__(self, sign: Sign):
        super().__init__(sign)
        self._cursor = Cursor()

    def next_move(self, board: TermBoard):
        board.refresh()
        while True:
            ch = board.getch(*self._cursor)
            if ch == curses.KEY_UP:
                self._cursor -= 3
            elif ch == curses.KEY_DOWN:
                self._cursor += 3
            elif ch == curses.KEY_LEFT:
                self._cursor -= 1
            elif ch == curses.KEY_RIGHT:
                self._cursor += 1
            elif (ch == ord('\n') or ch == ord(' ')) and \
                    self._cursor.value in board.empty_cells:
                return self._cursor.value


class InfoWrapper(Player):

    def __init__(self, delegate: Player, index, info):
        super().__init__(delegate.sign)
        self._delegate = delegate
        self._index = index
        self._info = info

    def next_move(self, board: Board):
        self._info.addstr(1 - self._index, 0, ' ')
        self._info.addstr(self._index, 0, '>', curses.color_pair(curses.COLOR_RED))
        self._info.refresh()
        return self._delegate.next_move(board)


strategies['disable'] = TermPlayer


def parse_args():
    signs = (Sign.X, Sign.O)
    parser = argparse.ArgumentParser(description='Command-line Tic-Tac-Toe game.', add_help=False)
    parser.add_argument('--sign', type=Sign, default=Sign.X, choices=signs, help='Specify a sign to play for it.')
    parser.add_argument('--start-sign', type=Sign, default=Sign.X, choices=signs, help='Which sign will goes first.')
    parser.add_argument('--strategy', type=str, default='minimax', choices=strategies.keys(), help='Strategy name.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Display detailed help.')
    return parser.parse_args()


def main(args, stdscr: curses.window):
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()
    for color in curses.COLOR_GREEN, curses.COLOR_CYAN, curses.COLOR_RED, curses.COLOR_YELLOW:
        curses.init_pair(color, color, curses.COLOR_BLACK)
    for i, line in enumerate(LOGO.strip().split('\n')):
        stdscr.addstr(i + 1, 0, line, curses.color_pair(curses.COLOR_GREEN))
    stdscr.refresh()
    gamescr = curses.newwin(6, 11, 9, 3)
    infoscr = curses.newwin(8, 40, 10, 20)
    infoscr.addstr(0, 2, f'Player 1 ({args.sign})')
    infoscr.addstr(1, 2, f'Player 2 ({-args.sign})')
    infoscr.refresh()

    winner = play(
        InfoWrapper(TermPlayer(args.sign), 0, infoscr),
        InfoWrapper(strategies[args.strategy](-args.sign), 1, infoscr),
        TermBoard(stdscr, gamescr),
        args.start_sign
    )

    infoscr.addstr(2, 2, 'Player %s win!' % winner if winner is not None else 'Draw',
                   curses.A_BOLD + curses.color_pair(curses.COLOR_YELLOW))
    infoscr.refresh()
    stdscr.getch()


if __name__ == '__main__':
    wrapper(functools.partial(main, parse_args()))
