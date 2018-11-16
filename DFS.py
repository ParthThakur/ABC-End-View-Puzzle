"""
Implements the DFS algorithm on given puzzle.
' ' (<space>) implies an empty cell, which is also 'X' in most representations
of this puzzle.
"""

import pandas as pd
import numpy as np
import copy
from time import time

start = time()

letter_options = []
grid_size = 0


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

    def set_options(self, letter):
        """
        Set value options for cell.
        :param letter: List of options.
        :return: None
        """
        if self.check(letter):
            self.value_set += letter

    def set(self, option):
        """
        Set the value of cell.
        :param option: Value to be set.
        :return: None
        """
        self.value = option

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

    def __init__(self, constraints):
        """
        Initialize Board of the puzzle.
        :param constraints: List of all constraints.
        """
        self.top, self.bottom, self.left, self.right = constraints
        self.no_nan = grid_size - len(letter_options)

        self.board = load_board()
        self.board = self.get_initial_state(self.board)

    def get_initial_state(self, board):
        """
        Set values options of cells based on constraints.
        :param board: NumPy array of cells on the board.
        :return: NumPy array with initial values set.
        """
        top = self.top[::-1]
        bot = self.bottom[::-1]
        left = self.left[::-1]
        right = self.right[::-1]
        for cell in board[0]:
            x = top.pop()
            cell.set_options(x) if x else None
        for cell in board[grid_size - 1]:
            x = bot.pop()
            cell.set_options(x) if x else None
        for cell in board[:, 0]:
            x = left.pop()
            cell.set_options(x) if x else None
        for cell in board[:, grid_size - 1]:
            x = right.pop()
            cell.set_options(x) if x else None
        return board

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
            if sum(row[:c] == ' ') < self.no_nan:
                if sum(column[:r] == ' ') < self.no_nan:
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
            if try_value == self.top[c]:
                if r > self.no_nan:
                    return False
                if not (board_fix_values[:, c][:r] == ' ').all():
                    return False
            else:
                if self.top[c] != 0:
                    if set(column[:r]) == {' '}:
                        return False

            # If option is equal to bottom constraint, return true only if ' '
            # below cell.
            # Also check if row index is permissible. i.e Cell is not too far
            # up, making other cells in row invalid.
            if try_value == self.bottom[c]:
                if r < grid_size - self.no_nan - 1:
                    return False
                if not (board_fix_values[r + 1:][:, c] == ' ').all():
                    return False
            else:
                if self.bottom[c] in column.tolist():
                    return False

        # Check entire Column
        if 0 <= c <= grid_size:

            # If option is equal to left constraint, return true only if ' '
            # on left of the cell.
            # Also check if column index is permissible. i.e Cell is not too far
            # right, making other cells in row invalid.
            if try_value == self.left[r]:
                if c > self.no_nan:
                    return False
                if not (board_fix_values[r][:c] == ' ').all():
                    return False
            else:
                if self.left[r] != 0:
                    if set(row[:c]) == {' '}:
                        return False

            # If option is equal to right constraint, return true only if ' '
            # on right of the cell.
            # Also check if column index is permissible. i.e Cell is not too far
            # left, making other cells in row invalid.
            if try_value == self.right[r]:
                if c < grid_size - 1 - self.no_nan:
                    return False
                if not (board_fix_values[r][c+1:] == ' ').all():
                    return False
            else:
                if self.right[r] in row.tolist():
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

    def __repr__(self):
        return pd.DataFrame(self.board_current_state()).to_string()


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
        letter = value.pop(0)
    except IndexError:
        return False
    if board.check_cell(cell, letter):
        cell.set(letter)
        return True
    else:
        if len(value) > 0:
            return cell_set_option(cell, board)


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
    while len(board_stack) > 0:
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
    grid_size = g_s
    constraints = [t, b, l, r]
    if grid_size < len(letter_set):
        raise Exception("Grid size not proper. Size of the board must be "
                        "greater than the length of the letter set.")

    letter_options = letter_options + letter_set
    board = EndViewBoard(constraints)

    print("Solving...")
    solved_board = guess(board)

    print("Solved in", time() - start, "seconds.")
    if solved_board[0]:
        print(solved_board[1], "\n")
        return solved_board

    else:
        print("A solution could not be found.")
        print("The best case solution is:")
        print(solved_board[1], "\n")
        return solved_board
