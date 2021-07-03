import argparse
import curses
import functools
import sys
from curses import wrapper

from _engine import *


class ShellGame(Game):

    def __init__(self, speed: float, length: int, stdscr: curses.window):
        super().__init__(speed, length)
        self.__stdscr = stdscr
        self.__queue = set()

    def move(self, direction: Direction = None) -> None:
        super(ShellGame, self).move(direction)
        self.draw()

    def draw(self):
        def draw_point(point, attr):
            _y, ch = divmod(point.y, 2)
            point = _y, point.x
            self.__stdscr.addstr(*point, '█' if point in self.__queue else ('▀' if ch == 0 else '▄'), attr)
            self.__queue.add(point)

        for y, x in self.__queue:
            self.__stdscr.addstr(y, x, ' ')
        self.__queue.clear()

        for point in self.snake:
            draw_point(point, curses.color_pair(curses.COLOR_GREEN if self.is_alive else curses.COLOR_RED))
        draw_point(self.apple, curses.color_pair(curses.COLOR_GREEN))

        self.__stdscr.refresh()


def main(args, stdscr: curses.window):
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()
    for color in curses.COLOR_GREEN, curses.COLOR_CYAN, curses.COLOR_RED:
        curses.init_pair(color, color, curses.COLOR_BLACK)
    stdscr.refresh()

    rows, cols = stdscr.getmaxyx()
    Game.Height, Game.Width = rows * 2 - 1, cols - 2
    game = ShellGame(args.speed, args.length, stdscr)
    game.draw()

    try:
        while game.is_alive:
            ch = stdscr.getch()
            if ch == curses.KEY_UP:
                game.up()
            elif ch == curses.KEY_DOWN:
                game.down()
            elif ch == curses.KEY_LEFT:
                game.left()
            elif ch == curses.KEY_RIGHT:
                game.right()

    except KeyboardInterrupt:
        game.stop()
        return

    message = f'Your score: {game.score}'
    stdscr.addstr(Game.Height // 2, Game.Width - len(message), message)

    while True:
        if stdscr.getch() == 10:
            break


def parse_args(args):
    parser = argparse.ArgumentParser(description='Command-line Snake game.', add_help=False)
    parser.add_argument('--speed', type=float, default=0.3, help='Snake speed.')
    parser.add_argument('--length', type=int, default=3, help='Initial snake length.')
    return parser.parse_args(args=args)


if __name__ == '__main__':
    wrapper(functools.partial(main, parse_args(sys.argv[1:])))
