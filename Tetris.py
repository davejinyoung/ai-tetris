import random
import pygame
from agent import TetrisAgent

"""
10 x 20 grid
play_height = 2 * play_width

tetriminos:
    0 - S - green
    1 - Z - red
    2 - I - cyan
    3 - O - yellow
    4 - J - blue
    5 - L - orange
    6 - T - purple
"""

pygame.font.init()

# global variables

col = 10  # 10 columns
row = 20  # 20 rows
s_width = 800  # window width
s_height = 750  # window height
play_width = 300  # play window width; 300/10 = 30 width per block
play_height = 600  # play window height; 600/20 = 20 height per block
block_size = 30  # size of block

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

filepath = './highscore.txt'
fontpath = './arcade.ttf'
fontpath_mario = './mario.ttf'

# shapes formats

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# index represents the shape
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# class to represent each of the pieces
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]
    
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[(x, y)]
                grid[y][x] = color

    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row_list = list(line)
        for j, column in enumerate(row_list):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(piece, grid):
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    accepted_pos = [x for item in accepted_pos for x in item]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(fontpath, size)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))


def draw_grid(surface):
    grid_color = (0, 0, 0)
    for i in range(row):
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
    for j in range(col):
        pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))


def clear_rows(grid, locked):
    """
    Checks for completed rows, clears them, and shifts the rows above down.
    Returns the number of rows cleared.
    """
    rows_to_clear = []
    for i in range(len(grid)):
        if (0, 0, 0) not in grid[i]:
            rows_to_clear.append(i)

    cleared_count = len(rows_to_clear)

    if cleared_count > 0:
        new_locked = {}
        for (x, y), color in locked.items():
            if y not in rows_to_clear:
                shift = sum(1 for cleared_row_index in rows_to_clear if y < cleared_row_index)
                new_locked[(x, y + shift)] = color
        
        locked.clear()
        locked.update(new_locked)

    return cleared_count


def draw_next_shape(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row_list = list(line)
        for j, column in enumerate(row_list):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)

    surface.blit(label, (start_x, start_y - 30))


def draw_window(surface, grid, score=0, last_score=0, level=1):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.Font(fontpath_mario, 65)
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.Font(fontpath, 25)
    label = font.render('SCORE   ' + str(score) , 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    surface.blit(label, (start_x, start_y + 200))

    # last score
    label_hi = font.render('HIGHSCORE   ' + str(last_score), 1, (255, 255, 255))

    start_x_hi = top_left_x - 240
    start_y_hi = top_left_y + 200

    surface.blit(label_hi, (start_x_hi + 20, start_y_hi + 200))

    # Level
    label_level = font.render('LEVEL: ' + str(level), 1, (255, 255, 255))
    surface.blit(label_level, (start_x_hi + 20, start_y_hi + 240))

    # draw content of the grid
    for i in range(row):
        for j in range(col):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    draw_grid(surface)

    # draw rectangular border around play area
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)


def update_score(new_score):
    score = get_max_score()

    with open(filepath, 'w') as file:
        if new_score > score:
            file.write(str(new_score))
        else:
            file.write(str(score))


def get_max_score():
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            if lines:
                score = int(lines[0].strip())
            else:
                score = 0
    except (FileNotFoundError, IndexError, ValueError):
        score = 0
    return score


def get_game_state(current_piece, next_piece, grid, locked_positions):
    return {
        'current_piece': current_piece,
        'next_piece': next_piece,
        'grid': grid,
        'locked_positions': locked_positions
    }


