import pandas as pd
import numpy as np

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
        self.value_try = ""
        self.value_set = [np.nan, *list('IRAGE')]

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

    def verify(self, option):
        option = str(option)
        if len(option) == 1 or option == 'nan':
            return True
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

    def check_cell(self, cell):
        board_fix_values = self.board_current_state()
        (r, c) = (cell.row, cell.column)
        x = grid_size - len(letter_options)
        try_value = cell.value_try
        if try_value == 'nan':
            return True
        row = board_fix_values[r]
        column = board_fix_values[:, c]
        status = [True]

        print(row, column, sep="\n")
        print(self.bottom.constraints[c])
        if try_value in row or try_value in column:
            print("try value in row or column")
            status.append(False)

        if 0 <= r <= grid_size:
            if try_value == self.top.constraints[c]:
                print("try value == top.constraint")
                if r > 1:
                    status.append(False)
                if (board_fix_values[:, c][:r] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke upar not nan")
                    status.append(False)

            if try_value == self.bottom.constraints[c]:
                print("try value == bottom.constraint")
                if r < grid_size - 1:
                    status.append(False)
                if (board_fix_values[r + 1:][:, c] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke neeche not nan")
                    status.append(False)

        if 0 <= c <= grid_size:
            if try_value == self.left.constraints[r]:
                print("try value == left.constraint")
                if c > 1:
                    status.append(False)
                if (board_fix_values[r][:c] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke left mein not nan")
                    status.append(False)

            if try_value == self.right.constraints[r]:
                print("try value == right.constraint")
                if c > grid_size - 1:
                    status.append(False)
                if (board_fix_values[r][c+1:] == 'nan').all():
                    status.append(True)
                else:
                    print(try_value, "ke right mein not nan")
                    status.append(False)
            else:
                if self.right.constraints[r] in board_fix_values[r][:c]:
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

    for r in range(grid_size):
        for c in range(grid_size):
            cell = board.board[r][c]
            value = cell.value_set
            print(r, c, value)
            if len(value) == 1:
                cell.value = value[0]
                continue
            option = value.pop()
            while len(value) > 0:
                print("try value:", option)
                if cell.try_(option):
                    if board.check_cell(cell):
                        cell.set(option)
                        print("cell.set({}): True".format(option))
                        print("cell.value = ", cell.value, "\n")
                        break
                    else:
                        option = value.pop()
        print("--- row {} done.".format(r), "\n\n")

    print("\n\n")
    for rows in board.board_current_state():
        unique, counts = np.unique(rows, return_counts=True)
        print(unique, counts)

    print(board)
    # print(pd.DataFrame(board.board_values))

