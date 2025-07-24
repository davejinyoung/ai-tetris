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
        self.color = shape_colors[shapes.index(shape)]  # choose color from the shape_color list
        self.rotation = 0  # chooses the rotation according to index


# initialise the grid
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]  # grid represented rgb tuples

    # locked_positions dictionary
    # (x,y):(r,g,b)
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]  # get the value color (r,g,b) from the locked_positions dictionary using key (x,y)
                grid[y][x] = color  # set grid position to color

    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]  # get the desired rotated shape from piece

    '''
    e.g.
       ['.....',
        '.....',
        '..00.',
        '.00..',
        '.....']
    '''
    for i, line in enumerate(shape_format):  # i gives index; line gives string
        row = list(line)  # makes a list of char from string
        for j, column in enumerate(row):  # j gives index of char; column gives char
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)  # offset according to the input given with dot and zero

    return positions


# checks if current position of piece in grid is valid
def valid_space(piece, grid):
    # makes a 2D list of all the possible (x,y)
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    # removes sub lists and puts (x,y) in one list; easier to search
    accepted_pos = [x for item in accepted_pos for x in item]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True


# check if piece is out of board
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# chooses a shape randomly from shapes list
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# draws text in the middle
def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(fontpath, size)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))


# draws the lines of the grid for the game
def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)

    for i in range(row):
        # draw grey horizontal lines
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            # draw grey vertical lines
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))


# clear a row when it is filled
def clear_rows(grid, locked):
    # need to check if row is clear then shift every other row above down one
    increment = 0
    for i in range(len(grid) - 1, -1, -1):      # start checking the grid backwards
        grid_row = grid[i]                      # get the last row
        if (0, 0, 0) not in grid_row:           # if there are no empty spaces (i.e. black blocks)
            increment += 1
            # add positions to remove from locked
            index = i                           # row index will be constant
            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]          # delete every locked element in the bottom row
                except ValueError:
                    continue

    # shift every row one step down
    # delete filled bottom row
    # add another empty row on the top
    # move down one step
    if increment > 0:
        # sort the locked list according to y value in (x,y) and then reverse
        # reversed because otherwise the ones on the top will overwrite the lower ones
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                       # if the y value is above the removed index
                new_key = (x, y + increment)    # shift position to down
                locked[new_key] = locked.pop(key)

    return increment


# draws the upcoming piece
def draw_next_shape(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)

    surface.blit(label, (start_x, start_y - 30))


# draws the content of the window
def draw_window(surface, grid, score=0, last_score=0, level=1):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.Font(fontpath_mario, 65)
    label = font.render('TETRIS', 1, (255, 255, 255))
    surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))

    font = pygame.font.Font(fontpath, 25)
    
    # Current Score
    label = font.render('SCORE: ' + str(score) , 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)
    surface.blit(label, (start_x, start_y + 200))

    # High Score
    label_hi = font.render('HIGHSCORE: ' + str(last_score), 1, (255, 255, 255))
    start_x_hi = top_left_x - 240
    surface.blit(label_hi, (start_x_hi, start_y + 200))
    
    # Level
    label_level = font.render('LEVEL: ' + str(level), 1, (255, 255, 255))
    surface.blit(label_level, (start_x_hi, start_y + 240))


    for i in range(row):
        for j in range(col):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    draw_grid(surface)
    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y, play_width, play_height), 4)

# update the score txt file with high score
def update_score(new_score):
    score = get_max_score()

    with open(filepath, 'w') as file:
        if new_score > score:
            file.write(str(new_score))
        else:
            file.write(str(score))


# get the high score from the file
def get_max_score():
    with open(filepath, 'r') as file:
        lines = file.readlines()        # reads all the lines and puts in a list
        score = int(lines[0].strip())   # remove \n

    return score


def get_game_state(current_piece, next_piece, grid, locked_positions):
    return {
        'current_piece': current_piece,
        'next_piece': next_piece,
        'grid': grid,
        'locked_positions': locked_positions
    }

def perform_action(action, current_piece, grid):
    if action == 'left':
        current_piece.x -= 1
        if not valid_space(current_piece, grid):
            current_piece.x += 1
    elif action == 'right':
        current_piece.x += 1
        if not valid_space(current_piece, grid):
            current_piece.x -= 1
    elif action == 'down':
        current_piece.y += 1
        if not valid_space(current_piece, grid):
            current_piece.y -= 1
    elif action == 'rotate':
        current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
        if not valid_space(current_piece, grid):
            current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
    elif action == 'drop':
        while valid_space(current_piece, grid):
            current_piece.y += 1
        current_piece.y -= 1

