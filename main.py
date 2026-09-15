import os
import sys
import math
import array
import random

import pygame


try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
except Exception:
    pass

pygame.init()

try:
    pygame.mixer.init()
except Exception:
    pass


WIDTH, HEIGHT = 720, 1280

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ЗВЁЗДНЫЙ УВОРОТ")

clock = pygame.time.Clock()


# =========================
# ЦВЕТА
# =========================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (60, 255, 100)
BLUE = (60, 150, 255)
YELLOW = (255, 220, 50)
PURPLE = (180, 70, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 50)


# =========================
# ШРИФТЫ
# =========================

def get_safe_font(size):
    try:
        return pygame.font.Font(None, size)
    except Exception:
        return pygame.font.SysFont(None, size)


font_big = get_safe_font(70)
font_medium = get_safe_font(50)
font_small = get_safe_font(36)
font_tiny = get_safe_font(28)


# =========================
# ЗВУКИ
# =========================

def make_sound(frequency, duration, volume=0.25):
    try:
        sample_rate = 44100
        samples = int(sample_rate * duration)

        buf = array.array('h')

        for i in range(samples):
            t = i / sample_rate

            fade = min(
                1.0,
                i / (samples * 0.08),
                (samples - i) / (samples * 0.08)
            )

            value = int(
                32767
                * volume
                * max(0.0, fade)
                * math.sin(2 * math.pi * frequency * t)
            )

            buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    except Exception:
        return None


shoot_sound = make_sound(880, 0.045, 0.18)
kill_sound = make_sound(180, 0.09, 0.25)
shop_sound = make_sound(520, 0.12, 0.22)
respawn_sound = make_sound(330, 0.18, 0.22)


def play_sound(sound):
    try:
        if sound is not None:
            sound.play()
    except Exception:
        pass


# =========================
# СОСТОЯНИЯ
# =========================

MENU = "MENU"
SHOP = "SHOP"
PLAYING = "PLAYING"
GAMEOVER = "GAMEOVER"

game_state = MENU


# =========================
# ИГРОВЫЕ ДАННЫЕ
# =========================

coins = 0
run_coins = 0

distance = 0.0

last_boss_fifty = 0

weapon_level = 1

shield_time = 0

current_skin = "green"


# =========================
# СПИСКИ
# =========================

bullets = []
enemies = []
enemy_bullets = []


# =========================
# ИГРОК
# =========================

class Player:

    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 250
        self.speed = 0.25
        self.width = 80
        self.height = 100

    def draw(self):

        x = int(self.x)
        y = int(self.y)

        color = {
            "green": GREEN,
            "blue": BLUE,
            "red": RED,
            "yellow": YELLOW
        }.get(current_skin, GREEN)

        # Двигатели
        pygame.draw.polygon(
            screen,
            ORANGE if False else color,
            [
                (x - 35, y + 40),
                (x - 15, y + 40),
                (x - 25, y + 70)
            ]
        )

        pygame.draw.polygon(
            screen,
            color,
            [
                (x + 15, y + 40),
                (x + 35, y + 40),
                (x + 25, y + 70)
            ]
        )

        # Крылья
        pygame.draw.polygon(
            screen,
            color,
            [
                (x - 30, y),
                (x - 65, y + 35),
                (x - 30, y + 30)
            ]
        )

        pygame.draw.polygon(
            screen,
            color,
            [
                (x + 30, y),
                (x + 65, y + 35),
                (x + 30, y + 30)
            ]
        )

        # Основной корпус
        pygame.draw.polygon(
            screen,
            color,
            [
                (x, y - 50),
                (x - 30, y + 40),
                (x, y + 25),
                (x + 30, y + 40)
            ]
        )

        # Окно
        pygame.draw.ellipse(
            screen,
            WHITE,
            (x - 12, y - 15, 24, 30)
        )

        # Щит
        if shield_time > 0:
            pygame.draw.circle(
                screen,
                BLUE,
                (x, y),
                65,
                5
            )


