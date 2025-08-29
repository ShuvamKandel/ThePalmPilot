import pygame
import random
import pyrebase
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

# Initialize pygame
pygame.init()

# Set display width and height
dis_width = 600
dis_height = 400
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Firebase Controlled Snake')

# Set clock
clock = pygame.time.Clock()

# Define snake parameters
snake_block = 10
initial_speed = 15  # Initial speed
speed_increment = 1  # Speed increment after eating food

# Snake color
black = (0, 0, 0)
green = (0, 255, 0)

# Firebase data retrieval function
def get_firebase_data():
    data = db.child('Data').get()
    X = data.val()['X']
    Y = data.val()['Y']
    return X, Y

# Main game function
def gameLoop():
    x = dis_width / 2
    y = dis_height / 2

    snake_list = []
    length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    game_over = False
    snake_speed = initial_speed

    while not game_over:
        # Get the X and Y values from Firebase
        X, Y = get_firebase_data()

        # Determine snake direction based on thresholds
        x_change = 0
        y_change = 0

        if X < 50:
            x_change = -snake_block  # Move left
        elif X > 150:
            x_change = snake_block   # Move right

        if Y < 70:
            y_change = -snake_block  # Move up
        elif Y > 200:
            y_change = snake_block   # Move down

        # Update snake position
        x += x_change
        y += y_change

        # Boundary check to quit game if snake hits edge
        if x >= dis_width or x < 0 or y >= dis_height or y < 0:
            game_over = True

        # Update display
        dis.fill((255, 255, 255))
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check if snake collides with itself
        for block in snake_list[:-1]:
            if block == snake_head:
                game_over = True

        for block in snake_list:
            pygame.draw.rect(dis, black, [block[0], block[1], snake_block, snake_block])

        pygame.display.update()

        # Snake eats food
        if x == foodx and y == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            length_of_snake += 1
            snake_speed += speed_increment  # Increase speed after eating food

        # Control speed
        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()
