import os

# loads puzzle from text files (either HARD or EASY puzzle)
def load_puzzle(filename):
    # get current path & puzzle path
    current_dir = os.path.dirname(__file__)
    puzzle_path = os.path.join(current_dir, filename)
    
    with open(puzzle_path, 'r') as file:
        # read text puzzle and convert to 2-dim list of integers so easier to process
        puzzle = []
        for line in file:
            row = [int(num) for num in line.strip().split()] # convert each line to list of integers
            puzzle.append(row)
    return puzzle

# return EASY puzzle
def get_easy_puzzle():
    return load_puzzle('easy_sudoku.txt')

# return HARD puzzle
def get_hard_puzzle():
    return load_puzzle('hard_sudoku.txt')

__all__ = ['get_easy_puzzle', 'get_hard_puzzle']