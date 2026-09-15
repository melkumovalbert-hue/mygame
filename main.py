import os
import sys
import math
import array
import random

try:
    import pygame

    # ============================================================
    # ИНИЦИАЛИЗАЦИЯ
    # ============================================================

    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    try:
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        SOUND_ENABLED = True
    except Exception:
        SOUND_ENABLED = False

    WIDTH, HEIGHT = 720, 1280
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ЗВЁЗДНЫЙ УВОРОТ")

    clock = pygame.time.Clock()

    # ============================================================
    # ЦВЕТА
    # ============================================================

    BLACK = (10, 10, 25)
    WHITE = (255, 255, 255)
    RED = (230, 50, 50)
    GREEN = (50, 230, 50)
    BLUE = (50, 150, 255)
    YELLOW = (255, 215, 0)
    PURPLE = (147, 112, 219)
    GRAY = (50, 50, 60)
    DARK_GRAY = (30, 30, 40)

    # ============================================================
    # ШРИФТЫ
    # ============================================================

    def get_safe_font(size):
        for name in ['arial', 'sans-serif', 'freesans', None]:
            try:
                f = pygame.font.SysFont(name, size)
                if f:
                    return f
            except:
                continue

        try:
            return pygame.font.Font(None, size)
        except:
            return None

    font = get_safe_font(36)
    font_large = get_safe_font(52)

    # ============================================================
    # ЗВУКИ
    # ============================================================

    def make_tone(frequency, duration, volume=0.25):
        if not SOUND_ENABLED:
            return None

        sample_rate = 44100
        samples = int(sample_rate * duration)

        buf = array.array('h')

        attack = max(1, int(samples * 0.08))
        release = max(1, int(samples * 0.18))

        for i in range(samples):
            t = i / sample_rate

            if i < attack:
                envelope = i / attack
            elif i > samples - release:
                envelope = max(
                    0.0,
                    (samples - i) / release
                )
            else:
                envelope = 1.0

            value = (
                math.sin(
                    2 * math.pi * frequency * t
                )
                * volume
                * envelope
            )

            buf.append(int(value * 32767))

        try:
            return pygame.mixer.Sound(
                buffer=buf.tobytes()
            )
        except:
            return None

    def make_sweep(
        start_freq,
        end_freq,
        duration,
        volume=0.20
    ):
        if not SOUND_ENABLED:
            return None

        sample_rate = 44100
        samples = int(sample_rate * duration)

        buf = array.array('h')

        attack = max(1, int(samples * 0.04))
        release = max(1, int(samples * 0.25))

        phase = 0.0

        for i in range(samples):

            progress = i / max(
                1,
                samples - 1
            )

            freq = (
                start_freq
                + (end_freq - start_freq)
                * progress
            )

            phase += (
                2 * math.pi
                * freq
                / sample_rate
            )

            if i < attack:
                envelope = i / attack
            elif i > samples - release:
                envelope = max(
                    0.0,
                    (samples - i) / release
                )
            else:
                envelope = 1.0

            sample = (
                math.sin(phase) * 0.75
                + math.sin(phase * 2.0) * 0.20
            )

            value = (
                sample
                * volume
                * envelope
            )

            buf.append(int(value * 32767))

        try:
            return pygame.mixer.Sound(
                buffer=buf.tobytes()
            )
        except:
            return None

    def make_sequence(notes, volume=0.25):
        if not SOUND_ENABLED:
            return None

        sample_rate = 44100
        buf = array.array('h')

        for frequency, duration in notes:

            samples = int(
                sample_rate * duration
            )

            attack = max(
                1,
                int(samples * 0.06)
            )

            release = max(
                1,
                int(samples * 0.20)
            )

            for i in range(samples):

                t = i / sample_rate

                if i < attack:
                    envelope = i / attack

                elif i > samples - release:
                    envelope = max(
                        0.0,
                        (samples - i) / release
                    )

                else:
                    envelope = 1.0

                wave = (
                    math.sin(
                        2
                        * math.pi
                        * frequency
                        * t
                    ) * 0.78
                    +
                    math.sin(
                        2
                        * math.pi
                        * frequency
                        * 2
                        * t
                    ) * 0.18
                )

                value = (
                    wave
                    * volume
                    * envelope
                )

                buf.append(
                    int(value * 32767)
                )

        try:
            return pygame.mixer.Sound(
                buffer=buf.tobytes()
            )
        except:
            return None

    def make_cash_sound():
        # Синтезированный звук "ча-чин"
        if not SOUND_ENABLED:
            return None

        sample_rate = 44100

        parts = [
            (880, 0.07),
            (1320, 0.08),
            (1760, 0.12),
            (2200, 0.07)
        ]

        buf = array.array('h')

        for frequency, duration in parts:

            samples = int(
                sample_rate * duration
            )

            for i in range(samples):

                t = i / sample_rate

                attack = min(
                    1.0,
                    i / 500.0
                )

                release = min(
                    1.0,
                    (samples - i) / 1200.0
                )

                envelope = min(
                    attack,
                    release
                )

                wave = (
                    math.sin(
                        2
                        * math.pi
                        * frequency
                        * t
                    ) * 0.65
                    +
                    math.sin(
                        2
                        * math.pi
                        * frequency
                        * 2
                        * t
                    ) * 0.20
                    +
                    math.sin(
                        2
                        * math.pi
                        * frequency
                        * 3
                        * t
                    ) * 0.08
                )

                value = (
                    wave
                    * 0.24
                    * envelope
                )

                buf.append(
                    int(value * 32767)
                )

        try:
            return pygame.mixer.Sound(
                buffer=buf.tobytes()
            )
        except:
            return None

    # ============================================================
    # ГОТОВЫЕ ЗВУКИ
    # ============================================================

    shoot_sound = make_sweep(
        1550,
        550,
        0.085,
        0.18
    )

    kill_sound = make_sequence(
        [
            (620, 0.045),
            (900, 0.055),
            (1350, 0.075),
            (1750, 0.045)
        ],
        0.34
    )

    buy_sound = make_cash_sound()

    shield_sound = make_sequence(
        [
            (500, 0.08),
            (750, 0.08),
            (1000, 0.12)
        ],
        0.24
    )

    respawn_sound = make_sequence(
        [
            (350, 0.10),
            (500, 0.10),
            (700, 0.12),
            (900, 0.14)
        ],
        0.25
    )

    boss_sound = make_sequence(
        [
            (180, 0.16),
            (140, 0.16),
            (110, 0.20)
        ],
        0.28
    )

    hit_sound = make_sweep(
        500,
        180,
        0.10,
        0.16
    )

    def play_sound(sound):
        if SOUND_ENABLED and sound is not None:
            try:
                channel = pygame.mixer.find_channel(
                    True
                )

                if channel:
                    channel.play(sound)

            except:
                try:
                    sound.play()
                except:
                    pass

    # ============================================================
    # ПЕРЕМЕННЫЕ ИГРЫ
    # ============================================================

    coins = 0
    run_coins = 0
    distance = 0.0
    last_boss_fifty = 0
    weapon_level = 1
    shield_time = 0
    game_state = "MENU"
    current_skin = "green"

    # ============================================================
    # ИГРОК
    # ============================================================

    class Player:

        def __init__(self):
            self.x = float(WIDTH // 2)
            self.y = float(HEIGHT - 250)
            self.width = 60
            self.height = 60

        def draw(self):

            if current_skin == "blue":

                main_color = (
                    30,
                    144,
                    255
                )

                wing_color = (
                    0,
                    100,
                    200
                )

                engine_color = (
                    0,
                    255,
                    255
                )

            elif current_skin == "red":

                main_color = (
                    255,
                    69,
                    0
                )

                wing_color = (
                    178,
                    34,
                    34
                )

                engine_color = (
                    255,
                    255,
                    0
                )

            elif current_skin == "yellow":

                main_color = (
                    255,
                    215,
                    0
                )

                wing_color = (
                    218,
                    165,
                    32
                )

                engine_color = (
                    255,
                    100,
                    0
                )

            else:

                main_color = (
                    50,
                    205,
                    50
                )

                wing_color = (
                    34,
                    139,
                    34
                )

                engine_color = (
                    0,
                    255,
                    127
                )

            px = int(self.x)
            py = int(self.y)

            pygame.draw.polygon(
                screen,
                engine_color,
                [
                    (px - 15, py + 50),
                    (px - 5, py + 70),
                    (px - 25, py + 70)
                ]
            )

            pygame.draw.polygon(
                screen,
                engine_color,
                [
                    (px + 15, py + 50),
                    (px + 5, py + 70),
                    (px + 25, py + 70)
                ]
            )

            pygame.draw.polygon(
                screen,
                wing_color,
                [
                    (px, py + 10),
                    (px - 45, py + 55),
                    (px - 15, py + 45)
                ]
            )

            pygame.draw.polygon(
                screen,
                wing_color,
                [
                    (px, py + 10),
                    (px + 45, py + 55),
                    (px + 15, py + 45)
                ]
            )

            pygame.draw.polygon(
                screen,
                main_color,
                [
                    (px, py),
                    (px - 20, py + 55),
                    (px + 20, py + 55)
                ]
            )

            pygame.draw.ellipse(
                screen,
                WHITE,
                (
                    px - 8,
                    py + 20,
                    16,
                    25
                )
            )

            if shield_time > 0:

                pygame.draw.circle(
                    screen,
                    BLUE,
                    (px, py + 30),
                    65,
                    4
                )

    # ============================================================
    # ПУЛЯ ИГРОКА
    # ============================================================

    class Bullet:

        def __init__(self, x, y):
            self.x = x
            self.y = y

        def update(self):
            self.y -= 22

        def draw(self):

            pygame.draw.rect(
                screen,
                YELLOW,
                (
                    int(self.x - 4),
                    int(self.y - 15),
                    8,
                    20
                ),
                border_radius=3
            )

    # ============================================================
    # ПУЛЯ ВРАГА
    # ============================================================

    class EnemyBullet:

        def __init__(
            self,
            x,
            y,
            speed=8
        ):

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
                    int(self.x - 4),
                    int(self.y),
                    8,
                    16
                ),
                border_radius=3
            )

    # ============================================================
    # ВРАГ
    # ============================================================

    class Enemy:

        def __init__(self, type_str):

            self.type = type_str

            self.x = random.randint(
                80,
                WIDTH - 80
            )

            self.y = -80

            self.shoot_timer = random.randint(
                90,
                160
            )

            if self.type == 'normal':

                self.width = 70
                self.height = 60

                self.hp = 4

                self.speed = random.randint(
                    2,
                    4
                )

                self.color = RED
                self.reward = 1

            elif self.type == 'elite':

                self.width = 95
                self.height = 80

                self.hp = 8

                self.speed = 2

                self.color = PURPLE
                self.reward = 3

            elif self.type == 'boss':

                self.width = 180
                self.height = 120

                self.hp = 50

                self.speed = 1

                self.color = YELLOW
                self.reward = 10

                self.is_stopped = False
                self.shoot_timer = 50

        def update(self):

            if self.type == 'boss':

                if not self.is_stopped:

                    self.y += self.speed

                    if self.y >= 200:
                        self.is_stopped = True

                self.shoot_timer -= 1

                if self.shoot_timer <= 0:

                    self.shoot_timer = 65

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x - 40,
                            self.y
                            + self.height // 2,
                            7
                        )
                    )

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x,
                            self.y
                            + self.height // 2,
                            8
                        )
                    )

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x + 40,
                            self.y
                            + self.height // 2,
                            7
                        )
                    )

            else:

                self.y += self.speed

                self.shoot_timer -= 1

                if self.shoot_timer <= 0:

                    self.shoot_timer = random.randint(
                        100,
                        180
                    )

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x,
                            self.y
                            + self.height // 2
                        )
                    )

        def draw(self):

            ex = int(self.x)
            ey = int(self.y)

            if self.type == 'normal':

                pygame.draw.ellipse(
                    screen,
                    self.color,
                    (
                        ex - 35,
                        ey - 15,
                        70,
                        30
                    )
                )

                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (ex, ey),
                    6
                )

            elif self.type == 'elite':

                pygame.draw.polygon(
                    screen,
                    self.color,
                    [
                        (ex, ey + 30),
                        (ex - 45, ey - 20),
                        (ex + 45, ey - 20)
                    ]
                )

            elif self.type == 'boss':

                pygame.draw.rect(
                    screen,
                    DARK_GRAY,
                    (
                        ex - 90,
                        ey - 45,
                        180,
                        90
                    ),
                    border_radius=15
                )

                pygame.draw.rect(
                    screen,
                    self.color,
                    (
                        ex - 60,
                        ey - 60,
                        120,
                        30
                    ),
                    border_radius=8
                )

    # ============================================================
    # ОБЪЕКТЫ
    # ============================================================

    player = Player()

    bullets = []
    enemy_bullets = []
    enemies = []

    touch_pos = (
        WIDTH // 2,
        HEIGHT - 250
    )

    is_touching = False
    fire_cooldown = 0
    running = True

    # ============================================================
    # КНОПКА
    # ============================================================

    def draw_btn(
        text,
        x,
        y,
        w,
        h,
        col=GRAY
    ):

        pygame.draw.rect(
            screen,
            col,
            (
                x,
                y,
                w,
                h
            ),
            border_radius=15
        )

        if font:

            txt = font.render(
                text,
                True,
                WHITE
            )

            screen.blit(
                txt,
                (
                    x
                    + (w - txt.get_width())
                    // 2,

                    y
                    + (h - txt.get_height())
                    // 2
                )
            )

    # ============================================================
    # СБРОС ПРОГРЕССА
    # ============================================================

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

        player.x = float(
            WIDTH // 2
        )

        player.y = float(
            HEIGHT - 250
        )

        game_state = "MENU"

    # ============================================================
    # ГЛАВНЫЙ ЦИКЛ
    # ============================================================

    while running:

        screen.fill(BLACK)

        click_event = False

        # ========================================================
        # СОБЫТИЯ
        # ========================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                click_event = True
                is_touching = True
                touch_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:

                is_touching = False

            elif event.type == pygame.MOUSEMOTION:

                if is_touching:
                    touch_pos = event.pos

        # ========================================================
        # МЕНЮ
        # ========================================================

        if game_state == "MENU":

            if font_large:

                title = font_large.render(
                    "ЗВЁЗДНЫЙ УВОРОТ",
                    True,
                    WHITE
                )

                screen.blit(
                    title,
                    (
                        WIDTH // 2
                        - title.get_width() // 2,
                        HEIGHT // 4
                    )
                )

            # ----------------------------------------------------
            # КНОПКИ МЕНЮ
            # ----------------------------------------------------

            play_x = 100
            play_y = HEIGHT * 0.45
            play_w = WIDTH - 200
            play_h = 90

            shop_x = 100
            shop_y = HEIGHT * 0.58
            shop_w = WIDTH - 200
            shop_h = 90

            reset_x = 100
            reset_y = HEIGHT * 0.71
            reset_w = WIDTH - 200
            reset_h = 90

            draw_btn(
                "ИГРАТЬ",
                play_x,
                play_y,
                play_w,
                play_h,
                BLUE
            )

            draw_btn(
                "МАГАЗИН",
                shop_x,
                shop_y,
                shop_w,
                shop_h,
                GRAY
            )

            draw_btn(
                "СБРОС ПРОГРЕССА",
                reset_x,
                reset_y,
                reset_w,
                reset_h,
                RED
            )

            # ----------------------------------------------------
            # ИСПРАВЛЕННОЕ НАЖАТИЕ КНОПОК
            # ----------------------------------------------------

            if click_event:

                mx, my = touch_pos

                # ИГРАТЬ
                if (
                    play_x <= mx <= play_x + play_w
                    and
                    play_y <= my <= play_y + play_h
                ):

                    game_state = "PLAYING"

                    distance = 0.0
                    run_coins = 0
                    last_boss_fifty = 0

                    enemies.clear()
                    bullets.clear()
                    enemy_bullets.clear()

                    player.x = float(
                        WIDTH // 2
                    )

                    player.y = float(
                        HEIGHT - 250
                    )

                # МАГАЗИН
                elif (
                    shop_x <= mx <= shop_x + shop_w
                    and
                    shop_y <= my <= shop_y + shop_h
                ):

                    game_state = "SHOP"

                # СБРОС ПРОГРЕССА
                elif (
                    reset_x <= mx <= reset_x + reset_w
                    and
                    reset_y <= my <= reset_y + reset_h
                ):

                    reset_progress()

        # ========================================================
        # МАГАЗИН
        # ========================================================

        elif game_state == "SHOP":

            if font_large:

                title = font_large.render(
                    "МАГАЗИН",
                    True,
                    WHITE
                )

                screen.blit(
                    title,
                    (
                        WIDTH // 2
                        - title.get_width() // 2,
                        60
                    )
                )

            if font:

                t_coins = font.render(
                    f"Монеты: {coins}",
                    True,
                    YELLOW
                )

                screen.blit(
                    t_coins,
                    (60, 140)
                )

            # ----------------------------------------------------
            # ЦЕНА ПУШКИ
            # ----------------------------------------------------

            if weapon_level == 1:

                weapon_cost = 50
                weapon_text = (
                    "Улучшить пушку (50)"
                )

            elif weapon_level == 2:

                weapon_cost = 70
                weapon_text = (
                    "Улучшить пушку (70)"
                )

            elif weapon_level == 3:

                weapon_cost = 80
                weapon_text = (
                    "Улучшить пушку (80)"
                )

            else:

                weapon_cost = 999999
                weapon_text = (
                    "Пушка максимальна"
                )

            draw_btn(
                "Синий скин (40)",
                70,
                270,
                WIDTH - 140,
                75
            )

            draw_btn(
                "Огненный (60)",
                70,
                360,
                WIDTH - 140,
                75
            )

            draw_btn(
                "Золотой (100)",
                70,
                450,
                WIDTH - 140,
                75
            )

            draw_btn(
                weapon_text,
                70,
                540,
                WIDTH - 140,
                75
            )

            draw_btn(
                "Щит 10 сек (45)",
                70,
                630,
                WIDTH - 140,
                75
            )

            draw_btn(
                "НАЗАД",
                70,
                HEIGHT - 140,
                WIDTH - 140,
                80,
                RED
            )

            # ----------------------------------------------------
            # ПОКУПКИ
            # ----------------------------------------------------

            if click_event:

                mx, my = touch_pos

                if (
                    70 <= mx <= WIDTH - 70
                ):

                    # НАЗАД
                    if (
                        HEIGHT - 140
                        <= my
                        <= HEIGHT - 60
                    ):

                        game_state = "MENU"

                    # СИНИЙ СКИН
                    elif (
                        270 <= my <= 345
                        and coins >= 40
                    ):

                        coins -= 40
                        current_skin = "blue"

                        play_sound(
                            buy_sound
                        )

                    # ОГНЕННЫЙ СКИН
                    elif (
                        360 <= my <= 435
                        and coins >= 60
                    ):

                        coins -= 60
                        current_skin = "red"

                        play_sound(
                            buy_sound
                        )

                    # ЗОЛОТОЙ СКИН
                    elif (
                        450 <= my <= 525
                        and coins >= 100
                    ):

                        coins -= 100
                        current_skin = "yellow"

                        play_sound(
                            buy_sound
                        )

                    # ПУШКА
                    elif (
                        540 <= my <= 615
                        and coins >= weapon_cost
                        and weapon_level < 4
                    ):

                        coins -= weapon_cost
                        weapon_level += 1

                        play_sound(
                            buy_sound
                        )

                    # ЩИТ
                    elif (
                        630 <= my <= 705
                        and coins >= 45
                    ):

                        coins -= 45
                        shield_time = 600

                        play_sound(
                            shield_sound
                        )

        # ========================================================
        # ИГРА
        # ========================================================

        elif game_state == "PLAYING":

            distance += 0.05

            # БОССЫ КАЖДЫЕ 100
            current_fifty = (
                int(distance) // 100
            )

            if (
                current_fifty > last_boss_fifty
                and int(distance) > 0
            ):

                enemies.append(
                    Enemy('boss')
                )

                last_boss_fifty = current_fifty

                play_sound(
                    boss_sound
                )

            # ----------------------------------------------------
            # УПРАВЛЕНИЕ
            # ----------------------------------------------------

            if is_touching:

                player.x += (
                    float(touch_pos[0])
                    - player.x
                ) * 0.25

                player.y += (
                    float(touch_pos[1])
                    - player.y
                ) * 0.25

                player.x = max(
                    50,
                    min(
                        float(WIDTH - 50),
                        player.x
                    )
                )

                player.y = max(
                    150,
                    min(
                        float(HEIGHT - 150),
                        player.y
                    )
                )

            # ----------------------------------------------------
            # СТРЕЛЬБА
            # ----------------------------------------------------

            if fire_cooldown > 0:
                fire_cooldown -= 1

            if (
                is_touching
                and fire_cooldown == 0
            ):

                if weapon_level == 1:

                    bullets.append(
                        Bullet(
                            player.x,
                            player.y
                        )
                    )

                elif weapon_level == 2:

                    bullets.append(
                        Bullet(
                            player.x - 15,
                            player.y
                        )
                    )

                    bullets.append(
                        Bullet(
                            player.x + 15,
                            player.y
                        )
                    )

                else:

                    bullets.append(
                        Bullet(
                            player.x,
                            player.y
                        )
                    )

                    bullets.append(
                        Bullet(
                            player.x - 20,
                            player.y
                        )
                    )

                    bullets.append(
                        Bullet(
                            player.x + 20,
                            player.y
                        )
                    )

                fire_cooldown = 14

                play_sound(
                    shoot_sound
                )

            # ----------------------------------------------------
            # ПОЯВЛЕНИЕ ВРАГОВ
            # ----------------------------------------------------

            if random.randint(1, 40) == 1:

                e_type = (
                    'normal'
                    if random.randint(1, 4) != 1
                    else 'elite'
                )

                enemies.append(
                    Enemy(e_type)
                )

            # ----------------------------------------------------
            # ПУЛИ ИГРОКА
            # ----------------------------------------------------

            for b in bullets[:]:

                b.update()
                b.draw()

                if b.y < 0:

                    if b in bullets:
                        bullets.remove(b)

            # ----------------------------------------------------
            # ПУЛИ ВРАГОВ
            # ----------------------------------------------------

            for eb in enemy_bullets[:]:

                eb.update()
                eb.draw()

                if (
                    abs(player.x - eb.x) < 30
                    and
                    abs(
                        player.y + 25
                        - eb.y
                    ) < 30
                ):

                    if shield_time > 0:

                        if eb in enemy_bullets:
                            enemy_bullets.remove(eb)

                    else:

                        coins += run_coins
                        run_coins = 0

                        play_sound(
                            hit_sound
                        )

                        game_state = "GAMEOVER"

                if eb.y > HEIGHT:

                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)

            # ----------------------------------------------------
            # ВРАГИ
            # ----------------------------------------------------

            for e in enemies[:]:

                e.update()
                e.draw()

                # СТОЛКНОВЕНИЕ
                if (
                    abs(player.x - e.x)
                    <
                    (
                        player.width
                        + e.width
                    ) // 2
                    and
                    abs(player.y - e.y)
                    <
                    (
                        player.height
                        + e.height
                    ) // 2
                ):

                    if shield_time > 0:

                        if e in enemies:
                            enemies.remove(e)

                    else:

                        coins += run_coins
                        run_coins = 0

                        play_sound(
                            hit_sound
                        )

                        game_state = "GAMEOVER"

                # ПОПАДАНИЕ ПУЛИ
                for b in bullets[:]:

                    if (
                        abs(b.x - e.x)
                        < e.width // 2
                        and
                        abs(b.y - e.y)
                        < e.height // 2
                    ):

                        e.hp -= 1

                        if b in bullets:
                            bullets.remove(b)

                        # УНИЧТОЖЕНИЕ ВРАГА
                        if e.hp <= 0:

                            run_coins += e.reward

                            if e in enemies:
                                enemies.remove(e)

                            # Отдельный звук убийства
                            play_sound(
                                kill_sound
                            )

                            break

                if e.y > HEIGHT + 100:

                    if e in enemies:
                        enemies.remove(e)

            # ----------------------------------------------------
            # ЩИТ
            # ----------------------------------------------------

            if shield_time > 0:
                shield_time -= 1

            # ----------------------------------------------------
            # ИНФОРМАЦИЯ
            # ----------------------------------------------------

            if font:

                txt_d = font.render(
                    f"Дист: {int(distance)}",
                    True,
                    WHITE
                )

                txt_c = font.render(
                    f"Монеты: {run_coins}",
                    True,
                    YELLOW
                )

                screen.blit(
                    txt_d,
                    (40, 40)
                )

                screen.blit(
                    txt_c,
                    (WIDTH - 260, 40)
                )

            player.draw()

        # ========================================================
        # GAME OVER
        # ========================================================

        elif game_state == "GAMEOVER":

            if font_large:

                title = font_large.render(
                    "ИГРА ОКОНЧЕНА",
                    True,
                    RED
                )

                screen.blit(
                    title,
                    (
                        WIDTH // 2
                        - title.get_width() // 2,
                        HEIGHT * 0.2
                    )
                )

            if font:

                txt_res = font.render(
                    f"Пройдено: {int(distance)}",
                    True,
                    WHITE
                )

                txt_tot = font.render(
                    f"Всего монет: {coins}",
                    True,
                    YELLOW
                )

                screen.blit(
                    txt_res,
                    (
                        WIDTH // 2
                        - txt_res.get_width() // 2,
                        HEIGHT * 0.33
                    )
                )

                screen.blit(
                    txt_tot,
                    (
                        WIDTH // 2
                        - txt_tot.get_width() // 2,
                        HEIGHT * 0.40
                    )
                )

            draw_btn(
                "ВОЗРОДИТЬСЯ (30)",
                70,
                HEIGHT * 0.52,
                WIDTH - 140,
                75,
                GREEN
            )

            draw_btn(
                "ЕЩЕ РАЗ",
                70,
                HEIGHT * 0.63,
                WIDTH - 140,
                75,
                BLUE
            )

            draw_btn(
                "В МЕНЮ",
                70,
                HEIGHT * 0.74,
                WIDTH - 140,
                75,
                GRAY
            )

            if click_event:

                mx, my = touch_pos

                if (
                    70 <= mx <= WIDTH - 70
                ):

                    # ВОЗРОДИТЬСЯ
                    if (
                        HEIGHT * 0.52
                        <= my
                        <= HEIGHT * 0.52 + 75
                        and coins >= 30
                    ):

                        coins -= 30

                        shield_time = 300

                        enemies.clear()
                        enemy_bullets.clear()

                        player.x = float(
                            WIDTH // 2
                        )

                        player.y = float(
                            HEIGHT - 250
                        )

                        game_state = "PLAYING"

                        play_sound(
                            respawn_sound
                        )

                    # ЕЩЕ РАЗ
                    elif (
                        HEIGHT * 0.63
                        <= my
                        <= HEIGHT * 0.63 + 75
                    ):

                        distance = 0.0
                        run_coins = 0
                        last_boss_fifty = 0

                        enemies.clear()
                        bullets.clear()
                        enemy_bullets.clear()

                        game_state = "PLAYING"

                    # В МЕНЮ
                    elif (
                        HEIGHT * 0.74
                        <= my
                        <= HEIGHT * 0.74 + 75
                    ):

                        game_state = "MENU"

        # ========================================================
        # ЭКРАН
        # ========================================================

        pygame.display.flip()

        # FPS НЕ МЕНЯЛ
        clock.tick(60)

except Exception as e:

    print(
        f"Ошибка: {e}"
    )

finally:

    try:
        pygame.quit()
    except:
        pass

    sys.exit()
