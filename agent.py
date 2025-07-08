import copy

from pygame.draw import lines


class TetrisAgent:
    def __init__(self):
        weights = []

    def choose_action(self, game_state):
        """
        Given the current game state, return the best action.
        The action is the final state that the piece should land on.
        """
        from Tetris import valid_space, convert_shape_format, col, row, clear_rows
        current_piece = game_state['current_piece']
        grid = game_state['grid']
        locked_positions = game_state['locked_positions']
        possible_moves = []

        # Try all rotations
        for rotation in range(len(current_piece.shape)):
            piece = copy.deepcopy(current_piece)
            piece.rotation = rotation

            # Try all columns
            for x in range(col):
                piece.x = x
                piece.y = 0

                # Drop piece down until it lands
                while valid_space(piece, grid):
                    piece.y += 1
                piece.y -= 1  # Move back up to last valid position

                if valid_space(piece, grid):
                    # Simulate locking the piece
                    move_locked = copy.deepcopy(locked_positions)
                    for pos in convert_shape_format(piece):
                        if pos[1] >= 0:
                            move_locked[(pos[0], pos[1])] = piece.color

                    # Create the resulting grid
                    move_grid = [[(0, 0, 0) for _ in range(col)] for _ in range(row)]
                    for (lx, ly), color in move_locked.items():
                        if 0 <= lx < col and 0 <= ly < row:
                            move_grid[ly][lx] = color

                    # Optionally, simulate row clearing
                    # clear_rows(move_grid, move_locked)

                    # if any position has a negative value, continue the loop
                    positions = convert_shape_format(piece)
                    if any(pos[1] < 0 for pos in positions):
                        continue  # Skip moves where the piece is not fully on the board

                    move = {
                        'rotation': rotation,
                        'x': x,
                        'y': piece.y,
                        'positions': positions,
                        'resulting_grid': move_grid,
                        'eval_score': 0
                    }
                    possible_moves.append(move)

            best_move = self.evaluate_moves(possible_moves)

        return best_move

    # Heuristic evaluation of resulting grid state given every possible move
    def evaluate_moves(self, possible_moves):
        temp_weights = [1, 1, 1, 1] # TODO: replace these placeholder weights for trained weights from GA
        # Heuristic evaluations: lines cleared (+), holes (-), bumpiness (-), Aggregate Height (-)
        best_move = possible_moves[0]
        for move in possible_moves:
            lines_cleared = self.lines_cleared(move['resulting_grid'])
            holes = self.count_holes(move['resulting_grid'])
            aggregate_height = self.get_aggregate_height(move['resulting_grid'])
            bumpiness = self.get_bumpiness(move['resulting_grid'])

            move['eval_score'] = (temp_weights[0]*lines_cleared -
                                  temp_weights[1]*holes -
                                  temp_weights[2]*aggregate_height -
                                  temp_weights[3]*bumpiness)

            if move['eval_score'] > best_move['eval_score']:
                best_move = move

        return best_move

    def lines_cleared(self, resulting_grid):
        cleared_lines = [line for line in resulting_grid if (0, 0, 0) not in line]
        return len(cleared_lines)

    def count_holes(self, resulting_grid):
        total_holes = 0

        # Check if the grid is empty to avoid errors
        if not resulting_grid or not resulting_grid[0]:
            return 0

        num_rows = len(resulting_grid)
        num_cols = len(resulting_grid[0])

        # Iterate through each column from left to right
        for col in range(num_cols):
            block_found_in_column = False
            # Scan down the column from top to bottom
            for row in range(num_rows):
                # Check if the cell is filled
                if resulting_grid[row][col] != (0, 0, 0):
                    block_found_in_column = True
                # If we've already passed a block in this column and the current cell is empty...
                elif block_found_in_column and resulting_grid[row][col] == (0, 0, 0):
                    # ...it's a hole.
                    total_holes += 1

        return total_holes

    def get_aggregate_height(self, resulting_grid):
        """
        Calculates the sum of the heights of all columns.
        """
        total_height = 0
        if not resulting_grid or not resulting_grid[0]:
            return 0

        num_rows = len(resulting_grid)
        num_cols = len(resulting_grid[0])

        # Iterate through each column
        for col in range(num_cols):
            column_height = 0
            # Scan down the column to find the first filled block
            for row in range(num_rows):
                if resulting_grid[row][col] != (0, 0, 0):
                    # The height is the distance from the bottom
                    column_height = num_rows - row
                    break  # Move to the next column
            total_height += column_height

        return total_height

    def get_column_heights(self, resulting_grid):
        """
        Returns a list containing the height of each column.
        """
        if not resulting_grid or not resulting_grid[0]:
            return []

        num_rows = len(resulting_grid)
        num_cols = len(resulting_grid[0])
        heights = [0] * num_cols

        for col in range(num_cols):
            for row in range(num_rows):
                if resulting_grid[row][col] != (0, 0, 0):
                    heights[col] = num_rows - row
                    break
        return heights

    def get_bumpiness(self, resulting_grid):
        """
        Calculates the total bumpiness of the board.
        """
        heights = self.get_column_heights(resulting_grid)

        if not heights:
            return 0

        total_bumpiness = 0
        # Iterate through all adjacent column pairs
        for i in range(len(heights) - 1):
            total_bumpiness += abs(heights[i] - heights[i + 1])

        return total_bumpiness

