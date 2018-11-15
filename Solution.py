import pandas as pd
import numpy as np
import copy
import time

start = time.time()

letter_options = []
grid_size = 0


def load_board():

    d_board = []
    for i in range(grid_size):
        d_board.append([Cell(i, j) for j in range(grid_size)])

    df_board = np.array(d_board)
    return df_board


class Cell(object):
    """
    Cell object for individual cells on the board.
    """

    def __init__(self, row, column):
        self.row = row
        self.column = column

        self.value = str(np.nan)
        self.value_set = [np.nan, *letter_options]

    def set_options(self, letter):
        if self.check(letter):
            self.value_set += letter

    def set(self, option):
        self.value = option

    def check(self, l):
        if not type(l) == str:
            pass
        elif l:
            self.value_set = self.value_set[:1]

        if l not in self.value_set and len(self.value_set) < 2:
            return True
        return False

    @staticmethod
    def verify(option):
        option = str(option)
        if len(option) == 1 or option == 'nan':
            return True
        return False

    def __repr__(self):
        return str(self.value)

    def __add__(self, other):
        raise Exception("Don't try to add two cells.")


class EndViewBoard(object):
    """
    Board is the entire board for the game with a size of "grid_size".
    """

    def __init__(self, constraints):
        self.top, self.bottom, self.left, self.right = constraints
        self.no_nan = grid_size - len(letter_options)

        self.board = load_board()
        self.board = self.get_initial_state(self.board)
        self.board_values = self.board_values()

    def get_initial_state(self, board):
        top = self.top.constraints[::-1]
        bot = self.bottom.constraints[::-1]
        left = self.left.constraints[::-1]
        right = self.right.constraints[::-1]
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

    def all_cells(self):
        return ([(*index, value)
                for index, value in np.ndenumerate(self.board_values)])

    def check_cell(self, cell, letter):
        board_fix_values = self.board_current_state()
        (r, c) = (cell.row, cell.column)
        try_value = str(letter)
        row = np.delete(board_fix_values[r], c)
        column = np.delete(board_fix_values[:, c], r)

        if try_value == 'nan':
            if sum(row[:c] == 'nan') < self.no_nan:
                if sum(column[:r] == 'nan') < self.no_nan:
                    return True
            else:
                return False

        if try_value in row or try_value in column:
            return False

        if 0 <= r <= grid_size:
            if try_value == self.top.constraints[c]:
                if r > self.no_nan:
                    return False
                if not (board_fix_values[:, c][:r] == 'nan').all():
                    return False
            else:
                if self.top.constraints[c] != 0:
                    if set(column[:r]) == {'nan'}:
                        return False

            if try_value == self.bottom.constraints[c]:
                if r < grid_size - self.no_nan - 1:
                    return False
                if not (board_fix_values[r + 1:][:, c] == 'nan').all():
                    return False
            else:
                if self.bottom.constraints[c] in column.tolist():
                    return False

        if 0 <= c <= grid_size:
            if try_value == self.left.constraints[r]:
                if c > self.no_nan:
                    return False
                if not (board_fix_values[r][:c] == 'nan').all():
                    return False
            else:
                if self.left.constraints[r] != 0:
                    if set(row[:c]) == {'nan'}:
                        return False

            if try_value == self.right.constraints[r]:
                if c < grid_size - 1 - self.no_nan:
                    return False
                if not (board_fix_values[r][c+1:] == 'nan').all():
                    return False
            else:
                if self.right.constraints[r] in row.tolist():
                    return False
        return True

    def board_values(self):
        value_board = []
        for rows in self.board:
            value_board.append([cell.value_set for cell in rows])
        return np.array(value_board)

    def board_current_state(self):
        set_values = []
        for rows in self.board:
            set_values.append([cell.value for cell in rows])
        return np.array(set_values)

    def __repr__(self):
        return "EndViewBoard({}, {}, {}, {})".format(grid_size,
                                                     self.top,
                                                     self.bottom,
                                                     self.left,
                                                     self.right)

    def __str__(self):
        return pd.DataFrame(self.board_current_state()).to_string()


def cell_set_option(cell, board):
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
    board_stack = [copy.deepcopy(board)]
    best_solution = board_stack[-1]
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
                        board_stack.pop()
                        if row < 0:
                            return [False,
                                    pd.DataFrame(best_solution.board_current_state())]
                row += 1
        return [True,
                pd.DataFrame(best_solution.board_current_state())]


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

    print("Solving...")
    solved_board = guess(board)

    print("Solved in", time.time() - start, "seconds.")
    if solved_board[0]:
        print(solved_board[1], "\n")
        return solved_board

    else:
        print("A solution could not be found.")
        print("The best case solution is:")
        print(solved_board[1], "\n")
        return solved_board

