
import asyncio
import pygame
import random
import math
import json
import os

pygame.init()

# ============================================================
# تنظیمات اصلی
# ============================================================

screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Pixel Snake")

clock = pygame.time.Clock()

SCREEN_W, SCREEN_H = screen.get_size()

BOARD_SIZE = 600
CELL = 30
GRID = 20
BORDER = 15

BOARD_X = (SCREEN_W - BOARD_SIZE) // 2
BOARD_Y = (SCREEN_H - BOARD_SIZE) // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CREAM = (245, 222, 179)

GREEN_LIGHT = (170, 255, 80)
GREEN_DARK = (60, 130, 50)

YELLOW = (255, 220, 0)
RED = (240, 35, 35)
DARK_RED = (150, 0, 0)
LIGHT_RED = (255, 90, 90)

GRAY = (100, 100, 100)
DARK_GRAY = (55, 55, 55)
LIGHT_GRAY = (160, 160, 160)

BLUE = (60, 150, 255)
CYAN = (70, 240, 240)
PURPLE = (180, 80, 255)

# ============================================================
# فایل ذخیره رکورد
# ============================================================

HIGH_SCORE_FILE = "snake_high_score.json"


def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return int(data.get("high_score", 0))
    except:
        pass
    return 0


def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            json.dump({"high_score": value}, file)
    except:
        pass


high_score = load_high_score()

# ============================================================
# فونت‌ها
# ============================================================

font_title = pygame.font.Font(None, 90)
font_big = pygame.font.Font(None, 75)
font_medium = pygame.font.Font(None, 45)
font_small = pygame.font.Font(None, 32)

# ============================================================
# وضعیت بازی
# ============================================================

MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

state = MENU

# ============================================================
# مار
# ============================================================


def new_snake():
    return [
        [10, 10],
        [9, 10],
        [8, 10]
    ]


snake = new_snake()
direction = "RIGHT"

# ============================================================
# آیتم‌ها
# ============================================================

apples = []
rocks = []
bombs = []
tnts = []
special_blocks = []

# ============================================================
# زمان‌بندی آیتم‌ها
# ============================================================

APPLE_SPAWN = 2000
APPLE_LIFE = 30000

ROCK_SPAWN = 5000
ROCK_LIFE = 15000

BOMB_SPAWN = 3000
BOMB_LIFE = 25000

TNT_SPAWN = 10000
TNT_LIFE = 2000

SPECIAL_EVENT = 13000
SPECIAL_RED_TIME = 1000

last_apple_spawn = 0
last_rock_spawn = 0
last_bomb_spawn = 0
last_tnt_spawn = 0
last_special_event = 0

# ============================================================
# امتیاز و حرکت
# ============================================================

score = 0
game_time = 0
game_start_time = 0

last_score_time = 0
last_move = 0

INITIAL_MOVE_TIME = 500
move_time = INITIAL_MOVE_TIME

# ============================================================
# Combo
# ============================================================

combo = 0
last_apple_time = 0
COMBO_TIMEOUT = 3000

# ============================================================
# Power-up
# ============================================================

powerups = []
powerup_life = 12000
powerup_spawn_time = 18000
last_powerup_spawn = 0

active_power = None
active_power_end = 0

# ============================================================
# آمار
# ============================================================

max_length = 3

# ============================================================
# صدا
# ============================================================

sound_eat = None
sound_bomb = None
sound_game_over = None
sound_powerup = None

try:
    sound_eat = pygame.mixer.Sound("eat.wav")
    sound_bomb = pygame.mixer.Sound("bomb.wav")
    sound_game_over = pygame.mixer.Sound("gameover.wav")
    sound_powerup = pygame.mixer.Sound("powerup.wav")
except:
    pass


def play_sound(sound):
    if sound:
        try:
            sound.play()
        except:
            pass


# ============================================================
# محدوده زمین
# ============================================================


def get_bounds():
    shrink = score // 400

    # جلوگیری از نابودی کامل زمین
    shrink = min(shrink, 8)

    return (
        shrink,
        GRID - 1 - shrink,
        shrink,
        GRID - 1 - shrink
    )


