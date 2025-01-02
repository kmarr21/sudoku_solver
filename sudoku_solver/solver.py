#
# Main solver of sudoku boards, using various CSP techniques
# Implements: conflict-directed backjumping, forward checking, AC3, LCV, and MRV
#

from collections import deque
import time
import copy
from .utils import validate_solution, is_valid_board

# main solver class: initialize the sudoku solver for board
class SudokuSolver:
    def __init__(self, board, use_mrv=True, use_forward_checking=True, use_ac3=True, use_lcv=True):
        if not is_valid_board(board):
            raise ValueError("Invalid Sudoku board")
            
        self.board = board
        self.size = 9
        self.box_size = 3
        self.empty = 0
        
        # set solving flags (user has opportunity to turn these off, but they are defaulted ON)
        self.use_mrv = use_mrv
        self.use_forward_checking = use_forward_checking
        self.use_ac3 = use_ac3
        self.use_lcv = use_lcv
        
        # initialize domains and conflict set tracking 
        self.domains = self.initialize_domains()
        self.conflict_sets = {}
        self.assignment_order = []

    # initialize domain for all empty cells: this is [1-9] to start, all viable values a sudoku blank space can take
    def initialize_domains(self):
        domains = {}
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == self.empty:
                    domains[(i, j)] = set(range(1, 10))
                    self.update_domain((i, j), domains)
        return domains

    # update domain of a board position based on the current state (set of valid values an empty square can take: starts as [1-9])
    #   removes values that would violate Sudoku rules
    def update_domain(self, pos, domains):
        if pos not in domains: return
        row, col = pos
        # remove values seen in row
        for j in range(self.size):
            if self.board[row][j] != self.empty:
                domains[pos].discard(self.board[row][j])
                
        # remove values seen in column
        for i in range(self.size):
            if self.board[i][col] != self.empty:
                domains[pos].discard(self.board[i][col])
                
        # remove values seen in 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] != self.empty:
                    domains[pos].discard(self.board[i][j])

    # main solving method using extra techniques; returns TRUE if solution is found, FALSE otherwise
    def solve(self):
        # AC-3 if enabled
        if self.use_ac3:
            initial_conflicts = self.ac3_with_conflicts()
            if initial_conflicts is not None: return False
        
        # primary solving algorithm with conflict-directed backjumping
        success, _ = self.backtrack_with_conflicts()
        return success

    # conflict-direted backjumping function; returns success (T or F) and conflict set
    def backtrack_with_conflicts(self, depth=0):
        var = self.get_next_variable()
        if var is None:  # solution found
            return True, set()

        row, col = var
        current_conflicts = set()
        
        for value in self.get_ordered_values(var):
            if self.is_safe(var, value):
                # save state for backtracking
                old_domains = copy.deepcopy(self.domains)
                old_conflicts = copy.deepcopy(self.conflict_sets)
                
                # make assignment to blank spot
                self.board[row][col] = value
                self.assignment_order.append(var)
                del self.domains[var]

                # forward checking
                if self.use_forward_checking:
                    fc_conflicts = self.forward_check_with_conflicts(var, value)
                    if fc_conflicts is not None:
                        current_conflicts.update(fc_conflicts - {var})
                        self.restore_state(var, old_domains, old_conflicts)
                        continue

                # AC-3
                if self.use_ac3:
                    ac3_conflicts = self.ac3_with_conflicts()
                    if ac3_conflicts is not None:
                        current_conflicts.update(ac3_conflicts - {var})
                        self.restore_state(var, old_domains, old_conflicts)
                        continue

                # recursive call
                success, new_conflicts = self.backtrack_with_conflicts(depth + 1)
                if success: return True, set()

                # update conflicts and backjump
                current_conflicts.update(new_conflicts - {var})
                self.restore_state(var, old_domains, old_conflicts)

        # store conflicts for this variable
        self.conflict_sets[var] = current_conflicts
        return False, current_conflicts

    # restore solver state during backtracking (undoes a move when it doesn't work out)
    def restore_state(self, var, old_domains, old_conflicts):
        self.board[var[0]][var[1]] = self.empty
        self.domains = old_domains
        self.conflict_sets = old_conflicts
        self.assignment_order.pop()

    # gets next variable if MRV is enabled
    def get_next_variable(self):
        if not self.use_mrv:
            return self.get_first_empty()
        return self.get_mrv_variable()

    # gets first empty cell in the board
    def get_first_empty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == self.empty: return (i, j)
        return None

    # implements MRV (Minimum Remaining Values heuristic)
    #   decides WHICH cell is best to choose next
    def get_mrv_variable(self):
        min_length = float('inf')
        min_var = None
        for var in self.domains:
            domain_length = len(self.domains[var])
            if domain_length < min_length:
                min_length = domain_length
                min_var = var
        return min_var

    # gets values ordered by LCV (Least Constraining Value) if enabled
    #   chooses WHAT value to try in cell first
    #   tries values that eliminate the fewest options for other cells
    def get_ordered_values(self, var):
        if not self.use_lcv:
            return sorted(self.domains[var])
            
        def count_constraints(value):
            count = 0
            row, col = var
            for i in range(self.size):
                for j in range(self.size):
                    if (i, j) != var and self.board[i][j] == self.empty:
                        if i == row or j == col or (i//3 == row//3 and j//3 == col//3):
                            if value in self.domains.get((i, j), set()):
                                count += 1
            return count
        return sorted(self.domains[var], key=count_constraints)

    # function to run forwrd check with conflicts: returns NONE if successful, set of conflicting values if failed
    #   Immediately looks ahead and sees if a move removes all options from any remaining cell
    def forward_check_with_conflicts(self, var, value):
        conflicts = set()
        row, col = var
        
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == self.empty:
                    if (i == row or j == col or 
                        (i//3 == row//3 and j//3 == col//3)):
                        curr_pos = (i, j)
                        self.domains.get(curr_pos, set()).discard(value)
                        
                        if curr_pos in self.domains and not self.domains[curr_pos]:
                            conflicts.add(var)
                            return conflicts
        return None

    # AC3 implementation (with conflict tracking): returns NONE if successful, set of conflicting values if failed
    #   propagation of constraints; can detect further than one step ahead, unlike forward checking
    def ac3_with_conflicts(self):
        queue = deque(self.get_all_edges())
        conflicts = set()
        
        while queue:
            (xi, xj) = queue.popleft()
            
            if self.remove_inconsistent_values(xi, xj):
                if not self.domains[xi]:
                    conflicts.add(xi)
                    conflicts.add(xj)
                    return conflicts
                    
                for xk in self.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))
        return None

    # returns all edges (or pairs of cells) that directly constrain each other in the puzzle
    def get_all_edges(self):
        edges = []
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) in self.domains:
                    # row edges
                    for k in range(self.size):
                        if k != j and (i, k) in self.domains:
                            edges.append(((i, j), (i, k)))
                    # column edges
                    for k in range(self.size):
                        if k != i and (k, j) in self.domains:
                            edges.append(((i, j), (k, j)))
                    # box edges
                    box_i, box_j = 3 * (i // 3), 3 * (j // 3)
                    for k in range(box_i, box_i + 3):
                        for l in range(box_j, box_j + 3):
                            if (k, l) != (i, j) and (k, l) in self.domains:
                                edges.append(((i, j), (k, l)))
        return edges

    # returns all cells that could affect( or be affected by) the value we put in a cell
    def get_neighbors(self, var):
        neighbors = set()
        row, col = var
        # check row neighbors
        for j in range(self.size):
            if j != col and (row, j) in self.domains:
                neighbors.add((row, j))
        
        # check column neighbors
        for i in range(self.size):
            if i != row and (i, col) in self.domains:
                neighbors.add((i, col))
        
        # check box (3x3) neighbors
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i, j) != var and (i, j) in self.domains:
                    neighbors.add((i, j))
        
        return neighbors

    # removes values from a cells domain if they can't work given another cell's domain
    #   helper for AC-3
    def remove_inconsistent_values(self, xi, xj):
        removed = False
        xi_domain = self.domains[xi].copy()
        for x in xi_domain:
            if not any(y != x for y in self.domains[xj]):
                self.domains[xi].remove(x)
                removed = True
        return removed

    # checks if placing a value at a given position is a valid
    def is_safe(self, pos, value):
        row, col = pos
        
        # check the row
        for j in range(self.size):
            if self.board[row][j] == value:
                return False
        
        # check the column       
        for i in range(self.size):
            if self.board[i][col] == value:
                return False
        
        # check the box (3x3)
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == value:
                    return False
        # if none of these snag, then return TRUE, the placement is valid
        return True