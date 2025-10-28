import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import random
import math
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Optional

SOUND_FOLDER = "sound"

pygame.init()

# --- CONSTANTS ---
WIDTH, HEIGHT = 500, 800
FPS = 60
MAX_PLATFORM_SPEED = 14

# --- COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (10, 10, 40)
PLAYER_BLUE = (100, 149, 237)
PURPLE_DARK = (60, 40, 90)
PURPLE_LIGHT = (80, 60, 110)
PURPLE_ACTIVE = (100, 70, 140)
PASTEL_CREAM = (255, 255, 204)
PASTEL_PEACH = (255, 229, 180)
WAVE_1_COLOR = (75, 0, 130, 100)
WAVE_2_COLOR = (106, 90, 205, 100)
WAVE_3_COLOR = (60, 40, 120, 100)
NUM_BG_STARS = 200

# --- HELPER FUNCTIONS ---
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

# --- ABSTRACT CLASSES ---

class GameObject(ABC):
    @abstractmethod
    def update(self, dt, **kwargs):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

class UIElement(GameObject):
    def __init__(self, x, y, w, h):
        self._rect = pygame.Rect(x, y, w, h)

    def update(self, dt, **kwargs):
        pass

class GameState(ABC):
    def __init__(self, game):
        self._game = game

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

# --- GENERIC OBJECT MANAGER ---
T = TypeVar('T', bound=GameObject)

class ObjectManager(Generic[T]):
    def __init__(self):
        self._objects: List[T] = []

    def add(self, obj: T):
        self._objects.append(obj)

    def remove(self, obj: T):
        if obj in self._objects:
            self._objects.remove(obj)

    def get_list(self) -> List[T]:
        return self._objects[:]

    def clear(self):
        self._objects.clear()

    def update_all(self, dt, **kwargs):
        for obj in self._objects[:]:
            obj.update(dt, **kwargs)

    def draw_all(self, surface):
        for obj in self._objects:
            obj.draw(surface)

# --- GAME OBJECT CLASSES ---

class ProceduralWave(GameObject):
    def __init__(self, color, amplitude, frequency, speed, y_offset):
        self._color = color
        self._amplitude = amplitude
        self._frequency = frequency
        self._speed = speed
        self._y_offset = y_offset
        self._phase = random.uniform(0, 2 * math.pi)
        self._surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def update(self, dt, **kwargs):
        self._phase += self._speed * dt

    def draw(self, surface):
        self._surface.fill((0, 0, 0, 0))
        points = []
        for x in range(WIDTH + 1):
            y = self._amplitude * math.sin(self._frequency * x + self._phase) + self._y_offset
            points.append((x, y))
        points.append((WIDTH, HEIGHT))
        points.append((0, HEIGHT))
        pygame.draw.polygon(self._surface, self._color, points)
        surface.blit(self._surface, (0, 0))

class Particle(GameObject):
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._vx = random.uniform(-150, 150)
        self._vy = random.uniform(-150, 150)
        self._size = random.uniform(2, 5)
        self._color = PASTEL_CREAM
        self._lifetime = random.uniform(0.2, 0.5)

    def update(self, dt, **kwargs):
        self._x += self._vx * dt
        self._y += self._vy * dt
        self._lifetime -= dt
        self._size -= 5 * dt
        return self._lifetime > 0 and self._size > 1

    def draw(self, surface):
        if self._size > 0:
            pygame.draw.circle(surface, self._color, (self._x, self._y), int(self._size))

class Basket(GameObject):
    def __init__(self):
        self._width = 150
        self._height = 20
        self._x = WIDTH // 2 - self._width // 2
        self._y = HEIGHT - 80
        self._base_vel = 9
        self._vel = self._base_vel

    def update(self, dt, **kwargs):
        keys = kwargs.get("keys")
        speed_multiplier = kwargs.get("speed_multiplier", 1.0)
        if not keys:
            return

        calculated_vel = self._base_vel + (speed_multiplier - 1.0) * 3.0
        self._vel = min(MAX_PLATFORM_SPEED, calculated_vel)

        if keys[pygame.K_LEFT] and self._x > 0:
            self._x -= self._vel
        if keys[pygame.K_RIGHT] and self._x < WIDTH - self._width:
            self._x += self._vel

    def get_vel(self) -> float:
        return self._vel

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self._x, self._y, self._width, self._height)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_BLUE, self.get_rect(), border_radius=5)

