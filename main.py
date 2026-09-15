import os
import sys
import math
import array
import random

import pygame

# =========================
# ИНИЦИАЛИЗАЦИЯ
# =========================

try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
except Exception:
    pygame.init()

WIDTH = 720
HEIGHT = 1280

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ЗВЁЗДНЫЙ УВОРОТ")

clock = pygame.time.Clock()

# =========================
# ЦВЕТА
# =========================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BLUE = (30, 100, 200)
LIGHT_BLUE = (80, 180, 255)

RED = (220, 50, 50)
GREEN = (50, 220, 100)
YELLOW = (255, 220, 50)
PURPLE = (180, 70, 220)

DARK_BLUE = (8, 8, 25)
GRAY = (100, 100, 110)

# =========================
# ИКОНКА ИГРЫ
# =========================

try:
    icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    icon.fill((8, 8, 25, 255))

    pygame.draw.circle(icon, WHITE, (10, 10), 2)
    pygame.draw.circle(icon, WHITE, (52, 13), 2)
    pygame.draw.circle(icon, WHITE, (15, 48), 2)
    pygame.draw.circle(icon, WHITE, (51, 50), 2)

    pygame.draw.polygon(
        icon,
        (255, 100, 0),
        [(27, 46), (32, 61), (37, 46)]
    )

    pygame.draw.polygon(
        icon,
        YELLOW,
        [(29, 45), (32, 56), (35, 45)]
    )

    pygame.draw.polygon(
        icon,
        (30, 100, 200),
        [(28, 30), (8, 48), (25, 43)]
    )

    pygame.draw.polygon(
        icon,
        (30, 100, 200),
        [(36, 30), (56, 48), (39, 43)]
    )

    pygame.draw.polygon(
        icon,
        BLUE,
        [(32, 8), (22, 43), (32, 49), (42, 43)]
    )

    pygame.draw.ellipse(
        icon,
        (200, 240, 255),
        (27, 20, 10, 15)
    )

    pygame.display.set_icon(icon)

except Exception:
    pass

# =========================
# ШРИФТЫ
# =========================

try:
    FONT_BIG = pygame.font.Font(None, 90)
    FONT_MEDIUM = pygame.font.Font(None, 60)
    FONT_SMALL = pygame.font.Font(None, 40)
except Exception:
    FONT_BIG = pygame.font.SysFont(None, 90)
    FONT_MEDIUM = pygame.font.SysFont(None, 60)
    FONT_SMALL = pygame.font.SysFont(None, 40)

# =========================
# ЗВУКИ
# =========================

def make_sound(freq, duration, volume=0.25):
    try:
        sample_rate = 44100
        count = int(sample_rate * duration)

        buf = array.array("h")

        for i in range(count):
            value = int(
                32767
                * volume
                * math.sin(
                    2 * math.pi * freq * i / sample_rate
                )
            )
            buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    except Exception:
        return None


try:
    snd_shoot = make_sound(700, 0.05)
    snd_kill = make_sound(250, 0.12)
    snd_shop = make_sound(500, 0.15)
    snd_respawn = make_sound(900, 0.15)
except Exception:
    snd_shoot = None
    snd_kill = None
    snd_shop = None
    snd_respawn = None


def play_sound(sound):
    try:
        if sound:
            sound.play()
    except Exception:
        pass


# =========================
# СОСТОЯНИЯ
# =========================

MENU = "menu"
SHOP = "shop"
PLAYING = "playing"
GAMEOVER = "gameover"

game_state = MENU

# =========================
# ПЕРЕМЕННЫЕ
# =========================

coins = 0
run_coins = 0

distance = 0.0

# Босс каждые 100 очков
last_boss_hundred = 0

weapon_level = 1
shield_time = 0

current_skin = "green"

# =========================
# ИГРОК
# =========================

player = pygame.Rect(
    WIDTH // 2 - 35,
    HEIGHT - 250,
    70,
    80
)

player_speed = 12

# =========================
# СПИСКИ
# =========================

bullets = []
enemies = []
enemy_bullets = []

# =========================
# ЗВЁЗДЫ
# =========================

stars = []

for _ in range(100):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 4)
    ])


# =========================
# РИСОВАНИЕ ИГРОКА
# =========================

