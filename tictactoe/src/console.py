#!/usr/bin/env python3

import argparse
import os

from _engine import *

__all__ = (
    'ConsolePlayer'
    'main'
)

LOGO = """
████████╗██╗ ██████╗    ████████╗ █████╗  ██████╗    ████████╗ ██████╗ ███████╗
╚══██╔══╝██║██╔════╝    ╚══██╔══╝██╔══██╗██╔════╝    ╚══██╔══╝██╔═══██╗██╔════╝
   ██║   ██║██║    █████╗  ██║   ███████║██║    █████╗  ██║   ██║   ██║█████╗  
   ██║   ██║██║    ╚════╝  ██║   ██╔══██║██║    ╚════╝  ██║   ██║   ██║██╔══╝  
   ██║   ██║╚██████╗       ██║   ██║  ██║╚██████╗       ██║   ╚██████╔╝███████╗
   ╚═╝   ╚═╝ ╚═════╝       ╚═╝   ╚═╝  ╚═╝ ╚═════╝       ╚═╝    ╚═════╝ ╚══════╝
"""


def _print(board):
    os.system('clear' if os.name == 'posix' else 'cls')
    print(LOGO)
    print(board)
    print()


class ConsolePlayer(Player):

    def next_move(self, board: Board):
        _print(board)
        while True:
            try:
                cell = int(input('Player %s enter a cell number to move: ' % self.sign)) - 1
            except ValueError:
                print('\033[91mERROR: Value should be digits.\033[0m')
            else:
                if cell not in range(9):
                    print('\033[91mERROR: Value should be in range (1-9).\033[0m')
                elif cell not in board.empty_cells:
                    print('\033[91mERROR: Cell is not empty.\033[0m')
                else:
                    return cell


class WrapPlayer(Player):

    def __init__(self, delegate: Player):
        super().__init__(delegate.sign)
        self._delegate = delegate

    def next_move(self, board: Board):
        _print(board)
        return self._delegate.next_move(board)


strategies['disable'] = ConsolePlayer


def parse_args():
    signs = (Sign.X, Sign.O)
    parser = argparse.ArgumentParser(description='Command-line Tic-Tac-Toe game.', add_help=False)
    parser.add_argument('--sign', type=Sign, default=Sign.X, choices=signs, help='Specify a sign to play for it.')
    parser.add_argument('--start-sign', type=Sign, default=Sign.X, choices=signs, help='Which sign will goes first.')
    parser.add_argument('--strategy', type=str, default='minimax', choices=strategies.keys(), help='Strategy name.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Display detailed help.')
    return parser.parse_args()


def main(args):
    print('You (%s) vs. Opponent (%s). Player %s will go first.' % (args.sign, -args.sign, args.start_sign))
    board = Board()

    winner = play(
        ConsolePlayer(args.sign),
        WrapPlayer(strategies[args.strategy](-args.sign)),
        board,
        args.start_sign
    )

    _print(board)
    print('Player %s win!' % winner if winner is not None else 'Draw')


if __name__ == '__main__':
    print(LOGO)
    main(parse_args())
