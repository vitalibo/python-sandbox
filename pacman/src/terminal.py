from __future__ import annotations

import abc
import argparse
import curses
import functools
import random
import sys
import time
import typing
from curses import wrapper
from datetime import datetime, timedelta
from enum import Enum
from threading import Timer

CLASSIC_MAP = """\
╔═════════════════════════╗ ╔═════════════════════════╗
║ · · · · · · · · · · · · ║ ║ · · · · · · · · · · · · ║
║ · ╔═════╗ · ╔═══════╗ · ║ ║ · ╔═══════╗ · ╔═════╗ · ║
║ * ║     ║ · ║       ║ · ║ ║ · ║       ║ · ║     ║ * ║
║ · ╚═════╝ · ╚═══════╝ · ╚═╝ · ╚═══════╝ · ╚═════╝ · ║
║ · · · · · · · · · · · · · · · · · · · · · · · · · · ║
║ · ╔═════╗ · ╔═╗ · ╔═════════════╗ · ╔═╗ · ╔═════╗ · ║
║ · ╚═════╝ · ║ ║ · ╚═════╗ ╔═════╝ · ║ ║ · ╚═════╝ · ║
║ · · · · · · ║ ║ · · · · ║ ║ · · · · ║ ║ · · · · · · ║
╚═════════╗ · ║ ╚═════╗   ║ ║   ╔═════╝ ║ · ╔═════════╝
          ║ · ║ ╔═════╝   ╚═╝   ╚═════╗ ║ · ║          
          ║ · ║ ║           A         ║ ║ · ║          
══════════╝ · ╚═╝   ╔═════───═════╗   ╚═╝ · ╚══════════
            ·       ║   A   A   A ║       ·            
══════════╗ · ╔═╗   ╚═════════════╝   ╔═╗ · ╔══════════
          ║ · ║ ║         I           ║ ║ · ║          
          ║ · ║ ║   ╔═════════════╗   ║ ║ · ║          
╔═════════╝ · ╚═╝   ╚═════╗ ╔═════╝   ╚═╝ · ╚═════════╗
║ · · · · · · · · · · · · ║ ║ · · · · · · · · · · · · ║
║ · ╔═════╗ · ╔═══════╗ · ║ ║ · ╔═══════╗ · ╔═════╗ · ║
║ · ╚═══╗ ║ · ╚═══════╝ · ╚═╝ · ╚═══════╝ · ║ ╔═══╝ · ║
║ * · · ║ ║ · · · · · · · · C · · · · · · · ║ ║ · · * ║
╚═══╗ · ║ ║ · ╔═╗ · ╔═════════════╗ · ╔═╗ · ║ ║ · ╔═══╝
╔═══╝ · ╚═╝ · ║ ║ · ╚═════╗ ╔═════╝ · ║ ║ · ╚═╝ · ╚═══╗
║ · · · · · · ║ ║ · · · · ║ ║ · · · · ║ ║ · · · · · · ║
║ · ╔═════════╝ ╚═════╗ · ║ ║ · ╔═════╝ ╚═════════╗ · ║
║ · ╚═════════════════╝ · ╚═╝ · ╚═════════════════╝ · ║
║ · · · · · · · · · · · · · · · · · · · · · · · · · · ║
╚═════════════════════════════════════════════════════╝\
"""


class Block(abc.ABC):

    def __init__(self, y: int, x: int, char=' ') -> None:
        self.y = y
        self.x = x
        self.char = char

    @abc.abstractmethod
    def draw(self, screen: curses.window) -> None:
        pass

    def __repr__(self) -> str:
        return self.char


class Wall(Block):
    def draw(self, screen: curses.window) -> None:
        screen.addstr(self.y, self.x * 2, self.char, curses.color_pair(curses.COLOR_BLUE))


class Door(Wall):
    pass


class Empty(Block):
    def draw(self, screen: curses.window) -> None:
        screen.addstr(self.y, self.x * 2, '  ')


class Info(Empty):
    pass


class Cookie(Block):
    def draw(self, screen: curses.window) -> None:
        screen.addstr(self.y, self.x * 2, self.char, curses.color_pair(curses.COLOR_GREEN))


class Pill(Block):
    def draw(self, screen: curses.window) -> None:
        screen.addstr(self.y, self.x * 2, self.char, curses.color_pair(curses.COLOR_GREEN))


class Direction(Enum):
    Up = 12
    Down = 21
    Left = 34
    Right = 43

    def __neg__(self) -> Direction:
        high, low = divmod(self.value, 10)
        return Direction(low * 10 + high)


