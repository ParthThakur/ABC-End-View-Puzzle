import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 500)

letter_options = ['X']
grid_size = 0


def _make_cell(i, j):
    """
    Helper function for EndViewBoard.load_board().
    Initializes each cell with 'X' as an option.
    :return:
    """
    cell = Cell(i, j)
    return cell


def load_board():

    d_board = []
    for i in range(grid_size):
        d_board.append([_make_cell(i, j) for j in range(grid_size)])

    df_board = np.array(d_board)
    # print(df_board)
    return df_board


class Cell(object):
    """
    Cell object for individual cells on the board.
    """

    def __init__(self, row, column):
        self.row = row
        self.column = column

        self.value = ""
        self.value_try = ""
        self.value_set = [np.nan]

    def set_options(self, letter):
        if self.check(letter):
            self.value_set += letter

    def set(self, option):
        if self.verify(option):
            self.value = option
            return True
        return False

    def check(self, l):
        if not type(l) == str:
            pass
        elif l:
            self.value_set = self.value_set[:1]

        if l not in self.value_set and len(self.value_set) < 2:
            return True
        return False

    def verify(self, option):
        if len(option) == 1:
            return True
        self.value_set.pop()
        return False

    def try_(self, option):
        self.value_try = option
        return self.verify(option)

    def __add__(self, other):
        raise Exception("Don't try to add two cells.")


class EndViewBoard(object):
    """
    Board is the entire board for the game with a size of "grid_size".
    """

    def __init__(self, constraints):
        self.top, self.bottom, self.left, self.right = constraints

        self.board = load_board()
        self.board = self.get_initial_state(self.board)
        self.board_values = self._board_values()

    def get_initial_state(self, board):
        top = self.top.constraints[::-1]
        bot = self.bottom.constraints[::-1]
        left = self.left.constraints[::-1]
        right = self.right.constraints[::-1]
        for cell in board[0]:
            x = top.pop()
            cell.set_options(x if x else list('IRAGE'))
        for cell in board[grid_size - 1]:
            x = bot.pop()
            cell.set_options(x if x else list('IRAGE'))
        for cell in board[:, 0]:
            x = left.pop()
            cell.set_options(x if x else list('IRAGE'))
        for cell in board[:, grid_size - 1]:
            x = right.pop()
            cell.set_options(x if x else list('IRAGE'))
        return board

    def all_cells(self):
        return ([(*index, value)
                for index, value in np.ndenumerate(self.board_values)])

    def check_cell(self, cell):
        r, c = cell.row, cell.column
        x = grid_size - len(letter_options)
        try_value = cell.value_try
        row = self.board_values[r]
        column = self.board_values[:, c]
        if try_value in row:
            if try_value in column:
                return False
        # if r <= x:
        #     if c <= x:
        #         if try_value == self.top.constraints[c]:
        #             if 'X' == (column[:r]).all():
        #                 if 'X' == (row[:c]).all():
        #                     return True
        #         if try_value == self.left.constraints[c]:
        #             if 'X' == (column[:r]).all():
        #                 if 'X' == (row[:c]).all():
        #                     return True
        return True

    def _board_values(self):
        value_board = []
        for rows in self.board:
            value_board.append([cell.value_set for cell in rows])
        return np.array(value_board)

    def __repr__(self):
        return "EndViewBoard({}, {}, {}, {})".format(grid_size,
                                                     self.top,
                                                     self.bottom,
                                                     self.left,
                                                     self.right)

    def __str__(self):
        disp_board = []
        for rows in self.board:
            disp_board.append([cell.value for cell in rows])
        return pd.DataFrame(disp_board).to_string()


def solve(g_s, letter_set, t, b, l, r):
    global letter_options
    global grid_size
    grid_size = g_s
    constraints = [t, b, l, r]
    if grid_size < len(letter_set):
        raise Exception("Grid size not proper. Size of the board must be "
                        "greater than the length of the letter set.")

    letter_options = letter_options + letter_set
    board = EndViewBoard(constraints)
    print("\n####\n")
    # print(pd.DataFrame(board.board_values))

    for (r, c, value) in board.all_cells():
        print(r, c, value)
        cell = board.board[r][c]
        if len(value) == 1:
            cell.value = value[0]
            continue

        option = value.pop()
        while len(value) >= 0:
            print("try value:", option)
            if cell.try_(option):
                if board.check_cell(cell):
                    cell.set(option)
                    break
                option = value.pop()
    print(board)
