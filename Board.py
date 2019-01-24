import numpy as np
import pandas as pd


def iscorner(row, column, g_size):
    return any([all([row == 0, column == 0]),
                all([row == g_size, column == g_size]),
                all([row == 0, column == g_size]),
                all([row == g_size, column == 0])])


def central_array(array, num_blanks):
    x, y = array.shape
    for index, value in np.ndenumerate(array[num_blanks:x - num_blanks, num_blanks:y-num_blanks]):
        yield index, value


def corners(array):
    for index, value in np.ndenumerate(array[::array.shape[0]-1, ::array.shape[1]-1]):
        yield index, value


def sides(array, num_blank):
    x, y = array.shape
    iter1 = np.ndenumerate(array[[*list(range(num_blank+1)), *list(range(x-num_blank-1, x))]])
    iter2 = np.ndenumerate(array[:, [*list(range(num_blank)), *list(range(x - num_blank-1, x))]])
    for iter_ in [iter1, iter2]:
        for index, value in iter_:
            if iscorner(*index, x):
                continue
            else:
                yield index, value


class Board:
    letter_options = set()
    num_blank = None
    grid_size = None
    board = None

    def __init__(self, grid_size: int):
        Board.grid_size = grid_size - 1
        temp = []
        for _ in range(grid_size):
            temp.append([Cell() for _ in range(grid_size)])
        Board.board = np.array(temp)

    def __repr__(self):
        return pd.DataFrame(self.board).to_string()

    @classmethod
    def freeze_cells(cls):
        for cell in cls.board.flat:
            cell.freeze_values()

    @classmethod
    def set_initial_state(cls, initial_states, letter_set=None):
        """
        Use constraints and remove impossible values from board.
        :param dict of str, list initial_states: Constraints for the board.
        :param list or set letter_set: Set of letters or number to solve the board.
        :return: None
        """
        if letter_set is None:
            for pos, constraints in initial_states.items():
                cls.letter_options |= set(constraints)
            cls.letter_options = frozenset(cls.letter_options)

        else:
            cls.letter_options = frozenset(letter_set)

        cls.num_blank = cls.grid_size + 1 - len(cls.letter_options)

        top_constraint = initial_states['top']
        bot_constraints = initial_states['bottom']
        left_constraints = initial_states['left']
        right_constraints = initial_states['right']

        top_bot = [top_constraint, bot_constraints]
        left_right = [left_constraints, right_constraints]

        for (row, column), cell in corners(cls.board):
            c_1 = top_bot[0 if column == 0 else 1][0 if row == 0 else cls.grid_size]
            c_2 = left_right[0 if row == 0 else 1][0 if column == 0 else cls.grid_size]

            if c_1 == c_2:
                cell.value_set = {c_1}
            else:
                cell.value_set = {c_2, c_1}
            print(row, column, c_1, c_2)

        for (row, column), cell in sides(cls.board, cls.num_blank):
            if row <= cls.num_blank:
                cell.value_set.add(top_constraint[column])
            elif row >= cls.grid_size - cls.num_blank:
                cell.value_set.add(bot_constraints[column])

            if column <= cls.num_blank:
                cell.value_set.add(left_constraints[row])
            elif column >= cls.grid_size - cls.num_blank:
                cell.value_set.add(right_constraints[row])
        cls.freeze_cells()


class Cell:

    def __init__(self):
        self.value = None
        self.value_set = set()

    def freeze_values(self):
        self.value_set.discard(np.nan)

    def __repr__(self):
        return str(self.value_set)