player = Player()


# =========================
# ПУЛЯ ИГРОКА
# =========================

class Bullet:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 22
        self.width = 10
        self.height = 25

    def update(self):
        self.y -= self.speed

    def draw(self):

        pygame.draw.rect(
            screen,
            YELLOW,
            (
                int(self.x - self.width / 2),
                int(self.y),
                self.width,
                self.height
            ),
            border_radius=5
        )


# =========================
# ПУЛЯ ВРАГА
# =========================

class EnemyBullet:

    def __init__(self, x, y, speed=7):
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.y += self.speed

    def draw(self):

        pygame.draw.rect(
            screen,
            RED,
            (
                int(self.x - 7),
                int(self.y),
                14,
                30
            ),
            border_radius=5
        )


# =========================
# ВРАГ
# =========================

class Enemy:

    def __init__(self, enemy_type="normal"):

        self.type = enemy_type

        if enemy_type == "normal":

            self.width = 70
            self.height = 60

            self.x = random.randint(
                self.width,
                WIDTH - self.width
            )

            self.y = -self.height

            self.hp = 4
            self.max_hp = 4

            self.speed = random.uniform(2, 4)

            self.color = RED
            self.reward = 1

        elif enemy_type == "elite":

            self.width = 95
            self.height = 80

            self.x = random.randint(
                self.width,
                WIDTH - self.width
            )

            self.y = -self.height

            self.hp = 8
            self.max_hp = 8

            self.speed = 2

            self.color = PURPLE
            self.reward = 3

        elif enemy_type == "boss":

            self.width = 180
            self.height = 120

            self.x = WIDTH // 2

            self.y = -self.height

            self.hp = 50
            self.max_hp = 50

            self.speed = 1

            self.color = YELLOW
            self.reward = 10

            self.shoot_timer = 0

    def update(self):

        if self.type == "boss":

            if self.y < 200:
                self.y += self.speed

            self.shoot_timer += 1

            if self.shoot_timer >= 70:

                self.shoot_timer = 0

                enemy_bullets.append(
                    EnemyBullet(
                        self.x - 55,
                        self.y + 60,
                        7
                    )
                )

                enemy_bullets.append(
                    EnemyBullet(
                        self.x,
                        self.y + 60,
                        8
                    )
                )

                enemy_bullets.append(
                    EnemyBullet(
                        self.x + 55,
                        self.y + 60,
                        7
                    )
                )

        else:
            self.y += self.speed

    def draw(self):

        x = int(self.x)
        y = int(self.y)

        if self.type == "normal":

            pygame.draw.ellipse(
                screen,
                RED,
                (
                    x - self.width // 2,
                    y,
                    self.width,
                    self.height
                )
            )

            pygame.draw.ellipse(
                screen,
                YELLOW,
                (
                    x - 10,
                    y + 15,
                    20,
                    20
                )
            )

        elif self.type == "elite":

            pygame.draw.polygon(
                screen,
                PURPLE,
                [
                    (x, y),
                    (x - self.width // 2, y + self.height),
                    (x + self.width // 2, y + self.height)
                ]
            )

        elif self.type == "boss":

            pygame.draw.rect(
                screen,
                DARK_GRAY,
                (
                    x - self.width // 2,
                    y,
                    self.width,
                    self.height
                )
            )

            pygame.draw.rect(
                screen,
                YELLOW,
                (
                    x - self.width // 2,
                    y,
                    self.width,
                    25
                )
            )

            # Полоска здоровья
            bar_width = self.width

            pygame.draw.rect(
                screen,
                RED,
                (
                    x - bar_width // 2,
                    y - 25,
                    bar_width,
                    12
                )
            )

            pygame.draw.rect(
                screen,
                GREEN,
                (
                    x - bar_width // 2,
                    y - 25,
                    int(
                        bar_width
                        * self.hp
                        / self.max_hp
                    ),
                    12
                )
            )


# =========================
# СБРОС ПРОГРЕССА
# =========================

def reset_progress():

    global coins
    global run_coins
    global distance
    global last_boss_fifty
    global weapon_level
    global shield_time
    global game_state
    global current_skin

    coins = 0
    run_coins = 0
    distance = 0.0

    last_boss_fifty = 0

    weapon_level = 1

    shield_time = 0

    current_skin = "green"

    bullets.clear()
    enemies.clear()
    enemy_bullets.clear()

    player.x = float(WIDTH // 2)
    player.y = float(HEIGHT - 250)

    game_state = MENU


# =========================
# ТЕКСТ
# =========================

def draw_text(
    text,
    font,
    color,
    x,
    y,
    center=True
):

    surface = font.render(
        text,
        True,
        color
    )

    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


# =========================
# КНОПКА
# =========================

def draw_button(
    text,
    rect,
    color
):

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=15
    )

    draw_text(
        text,
        font_medium,
        WHITE,
        rect.centerx,
        rect.centery
    )


# =========================
# МЕНЮ
# =========================

def draw_menu():

    screen.fill(BLACK)

    draw_text(
        "ЗВЁЗДНЫЙ УВОРОТ",
        font_big,
        WHITE,
        WIDTH // 2,
        180
    )

    draw_text(
        f"Монеты: {coins}",
        font_small,
        YELLOW,
        WIDTH // 2,
        300
    )

    play_rect = pygame.Rect(
        100,
        450,
        WIDTH - 200,
        90
    )

    shop_rect = pygame.Rect(
        100,
        570,
        WIDTH - 200,
        90
    )

    reset_rect = pygame.Rect(
        100,
        int(HEIGHT * 0.71),
        WIDTH - 200,
        90
    )

    draw_button(
        "ИГРАТЬ",
        play_rect,
        GREEN
    )

    draw_button(
        "МАГАЗИН",
        shop_rect,
        BLUE
    )

    draw_button(
        "СБРОС ПРОГРЕССА",
        reset_rect,
        RED
    )


# =========================
# МАГАЗИН
# =========================

def draw_shop():

    screen.fill(BLACK)

    draw_text(
        "МАГАЗИН",
        font_big,
        WHITE,
        WIDTH // 2,
        100
    )

    draw_text(
        f"Монеты: {coins}",
        font_small,
        YELLOW,
        WIDTH // 2,
        180
    )

    draw_text(
        "СКИНЫ",
        font_medium,
        WHITE,
        WIDTH // 2,
        270
    )

    blue_rect = pygame.Rect(
        60,
        330,
        280,
        80
    )

    red_rect = pygame.Rect(
        380,
        330,
        280,
        80
    )

    yellow_rect = pygame.Rect(
        60,
        430,
        280,
        80
    )

    weapon_rect = pygame.Rect(
        380,
        430,
        280,
        80
    )

    shield_rect = pygame.Rect(
        60,
        540,
        WIDTH - 120,
        80
    )

    back_rect = pygame.Rect(
        60,
        HEIGHT - 130,
        WIDTH - 120,
        80
    )

    draw_button(
        "СИНИЙ 40",
        blue_rect,
        BLUE
    )

    draw_button(
        "КРАСНЫЙ 60",
        red_rect,
        RED
    )

    draw_button(
        "ЖЁЛТЫЙ 100",
        yellow_rect,
        YELLOW
    )

    draw_button(
        f"ОРУЖИЕ {weapon_level}/4",
        weapon_rect,
        PURPLE
    )

    draw_button(
        "ЩИТ 10 СЕК — 45",
        shield_rect,
        GREEN
    )

    draw_button(
        "НАЗАД",
        back_rect,
        GRAY
    )


# =========================
# ИГРА
# =========================

fire_timer = 0


def start_game():

    global game_state
    global distance
    global run_coins
    global last_boss_fifty
    global shield_time

    game_state = PLAYING

    distance = 0.0
    run_coins = 0
    last_boss_fifty = 0
    shield_time = 0

    bullets.clear()
    enemies.clear()
    enemy_bullets.clear()

    player.x = WIDTH // 2
    player.y = HEIGHT - 250


# =========================
# ИГРОВОЙ ЦИКЛ
# =========================

running = True

touching = False
touch_x = WIDTH // 2
touch_y = HEIGHT // 2


while running:

    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # =========================
        # НАЖАТИЯ
        # =========================

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos

            # -------------------------
            # МЕНЮ
            # -------------------------

            if game_state == MENU:

                play_rect = pygame.Rect(
                    100,
                    450,
                    WIDTH - 200,
                    90
                )

                shop_rect = pygame.Rect(
                    100,
                    570,
                    WIDTH - 200,
                    90
                )

                reset_rect = pygame.Rect(
                    100,
                    int(HEIGHT * 0.71),
                    WIDTH - 200,
                    90
                )

                if play_rect.collidepoint(mx, my):

                    start_game()

                elif shop_rect.collidepoint(mx, my):

                    game_state = SHOP

                elif reset_rect.collidepoint(mx, my):

                    reset_progress()

            # -------------------------
            # МАГАЗИН
            # -------------------------

            elif game_state == SHOP:

                blue_rect = pygame.Rect(
                    60,
                    330,
                    280,
                    80
                )

                red_rect = pygame.Rect(
                    380,
                    330,
                    280,
                    80
                )

                yellow_rect = pygame.Rect(
                    60,
                    430,
                    280,
                    80
                )

                weapon_rect = pygame.Rect(
                    380,
                    430,
                    280,
                    80
                )

                shield_rect = pygame.Rect(
                    60,
                    540,
                    WIDTH - 120,
                    80
                )

                back_rect = pygame.Rect(
                    60,
                    HEIGHT - 130,
                    WIDTH - 120,
                    80
                )

                if blue_rect.collidepoint(mx, my):

                    if coins >= 40:

                        coins -= 40
                        current_skin = "blue"
                        play_sound(shop_sound)

                elif red_rect.collidepoint(mx, my):

                    if coins >= 60:

                        coins -= 60
                        current_skin = "red"
                        play_sound(shop_sound)

                elif yellow_rect.collidepoint(mx, my):

                    if coins >= 100:

                        coins -= 100
                        current_skin = "yellow"
                        play_sound(shop_sound)

                elif weapon_rect.collidepoint(mx, my):

                    costs = {
                        1: 50,
                        2: 70,
                        3: 80
                    }

                    if weapon_level < 4:

                        cost = costs.get(
                            weapon_level,
                            80
                        )

                        if coins >= cost:

                            coins -= cost
                            weapon_level += 1

                            play_sound(shop_sound)

                elif shield_rect.collidepoint(mx, my):

                    if coins >= 45:

                        coins -= 45
                        shield_time = 600

                        play_sound(shop_sound)

                elif back_rect.collidepoint(mx, my):

                    game_state = MENU

            # -------------------------
            # GAMEOVER
            # -------------------------

            elif game_state == GAMEOVER:

                respawn_rect = pygame.Rect(
                    100,
                    500,
                    WIDTH - 200,
                    80
                )

                retry_rect = pygame.Rect(
                    100,
                    610,
                    WIDTH - 200,
                    80
                )

                menu_rect = pygame.Rect(
                    100,
                    720,
                    WIDTH - 200,
                    80
                )

                if respawn_rect.collidepoint(mx, my):

                    if coins >= 30:

                        coins -= 30

                        shield_time = 300

                        player.x = WIDTH // 2
                        player.y = HEIGHT - 250

                        enemies.clear()
                        bullets.clear()
                        enemy_bullets.clear()

                        game_state = PLAYING

                        play_sound(respawn_sound)

                elif retry_rect.collidepoint(mx, my):

                    start_game()

                elif menu_rect.collidepoint(mx, my):

                    game_state = MENU

        # =========================
        # TOUCH
        # =========================

        if event.type == pygame.MOUSEBUTTONDOWN:

            touching = True

            touch_x, touch_y = event.pos

        elif event.type == pygame.MOUSEMOTION:

            if touching:

                touch_x, touch_y = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:

            touching = False

    # =========================
    # PLAYING
    # =========================

    if game_state == PLAYING:

        distance += 0.05

        if shield_time > 0:

            shield_time -= 1

        # -------------------------
        # ДВИЖЕНИЕ ИГРОКА
        # -------------------------

        if touching:

            player.x += (
                touch_x - player.x
            ) * player.speed

            player.y += (
                touch_y - player.y
            ) * player.speed

        player.x = max(
            50,
            min(WIDTH - 50, player.x)
        )

        player.y = max(
            100,
            min(HEIGHT - 100, player.y)
        )

        # -------------------------
        # БОСС КАЖДЫЕ 100
        # -------------------------

        current_fifty = int(distance) // 100

        if (
            current_fifty > last_boss_fifty
            and int(distance) > 0
        ):

            enemies.append(
                Enemy("boss")
            )

            last_boss_fifty = current_fifty

        # -------------------------
        # ПОЯВЛЕНИЕ ВРАГОВ
        # -------------------------

        # 1 шанс из 40 за кадр
        if random.randint(1, 40) == 1:

            enemy_type = "normal"

            if random.randint(1, 10) == 1:

                enemy_type = "elite"

            enemies.append(
                Enemy(enemy_type)
            )

        # -------------------------
        # СТРЕЛЬБА
        # -------------------------

        fire_timer += 1

        if fire_timer >= 14:

            fire_timer = 0

            if weapon_level == 1:

                bullets.append(
                    Bullet(
                        player.x,
                        player.y - 55
                    )
                )

            elif weapon_level == 2:

                bullets.append(
                    Bullet(
                        player.x - 20,
                        player.y - 50
                    )
                )

                bullets.append(
                    Bullet(
                        player.x + 20,
                        player.y - 50
                    )
                )

            else:

                bullets.append(
                    Bullet(
                        player.x,
                        player.y - 55
                    )
                )

                bullets.append(
                    Bullet(
                        player.x - 25,
                        player.y - 45
                    )
                )

                bullets.append(
                    Bullet(
                        player.x + 25,
                        player.y - 45
                    )
                )

            play_sound(shoot_sound)

        # -------------------------
        # ОБНОВЛЕНИЕ ПУЛЬ
        # -------------------------

        for bullet in bullets[:]:

            bullet.update()

            if bullet.y < -50:

                bullets.remove(bullet)

        # -------------------------
        # ОБНОВЛЕНИЕ ВРАГОВ
        # -------------------------

        for enemy in enemies[:]:

            enemy.update()

            if enemy.y > HEIGHT + 200:

                enemies.remove(enemy)

        # -------------------------
        # ОБНОВЛЕНИЕ ПУЛЬ ВРАГОВ
        # -------------------------

        for bullet in enemy_bullets[:]:

            bullet.update()

            if bullet.y > HEIGHT + 50:

                enemy_bullets.remove(bullet)

        # -------------------------
        # ПУЛЯ → ВРАГ
        # -------------------------

        for bullet in bullets[:]:

            bullet_rect = pygame.Rect(
                int(bullet.x - 5),
                int(bullet.y),
                10,
                25
            )

            hit = False

            for enemy in enemies[:]:

                enemy_rect = pygame.Rect(
                    int(
                        enemy.x
                        - enemy.width / 2
                    ),
                    int(enemy.y),
                    enemy.width,
                    enemy.height
                )

                if bullet_rect.colliderect(
                    enemy_rect
                ):

                    enemy.hp -= 1

                    hit = True

                    if enemy.hp <= 0:

                        coins += enemy.reward
                        run_coins += enemy.reward

                        enemies.remove(enemy)

                        play_sound(
                            kill_sound
                        )

                    break

            if hit and bullet in bullets:

                bullets.remove(bullet)

        # -------------------------
        # ВРАГ → ИГРОК
        # -------------------------

        player_rect = pygame.Rect(
            int(player.x - 30),
            int(player.y - 50),
            60,
            90
        )

        if shield_time <= 0:

            for enemy in enemies[:]:

                enemy_rect = pygame.Rect(
                    int(
                        enemy.x
                        - enemy.width / 2
                    ),
                    int(enemy.y),
                    enemy.width,
                    enemy.height
                )

                if player_rect.colliderect(
                    enemy_rect
                ):

                    game_state = GAMEOVER
                    break

        # -------------------------
        # ПУЛЯ ВРАГА → ИГРОК
        # -------------------------

        if shield_time <= 0:

            for bullet in enemy_bullets[:]:

                bullet_rect = pygame.Rect(
                    int(bullet.x - 7),
                    int(bullet.y),
                    14,
                    30
                )

                if player_rect.colliderect(
                    bullet_rect
                ):

                    if bullet in enemy_bullets:
                        enemy_bullets.remove(
                            bullet
                        )

                    game_state = GAMEOVER
                    break

    # =========================
    # ОТРИСОВКА
    # =========================

    if game_state == MENU:

        draw_menu()

    elif game_state == SHOP:

        draw_shop()

    elif game_state == PLAYING:

        screen.fill(BLACK)

        # Звёзды
        random.seed(123)

        for i in range(80):

            x = random.randint(
                0,
                WIDTH
            )

            y = random.randint(
                0,
                HEIGHT
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (x, y),
                2
            )

        random.seed()

        for bullet in bullets:
            bullet.draw()

        for enemy in enemies:
            enemy.draw()

        for bullet in enemy_bullets:
            bullet.draw()

        player.draw()

        draw_text(
            f"Монеты: {coins}",
            font_small,
            YELLOW,
            20,
            20,
            False
        )

        draw_text(
            f"Дистанция: {int(distance)}",
            font_small,
            WHITE,
            20,
            65,
            False
        )

        draw_text(
            f"Оружие: {weapon_level}",
            font_small,
            WHITE,
            20,
            110,
            False
        )

        if shield_time > 0:

            draw_text(
                f"ЩИТ: {shield_time // 60 + 1}",
                font_small,
                BLUE,
                WIDTH - 20,
                20,
                False
            )

    elif game_state == GAMEOVER:

        screen.fill(BLACK)

        draw_text(
            "ИГРА ОКОНЧЕНА",
            font_big,
            RED,
            WIDTH // 2,
            250
        )

        draw_text(
            f"Дистанция: {int(distance)}",
            font_medium,
            WHITE,
            WIDTH // 2,
            350
        )

        draw_text(
            f"Заработано: {run_coins}",
            font_small,
            YELLOW,
            WIDTH // 2,
            410
        )

        respawn_rect = pygame.Rect(
            100,
            500,
            WIDTH - 200,
            80
        )

        retry_rect = pygame.Rect(
            100,
            610,
            WIDTH - 200,
            80
        )

        menu_rect = pygame.Rect(
            100,
            720,
            WIDTH - 200,
            80
        )

        draw_button(
            "ВОЗРОДИТЬСЯ — 30",
            respawn_rect,
            BLUE
        )

        draw_button(
            "ЗАНОВО",
            retry_rect,
            GREEN
        )

        draw_button(
            "В МЕНЮ",
            menu_rect,
            GRAY
        )

    pygame.display.flip()


pygame.quit()
sys.exit()
