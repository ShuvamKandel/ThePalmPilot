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
SCREEN_WIDTH = 1260
SCREEN_HEIGHT = 800
GROUND_HEIGHT = 70
DINO_WIDTH, DINO_HEIGHT = 40, 40
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 20, 30
COLORS = {
    "white": (245, 245, 245),
    "black": (33, 33, 33),
    "gray": (160, 160, 160),
    "red": (220, 38, 38),
    "sky_blue": (186, 228, 248),
    "ground_green": (156, 204, 101),
}

FPS = 30
GRAVITY = 2
DINO_JUMP_VELOCITY = -15
OBSTACLE_SPEED = 15
MIN_OBSTACLE_GAP = 10 * DINO_WIDTH

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Firebase-Controlled Dinosaur Game")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Dino and obstacles
dino = {"x": 50, "y": SCREEN_HEIGHT - DINO_HEIGHT - GROUND_HEIGHT, "velocity_y": 0, "is_jumping": False}
obstacles = [{"x": SCREEN_WIDTH, "y": SCREEN_HEIGHT - OBSTACLE_HEIGHT - GROUND_HEIGHT}]
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

def draw_dino(dino):
    """Draw the dinosaur."""
    pygame.draw.rect(screen, COLORS["black"], (dino["x"] + 10, dino["y"], 30, 40))  # Body
    pygame.draw.rect(screen, COLORS["black"], (dino["x"], dino["y"] + 30, 10, 10))  # Tail
    pygame.draw.rect(screen, COLORS["black"], (dino["x"] + 30, dino["y"] + 10, 10, 10))  # Head

def draw_game_over():
    """Display the Game Over screen."""
    game_over_text = large_font.render("Game Over", True, COLORS["red"])
    play_again_text = font.render("Press R to Restart or Q to Quit", True, COLORS["black"])
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - play_again_text.get_width() // 2, SCREEN_HEIGHT // 2))

def reset_game():
    """Reset the game state."""
    global dino, obstacles, score, game_over
    dino.update({"y": SCREEN_HEIGHT - DINO_HEIGHT - GROUND_HEIGHT, "velocity_y": 0, "is_jumping": False})
    obstacles = [{"x": SCREEN_WIDTH, "y": SCREEN_HEIGHT - OBSTACLE_HEIGHT - GROUND_HEIGHT}]
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

def update_dino():
    """Update the dinosaur's position and jump logic."""
    global dino
    j_value = fetch_j_value()
    if j_value and not dino["is_jumping"]:  # Jump trigger if Data/J is True
        dino["velocity_y"] = DINO_JUMP_VELOCITY
        dino["is_jumping"] = True

    dino["velocity_y"] += GRAVITY
    dino["y"] += dino["velocity_y"]
    if dino["y"] >= SCREEN_HEIGHT - DINO_HEIGHT - GROUND_HEIGHT:
        dino["y"] = SCREEN_HEIGHT - DINO_HEIGHT - GROUND_HEIGHT
        dino["is_jumping"] = False

def update_obstacles():
    """Update obstacle positions and spawn new ones."""
    global obstacles, score, game_over

    for obstacle in obstacles:
        obstacle["x"] -= OBSTACLE_SPEED

    if obstacles and obstacles[0]["x"] < -OBSTACLE_WIDTH:
        obstacles.pop(0)
        score += 1

    if not obstacles or SCREEN_WIDTH - obstacles[-1]["x"] > random.randint(MIN_OBSTACLE_GAP, MIN_OBSTACLE_GAP + 200):
        obstacles.append({"x": SCREEN_WIDTH, "y": SCREEN_HEIGHT - OBSTACLE_HEIGHT - GROUND_HEIGHT})

    # Collision detection
    for obstacle in obstacles:
        if (dino["x"] < obstacle["x"] + OBSTACLE_WIDTH and
            dino["x"] + DINO_WIDTH > obstacle["x"] and
            dino["y"] < obstacle["y"] + OBSTACLE_HEIGHT and
            dino["y"] + DINO_HEIGHT > obstacle["y"]):
            game_over = True

# Main game loop
while running:
    handle_events()

    if game_over:
        screen.fill(COLORS["white"])
        draw_game_over()
    else:
        screen.fill(COLORS["sky_blue"])
        pygame.draw.rect(screen, COLORS["ground_green"], (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        update_dino()
        update_obstacles()
        draw_dino(dino)

        for obstacle in obstacles:
            pygame.draw.rect(screen, COLORS["gray"], (obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

        score_text = font.render(f"Score: {score}", True, COLORS["black"])
        screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
