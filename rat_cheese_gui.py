# Enhanced screen setup with improved visuals and better scoreboard
import pygame
import sys
import random
import math
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# Screen setup (windowed mode with standard game resolution)
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rat, Cheese & Trap Word Guessing Game")

# Colors
BACKGROUND = (30, 25, 40)  # darker for contrast
TEXT_COLOR = (240, 240, 255)
ACCENT = (255, 215, 0)
RAT_COLOR = (160, 160, 170)
TRAP_COLOR = (200, 60, 60)
CHEESE_COLOR = (255, 230, 100)
BUTTON_COLOR = (80, 140, 200)
BUTTON_HOVER = (110, 170, 230)
GRID_COLOR = (70, 65, 90)
CORRECT_COLOR = (110, 240, 110)
INCORRECT_COLOR = (240, 110, 110)
KITCHEN_WALL = (80, 70, 100)  # dark cabinet wall
KITCHEN_TILE = (60, 50, 80)   # muted floor tiles
KITCHEN_CABINET = (100, 80, 60)  # dark wood for contrast
SCOREBOARD_BG = (45, 40, 65)  # darker background for scoreboard
SCOREBOARD_BORDER = (120, 100, 140)  # subtle border color

# Fixed positioning constants
TITLE_Y = 25
SCOREBOARD_Y = 90   # Moved up slightly to avoid overlap
PIXEL_ART_Y = 150   # Adjusted to maintain spacing
PATH_Y = 260
WORD_Y = 330        # Moved up to maintain proportions
LETTER_GRID_Y = 400 # Adjusted accordingly
RESTART_BUTTON_Y = 700  # Moved to bottom, well below letter grid