class Mob(Block, abc.ABC):

    def __init__(self, y: int, x: int, direction: Direction) -> None:
        super().__init__(y, x)
        self.direction = direction
        self.__original = Empty(y, x)
        self.__spawn = (y, x, direction)

    def spawn(self, game: Game) -> None:
        game.map[self.y][self.x] = self.__original
        self.y, self.x, self.direction = self.__spawn
        self.__original = Empty(self.y, self.x)
        game.map[self.y][self.x] = self

    def do(self, game: Game, direction: typing.Union[None, Direction]) -> bool:
        direction = direction if direction else self.direction

        ny, nx = self.y, self.x
        if direction in (Direction.Up, Direction.Down):
            ny += -1 if direction == Direction.Up else 1
        else:
            nx += -1 if direction == Direction.Left else 1

        swap = lambda i, __max: i if 0 <= i < __max else (0 if 0 <= i else __max - 1)
        ny, nx = swap(ny, game.map.rows), swap(nx, game.map.cols)

        block = game.map[ny][nx]
        if not self.do_move(game, block):
            return False

        game.map[self.y][self.x] = self.__original
        self.y, self.x = ny, nx
        self.__original = game.map[self.y][self.x]
        if isinstance(self.__original, Mob):
            self.__original = self.__original.__original
        game.map[self.y][self.x] = self
        self.direction = direction
        return True

    @abc.abstractmethod
    def do_move(self, game: Game, block: Block) -> bool:
        pass


class Pacman(Mob):

    def __init__(self, y: int, x: int, *args) -> None:
        super().__init__(y, x, Direction.Left)

    def do_move(self, game: Game, block: Block) -> bool:
        if isinstance(block, (Wall, Door)):
            return False
        elif isinstance(block, (Cookie, Pill)):
            game.map[block.y][block.x] = Empty(block.y, block.x)
            game.score += 10
            game.cookies -= 1
            if isinstance(block, Pill):
                for ghost in game.ghosts:
                    ghost.eatable = True
        elif isinstance(block, Ghost):
            if block.eatable:
                self.eat_ghost(game, block)
            else:
                block.eat_pacman(game, self)
            return False
        return True

    @staticmethod
    def eat_ghost(game: Game, ghost: Ghost) -> None:
        game.score += 100
        ghost.spawn(game)

    def draw(self, screen: curses.window) -> None:
        screen.addstr(self.y, self.x * 2, 'C', curses.color_pair(0xDC) + curses.A_BOLD)


class Ghost(Mob):
    __colors = [curses.COLOR_RED, curses.COLOR_MAGENTA, curses.COLOR_CYAN, curses.COLOR_YELLOW]

    def __init__(self, y: int, x: int, *args) -> None:
        super().__init__(y, x, random.choice(list(Direction)))
        self.__color = random.choice(Ghost.__colors)
        Ghost.__colors.remove(self.__color)
        self.__probability_change_direction = 0.6
        self.__remain_steps_when_is_eatable = 0

    @property
    def eatable(self):
        return self.__remain_steps_when_is_eatable > 0

    @eatable.setter
    def eatable(self, enable):
        self.__remain_steps_when_is_eatable = 30 if enable else 0

    def do(self, game: Game, direction: typing.Union[None, Direction]) -> None:
        if self.__remain_steps_when_is_eatable > 0:
            self.__remain_steps_when_is_eatable -= 1

        directions = list(Direction)
        directions.remove(self.direction)
        directions.remove(-self.direction)
        random.shuffle(directions)

        if random.uniform(0, 1) > self.__probability_change_direction:
            for direction in directions:
                if super(Ghost, self).do(game, direction):
                    return

        directions.insert(0, None)
        directions.append(-self.direction)
        for direction in directions:
            if super(Ghost, self).do(game, direction):
                return

    def do_move(self, game: Game, block: Block) -> bool:
        if isinstance(block, Door):
            pass
        elif isinstance(block, (Wall, Ghost)):
            return False
        elif isinstance(block, Pacman):
            if self.eatable:
                block.eat_ghost(game, self)
            else:
                self.eat_pacman(game, block)
            return False
        return True

    @staticmethod
    def eat_pacman(game: Game, pacman: Pacman) -> None:
        game.life -= 1
        pacman.spawn(game)
        for ghost in game.ghosts:
            ghost.spawn(game)

    def draw(self, screen: curses.window) -> None:
        screen.addstr(self.y, self.x * 2, 'O', curses.A_BOLD +
                      curses.color_pair(curses.COLOR_GREEN if self.eatable else self.__color))


