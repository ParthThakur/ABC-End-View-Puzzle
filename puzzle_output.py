import pandas as pd
import numpy as np

puzzle_input = pd.read_csv("puzzle_input.csv", header=None)
puzzle_input.replace('X', 0, inplace=True)

print(puzzle_input, end="\n\n")
grid_size = int(puzzle_input[0][0])
letter_set = puzzle_input.T[1].dropna().tolist()
