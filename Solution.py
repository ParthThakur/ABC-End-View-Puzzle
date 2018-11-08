import pandas as pd
import numpy as np

letter_options = ['X']
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def _make_cell():
    """
    Helper function for EndViewBoard.load_board().
    Initializes each cell with 'X' as an option.
    :return:
    """
    cell = Cell()
    cell.set_options('X')
    return cell


class Cell(object):
    """
    Cell object for individual cells on the board.
    """

    def __init__(self):
        self.value = ""
        self.value_option = ""
        self.value_set = []

    def set_options(self, letter):
        if self.check(letter):
            self.value_set.append(letter)

    def set(self, letter):
        self.value_option = letter
        return self.check()

    def check(self, l):
        if l not in self.value_set:
            return True
        return False

        # if len(self.value_set) == 1:
        #     self.value = self.value_set.pop()
        #     return True
        # return False

    def __add__(self, other):
        raise Exception("Don't try to add two cells.")


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

        self.board = self.load_board()
        self.board = self.get_initial_state(self.board)

    def load_board(self):

        d_board = []
        for _ in range(self.grid_size):
            d_board.append([_make_cell() for _ in range(self.grid_size)])

        df_board = np.array(d_board)
        # print(df_board)
        return df_board

    def get_initial_state(self, board):
        top = self.top.constraints[::-1]
        bot = self.bottom.constraints[::-1]
        left = self.left.constraints[::-1]
        right = self.right.constraints[::-1]
        for cell in board[0]:
            x = top.pop()
            cell.set_options(x)
        for cell in board[self.grid_size - 1]:
            x = bot.pop()
            cell.set_options(x)
        for cell in board[:, 0]:
            x = left.pop()
            cell.set_options(x)
        for cell in board[:, self.grid_size - 1]:
            x = right.pop()
            cell.set_options(x)
        return board

    def __repr__(self):
        return "EndViewBoard({}, {}, {}, {})".format(self.grid_size,
                                                     self.top,
                                                     self.bottom,
                                                     self.left,
                                                     self.right)

    def __str__(self):

        disp_board = []

        for rows in self.board:
            disp_board.append([cell.value_set for cell in rows])
        print(pd.DataFrame(disp_board))

        return ""


def solve(grid_size, letter_set, top, bottom, left, right):
    global letter_options
    if grid_size < len(letter_set):
        raise Exception("Grid size not proper. Size of the board must be "
                        "greater than the length of the letter set.")

    letter_options = letter_options + letter_set
    board = EndViewBoard(grid_size, top, bottom, left, right)
    print("\n####\n")
    # print(pd.DataFrame(board.board))
    print(board)
    #
    # board.board[0][0].set_options('A')
    # board.board[0][0].set_options('B')
    # board.board[0][1].set_options('C')
    # board.board[0][1].set_options('D')
    # print(board.board[0][0].value_set)
    # print(board.board[0][1].value_set)
