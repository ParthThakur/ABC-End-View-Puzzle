import numpy as np
import pandas as pd
import time


def corner_pos(x, y):
    return [(0, 0), (x - 1, y - 1), (0, x - 1), (y - 1, 0)]


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
    iter1 = array[0].flat
    iter2 = array[:, 0].flat
    iter3 = array[-1].flat
    iter4 = array[:, -1].flat

    for iter_ in [iter1, iter2, iter3, iter4]:
        for value in iter_:
            if value.position in corner_pos(x, y):
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
        for cell in cls.board.flat:
            cell.value_set = set(cell.value_set)
            if cell.position not in corner_pos(*cls.board.shape):
                cell.value_set |= {' '}
            cell.fixed_set = True
            cell.value_set = set(cell.value_set)

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

            constraint_1 = top_bot[1 if row == 0 else 0]
            constraint_2 = left_right[1 if column == 0 else 0]
            far_1 = constraint_1[column]
            far_2 = constraint_2[row]

            if close_1 == close_2:
                cell.value = close_1
                cell.value_fixed = True
            else:
                if [str(close_1), str(close_2)] == ['nan', 'nan']:
                    cell.value_set = {' ', *cls.letter_options}
                elif str(close_1) == 'nan' or str(close_2) == 'nan':
                    cell.value_set = {str(close_1), str(close_2), ' '}
                else:
                    cell.value = ' '
                    cell.value_fixed = True
            cell.value_set = {x for x in cell.value_set if x not in [far_1, far_2]}

            # if [str(close_1), str(close_2)] == ['nan', 'nan']:
            #     cell.value_set = {' ', *[x for x in cls.letter_options if x not in [far_1, far_2]]}

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
                if (all([row == cls.grid_size / 2, column == cls.grid_size / 2]) and
                   all([row == cls.num_blank, column == cls.num_blank])):
                    value_set = cls.letter_options
                else:
                    constraint_1 = top_bot[0 if row > cls.num_blank else 1]
                    constraint_2 = left_right[0 if column > cls.num_blank else 1]

                    far_1 = constraint_1[column]
                    far_2 = constraint_2[row]

                    value_set = [x for x in cls.letter_options if x not in [far_1, far_2]]
            except AttributeError:
                continue
            cell.value_set = {*value_set}

        cls.add_nan()
        cls.second_pass()

    @classmethod
    def check_blanks(cls, position):
        row_value = [cell.value for cell in cls.board[position[0]]]
        column_value = [cell.value for cell in cls.board[:, position[1]]]
        if row_value.count(' ') == cls.num_blank:
            # print(f'{position[0]} row has {cls.num_blank} blanks.')
            for cell in cls.board[position[0]]:
                yield cell
        if column_value.count(' ') == cls.num_blank:
            # print(f'{position[1]} column has {cls.num_blank} blanks.')
            for cell in cls.board[:, position[1]]:
                yield cell

    @classmethod
    def second_pass(cls):
        print(pd.DataFrame(cls.board).to_string())
        previous = np.copy([0])
        new = np.array([1])
        count = 0
        while not np.array_equal(previous, new):
            count += 1
            previous = np.copy(new)
            for cell in cls.board.flat:
                row, column = cell.position
                if cell.value_fixed:
                    if cell.value != ' ':
                        # time.sleep(.5)
                        # print(cell.position, ': fixed.')
                        for ce in cls.board[row]:
                            try:
                                tmp = ce.value_set
                                tmp.remove(cell.value)
                                # time.sleep(.5)
                                # print(f'\tremove {cell.value} from {ce.position}')
                                cell.pass_ = True
                                ce.value_set = tmp
                            except KeyError:
                                pass
                        for ce in cls.board[:, column]:
                            try:
                                tmp = ce.value_set
                                tmp.remove(cell.value)
                                # time.sleep(.5)
                                # print(f'\tremove {cell.value} from {ce.position}')
                                ce.value_set = tmp
                            except KeyError:
                                pass
                # if len(cell.value_set) == 1:
                #     time.sleep(.5)
                #     print(f'{cell.position} valueset contains one element.')
                #     cell.value = cell.value_set.pop()
                #     cell.value_fixed = True
                for ce in cls.check_blanks(cell.position):
                    try:
                        # time.sleep(.5)
                        # print(f'\tremove from {ce.position}')
                        tmp = ce.value_set
                        tmp.remove(' ')
                        ce.value_set = tmp
                    except KeyError:
                        pass
                # print(f'Done removing blank from {cell.position}')
            new = cls.board
            # time.sleep(.5)
            # print(previous == new, previous, new, '\n\n', sep='\n')
            # time.sleep(.5)
            # print(count)
            # print(f'id of previous: {id(previous)}. \nid of new: {id(new)}.'
            #       f'\n\t previous.id == new.id: {id(previous) == id(new)}.'
            #       f'\n\t previous == new: {np.array_equal(previous, new)}')


class Cell:
    return_value_set = True

    def __init__(self, row: int, column: int):
        self.position = (row, column)
        self.value_fixed = False
        self.fixed_set = False
        self.value = None
        self.value_set = set()

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

    def __setattr__(self, key, value, override=False):
        if key == 'value' and self.value_fixed or override:
            raise AttributeError(f'Value of the cell has been fixed and cannot be changed.'
                                 f'\nCell at position: {self.position}')
        elif key == 'value_set' and self.fixed_set:
            self.__dict__['value_set'] = value
            # print(f'\t\t{self.position} valueset: {value}')
            if len(self.__dict__['value_set']) == 1:
                # time.sleep(0.5)
                # print(f'\t\t {self.position} valueset has one element.')
                self.__dict__['value'] = self.value_set.pop()
                self.__dict__['value_fixed'] = True
        else:
            self.__dict__[key] = value

    def __eq__(self, other):
        return str(self.value) == str(other.value)

    def __ne__(self, other):
        return not self.__eq__(other)
