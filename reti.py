import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 500, 800
FPS = 60
MAX_PLATFORM_SPEED = 14

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (10, 10, 40)
STAR_YELLOW = (255, 223, 0)
PLAYER_BLUE = (100, 149, 237)
GREY = (50, 50, 50)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
HOVER_GREY = (80, 80, 80)

PURPLE_DARK = (60, 40, 90)
PURPLE_LIGHT = (80, 60, 110)
PURPLE_ACTIVE = (100, 70, 140)

PASTEL_CREAM = (255, 255, 204)
PASTEL_PEACH = (255, 229, 180)

WAVE_1_COLOR = (75, 0, 130, 100)
WAVE_2_COLOR = (106, 90, 205, 100)
WAVE_3_COLOR = (60, 40, 120, 100)
NUM_STARS = 200

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retinal")
clock = pygame.time.Clock()

FONT_FILE = "Moonscape Demo.otf"
try:
    FONT_BIG = pygame.font.Font(FONT_FILE, 70)
    FONT_MEDIUM = pygame.font.Font(FONT_FILE, 40)
    FONT_SMALL = pygame.font.Font(FONT_FILE, 30)
    FONT_TINY = pygame.font.Font(FONT_FILE, 24)
    print(f"Successfully loaded font: {FONT_FILE}")
except Exception:
    print(f"Error loading font '{FONT_FILE}', using default...")
    FONT_BIG = pygame.font.SysFont("Arial", 60, bold=True)
    FONT_MEDIUM = pygame.font.SysFont("Arial", 36)
    FONT_SMALL = pygame.font.SysFont("Arial", 28)
    FONT_TINY = pygame.font.SysFont("Arial", 22)


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def draw_text(surf, text, font, x, y, color=WHITE, align="center"):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.midtop = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    surf.blit(text_surface, text_rect)

class ProceduralWave:
    def __init__(self, color, amplitude, frequency, speed, y_offset):
        self.color = color
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.y_offset = y_offset
        self.phase = random.uniform(0, 2 * math.pi)
        
        self.surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def update(self, dt):
        self.phase += self.speed * dt

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))
        points = []
        for x in range(WIDTH + 1):
            y = self.amplitude * math.sin(self.frequency * x + self.phase) + self.y_offset
            points.append((x, y))
        points.append((WIDTH, HEIGHT))
        points.append((0, HEIGHT))
        pygame.draw.polygon(self.surface, self.color, points)
        screen.blit(self.surface, (0, 0))


class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = FONT_MEDIUM
        if "Easy" in text or "Hard" in text or "Normal" in text:
             self.font = FONT_SMALL

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        
        text_y = self.rect.centery - self.font.get_height() // 2
        draw_text(surface, self.text, self.font, self.rect.centerx, text_y)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self):
        return self.is_hovered and pygame.mouse.get_pressed()[0]

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-150, 150) 
        self.vy = random.uniform(-150, 150)
        self.size = random.uniform(2, 5)
        self.color = PASTEL_CREAM
        self.lifetime = random.uniform(0.2, 0.5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.size -= 5 * dt
        return self.lifetime > 0 and self.size > 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), int(self.size))

class Basket:
    def __init__(self):
        self.width = 100
        self.height = 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 80
        self.base_vel = 9
        self.vel = self.base_vel
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys, speed_multiplier):
        calculated_vel = self.base_vel + (speed_multiplier - 1.0) * 3.0
        self.vel = min(MAX_PLATFORM_SPEED, calculated_vel)
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.vel
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.vel
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_BLUE, self.rect, border_radius=5)

