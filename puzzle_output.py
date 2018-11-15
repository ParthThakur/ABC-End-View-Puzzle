import pandas as pd
from Solution import solve

puzzle_input = pd.read_csv("puzzle_2.csv", header=None)
puzzle_input.replace('X', 0, inplace=True)

print(puzzle_input, end="\n\n")
grid_size = int(puzzle_input[0][0])
letter_set = puzzle_input.T[1].dropna().tolist()


class Constraints:

    def __init__(self, constraints):
        self.constraints = constraints
        self.missing = list(set(letter_set) - set(constraints))
        self.blanks = self.blank_constraints(constraints)

    @staticmethod
    def blank_constraints(constraints):
        count = 0
        blank_index = []
        for element in constraints:
            if element == 'X':
                blank_index.append(count)
            count += 1
        return blank_index


top = Constraints(puzzle_input.T[2].tolist())
bottom = Constraints(puzzle_input.T[3].tolist())
left = Constraints(puzzle_input.T[4].tolist())
right = Constraints(puzzle_input.T[5].tolist())

solve(grid_size, letter_set, top, bottom, left, right)
