import os
import sys
import random
import math
import array
import pygame

# 1. Защищенная инициализация звука для Android
os.environ['SDL_AUDIODRIVER'] = 'dummy' if not os.environ.get('SDL_AUDIODRIVER') else os.environ['SDL_AUDIODRIVER']

try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.font.init()
except Exception as e:
    print(f"Ошибка инициализации Pygame: {e}")

# --- Генератор звуковых эффектов в памяти (без внешних файлов .wav) ---
def create_synth_sound(freq_start, freq_end, duration, wave_type='square', volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        progress = float(i) / n_samples
        freq = freq_start + (freq_end - freq_start) * progress
        
        if wave_type == 'square':
            val = 32767 if math.sin(2 * math.pi * freq * t) > 0 else -32768
        elif wave_type == 'saw':
            val = int(32767 * (2 * (t * freq - math.floor(t * freq + 0.5))))
        elif wave_type == 'noise':
            val = random.randint(-32768, 32767)
        else:  # sine
            val = int(32767 * math.sin(2 * math.pi * freq * t))
            
        env = 1.0 - progress  # плавное затухание
        buf.append(int(val * volume * env))
        
    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def safe_play(sound):
    if sound:
        try:
            sound.play()
        except Exception:
            pass

# Инициализация звуков
snd_kill = create_synth_sound(300, 50, 0.15, wave_type='noise', volume=0.4)       # Убийство
snd_buy = create_synth_sound(600, 900, 0.12, wave_type='square', volume=0.3)      # Покупка
snd_boss = create_synth_sound(120, 60, 0.6, wave_type='saw', volume=0.5)          # Появление босса
snd_upgrade = create_synth_sound(400, 800, 0.25, wave_type='sine', volume=0.4)    # Улучшение
snd_respawn = create_synth_sound(200, 600, 0.35, wave_type='sine', volume=0.4)    # Возрождение
snd_shield = create_synth_sound(500, 550, 0.2, wave_type='saw', volume=0.3)       # Активация щита

# 2. Разрешение экрана
info = pygame.display.Info()
WIDTH = info.current_w if info.current_w > 0 else 720
HEIGHT = info.current_h if info.current_h > 0 else 1280

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Безопасный встроенный шрифт
def get_safe_font(size):
    return pygame.font.Font(None, size)

font = get_safe_font(36)
font_large = get_safe_font(52)

# Цвета
BLACK = (10, 10, 25)
WHITE = (255, 255, 255)
RED = (235, 50, 50)
GREEN = (50, 230, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)

# Состояние игры и ресурсы
coins = 0
run_coins = 0
distance = 0.0
last_boss_fifty = 0
weapon_level = 1
shield_time = 0
game_state = "MENU"  # MENU, PLAYING, SHOP, GAMEOVER
current_skin = "green"

class Player:
    def __init__(self):
        self.width = 60
        self.height = 60
        self.x = float(WIDTH // 2)
        self.y = float(HEIGHT - 250)
        self.hp = 100
        self.max_hp = 100

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        main_color = GREEN if current_skin == "green" else (BLUE if current_skin == "blue" else RED)
        
        # Отрисовка корабля
        pygame.draw.polygon(surface, main_color, [(px, py), (px - 25, py + 50), (px + 25, py + 50)])
        pygame.draw.polygon(surface, WHITE, [(px, py + 10), (px - 10, py + 40), (px + 10, py + 40)])
        
        # Щит
        if shield_time > 0:
            pygame.draw.circle(surface, BLUE, (px, py + 25), 45, 3)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 18

    def update(self):
        self.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, (int(self.x) - 3, int(self.y), 6, 16))

class Enemy:
    def __init__(self, is_boss=False):
        self.is_boss = is_boss
        self.radius = 60 if is_boss else random.randint(20, 40)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.speed = 4 if is_boss else random.randint(5, 9)
        self.hp = 20 if is_boss else 1

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        color = PURPLE if self.is_boss else RED
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

def main():
    global coins, run_coins, distance, last_boss_fifty, weapon_level, shield_time, game_state, current_skin

    player = Player()
    bullets = []
    enemies = []
    last_shot = 0
    dragging = False

    running = True
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = pygame.mouse.get_pos()
                
                if game_state == "MENU":
                    # Кнопка старта
                    game_state = "PLAYING"
                    player.hp = 100
                    enemies.clear()
                    bullets.clear()
                    distance = 0.0
                    run_coins = 0
                    safe_play(snd_respawn)  # Звук старта / возрождения
                    
                elif game_state == "GAMEOVER":
                    # Возрождение
                    game_state = "PLAYING"
                    player.hp = 100
                    enemies.clear()
                    bullets.clear()
                    safe_play(snd_respawn)  # Звук возрождения
                    
                elif game_state == "PLAYING":
                    dragging = True
                    player.x, player.y = pos[0], pos[1]

            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                dragging = False

            elif event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION):
                if dragging and game_state == "PLAYING":
                    pos = pygame.mouse.get_pos()
                    player.x, player.y = pos[0], pos[1]

        # --- Логика игры ---
        if game_state == "PLAYING":
            distance += 0.1
            if shield_time > 0:
                shield_time -= 1

            # Появление босса каждые 50 единиц дистанции
            current_fifty = int(distance // 50)
            if current_fifty > last_boss_fifty:
                last_boss_fifty = current_fifty
                enemies.append(Enemy(is_boss=True))
                safe_play(snd_boss)  # Звук появления босса

            # Выстрелы
            if now - last_shot > 150:
                bullets.append(Bullet(player.x, player.y))
                last_shot = now

            # Спавн обычных врагов
            if random.random() < 0.05:
                enemies.append(Enemy(is_boss=False))

            # Обновление пуль
            for b in bullets[:]:
                b.update()
                if b.y < -20:
                    bullets.remove(b)

            # Обновление и столкновения врагов
            for e in enemies[:]:
                e.update()

                # Попадание пули во врага
                for b in bullets[:]:
                    if math.hypot(b.x - e.x, b.y - e.y) < e.radius:
                        e.hp -= weapon_level
                        if b in bullets:
                            bullets.remove(b)
                        if e.hp <= 0:
                            if e in enemies:
                                enemies.remove(e)
                            safe_play(snd_kill)  # Звук убийства врага
                            run_coins += 5 if e.is_boss else 1
                            coins += 5 if e.is_boss else 1
                            break

                # Столкновение с игроком
                if math.hypot(player.x - e.x, player.y - e.y) < e.radius + 25:
                    if shield_time <= 0:
                        player.hp -= 30 if e.is_boss else 15
                        if player.hp <= 0:
                            game_state = "GAMEOVER"
                    if e in enemies:
                        enemies.remove(e)

                if e.y > HEIGHT + 50 and e in enemies:
                    enemies.remove(e)

        # --- Отрисовка ---
        screen.fill(BLACK)

        if game_state == "PLAYING":
            player.draw(surface=screen)
            for b in bullets:
                b.draw(screen)
            for e in enemies:
                e.draw(screen)

            # Текст UI
            txt_dist = font.render(f"Дистанция: {int(distance)}m", True, WHITE)
            txt_coins = font.render(f"Монеты: {coins}", True, YELLOW)
            txt_hp = font.render(f"HP: {max(0, player.hp)}%", True, GREEN if player.hp > 30 else RED)
            screen.blit(txt_dist, (20, 30))
            screen.blit(txt_coins, (20, 70))
            screen.blit(txt_hp, (WIDTH - 160, 30))

        elif game_state == "MENU":
            txt_title = font_large.render("SPACE SHOOTER", True, BLUE)
            txt_start = font.render("Нажмите на экран для старта", True, WHITE)
            screen.blit(txt_title, (WIDTH // 2 - txt_title.get_width() // 2, HEIGHT // 3))
            screen.blit(txt_start, (WIDTH // 2 - txt_start.get_width() // 2, HEIGHT // 2))

        elif game_state == "GAMEOVER":
            txt_over = font_large.render("GAME OVER", True, RED)
            txt_restart = font.render("Нажмите, чтобы возродиться", True, WHITE)
            screen.blit(txt_over, (WIDTH // 2 - txt_over.get_width() // 2, HEIGHT // 3))
            screen.blit(txt_restart, (WIDTH // 2 - txt_restart.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Функция покупки/улучшений (вызывается при необходимости в меню)
def buy_upgrade(upgrade_type):
    global coins, weapon_level, shield_time
    if upgrade_type == "weapon" and coins >= 20:
        coins -= 20
        weapon_level += 1
        safe_play(snd_upgrade)  # Звук улучшения
    elif upgrade_type == "shield" and coins >= 15:
        coins -= 15
        shield_time += 300
        safe_play(snd_shield)   # Звук активации щита
    elif upgrade_type == "skin" and coins >= 50:
        coins -= 50
        safe_play(snd_buy)      # Звук покупки

if __name__ == "__main__":
    main()
