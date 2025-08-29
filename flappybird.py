import pygame
import pyrebase
import random
import time

# Firebase configuration and initialization
firebaseConfig = {
    'apiKey': "AIzaSyDJFGpxt4NhJw_BICivqq9e84_VryR6vZk",
    'authDomain': "dinojump-5972c.firebaseapp.com",
    'databaseURL': "https://dinojump-5972c-default-rtdb.firebaseio.com",
    'projectId': "dinojump-5972c",
    'storageBucket': "dinojump-5972c.firebasestorage.app",
    'messagingSenderId': "373596765004",
    'appId': "1:373596765004:web:d375398c1269a677662de9"
}


firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Pygame initialization
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 70
BIRD_WIDTH, BIRD_HEIGHT = 20, 20
PIPE_WIDTH = 10
PIPE_GAP = 300
PIPE_VELOCITY = 5
GRAVITY = 1
BIRD_JUMP_VELOCITY = -10
FPS = 20
COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "sky_blue": (135, 206, 235),
    "ground_green": (156, 204, 101),
    "pipe_green": (0, 255, 0)
}

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird with Firebase")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Game variables
bird = {"x": 50, "y": SCREEN_HEIGHT // 2, "velocity_y": 0}
pipes = [{"x": SCREEN_WIDTH, "y": random.randint(100, SCREEN_HEIGHT - 100)}]
score = 0
game_over = False
running = True

# Firebase cache
firebase_refresh_rate = 0.1  # seconds
last_firebase_fetch = 0
cached_j_value = False  # Initialize the cached value for Data/J

def fetch_j_value():
    """Retrieve and cache the J value from Firebase."""
    global cached_j_value, last_firebase_fetch
    if time.time() - last_firebase_fetch >= firebase_refresh_rate:
        data = db.child('Data').get()
        cached_j_value = data.val().get('J', False)  # Default to False if 'J' is missing
        last_firebase_fetch = time.time()
    return cached_j_value

def draw_bird(bird):
    """Draw the bird."""
    pygame.draw.rect(screen, COLORS["black"], (bird["x"], bird["y"], BIRD_WIDTH, BIRD_HEIGHT))

def draw_pipes():
    """Draw the pipes."""
    for pipe in pipes:
        pygame.draw.rect(screen, COLORS["pipe_green"], (pipe["x"], 0, PIPE_WIDTH, pipe["y"]))
        pygame.draw.rect(screen, COLORS["pipe_green"], (pipe["x"], pipe["y"] + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - pipe["y"] - PIPE_GAP))

def draw_ground():
    """Draw the ground."""
    pygame.draw.rect(screen, COLORS["ground_green"], (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

def draw_game_over():
    """Display the Game Over screen."""
    game_over_text = large_font.render("Game Over", True, COLORS["black"])
    play_again_text = font.render("Press R to Restart or Q to Quit", True, COLORS["black"])
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - play_again_text.get_width() // 2, SCREEN_HEIGHT // 2))

def reset_game():
    """Reset the game state."""
    global bird, pipes, score, game_over
    bird.update({"y": SCREEN_HEIGHT // 2, "velocity_y": 0})
    pipes = [{"x": SCREEN_WIDTH, "y": random.randint(100, SCREEN_HEIGHT - 100)}]
    score = 0
    game_over = False

def handle_events():
    """Handle Pygame events."""
    global running, game_over
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_q:
                running = False

def update_bird():
    """Update the bird's position and jump logic."""
    global bird
    j_value = fetch_j_value()
    if j_value and bird["y"] >= 0:  # Jump trigger if Data/J is True
        bird["velocity_y"] = BIRD_JUMP_VELOCITY

    bird["velocity_y"] += GRAVITY
    bird["y"] += bird["velocity_y"]

    if bird["y"] >= SCREEN_HEIGHT - GROUND_HEIGHT - BIRD_HEIGHT:
        bird["y"] = SCREEN_HEIGHT - GROUND_HEIGHT - BIRD_HEIGHT
        bird["velocity_y"] = 0
        global game_over
        game_over = True

def update_pipes():
    """Update pipe positions and spawn new ones."""
    global pipes, score, game_over

    for pipe in pipes:
        pipe["x"] -= PIPE_VELOCITY

    if pipes and pipes[0]["x"] < -PIPE_WIDTH:
        pipes.pop(0)
        score += 1

    if not pipes or pipes[-1]["x"] < SCREEN_WIDTH - random.randint(200, 300):
        pipes.append({"x": SCREEN_WIDTH, "y": random.randint(100, SCREEN_HEIGHT - 100)})

    # Collision detection
    for pipe in pipes:
        if (bird["x"] + BIRD_WIDTH > pipe["x"] and bird["x"] < pipe["x"] + PIPE_WIDTH and
            (bird["y"] < pipe["y"] or bird["y"] + BIRD_HEIGHT > pipe["y"] + PIPE_GAP)):
            game_over = True

# Main game loop
while running:
    handle_events()

    if game_over:
        screen.fill(COLORS["white"])
        draw_game_over()
    else:
        screen.fill(COLORS["sky_blue"])
        draw_ground()

        update_bird()
        update_pipes()
        draw_bird(bird)
        draw_pipes()

        score_text = font.render(f"Score: {score}", True, COLORS["black"])
        screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
