import pygame
import time
import random
import os
from datetime import datetime

# Initialize pygame
pygame.init()

# ... your other setup code ...

# Load game background once


# Constants
window_x = 720
window_y = 480
header_height = 60
game_area = pygame.Rect(20, header_height + 10, window_x - 40, window_y - header_height - 30)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
# Poison spawn positions: Left, Top, Right (cyclic)
blue_spawn_positions = [
    [game_area.left + 20, random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10],  # Left
    [random.randint(game_area.left // 10, (game_area.right - 10) // 10) * 10, game_area.top + 20],    # Top
    [game_area.right - 20, random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10],  # Right
]
blue_spawn_index = 0

yellow = pygame.Color(255, 255, 0)
grey = pygame.Color(128, 128, 128)
# Load and prepare the gameplay area background image
def load_game_background():
    try:
        bg = pygame.image.load("playing.jpeg")  # Replace with your image filename
        bg = pygame.transform.scale(bg, (game_area.width, game_area.height))
        return bg
    except pygame.error as e:
        print(f"Failed to load background image: {e}")
        return None
game_bg_image = load_game_background()

# Files
high_score_file = "highscore.txt"
history_file = "history.txt"
scoreboard_file = "highscores.txt"

# Setup display
pygame.display.set_caption('Snake Game')
game_window = pygame.display.set_mode((window_x, window_y), pygame.RESIZABLE)
fps = pygame.time.Clock()

player_name = ""  # Global player name

# ========================== UTIL FUNCTIONS ==========================

def get_player_name():
    name = ""
    # Load and scale the background image
    try:
        bg_image = pygame.image.load("name.jpeg")
        bg_image = pygame.transform.scale(bg_image, (window_x, window_y))
    except pygame.error:
        bg_image = None

    # Fonts with bold
    title_font = pygame.font.SysFont('times new roman', 40, bold=True)
    input_font = pygame.font.SysFont('times new roman', 32, bold=True)
    message_font = pygame.font.SysFont('times new roman', 28, bold=True)

    while True:
        # Draw background
        if bg_image:
            game_window.blit(bg_image, (0, 0))
            # Dark overlay to improve text visibility
            overlay = pygame.Surface((window_x, window_y))
            overlay.set_alpha(150)  # Transparency: 0 (invisible) to 255 (opaque)
            overlay.fill((0, 0, 0))  # Black overlay
            game_window.blit(overlay, (0, 0))
        else:
            game_window.fill(black)

        # "All the Best!" at top
        all_best = title_font.render("All the Best!", True, yellow)
        game_window.blit(all_best, all_best.get_rect(center=(window_x // 2, window_y // 2 - 120)))

        # "Enter your name: ____" in the center
        prompt = input_font.render("Enter your name: " + name, True, white)
        game_window.blit(prompt, prompt.get_rect(center=(window_x // 2, window_y // 2)))

        # "Press ENTER to Start the Game" below the name prompt
        enter_msg = message_font.render("Press ENTER to Start the Game", True, green)
        game_window.blit(enter_msg, enter_msg.get_rect(center=(window_x // 2, window_y // 2 + 50)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 15 and event.unicode.isprintable():
                    name += event.unicode


def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as f:
            return int(f.read())
    return 0

def save_high_score(score):
    high = load_high_score()
    if score > high:
        with open(high_score_file, "w") as f:
            f.write(str(score))

def save_history(score, duration, difficulty):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_file, "a") as f:
        f.write(f"{now} | Name: {player_name} | Score: {score} | Time: {duration}s | Difficulty: {difficulty}\n")

def load_history():
    if not os.path.exists(history_file):
        return []
    with open(history_file, "r") as f:
        lines = f.readlines()
        return lines[::-1]  # Reverse to show most recent first, no limit

def save_top_scores(name, score):
    scores = load_top_scores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:5]
    with open(scoreboard_file, "w") as f:
        for entry in scores:
            f.write(f"{entry[0]}|{entry[1]}\n")

def load_top_scores():
    if not os.path.exists(scoreboard_file):
        return []
    with open(scoreboard_file, "r") as f:
        return [(line.split("|")[0], int(line.split("|")[1])) for line in f if "|" in line]

# ========================== DISPLAY SCREENS ==========================
def show_score(score, color, font_name, size):
    font = pygame.font.SysFont(font_name, size)
    score_surface = font.render(f'Score : {score}', True, color)
    score_rect = score_surface.get_rect(topleft=(30, header_height + 10))
    game_window.blit(score_surface, score_rect)


def display_history_screen():
    history = load_history()  # Returns list of strings (lines)
    font = pygame.font.SysFont('times new roman', 18)
    title_font = pygame.font.SysFont('times new roman', 22)
    max_lines_on_screen = 15
    scroll_pos = 0

    while True:
        game_window.fill(black)

        # Title / Instruction
        title_surface = title_font.render("Game History (↑/↓ to scroll, BACKSPACE to return)", True, yellow)
        game_window.blit(title_surface, (40, 20))

        if not history:
            game_window.blit(font.render("No history found.", True, white), (60, 100))
        else:
            visible_lines = history[scroll_pos:scroll_pos + max_lines_on_screen]
            for i, line in enumerate(visible_lines):
                game_window.blit(font.render(line.strip(), True, white), (40, 60 + i * 25))

        pygame.display.update()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and scroll_pos > 0:
                    scroll_pos -= 1
                elif event.key == pygame.K_DOWN and scroll_pos + max_lines_on_screen < len(history):
                    scroll_pos += 1
                elif event.key == pygame.K_BACKSPACE:
                    return  # Go back to menu

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # Mouse click no longer exits

def display_top_scores():
    scores = load_top_scores()
    font = pygame.font.SysFont('times new roman', 30)
    game_window.fill(black)
    game_window.blit(font.render("Top 5 High Scores", True, yellow), (window_x // 2 - 150, 50))

    if not scores:
        game_window.blit(font.render("No scores available.", True, white), (window_x // 2 - 120, 150))
    else:
        for i, (name, score) in enumerate(scores):
            game_window.blit(font.render(f"{i+1}. {name} - {score}", True, white), (100, 120 + i * 40))

    game_window.blit(font.render("Click or Press any key to return", True, green), (100, 400))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                return

def display_help_screen():
    help_font = pygame.font.SysFont('times new roman', 28)
    help_lines = [
        "How to Play:",
        "- Use Arrow keys to move the snake",
        "- Eat white food (+10 points)",
        "- Eat yellow bonus food (+30 points)",
        "- Avoid walls and yourself",
        "- Press 'P' to pause and 'R' to restart",
        "- Press 'Q' to quit the game"
    ]
    game_window.fill(black)
    game_window.blit(help_font.render("Instructions", True, green), (window_x // 2 - 80, 40))
    for i, line in enumerate(help_lines):
        game_window.blit(help_font.render(line, True, white), (80, 100 + i * 40))
    game_window.blit(help_font.render("Click anywhere or press any key to go back", True, yellow), (80, 400))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                return
def display_screen():
    levels = ['Easy', 'Medium', 'Hard']
    selected = 1
    font = pygame.font.SysFont('times new roman', 32)
    title_font = pygame.font.SysFont('times new roman', 50)
    hist_font = pygame.font.SysFont('times new roman', 24)

    # Load background and snake image safely
    try:
        background_img = pygame.image.load("assetsbackground.jpeg")
    except:
        background_img = None

    try:
        snake_img = pygame.image.load("snake.png")  # Replace with your snake image path
    except:
        snake_img = None

    while True:
        current_width = game_window.get_width()
        current_height = game_window.get_height()

        # Draw and scale background
        if background_img:
            scaled_bg = pygame.transform.scale(background_img, (current_width, current_height))
            game_window.blit(scaled_bg, (0, 0))
        else:
            game_window.fill((0, 0, 0))

        # Overlay semi-transparent dark box
        overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        game_window.blit(overlay, (0, 0))

        # Title
        game_window.blit(title_font.render("Welcome to Snake Game", True, (255, 255, 0)), (current_width // 2 - 230, 60))

        # Help icon
        pygame.draw.circle(game_window, (255, 255, 255), (current_width - 40, 40), 15)
        q_mark = pygame.font.SysFont(None, 24).render("?", True, (0, 0, 0))
        game_window.blit(q_mark, (current_width - 46, 28))

        # Start Instruction
        game_window.blit(font.render("Press ENTER to Start the Game", True, (255, 255, 255)), (current_width // 2 - 200, 140))

        # Difficulty Label
        difficulty_label_y = 200
        game_window.blit(font.render("Select Difficulty:", True, (255, 255, 255)), (current_width // 2 - 120, difficulty_label_y))

        # Difficulty Options
        for i, level in enumerate(levels):
            color = (0, 255, 0) if i == selected else (255, 255, 255)
            difficulty_surface = font.render(level, True, color)
            difficulty_rect = difficulty_surface.get_rect(topleft=(current_width // 2 + 80, difficulty_label_y + 50 + i * 40))
            game_window.blit(difficulty_surface, difficulty_rect)

        # View History Button
        hist_surf = hist_font.render("View History", True, (0, 128, 255))
        hist_rect = hist_surf.get_rect(topleft=(50, current_height - 40))
        game_window.blit(hist_surf, hist_rect)

        # View Top Scores Button
        high_surf = hist_font.render("View Highest Scores", True, (255, 255, 0))
        high_rect = high_surf.get_rect(bottomright=(current_width - 50, current_height - 20))
        game_window.blit(high_surf, high_rect)

        # Draw snake image
        if snake_img:
            game_window.blit(snake_img, (30, current_height - 130))

        pygame.display.update()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return levels[selected]
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(levels)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(levels)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Help icon
                if (current_width - 55) <= mx <= (current_width - 25) and 25 <= my <= 55:
                    display_help_screen()

                # History button
                elif hist_rect.collidepoint(mx, my):
                    display_history_screen()

                # Top scores button
                elif high_rect.collidepoint(mx, my):
                    display_top_scores()

                # Difficulty click
                for i, level in enumerate(levels):
                    rect_y = difficulty_label_y + 50 + i * 40
                    diff_rect = pygame.Rect(current_width // 2 + 80, rect_y, 150, 30)
                    if diff_rect.collidepoint(mx, my):
                        selected = i
def show_header(score, high_score, start_time, color, font, size):
    current_time = int(time.time() - start_time)
    score_font = pygame.font.SysFont(font, size)
    text = f"Score: {score}   High Score: {high_score}   Time: {current_time}s"
    score_surface = score_font.render(text, True, color)
    score_rect = score_surface.get_rect(center=(window_x / 2, header_height // 2))
    pygame.draw.rect(game_window, grey, (10, 10, window_x - 20, header_height), border_radius=8)
    game_window.blit(score_surface, score_rect)

def reset_game():
    return (
        [game_area.left + 20, game_area.top + 20],
        [[game_area.left + 20, game_area.top + 20]],
        [random.randint(game_area.left // 10, (game_area.right - 10) // 10) * 10,
         random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10],
        True,
        None,
        0, 0,
        time.time(),
        'RIGHT', 'RIGHT',
        0,
        time.time(),
        False
    )

def game_over_screen(score, duration, difficulty):
    global show_menu

    # Load and scale background image
    try:
        bg_image = pygame.image.load("assetsover.jpeg")
        bg_image = pygame.transform.scale(bg_image, (window_x, window_y))
    except:
        bg_image = None

    while True:
        # Draw background
        if bg_image:
            game_window.blit(bg_image, (0, 0))
        else:
            game_window.fill(black)

        # 🔲 Draw a semi-transparent black overlay (makes text readable)
        overlay = pygame.Surface((window_x, window_y), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # RGBA (last value is opacity)
        game_window.blit(overlay, (0, 0))

        # Bold fonts
        game_over_font = pygame.font.SysFont('times new roman', 50, bold=True)
        score_font = pygame.font.SysFont('times new roman', 30, bold=True)

        # Text surfaces
        game_over_surface = game_over_font.render('Game Over!', True, red)
        final_score_surface = score_font.render(f'Final Score: {score}', True, white)
        time_surface = score_font.render(f'Time Survived: {duration} sec', True, white)
        continue_surface = score_font.render("Press ENTER to Restart | M for Menu | Q to Quit", True, yellow)

        # Blit text
        game_window.blit(game_over_surface, game_over_surface.get_rect(center=(window_x / 2, window_y / 2 - 60)))
        game_window.blit(final_score_surface, final_score_surface.get_rect(center=(window_x / 2, window_y / 2 - 20)))
        game_window.blit(time_surface, time_surface.get_rect(center=(window_x / 2, window_y / 2 + 20)))
        game_window.blit(continue_surface, continue_surface.get_rect(center=(window_x / 2, window_y / 2 + 60)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    show_menu = False
                    return
                elif event.key == pygame.K_m:
                    show_menu = True
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

# Blue fruit initialization
blue_fruit_pos = [0, 0]
blue_fruit_active = False
blue_fruit_timer = 0
blue_fruit_duration = 5
last_blue_spawn_time = time.time()



show_menu = True
paused=False
while True:
    if show_menu:
        difficulty = display_screen()
        snake_speed = {'Easy': 10, 'Medium': 15, 'Hard': 20}[difficulty]
        player_name = get_player_name()
        show_menu = False
    chances = 2 # You get 2 extra chances

    # Game Initialization
    snake_pos = [window_x // 2, window_y // 2]
    snake_body = [list(snake_pos)]
    direction = 'RIGHT'
    change_to = direction
    score = 0
    fruit_pos = [random.randint(game_area.left // 10, (game_area.right - 10) // 10) * 10,
                 random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10]
    fruit_spawn = True
    start_time = time.time()
    game_over = False

    # Bonus food
    bonus_fruit_pos = [random.randint(game_area.left // 10, (game_area.right - 10) // 10) * 10,
                       random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10]
    bonus_fruit_active = False
    bonus_fruit_timer = 0
    bonus_fruit_duration = 5
    last_bonus_spawn_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w] and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key in [pygame.K_DOWN, pygame.K_s] and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key in [pygame.K_LEFT, pygame.K_a] and direction != 'RIGHT':
                    change_to = 'LEFT'
                elif event.key in [pygame.K_RIGHT, pygame.K_d] and direction != 'LEFT':
                    change_to = 'RIGHT'
                elif event.key == pygame.K_p:
                    paused = True
                elif event.key == pygame.K_r:
                    paused = False
        if paused:
            pause_font = pygame.font.SysFont('times new roman', 40)
            pause_text = pause_font.render("Game Paused - Press R to Resume", True, yellow)
            game_window.blit(pause_text, pause_text.get_rect(center=(window_x // 2, window_y // 2)))
            pygame.display.update()
            continue  # Skip the rest of the loop while paused

        direction = change_to
        if direction == 'UP':
            snake_pos[1] -= 10
        elif direction == 'DOWN':
            snake_pos[1] += 10
        elif direction == 'LEFT':
            snake_pos[0] -= 10
        elif direction == 'RIGHT':
            snake_pos[0] += 10

        snake_body.insert(0, list(snake_pos))
        if snake_pos == fruit_pos:
            score += 10
            fruit_spawn = False
        elif bonus_fruit_active and snake_pos == bonus_fruit_pos:
            score += 30
            bonus_fruit_active = False
        elif blue_fruit_active and snake_pos == blue_fruit_pos:
            game_over = True  # Immediate end if blue fruit eaten
            break
        else:
            snake_body.pop()

        if not fruit_spawn:
            fruit_pos = [random.randint(game_area.left // 10, (game_area.right - 10) // 10) * 10,
                         random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10]
        fruit_spawn = True

        # Timer logic
        current_time = time.time()

        # Bonus food timer logic
        if not bonus_fruit_active and (current_time - last_bonus_spawn_time) >= 15:
            bonus_fruit_active = True
            bonus_fruit_timer = current_time
            last_bonus_spawn_time = current_time
            bonus_fruit_pos = [random.randint(game_area.left // 10, (game_area.right - 10) // 10) * 10,
                               random.randint(game_area.top // 10, (game_area.bottom - 10) // 10) * 10]

        if bonus_fruit_active and (current_time - bonus_fruit_timer > bonus_fruit_duration):
            bonus_fruit_active = False

        # Blue fruit logic
        if score > 50:
            if not blue_fruit_active and (current_time - last_blue_spawn_time >= 20):
                blue_fruit_active = True
                blue_fruit_timer = current_time
                last_blue_spawn_time = current_time
                blue_fruit_pos = blue_spawn_positions[blue_spawn_index % 3]
                blue_spawn_index += 1
        if blue_fruit_active and (current_time - blue_fruit_timer > blue_fruit_duration):
            blue_fruit_active = False

        game_window.fill(black)
        if game_bg_image:
            game_window.blit(game_bg_image, (game_area.left, game_area.top))
        pygame.draw.rect(game_window, white, game_area, 3)
        # === Change snake color based on score ===
        if score >= 100:
            snake_color = pygame.Color(255, 0, 255)  # Purple
        elif score >= 50:
            snake_color = pygame.Color(0, 255, 255)  # Cyan
        else:
            snake_color = green
        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

        pygame.draw.rect(game_window, red, pygame.Rect(fruit_pos[0], fruit_pos[1], 10, 10))

        if bonus_fruit_active:
            pygame.draw.rect(game_window, yellow, pygame.Rect(bonus_fruit_pos[0], bonus_fruit_pos[1], 10, 10))
            bonus_time_left = max(0, int(bonus_fruit_duration - (current_time - bonus_fruit_timer)))
            bonus_font = pygame.font.SysFont('times new roman', 20)
            timer_surface = bonus_font.render(f"Bonus: {bonus_time_left}s", True, yellow)
            game_window.blit(timer_surface, (game_area.right - 110, game_area.top + 5))

        if blue_fruit_active:
            pygame.draw.circle(game_window, blue, (blue_fruit_pos[0] + 5, blue_fruit_pos[1] + 5), 5)
            blue_time_left = max(0, int(blue_fruit_duration - (current_time - blue_fruit_timer)))
            blue_font = pygame.font.SysFont('times new roman', 20)
            blue_timer_surface = blue_font.render(f"Possion: {blue_time_left}s", True, blue)
            game_window.blit(blue_timer_surface, (game_area.left + 10, game_area.top + 10))
            danger_font = pygame.font.SysFont('times new roman', 16, bold=True)
            danger_text = danger_font.render("DANGER!", True, red)
            game_window.blit(danger_text, (blue_fruit_pos[0] - 5, blue_fruit_pos[1] - 20))
        show_header(score, load_high_score(), start_time, white, 'times new roman', 20)
        pygame.display.update()
        fps.tick(snake_speed)

        if (snake_pos[0] < game_area.left or snake_pos[0] > game_area.right - 10 or
            snake_pos[1] < game_area.top or snake_pos[1] > game_area.bottom - 10):

            if chances > 0:
                asking = True
                try:
                    crash_bg = pygame.image.load("crash.jpeg")
                    crash_bg = pygame.transform.scale(crash_bg, (window_x, window_y))
                except:
                    crash_bg = None
                while asking:
                    if crash_bg:
                        game_window.blit(crash_bg, (0, 0))
                        overlay = pygame.Surface((window_x, window_y), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 140))  # Semi-transparent
                        game_window.blit(overlay, (0, 0))
                    else:
                        game_window.fill(black)
                    #pygame.draw.rect(game_window, white, game_area, 3)

                    font = pygame.font.SysFont('times new roman', 36)
                    msg = font.render(f"You crashed! Use a chance? ({chances} left)", True, white)
                    sub_msg = font.render("Press Y to use, N to quit", True, white)
                    game_window.blit(msg, msg.get_rect(center=(window_x/2, window_y/2 - 20)))
                    game_window.blit(sub_msg, sub_msg.get_rect(center=(window_x/2, window_y/2 + 30)))

                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_y:
                                chances -= 1
                                snake_pos = [window_x // 2, window_y // 2]
                                snake_body = [list(snake_pos)]
                                direction = 'RIGHT'
                                change_to = 'RIGHT'
                                score = max(0, score - 5)
                                fruit_spawn = True
                                asking = False
                            elif event.key == pygame.K_n:
                                game_over = True
                                asking = False
                if game_over:
                    break
            else:
                game_over = True
                break

        for block in snake_body[1:]:
            if snake_pos == block:
                game_over = True
                break

        if game_over:
            break

    if game_over:
        duration = int(time.time() - start_time)
        save_history(score, duration, difficulty)
        save_high_score(score)
        save_top_scores(player_name, score)  
        game_over_screen(score, duration, difficulty)
        continue
