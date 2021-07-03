from __future__ import annotations

import random
import typing
from dataclasses import dataclass
from enum import Enum
from threading import Timer


class Direction(Enum):
    Up = 12
    Down = 21
    Left = 34
    Right = 43

    def __neg__(self):
        high, low = divmod(self.value, 10)
        return Direction(low * 10 + high)


@dataclass
class Point:
    __DIRECTIONS = {
        Direction.Up: lambda p: (p.x, p.y - 1),
        Direction.Down: lambda p: (p.x, p.y + 1),
        Direction.Left: lambda p: (p.x - 1, p.y),
        Direction.Right: lambda p: (p.x + 1, p.y)
    }

    x: int
    y: int

    def move(self, direction: Direction) -> Point:
        x, y = Point.__DIRECTIONS[direction](self)
        assert 0 <= x <= Game.Width and 0 <= y <= Game.Height, 'out of range'
        return Point(x, y)


class Snake(list):

    def __init__(self, direction: Direction, body: typing.List[Point]):
        super().__init__(body)
        self.direction = direction

    def move(self, direction: Direction, apple: Point) -> bool:
        self.direction = direction if direction else self.direction
        if not self.direction:
            return False

        eat_apple = True
        head = self[0].move(self.direction)
        if head != apple:
            eat_apple = False
            del self[-1]

        self.insert(0, head)
        assert head not in self[1:], 'snake eat self'
        return eat_apple

    def __repr__(self) -> str:
        return f'Snake({self.direction}, {list(self)})'


class Game:
    Width = 80
    Height = 20

    def __init__(self, speed: float, length: int):
        self.snake = self.spawn_snake(length)
        self.apple = self.spawn_apple()
        self.is_alive = True
        self.score = 0
        self.__speed = speed
        self.__timer = Timer(speed, self.move)
        self.__timer.start()

    def up(self) -> None:
        self.move(Direction.Up)

    def down(self) -> None:
        self.move(Direction.Down)

    def left(self) -> None:
        self.move(Direction.Left)

    def right(self) -> None:
        self.move(Direction.Right)

    def move(self, direction: Direction = None) -> None:
        if not self.is_alive or (direction and self.snake.direction and direction == -self.snake.direction):
            return

        try:
            if self.snake.move(direction, self.apple):
                self.apple = self.spawn_apple()
                self.score += 10
                if self.score % 100 == 0:
                    self.__speed -= self.__speed / 10

            self.__timer.cancel()
            self.__timer = Timer(self.__speed, self.move)
            self.__timer.start()
        except AssertionError:
            self.is_alive = False

    def stop(self):
        self.__timer.cancel()

    @staticmethod
    def spawn_snake(length: int):
        return Snake(None, [Point(length - i - 1, 0) for i in range(length)])

    def spawn_apple(self) -> Point:
        apple = Point(random.randint(0, Game.Width), random.randint(0, Game.Height))
        if apple in self.snake:
            return self.spawn_apple()

        return apple
