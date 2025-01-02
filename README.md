# Sodoku-Solver Constraint Satisfaction Problem

## Introduction
This project implements a Sudoku puzzle solver using a Constraint Satisfaction Problem (CSP) approach. It can be applied to 2 different puzzles, an "easy" puzzle (easy_sudoku.txt) and a "hard" puzzle (hard_sudoku.txt) (you could also add your own puzzle to the "puzzles" folder and alter the solver to be able to run on this, if desired). Traditional Sudoku is a 9x9 puzzle grid of 3x3 regions or "boxes." Each region, row, and column contains 9 cells. The numbers shown in the initial un-solved easy and hard sudoku boards are fixed and cannot be changed — it is only the remaining empty spaces (signified by 0s) that will be filled in. The object of the puzzle is to place the numbers 1 to 9 in the emtpy cells so that each row, columns, and 3x3 region contains the same number only once. 

This program implements a smart Sudoku solver that uses various CSP techniques to efficiently find solutions. It allows users to choose between different solving strategies (i.e., toggle them on and off via flags) and compare their effectiveness (time taken to solve, if puzzle gets solved, etc.) on both easy and hard puzzles. The program features an interactive interface where users can select which puzzle to solve and which solving techniques to enable.

## Dependencies / Assumptions
- Python 3
- All puzzle inputs have to be valid 9x9 grids (though the program will also check for this)
- Empty cells are represented by 0s in the intial puzzle files
- No additional python packages outside standard ones are required

## How to Run

1. Ensure you have python 3 installed
2. Navigate to the correct directory in your terminal
2. Run the script: 
   ```
   python run.py
   ```
3. Follow the user prompts to select solving techniques to use (default is all of them), which puzzle to solve (easy or hard), and view results

## Code Structure

### Main Components
- **Backtracking with conflict-directed backjumping**: 
    - Base solver component 
    - More intelligent than simple backtracking which just backs up to the previous assignment
    - Keeps track of which variables caused each conflict using conflict sets
    - When failure is found, it can jump back multiple levels to the most recent variable that actually contributed to the failure
    - Example: If placing a 5 in cell (4,4) leads to a conflict in row 8, we can jump back to the last assignment we made in row 8, skipping any other assignments in between
    - Avoids wasting time exploring parts of the search space that won't fix the actual problem

### Added Optimization Techniques
- **MRV (Minimum Remaining Values)**:
    - Chooses which CELL to fill next by selecting the one with the fewest valid values in its domain (here, "domains" are, for any empty cell in the puzzle, the remaining set of valid values that could possibly go in that cell based on current constraints — this gets reduced as we make assignments to other cells and apply constraints)
    - I chose this over the degree heuristic because in Sudoku every empty cell has the same degree
    - MRV is effective since it focuses in on the most constrained cells

- **Forward checking**:
    - Immediately updates domains of related cells after each assignment
    - Catches failures early by checking if any cell runs out of valid options
    - Helps prevent running into dead ends

- **AC-3 (Arc Consistency)**:
    - This technique maintains "arc consistency" between pairs of variables
    - Arc consistency can be defined as follows: an arc, or edge (X→Y), is consistent if for every value in X's domain, there exists at least one value in Y's domain that satisfies the constraint between X and Y
    - In oher words: for each cell X, and each number that could go in X, there must be at least one legal number for each cell Y that doesn't conflict with X
    - Example: if cells X and Y are in the same row and X can only be {1,2}, then:
      * For value 1 in X: Y must have some value other than 1 available
      * For value 2 in X: Y must have some value other than 2 available
      * If either condition fails, that value can be removed from X's domain
    - This is often more effective than forward checking alone because forward checking only looks at direct conflicts, while AC-3 looks forward through the possible chain of conflicts in related cells and thus can identify problems earlier on

- **LCV (Least Constraining Value)**:
    - Chooses which VALUE to try first in a cell (I capitalize value here to emphasize how what LCV does is different than MRV)
    - Tries values that restrict other cells the *least*
    - Keeps options open in remaining empty cells

## Notes

- The solver is currently configured to use all optimization techniques by default — if you want to remove one and test the efficacy of the solver without it, you will have to do so through the interactive UI
- Program also measures and prints solving time so you can compare how quickly it worked with different optimization and/or on the easy vs. hard puzzle
