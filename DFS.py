"""
Implements the DFS algorithm on given puzzle.
' ' (<space>) implies an empty cell, which is also 'X' in most representations
of this puzzle.
"""

import pandas as pd
import numpy as np
import copy
from time import sleep

pd.set_option('display.max_columns', 1000)

letter_options = []
top, bot, left, right = [], [], [], []
grid_size = 0
no_nan = 0


def load_board():
    """
    Function initializes individual boxes on the board with ' ' values and it's
    position on the board.
    :return: NumPy array of Cell objects.
    """

    d_board = []
    for i in range(grid_size):
        d_board.append([Cell(i, j) for j in range(grid_size)])

    df_board = np.array(d_board)
    return df_board


class Cell(object):
    """
    Cell object for individual boxes on the board.
    """

    def __init__(self, row, column):
        """
        Initializes cells with index and ' ' values.
        :param row: Row index
        :param column: Column Index
        """
        self.row = row
        self.column = column

        self.value = str(' ')
        self.value_set = [' ', *letter_options]

    def __call__(self, option):
        self.value = option

    def __repr__(self):
        return ','.join(self.value_set)

    def __iter__(self):
        yield [option for option in self.value_set]

    def set_options(self, letter):
        """
        Set value options for cell.
        :param letter: List of options.
        :return: None
        """
        if self.check(letter):
            self.value_set += letter

    def remove_option(self, option):
        self.value_set.remove(option)

    def check(self, l):
        """
        Check if the all values in the set are string.
        :param l: List of options.
        :return: True if OK, False if not.
        """
        if not type(l) == str:
            pass
        elif l:
            self.value_set = self.value_set[:1]

        if l not in self.value_set and len(self.value_set) < 2:
            return True
        return False


class EndViewBoard(object):
    """
    Class for the entire puzzle. Creates a numpy array of individual boxes
    arranged in a matrix of size "grid_size".
    """

    def __init__(self):
        """
        Initialize Board of the puzzle.
        """

        self.board = load_board()  # Numpy array of cell objects.

    def __repr__(self):
        return pd.DataFrame(self.board_current_state()).to_string()

    def __iter__(self):
        for i in self.board:
            for cell in i:
                yield cell

    def remove_options(self, cell):
        letter = cell.value
        r, c = cell.row, cell.column
        row = self.board[r][c + 1:]
        column = self.board[:, c][r + 1:]

        for box in [*row, *column]:
            remove(box, letter)
        return None

    def check_cell(self, cell, letter):
        """
        Checks the value of the given cell.
        :param cell: Cell object to be checked.
        :param letter: Value of cell to check.
        :return: True if OK, False if not.
        """
        board_fix_values = self.board_current_state()
        (r, c) = (cell.row, cell.column)
        try_value = str(letter)
        row = np.delete(board_fix_values[r], c)
        column = np.delete(board_fix_values[:, c], r)

        # Check if value is ' '.
        # If ' ', return True only if the number of NaNs in row or column are
        # acceptable.
        if try_value == ' ':
            if sum(row[:c] == ' ') < no_nan:
                if sum(column[:r] == ' ') < no_nan:
                    return True
            else:
                return False

        # If letter already exists in row ar column, return False.
        if try_value in row or try_value in column:
            return False

        # Check entire Row.
        if 0 <= r <= grid_size:

            # If option is equal to top constraint, return true only if ' '
            # above of cell.
            # Also check if row index is permissible. i.e Cell is not too far
            # down, making other cells in row invalid.
            if try_value == top[c]:
                if r > no_nan:
                    return False
                if not (board_fix_values[:, c][:r] == ' ').all():
                    return False
            else:
                if top[c] != 0:
                    if set(column[:r]) == {' '}:
                        return False

            # If option is equal to bottom constraint, return true only if ' '
            # below cell.
            # Also check if row index is permissible. i.e Cell is not too far
            # up, making other cells in row invalid.
            if try_value == bot[c]:
                if r < grid_size - no_nan - 1:
                    return False
                if not (board_fix_values[r + 1:][:, c] == ' ').all():
                    return False
            else:
                if bot[c] in column.tolist():
                    return False

        # Check entire Column
        if 0 <= c <= grid_size:

            # If option is equal to left constraint, return true only if ' '
            # on left of the cell.
            # Also check if column index is permissible. i.e Cell is not too far
            # right, making other cells in row invalid.
            if try_value == left[r]:
                if c > no_nan:
                    return False
                if not (board_fix_values[r][:c] == ' ').all():
                    return False
            else:
                if left[r] != 0:
                    if set(row[:c]) == {' '}:
                        return False

            # If option is equal to right constraint, return true only if ' '
            # on right of the cell.
            # Also check if column index is permissible. i.e Cell is not too far
            # left, making other cells in row invalid.
            if try_value == right[r]:
                if c < grid_size - 1 - no_nan:
                    return False
                if not (board_fix_values[r][c + 1:] == ' ').all():
                    return False
            else:
                if right[r] in row.tolist():
                    return False
        return True

    def board_current_state(self):
        """
        :return: NumPy array of current values of individual cells.
        """
        set_values = []
        for rows in self.board:
            set_values.append([cell.value for cell in rows])
        return np.array(set_values)