class Star:
    def __init__(self, speed_multiplier):
        self.x = random.randint(100, WIDTH - 100) 
        self.y = random.randint(-200, -20)
        self.z = random.uniform(0.1, 1.0) 
        self.base_speed = random.uniform(1.4, 1.6)
        self.vel = self.base_speed * speed_multiplier
        self.base_size = 5 + self.z * 5
        self.points = int(15 - (self.z * 10))
        self.blink_timer = random.uniform(0, 2 * math.pi)
        self.blink_speed = random.uniform(1.0, 3.0)

    def update(self, dt, speed_multiplier):
        self.vel = self.base_speed * speed_multiplier
        self.y += self.vel
        self.blink_timer += self.blink_speed * dt

    def draw(self, surface):
        p = clamp((math.sin(self.blink_timer) * 0.5 + 0.5), 0, 1)
        current_size = self.base_size * (0.7 + p * 0.6)
        
        inner_size = int(current_size)
        outer_size = int(current_size * 1.6)
        
        base_alpha = int(100 + 155 * self.z) 
        base_alpha = clamp(base_alpha, 0, 255)

        s_size = int(outer_size * 2)
        if s_size < 1: s_size = 1
        s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
        
        outer_alpha = int(base_alpha * 0.5) 
        pygame.draw.circle(
            s, 
            (PASTEL_CREAM[0], PASTEL_CREAM[1], PASTEL_CREAM[2], outer_alpha),
            (s_size // 2, s_size // 2), 
            outer_size
        )

        pygame.draw.circle(
            s, 
            (PASTEL_PEACH[0], PASTEL_PEACH[1], PASTEL_PEACH[2], base_alpha), 
            (s_size // 2, s_size // 2), 
            inner_size
        )
        
        surface.blit(s, (self.x - s_size // 2, self.y - s_size // 2))

    def rect(self):
        return pygame.Rect(self.x - self.base_size, self.y - self.base_size, 
                            self.base_size * 2, self.base_size * 2)

def reset_game(current_settings):
    return {
        "basket": Basket(),
        "stars": [],
        "particles": [],
        "score": 0,
        "combo": 0,
        "speed_multiplier": 1.0,
        "star_add_counter": 0,
        "current_add_rate": current_settings["star_rate"]
    }

def draw_background(surface, bg_stars_list, waves_list):
    surface.fill(DARK_BLUE)
    for star in bg_stars_list:
        pygame.draw.circle(surface, WHITE, star['pos'], star['radius'])
    for wave in waves_list:
        wave.draw(surface)

def update_background(waves_list, dt):
    for wave in waves_list:
        wave.update(dt)

def main():
    game_state = 'MENU'
    running = True

    settings = {
        "star_rate": 100, # <--- ЗМІНЕНО (було 70)
        "star_rate_name": "Normal"
    }

    BTN_COLOR = PURPLE_DARK
    BTN_HOVER = PURPLE_LIGHT
    BTN_ACTIVE = PURPLE_ACTIVE

    btn_start = Button(WIDTH//2 - 100, 300, 200, 50, "START", BTN_COLOR, BTN_HOVER)
    btn_settings = Button(WIDTH//2 - 100, 370, 200, 50, "SETTINGS", BTN_COLOR, BTN_HOVER)
    btn_quit = Button(WIDTH//2 - 100, 440, 200, 50, "QUIT", BTN_COLOR, BTN_HOVER)
    
    btn_back = Button(WIDTH//2 - 100, 500, 200, 50, "BACK", BTN_COLOR, BTN_HOVER)
    btn_easy = Button(WIDTH//2 - 150, 330, 90, 40, "Easy", BTN_COLOR, BTN_HOVER)
    btn_medium = Button(WIDTH//2 - 50, 330, 100, 40, "Normal", BTN_COLOR, BTN_HOVER)
    btn_hard = Button(WIDTH//2 + 60, 330, 90, 40, "Hard", BTN_COLOR, BTN_HOVER)

    game_vars = reset_game(settings)

    print("Creating procedural background...")
    
    bg_stars = []
    for _ in range(NUM_STARS):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(1, 2)
        bg_stars.append({'pos': (x, y), 'radius': radius})
    
    
    wave1 = ProceduralWave(
        color=WAVE_1_COLOR,
        amplitude=70,      
        frequency=0.012,   
        speed=0.3,         
        y_offset=610
    )
    wave2 = ProceduralWave(
        color=WAVE_2_COLOR,
        amplitude=50,      
        frequency=0.007, 
        speed=-0.45,       
        y_offset=620
    )
    wave3 = ProceduralWave(
        color=WAVE_3_COLOR,
        amplitude=30,      
        frequency=0.01, 
        speed=0.6,         
        y_offset=600
    )
    
    waves = [wave1, wave2, wave3]
    
    print("Procedural background created.")

    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()

        if game_state == 'MENU':
            update_background(waves, dt)
            draw_background(window, bg_stars, waves)
            
            draw_text(window, "Retinal", FONT_BIG, WIDTH // 2, 150)
            
            btn_start.check_hover(mouse_pos)
            btn_settings.check_hover(mouse_pos)
            btn_quit.check_hover(mouse_pos)
            
            btn_start.draw(window)
            btn_settings.draw(window)
            btn_quit.draw(window)

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_start.check_click():
                        game_vars = reset_game(settings)
                        game_state = 'PLAYING'
                    if btn_settings.check_click():
                        game_state = 'SETTINGS'
                    if btn_quit.check_click():
                        running = False

        elif game_state == 'SETTINGS':
            update_background(waves, dt)
            draw_background(window, bg_stars, waves)

            draw_text(window, "Settings", FONT_BIG, WIDTH // 2, 150)
            draw_text(window, "Star Frequency:", FONT_MEDIUM, WIDTH // 2, 280)

            btn_easy.check_hover(mouse_pos)
            btn_medium.check_hover(mouse_pos)
            btn_hard.check_hover(mouse_pos)
            
            btn_easy.color = BTN_ACTIVE if settings["star_rate_name"] == "Easy" else BTN_COLOR
            btn_medium.color = BTN_ACTIVE if settings["star_rate_name"] == "Normal" else BTN_COLOR
            btn_hard.color = BTN_ACTIVE if settings["star_rate_name"] == "Hard" else BTN_COLOR

            btn_easy.draw(window)
            btn_medium.draw(window)
            btn_hard.draw(window)
            
            btn_back.check_hover(mouse_pos)
            btn_back.draw(window)

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_back.check_click():
                        game_state = 'MENU'
                    
                    if btn_easy.check_click():
                        settings["star_rate"] = 130 # <--- ЗМІНЕНО (було 90)
                        settings["star_rate_name"] = "Easy"
                    if btn_medium.check_click():
                        settings["star_rate"] = 100 # <--- ЗМІНЕНО (було 70)
                        settings["star_rate_name"] = "Normal"
                    if btn_hard.check_click():
                        settings["star_rate"] = 80 # <--- ЗМІНЕНО (було 50)
                        settings["star_rate_name"] = "Hard"

        elif game_state == 'PLAYING':
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = 'PAUSED'
            
            update_background(waves, dt)
            game_vars['basket'].move(keys_pressed, game_vars['speed_multiplier'])
            
            game_vars['star_add_counter'] += 1
            if game_vars['star_add_counter'] >= game_vars['current_add_rate']:
                game_vars['star_add_counter'] = 0
                num_to_spawn = 1
                if game_vars['speed_multiplier'] > 3.5: num_to_spawn = 3
                elif game_vars['speed_multiplier'] > 2.0: num_to_spawn = 2
                for _ in range(num_to_spawn):
                    game_vars['stars'].append(Star(game_vars['speed_multiplier']))

            missed_star = False
            for star in game_vars['stars'][:]:
                star.update(dt, game_vars['speed_multiplier'])
                if star.y > HEIGHT:
                    game_vars['stars'].remove(star)
                    missed_star = True
                    game_vars['score'] = max(0, game_vars['score'] - 5) 
                elif star.rect().colliderect(game_vars['basket'].rect):
                    game_vars['score'] += star.points + game_vars['combo']
                    game_vars['combo'] += 1
                    if game_vars['speed_multiplier'] < 5.0:
                        game_vars['speed_multiplier'] = min(game_vars['speed_multiplier'] + 0.03, 5.0)
                    num_particles = random.randint(8, 12)
                    for _ in range(num_particles):
                        game_vars['particles'].append(Particle(star.x, star.y))
                    game_vars['stars'].remove(star)

            if missed_star:
                game_vars['combo'] = 0

            for particle in game_vars['particles'][:]:
                if not particle.update(dt):
                    game_vars['particles'].remove(particle)

            draw_background(window, bg_stars, waves)
            game_vars['basket'].draw(window)
            for star in game_vars['stars']:
                star.draw(window)
            for particle in game_vars['particles']:
                particle.draw(window)
            
            draw_text(window, f"Score: {game_vars['score']}", FONT_MEDIUM, 60, 20, align="topleft")
            draw_text(window, f"Combo: x{game_vars['combo']}", FONT_SMALL, 60, 60, align="topleft")
            draw_text(window, f"Speed: {game_vars['speed_multiplier']:.2f}x", FONT_TINY, WIDTH - 80, 20, align="topright")
            draw_text(window, f"Platform: {game_vars['basket'].vel:.1f}", FONT_TINY, WIDTH - 80, 50, align="topright")

        elif game_state == 'PAUSED':
            draw_background(window, bg_stars, waves) 
            game_vars['basket'].draw(window)
            for star in game_vars['stars']:
                star.draw(window)
            for particle in game_vars['particles']:
                particle.draw(window)
                
            draw_text(window, f"Score: {game_vars['score']}", FONT_MEDIUM, 60, 20, align="topleft")
            draw_text(window, f"Combo: x{game_vars['combo']}", FONT_SMALL, 60, 60, align="topleft")
            draw_text(window, f"Speed: {game_vars['speed_multiplier']:.2f}x", FONT_TINY, WIDTH - 80, 20, align="topright")
            draw_text(window, f"Platform: {game_vars['basket'].vel:.1f}", FONT_TINY, WIDTH - 80, 50, align="topright")

            pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 180))
            window.blit(pause_overlay, (0, 0))

            draw_text(window, "PAUSED", FONT_BIG, WIDTH // 2, 300)
            draw_text(window, "Press SPACE to resume", FONT_SMALL, WIDTH // 2, 400)
            draw_text(window, "Press ESC for menu", FONT_TINY, WIDTH // 2, 450)

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = 'PLAYING'
                    if event.key == pygame.K_ESCAPE:
                        game_state = 'MENU'

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()