# Fonts (scaled to resolution)
title_font = pygame.font.SysFont("couriernew", min(48, HEIGHT // 20), bold=True)
word_font = pygame.font.SysFont("couriernew", min(40, HEIGHT // 25), bold=True)
letter_font = pygame.font.SysFont("couriernew", min(32, HEIGHT // 30))
button_font = pygame.font.SysFont("couriernew", min(28, HEIGHT // 35))
score_font = pygame.font.SysFont("couriernew", min(36, HEIGHT // 25), bold=True)

# Load words from wordlist.txt
try:
    with open("wordlist.txt") as f:
        WORDS = [line.strip().upper() for line in f if line.strip()]
except FileNotFoundError:
    # Fallback words if file doesn't exist
    WORDS = ["PYTHON", "GAMES", "CODING", "PUZZLE", "KITCHEN", "MOUSE", "CHEESE", "TRAP"]

try:
    # Create simple beep sounds
    correct_sound = pygame.mixer.Sound(buffer=bytes([128] * 1000))
    correct_sound.set_volume(0.3)
    incorrect_sound = pygame.mixer.Sound(buffer=bytes([0] * 1000))
    incorrect_sound.set_volume(0.3)
    win_sound = pygame.mixer.Sound(buffer=bytes([200] * 2000))
    win_sound.set_volume(0.5)
    lose_sound = pygame.mixer.Sound(buffer=bytes([50] * 3000))
    lose_sound.set_volume(0.5)
except:
    # Fallback if sound initialization fails
    correct_sound = incorrect_sound = win_sound = lose_sound = None

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False
        self.shadow_offset = 5
        
    def draw(self, surface):
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(surface, (30, 30, 50), shadow_rect, border_radius=8)
        
        # Draw button
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=8)
        
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def draw_kitchen_background(surface):
    # Draw kitchen walls
    surface.fill(KITCHEN_WALL)
    
    # Draw kitchen tiles (floor)
    tile_size = 60
    for y in range(HEIGHT // 2, HEIGHT, tile_size):
        for x in range(0, WIDTH, tile_size):
            color = KITCHEN_TILE if (x//tile_size + y//tile_size) % 2 == 0 else (KITCHEN_TILE[0]-20, KITCHEN_TILE[1]-20, KITCHEN_TILE[2]-20)
            pygame.draw.rect(surface, color, (x, y, tile_size, tile_size))
            pygame.draw.rect(surface, (KITCHEN_TILE[0]-40, KITCHEN_TILE[1]-40, KITCHEN_TILE[2]-40), 
                           (x, y, tile_size, tile_size), 1)
    
    # Draw kitchen cabinets (top)
    pygame.draw.rect(surface, KITCHEN_CABINET, (0, 0, WIDTH, HEIGHT//8))
    pygame.draw.rect(surface, (KITCHEN_CABINET[0]-30, KITCHEN_CABINET[1]-30, KITCHEN_CABINET[2]-30), 
                   (0, HEIGHT//8, WIDTH, 15))
    
    # Draw cabinet details
    cabinet_width = WIDTH // 6
    for i in range(6):
        x = i * cabinet_width
        pygame.draw.rect(surface, (KITCHEN_CABINET[0]-40, KITCHEN_CABINET[1]-40, KITCHEN_CABINET[2]-40), 
                       (x + cabinet_width//2 - 10, HEIGHT//16 - 10, 20, 20), border_radius=10)
    
    # Draw countertop
    pygame.draw.rect(surface, (100, 80, 60), (0, HEIGHT//8 + 15, WIDTH, 25))
    
    # Draw backsplash
    backsplash_height = HEIGHT//10
    pygame.draw.rect(surface, (180, 150, 120), (0, HEIGHT//8 + 40, WIDTH, backsplash_height))
    
    # Draw tile pattern on backsplash
    tile_size = backsplash_height // 2
    for y in range(HEIGHT//8 + 40, HEIGHT//8 + 40 + backsplash_height, tile_size):
        for x in range(0, WIDTH, tile_size):
            pygame.draw.rect(surface, (160, 130, 100), (x, y, tile_size, tile_size), 2)

def draw_pixel_art(surface, rat_pos, game_over, win):
    # Enhanced trap (more detailed pixel art)
    trap_x = WIDTH * 0.1 - 30
    trap_y = PIXEL_ART_Y - 10
    trap_color = TRAP_COLOR if not game_over or not win else (100, 100, 100)
    
    # More realistic trap with spring mechanism
    trap_pixels = [
        "    XXXXXXXXXX    ",
        "   X          X   ",
        "  X   XXXXXX   X  ",
        " X   X      X   X ",
        "X   X XXXXXX X   X",
        "X  X  X    X  X  X",
        "X  X  X    X  X  X",
        "X  X  XXXXXX  X  X",
        "X   X        X   X",
        " X   XXXXXXXX   X ",
        "  X            X  ",
        "   XXXXXXXXXXXX   ",
        "    XXXXXXXXXX    "
    ]
    
    for i, row in enumerate(trap_pixels):
        for j, char in enumerate(row):
            if char == 'X':
                pygame.draw.rect(surface, trap_color, 
                                (trap_x + j*4, trap_y + i*4, 3, 3))
    
    # Add trap details (spring and trigger)
    spring_color = (150, 150, 150)
    pygame.draw.rect(surface, spring_color, (trap_x + 28, trap_y + 20, 8, 20))
    pygame.draw.rect(surface, spring_color, (trap_x + 40, trap_y + 20, 8, 20))
    
    # Enhanced cheese (more detailed and appetizing)
    cheese_x = WIDTH * 0.8 - 30
    cheese_y = PIXEL_ART_Y - 10
    cheese_color = CHEESE_COLOR if not game_over or win else (180, 180, 100)
    cheese_dark = (200, 180, 60)
    
    # More realistic cheese with holes
    cheese_pixels = [
        "     XXXXXXXX     ",
        "   XX        XX   ",
        "  X    XX      X  ",
        " X   XX  XX     X ",
        "X    X    X   X  X",
        "X  XX      XX    X",
        "X X    XX    X   X",
        "X   XX    XX   X X",
        "X    X      X    X",
        " X    XXXXXX    X ",
        "  X            X  ",
        "   XXXXXXXXXXXX   ",
        "    XXXXXXXXXX    "
    ]
    
    for i, row in enumerate(cheese_pixels):
        for j, char in enumerate(row):
            if char == 'X':
                # Add shading to make it look more 3D
                color = cheese_dark if i > 6 or j > 8 else cheese_color
                pygame.draw.rect(surface, color, 
                                (cheese_x + j*4, cheese_y + i*4, 3, 3))
    
    # Add cheese holes
    hole_color = (180, 150, 80)
    pygame.draw.circle(surface, hole_color, (cheese_x + 20, cheese_y + 16), 4)
    pygame.draw.circle(surface, hole_color, (cheese_x + 40, cheese_y + 24), 3)
    pygame.draw.circle(surface, hole_color, (cheese_x + 28, cheese_y + 32), 2)
    
    # Enhanced rat (more detailed and cute)
    rat_x = WIDTH * 0.1 + (WIDTH * 0.7) * rat_pos - 35
    rat_y = PIXEL_ART_Y - 15
    rat_color = RAT_COLOR
    rat_dark = (120, 120, 130)
    
    # Add animation effect
    animation_offset = 0
    if not game_over:
        animation_offset = math.sin(pygame.time.get_ticks() / 200) * 2
    
    # More detailed rat with ears, tail, and whiskers
    rat_pixels = [
        "   XX      XX   ",
        "  X  X    X  X  ",
        " X    XXXX    X ",
        "X   XX    XX   X",
        "X  X        X  X",
        "X X  XX  XX  X X",
        "X X  X    X  X X",
        "X  X  XXXX  X  X",
        " X   X    X   X ",
        "  X   XXXX   X  ",
        "   XX      XX   ",
        "    XXXXXXXX    ",
        "   XXXXXXXXXX   ",
        "  XXXXXXXXXXXX  "
    ]
    
    for i, row in enumerate(rat_pixels):
        for j, char in enumerate(row):
            if char == 'X':
                # Add shading for 3D effect
                color = rat_dark if i > 8 or j > 8 else rat_color
                pygame.draw.rect(surface, color, 
                                (rat_x + j*3, rat_y + i*3 + animation_offset, 2, 2))
    
    # Add rat details (eyes, nose, whiskers)
    eye_color = (50, 50, 50)
    nose_color = (200, 100, 100)
    whisker_color = (100, 100, 100)
    
    # Eyes
    pygame.draw.circle(surface, eye_color, (int(rat_x + 18), int(rat_y + 18 + animation_offset)), 2)
    pygame.draw.circle(surface, eye_color, (int(rat_x + 30), int(rat_y + 18 + animation_offset)), 2)
    
    # Nose
    pygame.draw.circle(surface, nose_color, (int(rat_x + 24), int(rat_y + 24 + animation_offset)), 1)
    
    # Whiskers
    pygame.draw.line(surface, whisker_color, (rat_x + 10, rat_y + 22 + animation_offset), (rat_x + 2, rat_y + 20 + animation_offset), 1)
    pygame.draw.line(surface, whisker_color, (rat_x + 10, rat_y + 26 + animation_offset), (rat_x + 2, rat_y + 28 + animation_offset), 1)
    pygame.draw.line(surface, whisker_color, (rat_x + 38, rat_y + 22 + animation_offset), (rat_x + 46, rat_y + 20 + animation_offset), 1)
    pygame.draw.line(surface, whisker_color, (rat_x + 38, rat_y + 26 + animation_offset), (rat_x + 46, rat_y + 28 + animation_offset), 1)
    
    # Tail
    tail_segments = 8
    for i in range(tail_segments):
        tail_x = rat_x - 10 - i * 4
        tail_y = rat_y + 35 + math.sin(i * 0.5 + pygame.time.get_ticks() / 300) * 3
        pygame.draw.circle(surface, rat_color, (int(tail_x), int(tail_y)), 2)

def draw_path(surface, rat_pos):
    # Draw path from trap to cheese
    path_y = PATH_Y
    pygame.draw.line(surface, (80, 70, 50), (WIDTH*0.1, path_y), (WIDTH*0.9, path_y), 5)
    
    # Draw path details
    for i in range(0, int(WIDTH*0.8), 15):
        x = WIDTH*0.1 + i
        pygame.draw.line(surface, (100, 90, 60), (x, path_y-3), (x, path_y+3), 2)
    
    # Draw rat position indicator
    rat_x = WIDTH*0.1 + (WIDTH*0.8) * rat_pos
    pygame.draw.circle(surface, RAT_COLOR, (int(rat_x), int(path_y)), 15)
    pygame.draw.circle(surface, (200, 200, 220), (int(rat_x), int(path_y)), 8)
    
    # Draw trap and cheese indicators
    pygame.draw.circle(surface, TRAP_COLOR, (int(WIDTH*0.1), int(path_y)), 12)
    pygame.draw.circle(surface, CHEESE_COLOR, (int(WIDTH*0.9), int(path_y)), 12)

def draw_letters(surface, guessed, correct_letters, incorrect_letters):
    # Draw letter grid
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    start_x = WIDTH // 2 - 250
    start_y = LETTER_GRID_Y
    
    for i, letter in enumerate(letters):
        row = i // 7
        col = i % 7
        x = start_x + col * 70
        y = start_y + row * 60
        
        rect = pygame.Rect(x, y, 50, 50)
        color = CORRECT_COLOR if letter in correct_letters else \
                INCORRECT_COLOR if letter in incorrect_letters else \
                GRID_COLOR
        
        # Draw shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(surface, (30, 30, 50), shadow_rect, border_radius=5)
        
        # Draw letter box
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, TEXT_COLOR, rect, 2, border_radius=5)
        
        text_color = BACKGROUND if letter in correct_letters or letter in incorrect_letters else TEXT_COLOR
        text_surf = letter_font.render(letter, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

def draw_word(surface, word, guessed):
    # Display the word with blanks for unguessed letters
    display_word = ""
    for char in word:
        if char in guessed:
            display_word += char + " "
        else:
            display_word += "_ "
    
    # Create a background for the word
    word_bg = pygame.Rect(WIDTH//2 - 200, WORD_Y - 30, 400, 60)
    pygame.draw.rect(surface, (50, 45, 70, 180), word_bg, border_radius=10)
    pygame.draw.rect(surface, TEXT_COLOR, word_bg, 2, border_radius=10)
    
    text_surf = word_font.render(display_word, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(WIDTH//2, WORD_Y))
    surface.blit(text_surf, text_rect)

def draw_scoreboard(surface, wins, losses):
    # Enhanced scoreboard with better background coverage and positioning
    score_bg = pygame.Rect(WIDTH//2 - 180, SCOREBOARD_Y - 25, 360, 50)
    
    # Draw multiple layers for better coverage
    # Shadow layer
    shadow_rect = score_bg.copy()
    shadow_rect.x += 3
    shadow_rect.y += 3
    pygame.draw.rect(surface, (20, 15, 30), shadow_rect, border_radius=15)
    
    # Main background - darker and more opaque
    pygame.draw.rect(surface, SCOREBOARD_BG, score_bg, border_radius=15)
    
    # Inner border for depth
    inner_rect = pygame.Rect(WIDTH//2 - 170, SCOREBOARD_Y - 15, 340, 30)
    pygame.draw.rect(surface, (55, 50, 75), inner_rect, border_radius=12)
    
    # Outer border with accent color
    pygame.draw.rect(surface, SCOREBOARD_BORDER, score_bg, 2, border_radius=15)
    
    # Draw decorative elements - smaller and more subtle
    # Left decoration
    pygame.draw.circle(surface, ACCENT, (WIDTH//2 - 150, SCOREBOARD_Y), 6)
    pygame.draw.circle(surface, SCOREBOARD_BG, (WIDTH//2 - 150, SCOREBOARD_Y), 4)
    
    # Right decoration
    pygame.draw.circle(surface, ACCENT, (WIDTH//2 + 150, SCOREBOARD_Y), 6)
    pygame.draw.circle(surface, SCOREBOARD_BG, (WIDTH//2 + 150, SCOREBOARD_Y), 4)
    
    # Draw score text with better formatting
    wins_text = f"WINS: {wins}"
    losses_text = f"LOSSES: {losses}"
    
    # Use slightly smaller font for better fit
    score_display_font = pygame.font.SysFont("couriernew", min(28, HEIGHT // 30), bold=True)
    
    # Draw wins
    wins_surf = score_display_font.render(wins_text, True, CORRECT_COLOR)
    wins_rect = wins_surf.get_rect(center=(WIDTH//2 - 70, SCOREBOARD_Y))
    surface.blit(wins_surf, wins_rect)
    
    # Draw separator
    separator_surf = score_display_font.render("•", True, TEXT_COLOR)
    separator_rect = separator_surf.get_rect(center=(WIDTH//2, SCOREBOARD_Y))
    surface.blit(separator_surf, separator_rect)
    
    # Draw losses
    losses_surf = score_display_font.render(losses_text, True, INCORRECT_COLOR)
    losses_rect = losses_surf.get_rect(center=(WIDTH//2 + 70, SCOREBOARD_Y))
    surface.blit(losses_surf, losses_rect)

def draw_title(surface):
    # Draw title with shadow
    title_text = "RAT, CHEESE & TRAP"
    shadow_surf = title_font.render(title_text, True, (30, 30, 50))
    shadow_rect = shadow_surf.get_rect(center=(WIDTH//2 + 3, TITLE_Y + 3))
    surface.blit(shadow_surf, shadow_rect)
    
    title_surf = title_font.render(title_text, True, ACCENT)
    title_rect = title_surf.get_rect(center=(WIDTH//2, TITLE_Y))
    surface.blit(title_surf, title_rect)
    
    # Draw subtitle
    subtitle_text = "WORD GUESSING GAME"
    subtitle_surf = button_font.render(subtitle_text, True, TEXT_COLOR)
    subtitle_rect = subtitle_surf.get_rect(center=(WIDTH//2, TITLE_Y + 35))
    surface.blit(subtitle_surf, subtitle_rect)

def main():
    clock = pygame.time.Clock()
    
    # Game state
    current_word = random.choice(WORDS)
    guessed_letters = set()
    correct_letters = set()
    incorrect_letters = set()
    rat_position = 0.5  # 0.0 = trap, 1.0 = cheese
    game_over = False
    win = False
    wins = 0
    losses = 0
    last_move_time = 0
    
    # Create buttons with fixed positions
    restart_button = Button(WIDTH//2 - 100, RESTART_BUTTON_Y, 200, 50, "RESTART GAME")
    exit_button = Button(WIDTH - 120, 20, 100, 40, "EXIT")
    
    # Animation variables
    cheese_particles = []
    trap_particles = []
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            if not game_over:
                if event.type == KEYDOWN:
                    if event.unicode.isalpha():
                        letter = event.unicode.upper()
                        if letter not in guessed_letters:
                            guessed_letters.add(letter)
                            
                            if letter in current_word:
                                correct_letters.add(letter)
                                if correct_sound:
                                    correct_sound.play()
                                rat_position = min(rat_position + 0.1, 1.0)
                                last_move_time = current_time
                            else:
                                incorrect_letters.add(letter)
                                if incorrect_sound:
                                    incorrect_sound.play()
                                rat_position = max(rat_position - 0.1, 0.0)
                                last_move_time = current_time
            
            # Check button clicks
            if restart_button.is_clicked(mouse_pos, event):
                # Reset game
                current_word = random.choice(WORDS)
                guessed_letters = set()
                correct_letters = set()
                incorrect_letters = set()
                rat_position = 0.5
                game_over = False
                win = False
                cheese_particles = []
                trap_particles = []
            
            if exit_button.is_clicked(mouse_pos, event):
                running = False
        
        # Update button hover state
        restart_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        
        # Check game state
        if not game_over:
            # Check if all letters are guessed
            if all(letter in guessed_letters for letter in current_word):
                game_over = True
                win = True
                wins += 1
                if win_sound:
                    win_sound.play()
                # Create cheese particles
                for _ in range(30):
                    cheese_particles.append({
                        'x': WIDTH * 0.8,
                        'y': PIXEL_ART_Y,
                        'dx': random.uniform(-3, 3),
                        'dy': random.uniform(-3, 3),
                        'life': random.randint(20, 40)
                    })
            
            # Check if rat reached trap or cheese
            if rat_position <= 0.0:
                game_over = True
                win = False
                losses += 1
                if lose_sound:
                    lose_sound.play()
                # Create trap particles
                for _ in range(30):
                    trap_particles.append({
                        'x': WIDTH * 0.1,
                        'y': PIXEL_ART_Y,
                        'dx': random.uniform(-3, 3),
                        'dy': random.uniform(-3, 3),
                        'life': random.randint(20, 40)
                    })
            elif rat_position >= 1.0:
                game_over = True
                win = True
                wins += 1
                if win_sound:
                    win_sound.play()
                # Create cheese particles
                for _ in range(30):
                    cheese_particles.append({
                        'x': WIDTH * 0.8,
                        'y': PIXEL_ART_Y,
                        'dx': random.uniform(-3, 3),
                        'dy': random.uniform(-3, 3),
                        'life': random.randint(20, 40)
                    })
        
        # Update particles
        for p in cheese_particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                cheese_particles.remove(p)
                
        for p in trap_particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                trap_particles.remove(p)
        
        # Draw everything
        draw_kitchen_background(screen)
        
        # Draw title
        draw_title(screen)
        
        # Draw enhanced scoreboard (now with better coverage)
        draw_scoreboard(screen, wins, losses)
        
        # Draw enhanced pixel art
        draw_pixel_art(screen, rat_position, game_over, win)
        
        # Draw path and rat position
        draw_path(screen, rat_position)
        
        # Draw word
        draw_word(screen, current_word, guessed_letters)
        
        # Draw letter grid
        draw_letters(screen, guessed_letters, correct_letters, incorrect_letters)
        
        # Draw particles
        for p in cheese_particles:
            pygame.draw.circle(screen, CHEESE_COLOR, (int(p['x']), int(p['y'])), 3)
            
        for p in trap_particles:
            pygame.draw.circle(screen, TRAP_COLOR, (int(p['x']), int(p['y'])), 3)
        
        # Draw game status
        if game_over:
            # Draw result background
            result_bg = pygame.Rect(WIDTH//2 - 200, WORD_Y - 80, 400, 100)
            pygame.draw.rect(screen, (50, 45, 70, 200), result_bg, border_radius=15)
            pygame.draw.rect(screen, ACCENT if win else TRAP_COLOR, result_bg, 3, border_radius=15)
            
            status_text = "YOU WIN! CHEESE ACQUIRED!" if win else "YOU LOSE! TRAPPED!"
            status_color = CORRECT_COLOR if win else INCORRECT_COLOR
            status_surf = score_font.render(status_text, True, status_color)
            status_rect = status_surf.get_rect(center=(WIDTH//2, WORD_Y - 50))
            screen.blit(status_surf, status_rect)
            
            # Show the full word
            word_surf = word_font.render(f"Word: {current_word}", True, TEXT_COLOR)
            word_rect = word_surf.get_rect(center=(WIDTH//2, WORD_Y - 10))
            screen.blit(word_surf, word_rect)
        
        # Draw restart button (now positioned at bottom)
        restart_button.draw(screen)
        exit_button.draw(screen)
        
        # Draw instructions
        if not game_over:
            inst_text = "Guess letters to move the rat toward the CHEESE!"
            inst_surf = button_font.render(inst_text, True, TEXT_COLOR)
            inst_rect = inst_surf.get_rect(center=(WIDTH//2, RESTART_BUTTON_Y - 30))
            screen.blit(inst_surf, inst_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()