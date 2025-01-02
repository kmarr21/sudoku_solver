#
# Utility functions for CSP Sudoku solver
#

# Prints pretty version of Sudoku board
# board = 9x9 sudoku board
def print_board(board):
    for i in range(len(board)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - -")
        for j in range(len(board[0])):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            if j == 8:
                print(board[i][j])
            else:
                print(str(board[i][j]) + " ", end="")

# checks if board is generally valid: 9x9 and all values within 0-9 range
def is_valid_board(board):
    # checks board size
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False
    
    # checks value range
    for row in board:
        if any(not isinstance(x, int) or x < 0 or x > 9 for x in row):
            return False
    
    return True

# tests to see if current board is a valid sudoku solution; returns True or False
def validate_solution(board):
    # check each row for validity
    for row in board:
        if not all(x in row for x in range(1, 10)):
            return False
    
    # check each column for validity
    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if not all(x in column for x in range(1, 10)):
            return False
    
    # check each 3x3 box for validity
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = []
            for i in range(3):
                for j in range(3): box.append(board[box_row + i][box_col + j])
            if not all(x in box for x in range(1, 10)):
                return False
    # if not false, return True
    return True

# creates a deep copy of the board (so that completely independent from the original)
def copy_board(board):
    return [row[:] for row in board]