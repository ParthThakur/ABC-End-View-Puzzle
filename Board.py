import numpy as np
import pandas as pd


def centre(array, num_blanks):
    x, y = array.shape
    stop = max(0, num_blanks+1)
    for value in array[stop:x - stop, stop:y - stop].flat:
        yield value


def corners(array):
    for value in (array[::array.shape[0]-1, ::array.shape[1]-1]).flat:
        yield value


def sides(array, num_blanks):
    x, y = array.shape
    stop = max(0, num_blanks)
    iter1 = array[:stop].flat
    iter2 = array[x - stop:x].flat
    iter3 = array[:, :stop].flat
    iter4 = array[:, x - stop:x].flat

    for iter_ in [iter1, iter2, iter3, iter4]:
        for value in iter_:
            yield value


class Board:
    letter_options = set()
    num_blank = None
    grid_size = None
    board = None

    def __init__(self, grid_size: int):
        Board.grid_size = grid_size - 1
        temp = []
        for row in range(grid_size):
            temp.append([Cell(row, column) for column in range(grid_size)])
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
        print(f'Grid size: {cls.grid_size} \nNum Blanks: {cls.num_blank} \nLetter Set: {cls.letter_options}')

        top_constraints = initial_states['top']
        bot_constraints = initial_states['bottom']
        left_constraints = initial_states['left']
        right_constraints = initial_states['right']

        top_bot = [top_constraints, bot_constraints]
        left_right = [left_constraints, right_constraints]

        for cell in corners(cls.board):
            row, column = cell.position
            c_1 = top_bot[0 if column == 0 else 1][0 if row == 0 else cls.grid_size]
            c_2 = left_right[0 if row == 0 else 1][0 if column == 0 else cls.grid_size]

            if c_1 == c_2:
                cell.value_set = {c_1}
            else:
                if [str(c_1), str(c_2)] == ['nan', 'nan']:
                    cell.value_set = {np.nan, *cls.letter_options}
                else:
                    cell.value_set = {c_2, c_1}

            cell.freeze_values()

        for cell in sides(cls.board, cls.num_blank):
            row, column = cell.position
            try:
                if row <= cls.num_blank:
                    cell.value_set.add(top_constraints[column])
                elif row >= cls.grid_size - cls.num_blank:
                    cell.value_set.add(bot_constraints[column])

                if column <= cls.num_blank:
                    cell.value_set.add(left_constraints[row])
                elif column >= cls.grid_size - cls.num_blank:
                    cell.value_set.add(right_constraints[row])
            except AttributeError:
                continue

            if cell.isnan:
                cell.value_set.update(cls.letter_options)
            cell.value_set.add(np.nan)

        for cell in centre(cls.board, cls.num_blank):
            row, column = cell.position
            constraints = [top_constraints[column], bot_constraints[column],
                           left_constraints[row], right_constraints[row]]
            for option in cls.letter_options:
                cell.value_set.add(option if option not in constraints else np.nan)
            cell.value_set.add(np.nan)

        cls.freeze_cells()


class Cell:

    def __init__(self, row, column):
        self.value = None
        self.value_set = set()
        self.position = (row, column)

    def freeze_values(self):
        self.value_set = frozenset(self.value_set)
        # self.value_set.discard(np.nan)

    @property
    def isnan(self):
        check = [x for x in self.value_set if str(x) != 'nan']
        return not bool(check)

    def __repr__(self):
        return str(list(self.value_set))