def draw_player():

    color = GREEN

    if current_skin == "blue":
        color = BLUE
    elif current_skin == "red":
        color = RED
    elif current_skin == "yellow":
        color = YELLOW

    x = player.centerx
    y = player.centery

    pygame.draw.polygon(
        screen,
        color,
        [
            (x - 25, y),
            (x - 60, y + 40),
            (x - 15, y + 30)
        ]
    )

    pygame.draw.polygon(
        screen,
        color,
        [
            (x + 25, y),
            (x + 60, y + 40),
            (x + 15, y + 30)
        ]
    )

    pygame.draw.polygon(
        screen,
        color,
        [
            (x, y - 40),
            (x - 25, y + 35),
            (x, y + 50),
            (x + 25, y + 35)
        ]
    )

    pygame.draw.ellipse(
        screen,
        LIGHT_BLUE,
        (
            x - 10,
            y - 20,
            20,
            30
        )
    )

    pygame.draw.polygon(
        screen,
        RED,
        [
            (x - 12, y + 42),
            (x, y + 65),
            (x + 12, y + 42)
        ]
    )


# =========================
# ПУЛЯ
# =========================

class Bullet:

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            int(x - 5),
            int(y),
            10,
            25
        )

        self.speed = 22

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        pygame.draw.rect(
            screen,
            YELLOW,
            self.rect
        )


# =========================
# ВРАЖЕСКАЯ ПУЛЯ
# =========================

class EnemyBullet:

    def __init__(self, x, y, speed=8):

        self.rect = pygame.Rect(
            int(x - 5),
            int(y),
            10,
            25
        )

        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(
            screen,
            RED,
            self.rect
        )


# =========================
# ВРАГ
# =========================

class Enemy:

    def __init__(self, enemy_type):

        self.enemy_type = enemy_type

        if enemy_type == "normal":

            self.width = 70
            self.height = 60

            self.hp = 4
            self.max_hp = 4

            self.speed = random.uniform(2, 4)

            self.color = RED
            self.reward = 1

        elif enemy_type == "elite":

            self.width = 95
            self.height = 80

            self.hp = 8
            self.max_hp = 8

            self.speed = random.uniform(2, 3)

            self.color = PURPLE
            self.reward = 3

        else:

            self.width = 180
            self.height = 120

            self.hp = 50
            self.max_hp = 50

            self.speed = 1

            self.color = YELLOW
            self.reward = 10

        self.x = random.randint(
            self.width // 2,
            WIDTH - self.width // 2
        )

        self.y = -self.height

        self.rect = pygame.Rect(
            int(self.x - self.width // 2),
            int(self.y),
            self.width,
            self.height
        )

        self.shoot_timer = random.randint(40, 100)

    def update(self):

        if self.enemy_type == "boss":

            if self.y < 200:
                self.y += self.speed

            self.shoot_timer -= 1

            if self.shoot_timer <= 0:

                enemy_bullets.append(
                    EnemyBullet(
                        self.rect.centerx,
                        self.rect.bottom,
                        8
                    )
                )

                enemy_bullets.append(
                    EnemyBullet(
                        self.rect.centerx - 45,
                        self.rect.bottom,
                        7
                    )
                )

                enemy_bullets.append(
                    EnemyBullet(
                        self.rect.centerx + 45,
                        self.rect.bottom,
                        7
                    )
                )

                self.shoot_timer = 90

        else:
            self.y += self.speed

        self.rect.x = int(
            self.x - self.width // 2
        )

        self.rect.y = int(self.y)

    def draw(self):

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=15
        )

        eye_y = self.rect.y + self.height // 3

        pygame.draw.circle(
            screen,
            WHITE,
            (
                self.rect.x + self.width // 3,
                eye_y
            ),
            8
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                self.rect.x + self.width * 2 // 3,
                eye_y
            ),
            8
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                self.rect.x + self.width // 3,
                eye_y
            ),
            4
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                self.rect.x + self.width * 2 // 3,
                eye_y
            ),
            4
        )

        hp_width = self.width

        current_width = int(
            hp_width * self.hp / self.max_hp
        )

        bar_y = self.rect.y - 18 if self.enemy_type == "boss" else self.rect.y - 12
        bar_h = 10 if self.enemy_type == "boss" else 7

        pygame.draw.rect(
            screen,
            RED,
            (
                self.rect.x,
                bar_y,
                hp_width,
                bar_h
            )
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.rect.x,
                bar_y,
                current_width,
                bar_h
            )
        )


# =========================
# КНОПКА
# =========================

def draw_btn(text, x, y, w, h, color):

    rect = pygame.Rect(
        int(x),
        int(y),
        int(w),
        int(h)
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=20
    )

    txt = FONT_SMALL.render(
        text,
        True,
        WHITE
    )

    screen.blit(
        txt,
        (
            rect.centerx - txt.get_width() // 2,
            rect.centery - txt.get_height() // 2
        )
    )

    return rect