def random_free_position():
    min_x, max_x, min_y, max_y = get_bounds()

    occupied = []

    for part in snake:
        occupied.append(part[:2])

    for item in apples + rocks + bombs + tnts + special_blocks:
        occupied.append(item[:2])

    for item in powerups:
        occupied.append(item[:2])

    for _ in range(300):
        pos = [
            random.randint(min_x, max_x),
            random.randint(min_y, max_y)
        ]

        if pos not in occupied:
            return pos

    return [min_x, min_y]


# ============================================================
# شروع بازی
# ============================================================


def start_game():
    global snake, direction, state
    global apples, rocks, bombs, tnts, special_blocks, powerups
    global score, game_time, max_length
    global last_score_time, last_move, game_start_time
    global last_apple_spawn, last_rock_spawn
    global last_bomb_spawn, last_tnt_spawn
    global last_special_event, last_powerup_spawn
    global combo, last_apple_time
    global active_power, active_power_end
    global move_time

    snake = new_snake()
    direction = "RIGHT"

    apples.clear()
    golden_apples.clear()
    rocks.clear()
    bombs.clear()
    tnts.clear()
    special_blocks.clear()
    powerups.clear()

    score = 0
    game_time = 0
    max_length = 3

    combo = 0
    last_apple_time = 0

    active_power = None
    active_power_end = 0

    move_time = INITIAL_MOVE_TIME

    now = pygame.time.get_ticks()

    last_score_time = now
    game_start_time = now
    last_move = now

    last_apple_spawn = now
    last_rock_spawn = now
    last_bomb_spawn = now
    last_tnt_spawn = now
    last_special_event = now
    last_powerup_spawn = now

    state = PLAYING


# ============================================================
# Game Over
# ============================================================


def end_game():
    global state, high_score

    state = GAME_OVER

    if score > high_score:
        high_score = score
        save_high_score(high_score)

    play_sound(sound_game_over)


# ============================================================
# ستاره
# ============================================================


def draw_star(surface, cx, cy, outer, inner, color):
    points = []

    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer if i % 2 == 0 else inner

        points.append(
            (
                cx + math.cos(angle) * radius,
                cy + math.sin(angle) * radius
            )
        )

    pygame.draw.polygon(surface, color, points)


# ============================================================
# سیب
# ============================================================


def draw_apple(surface, gx, gy, golden=False):
    x = BOARD_X + gx * CELL
    y = BOARD_Y + gy * CELL

    color = YELLOW if golden else RED
    dark = (180, 140, 0) if golden else DARK_RED

    pygame.draw.circle(
        surface,
        dark,
        (x + 15, y + 16),
        12
    )

    pygame.draw.circle(
        surface,
        color,
        (x + 13, y + 14),
        10
    )

    pygame.draw.circle(
        surface,
        WHITE,
        (x + 9, y + 10),
        3
    )

    pygame.draw.line(
        surface,
        GREEN_DARK,
        (x + 15, y + 5),
        (x + 19, y),
        3
    )


# ============================================================
# سنگ
# ============================================================


def draw_rock(surface, gx, gy):
    x = BOARD_X + gx * CELL
    y = BOARD_Y + gy * CELL

    pygame.draw.circle(
        surface,
        DARK_GRAY,
        (x + 15, y + 16),
        13
    )

    pygame.draw.circle(
        surface,
        GRAY,
        (x + 13, y + 13),
        10
    )

    pygame.draw.circle(
        surface,
        LIGHT_GRAY,
        (x + 9, y + 9),
        3
    )


# ============================================================
# بمب
# ============================================================


def draw_bomb(surface, gx, gy):
    x = BOARD_X + gx * CELL
    y = BOARD_Y + gy * CELL

    pygame.draw.circle(
        surface,
        BLACK,
        (x + 15, y + 16),
        12
    )

    pygame.draw.circle(
        surface,
        DARK_GRAY,
        (x + 12, y + 13),
        9
    )

    pygame.draw.line(
        surface,
        BLACK,
        (x + 20, y + 6),
        (x + 26, y),
        3
    )

    pygame.draw.circle(
        surface,
        RED,
        (x + 27, y),
        3
    )


# ============================================================
# TNT
# ============================================================


