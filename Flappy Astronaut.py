# Import necessary modules
from sense_hat import SenseHat  # For controlling the Sense HAT hardware
from random import randint  # To generate random numbers for pipe gaps and bonuses
from time import sleep, time  # To manage timing and calculate elapsed time

# Initialize Sense HAT and define colors
sense = SenseHat()
RED = (255, 0, 0)       # Color for pipes
BLUE = (0, 0, 255)      # Background color
YELLOW = (255, 255, 0)  # Color for the astronaut
WHITE = (255, 255, 255) # Text color
GREEN = (0, 255, 0)     # Bonus points color

# Initial astronaut position and game variables
x, y = 0, 0             # Astronaut starts at the top-left corner
game_over = False       # Flag to indicate the game state
start_time = time()     # Record start time for score calculation
score = 0               # Initialize player score
bonus_active = False    # Tracks if a bonus point is active

# Create an 8x8 matrix to represent the screen
matrix = [[BLUE for column in range(8)] for row in range(8)]

def flatten(matrix):
    """
    Converts the 2D matrix into a single list for the Sense HAT display.
    This is required because Sense HAT uses a flattened list for its LED grid.
    """
    return [pixel for row in matrix for pixel in row]

def gen_pipes(matrix):
    """
    Generates new pipes with a random gap and possible bonus points.
    Pipes are created in the rightmost column and bonus points are added randomly.
    """
    # Set all rightmost column pixels to RED (pipe)
    for row in matrix:
        row[-1] = RED
    
    # Create a random gap in the pipe
    gap = randint(1, 6)
    matrix[gap][-1] = BLUE
    matrix[gap - 1][-1] = BLUE
    matrix[gap + 1][-1] = BLUE

    # Randomly add bonus points (GREEN) in the last 4 columns
    for _ in range(randint(0, 2)):  # Add 0 to 2 bonus points
        bonus_row = randint(0, 7)
        bonus_col = randint(4, 7)  # Bonus only in the rightmost 4 columns
        if matrix[bonus_row][bonus_col] == BLUE:  # Avoid overwriting pipes
            matrix[bonus_row][bonus_col] = GREEN
    return matrix

def move_pipes(matrix):
    """
    Moves all pipe columns one step to the left.
    The leftmost column is overwritten, and the rightmost column is reset.
    """
    for row in matrix:
        for i in range(7):
            row[i] = row[i + 1]
        row[-1] = BLUE  # Reset the rightmost column
    return matrix

def draw_astronaut(event):
    """
    Handles joystick input to move the astronaut. 
    Checks for collisions and bonuses at the new position.
    """
    global y, x, game_over, score, bonus_active

    if game_over:  # Ignore input if the game is over
        return

    # Clear the astronaut's previous position
    sense.set_pixel(x, y, BLUE)

    # Update position based on joystick input
    if event.action == "pressed":
        if event.direction == "up" and y > 0:
            y -= 1
        elif event.direction == "down" and y < 7:
            y += 1
        elif event.direction == "right" and x < 7:
            x += 1
        elif event.direction == "left" and x > 0:
            x -= 1

    # Check for collisions or bonuses
    if matrix[y][x] == RED:  # Collision with pipe
        game_over = True
    elif matrix[y][x] == GREEN:  # Collect bonus
        score += 5

    # Draw the astronaut at the new position
    sense.set_pixel(x, y, YELLOW)

def check_collision(matrix):
    """
    Checks if the astronaut's current position collides with a pipe.
    """
    return matrix[y][x] == RED

def display_game_over():
    """
    Displays the 'Game Over' message and the final score.
    """
    elapsed_time = int(time() - start_time)  # Calculate time survived
    total_score = elapsed_time + score  # Combine time and bonuses for the score
    sense.clear()  # Clear the screen
    sense.show_message('Game Over! Score: {}'.format(total_score), text_colour=WHITE, scroll_speed=0.1)

def custom_start_screen():
    """
    Displays a custom start screen animation before the game begins.
    """
    sense.clear(BLUE)  # Fill the screen with the background color
    sleep(0.5)
    # Draw lines on the screen
    for i in range(8):
        sense.set_pixel(i, 3, WHITE)
        sense.set_pixel(i, 4, WHITE)
        sleep(0.1)
    sleep(0.5)
    # Display "Ready?" message
    sense.show_message("Ready?", text_colour=YELLOW, scroll_speed=0.1)
    sense.clear()

# Bind joystick events to the astronaut movement function
sense.stick.direction_any = draw_astronaut

# Display the start screen
custom_start_screen()

# Main game loop
while not game_over:
    elapsed_time = int(time() - start_time)

    # Generate pipes
    matrix = gen_pipes(matrix)
    if check_collision(matrix):  # Check for immediate collision
        game_over = True
        break

    # Move pipes across the screen
    for _ in range(3):
        matrix = move_pipes(matrix)
        sense.set_pixels(flatten(matrix))  # Update the screen
        sense.set_pixel(x, y, YELLOW)  # Draw the astronaut

        if check_collision(matrix):  # Check for collision during movement
            game_over = True
            break

        # Adjust game speed dynamically
        sleep_time = max(0.1, 0.5 - (elapsed_time * 0.01))
        sleep(sleep_time)

# Display game over screen when the loop ends
if game_over:
    display_game_over()
