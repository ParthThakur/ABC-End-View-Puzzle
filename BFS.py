from time import time
from Board import Board


def solve(constraints, grid_size, letter_options=None):
    start = time()
    board = Board(grid_size)
    board.set_initial_state(constraints, letter_options)
    print(board)
    print(time() - start)
