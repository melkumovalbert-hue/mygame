import os
import sys
import math
import array
import random

import pygame

# ============================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================

try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.font.init()
except Exception as e:
    print(f"Ошибка инициализации: {e}")


# ============================================================
# СИНТЕЗАТОР ЗВУКОВ
# ============================================================

def create_synth_sound(freq_start, freq_end, duration,
                       wave_type='square', volume=0.3):
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h')

        for i in range(n_samples):
            t = float(i) / sample_rate
            progress = float(i) / n_samples
            freq = freq_start + (freq_end - freq_start) * progress

            if wave_type == 'square':
                val = 32767 if math.sin(
                    2 * math.pi * freq * t
                ) > 0 else -32768

            elif wave_type == 'saw':
                val = int(
                    32767 *
                    (2 * (t * freq - math.floor(t * freq + 0.5)))
                )

            elif wave_type == 'noise':
                val = random.randint(-32768, 32767)

            else:
                val = int(
                    32767 *
                    math.sin(2 * math.pi * freq * t)
                )

            env = 1.0 - progress
            buf.append(int(val * volume * env))

        return pygame.mixer.Sound(buffer=buf.tobytes())

    except Exception:
        return None


def safe_play(sound):
    if sound:
        try:
            sound.play()
        except Exception:
            pass


snd_shoot = create_synth_sound(
    800, 200, 0.06,
    wave_type='square',
    volume=0.15
)

snd_kill = create_synth_sound(
    250, 40, 0.14,
    wave_type='noise',
    volume=0.4
)

snd_shop = create_synth_sound(
    440, 660, 0.15,
    wave_type='sine',
    volume=0.3
)

snd_respawn = create_synth_sound(
    220, 700, 0.35,
    wave_type='sine',
    volume=0.4
)


# ============================================================
# ЭКРАН
# ============================================================

