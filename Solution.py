import pandas as pd
import numpy as np

letter_options = ['X']
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class Cell(object):
    """
    Cell object for individual cells on the board.
    """

    def __init__(self, letter):
        self.value = letter
        self.value_options = ({self.value, 'X'} if self.value
                              else set(letter_options))

    def set(self, options):
        self.value_options = options
        return self.check()

    def check(self):
        if len(self.value_options) == 1:
            self.value = self.value_options.pop()
            return True
        return False

    def __add__(self, other):
        return [self, other]


class EndViewBoard(object):
    """
    Board is the entire board for the game with a size of "grid_size".
    """

    def __init__(self, grid_size, top, bottom, left, right):
        self.grid_size = grid_size
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

        print(top.constraints)
        print(bottom.constraints)
        print(left.constraints)
        print(right.constraints)

        self.board = self.load_board()

    def load_board(self):

        d_board = []
        for _ in range(self.grid_size):
            d_board.append([Cell('')
                            for _ in range(self.grid_size)])

        df_board = pd.DataFrame(d_board)
        return df_board

    def __repr__(self):
        return "EndViewBoard({}, {}, {}, {})".format(self.grid_size,
                                                     self.top,
                                                     self.bottom,
                                                     self.left,
                                                     self.right)

    def __str__(self):

        disp_board = []

        for index, rows in self.board.iterrows():
            disp_board.append([cell.value for column, cell in rows.iteritems()])

        return "\n".join([''.join(["{:4}".format(str(item)) for item in row])
                          for row in disp_board])


def solve(grid_size, letter_set, top, bottom, left, right):
    global letter_options
    if grid_size < len(letter_set):
        raise Exception("Grid size not proper. Size of the board must be "
                        "greater than the length of the letter set.")

    letter_options = letter_options + letter_set
    board = EndViewBoard(grid_size, top, bottom, left, right)
    print("\n####\n")
    print(board)
