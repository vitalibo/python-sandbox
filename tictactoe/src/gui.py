#!/usr/bin/env python3

import argparse
import queue
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import tkinter.messagebox as tkmessagebox

from _engine import *

__all__ = (
    'BoardFrame',
    'main'
)


class BoardFrame(tk.Frame):

    def __init__(self, **kw):
        super().__init__(**kw)
        self._events = queue.Queue()
        self._cells = list()
        for i in range(3):
            row = []
            for j in range(3):
                frame = tk.Frame(master=self, relief=tk.SUNKEN, borderwidth=1)
                frame.grid(row=i, column=j)
                label = tk.Label(master=frame, text=' ', height=1, width=2, font=(None, 48, tkfont.BOLD))
                label.bind('<Button-1>', lambda event, x=i, y=j: self._events.put(x * 3 + y))
                label.pack(fill=tk.BOTH)
                row.append(label)
            self._cells.append(row)

    def __setitem__(self, key, value):
        i, j = key if isinstance(key, tuple) else divmod(key, 3)
        self._cells[i][j].configure(text=str(value), foreground='red' if value == Sign.X else 'blue')

    def wraps(self, delegate: Player):
        class Inner(Player):
            def next_move(self, board: Board):
                cell = delegate.next_move(board)
                _outer_self[cell] = self.sign
                time.sleep(0.1)
                _outer_self._events.queue.clear()
                return cell

        _outer_self = self
        return Inner(delegate.sign)

    def manual(self, sign: Sign):
        class Inner(Player):
            def next_move(self, board: Board):
                while True:
                    cell = _outer_self._events.get()
                    if cell in board.empty_cells:
                        return cell

        _outer_self = self
        return self.wraps(Inner(sign))


def parse_args():
    signs = (Sign.X, Sign.O)
    strategies['disable'] = None
    parser = argparse.ArgumentParser(description='Tic-Tac-Toe game.', add_help=False)
    parser.add_argument('--sign', type=Sign, default=Sign.X, choices=signs, help='Specify a sign to play for it.')
    parser.add_argument('--start-sign', type=Sign, default=Sign.X, choices=signs, help='Which sign will goes first.')
    parser.add_argument('--strategy', type=str, default='minimax', choices=strategies.keys(), help='Strategy name.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Display detailed help.')
    return parser.parse_args()


def main(args):
    window = tk.Tk()
    window.title('Tic-Tac-Toe')
    window.resizable(False, False)
    frame = BoardFrame(master=window)
    frame.pack()

    def run():
        strategies['disable'] = frame.manual
        winner = play(frame.manual(args.sign), frame.wraps(strategies[args.strategy](-args.sign)))

        tkmessagebox.showinfo(
            message='Player %s win!' % winner if winner is not None else 'Draw',
            command=lambda ignore: sys.exit(0)
        )

    thread = threading.Thread(target=run, args=())
    thread.start()

    window.mainloop()


if __name__ == '__main__':
    main(parse_args())
