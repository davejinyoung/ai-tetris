import copy
import numpy as np

class TetrisAgent:
    def __init__(self, weights=None):
        """
        Initializes the agent.
        """
        if weights is not None:
            self.weights = weights
        else:
            self.weights = np.array([0.55580476, 0.83967109, 0.32826192, 0.26066793]) # current best weights according to GA

    def choose_action(self, game_state):
        """
        Given the current game state, return the best action.
        The action is the final state that the piece should land on.
        """
        from Tetris import valid_space, convert_shape_format, col, row
        current_piece = game_state['current_piece']
        grid = game_state['grid']
        
        possible_moves = []

        # Try all rotations
        for rotation in range(len(current_piece.shape)):
            piece = copy.deepcopy(current_piece)
            piece.rotation = rotation

            # Try all columns
            for x in range(col):
                piece.x = x
                
                # Find where the piece would land in this column
                piece.y = 0
                while valid_space(piece, grid):
                    piece.y += 1
                piece.y -= 1

                # Create a temporary grid representing the board after this move
                temp_grid = [row[:] for row in grid]
                piece_pos = convert_shape_format(piece)
                
                # Check if the move is valid (not partially off-screen at the top)
                if any(p[1] < 0 for p in piece_pos):
                    continue

                for x_pos, y_pos in piece_pos:
                    if y_pos < row and x_pos < col:
                        temp_grid[y_pos][x_pos] = piece.color
                
                move = {
                    'rotation': rotation,
                    'x': x,
                    'y': piece.y,
                    'resulting_grid': temp_grid,
                }
                possible_moves.append(move)
        
        if not possible_moves:
             return {'rotation': 0, 'x': 5, 'y': 0} # Default move if no valid moves found

        best_move = self.evaluate_moves(possible_moves)
        return best_move

    def evaluate_moves(self, possible_moves):
        """Heuristic evaluation of resulting grid state given every possible move."""
        best_score = -float('inf')
        best_move = possible_moves[0]

        for move in possible_moves:
            grid = move['resulting_grid']
            
            lines_cleared = self.lines_cleared(grid)
            holes = self.count_holes(grid)
            aggregate_height = self.get_aggregate_height(grid)
            bumpiness = self.get_bumpiness(grid)
            
            # Use the agent's weights for evaluation
            score = (self.weights[0] * lines_cleared -
                     self.weights[1] * holes -
                     self.weights[2] * aggregate_height -
                     self.weights[3] * bumpiness)

            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def lines_cleared(self, resulting_grid):
        """Counts the number of lines to be cleared in the given grid"""
        cleared_lines = 0
        for row in resulting_grid:
            if (0, 0, 0) not in row:
                cleared_lines += 1
        return cleared_lines

    def count_holes(self, resulting_grid):
        """Counts the number of holes in the given grid"""
        total_holes = 0
        num_cols = len(resulting_grid[0])
        for col_idx in range(num_cols):
            block_found = False
            for row_idx in range(len(resulting_grid)):
                if resulting_grid[row_idx][col_idx] != (0, 0, 0):
                    block_found = True
                elif block_found and resulting_grid[row_idx][col_idx] == (0, 0, 0):
                    total_holes += 1
        return total_holes

    def get_aggregate_height(self, resulting_grid):
        """Sum of the column height"""
        heights = self.get_column_heights(resulting_grid)
        return sum(heights)

    def get_column_heights(self, resulting_grid):
        """All column heights"""
        num_rows = len(resulting_grid)
        num_cols = len(resulting_grid[0])
        heights = [0] * num_cols
        for col_idx in range(num_cols):
            for row_idx in range(num_rows):
                if resulting_grid[row_idx][col_idx] != (0, 0, 0):
                    heights[col_idx] = num_rows - row_idx
                    break
        return heights

    
    def get_bumpiness(self, resulting_grid):
        """The total difference in height between columns"""
        heights = self.get_column_heights(resulting_grid)
        total_bumpiness = 0
        for i in range(len(heights) - 1):
            total_bumpiness += abs(heights[i] - heights[i+1])
        return total_bumpiness
