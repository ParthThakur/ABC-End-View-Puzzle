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


def sides(array):
    x, y = array.shape
    corners_ = [(0, 0), (x-1, y-1), (0, x-1), (y-1,0)]
    iter1 = array[0].flat
    iter2 = array[:, 0].flat
    iter3 = array[-1].flat
    iter4 = array[:, -1].flat

    for iter_ in [iter1, iter2, iter3, iter4]:
        for value in iter_:
            if value.position in corners_:
                continue
            yield value


def remnants(array):
    for cell in array.flat:
        if cell.isnan_valueset:
            yield cell


class Board:
    letter_options = set()
    num_blank = None
    grid_size = None
    board = None

    top = None
    bot = None
    left = None
    right = None

    def __init__(self, grid_size: int):
        Board.grid_size = grid_size - 1
        temp = []
        for row in range(grid_size):
            temp.append([Cell(row, column) for column in range(grid_size)])
        Board.board = np.array(temp)

    def __repr__(self):
        return pd.DataFrame(self.board).to_string()

    def __iter__(self):
        return self.board.flat

    @classmethod
    def freeze_cells(cls):
        for cell in cls.board.flat:
            cell.freeze_values()

    @classmethod
    def add_nan(cls):
        corner_cells = list(corners(cls.board))
        for cell in cls.board.flat:
            cell.value_set = set(cell.value_set)
            if cell not in corner_cells:
                cell.value_set |= {' '}

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

        cls.top, cls.bot, cls.left, cls.right = top_constraints, bot_constraints, left_constraints, right_constraints

        top_bot = [top_constraints, bot_constraints]
        left_right = [left_constraints, right_constraints]

        for cell in corners(cls.board):
            row, column = cell.position
            constraint_1 = top_bot[0 if row == 0 else 1]
            constraint_2 = left_right[0 if column == 0 else 1]

            close_1 = constraint_1[column]
            close_2 = constraint_2[row]

            far_1 = constraint_1[cls.grid_size if row == 0 else 0]
            far_2 = constraint_2[cls.grid_size if column == 0 else 0]

            if close_1 == close_2:
                cell.value_set = {close_1}
            else:
                if [str(close_1), str(close_2)] == ['nan', 'nan']:
                    cell.value_set = {' ', *[x for x in cls.letter_options if x not in [far_1, far_2]]}
                elif str(close_1) == 'nan' or str(close_2) == 'nan':
                    cell.value_set = {str(close_1), str(close_2), ' '}
                else:
                    cell.value_set = {' '}

            if [str(close_1), str(close_2)] == ['nan', 'nan']:
                cell.value_set = {' ', *[x for x in cls.letter_options if x not in [far_1, far_2]]}

            cell.freeze_values()

        for cell in sides(cls.board):
            row, column = cell.position
            if row == 0:
                cell.value_set = {top_constraints[column]}
            elif row == cls.grid_size:
                cell.value_set = {bot_constraints[column]}
            elif column == 0:
                cell.value_set = {left_constraints[row]}
            elif column == cls.grid_size:
                cell.value_set = {right_constraints[row]}

            if not cell.isnan_valueset:
                cell.freeze_values()

        for cell in centre(cls.board, cls.num_blank):
            row, column = cell.position
            constraints = [top_constraints[column], bot_constraints[column],
                           left_constraints[row], right_constraints[row]]
            for option in cls.letter_options:
                if option not in constraints:
                    cell.value_set.add(option)
            cell.freeze_values()

        for cell in remnants(cls.board):
            row, column = cell.position
            try:
                constraint_1 = top_bot[0 if row > cls.num_blank else 1]
                constraint_2 = left_right[0 if column > cls.num_blank else 1]

                far_1 = constraint_1[column]
                far_2 = constraint_2[row]

                cell.value_set = {*[x for x in cls.letter_options if x not in [far_1, far_2]]}

            except AttributeError:
                continue

        cls.add_nan()


class Cell:
    return_value_set = True

    def __init__(self, row, column):
        self.value = None
        self.value_set = set()
        self.position = (row, column)

    def freeze_values(self):
        self.value_set = frozenset([x for x in self.value_set if str(x) != 'nan'])

    def remove_options(self, option):
        try:
            self.value_set.remove(option)
        except KeyError:
            pass

    @property
    def isnan_valueset(self):
        check = [x for x in self.value_set if str(x) != 'nan']
        return not bool(check) and type(self.value_set) != frozenset

    @property
    def isnan(self):
        return str(self.value) in ['nan', ' ', '']

    def __repr__(self):
        if self.return_value_set:
            return str(self.value_set)
        return str(self.value)