class Star(GameObject):
    def __init__(self, speed_multiplier):
        self._x = random.randint(100, WIDTH - 100)
        self._y = random.randint(-200, -20)
        self._z = random.uniform(0.1, 1.0)
        self._base_speed = random.uniform(1.4, 1.6)
        self._vel = self._base_speed * speed_multiplier
        self._base_size = 5 + self._z * 5
        self._points = int(15 - (self._z * 10))
        self._blink_timer = random.uniform(0, 2 * math.pi)
        self._blink_speed = random.uniform(1.0, 3.0)

    def update(self, dt, **kwargs):
        speed_multiplier = kwargs.get("speed_multiplier", 1.0)
        self._vel = self._base_speed * speed_multiplier
        self._y += self._vel
        self._blink_timer += self._blink_speed * dt

    def get_y(self) -> float:
        return self._y

    def get_points(self) -> int:
        return self._points

    def get_pos(self) -> tuple[float, float]:
        return (self._x, self._y)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self._x - self._base_size, self._y - self._base_size,
                            self._base_size * 2, self._base_size * 2)

    def draw(self, surface):
        p = clamp((math.sin(self._blink_timer) * 0.5 + 0.5), 0, 1)
        current_size = self._base_size * (0.7 + p * 0.6)

        inner_size = int(current_size)
        outer_size = int(current_size * 1.6)
        base_alpha = int(100 + 155 * self._z)
        base_alpha = clamp(base_alpha, 0, 255)

        s_size = int(outer_size * 2)
        if s_size < 1: s_size = 1
        s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)

        outer_alpha = int(base_alpha * 0.5)
        pygame.draw.circle(
            s, (PASTEL_CREAM[0], PASTEL_CREAM[1], PASTEL_CREAM[2], outer_alpha),
            (s_size // 2, s_size // 2), outer_size)

        pygame.draw.circle(
            s, (PASTEL_PEACH[0], PASTEL_PEACH[1], PASTEL_PEACH[2], base_alpha),
            (s_size // 2, s_size // 2), inner_size)

        surface.blit(s, (self._x - s_size // 2, self._y - s_size // 2))

# --- UI CLASSES ---

class Button(UIElement):
    def __init__(self, x, y, w, h, text, color, hover_color, font):
        super().__init__(x, y, w, h)
        self._text = text
        self._color = color
        self._hover_color = hover_color
        self._is_hovered = False
        self._font = font

    def update(self, dt, **kwargs):
        mouse_pos = kwargs.get("mouse_pos")
        if mouse_pos:
            self._is_hovered = self._rect.collidepoint(mouse_pos)
        else:
            self._is_hovered = False

    def draw(self, surface):
        color = self._hover_color if self._is_hovered else self._color
        pygame.draw.rect(surface, color, self._rect, border_radius=10)
        text_y = self._rect.centery - self._font.get_height() // 2
        draw_text(surface, self._text, self._font, self._rect.centerx, text_y)

    def check_click(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._is_hovered
        return False

    def set_color(self, color):
        self._color = color

# --- GAME STATE CLASSES ---

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        BTN_COLOR = PURPLE_DARK
        BTN_HOVER = PURPLE_LIGHT
        self._btn_start = Button(WIDTH//2 - 100, 300, 200, 50, "START", BTN_COLOR, BTN_HOVER, game.FONT_MEDIUM)
        self._btn_settings = Button(WIDTH//2 - 100, 370, 200, 50, "SETTINGS", BTN_COLOR, BTN_HOVER, game.FONT_MEDIUM)
        self._btn_quit = Button(WIDTH//2 - 100, 440, 200, 50, "QUIT", BTN_COLOR, BTN_HOVER, game.FONT_MEDIUM)
        self._buttons = [self._btn_start, self._btn_settings, self._btn_quit]

    def handle_event(self, event):
        if self._btn_start.check_click(event):
            self._game.change_state(PlayingState(self._game))
        elif self._btn_settings.check_click(event):
            self._game.change_state(SettingsState(self._game))
        elif self._btn_quit.check_click(event):
            self._game.stop()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons:
            btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        draw_text(surface, "Retinal", self._game.FONT_BIG, WIDTH // 2, 150)
        for btn in self._buttons:
            btn.draw(surface)

class SettingsState(GameState):
    def __init__(self, game):
        super().__init__(game)
        BTN_COLOR = PURPLE_DARK
        BTN_HOVER = PURPLE_LIGHT
        self._btn_back = Button(WIDTH//2 - 100, 500, 200, 50, "BACK", BTN_COLOR, BTN_HOVER, self._game.FONT_MEDIUM)
        self._btn_easy = Button(WIDTH//2 - 150, 330, 90, 40, "Easy", BTN_COLOR, BTN_HOVER, self._game.FONT_SMALL)
        self._btn_medium = Button(WIDTH//2 - 50, 330, 100, 40, "Normal", BTN_COLOR, BTN_HOVER, self._game.FONT_SMALL)
        self._btn_hard = Button(WIDTH//2 + 60, 330, 90, 40, "Hard", BTN_COLOR, BTN_HOVER, self._game.FONT_SMALL)
        self._buttons = [self._btn_back, self._btn_easy, self._btn_medium, self._btn_hard]
        self._update_button_colors()

    def _update_button_colors(self):
        settings = self._game.get_settings()
        self._btn_easy.set_color(PURPLE_ACTIVE if settings["star_rate_name"] == "Easy" else PURPLE_DARK)
        self._btn_medium.set_color(PURPLE_ACTIVE if settings["star_rate_name"] == "Normal" else PURPLE_DARK)
        self._btn_hard.set_color(PURPLE_ACTIVE if settings["star_rate_name"] == "Hard" else PURPLE_DARK)

    def handle_event(self, event):
        settings = self._game.get_settings()
        if self._btn_back.check_click(event):
            self._game.change_state(MenuState(self._game))
        elif self._btn_easy.check_click(event):
            settings["star_rate"] = 130
            settings["star_rate_name"] = "Easy"
        elif self._btn_medium.check_click(event):
            settings["star_rate"] = 100
            settings["star_rate_name"] = "Normal"
        elif self._btn_hard.check_click(event):
            settings["star_rate"] = 80
            settings["star_rate_name"] = "Hard"
        self._update_button_colors()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons:
            btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        draw_text(surface, "Settings", self._game.FONT_BIG, WIDTH // 2, 150)
        draw_text(surface, "Star Frequency:", self._game.FONT_MEDIUM, WIDTH // 2, 280)
        for btn in self._buttons:
            btn.draw(surface)

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self._basket = Basket()
        self._star_manager = ObjectManager[Star]()
        self._particle_manager = ObjectManager[Particle]()
        self.reset_game()

    def reset_game(self):
        self._score = 0
        self._combo = 0
        self._speed_multiplier = 1.0
        self._star_add_counter = 0
        self._current_add_rate = self._game.get_settings()["star_rate"]
        self._star_manager.clear()
        self._particle_manager.clear()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._game.change_state(PausedState(self._game, self))

    def _spawn_stars(self):
        self._star_add_counter += 1
        if self._star_add_counter >= self._current_add_rate:
            self._star_add_counter = 0
            num_to_spawn = 1
            if self._speed_multiplier > 3.5: num_to_spawn = 3
            elif self._speed_multiplier > 2.0: num_to_spawn = 2
            for _ in range(num_to_spawn):
                self._star_manager.add(Star(self._speed_multiplier))

    def _handle_collisions(self):
        missed_star = False
        basket_rect = self._basket.get_rect()
        for star in self._star_manager.get_list()[:]:
            if star.get_y() > HEIGHT:
                self._star_manager.remove(star)
                missed_star = True
                self._score = max(0, self._score - 5)
            elif star.get_rect().colliderect(basket_rect):
                self._game.play_catch_sound()
                self._score += star.get_points() + self._combo
                self._combo += 1
                if self._speed_multiplier < 5.0:
                    self._speed_multiplier = min(self._speed_multiplier + 0.03, 5.0)
                num_particles = random.randint(8, 12)
                star_pos = star.get_pos()
                for _ in range(num_particles):
                    self._particle_manager.add(Particle(star_pos[0], star_pos[1]))
                self._star_manager.remove(star)
        if missed_star:
            self._combo = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._basket.update(dt, keys=keys, speed_multiplier=self._speed_multiplier)
        self._spawn_stars()
        self._star_manager.update_all(dt, speed_multiplier=self._speed_multiplier)
        self._handle_collisions()
        for particle in self._particle_manager.get_list()[:]:
            if not particle.update(dt):
                self._particle_manager.remove(particle)

    def draw(self, surface):
        self._basket.draw(surface)
        self._star_manager.draw_all(surface)
        self._particle_manager.draw_all(surface)
        draw_text(surface, f"Score: {self._score}", self._game.FONT_MEDIUM, 60, 20, align="topleft")
        draw_text(surface, f"Combo: x{self._combo}", self._game.FONT_SMALL, 60, 60, align="topleft")
        draw_text(surface, f"Speed: {self._speed_multiplier:.2f}x", self._game.FONT_TINY, WIDTH - 80, 20, align="topright")
        draw_text(surface, f"Platform: {self._basket.get_vel():.1f}", self._game.FONT_TINY, WIDTH - 80, 50, align="topright")

class PausedState(GameState):
    def __init__(self, game, playing_state: PlayingState):
        super().__init__(game)
        self._playing_state = playing_state
        self._overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._game.change_state(self._playing_state)
            elif event.key == pygame.K_ESCAPE:
                self._game.change_state(MenuState(self._game))

    def update(self, dt):
        pass

    def draw(self, surface):
        self._playing_state.draw(surface)
        surface.blit(self._overlay, (0, 0))
        draw_text(surface, "PAUSED", self._game.FONT_BIG, WIDTH // 2, 300)
        draw_text(surface, "Press SPACE to resume", self._game.FONT_SMALL, WIDTH // 2, 400)
        draw_text(surface, "Press ESC for menu", self._game.FONT_TINY, WIDTH // 2, 450)

# --- MAIN GAME CLASS ---

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self._window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Retinal")
        self._clock = pygame.time.Clock()
        self._running = True
        self._settings = {"star_rate": 100, "star_rate_name": "Normal"}
        self._load_fonts()
        self._create_background()
        self._menu_music_path = os.path.join(SOUND_FOLDER, "menu_sound.mp3")
        self._game_music_path = os.path.join(SOUND_FOLDER, "game_sound.mp3")
        self._sound_effect_paths = {"hight": os.path.join(SOUND_FOLDER, "hight.mp3")}
        self._current_music_path: Optional[str] = None
        self._catch_sound: Optional[pygame.mixer.Sound] = None
        self._sound_channel_star: Optional[pygame.mixer.Channel] = None
        self._load_audio()
        self._current_state: GameState = MenuState(self)
        self.play_music(self._menu_music_path)

    def _load_fonts(self):
        FONT_FILE = "Moonscape Demo.otf"
        try:
            self.FONT_BIG = pygame.font.Font(FONT_FILE, 70)
            self.FONT_MEDIUM = pygame.font.Font(FONT_FILE, 40)
            self.FONT_SMALL = pygame.font.Font(FONT_FILE, 30)
            self.FONT_TINY = pygame.font.Font(FONT_FILE, 24)
            print(f"Successfully loaded font: {FONT_FILE}")
        except Exception:
            print(f"Error loading font '{FONT_FILE}', using default...")
            self.FONT_BIG = pygame.font.SysFont("Arial", 60, bold=True)
            self.FONT_MEDIUM = pygame.font.SysFont("Arial", 36)
            self.FONT_SMALL = pygame.font.SysFont("Arial", 28)
            self.FONT_TINY = pygame.font.SysFont("Arial", 22)

    def _create_background(self):
        print("Creating procedural background...")
        self._bg_stars = []
        for _ in range(NUM_BG_STARS):
            self._bg_stars.append({'pos': (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 'radius': random.randint(1, 2)})
        self._waves_manager = ObjectManager[ProceduralWave]()
        self._waves_manager.add(ProceduralWave(WAVE_1_COLOR, 70, 0.012, 0.3, 610))
        self._waves_manager.add(ProceduralWave(WAVE_2_COLOR, 50, 0.007, -0.45, 620))
        self._waves_manager.add(ProceduralWave(WAVE_3_COLOR, 30, 0.01, 0.6, 600))
        print("Procedural background created.")

    def _load_audio(self):
        try:
            hight_path = self._sound_effect_paths.get("hight")
            if hight_path and os.path.exists(hight_path):
                 self._catch_sound = pygame.mixer.Sound(hight_path)
                 self._sound_channel_star = pygame.mixer.Channel(0)
                 print(f"Successfully loaded catch sound ({os.path.basename(hight_path)}) from '{SOUND_FOLDER}' folder")
            else:
                 print(f"Warning: Sound file 'hight.mp3' not found in '{SOUND_FOLDER}' folder.")
                 self._catch_sound = None
                 self._sound_channel_star = None
        except pygame.error as e:
            print(f"Warning: Could not load sound from '{SOUND_FOLDER}'. Error: {e}")
            self._catch_sound = None
            self._sound_channel_star = None

    def play_catch_sound(self):
        if self._sound_channel_star and self._catch_sound:
            self._sound_channel_star.play(self._catch_sound)

    def play_music(self, music_path: str, fade_ms: int = 1000, volume: float = 0.5):
        if not os.path.exists(music_path):
             print(f"Error: Music file not found at '{music_path}'")
             self._current_music_path = None
             return
        if music_path == self._current_music_path and pygame.mixer.music.get_busy():
            if abs(pygame.mixer.music.get_volume() - volume) > 0.01:
                 pygame.mixer.music.set_volume(volume)
            return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self._current_music_path = music_path
            print(f"Playing music: {os.path.basename(music_path)} at volume {volume:.1f}")
        except pygame.error as e:
            print(f"Warning: Could not load or play music '{music_path}'. Error: {e}")
            self._current_music_path = None

    def run(self):
        while self._running:
            dt = self._clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            self._current_state.handle_event(event)

    def _update(self, dt):
        self._waves_manager.update_all(dt)
        self._current_state.update(dt)

    def _draw(self):
        self._window.fill(DARK_BLUE)
        for star in self._bg_stars:
            pygame.draw.circle(self._window, WHITE, star['pos'], star['radius'])
        self._waves_manager.draw_all(self._window)
        self._current_state.draw(self._window)
        pygame.display.flip()

    def change_state(self, new_state: GameState):
        print(f"Changing state from {type(self._current_state).__name__} to {type(new_state).__name__}")
        self._current_state = new_state
        if isinstance(new_state, (MenuState, SettingsState)):
            self.play_music(self._menu_music_path, volume=0.5)
        elif isinstance(new_state, PlayingState):
            self.play_music(self._game_music_path, volume=0.3)

    def stop(self):
        self._running = False

    def get_settings(self) -> dict:
        return self._settings

# --- GAME LAUNCH ---
if __name__ == "__main__":
    game = Game()
    game.run()