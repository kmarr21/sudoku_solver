#
# Run function for total algorithm: gets user input and calls main solver
#

import time
from sudoku_solver.solver import SudokuSolver
from sudoku_solver.puzzles import get_easy_puzzle, get_hard_puzzle
from sudoku_solver.utils import print_board

# Get user preferences for running code (i.e., decide what methods to use and not if user wants to customize and not use techniques recommended)
def get_user_preferences():
    print("\nBy default, all solving techniques are enabled for optimal performance.")
    print("Would you like to customize which techniques to use?")
    customize = input("Enter 'y' for custom configuration, any other key for all techniques: ").lower()
    
    if customize != 'y':
        return {'use_mrv': True, 'use_forward_checking': True, 'use_ac3': True, 'use_lcv': True}
    
    print("\nFor each technique, press Enter to enable or 'n' to disable:")
    
    mrv = input("\nUse MRV (Minimum Remaining Values)? \n"
                "This helps choose which cell to fill next by selecting the one with fewest possible values [Y/n]: ").lower() != 'n'
    
    fc = input("\nUse Forward Checking? \n"
               "This immediately removes invalid values from related cells after each assignment [Y/n]: ").lower() != 'n'
    
    ac3 = input("\nUse AC-3 (Arc Consistency)? \n"
                "This propagates constraints to reduce the search space [Y/n]: ").lower() != 'n'
    
    lcv = input("\nUse LCV (Least Constraining Value)? \n"
                "This helps choose which number to try first by selecting the one that restricts neighbors least [Y/n]: ").lower() != 'n'
    
    return {'use_mrv': mrv, 'use_forward_checking': fc, 'use_ac3': ac3, 'use_lcv': lcv}

# MAIN program function: provides introduction and faciliates user interface/options
def main():
    print("Welcome to the Sudoku Solver!")
    print("\nThis program solves Sudoku puzzles using Constraint Satisfaction Problem (CSP) techniques.")
    print("A Sudoku puzzle is solved when:")
    print("1. Each row contains all numbers from 1-9")
    print("2. Each column contains all numbers from 1-9")
    print("3. Each 3x3 box contains all numbers from 1-9")
    
    print("\nThe solver uses several techniques to efficiently find solutions:")
    print("- Conflict-Directed Backjumping: Intelligently backtracks to the source of failures")
    print("- MRV (Minimum Remaining Values): Chooses cells with fewest possible values")
    print("- Forward Checking: Immediately updates affected cells after each assignment")
    print("- AC-3 (Arc Consistency): Propagates constraints to reduce invalid choices")
    print("- LCV (Least Constraining Value): Tries values that restrict neighbors least")

    # get solving preferences (i.e., can turn off algorithmic enhancements like MRV, etc.)
    preferences = get_user_preferences()

    # load and display puzzles
    easy_puzzle = get_easy_puzzle()
    hard_puzzle = get_hard_puzzle()
    
    print("\nEasy Puzzle:")
    print_board(easy_puzzle)
    print("\nHard Puzzle:")
    print_board(hard_puzzle)
    
    # get user decision on which puzzle to solve
    while True:
        choice = input("\nWhich puzzle would you like to solve? (1 for Easy, 2 for Hard): ").strip()
        if choice in ['1', '2']: break
        print("Invalid choice. Please enter 1 or 2.")
    
    # select puzzle
    puzzle = easy_puzzle if choice == '1' else hard_puzzle
    puzzle_name = "Easy" if choice == '1' else "Hard"
    
    print(f"\nSolving {puzzle_name} puzzle with the following techniques:")
    for technique, enabled in preferences.items():
        print(f"- {technique[4:].upper()}: {'Enabled' if enabled else 'Disabled'}")
    
    # solve the puzzle
    solver = SudokuSolver(puzzle, **preferences)
    start_time = time.time()
    success = solver.solve()
    solve_time = time.time() - start_time
    
    # display the results and how the puzzle was solved + time needed to sovle
    print("\nResults:")
    if success:
        print(f"\nSolution found in {solve_time:.4f} seconds!")
        print("\nSolved puzzle:")
        print_board(puzzle)
    else:
        print("\nNo solution found!")
        print(f"Time spent attempting to solve: {solve_time:.4f} seconds")

if __name__ == "__main__":
    main()