# =========================
# СБРОС ПРОГРЕССА
# =========================

def reset_progress():

    global coins
    global run_coins
    global distance
    global last_boss_hundred
    global weapon_level
    global shield_time
    global current_skin
    global game_state

    coins = 0
    run_coins = 0
    distance = 0.0

    last_boss_hundred = 0

    weapon_level = 1
    shield_time = 0

    current_skin = "green"

    bullets.clear()
    enemies.clear()
    enemy_bullets.clear()

    player.x = WIDTH // 2 - player.width // 2
    player.y = HEIGHT - 250

    game_state = MENU


# =========================
# НАЧАЛО ИГРЫ
# =========================

def start_game():

    global run_coins
    global distance
    global last_boss_hundred
    global shield_time
    global game_state

    run_coins = 0
    distance = 0.0

    last_boss_hundred = 0

    shield_time = 0

    bullets.clear()
    enemies.clear()
    enemy_bullets.clear()

    player.x = WIDTH // 2 - player.width // 2
    player.y = HEIGHT - 250

    game_state = PLAYING


# =========================
# МЕНЮ
# =========================

def draw_menu():

    screen.fill(DARK_BLUE)

    for star in stars:

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(star[0]),
                int(star[1])
            ),
            star[2]
        )

    title = FONT_BIG.render(
        "ЗВЁЗДНЫЙ УВОРОТ",
        True,
        WHITE
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            130
        )
    )

    coins_text = FONT_MEDIUM.render(
        f"Монеты: {coins}",
        True,
        YELLOW
    )

    screen.blit(
        coins_text,
        (
            WIDTH // 2 - coins_text.get_width() // 2,
            260
        )
    )

    draw_btn(
        "ИГРАТЬ",
        100,
        400,
        WIDTH - 200,
        100,
        GREEN
    )

    draw_btn(
        "МАГАЗИН",
        100,
        520,
        WIDTH - 200,
        90,
        BLUE
    )

    draw_btn(
        "СБРОС ПРОГРЕССА",
        100,
        HEIGHT * 0.64,
        WIDTH - 200,
        90,
        RED
    )


# =========================
# МАГАЗИН
# =========================

def draw_shop():

    screen.fill(DARK_BLUE)

    title = FONT_BIG.render(
        "МАГАЗИН",
        True,
        WHITE
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            70
        )
    )

    coins_text = FONT_MEDIUM.render(
        f"Монеты: {coins}",
        True,
        YELLOW
    )

    screen.blit(
        coins_text,
        (
            WIDTH // 2 - coins_text.get_width() // 2,
            180
        )
    )

    draw_btn(
        "СИНИЙ СКИН - 40",
        80,
        300,
        WIDTH - 160,
        80,
        BLUE
    )

    draw_btn(
        "КРАСНЫЙ СКИН - 60",
        80,
        400,
        WIDTH - 160,
        80,
        RED
    )

    draw_btn(
        "ЖЁЛТЫЙ СКИН - 100",
        80,
        500,
        WIDTH - 160,
        80,
        YELLOW
    )

    draw_btn(
        "УЛУЧШИТЬ ОРУЖИЕ",
        80,
        650,
        WIDTH - 160,
        80,
        PURPLE
    )

    weapon_text = FONT_SMALL.render(
        f"Оружие: {weapon_level}/3",
        True,
        WHITE
    )

    screen.blit(
        weapon_text,
        (
            WIDTH // 2 - weapon_text.get_width() // 2,
            750
        )
    )

    draw_btn(
        "ЩИТ 10 СЕК - 45",
        80,
        830,
        WIDTH - 160,
        80,
        GREEN
    )

    draw_btn(
        "НАЗАД",
        100,
        1050,
        WIDTH - 200,
        80,
        GRAY
    )


# =========================
# GAME OVER
# =========================

def draw_gameover():

    screen.fill(DARK_BLUE)

    title = FONT_BIG.render(
        "ИГРА ОКОНЧЕНА",
        True,
        RED
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            180
        )
    )

    score_text = FONT_MEDIUM.render(
        f"Очки: {int(distance)}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (
            WIDTH // 2 - score_text.get_width() // 2,
            320
        )
    )

    coins_text = FONT_MEDIUM.render(
        f"+{run_coins} монет",
        True,
        YELLOW
    )

    screen.blit(
        coins_text,
        (
            WIDTH // 2 - coins_text.get_width() // 2,
            400
        )
    )

    draw_btn(
        "ВОЗРОДИТЬСЯ - 30",
        80,
        600,
        WIDTH - 160,
        90,
        GREEN
    )

    draw_btn(
        "ЗАНОВО",
        80,
        720,
        WIDTH - 160,
        90,
        BLUE
    )

    draw_btn(
        "В МЕНЮ",
        80,
        840,
        WIDTH - 160,
        90,
        GRAY
    )


