import pandas as pd
import numpy as np

letter_options = ['X']


def _make_cell(constraints):
    """
    Helper function for EndViewBoard.load_board().
    Initializes each cell with 'X' as an option.
    :return:
    """
    cell = Cell(constraints)
    cell.set_options('X')
    return cell


class Cell(object):
    """
    Cell object for individual cells on the board.
    """

    def __init__(self, constraints):
        self.top, self.bottom, self.left, self.right = constraints

        self.value = ""
        self.value_option = ""
        self.value_set = []

    def set_options(self, letter):
        if self.check(letter):
            self.value_set += letter

    def set(self, option):
        self.value_option = option
        return self.verify(option)

    def check(self, l):
        if l and not len(l) > 0:
            self.value_set = self.value_set[:1]
        if l not in self.value_set and len(self.value_set) < 2:
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

    def __init__(self, grid_size, constraints):
        self.grid_size = grid_size
        self.top, self.bottom, self.left, self.right = constraints

        self.board = self.load_board(constraints)
        self.board = self.get_initial_state(self.board)
        self.board_values = self._board_values()

    def load_board(self, constraints):

        d_board = []
        for _ in range(self.grid_size):
            d_board.append([_make_cell(constraints) for _ in range(self.grid_size)])

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
            cell.set_options(x if x else list('IRAGE'))
        for cell in board[self.grid_size - 1]:
            x = bot.pop()
            cell.set_options(x if x else list('IRAGE'))
        for cell in board[:, 0]:
            x = left.pop()
            cell.set_options(x if x else list('IRAGE'))
        for cell in board[:, self.grid_size - 1]:
            x = right.pop()
            cell.set_options(x if x else list('IRAGE'))
        return board

    def all_cells(self):

        return ([(*index, value)
                for index, value in np.ndenumerate(self.board_values)])

    def _board_values(self):
        disp_board = []

        for rows in self.board:
            disp_board.append([cell.value_set for cell in rows])

        return np.array(disp_board)

    def __repr__(self):
        return "EndViewBoard({}, {}, {}, {})".format(self.grid_size,
                                                     self.top,
                                                     self.bottom,
                                                     self.left,
                                                     self.right)

    def __str__(self):

        return pd.DataFrame(self.board_values).to_string()


def solve(grid_size, letter_set, t, b, l, r):
    global letter_options
    constraints = [t, b, l, r]
    if grid_size < len(letter_set):
        raise Exception("Grid size not proper. Size of the board must be "
                        "greater than the length of the letter set.")

    letter_options = letter_options + letter_set
    board = EndViewBoard(grid_size, constraints)
    print("\n####\n")
    # print(pd.DataFrame(board.board))

    # for (r, c, value) in board.all_cells():
    #     # print(r, c, value)
    #     if value != ['X']:
    #         if len(value) == 1:
    #             board.board[r][c].value = value[0]
    #             continue
    #
    #         option = value[-1]
    #         if board.board[r][c].set(option):
    #             print("Found {} at {}, {} through Cell.set()".format(option,
    #                                                                  r, c))
    #
    #     break

    print(board)