try:
    WIDTH, HEIGHT = 720, 1280

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Новое название игры
    pygame.display.set_caption("ЗВЁЗДНЫЙ УВОРОТ")

    clock = pygame.time.Clock()

    BLACK = (10, 10, 25)
    WHITE = (255, 255, 255)
    RED = (230, 50, 50)
    GREEN = (50, 230, 50)
    BLUE = (50, 150, 255)
    YELLOW = (255, 215, 0)
    PURPLE = (147, 112, 219)
    GRAY = (50, 50, 60)
    DARK_GRAY = (30, 30, 40)


    # ========================================================
    # ИКОНКА КОСМОЛЁТА
    # ========================================================

    try:
        icon = pygame.Surface((64, 64), pygame.SRCALPHA)

        # космос
        icon.fill((8, 8, 25, 255))

        # маленькие звёзды
        pygame.draw.circle(icon, WHITE, (10, 10), 2)
        pygame.draw.circle(icon, WHITE, (52, 13), 2)
        pygame.draw.circle(icon, WHITE, (15, 48), 2)
        pygame.draw.circle(icon, WHITE, (51, 50), 2)

        # огонь двигателя
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

        # крылья
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

        # корпус
        pygame.draw.polygon(
            icon,
            BLUE,
            [(32, 8), (22, 43), (32, 49), (42, 43)]
        )

        # кабина
        pygame.draw.ellipse(
            icon,
            (200, 240, 255),
            (27, 20, 10, 15)
        )

        pygame.display.set_icon(icon)

    except Exception:
        pass


    # ========================================================
    # ШРИФТЫ
    # ========================================================

    def get_safe_font(size):
        try:
            return pygame.font.Font(None, size)
        except Exception:
            return None


    font = get_safe_font(36)
    font_large = get_safe_font(52)


    # ========================================================
    # ПРОГРЕСС
    # ========================================================

    coins = 0
    run_coins = 0
    distance = 0.0
    last_boss_fifty = 0

    weapon_level = 1
    shield_time = 0

    game_state = "MENU"
    current_skin = "green"


    # ========================================================
    # ИГРОК
    # ========================================================

    class Player:

        def __init__(self):
            self.x = float(WIDTH // 2)
            self.y = float(HEIGHT - 250)

            self.width = 60
            self.height = 60

        def draw(self):

            if current_skin == "blue":
                main_color = (30, 144, 255)
                wing_color = (0, 100, 200)
                engine_color = (0, 255, 255)

            elif current_skin == "red":
                main_color = (255, 69, 0)
                wing_color = (178, 34, 34)
                engine_color = (255, 255, 0)

            elif current_skin == "yellow":
                main_color = (255, 215, 0)
                wing_color = (218, 165, 32)
                engine_color = (255, 100, 0)

            else:
                main_color = (50, 205, 50)
                wing_color = (34, 139, 34)
                engine_color = (0, 255, 127)

            px, py = int(self.x), int(self.y)

            # двигатели
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

            # крылья
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

            # корпус
            pygame.draw.polygon(
                screen,
                main_color,
                [
                    (px, py),
                    (px - 20, py + 55),
                    (px + 20, py + 55)
                ]
            )

            # кабина
            pygame.draw.ellipse(
                screen,
                WHITE,
                (px - 8, py + 20, 16, 25)
            )

            # щит
            if shield_time > 0:
                pygame.draw.circle(
                    screen,
                    BLUE,
                    (px, py + 30),
                    65,
                    4
                )


    # ========================================================
    # ПУЛЯ ИГРОКА
    # ========================================================

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


    # ========================================================
    # ПУЛЯ ВРАГА
    # ========================================================

    class EnemyBullet:

        def __init__(self, x, y, speed=8):
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


    # ========================================================
    # ВРАГ
    # ========================================================

    class Enemy:

        def __init__(self, type_str):

            self.type = type_str

            self.x = random.randint(80, WIDTH - 80)
            self.y = -80

            self.shoot_timer = random.randint(90, 160)

            if self.type == 'normal':

                self.width = 70
                self.height = 60
                self.hp = 4
                self.speed = random.randint(2, 4)
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
                            self.y + self.height // 2,
                            7
                        )
                    )

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x,
                            self.y + self.height // 2,
                            8
                        )
                    )

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x + 40,
                            self.y + self.height // 2,
                            7
                        )
                    )

            else:

                self.y += self.speed

                self.shoot_timer -= 1

                if self.shoot_timer <= 0:

                    self.shoot_timer = random.randint(100, 180)

                    enemy_bullets.append(
                        EnemyBullet(
                            self.x,
                            self.y + self.height // 2
                        )
                    )


        def draw(self):

            ex, ey = int(self.x), int(self.y)

            if self.type == 'normal':

                pygame.draw.ellipse(
                    screen,
                    self.color,
                    (ex - 35, ey - 15, 70, 30)
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


    # ========================================================
    # ОБЪЕКТЫ
    # ========================================================

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


    # ========================================================
    # КНОПКА
    # ========================================================

    def draw_btn(text, x, y, w, h, col=GRAY):

        pygame.draw.rect(
            screen,
            col,
            (x, y, w, h),
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
                    x + (w - txt.get_width()) // 2,
                    y + (h - txt.get_height()) // 2
                )
            )


    # ========================================================
    # ПОЛНЫЙ СБРОС ПРОГРЕССА
    # ========================================================

    def reset_progress():

        global coins
        global run_coins
        global distance
        global last_boss_fifty
        global weapon_level
        global shield_time
        global current_skin
        global game_state

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

        game_state = "MENU"


    # ========================================================
    # ГЛАВНЫЙ ЦИКЛ
    # ========================================================

    while running:

        screen.fill(BLACK)

        click_event = False

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


        # ====================================================
        # МЕНЮ
        # ====================================================

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
                        WIDTH // 2 - title.get_width() // 2,
                        HEIGHT // 5
                    )
                )


            draw_btn(
                "ИГРАТЬ",
                100,
                HEIGHT * 0.40,
                WIDTH - 200,
                90,
                BLUE
            )

            draw_btn(
                "МАГАЗИН",
                100,
                HEIGHT * 0.52,
                WIDTH - 200,
                90,
                GRAY
            )

            # НОВАЯ КНОПКА СБРОСА
            draw_btn(
                "СБРОС ПРОГРЕССА",
                100,
                HEIGHT * 0.64,
                WIDTH - 200,
                90,
                RED
            )


            if click_event:

                bx = 100
                bw = WIDTH - 200

                # ИГРАТЬ
                if (
                    bx < touch_pos[0] < bx + bw
                    and HEIGHT * 0.40 < touch_pos[1] < HEIGHT * 0.40 + 90
                ):

                    game_state = "PLAYING"

                    distance = 0.0
                    run_coins = 0
                    last_boss_fifty = 0

                    enemies.clear()
                    bullets.clear()
                    enemy_bullets.clear()

                    player.x = float(WIDTH // 2)
                    player.y = float(HEIGHT - 250)


                # МАГАЗИН
                elif (
                    bx < touch_pos[0] < bx + bw
                    and HEIGHT * 0.52 < touch_pos[1] < HEIGHT * 0.52 + 90
                ):

                    game_state = "SHOP"

                    safe_play(snd_shop)


                # СБРОС
                elif (
                    bx < touch_pos[0] < bx + bw
                    and HEIGHT * 0.64 < touch_pos[1] < HEIGHT * 0.64 + 90
                ):

                    reset_progress()


        # ====================================================
        # МАГАЗИН
        # ====================================================

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
                        WIDTH // 2 - title.get_width() // 2,
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


            if weapon_level == 1:

                weapon_cost = 50
                weapon_text = "Улучшить пушку (50)"

            elif weapon_level == 2:

                weapon_cost = 70
                weapon_text = "Улучшить пушку (70)"

            elif weapon_level == 3:

                weapon_cost = 80
                weapon_text = "Улучшить пушку (80)"

            else:

                weapon_cost = 999999
                weapon_text = "Пушка максимальна"


            draw_btn(
                "Синий скин (40)",
                70, 270,
                WIDTH - 140,
                75
            )

            draw_btn(
                "Огненный (60)",
                70, 360,
                WIDTH - 140,
                75
            )

            draw_btn(
                "Золотой (100)",
                70, 450,
                WIDTH - 140,
                75
            )

            draw_btn(
                weapon_text,
                70, 540,
                WIDTH - 140,
                75
            )

            draw_btn(
                "Щит 10 сек (45)",
                70, 630,
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


            if click_event:

                if 70 < touch_pos[0] < WIDTH - 70:

                    y = touch_pos[1]

                    if HEIGHT - 140 < y < HEIGHT - 60:

                        game_state = "MENU"

                    elif 270 < y < 345 and coins >= 40:

                        coins -= 40
                        current_skin = "blue"

                    elif 360 < y < 435 and coins >= 60:

                        coins -= 60
                        current_skin = "red"

                    elif 450 < y < 525 and coins >= 100:

                        coins -= 100
                        current_skin = "yellow"

                    elif (
                        540 < y < 615
                        and coins >= weapon_cost
                        and weapon_level < 4
                    ):

                        coins -= weapon_cost
                        weapon_level += 1

                    elif 630 < y < 705 and coins >= 45:

                        coins -= 45
                        shield_time = 600


        # ====================================================
        # ИГРА
        # ====================================================

        elif game_state == "PLAYING":

            distance += 0.05


            # БОСС КАЖДЫЕ 50
            current_fifty = int(distance) // 50

            if (
                current_fifty > last_boss_fifty
                and int(distance) > 0
            ):

                enemies.append(
                    Enemy('boss')
                )

                last_boss_fifty = current_fifty


            # УПРАВЛЕНИЕ
            if is_touching:

                player.x += (
                    float(touch_pos[0]) - player.x
                ) * 0.25

                player.y += (
                    float(touch_pos[1]) - player.y
                ) * 0.25

                player.x = max(
                    50,
                    min(float(WIDTH - 50), player.x)
                )

                player.y = max(
                    150,
                    min(float(HEIGHT - 150), player.y)
                )


            # СТРЕЛЬБА
            if fire_cooldown > 0:
                fire_cooldown -= 1


            if is_touching and fire_cooldown == 0:

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

                safe_play(snd_shoot)

                fire_cooldown = 14


            # =================================================
            # ПРИШЕЛЬЦЫ
            # БЫЛО: 1 из 28
            # СТАЛО: 1 из 40
            # =================================================

            if random.randint(1, 40) == 1:

                e_type = (
                    'normal'
                    if random.randint(1, 4) != 1
                    else 'elite'
                )

                enemies.append(
                    Enemy(e_type)
                )


            # ПУЛИ ИГРОКА
            for b in bullets[:]:

                b.update()
                b.draw()

                if b.y < 0:

                    if b in bullets:
                        bullets.remove(b)


            # ПУЛИ ВРАГОВ
            for eb in enemy_bullets[:]:

                eb.update()
                eb.draw()

                if (
                    abs(player.x - eb.x) < 30
                    and abs(player.y + 25 - eb.y) < 30
                ):

                    if shield_time > 0:

                        if eb in enemy_bullets:
                            enemy_bullets.remove(eb)

                    else:

                        coins += run_coins
                        run_coins = 0

                        game_state = "GAMEOVER"

                if eb.y > HEIGHT:

                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)


            # ВРАГИ
            for e in enemies[:]:

                e.update()
                e.draw()


                # СТОЛКНОВЕНИЕ
                if (
                    abs(player.x - e.x)
                    < (player.width + e.width) // 2
                    and
                    abs(player.y - e.y)
                    < (player.height + e.height) // 2
                ):

                    if shield_time > 0:

                        if e in enemies:
                            enemies.remove(e)

                    else:

                        coins += run_coins
                        run_coins = 0

                        game_state = "GAMEOVER"


                # ПОПАДАНИЕ ПУЛИ
                for b in bullets[:]:

                    if (
                        abs(b.x - e.x) < e.width // 2
                        and
                        abs(b.y - e.y) < e.height // 2
                    ):

                        e.hp -= 1

                        if b in bullets:
                            bullets.remove(b)

                        if e.hp <= 0:

                            run_coins += e.reward

                            safe_play(snd_kill)

                            if e in enemies:
                                enemies.remove(e)

                            break


                # УШЁЛ ЗА ЭКРАН
                if e.y > HEIGHT + 100:

                    if e in enemies:
                        enemies.remove(e)


            # ЩИТ
            if shield_time > 0:
                shield_time -= 1


            # ИНФОРМАЦИЯ
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


        # ====================================================
        # ИГРА ОКОНЧЕНА
        # ====================================================

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
                        WIDTH // 2 - title.get_width() // 2,
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
                        WIDTH // 2 - txt_res.get_width() // 2,
                        HEIGHT * 0.33
                    )
                )

                screen.blit(
                    txt_tot,
                    (
                        WIDTH // 2 - txt_tot.get_width() // 2,
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

                bx = 70
                bw = WIDTH - 140


                # ВОЗРОЖДЕНИЕ
                if (
                    bx < touch_pos[0] < bx + bw
                    and
                    HEIGHT * 0.52
                    < touch_pos[1]
                    < HEIGHT * 0.52 + 75
                    and coins >= 30
                ):

                    coins -= 30

                    shield_time = 300

                    enemies.clear()
                    enemy_bullets.clear()

                    player.x = float(WIDTH // 2)
                    player.y = float(HEIGHT - 250)

                    game_state = "PLAYING"

                    safe_play(snd_respawn)


                # ЕЩЁ РАЗ
                elif (
                    bx < touch_pos[0] < bx + bw
                    and
                    HEIGHT * 0.63
                    < touch_pos[1]
                    < HEIGHT * 0.63 + 75
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
                    bx < touch_pos[0] < bx + bw
                    and
                    HEIGHT * 0.74
                    < touch_pos[1]
                    < HEIGHT * 0.74 + 75
                ):

                    game_state = "MENU"


        pygame.display.flip()

        clock.tick(60)


except Exception as e:

    print(
        f"Ошибка во время игры: {e}"
    )

finally:

    pygame.quit()
    sys.exit()2