# =========================
# ГЛАВНЫЙ ЦИКЛ
# =========================

running = True

while running:

    clock.tick(60)

    touch_pos = None

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            touch_pos = event.pos

        elif event.type == pygame.FINGERDOWN:

            touch_pos = (
                int(event.x * WIDTH),
                int(event.y * HEIGHT)
            )

    # =====================
    # МЕНЮ
    # =====================

    if game_state == MENU:

        draw_menu()

        if touch_pos:

            bx = 100
            bw = WIDTH - 200

            if (
                bx < touch_pos[0] < bx + bw
                and 400 < touch_pos[1] < 500
            ):
                start_game()

            elif (
                bx < touch_pos[0] < bx + bw
                and 520 < touch_pos[1] < 610
            ):
                game_state = SHOP

            elif (
                bx < touch_pos[0] < bx + bw
                and HEIGHT * 0.64
                < touch_pos[1]
                < HEIGHT * 0.64 + 90
            ):
                reset_progress()

    # =====================
    # МАГАЗИН
    # =====================

    elif game_state == SHOP:

        draw_shop()

        if touch_pos:

            bx = 80
            bw = WIDTH - 160

            if (
                bx < touch_pos[0] < bx + bw
                and 300 < touch_pos[1] < 380
            ):

                if coins >= 40:
                    coins -= 40
                    current_skin = "blue"
                    play_sound(snd_shop)

            elif (
                bx < touch_pos[0] < bx + bw
                and 400 < touch_pos[1] < 480
            ):

                if coins >= 60:
                    coins -= 60
                    current_skin = "red"
                    play_sound(snd_shop)

            elif (
                bx < touch_pos[0] < bx + bw
                and 500 < touch_pos[1] < 580
            ):

                if coins >= 100:
                    coins -= 100
                    current_skin = "yellow"
                    play_sound(snd_shop)

            elif (
                bx < touch_pos[0] < bx + bw
                and 650 < touch_pos[1] < 730
            ):

                if weapon_level == 1:
                    cost = 50
                elif weapon_level == 2:
                    cost = 70
                else:
                    cost = 80

                if (
                    weapon_level < 3
                    and coins >= cost
                ):
                    coins -= cost
                    weapon_level += 1
                    play_sound(snd_shop)

            elif (
                bx < touch_pos[0] < bx + bw
                and 830 < touch_pos[1] < 910
            ):

                if coins >= 45:
                    coins -= 45
                    shield_time = 600
                    play_sound(snd_shop)

            elif (
                100 < touch_pos[0] < WIDTH - 100
                and 1050 < touch_pos[1] < 1130
            ):

                game_state = MENU

    # =====================
    # ИГРА
    # =====================

    elif game_state == PLAYING:

        if touch_pos:

            target_x = (
                touch_pos[0]
                - player.width // 2
            )

            player.x += (
                target_x - player.x
            ) * 0.35

            if player.x < 0:
                player.x = 0

            if player.x > WIDTH - player.width:
                player.x = WIDTH - player.width

        # Автоматическая стрельба

        if random.randint(1, 8) == 1:

            if weapon_level == 1:

                bullets.append(
                    Bullet(
                        player.centerx,
                        player.top
                    )
                )

            elif weapon_level == 2:

                bullets.append(
                    Bullet(
                        player.centerx - 18,
                        player.top
                    )
                )

                bullets.append(
                    Bullet(
                        player.centerx + 18,
                        player.top
                    )
                )

            else:

                bullets.append(
                    Bullet(
                        player.centerx,
                        player.top
                    )
                )

                bullets.append(
                    Bullet(
                        player.centerx - 22,
                        player.top
                    )
                )

                bullets.append(
                    Bullet(
                        player.centerx + 22,
                        player.top
                    )
                )

            play_sound(snd_shoot)

        # =====================
        # ОЧКИ
        # =====================

        distance += 0.05

        # =====================
        # БОСС КАЖДЫЕ 100 ОЧКОВ
        # =====================

        current_hundred = int(distance) // 100

        if (
            current_hundred > last_boss_hundred
            and int(distance) > 0
        ):

            enemies.append(
                Enemy("boss")
            )

            last_boss_hundred = current_hundred

        # =====================
        # ПРИШЕЛЬЦЫ
        # =====================

        if random.randint(1, 50) == 1:

            e_type = (
                "normal"
                if random.randint(1, 4) != 1
                else "elite"
            )

            enemies.append(
                Enemy(e_type)
            )

        # =====================
        # ПУЛИ
        # =====================

        for bullet in bullets[:]:

            bullet.update()

            if bullet.rect.bottom < 0:

                bullets.remove(bullet)

        # =====================
        # ВРАГИ
        # =====================

        for enemy in enemies[:]:

            enemy.update()

            if enemy.rect.top > HEIGHT:

                enemies.remove(enemy)

        # =====================
        # ВРАЖЕСКИЕ ПУЛИ
        # =====================

        for bullet in enemy_bullets[:]:

            bullet.update()

            if bullet.rect.top > HEIGHT:

                enemy_bullets.remove(bullet)

        # =====================
        # ПОПАДАНИЯ
        # =====================

        for bullet in bullets[:]:

            hit = False

            for enemy in enemies[:]:

                if bullet.rect.colliderect(
                    enemy.rect
                ):

                    enemy.hp -= 1
                    hit = True

                    if enemy.hp <= 0:

                        run_coins += enemy.reward

                        play_sound(snd_kill)

                        enemies.remove(enemy)

                    break

            if hit and bullet in bullets:

                bullets.remove(bullet)

        # =====================
        # СТОЛКНОВЕНИЕ
        # =====================

        for enemy in enemies[:]:

            if enemy.rect.colliderect(
                player
            ):

                if shield_time > 0:

                    enemies.remove(enemy)

                else:

                    coins += run_coins
                    game_state = GAMEOVER

                break

        # =====================
        # ВРАЖЕСКИЕ ПУЛИ
        # =====================

        for bullet in enemy_bullets[:]:

            if bullet.rect.colliderect(
                player
            ):

                if shield_time > 0:

                    enemy_bullets.remove(
                        bullet
                    )

                else:

                    coins += run_coins
                    game_state = GAMEOVER

                    break

        # =====================
        # ЩИТ
        # =====================

        if shield_time > 0:

            shield_time -= 1

        # =====================
        # ФОН
        # =====================

        screen.fill(DARK_BLUE)

        for star in stars:

            star[1] += star[2]

            if star[1] > HEIGHT:

                star[1] = 0

                star[0] = random.randint(
                    0,
                    WIDTH
                )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(star[0]),
                    int(star[1])
                ),
                star[2]
            )

        # =====================
        # ОБЪЕКТЫ
        # =====================

        for bullet in bullets:
            bullet.draw()

        for enemy in enemies:
            enemy.draw()

        for bullet in enemy_bullets:
            bullet.draw()

        draw_player()

        # =====================
        # ЩИТ
        # =====================

        if shield_time > 0:

            pygame.draw.circle(
                screen,
                LIGHT_BLUE,
                player.center,
                65,
                5
            )

        # =====================
        # HUD
        # =====================

        distance_text = FONT_SMALL.render(
            f"Очки: {int(distance)}",
            True,
            WHITE
        )

        screen.blit(
            distance_text,
            (20, 20)
        )

        coins_text = FONT_SMALL.render(
            f"Монеты: {coins + run_coins}",
            True,
            YELLOW
        )

        screen.blit(
            coins_text,
            (20, 65)
        )

        weapon_text = FONT_SMALL.render(
            f"Оружие: {weapon_level}/3",
            True,
            WHITE
        )

        screen.blit(
            weapon_text,
            (
                WIDTH - weapon_text.get_width() - 20,
                20
            )
        )

    # =====================
    # GAME OVER
    # =====================

    elif game_state == GAMEOVER:

        draw_gameover()

        if touch_pos:

            bx = 80
            bw = WIDTH - 160

            # Возрождение
            if (
                bx < touch_pos[0] < bx + bw
                and 600 < touch_pos[1] < 690
            ):

                if coins >= 30:

                    coins -= 30

                    run_coins = 0

                    bullets.clear()
                    enemies.clear()
                    enemy_bullets.clear()

                    player.x = (
                        WIDTH // 2
                        - player.width // 2
                    )

                    player.y = HEIGHT - 250

                    shield_time = 300

                    game_state = PLAYING

                    play_sound(
                        snd_respawn
                    )

            # Заново
            elif (
                bx < touch_pos[0] < bx + bw
                and 720 < touch_pos[1] < 810
            ):

                start_game()

            # В меню
            elif (
                bx < touch_pos[0] < bx + bw
                and 840 < touch_pos[1] < 930
            ):

                game_state = MENU

    pygame.display.flip()


pygame.quit()
sys.exit()
