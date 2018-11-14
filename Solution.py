import pandas as pd
import numpy as np
import copy
import time

start = time.time()

pd.set_option('display.max_columns', 500)

letter_options = ['X']
grid_size = 0


def load_board():

    d_board = []
    for i in range(grid_size):
        d_board.append([Cell(i, j) for j in range(grid_size)])

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

        self.value = str(np.nan)
        self.value_set = [np.nan, *list('IRAGE')]

    def set_options(self, letter):
        if self.check(letter):
            self.value_set += letter

    def set(self, option):
        print("cell.value =", option)
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
        # x = grid_size - len(letter_options)
        try_value = str(letter)
        row = np.delete(board_fix_values[r], c)
        column = np.delete(board_fix_values[:, c], r)
        status = [True]

        if try_value == 'nan':
            print("try value is nan")
            if sum(row[:c] == 'nan') < 2:
                print("less than two nan in row")
                if sum(column[:r] == 'nan') < 2:
                    print("less than 2 nan in column")
                    return True
            else:
                print("already two nan in row or column.")
                return False

        print(row, column, sep="\n")
        if try_value in row or try_value in column:
            print("try value in row or column")
            status.append(False)

        if 0 <= r <= grid_size:
            if try_value == self.top.constraints[c]:
                print("try value == top.constraint")
                if r > 2:
                    status.append(False)
                if (board_fix_values[:, c][:r] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke upar not nan")
                    status.append(False)
            else:
                if self.top.constraints[c] != 0:
                    if set(column[:r]) == {'nan'}:
                        print("try value != top constraint and nan on top")
                        status.append(False)

            if try_value == self.bottom.constraints[c]:
                print("try value == bottom.constraint")
                if r < grid_size - 2:
                    print(r, "<", grid_size-1)
                    status.append(False)
                if (board_fix_values[r + 1:][:, c] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke neeche not nan")
                    status.append(False)

        if 0 <= c <= grid_size:
            if try_value == self.left.constraints[r]:
                print("try value == left.constraint")
                if c > 2:
                    status.append(False)
                if (board_fix_values[r][:c] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke left mein not nan")
                    status.append(False)
            else:
                if self.left.constraints[c] != 0:
                    if set(row[:c]) == {'nan'}:
                        print("try value != left constraint an no nan on left")
                        status.append(False)

            if try_value == self.right.constraints[r]:
                print("try value == right.constraint")
                if c < grid_size - 3:
                    print(c, "<", grid_size-3)
                    status.append(False)
                if (board_fix_values[r][c+1:] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke right mein not nan")
                    status.append(False)

        print("board.check_cell({}): {}".format(try_value,
                                                np.array(status).all()))
        return np.array(status).all()

    def check_row(self, r):
        row = self.board_current_state()[r]
        unique, counts = np.unique(row, return_counts=True)
        frequency = dict(zip(unique, counts))
        if frequency['nan'] != 2:
            print("Nan in row not equal to 2.")
            return False
        if len(unique) < len(letter_options):
            print("All letters not present in row.")
            return False
        if not sum(counts[:-1]) == len(counts[:-1]):
            print("Duplicate letters present in row.")
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
        disp_board = []
        for rows in self.board:
            disp_board.append([cell.value for cell in rows])
        return pd.DataFrame(disp_board).to_string()


def cell_set_option(cell, board):
    value = cell.value_set
    try:
        letter = value.pop()
    except IndexError:
        return False
    print("try value:", letter)
    if board.check_cell(cell, letter):
        cell.set(letter)
        print()
        return True
    else:
        if len(value) > 0:
            return cell_set_option(cell, board)


def guess(board):
    board_stack = [copy.deepcopy(board)]
    while len(board_stack) > 0:
        for r in range(grid_size):
            row = r
            while row <= r:
                for c in range(grid_size):
                    col = c
                    while col <= c:
                        cell = board_stack[-1].board[row][col]
                        print(row, col, cell.value_set)
                        if cell_set_option(cell, board_stack[-1]):
                            board_stack.append(copy.deepcopy(board_stack[-1]))
                            col += 1
                            continue
                        else:
                            print("\nPopping off a stack board.")
                            col -= 1
                            if col < 0:
                                row -= 1
                                col = grid_size - 1
                            board_stack.pop()
                row += 1
            print([x for x in board_stack[-1].board[r]])
            print("--- row {} done.".format(r), "\n\n")

        return [True, board_stack.pop()]
    return [False, board_stack.pop()]


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
    print(pd.DataFrame(board.board_values))

    solved_board = guess(board)

    print("\n\n")
    if solved_board[0]:
        for rows in solved_board[1].board_current_state():
            unique, counts = np.unique(rows, return_counts=True)
            print(unique, counts)
        print(solved_board[1], "\n\n")

    else:
        print("A solution could not be found.")

    print("finished in", time.time() - start, "seconds")
    y = 0
    # for x in board_stack:
    #     y += 1
    #     print("Stack", y)
    #     print(x)
    #     print("--------")
    # print(pd.DataFrame(board.board_values))