def main(window=None, agent=None, is_training=False):
    """
    Main game loop. Can be run in normal, AI, or training mode.
    
    Args:
        window: The pygame screen surface to draw on.
        agent: The AI agent that will play the game.
        is_training: Flag to run in high-speed mode without visuals.
    """
    is_ai_controlled = False
    if agent:
        is_ai_controlled = True
    else:
        try:
            global ai_mode
            is_ai_controlled = ai_mode
        except NameError:
            is_ai_controlled = False

    locked_positions = {}
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    
    if not is_training:
        clock = pygame.time.Clock()
    
    fall_time = 0
    level = 1
    score = 0
    total_lines_cleared = 0
    fall_speed = 0.35
    
    if not is_training:
        last_score = get_max_score()
    else:
        last_score = 0
    
    if is_ai_controlled and agent is None:
        agent = TetrisAgent()

    while run:
        grid = create_grid(locked_positions)
        
        if not is_training:
            fall_time += clock.get_rawtime()
            clock.tick(60)
        
        # Gravity Logic (ONLY for human players)
        if not is_ai_controlled:
            if fall_time / 1000 > fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True
        
        # Human Player Input
        if not is_ai_controlled and not is_training:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    if not is_training:
                        update_score(score)
                        pygame.display.quit()
                    return score
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid): 
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid): 
                            current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid): 
                            current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                        if not valid_space(current_piece, grid): 
                            current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                    elif event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1
                        change_piece = True
        
        # AI Logic
        elif is_ai_controlled:
            # Handle pygame events even in AI mode to prevent window freezing
            if not is_training:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        return score
            
            if not hasattr(current_piece, 'ai_plan'):
                game_state = get_game_state(current_piece, next_piece, grid, locked_positions)
                ai_target_action = agent.choose_action(game_state)
                current_piece.ai_plan = {
                    'target_x': ai_target_action['x'],
                    'target_rotation': ai_target_action['rotation'],
                    'target_y': ai_target_action['y']
                }
            
            plan = current_piece.ai_plan
            moved = False
            
            # Move horizontally first
            if current_piece.x < plan['target_x']:
                current_piece.x += 1
                if not valid_space(current_piece, grid):
                    current_piece.x -= 1
                moved = True
            elif current_piece.x > plan['target_x']:
                current_piece.x -= 1
                if not valid_space(current_piece, grid):
                    current_piece.x += 1
                moved = True
            # Then rotate
            elif current_piece.rotation != plan['target_rotation']:
                current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                if not valid_space(current_piece, grid):
                    current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                moved = True
            # Then soft drop
            elif current_piece.y < plan['target_y']:
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                moved = True
            # If at target, hard drop and lock
            else:
                while valid_space(current_piece, grid):
                    current_piece.y += 1
                current_piece.y -= 1
                change_piece = True
                if hasattr(current_piece, 'ai_plan'):
                    del current_piece.ai_plan
        
        # Piece Locking and Game State Update
        if change_piece:
            piece_pos = convert_shape_format(current_piece)
            for pos in piece_pos:
                if 0 <= pos[0] < col and 0 <= pos[1] < row:
                    locked_positions[(pos[0], pos[1])] = current_piece.color
            
            # Rebuild grid with locked piece before checking for line clears
            grid = create_grid(locked_positions)
            lines_cleared_this_turn = clear_rows(grid, locked_positions)
            
            if lines_cleared_this_turn > 0:
                total_lines_cleared += lines_cleared_this_turn
                score_multipliers = {1: 40, 2: 100, 3: 300, 4: 1200}
                base_points = score_multipliers.get(lines_cleared_this_turn, 0)
                score += base_points * level
                
                if total_lines_cleared >= level * 10:
                    level += 1
                    if fall_speed > 0.15: 
                        fall_speed -= 0.025
                
                # Show line clear animation if not training
                if not is_training and window:
                    # Flash the cleared lines briefly
                    temp_grid = create_grid(locked_positions)
                    draw_window(window, temp_grid, score, last_score, level)
                    draw_next_shape(next_piece, window)
                    pygame.display.update()
                    pygame.time.wait(50)
            
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            
            if not is_training and score > last_score:
                last_score = score
                update_score(last_score)

        # Drawing (only if not training)
        if not is_training and window:
            # Use the current grid state (which may have been updated by line clears)
            display_grid = create_grid(locked_positions)
            
            # Add current piece to display grid only if game is still running
            if run:
                piece_pos = convert_shape_format(current_piece)
                for x, y in piece_pos:
                    if 0 <= y < row and 0 <= x < col:
                        display_grid[y][x] = current_piece.color
            
            draw_window(window, display_grid, score, last_score, level)
            draw_next_shape(next_piece, window)
            pygame.display.update()

        # Check game over condition
        if check_lost(locked_positions):
            run = False

    # Game Over
    if not is_training and window:
        draw_text_middle('You Lost', 40, (255, 255, 255), window)
        pygame.display.update()
        pygame.time.delay(2000)
    
    return score


def draw_button(surface, text, x, y, width, height, color, hover_color):
    """Draw a button and return if it's being hovered over"""
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
    
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, hover_color, button_rect, border_radius=8)
    else:
        pygame.draw.rect(surface, color, button_rect, border_radius=8)
    
    pygame.draw.rect(surface, (255, 255, 255), button_rect, 2, border_radius=8)
    
    font = pygame.font.Font(fontpath, 30)
    label = font.render(text, 1, (255, 255, 255))
    text_x = x + (width - label.get_width()) // 2
    text_y = y + (height - label.get_height()) // 2
    surface.blit(label, (text_x, text_y))
    
    return button_rect.collidepoint(mouse_pos)


def main_menu(window):
    global ai_mode
    run = True
    clock = pygame.time.Clock()
    
    while run:
        window.fill((0, 0, 0))
        
        draw_text_middle('TETRIS', 80, (255, 255, 255), window)
        
        button_width = 220
        button_height = 60
        center_x = s_width // 2
        button_y = s_height // 2 + 50
        
        human_hover = draw_button(window, "Human Mode", center_x - button_width - 20, button_y, 
                                button_width, button_height, (0, 100, 0), (0, 150, 0))
        
        ai_hover = draw_button(window, "AI Mode", center_x + 20, button_y, 
                             button_width, button_height, (100, 0, 0), (150, 0, 0))
        
        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if human_hover:
                        ai_mode = False
                        main(window)
                    elif ai_hover:
                        ai_mode = True
                        main(window)
    
    pygame.quit()


if __name__ == '__main__':
    pygame.display.init()
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    main_menu(win)