class Map(list):

    @property
    def rows(self) -> int:
        return len(self)

    @property
    def cols(self) -> int:
        return len(self[0])

    def draw(self, screen: curses.window) -> None:
        for block in self.blocks():
            block.draw(screen)
        screen.refresh()

    def blocks(self, types=(Block,)):
        blocks = []
        for row_blocks in self:
            for block in row_blocks:
                if isinstance(block, types):
                    blocks.append(block)
        return blocks

    @staticmethod
    def parse(definition) -> Map:
        supported_blocks = {
            '╔': Wall, '╗': Wall, '╚': Wall, '╝': Wall, '═': Wall, '║': Wall, '─': Door,
            ' ': Empty, '·': Cookie, '*': Pill, 'C': Pacman, 'A': Ghost, 'I': Info
        }

        def parse_row(y, row):
            for x in range(0, len(row), 2):
                func = supported_blocks[row[x]]
                yield func(y, x // 2, row[x:x + 2])

        return Map([list(parse_row(y, row)) for y, row in enumerate(definition.split('\n'))])


class Game:

    def __init__(self, map_definition: str, stdscr: curses.window, speed: float, life: int) -> None:
        self.__stdscr = stdscr
        self.map = Map.parse(map_definition)
        self.__scr = curses.newwin(self.map.rows, self.map.cols * 2, 1, 0)
        self.__speed = speed
        self.__timer = None
        self.__key_pressed = None
        self.__key_pressed_ts = datetime.now()
        self.pacman: Pacman = self.map.blocks(Pacman)[0]
        self.ghosts: typing.List[Ghost] = self.map.blocks(Ghost)
        self.cookies = len(self.map.blocks((Cookie, Pill)))
        self.info: Info = self.map.blocks(Info)[0]
        self.life = life
        self.score = 0

    def start(self) -> None:
        if self.life == 0:
            return

        self.__timer = Timer(self.__speed, self.do)
        self.__timer.start()

    def __enter__(self):
        self.draw()
        self.show_info('READY!')
        time.sleep(1.5)
        self.start()
        return self

    def do(self) -> None:
        if (datetime.now() - self.__key_pressed_ts) > timedelta(seconds=self.__speed * 2):
            self.__key_pressed = None
        if not self.pacman.do(self, self.__key_pressed):
            self.pacman.do(self, None)
        else:
            self.__key_pressed = None

        for ghost in self.ghosts:
            ghost.do(self, None)

        self.draw()
        self.start()

    def play(self) -> None:
        while self.life > 0 and self.cookies > 0:
            ch = self.__stdscr.getch()
            if ch == curses.KEY_UP:
                self.__key_pressed = Direction.Up
            elif ch == curses.KEY_DOWN:
                self.__key_pressed = Direction.Down
            elif ch == curses.KEY_LEFT:
                self.__key_pressed = Direction.Left
            elif ch == curses.KEY_RIGHT:
                self.__key_pressed = Direction.Right
            else:
                continue
            self.__key_pressed_ts = datetime.now()

    def draw(self) -> None:
        self.map.draw(self.__scr)
        self.__scr.refresh()
        self.__stdscr.addstr(0, 0, f'SCORE:  {self.score:05d}', curses.A_BOLD)
        self.__stdscr.addstr(0, self.map.cols * 2 - 10, f'LIFE : {self.life:02d}', curses.A_BOLD)
        self.__stdscr.refresh()

    def stop(self) -> None:
        self.__timer.cancel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.show_info('GAME OVER!')

    def show_info(self, msg: str) -> None:
        self.__scr.addstr(self.info.y, self.info.x * 2 - (len(msg) // 2 - 2), msg, curses.A_BOLD)
        self.__scr.refresh()


def main(args, stdscr: curses.window):
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()
    for color in curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_MAGENTA, \
                 curses.COLOR_YELLOW, curses.COLOR_RED, curses.COLOR_CYAN, 0xDC:
        curses.init_pair(color, color, curses.COLOR_BLACK)
    stdscr.refresh()

    try:
        with Game(CLASSIC_MAP, stdscr, args.speed, args.life) as game:
            game.play()
    except KeyboardInterrupt:
        return

    while True:
        if stdscr.getch() == 10:
            break


def parse_args(args):
    parser = argparse.ArgumentParser(description='Command-line Pacman game.', add_help=False)
    parser.add_argument('--speed', type=float, default=0.3, help='Game speed.')
    parser.add_argument('--life', type=int, default=3, help='Pac-Man life.')
    return parser.parse_args(args=args)


if __name__ == '__main__':
    wrapper(functools.partial(main, parse_args(sys.argv[1:])))
