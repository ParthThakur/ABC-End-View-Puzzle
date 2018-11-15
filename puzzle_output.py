import pandas as pd
from Solution import solve

puzzle_input = pd.read_csv("puzzle_input.csv", header=None)
puzzle_input.replace('X', 0, inplace=True)

print(puzzle_input, end="\n\n")
grid_size = int(puzzle_input[0][0])
letter_set = puzzle_input.T[1].dropna().tolist()

top = puzzle_input.T[2].tolist()
bottom = puzzle_input.T[3].tolist()
left = puzzle_input.T[4].tolist()
right = puzzle_input.T[5].tolist()

solution = solve(grid_size, letter_set, top, bottom, left, right)

if solution[0]:
    name = "puzzle_output.csv"
else:
    name = "puzzle_output_(bestCase).csv"

solution[1].fillna('X').to_csv(name, index=False)