def main(window):
    locked_positions = {}
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    
    level = 1
    score = 0
    total_lines_cleared = 0
    fall_speed = 0.35 # Initial fall speed
    last_score = get_max_score()

    if ai_mode:
        agent = TetrisAgent()
        # AI needs to think about the very first piece before the loop starts
        game_state = get_game_state(current_piece, next_piece, create_grid(locked_positions), locked_positions)
        ai_target_action = agent.choose_action(game_state)
    else:
        ai_target_action = None

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        if not ai_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()
                    quit()
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
        else:
            # AI Logic (human-like animation)
            if not hasattr(current_piece, 'ai_plan'):
                # Plan the move for this piece
                game_state = get_game_state(current_piece, next_piece, grid, locked_positions)
                ai_target_action = agent.choose_action(game_state)
                current_piece.ai_plan = {
                    'target_x': ai_target_action['x'],
                    'target_rotation': ai_target_action['rotation'],
                    'target_y': ai_target_action['y']
                }
            plan = current_piece.ai_plan
            moved = False
            # Rotate if needed
            if current_piece.rotation != plan['target_rotation']:
                current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                moved = True
            # Move horizontally if needed
            elif current_piece.x < plan['target_x']:
                current_piece.x += 1
                if not valid_space(current_piece, grid):
                    current_piece.x -= 1
                moved = True
            elif current_piece.x > plan['target_x']:
                current_piece.x -= 1
                if not valid_space(current_piece, grid):
                    current_piece.x += 1
                moved = True
            # Move down if needed (simulate soft drop)
            elif current_piece.y < plan['target_y']:
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                moved = True
            # If at target, lock the piece
            else:
                while valid_space(current_piece, grid):
                    current_piece.y += 1
                current_piece.y -= 1
                change_piece = True
                del current_piece.ai_plan
            # Draw the piece on a temporary grid for smooth animation
            if moved:
                temp_grid = [row[:] for row in grid]
                piece_pos = convert_shape_format(current_piece)
                for x, y in piece_pos:
                    if y >= 0 and 0 <= x < col and 0 <= y < row:
                        temp_grid[y][x] = current_piece.color
                draw_window(window, temp_grid, score, last_score, level)
                draw_next_shape(next_piece, window)
                pygame.display.update()
                pygame.time.wait(2)

        piece_pos = convert_shape_format(current_piece)
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            
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
            
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            
            if score > last_score:
                last_score = score
                update_score(last_score)

            if ai_mode:
                game_state = get_game_state(current_piece, next_piece, grid, locked_positions)
                ai_target_action = agent.choose_action(game_state)

        draw_window(window, grid, score, last_score, level)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_middle('You Lost', 40, (255, 255, 255), window)
    pygame.display.update()
    pygame.time.delay(2000)

def draw_button(surface, text, x, y, width, height, color, hover_color):
    """Draw a button and return if it's being hovered over"""
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
    
    # Check if mouse is hovering over button
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, hover_color, button_rect)
    else:
        pygame.draw.rect(surface, color, button_rect)
    
    # Draw button border
    pygame.draw.rect(surface, (255, 255, 255), button_rect, 2)
    
    # Draw text
    font = pygame.font.Font(fontpath, 30)
    label = font.render(text, 1, (255, 255, 255))
    text_x = x + (width - label.get_width()) // 2
    text_y = y + (height - label.get_height()) // 2
    surface.blit(label, (text_x, text_y))
    
    return button_rect.collidepoint(mouse_pos)

def main_menu(window):
    global ai_mode
    run = True
    while run:
        window.fill((0, 0, 0))  # Fill with black background
        
        # Draw title
        draw_text_middle('TETRIS', 65, (255, 255, 255), window)
        
        # Button dimensions and positions
        button_width = 200
        button_height = 60
        center_x = s_width // 2
        button_y = s_height // 2 + 50
        
        # Human mode button
        human_button_x = center_x - button_width - 20
        human_hover = draw_button(window, "Human Mode", human_button_x, button_y, 
                                button_width, button_height, (0, 100, 0), (0, 150, 0))
        
        # AI mode button
        ai_button_x = center_x + 20
        ai_hover = draw_button(window, "AI Mode", ai_button_x, button_y, 
                             button_width, button_height, (100, 0, 0), (150, 0, 0))
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if human_hover:
                    ai_mode = False
                    main(window)
                elif ai_hover:
                    ai_mode = True
                    main(window)

    pygame.quit()


if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    main_menu(win)  # start game