def cell_set_option(cell, board):
    """
    Sets the value of the given cell.
    Goes through all possible values for the cell.
    :param cell: Cell object to set the value of.
    :param board: Latest puzzle board in Solution stack.
    :return: True if value is valid. False if none are.
    """
    value = cell.value_set
    try:
        letter = value.pop()
    except IndexError:
        return False
    if board.check_cell(cell, letter):
        cell(letter)
        return True
    else:
        if len(value) > 0:
            return cell_set_option(cell, board)


def remove(cell, value):
    try:
        cell.value_set.remove(value)
    except ValueError:
        pass


def first_pass(board):
    for cell in board:
        row = cell.row
        col = cell.column
        if row == 0:
            for x in top:
                cell.set_options(x) if x else None
        if col == 0:
            for x in top:
                cell.set_options(x) if x else None
        if row == grid_size - 1:
            for x in top:
                cell.set_options(x) if x else None
        if col == grid_size - 1:
            for x in top:
                cell.set_options(x) if x else None


def second_pass(board):
    for (row, col), cell in board:
        print(row, col, cell)
        for option in cell:
            if row < no_nan:
                if option == bot[col]:
                    cell.remove_option(option)


def guess_pythonic(board):
    board_stack = [copy.deepcopy(board)]
    best_solution = board_stack[-1]
    cells = [cell for cell in board]
    index = 0

    while len(board_stack) > 0:
        cell = cells[index]
        if cell_set_option(cell, board_stack[-1]):
            board_stack.append(copy.deepcopy(board_stack[-1]))
            board_stack[-1].remove_options(cell)
            best_solution = board_stack[-1]
            index += 1
        else:
            board_stack.pop()
            index -= 1
    return [True if len(board_stack) else False, best_solution]


def guess(board):
    """
    Implements Deep First Search on the entire board.
    :param board: Puzzle board.
    :return: Best possible solution for the puzzle.
             True if complete, False if incomplete.
    """
    board_stack = [copy.deepcopy(board)]
    best_solution = board_stack[-1]

    # DFS Implementation.
    for r in range(grid_size):
        row = r
        while row <= r:
            for c in range(grid_size):
                col = c
                while col <= c or row < r:
                    if col > grid_size - 1:
                        col = 0
                        row += 1
                    cell = board_stack[-1].board[row][col]
                    if cell_set_option(cell, board_stack[-1]):
                        board_stack.append(copy.deepcopy(board_stack[-1]))
                        board_stack[-1].remove_options(cell)
                        best_solution = board_stack[-1]
                        col += 1
                        continue
                    col -= 1
                    if col < 0:
                        row -= 1
                        col = grid_size - 1
                    if row < 0 or not len(board_stack) > 0:
                        return [False, best_solution]
                    board_stack.pop()

            row += 1
    return [True, best_solution]


def solve(g_s, letter_set, t, b, l, r):
    """
    Function returns the solution to given puzzle.
    :param g_s: Grid Size.
    :param letter_set: Set of letters to be used.
    :param t: Top Constraints.
    :param b: Bottom Constraints.
    :param l: Left Constraints.
    :param r: Right Constraints.
    :return: Pandas Dataframe of solution.
    """
    global letter_options
    global grid_size
    global no_nan
    global top, bot, left, right
    grid_size = g_s
    letter_options = letter_options + letter_set
    no_nan = grid_size - len(letter_options)
    constraints = [t, b, l, r]
    top = constraints[0][::-1]
    bot = constraints[1][::-1]
    left = constraints[2][::-1]
    right = constraints[3][::-1]
    if grid_size < len(letter_set):
        raise ValueError("Grid size not proper. Size of the board must be "
                         "greater than the length of the letter set.")

    board = EndViewBoard()
    print(pd.DataFrame(board.board))
    print("Solving...")
    first_pass(board)
    # second_pass(board)
    print(pd.DataFrame(board.board))
    # exit()
    solved_board = guess_pythonic(board)

    if solved_board[0]:
        print(solved_board[1], "\n")
        return solved_board

    else:
        print("A solution could not be found.")
        print("The best case solution is:")
        print(solved_board[1], "\n")
        return solved_board
