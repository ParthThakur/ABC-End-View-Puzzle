from time import time
import Board


def solve(constraints, grid_size, letter_options=None):
    start = time()
    board = Board.Board(grid_size)
    board.set_initial_state(constraints, letter_options)
    print(board)
    Board.Cell.return_value_set = False
    print(board)
    print(time() - start)
