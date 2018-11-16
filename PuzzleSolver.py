"""
An ABC End View puzzle solver using Deep First Search.
"""
__author__ = "Parth Thakur"
__email__ = "parththakur@gmail.com"

import pandas as pd
from DFS import solve


puzzle_no = "12"

puzzle_input = pd.read_csv("test puzzles/puzzle_"+puzzle_no+".csv", header=None)
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
    name = "puzzle_output_"
else:
    name = "puzzle_output_(bestCase)_"

output_path = "test_output\\"+name+puzzle_no+".csv"

df = pd.DataFrame(solution[1].board_current_state())
df.replace(' ', 'X').to_csv(output_path, header=False, index=False)

print("The solution was saved in", output_path)