def draw_tnt(surface, gx, gy):
    x = BOARD_X + gx * CELL
    y = BOARD_Y + gy * CELL

    pygame.draw.rect(
        surface,
        DARK_GRAY,
        (x + 3, y + 5, 24, 21),
        border_radius=4
    )

    for stripe_x in (7, 15, 23):
        pygame.draw.line(
            surface,
            RED,
            (x + stripe_x, y + 5),
            (x + stripe_x, y + 26),
            3
        )

    pygame.draw.line(
        surface,
        (70, 40, 20),
        (x + 20, y + 6),
        (x + 27, y),
        3
    )

    pygame.draw.circle(
        surface,
        YELLOW,
        (x + 27, y),
        3
    )


# ============================================================
# Power-up
# ============================================================


def draw_powerup(surface, gx, gy, power_type):
    x = BOARD_X + gx * CELL
    y = BOARD_Y + gy * CELL

    if power_type == "shield":
        color = CYAN
        symbol = "S"

    elif power_type == "double":
        color = YELLOW
        symbol = "2"

    else:
        color = PURPLE
        symbol = "T"

    pygame.draw.circle(
        surface,
        color,
        (x + 15, y + 15),
        12
    )

    text = font_small.render(
        symbol,
        True,
        BLACK
    )

    rect = text.get_rect(
        center=(x + 15, y + 15)
    )

    surface.blit(text, rect)


# ============================================================
# مار
# ============================================================


def draw_snake(surface):
    for i, part in enumerate(snake):

        x = BOARD_X + part[0] * CELL
        y = BOARD_Y + part[1] * CELL

        pygame.draw.rect(
            surface,
            YELLOW,
            (
                x + 2,
                y + 2,
                CELL - 4,
                CELL - 4
            ),
            border_radius=7
        )

        if i == 0:

            if direction == "RIGHT":
                eyes = [
                    (x + 20, y + 8),
                    (x + 20, y + 22)
                ]

            elif direction == "LEFT":
                eyes = [
                    (x + 10, y + 8),
                    (x + 10, y + 22)
                ]

            elif direction == "UP":
                eyes = [
                    (x + 8, y + 10),
                    (x + 22, y + 10)
                ]

            else:
                eyes = [
                    (x + 8, y + 20),
                    (x + 22, y + 20)
                ]

            for eye in eyes:
                pygame.draw.circle(
                    surface,
                    WHITE,
                    eye,
                    5
                )

                pygame.draw.circle(
                    surface,
                    BLACK,
                    eye,
                    2
                )


# ============================================================
# زمین
# ============================================================


def draw_board():
    screen.fill(BLACK)

    pygame.draw.rect(
        screen,
        CREAM,
        (
            BOARD_X - BORDER,
            BOARD_Y - BORDER,
            BOARD_SIZE + BORDER * 2,
            BOARD_SIZE + BORDER * 2
        )
    )

    for row in range(GRID):
        for col in range(GRID):

            color = (
                GREEN_LIGHT
                if (row + col) % 2 == 0
                else GREEN_DARK
            )

            pygame.draw.rect(
                screen,
                color,
                (
                    BOARD_X + col * CELL,
                    BOARD_Y + row * CELL,
                    CELL,
                    CELL
                )
            )

    min_x, max_x, min_y, max_y = get_bounds()

    # خارج محدوده قابل بازی
    if min_x > 0:
        pygame.draw.rect(
            screen,
            BLACK,
            (
                BOARD_X,
                BOARD_Y,
                min_x * CELL,
                BOARD_SIZE
            )
        )

    if max_x < GRID - 1:
        pygame.draw.rect(
            screen,
            BLACK,
            (
                BOARD_X + (max_x + 1) * CELL,
                BOARD_Y,
                min_x * CELL,
                BOARD_SIZE
            )
        )

    if min_y > 0:
        pygame.draw.rect(
            screen,
            BLACK,
            (
                BOARD_X,
                BOARD_Y,
                BOARD_SIZE,
                min_y * CELL
            )
        )

    if max_y < GRID - 1:
        pygame.draw.rect(
            screen,
            BLACK,
            (
                BOARD_X,
                BOARD_Y + (max_y + 1) * CELL,
                BOARD_SIZE,
                min_y * CELL
            )
        )


# ============================================================
# HUD
# ============================================================


