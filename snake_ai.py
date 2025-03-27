import pygame
import random
import heapq  # For A* algorithm
import sys

pygame.init()
pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # Snake moves in grid steps

gameWindow = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)

# Load sounds
pygame.mixer.music.load("nagin.mp3")  # Background music
beep_sound = pygame.mixer.Sound("beep.mp3")  # Sound when eating food
gameover_sound = pygame.mixer.Sound("gameover.mp3")  # Game over sound

pygame.mixer.music.play(-1)  # Play nagin music in loop

# Initialize high score
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

def text_screen(text, color, x, y):
    screen_text = font.render(text, True, color)
    gameWindow.blit(screen_text, [x, y])

def plot_snake(snk_list, size):
    for x, y in snk_list:
        pygame.draw.rect(gameWindow, BLACK, [x, y, size, size])

def heuristic(a, b):
    """Heuristic function for A* (Manhattan Distance)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_pathfinding(start, goal, snake_body):
    """A* algorithm to find the shortest path to food avoiding the snake's body."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    directions = [(0, -GRID_SIZE), (0, GRID_SIZE), (-GRID_SIZE, 0), (GRID_SIZE, 0)]

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in snake_body or not (0 <= neighbor[0] < SCREEN_WIDTH and 0 <= neighbor[1] < SCREEN_HEIGHT):
                continue

            temp_g_score = g_score[current] + 1
            if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def game_loop():
    global high_score

    exit_game = False
    game_over = False
    snake_x, snake_y = 100, 100
    snake_list = [(snake_x, snake_y)]
    snake_length = 3
    food_x = random.randrange(0, SCREEN_WIDTH, GRID_SIZE)
    food_y = random.randrange(0, SCREEN_HEIGHT, GRID_SIZE)
    score = 0  # Initialize score

    # Load the background image
    bgimg = pygame.image.load("back.jpg")  # Ensure the file is in the same folder
    bgimg = pygame.transform.scale(bgimg, (800, 600)).convert()

    while not exit_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Detect window close event
                pygame.quit()
                sys.exit()  # Force exit properly

        gameWindow.blit(bgimg, (0, 0))

        if game_over:
            pygame.mixer.music.stop()
            gameover_sound.play()
            gameWindow.fill(WHITE)
            text_screen("Game Over! Press ENTER to Restart or ESC to Quit", RED, 150, 250)
            text_screen(f"Score: {score}  High Score: {high_score}", BLUE, 280, 300)
            pygame.display.update()

            with open("highscore.txt", "w") as f:
                f.write(str(high_score))

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return  # Restart the game loop
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
        else:
            # Display Score and High Score
            text_screen(f"Score: {score}  High Score: {high_score}", BLUE, 10, 10)

            pygame.draw.rect(gameWindow, BLUE, [food_x, food_y, GRID_SIZE, GRID_SIZE])

            # AI Pathfinding
            path = a_star_pathfinding(snake_list[-1], (food_x, food_y), set(snake_list))
            if path:
                next_move = path[0]
                snake_x, snake_y = next_move
            else:
                game_over = True
                pygame.mixer.music.load('end.mp3')
                pygame.mixer.music.play()
                pygame.time.delay(1500)
                exit_game = True  # No valid path means AI is stuck

            snake_list.append((snake_x, snake_y))
            if len(snake_list) > snake_length:
                del snake_list[0]

            # Collision detection
            if (snake_x, snake_y) in snake_list[:-1]:
                game_over = True
            if snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT:
                game_over = True

            # Check if food is eaten
            if snake_x == food_x and snake_y == food_y:
                beep_sound.play()
                score += 10  # Increase score
                snake_length += 1
                food_x = random.randrange(0, SCREEN_WIDTH, GRID_SIZE)
                food_y = random.randrange(0, SCREEN_HEIGHT, GRID_SIZE)

                if score > high_score:  # Update high score
                    high_score = score

            plot_snake(snake_list, GRID_SIZE)

        pygame.display.update()
        clock.tick(10)  # Controls snake speed

    pygame.quit()
    sys.exit()

game_loop()