def draw_hud():
    draw_star(
        screen,
        35,
        35,
        15,
        6,
        YELLOW
    )

    score_text = font_small.render(
        str(score),
        True,
        YELLOW
    )

    screen.blit(
        score_text,
        (58, 20)
    )

    length_text = font_small.render(
        f"Length: {len(snake)}",
        True,
        RED
    )

    rect = length_text.get_rect(
        top=18,
        right=SCREEN_W - 20
    )

    screen.blit(
        length_text,
        rect
    )

    if combo > 1:
        combo_text = font_medium.render(
            f"COMBO x{combo}",
            True,
            YELLOW
        )

        combo_rect = combo_text.get_rect(
            center=(SCREEN_W // 2, 30)
        )

        screen.blit(
            combo_text,
            combo_rect
        )

    level = score // 500 + 1

    level_text = font_small.render(
        f"Level {level}",
        True,
        WHITE
    )

    screen.blit(
        level_text,
        (
            BOARD_X,
            BOARD_Y - 55
        )
    )

    time_text = font_small.render(
        f"Time: {game_time // 1000}s",
        True,
        WHITE
    )

    time_rect = time_text.get_rect(
        top=18,
        centerx=SCREEN_W // 2
    )

    screen.blit(
        time_text,
        time_rect
    )


# ============================================================
# منوی شروع
# ============================================================


def draw_menu():
    screen.fill(BLACK)

    title = font_title.render(
        "PIXEL SNAKE",
        True,
        YELLOW
    )

    title_rect = title.get_rect(
        center=(SCREEN_W // 2, SCREEN_H // 2 - 180)
    )

    screen.blit(title, title_rect)

    info = font_medium.render(
        "Classic Snake Challenge",
        True,
        WHITE
    )

    info_rect = info.get_rect(
        center=(SCREEN_W // 2, SCREEN_H // 2 - 100)
    )

    screen.blit(info, info_rect)

    start_button = pygame.Rect(
        SCREEN_W // 2 - 140,
        SCREEN_H // 2 - 30,
        280,
        65
    )

    exit_button = pygame.Rect(
        SCREEN_W // 2 - 140,
        SCREEN_H // 2 + 55,
        280,
        65
    )

    pygame.draw.rect(
        screen,
        GREEN_LIGHT,
        start_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        RED,
        exit_button,
        border_radius=12
    )

    start_text = font_medium.render(
        "START GAME",
        True,
        BLACK
    )

    exit_text = font_medium.render(
        "EXIT",
        True,
        BLACK
    )

    screen.blit(
        start_text,
        start_text.get_rect(
            center=start_button.center
        )
    )

    screen.blit(
        exit_text,
        exit_text.get_rect(
            center=exit_button.center
        )
    )

    high_text = font_small.render(
        f"High Score: {high_score}",
        True,
        YELLOW
    )

    high_rect = high_text.get_rect(
        center=(SCREEN_W // 2, SCREEN_H // 2 + 150)
    )

    screen.blit(
        high_text,
        high_rect
    )

    return start_button, exit_button


# ============================================================
# Pause
# ============================================================


def draw_pause():
    overlay = pygame.Surface(
        (SCREEN_W, SCREEN_H),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 160)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    text = font_big.render(
        "PAUSED",
        True,
        WHITE
    )

    screen.blit(
        text,
        text.get_rect(
            center=(SCREEN_W // 2, SCREEN_H // 2)
        )
    )

    info = font_small.render(
        "Press P to continue",
        True,
        YELLOW
    )

    screen.blit(
        info,
        info.get_rect(
            center=(SCREEN_W // 2, SCREEN_H // 2 + 60)
        )
    )


# ============================================================
# Game Over
# ============================================================


def draw_game_over():
    overlay = pygame.Surface(
        (SCREEN_W, SCREEN_H),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 180)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = font_big.render(
        "GAME OVER",
        True,
        RED
    )

    screen.blit(
        title,
        title.get_rect(
            center=(SCREEN_W // 2, SCREEN_H // 2 - 150)
        )
    )

    stats = [
        f"Score: {score}",
        f"High Score: {high_score}",
        f"Length: {len(snake)}",
        f"Best Length: {max_length}",
        f"Time: {game_time // 1000}s"
    ]

    for i, text_value in enumerate(stats):

        text = font_small.render(
            text_value,
            True,
            WHITE
        )

        rect = text.get_rect(
            center=(
                SCREEN_W // 2,
                SCREEN_H // 2 - 80 + i * 35
            )
        )

        screen.blit(text, rect)

    restart_button = pygame.Rect(
        SCREEN_W // 2 - 180,
        SCREEN_H // 2 + 130,
        160,
        60
    )

    exit_button = pygame.Rect(
        SCREEN_W // 2 + 20,
        SCREEN_H // 2 + 130,
        160,
        60
    )

    pygame.draw.rect(
        screen,
        GREEN_LIGHT,
        restart_button,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        RED,
        exit_button,
        border_radius=10
    )

    restart_text = font_small.render(
        "Restart",
        True,
        BLACK
    )

    exit_text = font_small.render(
        "Exit",
        True,
        BLACK
    )

    screen.blit(
        restart_text,
        restart_text.get_rect(
            center=restart_button.center
        )
    )

    screen.blit(
        exit_text,
        exit_text.get_rect(
            center=exit_button.center
        )
    )

    return restart_button, exit_button


# ============================================================
# حلقه اصلی
# ============================================================


# Golden apple
GOLDEN_APPLE_SPAWN = 5000       # every 5 seconds
GOLDEN_APPLE_LIFE = 40000       # 40 seconds
GOLDEN_APPLE_CHANCE = 0.20      # 1/5
GOLDEN_APPLE_LENGTH = 3
golden_apples = []
last_golden_apple_spawn = 0
touch_start_pos = None

running = True

async def main():
    global active_power, active_power_end, combo, direction, game_time, last_apple_spawn, last_apple_time, last_bomb_spawn, last_move, last_powerup_spawn, last_rock_spawn, last_score_time, last_special_event, last_tnt_spawn, last_golden_apple_spawn, max_length, move_time, running, score, state
    while running:

        now = pygame.time.get_ticks()

        # ========================================================
        # منو
        # ========================================================

        if state == MENU:

            start_button, exit_button = draw_menu()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        start_game()

                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if start_button.collidepoint(event.pos):
                        start_game()

                    elif exit_button.collidepoint(event.pos):
                        running = False

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)
            continue

        # ========================================================
        # بازی
        # ========================================================

        if state == PLAYING:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_p:
                        state = PAUSED

                    elif event.key == pygame.K_LEFT:

                        if direction != "RIGHT":
                            direction = "LEFT"

                    elif event.key == pygame.K_RIGHT:

                        if direction != "LEFT":
                            direction = "RIGHT"

                    elif event.key == pygame.K_UP:

                        if direction != "DOWN":
                            direction = "UP"

                    elif event.key == pygame.K_DOWN:

                        if direction != "UP":
                            direction = "DOWN"


                elif event.type == pygame.FINGERDOWN:
                    touch_start_pos = (event.x, event.y)

                elif event.type == pygame.FINGERUP:
                    if touch_start_pos is not None:
                        dx = event.x - touch_start_pos[0]
                        dy = event.y - touch_start_pos[1]
                        touch_start_pos = None

                        if abs(dx) > abs(dy):
                            if abs(dx) >= 0.15:
                                if dx > 0 and direction != "LEFT":
                                    direction = "RIGHT"
                                elif dx < 0 and direction != "RIGHT":
                                    direction = "LEFT"
                        else:
                            if abs(dy) >= 0.15:
                                if dy > 0 and direction != "UP":
                                    direction = "DOWN"
                                elif dy < 0 and direction != "DOWN":
                                    direction = "UP"

            # ================================================
            # زمان بازی
            # ================================================

            game_time = now - game_start_time

            # ================================================
            # امتیاز هر ثانیه
            # ================================================

            if now - last_score_time >= 1000:

                passed = (now - last_score_time) // 1000

                score += passed

                last_score_time += passed * 1000

            # ================================================
            # Combo timeout
            # ================================================

            if now - last_apple_time > COMBO_TIMEOUT:
                combo = 0

            # ================================================
            # سرعت
            # ================================================

            if active_power == "slow":

                base_time = INITIAL_MOVE_TIME * 2

            else:

                base_time = INITIAL_MOVE_TIME

            if score >= 1200:
                move_time = base_time // 4

            elif score >= 700:
                move_time = base_time // 2

            elif score >= 300:
                move_time = base_time // 3

            else:
                move_time = base_time

            # ================================================
            # سیب
            # ================================================

            if now - last_apple_spawn >= APPLE_SPAWN:

                last_apple_spawn = now

                pos = random_free_position()

                apples.append(
                    [
                        pos[0],
                        pos[1],
                        now,
                        "normal"
                    ]
                )

            for apple in apples[:]:

                if now - apple[2] >= APPLE_LIFE:
                    apples.remove(apple)

            # ================================================

            # Golden apple
            if now - last_golden_apple_spawn >= GOLDEN_APPLE_SPAWN:
                last_golden_apple_spawn = now
                if random.random() < GOLDEN_APPLE_CHANCE:
                    pos = random_free_position()
                    golden_apples.append([pos[0], pos[1], now])

            for golden in golden_apples[:]:
                if now - golden[2] >= GOLDEN_APPLE_LIFE:
                    golden_apples.remove(golden)

            # سنگ
            # ================================================

            if now - last_rock_spawn >= ROCK_SPAWN:

                last_rock_spawn = now

                for _ in range(4):

                    pos = random_free_position()

                    rocks.append(
                        [
                            pos[0],
                            pos[1],
                            now
                        ]
                    )

            for rock in rocks[:]:

                if now - rock[2] >= ROCK_LIFE:
                    rocks.remove(rock)

            # ================================================
            # بمب
            # ================================================

            if now - last_bomb_spawn >= BOMB_SPAWN:

                last_bomb_spawn = now

                pos = random_free_position()

                bombs.append(
                    [
                        pos[0],
                        pos[1],
                        now
                    ]
                )

            for bomb in bombs[:]:

                if now - bomb[2] >= BOMB_LIFE:

                    bombs.remove(bomb)

            # ================================================
            # TNT
            # ================================================

            if score >= 1000:

                if now - last_tnt_spawn >= TNT_SPAWN:

                    last_tnt_spawn = now

                    pos = random_free_position()

                    tnts.append(
                        [
                            pos[0],
                            pos[1],
                            now
                        ]
                    )

            for tnt in tnts[:]:

                if now - tnt[2] >= TNT_LIFE:

                    tx, ty = tnt[0], tnt[1]
                    sx, sy = snake[0]

                    if (
                        abs(sx - tx) <= 1
                        and abs(sy - ty) <= 1
                    ):

                        score = max(
                            0,
                            score - 200
                        )

                        play_sound(sound_bomb)

                    tnts.remove(tnt)

            # ================================================

            # Golden apple collision
            for golden in golden_apples[:]:
                if snake[0] == (golden[0], golden[1]):
                    for _ in range(GOLDEN_APPLE_LENGTH):
                        snake.append(snake[-1])
                    golden_apples.remove(golden)

            # Power-ups
            # ================================================

            if now - last_powerup_spawn >= powerup_spawn_time:

                last_powerup_spawn = now

                pos = random_free_position()

                powerups.append(
                    [
                        pos[0],
                        pos[1],
                        now,
                        random.choice(
                            [
                                "shield",
                                "double",
                                "slow"
                            ]
                        )
                    ]
                )

            for power in powerups[:]:

                if now - power[2] >= powerup_life:
                    powerups.remove(power)

            # ================================================
            # فعال بودن Power-up
            # ================================================

            if active_power is not None:

                if now >= active_power_end:

                    active_power = None
                    active_power_end = 0

            # ================================================
            # رویداد امتیاز بالای 1000
            # ================================================

            if score > 1000:

                if now - last_special_event >= SPECIAL_EVENT:

                    last_special_event = now

                    pos = random_free_position()

                    special_blocks.append(
                        [
                            pos[0],
                            pos[1],
                            now
                        ]
                    )

            for special in special_blocks[:]:

                if now - special[2] >= SPECIAL_RED_TIME:

                    special_blocks.remove(special)

                    for _ in range(8):

                        pos = random_free_position()

                        rocks.append(
                            [
                                pos[0],
                                pos[1],
                                now
                            ]
                        )

            # ================================================
            # حرکت مار
            # ================================================

            if now - last_move >= move_time:

                last_move = now

                head = snake[0][:]

                if direction == "RIGHT":
                    head[0] += 1

                elif direction == "LEFT":
                    head[0] -= 1

                elif direction == "UP":
                    head[1] -= 1

                elif direction == "DOWN":
                    head[1] += 1

                min_x, max_x, min_y, max_y = get_bounds()

                # دیوار
                if (
                    head[0] < min_x
                    or head[0] > max_x
                    or head[1] < min_y
                    or head[1] > max_y
                ):

                    end_game()

                # برخورد با خودش
                elif head in snake:

                    end_game()

                else:

                    snake.insert(0, head)

                    ate = False

                    # ==========================================
                    # سیب
                    # ==========================================

                    for apple in apples[:]:

                        if (
                            head[0] == apple[0]
                            and head[1] == apple[1]
                        ):

                            apples.remove(apple)

                            combo += 1

                            last_apple_time = now

                            if combo < 2:
                                combo_bonus = 20
                            else:
                                combo_bonus = 20 + combo * 5

                            if active_power == "double":
                                combo_bonus *= 2

                            score += combo_bonus

                            ate = True

                            play_sound(sound_eat)

                            break

                    # ==========================================
                    # بمب
                    # ==========================================

                    for bomb in bombs[:]:

                        if (
                            head[0] == bomb[0]
                            and head[1] == bomb[1]
                        ):

                            bombs.remove(bomb)

                            score = max(
                                0,
                                score - 50
                            )

                            break

                    # ==========================================
                    # سنگ
                    # ==========================================

                    if active_power != "shield":

                        for rock in rocks:

                            if (
                                head[0] == rock[0]
                                and head[1] == rock[1]
                            ):

                                end_game()
                                break

                    # ==========================================
                    # Power-up
                    # ==========================================

                    for power in powerups[:]:

                        if (
                            head[0] == power[0]
                            and head[1] == power[1]
                        ):

                            powerups.remove(power)

                            active_power = power[3]
                            active_power_end = now + 10000

                            play_sound(sound_powerup)

                            break

                    # ==========================================
                    # دم
                    # ==========================================

                    if state == PLAYING and not ate:
                        snake.pop()

                    max_length = max(
                        max_length,
                        len(snake)
                    )

        # ========================================================
        # Pause
        # ========================================================

        elif state == PAUSED:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_p:
                        state = PLAYING

                    elif event.key == pygame.K_ESCAPE:
                        running = False

        # ========================================================
        # رسم
        # ========================================================

        if state in (PLAYING, PAUSED):

            draw_board()

            # آیتم‌ها
            for apple in apples:
                draw_apple(
                    screen,
                    apple[0],
                    apple[1],
                    apple[3] == "gold"
                )

            for rock in rocks:
                draw_rock(
                    screen,
                    rock[0],
                    rock[1]
                )

            for bomb in bombs:
                draw_bomb(
                    screen,
                    bomb[0],
                    bomb[1]
                )

            for tnt in tnts:
                draw_tnt(
                    screen,
                    tnt[0],
                    tnt[1]
                )

            for power in powerups:
                draw_powerup(
                    screen,
                    power[0],
                    power[1],
                    power[3]
                )

            # بلاک قرمز
            for special in special_blocks:

                x = BOARD_X + special[0] * CELL
                y = BOARD_Y + special[1] * CELL

                pygame.draw.rect(
                    screen,
                    RED,
                    (
                        x,
                        y,
                        CELL,
                        CELL
                    )
                )


            # Golden apples
            for golden in golden_apples:
                gx = BOARD_X + golden[0] * CELL
                gy = BOARD_Y + golden[1] * CELL
                cx = gx + CELL // 2
                cy = gy + CELL // 2
                pygame.draw.circle(
                    screen, (255, 215, 0),
                    (cx, cy), CELL // 3
                )
                pygame.draw.circle(
                    screen, (255, 245, 140),
                    (cx - 5, cy - 5), 4
                )

            draw_snake(screen)
            draw_hud()

            if state == PAUSED:
                draw_pause()

        # ========================================================
        # Game Over
        # ========================================================

        elif state == GAME_OVER:

            draw_board()
            draw_snake(screen)

            restart_button, exit_button = draw_game_over()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        start_game()

                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if restart_button.collidepoint(event.pos):
                        start_game()

                    elif exit_button.collidepoint(event.pos):
                        running = False

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


    pygame.quit()

asyncio.run(main())
